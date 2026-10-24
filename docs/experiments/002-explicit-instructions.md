# Experimento: instruções explícitas no LOG-001

## Pergunta e alteração
A variante esclarece classificação exclusiva de linhas, duplicatas válidas, campos ausentes e proibição de Markdown. Foi escrita **após observar erros no piloto**: é um experimento exploratório de adaptação ao caso, não evidência de generalização ou avaliação cega.

Original: cases/LOG-001, id LOG-001, versão 1.0.0.
Variante: cases/LOG-001-explicit, mesmo id, versão 1.1.0 e experiment=explicit_instructions_v1.
Entrada e referência são cópias byte a byte; avaliador log_exact_v1 permanece intacto. O prompt não fornece números das linhas inválidas nem respostas esperadas. Apenas o prompt e os metadados de versão/experimento mudam. O motor já aceita o mesmo id em outro diretório; nenhuma alteração de código necessária.

## Protocolo antes da execução
Começar com uma execução Qwen2.5 3B e, após leitura da resposta e resfriamento, decidir se amplia a outros participantes. Usar os mesmos parâmetros explícitos do piloto: temperature=0, seed=42, num_ctx=4096, num_predict=1024. Não forçar format=json, não habilitar ferramentas e não reutilizar histórico. Preservar reprovações; não ajustar o prompt entre modelos nesta versão. Cada comando cria novo registro com snapshots e hashes.

Pausar até condições térmicas próximas das iniciais e acompanhar sensores. Há histórico de desligamento térmico e 90 °C observados na rodada Gemma 4B; o roteiro não constitui proteção térmica automática. Não executar lotes.

## Comandos no homelab
Na raiz do projeto, confira git status antes de atualizar. Se houver alterações versionadas locais, preserve-as antes de continuar:

```bash
git status --short
git pull --ff-only origin feat/ollama-runner
source .venv/bin/activate
git rev-parse HEAD
llm-lab export --case cases/LOG-001-explicit --output prompt-log-001-explicit.txt
cat prompt-log-001-explicit.txt
```

O export recusa sobrescrita; se já existir, confira o arquivo antes de usá-lo.

Após resfriamento e com monitor aberto, executar somente uma rodada:

```bash
llm-lab run-ollama --case cases/LOG-001-explicit --model qwen2.5:3b
```

Compartilhar saída, resposta salva, temperatura observada e commit. A execução original continua no mesmo local; não substitua seus arquivos. Para participantes comerciais futuros, exportar esta variante e usar sessão independente, identificando modelo e condições.

## Análise prevista
Comparar validade JSON, schema, eventos e invalid_lines separadamente; examinar respostas mesmo se o parser parar no primeiro check. Relatar tempo e geração com limites conhecidos. O campo protocol=first_response continua descrevendo uma geração sem correções; o tratamento experimental é identificado na versão e experiment do caso. Não misturar taxas de aprovação das versões 1.0.0 e 1.1.0. Uma aprovação nova significa sucesso neste prompt e entrada, não correção geral do modelo.

## Estado
Preparado, ainda não executado no homelab. Redação da variante e documentação com assistência de IA; avaliação automática determinística. Para testar generalização, criar futuramente logs novos com referência congelada antes da inferência, sem escolher apenas entradas favoráveis.
