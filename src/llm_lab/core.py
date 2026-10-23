"""Caso congelado, avaliação estrita e resultados rastreáveis, sem inferência."""
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone
from uuid import uuid4
from . import __version__


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load_case(directory):
    directory = Path(directory)
    manifest_bytes = (directory / "case.json").read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest["id"] != "LOG-001" or manifest["evaluator"] != "log_exact_v1":
        raise ValueError("Caso/avaliador não suportado nesta versão")
    files = {key: (directory / manifest[key]).read_bytes()
             for key in ("prompt", "input", "expected")}
    prompt = files["prompt"].decode().replace("{{INPUT}}", files["input"].decode())
    return manifest, files, prompt, digest(manifest_bytes)


def strict_json(text):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("Chave JSON duplicada")
            result[key] = value
        return result
    def invalid(value):
        raise ValueError("Constante JSON inválida: " + value)
    return json.loads(text, object_pairs_hook=pairs, parse_constant=invalid)


def evaluate(response, expected):
    try:
        value = strict_json(response)
    except (ValueError, TypeError) as exc:
        return {"passed": False, "checks": {"valid_json": False}, "error": str(exc)}
    shape = (type(value) is dict and set(value) == {"events", "invalid_lines"}
             and type(value["events"]) is list and type(value["invalid_lines"]) is list)
    fields = {"timestamp", "host", "service", "user", "ip"}
    schema = shape and all(type(e) is dict and set(e) == fields
                           and all(type(v) is str for v in e.values()) for e in value["events"])
    schema = schema and all(type(n) is int for n in value["invalid_lines"])
    checks = {"valid_json": True, "schema": bool(schema),
              "events_exact": bool(schema and value["events"] == expected["events"]),
              "invalid_lines_exact": bool(schema and value["invalid_lines"] == expected["invalid_lines"])}
    return {"passed": all(checks.values()), "checks": checks, "error": None}


def record(directory, response_path, participant, model, interface, configuration,
           kind, output_root, elapsed_seconds=None):
    manifest, files, prompt, manifest_hash = load_case(directory)
    raw = Path(response_path).read_bytes()
    response = raw.decode("utf-8")
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:12]
    target = Path(output_root) / run_id
    target.mkdir(parents=True, exist_ok=False)
    result = {"schema_version": "1.0.0", "run_id": run_id,
              "recorded_at": datetime.now(timezone.utc).isoformat(),
              "data_kind": kind, "protocol": "first_response",
              "status": "completed", "executor_version": __version__,
              "evaluator_version": "log_exact_v1", "case": manifest,
              "hashes": {"manifest": manifest_hash, "rendered_prompt": digest(prompt.encode()),
                         "response": digest(raw), **{k: digest(v) for k,v in files.items()}},
              "participant": {"name": participant, "model_reported": model,
                              "interface": interface, "configuration": configuration},
              "attempt": 1, "human_interventions": 0,
              "metrics": {"elapsed_seconds": elapsed_seconds,
                          "elapsed_source": "manual" if elapsed_seconds is not None else None,
                          "tokens_per_second": None, "cpu": None, "ram": None, "temperature": None,
                          "unavailable_reason": "Importação manual; sem telemetria de inferência"},
              "evaluation": evaluate(response, strict_json(files["expected"].decode()))}
    (target / "response.txt").write_bytes(raw)
    (target / "prompt.txt").write_text(prompt, encoding="utf-8")
    for key, content in files.items():
        (target / (key + ".snapshot")).write_bytes(content)
    (target / "case.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (target / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    return target, result
