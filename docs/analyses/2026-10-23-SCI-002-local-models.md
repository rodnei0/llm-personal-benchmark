# SCI-002 — estações do ano, análise provisória

Fonte: lote results/published/batches/20261024T022925Z-d61158a20c03 no commit 986173fa485ccb2e870bf6e194650c8315d59eca. Leitura direta de batch.json e das três respostas. Caso SCI-002 1.0.0; código 0859679642341b5f6a3b963b43bf8bb435907632. Uma resposta por participante; temperature=0, seed=42, num_ctx=4096, num_predict=1024. Mesmo hash de prompt em todas as execuções conforme lote.

**Análise assistida por IA, sem revisão humana assinada.** Registros permanecem passed=null, pending_human_review. Recomendações abaixo não alteram avaliações originais.

## Conteúdo

| Modelo | Acertos parciais | Problemas observados | Parecer provisório |
| --- | --- | --- | --- |
| Gemma 3 1B | Cita inclinação de 23,5° e iluminação variável | Diz que o Sul recebe mais luz no inverno; explicação de oposição é circular e não explica ângulo solar/duração do dia | Não aprovar integralmente |
| Qwen2.5 3B | Cita eixo inclinado e oposição verão/inverno | Afirma que durante verão de um hemisfério o outro está voltado para o Sol; depois diz que recebe menos luz, contradizendo o mecanismo; não explica adequadamente duração do dia | Não aprovar integralmente |
| Qwen Coder 3B | Menciona horários solares variáveis | Explica estações pela aproximação/afastamento do Sol; afirma genericamente ausência do Sol no inverno; não explica a inclinação e oposição com coerência | Reprovação recomendada por erros materiais |

A causa principal das estações é a inclinação do eixo combinada à órbita, que altera ângulo de incidência e duração do dia nos hemisférios em condições opostas. A distância Terra-Sol não é a explicação principal; noite polar não caracteriza todo inverno em todo hemisfério. Fonte de conferência: https://www.weather.gov/fsd/season (consultada em 2026-10-23). Os exemplos e a redação não precisam coincidir com a referência, mas os conceitos devem ser corretos.

Não atribuir os erros à temperatura ou à quantização sem estudo que isole variáveis. Estilo acessível, formatação em lista ou menção ao número 23,5 não comprovam entendimento. Não generalizar desta pergunta para ciência ou programação em geral.

## Execução

| Modelo | Tempo cliente | Tokens | Tokens/s | Pico CPU | Pico GPU |
| --- | --- | --- | --- | --- | --- |
| Gemma 3 1B | 8.64 s | 185 | 31.58 | 66 °C | 74 °C |
| Qwen2.5 3B | 28.41 s | 284 | 11.93 | 87 °C | 70 °C |
| Qwen Coder 3B | 30.75 s | 309 | 11.82 | 89 °C | 69 °C |

Lote completed, thermal_guard=true, limiares CPU 93 °C/GPU 80 °C e pausa mínima 30 s. Nenhum corte registrado; todos done_reason=stop e abaixo de 1024 tokens de saída. Temperaturas de início CPU 51/54/55 °C, GPU 50/52/54 °C. Picos amostrados segundo resumo do lote, não máximos garantidos. Não confundir desempenho de geração com correção de conteúdo.

Próximo contraste proposto: usar um problema quantitativo com avaliador determinístico, por exemplo MATH-001. Revisões humanas dos casos conceituais continuam pendentes; não convertê-las automaticamente em placar oficial.
