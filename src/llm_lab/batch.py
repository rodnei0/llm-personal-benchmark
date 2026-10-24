"""Lotes sequenciais; cada geração conserva seu resultado e resposta originais."""
import json
import math
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen
from uuid import uuid4

from .core import digest, load_case
from .ollama import run
from .thermal import ServiceStopper, GuardAbort, guarded_run


from .telemetry import cpu_temperature, Monitor, recovery_ready, summarize


def _git(*args):
    try:
        return subprocess.check_output(['git', *args], text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def _save(root, data):
    temporary = root / 'batch.json.tmp'
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    temporary.replace(root / 'batch.json')
    lines = ['# Lote LLM Lab', '', f"Estado: {data['status']}", '',
             '| Modelo | Repetição | Estado | Aprovado | Tempo (s) | Tokens/s |',
             '| --- | --- | --- | --- | --- | --- |']
    for item in data['runs']:
        metrics = item.get('metrics', {})
        # JSON é a fonte exata; valores controlados são escapados para a tabela.
        name = item['model'].replace('|', '\\|').replace('\n', ' ')
        approved = (item.get('evaluation') or {}).get('passed')
        approved = 'pendente' if approved is None else approved
        lines.append(f"| {name} | {item['repetition']} | {item['status']} | {approved} | {metrics.get('elapsed_seconds', '—')} | {metrics.get('tokens_per_second', '—')} |")
    if 'shutdown' in data:
        lines += ['', 'Parada do serviço confirmada: ' + str(data['shutdown'].get('confirmed')),
                  'Motivo: ' + str(data.get('error'))]
    lines += ['', '## Registros', '']
    for item in data['runs']:
        if 'path' in item:
            lines.append(f"- [Resultado]({item['path']}/result.json) · [Resposta original]({item['path']}/response.txt)")
        if 'telemetry_summary' in item:
            lines.append('- Telemetria: ' + json.dumps(item['telemetry_summary'], ensure_ascii=False))
        if 'error' in item:
            lines.append('- Erro: ' + str(item['error']).replace('\n', ' '))
    lines += ['', 'Avaliação estrita, sem reparar respostas. Reprovação funcional não é erro de infraestrutura.',
              'Telemetria amostrada durante o lote; recuperação adaptativa entre rodadas. Não há corte térmico automático durante a inferência.']
    (root / 'summary.md').write_text('\n'.join(lines) + '\n')


def run_batch(directory, models, *, repetitions=1, cooldown=30,
              output_root='results/runs/batches', temperature_check=True,
              max_start_temp=60, max_cooldown_wait=900,
              max_gpu_temp=60, max_cpu_usage=20, max_gpu_usage=10,
              sample_interval=2, stable_seconds=10, thermal_guard=False,
              abort_cpu_temp=85, abort_gpu_temp=80, **options):
    if not models or any(not m.strip() for m in models) or len(set(models)) != len(models):
        raise ValueError('Informe modelos não vazios e sem duplicatas; use --repetitions para repetir')
    if type(repetitions) is not int or repetitions < 1:
        raise ValueError('Repetições devem ser positivas')
    if math.isfinite(cooldown) and cooldown < 30:
        raise ValueError('O intervalo mínimo entre rodadas é de 30 segundos')
    if any(not math.isfinite(v) or v < 0 for v in (cooldown, max_cooldown_wait)) or not math.isfinite(max_start_temp):
        raise ValueError('Intervalos devem ser finitos e não negativos; temperatura deve ser finita')
    if any(not math.isfinite(v) for v in (max_gpu_temp, max_cpu_usage, max_gpu_usage, sample_interval, stable_seconds)) or sample_interval < 0.1 or stable_seconds < 0 or not 0 <= max_cpu_usage <= 100 or not 0 <= max_gpu_usage <= 100:
        raise ValueError('Limites de telemetria inválidos')
    if any(not math.isfinite(v) or v <= 0 for v in (abort_cpu_temp, abort_gpu_temp)):
        raise ValueError('Limites térmicos devem ser finitos e positivos')
    if thermal_guard and (not temperature_check or sample_interval > 2 or max_start_temp >= abort_cpu_temp or max_gpu_temp >= abort_gpu_temp):
        raise ValueError('Modo protegido exige recuperação habilitada, amostragem <=2 s e limites de início abaixo do corte')
    # Validação antes de criar o lote ou iniciar qualquer inferência.
    host = options.get('host', 'http://127.0.0.1:11434')
    timeout = options.get('timeout', 600)
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError('Timeout deve ser finito e positivo')
    temp = options.get('temperature', 0.0)
    if not math.isfinite(temp) or temp < 0 or options.get('num_ctx', 4096) <= 0 or options.get('num_predict', 1024) <= 0:
        raise ValueError('Parâmetros de geração inválidos')
    from urllib.parse import urlsplit
    parsed = urlsplit(host)
    if parsed.scheme not in ('http', 'https') or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path not in ('', '/'):
        raise ValueError('Host deve ser uma origem HTTP(S) sem credenciais ou caminho')
    if temperature_check and parsed.hostname not in ('localhost', '127.0.0.1', '::1'):
        raise ValueError('Sensor local não representa servidor remoto; use monitoramento externo e --no-temperature-check')
    stopper = ServiceStopper(host) if thermal_guard else None
    guard_preflight = stopper.preflight() if stopper else None
    manifest, files, prompt, manifest_hash = load_case(directory)
    if temperature_check:
        cpu_temperature()
    root = Path(output_root) / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid4().hex[:12])
    root.mkdir(parents=True, exist_ok=False)
    # Congelar o caso inteiro antes da primeira rodada, inclusive o manifesto original.
    source = Path(directory)
    frozen = root / 'case'
    frozen.mkdir()
    (frozen / 'case.json').write_bytes((source / 'case.json').read_bytes())
    for key, content in files.items():
        destination = frozen / manifest[key]
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
    data = {'schema_version': '1.0.0', 'status': 'running',
            'started_at': datetime.now(timezone.utc).isoformat(),
            'case': manifest, 'manifest_sha256': manifest_hash,
            'prompt_sha256': digest(prompt.encode()),
            'git_commit': _git('rev-parse', 'HEAD'), 'git_status': _git('status', '--porcelain'),
            'models': models, 'repetitions': repetitions, 'options': options,
            'cooldown_seconds': cooldown, 'temperature_check': temperature_check,
            'max_start_temp': max_start_temp, 'max_cooldown_wait': max_cooldown_wait,
            'temperature_source': 'max coretemp temp*_input' if temperature_check else None,
            'max_gpu_temp': max_gpu_temp, 'max_cpu_usage': max_cpu_usage,
            'max_gpu_usage': max_gpu_usage, 'sample_interval': sample_interval,
            'stable_seconds': stable_seconds, 'telemetry_file': 'telemetry.jsonl',
            'thermal_guard': thermal_guard, 'abort_cpu_temp': abort_cpu_temp,
            'abort_gpu_temp': abort_gpu_temp, 'guard_preflight': guard_preflight, 'runs': []}
    _save(root, data)
    print(f'Lote: {root}', flush=True)
    monitor = Monitor(root / 'telemetry.jsonl', sample_interval)
    try:
        monitor.start()
        # Não baixar modelos automaticamente; preservar inventário com digests e versão.
        def get(endpoint):
            with urlopen(host.rstrip('/') + endpoint, timeout=min(timeout, 30)) as stream:
                return json.load(stream)
        data['ollama_version'] = get('/api/version')
        data['ollama_tags'] = get('/api/tags')
        available = {m['name'] for m in data['ollama_tags']['models']}
        missing = [m for m in models if (m if ':' in m else m + ':latest') not in available]
        if missing:
            raise ValueError('Modelos não instalados: ' + ', '.join(missing))
        _save(root, data)
        # Repetição externa: alternar modelos entre repetições, sempre sequencial.
        for repetition in range(1, repetitions + 1):
            for model in models:
                if data['runs']:
                    monitor.phase = 'cooldown'
                    print(f'Intervalo de {cooldown:g}s antes de {model}', flush=True)
                    time.sleep(cooldown)
                monitor.phase, monitor.run_index = 'recovery', len(data['runs'])
                monitor.check()
                if temperature_check:
                    deadline = time.monotonic() + max_cooldown_wait
                    stable_since = None
                    while True:
                        sample = monitor.check()
                        # Se nvidia-smi existe mas falha, não confundir ausência de dados com GPU fria.
                        import shutil
                        gpu_expected = shutil.which('nvidia-smi') is not None
                        ready = recovery_ready(sample, cpu_temp=max_start_temp,
                            gpu_temp=max_gpu_temp, cpu_usage=max_cpu_usage, gpu_usage=max_gpu_usage)
                        ready = ready and (not gpu_expected or bool(sample['gpus']))
                        stable_since = (stable_since if stable_since is not None else time.monotonic()) if ready else None
                        data['pending'] = {'model': model, 'repetition': repetition, 'latest_sample': sample}
                        _save(root, data)
                        if stable_since is not None and time.monotonic() - stable_since >= stable_seconds:
                            break
                        if time.monotonic() >= deadline:
                            raise ValueError('CPU/GPU não retornaram aos limites de recuperação no prazo; lote encerrado')
                        print(f"Aguardando recuperação: CPU {sample.get('cpu_temp_c')} °C / {sample.get('cpu_percent')}%", flush=True)
                        time.sleep(min(sample_interval, max(0, deadline - time.monotonic())))
                item = {'model': model, 'repetition': repetition, 'status': 'running',
                        'telemetry_before': monitor.check()}
                data.pop('pending', None)
                data['runs'].append(item)
                _save(root, data)
                print(f'Executando {model}, repetição {repetition}', flush=True)
                monitor.phase, monitor.run_index = 'inference', len(data['runs']) - 1
                if stopper:
                    target, result = guarded_run(
                        lambda: run(frozen, model, root / 'runs', **options), monitor, stopper,
                        cpu_limit=abort_cpu_temp, gpu_limit=abort_gpu_temp)
                else:
                    target, result = run(frozen, model, root / 'runs', **options)
                monitor.phase = 'recovery'
                item.update(status='completed', path=str(target.relative_to(root)),
                            evaluation=result['evaluation'], metrics=result['metrics'],
                            response_sha256=result['hashes']['response'],
                            done_reason=result['inference']['response'].get('done_reason'),
                            eval_count=result['inference']['response'].get('eval_count'))
                _save(root, data)
                item['telemetry_after'] = monitor.check()
                with monitor.lock:
                    item['telemetry_summary'] = summarize(root / 'telemetry.jsonl', len(data['runs']) - 1)
                _save(root, data)
        data['status'] = 'completed'
    except GuardAbort as exc:
        data['status'] = 'aborted'
        data['error'] = exc.reason
        data['shutdown'] = exc.shutdown
        if data['runs']:
            data['runs'][-1]['evaluation'] = None
            data['runs'][-1]['abort_reason'] = exc.reason
            data['runs'][-1]['shutdown'] = exc.shutdown
    except KeyboardInterrupt:
        data['status'] = 'interrupted'
        data['error'] = 'Interrompido pelo usuário; cancelamento no servidor não confirmado'
    except Exception as exc:
        data['status'] = 'failed'
        data['error'] = str(exc)
    finally:
        monitor.stop()
        for index, item in enumerate(data['runs']):
            if 'path' in item:
                item['telemetry_summary'] = summarize(root / 'telemetry.jsonl', index)
            if item['status'] == 'running':
                item['status'] = data['status']
                item['error'] = data.get('error', 'Execução incompleta')
        data['finished_at'] = datetime.now(timezone.utc).isoformat()
        _save(root, data)
    if data['status'] != 'completed':
        raise ValueError(f"Lote {data['status']}: {data.get('error')}. Registro: {root}")
    return root, data
