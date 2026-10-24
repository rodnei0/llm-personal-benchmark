"""Telemetria Linux via procfs/sysfs e nvidia-smi, sem instalar agentes."""
import json
import math
import subprocess
import threading
import time
from datetime import datetime, timezone
from pathlib import Path


def cpu_temperature():
    readings = []
    for device in Path('/sys/class/hwmon').glob('hwmon*'):
        try:
            if (device / 'name').read_text().strip() == 'coretemp':
                readings.extend(float(p.read_text()) / 1000 for p in device.glob('temp*_input'))
        except OSError:
            continue
    if not readings or not all(math.isfinite(t) for t in readings):
        raise ValueError('Sensor coretemp indisponível')
    return max(readings)


class Sampler:
    def __init__(self):
        self.previous = None

    def sample(self):
        result = {'at': datetime.now(timezone.utc).isoformat(), 'errors': []}
        try:
            values = [int(n) for n in Path('/proc/stat').read_text().splitlines()[0].split()[1:9]]
            total, idle = sum(values), values[3] + values[4]
            result['cpu_percent'] = None
            if self.previous and total > self.previous[0]:
                result['cpu_percent'] = 100 * (1 - (idle - self.previous[1]) / (total - self.previous[0]))
            self.previous = total, idle
        except (OSError, ValueError, IndexError) as exc:
            result['cpu_percent'] = None
            result['errors'].append(str(exc))
        try:
            info = {line.split(':')[0]: int(line.split()[1]) for line in Path('/proc/meminfo').read_text().splitlines()}
            result['ram_total_bytes'] = info['MemTotal'] * 1024
            result['ram_used_bytes'] = (info['MemTotal'] - info['MemAvailable']) * 1024
        except (OSError, ValueError, KeyError) as exc:
            result['errors'].append(str(exc))
        try:
            result['cpu_temp_c'] = cpu_temperature()
        except (OSError, ValueError) as exc:
            result['cpu_temp_c'] = None
            result['errors'].append(str(exc))
        result['gpus'] = []
        try:
            raw = subprocess.check_output(['nvidia-smi', '--query-gpu=index,temperature.gpu,utilization.gpu,memory.used,memory.total', '--format=csv,noheader,nounits'], text=True, stderr=subprocess.DEVNULL, timeout=3)
            def number(value):
                try:
                    v = float(value.strip())
                    return v if math.isfinite(v) else None
                except ValueError:
                    return None
            for line in raw.splitlines():
                fields = line.split(',')
                if len(fields) != 5:
                    raise ValueError('Formato inesperado de nvidia-smi')
                result['gpus'].append(dict(zip(('index', 'temp_c', 'utilization_percent', 'memory_used_mib', 'memory_total_mib'), map(number, fields))))
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            result['errors'].append('GPU: ' + str(exc))
        return result


class Monitor:
    def __init__(self, path, interval=2):
        self.path, self.interval = Path(path), interval
        self.phase, self.run_index = 'setup', None
        self.lock = threading.Lock()
        self.latest = None
        self.error = None
        self.last_update = None
        self.stop_event = threading.Event()
        self.ready = threading.Event()
        self.thread = threading.Thread(target=self._loop, daemon=True)

    def _loop(self):
        sampler = Sampler()
        try:
            with self.path.open('x') as stream:
                while not self.stop_event.is_set():
                    phase, index = self.phase, self.run_index
                    sample = sampler.sample()
                    sample.update(phase=phase, run_index=index)
                    with self.lock:
                        stream.write(json.dumps(sample) + '\n')
                        stream.flush()
                    self.last_update = time.monotonic()
                    self.latest = sample
                    self.ready.set()
                    self.stop_event.wait(self.interval)
        except Exception as exc:
            self.error = str(exc)
            self.ready.set()

    def start(self):
        self.thread.start()
        if not self.ready.wait(10) or self.error:
            raise ValueError('Falha ao iniciar telemetria: ' + str(self.error))

    def stop(self):
        self.stop_event.set()
        self.thread.join(timeout=5)

    def check(self):
        if self.error or not self.thread.is_alive():
            raise ValueError('Telemetria interrompida: ' + str(self.error))
        if self.last_update is None or time.monotonic() - self.last_update > self.interval + 6:
            raise ValueError('Telemetria sem amostras recentes')
        return self.latest


def recovery_ready(sample, *, cpu_temp, gpu_temp, cpu_usage, gpu_usage):
    if sample.get('cpu_temp_c') is None or sample.get('cpu_percent') is None:
        return False
    if sample['cpu_temp_c'] > cpu_temp or sample['cpu_percent'] > cpu_usage:
        return False
    return all(g.get('temp_c') is not None and g.get('utilization_percent') is not None
               and g['temp_c'] <= gpu_temp and g['utilization_percent'] <= gpu_usage for g in sample['gpus'])


def summarize(path, index):
    samples = [json.loads(line) for line in Path(path).read_text().splitlines()]
    samples = [s for s in samples if s['phase'] == 'inference' and s['run_index'] == index]
    def peak(key):
        values = [s.get(key) for s in samples if s.get(key) is not None]
        return max(values) if values else None
    return {'sample_count': len(samples), 'cpu_peak_percent': peak('cpu_percent'),
            'cpu_peak_temp_c': peak('cpu_temp_c'), 'ram_peak_used_bytes': peak('ram_used_bytes'),
            'gpu_peak_temp_c': max((g['temp_c'] for s in samples for g in s['gpus'] if g['temp_c'] is not None), default=None),
            'gpu_peak_memory_used_mib': max((g['memory_used_mib'] for s in samples for g in s['gpus'] if g.get('memory_used_mib') is not None), default=None),
            'gpu_peak_percent': max((g['utilization_percent'] for s in samples for g in s['gpus'] if g['utilization_percent'] is not None), default=None)}
