# LOG-001 — primeiro lote publicado com telemetria

Fonte: commit de resultados 30a736fab13fa332574dea8ddf9971a1b788cfb5; lote results/published/batches/20261024T004319Z-f52921fff6a1. Código executado: d8dd7b69dd54b579d0af278cb496032c2370cd69. Lote concluído em 2026-10-23, 20:43–20:50 America/Cuiaba (timestamps dos arquivos em UTC no dia 24).

Leitura direta de batch.json, summary.md, telemetry.jsonl e dos três response.txt/result.json. Hashes das respostas conferidos contra os registros; mesmo hash de prompt dae6934e5bffbd6239a1383171164244e45e2d8e30b3856f53d0317790c215e4 em todas as rodadas. Caso original LOG-001 1.0.0; não é a variante explícita.

## Resultado funcional

| Modelo (Q4_K_M) | Tempo cliente | Tokens gerados | Tokens/s | Avaliação |
| --- | --- | --- | --- | --- |
| Qwen2.5 3B | 25.76 s | 216 | 11.24 | JSON/schema corretos; eventos e linhas inválidas incorretos |
| Qwen2.5 Coder 3B Instruct | 20.30 s | 155 | 11.31 | Eventos exatos; faltou linha 6 em invalid_lines |
| Gemma 3 1B | 17.97 s | 419 | 28.67 | JSON estrito reprovado; formato e conteúdo também incorretos na inspeção |

Qwen generalista repetiu byte a byte a resposta das duas primeiras execuções manuais: incluiu Daniel com ip vazio e listou invalid_lines=[3,5]. O Coder retornou somente Bruno e Carla corretamente e invalid_lines=[5], omitindo a linha malformada 6. Logo a especialização mostrou melhora observada na seleção dos eventos neste caso, mas não aprovação completa. Não transformar checks em nota percentual: têm pesos semânticos diferentes e não são uma escala calibrada.

Gemma 1B incluiu Markdown, array raiz, sucessos de Ana/Carla, Daniel com IP ausente preenchido e omitiu invalid_lines, repetindo o padrão anterior. O parser parou no primeiro caractere; os erros adicionais são inspeção qualitativa, não checks automáticos executados. Todas as gerações terminaram com done_reason=stop; nenhuma resposta atingiu num_predict=1024.

Coder gerou menos tokens que o generalista e levou menos tempo total; taxas de geração foram próximas. Não atribuir essa diferença automaticamente a backend mais eficiente. Não comparar tokens/s do Gemma como equivalência direta de trabalho útil ou qualidade.

## Telemetria amostrada durante inferência

| Modelo | CPU inicial/pico | GPU inicial/pico | Pico RAM do sistema | Pico VRAM |
| --- | --- | --- | --- | --- |
| Qwen2.5 3B | 51 / 86 °C | 49 / 74 °C | 4.26 GiB | 1035 MiB |
| Qwen Coder 3B | 51 / 85 °C | 50 / 75 °C | 4.02 GiB | 1030 MiB |
| Gemma 3 1B | 52 / 77 °C | 50 / 79 °C | 3.89 GiB | 947 MiB |

225 amostras no lote: 1 setup, 15 recovery, 32 inference e 177 cooldown; nenhuma amostra com errors preenchido. Por inferência: 13, 10 e 9 amostras, respectivamente. CPU/RAM são uso global, não isolado do processo Ollama. Picos são amostrados e podem perder transientes. Não há medição de energia ou throttling. GPU esteve ativa nos três testes; isso não determina a fração de camadas ou de trabalho CPU/GPU.

Gemma teve menor pico de CPU, mas maior pico de GPU neste lote. Portanto observar apenas temperatura de CPU não representa toda a carga térmica. Os limites de recuperação não são limites de pico durante inferência.

## Validação do lote

Modelos executados em sequência, com uma repetição cada; todos começaram com CPU <=52 °C, GPU <=50 °C e baixo uso. O lote registrou Ollama 0.40.10, digests completos, parâmetros temperature=0, seed=42, num_ctx=4096, num_predict=1024 e case snapshots.

Este lote usou cooldown_seconds=180. A mudança posterior para mínimo/padrão de 30 s não altera esses registros. Recuperação adaptativa permaneceu habilitada (CPU/GPU <=60 °C, uso CPU <=20%, GPU <=10%, estabilidade 10 s). As condições de início foram atendidas; não houve necessidade de espera prolongada além da pausa mais verificação. Testar 30 s exige nova rodada se quisermos quantificar o comportamento dessa política.

O metadata git_status lista arquivos não versionados, incluindo a pasta de resultados criada, mas não modificações versionadas de código reportadas. Inventário de modelos contém tags adicionais, não significa que foram executadas no lote. Campos antigos cpu/ram/temperature de result.json continuam null por compatibilidade; as medições estão no lote/JSONL.

Conclusão: primeiro lote real confirma coleta coretemp/procfs/nvidia-smi e preservação das três respostas no equipamento, além de execução sequencial concluída. Não valida caminhos de falha, parada térmica durante inferência ou operação sem supervisão. Um lote/caso com ordem fixa não sustenta ranking geral ou generalização para programação.

Assistência de IA: inspeção e análise dos artefatos publicados; execução e commit realizados pelo usuário. Avaliação funcional original determinística.
