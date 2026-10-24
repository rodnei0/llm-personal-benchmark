import json
from pathlib import Path
import pytest
from llm_lab.core import load_case, record
from llm_lab.evaluators import evaluate_case

ROOT=Path(__file__).resolve().parents[1]
PLAN=json.loads((ROOT/'suites/knowledge-v1.json').read_text())


@pytest.mark.parametrize('case',PLAN['cases'])
def test_catalog_references_and_no_expected_leak(case,tmp_path):
    manifest,files,prompt,_=load_case(ROOT/case)
    expected=json.loads(files['expected'])
    assert '{{INPUT}}' not in prompt
    assert manifest['version']=='1.0.0'
    assert manifest['evaluator'] in {'numeric_json_v1','boolean_json_v1','human_rubric_v1'}
    if manifest['evaluator']=='human_rubric_v1':
        result=evaluate_case('Resposta a revisar.',expected,manifest['evaluator'])
        assert result['passed'] is None and result['status']=='pending_human_review'
        assert expected['required_concepts'] and expected['major_errors']
    else:
        value={'answer':expected['answer']}
        if 'unit' in expected:value['unit']=expected['unit']
        assert evaluate_case(json.dumps(value),expected,manifest['evaluator'])['passed']
        value['answer']=not value['answer'] if type(value['answer']) is bool else value['answer']+1
        assert not evaluate_case(json.dumps(value),expected,manifest['evaluator'])['passed']
    answer=tmp_path/'response.txt';answer.write_text('not an evaluated answer')
    _,saved=record(ROOT/case,answer,'fixture','none','test','test','demonstrative',tmp_path/'runs')
    assert saved['evaluator_version']==manifest['evaluator']


@pytest.mark.parametrize('reply',['```json\n{"answer":7}\n```','{"answer":true}','{"answer":7,"extra":0}','{"answer":NaN}'])
def test_numeric_rejects_bad_contract(reply):
    assert not evaluate_case(reply,{'answer':7},'numeric_json_v1')['passed']


def test_numeric_tolerance_and_unit():
    expected={'answer':20,'unit':'m','absolute_tolerance':1e-6}
    assert evaluate_case('{"answer":20.0000001,"unit":"m"}',expected,'numeric_json_v1')['passed']
    assert not evaluate_case('{"answer":20,"unit":"cm"}',expected,'numeric_json_v1')['passed']
