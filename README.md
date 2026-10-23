# LLM Lab

Laboratório pessoal e aberto para avaliar a utilidade de modelos locais e comerciais em tarefas reais. Documentação em português brasileiro.

**Versão 0.1.0: apenas LOG-001 e importação manual.** Não há inferência Ollama, telemetria nem resultados reais nesta entrega. Os exemplos são demonstrativos e usam a resposta de referência, não um modelo.

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
