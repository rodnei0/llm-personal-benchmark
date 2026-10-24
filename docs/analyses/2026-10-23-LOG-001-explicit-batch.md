# LOG-001 — lote da variante explícita

Fonte: commit 6f24cf503dfcd708a6f8c38889020848c05b0ea4; lote results/published/batches/20261024T005518Z-d56b0a2d1279. Leitura direta de batch.json e das três respostas publicadas. Caso LOG-001 1.1.0 explicit_instructions_v1. Código registrado a72b2f9f0a0611198deaf28b535ef894e04233c4; parâmetros temperature=0, seed=42, num_ctx=4096, num_predict=1024. Ollama 0.40.10. Uma execução por modelo.

| Modelo | Tempo | Tokens/s | CPU inicial/pico | GPU inicial/pico | Resultado |
| --- | --- | --- | --- | --- | --- |
| Qwen2.5 3B | 27.26 s | 10.84 | 50/85 °C | 49/74 °C | JSON incompleto; Daniel com ip vazio; invalid_lines=[2] |
| Qwen Coder 3B | 27.98 s | 11.25 | 53/89 °C | 52/75 °C | Markdown; incluiu sucesso de Carla; invalid_lines=[5] |
| Gemma 3 1B | 17.95 s | 28.28 | 55/82 °C | 53/81 °C | Markdown; incluiu sucesso de Ana, duplicata de Bruno, Daniel com IP preenchido; invalid_lines=[1] |

Todos reprovaram no parser estrito; diagnósticos de conteúdo acima são inspeção qualitativa adicional. Todos terminaram com done_reason=stop; 212, 227 e 413 tokens respectivamente, abaixo do limite de saída. O Qwen repete o texto observado na execução manual da variante: continua faltando a chave de fechamento do objeto.

Comparado ao lote original, o Coder deixou de manter os eventos exatos: agora incluiu o evento de sucesso da última linha. A linha inválida 6 continua ausente. Gemma alterou o formato interno para objeto raiz, mas não resolveu o caso. Conclusão limitada: nenhuma aprovação nesta intervenção; mais explicitação não demonstrou benefício funcional nestas respostas. Não generalizar o efeito de prompts explícitos para outros casos/modelos.

## Recuperação e comparação térmica

Este lote usou pausa mínima de 30 s e barreira de recuperação habilitada; o original usou 180 s. Todos iniciaram dentro dos limites definidos, com uso baixo. Picos são amostras do sistema, não medidas isoladas do Ollama. CPU/GPU iniciais de Coder e Gemma estavam alguns graus acima do lote anterior. Como tanto prompt quanto política de pausa mudaram, não é um contraste controlado exclusivamente de prompt para métricas térmicas/tempo. Não atribuir o aumento de picos à redução do intervalo ou às instruções sem experimento que isole essas variáveis.

Para teste do Coder 7B, preservar os lotes existentes, preparar download fora da medição e executar um lote separado supervisionado no caso original. Desempenho/memória/térmica do 7B ainda não foram medidos no homelab.

Assistência de IA: leitura e análise documental; avaliador estrito determinístico. Referências: [lote](../../results/published/batches/20261024T005518Z-d56b0a2d1279/batch.json), [comparação original](2026-10-23-LOG-001-first-batch.md).
