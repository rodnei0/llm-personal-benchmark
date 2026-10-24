import json
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from unittest.mock import patch

import pytest
from llm_lab.batch import run_batch
from llm_lab.telemetry import recovery_ready, Sampler

CASE = Path(__file__).resolve().parents[1] / 'cases' / 'LOG-001'
SAMPLE = {'at': 'test', 'cpu_temp_c': 52, 'cpu_percent': 5, 'ram_used_bytes': 123, 'gpus': [], 'errors': []}


@pytest.fixture
def api():
    state = {'requests': []}
    expected = (CASE / 'expected.json').read_text()
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200); self.end_headers()
            reply = {'version': 'test'} if self.path == '/api/version' else {'models': [{'name': m, 'digest': m + '-digest'} for m in ['a:1', 'b:1']]}
            self.wfile.write(json.dumps(reply).encode())
        def do_POST(self):
            req = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            state['requests'].append(req)
            self.send_response(200); self.end_headers()
            reply = {'model': req['model'], 'response': expected if req['model'] == 'a:1' else '```json\n{}\n```', 'done': True, 'done_reason': 'stop', 'eval_count': 10, 'eval_duration': 1_000_000_000}
            self.wfile.write(json.dumps(reply).encode())
        def log_message(self, *args): pass
    http = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = Thread(target=http.serve_forever, daemon=True); thread.start()
    yield f'http://127.0.0.1:{http.server_port}', state
    http.shutdown(); http.server_close(); thread.join()


def test_sequential_runs_cooldown_and_artifacts(api, tmp_path):
    host, state = api
    with patch('llm_lab.telemetry.Sampler.sample', return_value=dict(SAMPLE)), patch('llm_lab.batch.time.sleep') as sleep:
        root, data = run_batch(CASE, ['a:1','b:1'], host=host, output_root=tmp_path, repetitions=2, temperature_check=False)
    assert [r['model'] for r in state['requests']] == ['a:1','b:1','a:1','b:1']
    assert sleep.call_count == 3
    sleep.assert_called_with(30)
    assert [r['evaluation']['passed'] for r in data['runs']] == [True,False,True,False]
    assert [r['repetition'] for r in data['runs']] == [1,1,2,2]
    assert json.loads((root/'batch.json').read_text()) == data
    assert (root/'case'/'input.log').read_bytes() == (CASE/'input.log').read_bytes()
    for item in data['runs']:
        assert (root/item['path']/'response.txt').is_file()
    assert (root/'telemetry.jsonl').read_text()
    assert data['ollama_tags']['models'][0]['digest'] == 'a:1-digest'
    assert 'b:1' in (root/'summary.md').read_text()


@pytest.mark.parametrize('failure',[ValueError('timeout simulado'),KeyboardInterrupt()])
def test_failure_or_interrupt_stops_without_retry(api,tmp_path,failure):
    host,state=api
    with patch('llm_lab.telemetry.Sampler.sample', return_value=dict(SAMPLE)), patch('llm_lab.batch.run',side_effect=failure) as runner:
        with pytest.raises(ValueError):
            run_batch(CASE,['a:1','b:1'],host=host,output_root=tmp_path,temperature_check=False)
    assert runner.call_count==1
    data=json.loads(next(tmp_path.glob('*/batch.json')).read_text())
    assert data['status'] in ('failed','interrupted')
    assert data['runs'][0]['status']==data['status']


def test_hot_machine_stops_before_inference(api,tmp_path):
    host,state=api
    with patch('llm_lab.batch.cpu_temperature',return_value=80), patch('llm_lab.telemetry.Sampler.sample',return_value={**SAMPLE,'cpu_temp_c':80}):
        with pytest.raises(ValueError,match='recuperação'):
            run_batch(CASE,['a:1'],host=host,output_root=tmp_path,max_cooldown_wait=0,stable_seconds=0)
    assert not state['requests']
    assert json.loads(next(tmp_path.glob('*/batch.json')).read_text())['status']=='failed'


def test_missing_model_preflight(api,tmp_path):
    host,state=api
    with patch('llm_lab.telemetry.Sampler.sample',return_value=dict(SAMPLE)):
        with pytest.raises(ValueError,match='não instalados'):
            run_batch(CASE,['missing'],host=host,output_root=tmp_path,temperature_check=False)
    assert not state['requests']


@pytest.mark.parametrize('kwargs',[{'repetitions':0},{'cooldown':float('nan')},{'cooldown':0},{'cooldown':29},{'timeout':-1},{'num_ctx':0},{'host':'file:///tmp/model'},{'sample_interval':0}])
def test_invalid_settings(tmp_path,kwargs):
    with pytest.raises(ValueError):
        run_batch(CASE,['a:1'],output_root=tmp_path,temperature_check=False,**kwargs)
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize('update,expected', [({},True),({'cpu_percent':None},False),({'cpu_temp_c':61},False),({'cpu_percent':30},False),({'gpus':[{'temp_c':70,'utilization_percent':0}]},False),({'gpus':[{'temp_c':52,'utilization_percent':None}]},False)])
def test_recovery_gate(update,expected):
    assert recovery_ready({**SAMPLE,**update},cpu_temp=60,gpu_temp=60,cpu_usage=20,gpu_usage=10)==expected


def test_sampler_records_unavailable_gpu():
    with patch('llm_lab.telemetry.cpu_temperature',return_value=52), patch('llm_lab.telemetry.subprocess.check_output',side_effect=FileNotFoundError('no GPU')):
        sample=Sampler().sample()
    assert sample['cpu_temp_c']==52
    assert sample['cpu_percent'] is None
    assert sample['gpus']==[]
    assert sample['errors']


def test_cool_machine_can_start_with_gate_enabled(api,tmp_path):
    host,state=api
    with patch('llm_lab.batch.cpu_temperature',return_value=52), patch('llm_lab.telemetry.Sampler.sample',return_value=dict(SAMPLE)), patch('shutil.which',return_value=None):
        _,data=run_batch(CASE,['a:1'],host=host,output_root=tmp_path,stable_seconds=0)
    assert len(state['requests'])==1
    assert data['runs'][0]['telemetry_before']['cpu_temp_c']==52


def test_guard_abort_records_shutdown_and_stops_batch(api,tmp_path):
    from unittest.mock import Mock
    from llm_lab.thermal import GuardAbort
    host,state=api
    stopper=Mock();stopper.preflight.return_value={}
    with patch('llm_lab.batch.ServiceStopper',return_value=stopper),patch('llm_lab.batch.cpu_temperature',return_value=52),patch('llm_lab.telemetry.Sampler.sample',return_value=dict(SAMPLE)),patch('shutil.which',return_value=None),patch('llm_lab.batch.guarded_run',side_effect=GuardAbort('CPU quente',{'confirmed':False})):
        with pytest.raises(ValueError,match='aborted'):
            run_batch(CASE,['a:1','b:1'],host=host,output_root=tmp_path,thermal_guard=True,stable_seconds=0)
    data=json.loads(next(tmp_path.glob('*/batch.json')).read_text())
    assert data['status']=='aborted' and data['shutdown']['confirmed'] is False
    assert len(data['runs'])==1 and data['runs'][0]['evaluation'] is None
    assert not state['requests']
