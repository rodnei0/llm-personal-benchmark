"""Sequência de casos congelados, cada um com seu lote e critérios próprios."""
import json
from pathlib import Path
import shutil
import time
from datetime import datetime, timezone
from uuid import uuid4

from .batch import run_batch
from .core import load_case


def run_suite(suite_path, models, *, output_root='results/runs/suites', **options):
    source = Path(suite_path).resolve()
    plan = json.loads(source.read_text())
    if not plan.get('cases') or len(set(plan['cases'])) != len(plan['cases']):
        raise ValueError('Suíte exige casos não vazios e sem duplicatas')
    cases = []
    for name in plan['cases']:
        directory = (source.parent.parent / name).resolve()
        if not directory.is_relative_to(source.parent.parent) or not directory.is_dir():
            raise ValueError('Caminho de caso inválido na suíte')
        load_case(directory)
        cases.append(directory)
    root = Path(output_root) / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid4().hex[:12])
    root.mkdir(parents=True, exist_ok=False)
    frozen = root / 'cases'
    frozen.mkdir()
    for index, directory in enumerate(cases):
        shutil.copytree(directory, frozen / str(index))
    data = {'schema_version': '1.0.0', 'suite': plan, 'status': 'running',
            'models': models, 'options': options, 'batches': [],
            'started_at': datetime.now(timezone.utc).isoformat()}
    def save():
        temp = root / 'suite.json.tmp'
        temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
        temp.replace(root / 'suite.json')
        lines = ['# Suíte LLM Lab', '', 'Estado: ' + data['status'], '',
                 'Casos conceituais podem estar pendentes de revisão humana. Sem ranking agregado.', '']
        for item in data['batches']:
            if 'path' in item:
                lines.append(f"- {item['case']}: [Resumo]({item['path']}/summary.md)")
        if 'error' in data:
            lines += ['', data['error']]
        (root / 'summary.md').write_text('\n'.join(lines) + '\n')
    save()
    print(f'Suíte: {root}', flush=True)
    try:
        for index, directory in enumerate(cases):
            if index:
                time.sleep(options.get('cooldown', 30))
            item = {'case': plan['cases'][index], 'status': 'running'}
            data['batches'].append(item)
            save()
            batch_root, batch_data = run_batch(frozen / str(index), models,
                                               output_root=root / 'batches', **options)
            item.update(status=batch_data['status'], path=str(batch_root.relative_to(root)))
            save()
        data['status'] = 'completed'
    except KeyboardInterrupt:
        data.update(status='interrupted', error='Interrompido entre casos; conferir os registros dos lotes')
    except Exception as exc:
        data.update(status='failed', error=str(exc))
    finally:
        for item in data['batches']:
            if item['status'] == 'running':
                item['status'] = data['status']
        data['finished_at'] = datetime.now(timezone.utc).isoformat()
        save()
    if data['status'] != 'completed':
        raise ValueError(f"Suíte encerrada: {data.get('error')}. Registros: {root}")
    return root, data
