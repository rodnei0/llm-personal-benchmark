import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import pytest

from llm_lab.ollama import run
from llm_lab.core import load_case
from test_pilot import CASE, EXPECTED


@pytest.fixture
def server():
    state = {"reply": {"model": "test:tiny", "done": True, "done_reason": "stop",
                       "response": json.dumps(EXPECTED), "eval_count": 20,
                       "eval_duration": 2_000_000_000}, "requests": []}

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            state["requests"].append((self.path, json.loads(self.rfile.read(int(self.headers["Content-Length"])))))
            self.send_response(state.get("status", 200))
            self.end_headers()
            self.wfile.write(json.dumps(state["reply"]).encode())

        def log_message(self, *args):
            pass

    http = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=http.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{http.server_port}", state
    http.shutdown()
    http.server_close()
    thread.join()


def test_http_roundtrip(server, tmp_path):
    host, state = server
    target, result = run(CASE, "test:tiny", tmp_path, host=host)
    assert result["evaluation"]["passed"]
    assert result["metrics"]["tokens_per_second"] == 10
    assert result["metrics"]["elapsed_source"] == "perf_counter"
    assert result["metrics"]["elapsed_seconds"] > 0
    assert result["inference"]["response"] == state["reply"]
    assert (target / "response.txt").read_text() == state["reply"]["response"]
    assert json.loads((target / "result.json").read_text()) == result
    path, request = state["requests"][0]
    assert len(state["requests"]) == 1
    assert path == "/api/generate"
    assert request["prompt"] == load_case(CASE)[2]
    assert request["stream"] is False and request["keep_alive"] == 0
    assert "format" not in request and "context" not in request


def test_incorrect_model_answer_is_valid_run(server, tmp_path):
    host, state = server
    state["reply"]["response"] = "```json\n{}\n```"
    state["reply"]["eval_duration"] = 0
    _, result = run(CASE, "test:tiny", tmp_path, host=host)
    assert not result["evaluation"]["passed"]
    assert result["metrics"]["tokens_per_second"] is None


@pytest.mark.parametrize("reply", [{}, {"done": False, "response": "partial"}, [], {"done": True, "response": None}])
def test_invalid_transport_response(server, tmp_path, reply):
    host, state = server
    state["reply"] = reply
    with pytest.raises(ValueError, match="inválida"):
        run(CASE, "test:tiny", tmp_path, host=host)
    assert not list(tmp_path.iterdir())


def test_http_failure_does_not_retry(server, tmp_path):
    host, state = server
    state["status"] = 500
    with pytest.raises(ValueError, match="sem retentativa"):
        run(CASE, "test:tiny", tmp_path, host=host)
    assert len(state["requests"]) == 1
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize("kwargs", [{"timeout": 0}, {"timeout": float("nan")},
                                   {"num_ctx": 0}, {"num_predict": -1},
                                   {"temperature": float("inf")},
                                   {"host": "http://user:password@localhost"}])
def test_invalid_settings(kwargs, tmp_path):
    with pytest.raises(ValueError):
        run(CASE, "test:tiny", tmp_path, **kwargs)
