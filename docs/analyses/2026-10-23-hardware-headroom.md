# Exigência do hardware e folga observável

Análise dos sete batch.json e sete telemetry.jsonl publicados até o commit d2830acedd7d24f09989c0d9ee4fb13858161491. Casos LOG-001 original/variante, SCI-001 e SCI-002: 13 inferências concluídas e uma interrompida. As estatísticas foram recalculadas a partir das amostras com phase=inference e run_index correspondente; médias aritméticas das amostras, não ponderadas pelo tempo nem exclusivas da geração de tokens. Inventário já confirmado: i7-6700HQ 4C/8T, turbo desativado, 16 GB instalados (15.01 GiB utilizáveis reportados), GTX 960M 2048 MiB.

## Comparação por modelo, execuções concluídas

| Modelo Q4_K_M | Rodadas | CPU média por rodada | Maior pico CPU % | Picos CPU por rodada | Picos GPU por rodada | VRAM máxima |
| --- | --- | --- | --- | --- | --- | --- |
| Gemma 3 1B | 4 | 18.7–31.2% | 43.5% | 66–82 °C | 73–81 °C | 947 MiB |
| Qwen2.5 3B | 4 | 43.9–47.3% | 64.5% | 85–87 °C | 68–74 °C | 1035 MiB |
| Qwen Coder 3B | 4 | 34.6–47.7% | 54.6% | 85–89 °C | 65–75 °C | 1030 MiB |
| Qwen Coder 7B | 1 | 40.8% | 54.8% | 93 °C | 76 °C | 1163 MiB |

GPU teve picos de utilização de 95–96% no Gemma e 100% em algumas rodadas Qwen/Coder. As médias de GPU variaram entre casos e incluem carga/preenchimento do prompt/geração; não permitem afirmar o gargalo exclusivo de cada fase. GPU com memória livre pode estar ocupada computacionalmente.

## RAM

Durante as inferências concluídas, a estimativa ram_used_bytes=MemTotal-MemAvailable teve picos por rodada de 3.82–4.26 GiB; a menor disponibilidade correspondente foi 10.75 GiB. Antes das rodadas, essa mesma estimativa ficava aproximadamente em 3.5–3.7 GiB. Há evidência de disponibilidade global, não de RAM esgotada.

Mas MemAvailable é estimativa de memória recuperável sem swap, incluindo tratamento de caches. Não representa literalmente páginas físicas desocupadas, RSS/PSS do Ollama ou todo o working set dos pesos. Arquivos de modelo mapeados/cacheados podem participar desse quadro; sua distribuição específica não foi coletada. O 7B reportar apenas 4.06 GiB por essa métrica NÃO comprova que todos os seus pesos e buffers couberam nesse valor.

Não foram coletados SwapFree/SwapTotal ao longo da execução, tráfego de swap, page faults, RSS/PSS por processo, Cached/Mapped ou pressão de memória. Logo não é possível afirmar ausência absoluta de paginação nem prometer que 14B terá mais de 10 GiB de margem útil. Tampouco há indício, nesses números globais, de que 16 GB tenham sido o gargalo já atingido.

Base da interpretação: https://docs.kernel.org/filesystems/proc.html, campos MemAvailable/Cached/Mapped. Valores em GiB/MiB, não GB decimais de catálogo.

## CPU e limite térmico

Percentual é agregado dos oito processadores lógicos. Cerca de 50% não prova que quatro núcleos físicos estejam ociosos nem que seja possível dobrar desempenho: SMT, distribuição de threads, dependências, acesso à RAM e transferência CPU/GPU não foram isolados. Os logs não incluem uso por núcleo, frequências durante carga, consumo elétrico, throttling ou largura de banda da memória.

O que está demonstrado: CPU sai de cerca de 50–55 °C e alcança 85–89 °C nos 3B e 93 °C no 7B. Houve corte confirmado a 86 °C na tentativa SCI-001 com limiar 85 °C; esse resultado interrompido está preservado e não entra nas médias de rodadas concluídas. Com política posterior de 93 °C, os picos 85–89 ficam somente 4–8 °C abaixo do limiar escolhido. Isso é distância até o limiar de software, não margem certificada de segurança. No 7B, 93 °C foi observado antes da implementação da guarda.

Conclusão prática: folga computacional adicional não pode ser inferida do percentual agregado, e a margem térmica observada para carga prolongada é pequena. Isso torna refrigeração um limite operacional evidente, ainda que o gargalo exato de velocidade não tenha sido identificado.

## GPU e folga nominal

Dos 2048 MiB, os picos registrados deixam aproximadamente 1101 MiB para Gemma, 1013/1018 MiB para os dois 3B e 885 MiB para 7B. É sobra nominal na amostra, não garantia de alocação útil: camadas/buffers precisam caber, drivers/desktop variam e a configuração de offload não foi coletada por rodada. Não se pode garantir que ocupar mais VRAM aumentará velocidade. A GPU teve temperaturas de até 81 °C em rodadas anteriores à guarda GPU de 80 °C.

## Escalar o modelo

No mesmo LOG-001 original, Coder 3B gerou a 11.31 tokens/s em 20.30 s; Coder 7B a 5.36 tokens/s em 51.61 s. Picos CPU: 85 contra 93 °C. A demanda maior se manifestou em tempo e temperatura, sem saturação global de RAM demonstrada. Uma rodada por tamanho, caches/ordem e formato de saída não isolados: não extrair uma lei de escala geral.

Para 14B, os logs permitem considerar memória possivelmente disponível, mas não comprovam encaixe confortável ou usabilidade. Não estimar velocidade exata pela metade nem supor temperatura maior obrigatória. Antes de concluir sobre expansão, enriquecer a telemetria de memória e CPU; alterar capacidade térmica/configuração terá de ser registrado como condição experimental.

## Síntese

- Folga aparente maior: disponibilidade global de RAM, com a limitação do indicador descrita.
- Folga nominal parcial: cerca de 0.86–1.08 GiB de VRAM nas amostras.
- Folga de velocidade não comprovada: percentuais CPU/GPU não são um orçamento simples de crescimento.
- Restrição operacional observada: temperaturas CPU elevadas e interrupção real pela guarda.
- Disco atual, swap dinâmica, temperatura ambiente e refrigeração não foram novamente medidos nesta análise.

Dados do usuário publicados, analisados com assistência de IA; não houve teste adicional de carga para produzir este relatório.
