import copy
import json
from pathlib import Path
import pytest
from llm_lab.core import evaluate, load_case, record, digest
from llm_lab.cli import main

CASE = Path(__file__).resolve().parents[1] / "cases" / "LOG-001"
EXPECTED = json.loads((CASE / "expected.json").read_text())


def test_reference_passes():
    assert evaluate(json.dumps(EXPECTED), EXPECTED)["passed"]


@pytest.mark.parametrize("mutation", ["missing", "duplicate", "order", "invented", "invalid", "extra", "bool"])
def test_wrong_answers_fail(mutation):
    value = copy.deepcopy(EXPECTED)
    if mutation == "missing": value["events"].pop()
    elif mutation == "duplicate": value["events"].append(value["events"][0])
    elif mutation == "order": value["events"].reverse()
    elif mutation == "invented": value["events"][0]["ip"] = "192.0.2.99"
    elif mutation == "invalid": value["invalid_lines"] = [5]
    elif mutation == "extra": value["explanation"] = "ok"
    elif mutation == "bool": value["invalid_lines"] = [True, 6]
    assert not evaluate(json.dumps(value), EXPECTED)["passed"]


@pytest.mark.parametrize("response", ['```json\n{}\n```', '{', '{"events":[],"events":[],"invalid_lines":[]}', 'NaN', '[]', '{} trailing'])
def test_invalid_or_wrong_json_fails(response):
    assert not evaluate(response, EXPECTED)["passed"]


def test_export_contains_no_reference():
    _, _, prompt, _ = load_case(CASE)
    assert "{{INPUT}}" not in prompt
    assert (CASE / "input.log").read_text() in prompt
    assert '"invalid_lines": [5, 6]' not in prompt


def test_record_roundtrip_and_unique_ids(tmp_path):
    response = tmp_path / "answer.txt"
    response.write_text(json.dumps(EXPECTED))
    paths = []
    for _ in range(2):
        target, result = record(CASE, response, "fixture", "none", "test", "none",
                                "demonstrative", tmp_path / "runs")
        paths.append(target)
        assert result["evaluation"]["passed"]
        assert result["data_kind"] == "demonstrative"
        assert result["metrics"]["elapsed_seconds"] is None
        assert (target / "response.txt").read_bytes() == response.read_bytes()
        assert result["hashes"]["response"] == digest(response.read_bytes())
        assert json.loads((target / "result.json").read_text()) == result
    assert paths[0] != paths[1]


def test_cli_export_refuses_overwrite(tmp_path, monkeypatch):
    output = tmp_path / "prompt.txt"
    output.write_text("preserve")
    monkeypatch.setattr("sys.argv", ["llm-lab", "export", "--case", str(CASE), "--output", str(output)])
    with pytest.raises(SystemExit) as error:
        main()
    assert error.value.code == 2
    assert output.read_text() == "preserve"
