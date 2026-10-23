"""Uma requisição, sem histórico, ferramentas ou retentativas automáticas."""
import json
import math
import tempfile
import time
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from .core import load_case, record


def run(directory, model, output_root="results/runs", *,
        host="http://127.0.0.1:11434", timeout=600,
        temperature=0.0, seed=42, num_ctx=4096, num_predict=1024):
    if not model.strip():
        raise ValueError("Informe o modelo instalado no Ollama")
    url = urlsplit(host)
    if url.scheme not in ("http", "https") or not url.hostname or url.username or url.password or url.query or url.fragment or url.path not in ("", "/"):
        raise ValueError("Host deve ser uma origem HTTP(S), sem credenciais ou caminho")
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("Timeout deve ser finito e positivo")
    if not math.isfinite(temperature) or temperature < 0 or num_ctx <= 0 or num_predict <= 0:
        raise ValueError("Parâmetros de geração inválidos")
    _, _, prompt, _ = load_case(directory)
    payload = {"model": model, "prompt": prompt, "stream": False,
               "keep_alive": 0,
               "options": {"temperature": temperature, "seed": seed,
                           "num_ctx": num_ctx, "num_predict": num_predict}}
    request = Request(host.rstrip("/") + "/api/generate",
                      data=json.dumps(payload).encode(),
                      headers={"Content-Type": "application/json"})
    started = time.perf_counter()
    try:
        with urlopen(request, timeout=timeout) as stream:
            reply = json.load(stream)
    except (URLError, TimeoutError, OSError) as exc:
        raise ValueError(f"Falha no Ollama (sem retentativa): {exc}") from exc
    elapsed = time.perf_counter() - started
    if not isinstance(reply, dict) or reply.get("done") is not True or not isinstance(reply.get("response"), str):
        raise ValueError("Resposta incompleta ou inválida do Ollama")
    count, duration = reply.get("eval_count"), reply.get("eval_duration")
    speed = (count * 1e9 / duration
             if type(count) is int and count >= 0 and type(duration) is int and duration > 0 else None)
    inference = {"provider": "ollama", "endpoint": host.rstrip("/"),
                 "request": payload, "response": reply,
                 "metrics": {"elapsed_seconds": elapsed, "tokens_per_second": speed}}
    with tempfile.TemporaryDirectory() as temp:
        response = Path(temp) / "response.txt"
        response.write_text(reply["response"], encoding="utf-8")
        return record(directory, response, "Ollama", reply.get("model", model),
                      "Ollama HTTP /api/generate", json.dumps(payload["options"]),
                      "real", output_root, elapsed, inference=inference)
