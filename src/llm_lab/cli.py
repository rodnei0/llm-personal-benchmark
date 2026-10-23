import argparse
import json
import math
from pathlib import Path
from .core import load_case, record
from .ollama import run


def nonnegative(value):
    number = float(value)
    if not math.isfinite(number) or number < 0:
        raise argparse.ArgumentTypeError("Informe segundos finitos e não negativos")
    return number


def main():
    parser = argparse.ArgumentParser(description="LLM Lab — piloto LOG-001")
    commands = parser.add_subparsers(dest="command", required=True)
    export = commands.add_parser("export", help="Exporta somente o prompt e entrada")
    export.add_argument("--case", required=True)
    export.add_argument("--output", required=True)
    imp = commands.add_parser("import-response", help="Preserva e avalia resposta manual")
    imp.add_argument("--case", required=True)
    imp.add_argument("--response", required=True)
    imp.add_argument("--participant", required=True)
    imp.add_argument("--model", required=True)
    imp.add_argument("--interface", required=True)
    imp.add_argument("--configuration", required=True, help="Configuração visível e limitações")
    imp.add_argument("--kind", choices=["real", "demonstrative"], required=True)
    imp.add_argument("--elapsed-seconds", type=nonnegative)
    imp.add_argument("--output-root", default="results/runs")
    ollama = commands.add_parser("run-ollama", help="Executa uma resposta via Ollama")
    ollama.add_argument("--case", required=True)
    ollama.add_argument("--model", required=True)
    ollama.add_argument("--host", default="http://127.0.0.1:11434")
    ollama.add_argument("--timeout", type=float, default=600)
    ollama.add_argument("--temperature", type=float, default=0.0)
    ollama.add_argument("--seed", type=int, default=42)
    ollama.add_argument("--num-ctx", type=int, default=4096)
    ollama.add_argument("--num-predict", type=int, default=1024)
    ollama.add_argument("--output-root", default="results/runs")
    args = parser.parse_args()
    try:
        if args.command == "export":
            _, _, prompt, _ = load_case(args.case)
            with Path(args.output).open("x", encoding="utf-8") as stream:
                stream.write(prompt)
            print(args.output)
        elif args.command == "run-ollama":
            target, result = run(args.case, args.model, args.output_root,
                                 host=args.host, timeout=args.timeout,
                                 temperature=args.temperature, seed=args.seed,
                                 num_ctx=args.num_ctx, num_predict=args.num_predict)
            print(json.dumps({"path": str(target), "evaluation": result["evaluation"],
                              "metrics": result["metrics"]}, ensure_ascii=False))
        else:
            target, result = record(args.case, args.response, args.participant, args.model,
                                    args.interface, args.configuration, args.kind,
                                    args.output_root, args.elapsed_seconds)
            print(json.dumps({"path": str(target), "evaluation": result["evaluation"]}, ensure_ascii=False))
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(2, f"Erro: {exc}\n")


if __name__ == "__main__":
    main()

