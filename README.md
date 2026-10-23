# LLM Lab

Laboratório pessoal e aberto para avaliar a utilidade de modelos locais e comerciais em tarefas reais. Documentação em português brasileiro.

**Versão 0.2.0: LOG-001, importação manual e execução via Ollama.** Os exemplos versionados continuam demonstrativos. Nenhum resultado de modelo real foi obtido durante o desenvolvimento.

## Instalação

Python 3.12 ou superior. Na raiz do projeto:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest -q
```

A execução usa somente a biblioteca padrão. pytest é dependência de desenvolvimento; setuptools é usado na instalação. As faixas em pyproject.toml não são um lockfile. O ambiente efetivamente testado consta em docs/execution-record.md.

## Primeiro experimento real

```bash
llm-lab export --case cases/LOG-001 --output prompt-log-001.txt
```

Abra uma conversa nova, preferencialmente temporária, sem memória/contexto do projeto nem ferramentas quando possível. Cole **todo** o conteúdo de prompt-log-001.txt. Salve somente a resposta recebida, sem editar, em resposta.txt. Não envie expected.json nem os testes ao participante.

```bash
llm-lab import-response --case cases/LOG-001 --response resposta.txt \
  --participant ChatGPT --model 'nome exibido na interface' \
  --interface 'ChatGPT web' \
  --configuration 'Conversa nova; ferramentas desativadas; demais parâmetros não expostos' \
  --kind real
```

`--elapsed-seconds 42.5` é opcional: use somente se cronometrado do envio à conclusão e registre limitações em configuration. O tempo de importação não é tempo de resposta.

Cada execução cria uma pasta nova em results/runs com resposta original, prompt, snapshots de entradas/referência, hashes e result.json. Não edite os registros; faça uma nova execução. O programa não impede alterações posteriores no filesystem. O resultado passed=false é um resultado válido do benchmark, não falha do comando; erros de uso retornam código 2.

## Demonstração local, sem modelo

```bash
llm-lab import-response --case cases/LOG-001 --response cases/LOG-001/expected.json \
  --participant reference-fixture --model none --interface fixture \
  --configuration 'Resposta de referência; não houve inferência' \
  --kind demonstrative --output-root results/examples
```

## Escopo e documentação

- [Metodologia](docs/methodology.md)
- [Limitações](docs/limitations.md)
- [Roadmap](docs/roadmap.md)
- [Decisão inicial](docs/decisions/001-minimal-pilot.md)
- [Registro de execução](docs/execution-record.md)

Os cinco casos planejados são LOG-001 (extração), PY-001 (script), SQL-001 (consulta), BUG-001 (correção) e INC-001 (incidente). Apenas LOG-001 está implementado.

Não há licença concedida ainda: a escolha da licença open source está pendente antes da publicação. Nenhum peso de modelo é distribuído. Nenhuma operação GitHub é necessária para executar este piloto.


## Executar no Ollama

Com Ollama instalado e ativo no próprio homelab:

```bash
ollama pull qwen2.5:3b
llm-lab run-ollama --case cases/LOG-001 --model qwen2.5:3b
```

Uma execução por comando, sem retentativas. O adaptador usa `/api/generate`, sem histórico e sem forçar formato JSON. Registra requisição, resposta completa da API, tempo de ponta a ponta e tokens/s de geração em `result.json`. `--host` permite selecionar outro servidor; o prompt será enviado ao endereço informado.

Padrões explícitos: temperatura 0, seed 42, contexto 4096, limite de saída 1024 e timeout HTTP 600 segundos. Todos possuem opções CLI correspondentes (`llm-lab run-ollama --help`). O template e demais configurações do modelo instalado continuam valendo. Seed não garante determinismo. `keep_alive=0` pede descarregamento após a execução; o estado inicial de cache não é controlado.

No ASUS com histórico de superaquecimento, faça uma única execução acompanhando o dashboard térmico existente. Este adaptador ainda não possui proteção térmica, coleta de sensores ou cancelamento confirmado no servidor. Timeout HTTP não comprova interrupção da inferência; não inicie outra execução até conferir o Ollama. Falhas de transporte retornam código 2, sem criar resultado; registre-as no diário da rodada e não as descarte da análise.

Antes de comparar rodadas, registre `ollama --version`, `ollama list` (identificador do modelo), hardware e condições térmicas no diário. A identificação automática do digest do modelo está pendente. Tokens/s usa `eval_count / (eval_duration / 1e9)` e não inclui carregamento; o tempo total do cliente inclui a requisição. Não compare tokens/s entre tokenizadores como se fossem equivalentes.

Referência da API: https://docs.ollama.com/api/generate
