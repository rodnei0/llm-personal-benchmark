import argparse
import json
import math
from pathlib import Path
from .core import load_case, record
from .ollama import run
from .batch import run_batch
from .thermal import check_guard
from .suite import run_suite


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
    batch = commands.add_parser("batch-ollama", help="Executa modelos sequencialmente com intervalo e resumo")
    suite = commands.add_parser("suite-ollama", help="Executa vários casos, modelos e telemetria sequencialmente")
    suite.add_argument("--suite", required=True)
    for target in (batch, suite):
        target.add_argument("--models", nargs="+", required=True)
        target.add_argument("--repetitions", type=int, default=1)
        target.add_argument("--cooldown", type=nonnegative, default=30, help="Pausa mínima entre rodadas, pelo menos 30 s (padrão: 30)")
        target.add_argument("--max-start-temp", type=float, default=60)
        target.add_argument("--max-cooldown-wait", type=nonnegative, default=900)
        target.add_argument("--max-gpu-temp", type=float, default=60)
        target.add_argument("--max-cpu-usage", type=float, default=20)
        target.add_argument("--max-gpu-usage", type=float, default=10)
        target.add_argument("--sample-interval", type=float, default=2)
        target.add_argument("--stable-seconds", type=float, default=10)
        target.add_argument("--no-temperature-check", action="store_true")
        target.add_argument("--output-root", default="results/runs/batches")
        target.add_argument("--host", default="http://127.0.0.1:11434")
        target.add_argument("--timeout", type=float, default=600)
        target.add_argument("--temperature", type=float, default=0.0)
        target.add_argument("--seed", type=int, default=42)
        target.add_argument("--num-ctx", type=int, default=4096)
        target.add_argument("--num-predict", type=int, default=1024)
        target.add_argument("--thermal-guard", action="store_true", help="Autoriza parada de ollama.service em corte, erro ou interrupção durante geração")
        target.add_argument("--abort-cpu-temp", type=float, default=85)
        target.add_argument("--abort-gpu-temp", type=float, default=80)
    batch.add_argument("--case", required=True)
    check = commands.add_parser("thermal-check", help="Verifica controle térmico local sem inferência")
    check.add_argument("--host", default="http://127.0.0.1:11434")
    check.add_argument("--test-stop", action="store_true", help="Para o serviço sem modelo carregado e confirma encerramento")
    args = parser.parse_args()
    try:
        if args.command == "thermal-check":
            print(json.dumps(check_guard(args.host, args.test_stop), ensure_ascii=False, indent=2))
        elif args.command == "export":
            _, _, prompt, _ = load_case(args.case)
            with Path(args.output).open("x", encoding="utf-8") as stream:
                stream.write(prompt)
            print(args.output)
        elif args.command in ("batch-ollama", "suite-ollama"):
            runner = run_batch if args.command == "batch-ollama" else run_suite
            source = args.case if args.command == "batch-ollama" else args.suite
            target, result = runner(source, args.models,
                repetitions=args.repetitions, cooldown=args.cooldown,
                output_root=args.output_root, temperature_check=not args.no_temperature_check,
                max_start_temp=args.max_start_temp, max_cooldown_wait=args.max_cooldown_wait,
                max_gpu_temp=args.max_gpu_temp, max_cpu_usage=args.max_cpu_usage,
                max_gpu_usage=args.max_gpu_usage, sample_interval=args.sample_interval,
                stable_seconds=args.stable_seconds, thermal_guard=args.thermal_guard,
                abort_cpu_temp=args.abort_cpu_temp, abort_gpu_temp=args.abort_gpu_temp,
                host=args.host, timeout=args.timeout, temperature=args.temperature,
                seed=args.seed, num_ctx=args.num_ctx, num_predict=args.num_predict)
            print(json.dumps({"path": str(target), "status": result["status"]}, ensure_ascii=False))
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

