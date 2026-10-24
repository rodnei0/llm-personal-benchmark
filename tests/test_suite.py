import json
import shutil
from pathlib import Path
from unittest.mock import patch
import pytest

from llm_lab.suite import run_suite
from test_batch import api, SAMPLE

ROOT=Path(__file__).resolve().parents[1]


def plan(tmp_path):
    source=tmp_path/'source';(source/'suites').mkdir(parents=True)
    for name in ['MATH-001','SCI-001']:
        shutil.copytree(ROOT/'cases'/name,source/'cases'/name)
    p=source/'suites'/'test.json'
    p.write_text(json.dumps({'id':'test','cases':['cases/MATH-001','cases/SCI-001']}))
    return p


def test_suite_freezes_cases_and_keeps_manual_pending(api,tmp_path):
    host,state=api
    p=plan(tmp_path)
    with patch('llm_lab.telemetry.Sampler.sample',return_value=dict(SAMPLE)),patch('llm_lab.suite.time.sleep') as sleep:
        root,data=run_suite(p,['a:1'],host=host,temperature_check=False,output_root=tmp_path/'out')
    assert data['status']=='completed' and len(data['batches'])==2
    assert len(state['requests'])==2
    sleep.assert_called_once_with(30)
    assert (root/'cases'/'0'/'expected.json').is_file()
    b=json.loads((root/data['batches'][1]['path']/'batch.json').read_text())
    assert b['runs'][0]['evaluation']['status']=='pending_human_review'
    assert b['runs'][0]['evaluation']['passed'] is None


def test_suite_stops_after_first_batch_error(tmp_path):
    p=plan(tmp_path)
    with patch('llm_lab.suite.run_batch',side_effect=ValueError('aborted')) as run:
        with pytest.raises(ValueError,match='aborted'):
            run_suite(p,['a:1'],output_root=tmp_path/'out')
    assert run.call_count==1
    assert json.loads(next((tmp_path/'out').glob('*/suite.json')).read_text())['status']=='failed'
