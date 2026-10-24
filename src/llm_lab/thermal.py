"""Controle opcional para Ollama local gerenciado por systemd/cgroup v2."""
import errno
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import threading
import time
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import urlopen

from .telemetry import Sampler


class GuardAbort(ValueError):
    def __init__(self, reason, shutdown):
        super().__init__(reason)
        self.reason, self.shutdown = reason, shutdown


def thermal_violation(sample, cpu_limit, gpu_limit, gpu_required):
    temperature = sample.get('cpu_temp_c')
    if temperature is None or not math.isfinite(temperature):
        return 'Sensor de temperatura CPU indisponível'
    if temperature >= cpu_limit:
        return f'CPU atingiu {temperature:g} °C (limite {cpu_limit:g} °C)'
    gpus = sample.get('gpus', [])
    if gpu_required and not gpus:
        return 'Telemetria NVIDIA indisponível'
    for gpu in gpus:
        temperature = gpu.get('temp_c')
        if temperature is None or not math.isfinite(temperature):
            return 'Sensor de temperatura GPU indisponível'
        if temperature >= gpu_limit:
            return f'GPU atingiu {temperature:g} °C (limite {gpu_limit:g} °C)'
    return None


class ServiceStopper:
    """Não instala permissões, não usa shell, não reinicia o servidor."""
    def __init__(self, host='http://127.0.0.1:11434'):
        u = urlsplit(host)
        if u.scheme != 'http' or u.hostname not in ('127.0.0.1', 'localhost') or u.port != 11434 or u.username or u.password or u.path not in ('', '/') or u.query or u.fragment:
            raise ValueError('Controle térmico exige Ollama HTTP local na porta 11434')
        self.host = host.rstrip('/')
        self.systemctl = shutil.which('systemctl')
        if not self.systemctl:
            raise ValueError('systemctl indisponível')
        self.command = [self.systemctl, 'stop', 'ollama.service']
        if os.geteuid() != 0:
            sudo = shutil.which('sudo')
            if not sudo:
                raise ValueError('sudo indisponível para parada não interativa')
            self.command = [sudo, '-n', *self.command]
        self.cgroup = None
        self.gpu_required = shutil.which('nvidia-smi') is not None

    def state(self):
        try:
            reply = subprocess.run([self.systemctl, 'show', 'ollama.service', '--no-pager',
                                    '--property=ActiveState,SubState,MainPID,ControlGroup,KillMode,SendSIGKILL,Environment'],
                                   capture_output=True, text=True, timeout=5, check=True)
        except (OSError, subprocess.SubprocessError) as exc:
            raise ValueError('Não foi possível consultar ollama.service: ' + str(exc)) from exc
        return dict(line.split('=', 1) for line in reply.stdout.splitlines() if '=' in line)

    def api(self, path):
        with urlopen(self.host + path, timeout=2) as stream:
            return json.load(stream)

    def preflight(self):
        state = self.state()
        if state.get('ActiveState') != 'active' or not state.get('MainPID', '0').isdigit() or int(state['MainPID']) <= 0:
            raise ValueError('ollama.service precisa estar ativo para verificar o controle')
        if state.get('KillMode') != 'control-group' or state.get('SendSIGKILL') != 'yes':
            raise ValueError('Exigidos KillMode=control-group e SendSIGKILL=yes')
        env = state.get('Environment', '').split()
        if 'OLLAMA_HOST=127.0.0.1:11434' not in env:
            raise ValueError('Serviço deve declarar OLLAMA_HOST=127.0.0.1:11434')
        group = state.get('ControlGroup', '')
        if not group.startswith('/') or group == '/':
            raise ValueError('ControlGroup do serviço inválido')
        self.cgroup = Path('/sys/fs/cgroup') / group.lstrip('/')
        if not self.cgroup.resolve().is_relative_to(Path('/sys/fs/cgroup')) or not (self.cgroup / 'cgroup.procs').is_file():
            raise ValueError('Confirmação exige cgroup v2 legível')
        # Verifica a leitura do grupo antes de iniciar a carga.
        (self.cgroup / 'cgroup.procs').read_text()
        if self.command[0] != self.systemctl:
            try:
                subprocess.run([self.command[0], '-n', '-l', *self.command[2:]],
                               capture_output=True, text=True, timeout=5, check=True)
            except (OSError, subprocess.SubprocessError) as exc:
                raise ValueError('Permissão de parada não interativa indisponível; consulte docs/thermal-guard.md') from exc
        self.api('/api/version')
        return {'service': 'ollama.service', 'active': True, 'kill_mode': state['KillMode'],
                'control_group': group, 'gpu_required': self.gpu_required}

    def stop(self):
        result = {'confirmed': False, 'service': 'ollama.service', 'errors': []}
        try:
            command = subprocess.run(self.command, capture_output=True, text=True, timeout=15)
            result['stop_returncode'] = command.returncode
            if command.returncode:
                result['errors'].append(command.stderr.strip())
        except (OSError, subprocess.SubprocessError) as exc:
            result['errors'].append(str(exc))
        deadline = time.monotonic() + 10
        while True:
            try:
                state = self.state()
                # Grupo original e descendentes devem estar sem processos ou já removidos.
                if self.cgroup is None:
                    raise ValueError('Preflight do cgroup não concluído')
                process_files = [self.cgroup / 'cgroup.procs', *self.cgroup.glob('**/cgroup.procs')]
                pids = set()
                for file in process_files:
                    try:
                        pids.update(file.read_text().split())
                    except FileNotFoundError:
                        pass
                refused = False
                try:
                    self.api('/api/version')
                except URLError as exc:
                    refused = isinstance(exc.reason, ConnectionRefusedError) or getattr(exc.reason, 'errno', None) == errno.ECONNREFUSED
                result.update(active_state=state.get('ActiveState'), main_pid=state.get('MainPID'),
                              remaining_pids=sorted(pids), api_connection_refused=refused)
                result['confirmed'] = state.get('ActiveState') == 'inactive' and state.get('MainPID') == '0' and not pids and refused
                if result['confirmed']:
                    break
            except (OSError, ValueError, subprocess.SubprocessError) as exc:
                result['errors'].append(str(exc))
            if time.monotonic() >= deadline:
                break
            time.sleep(0.5)
        return result


def guarded_run(function, monitor, stopper, *, cpu_limit=85, gpu_limit=80):
    outcome, done = {}, threading.Event()
    def worker():
        try:
            outcome['value'] = function()
        except BaseException as exc:
            outcome['error'] = exc
        finally:
            done.set()
    thread = threading.Thread(target=worker, daemon=True)
    def abort(reason):
        shutdown = stopper.stop()
        thread.join(timeout=5) if thread.ident is not None else None
        shutdown['client_finished'] = not thread.is_alive()
        raise GuardAbort(reason, shutdown)
    try:
        reason = thermal_violation(monitor.check(), cpu_limit, gpu_limit, stopper.gpu_required)
        if reason:
            abort(reason)
        thread.start()
        while not done.wait(0.2):
            reason = thermal_violation(monitor.check(), cpu_limit, gpu_limit, stopper.gpu_required)
            if reason:
                abort(reason)
        # Não deixar escapar o último pico disponível se a resposta já tiver terminado.
        reason = thermal_violation(monitor.check(), cpu_limit, gpu_limit, stopper.gpu_required)
        if reason:
            abort(reason)
        if 'error' in outcome:
            abort('Falha de execução: ' + str(outcome['error']))
        return outcome['value']
    except GuardAbort:
        raise
    except KeyboardInterrupt:
        abort('Interrompido pelo usuário')
    except Exception as exc:
        abort('Controle/telemetria falhou: ' + str(exc))


def check_guard(host, test_stop=False):
    stopper = ServiceStopper(host)
    result = {'preflight': stopper.preflight()}
    sample = Sampler().sample()
    reason = thermal_violation(sample, 85, 80, stopper.gpu_required)
    if reason:
        raise ValueError(reason)
    result['sample'] = sample
    if test_stop:
        if stopper.api('/api/ps').get('models'):
            raise ValueError('Ensaio sem carga exige nenhum modelo carregado em ollama ps')
        result['shutdown'] = stopper.stop()
        if not result['shutdown']['confirmed']:
            raise ValueError('Parada não confirmada: ' + json.dumps(result['shutdown']))
    return result
