# SCI-001 — comparação Qwen generalista e Coder, análise provisória

Fonte: commit 338cf4e801cb8ed3768882bac85ee97c0b86868c. Leitura dos batch.json de 20261024T022313Z-81ab982924bb e 20261024T022459Z-f939e4f37b81 e das duas respostas do lote concluído. Código registrado a1d76dea80b7b94821aea4ba10740bc3db6e32d5. Mesmo caso SCI-001 1.0.0 e prompt_sha256=b8f3233faf2b2cd856b07add0dd02412ba6eaa3e91bf7d241f61539e3abce2cf.

**Análise assistida por IA, não revisão humana assinada.** Os resultados conceituais permanecem passed=null, pending_human_review. Nenhuma decisão humana será presumida.

## Lote interrompido, preservado

Primeira tentativa: limite CPU 85 °C e GPU 80 °C. Qwen2.5 3B iniciou com CPU 50 °C/GPU 49 °C. O lote registrou CPU 86 °C, status aborted, avaliação null, e não iniciou o Coder.

shutdown.confirmed=true: stop_returncode=0, serviço inactive, main_pid=0, remaining_pids=[], api_connection_refused=true, client_finished=true. É a primeira evidência compartilhada de acionamento do mecanismo durante uma execução de inferência, além do ensaio sem carga. Demonstra um caminho real de parada confirmada, não garantia de ausência de overshoot ou de tratamento de todas as falhas.

## Lote seguinte concluído e mudança de política

Segundo lote usou abort_cpu_temp=93, em vez de 85; GPU permaneceu 80. Essa alteração consta nos artefatos e deve permanecer visível na comparação. As duas inferências chegaram a 86 °C de CPU, abaixo do novo limiar, e concluíram. Não confundir conclusão com validação de segurança a 93 °C. A mudança não foi feita pelo assistente no código nesta etapa.

| Modelo | Tempo cliente | Tokens | Tokens/s | CPU inicial/pico | GPU inicial/pico |
| --- | --- | --- | --- | --- | --- |
| Qwen2.5 3B | 22.31 s | 214 | 12.07 | 52/86 °C | 50/68 °C |
| Qwen Coder 3B | 18.59 s | 118 | 11.70 | 54/86 °C | 53/65 °C |

Parâmetros: temperature=0, seed=42, num_ctx=4096, num_predict=1024, cooldown=30, guarda ativa. Ambos terminaram com stop; picos conforme amostras resumidas no batch.json, não máximos garantidos. Lote com ordem fixa e uma resposta concluída por participante. A tentativa abortada não é resposta errada nem deve desaparecer do histórico.

## Resposta Qwen2.5 3B

Acerta que a luz branca contém várias cores e menciona espalhamento. Porém atribui o mecanismo a uma camada de ozônio e diz que a maioria das outras cores é absorvida/refletida, enquanto o azul é espalhado. Isso não explica corretamente o papel das moléculas atmosféricas no espalhamento seletivo do céu claro. Não apresenta a relação correta entre comprimento de onda e intensidade do espalhamento.

Parecer provisório: reprovar por mecanismo factual incorreto. A primeira exigência (mistura de cores) é atendida; a exigência sobre moléculas e dependência do comprimento de onda não é corretamente atendida. Fluência e extensão não compensam o erro.

## Resposta Qwen Coder 3B

Afirma corretamente que azul é mais espalhado que vermelho e que essa luz chega aos olhos. Mas descreve os agentes como partículas "como nuvens e polvo", sem uma explicação correta e clara do papel das moléculas do ar. Não explica que comprimentos de onda menores sofrem espalhamento mais intenso. "Polvo" é mantido como escrito: não presumir silenciosamente que era "poeira".

Parecer provisório: mais próximo do mecanismo relevante que a resposta generalista, mas incompleto/problemático para a rubrica integral. Recomendar não aprovar nesta forma, sujeito à revisão humana. A rubrica não exige o termo Rayleigh, mas exige o mecanismo, não somente a afirmação de que azul se espalha mais.

## Comparação com Gemma e próximos passos

Gemma 1B havia invertido a frequência do azul em relação às demais cores, como registrado na análise anterior. Nenhuma das três explicações é recomendada para aprovação integral por esta revisão assistida. Isso é restrito a uma pergunta e não representa ranking de conhecimento científico.

Antes de nova série, preferir manter o limiar conservador documentado de 85 °C e investigar como reduzir carga/rever refrigeração em vez de ampliar o limiar apenas para concluir a resposta. Não há evidência para atribuir os erros conceituais à temperatura. Qualquer mudança de threads, backend ou limite deve virar configuração registrada e nova rodada.

Fonte factual consultada: https://www.weather.gov/fgz/SkyBlue — composição da luz branca, espalhamento por moléculas do ar e maior espalhamento de azul/violeta. Análise e paráfrases com assistência de IA; revisão humana pendente.
