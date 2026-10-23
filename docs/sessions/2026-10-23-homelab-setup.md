# Preparação do homelab — 2026-10-23

Fonte: comandos executados pelo responsável no homelab e saídas compartilhadas na conversa. Nenhum acesso remoto pelo assistente. Inventário resumido, sem hostname nem dados de rede.

## Etapa 1 — inventário confirmado

| Item | Observado |
| --- | --- |
| Sistema | Ubuntu 26.04.1 LTS, Resolute Raccoon |
| Kernel | 7.0.0-38-generic |
| Arquitetura | x86_64 |
| CPU | Intel Core i7-6700HQ, 4 núcleos / 8 threads |
| Frequência máxima reportada por lscpu | 2600 MHz; configuração de turbo não confirmada por esta saída |
| Memória | 15 GiB reportados; 11 GiB disponíveis no momento |
| Swap | 4 GiB, 34 MiB usados no momento |
| Filesystem raiz | ext4, 218 GiB de capacidade e 139 GiB disponíveis reportados por df |
| Armazenamento adicional | Partições ext4 em /srv/storage e NTFS; não selecionadas para o laboratório |
| Python do sistema | 3.14.4 |
| Ollama | command -v ollama sem saída; executável não encontrado no PATH |
| GPU, driver e sensores | Ainda não verificados |

## Interpretação e próximo passo

Há recursos disponíveis para preparar o piloto; desempenho e estabilidade de inferência ainda não foram medidos. Python 3.14.4 atende ao mínimo declarado (>=3.12), mas a validação de desenvolvimento anterior ocorreu em 3.12.14: a compatibilidade efetiva deve ser confirmada pelos testes no homelab. Não substituir o Python do sistema.

Próxima etapa proposta: instalar ferramentas básicas com apt e verificar sensores/GPU. A execução dessa etapa ainda não foi confirmada. Não há Ollama, modelo baixado ou benchmark executado confirmado nesta sessão.

## Rastreabilidade e assistência

- Assistência de IA: interpretação do inventário e elaboração das próximas instruções/documentação.
- Execução dos comandos de inventário: usuário.
- Versões Git, dependências do projeto e commit local: pendentes; projeto ainda não instalado no homelab.
- Temperaturas, backend CPU/GPU, turbo e condições de ventilação: pendentes de observação.

## Etapa 2 — ferramentas, sensores e GPU observados

Saídas enviadas pelo usuário após as instruções de preparação (não foi compartilhado o log do apt; não se presume instalação nova de cada pacote).

- Git: 2.53.0.
- Sensores: coretemp, PCH, Wi-Fi, ASUS e ACPI respondendo.
- CPU Package: 55 °C; núcleos 50–53 °C nessa amostra. Carga/repouso não comprovados por medição de utilização.
- Ventoinhas CPU/GPU: ambas 1700 RPM reportadas.
- GPU integrada: Intel HD Graphics 530.
- GPU dedicada: NVIDIA GeForce GTX 960M; 2048 MiB de VRAM.
- Driver NVIDIA: 580.178.04; nvidia-smi operacional.
- GPU na amostra: 52 °C, 0% utilização e 4 MiB ocupados.
- Cabeçalho do nvidia-smi reporta CUDA Version 13.0: isso não comprova instalação do CUDA Toolkit nem compatibilidade de um backend específico.
- intel_pstate/no_turbo: 1 (turbo desativado).

Decisão: manter configurações térmicas e driver existentes. Aceleração Ollama ainda não testada; não inferir suporte efetivo apenas de nvidia-smi. Próximo passo: clonar a branch documentada, criar venv com Python 3.14.4 e executar os testes. Nenhum teste de modelo nesta etapa. Este complemento atualiza as pendências históricas acima; ventilação, condições de energia e estabilidade sob carga seguem não verificadas.

## Etapa 3 — projeto instalado e testes confirmados no homelab

Saída fornecida pelo usuário em terminal com .venv ativo, na pasta local do projeto:

- Python: 3.14.4.
- `python -m pytest -q`: 30 passed in 3.65s.
- `llm-lab run-ollama --help`: executou e exibiu os parâmetros previstos.

Isso confirma os testes e a disponibilidade da CLI nesse ambiente; não comprova inferência real, desempenho ou estabilidade térmica. O hash do commit local não foi compartilhado e segue pendente para rastreabilidade exata. Próximo passo proposto: instalar o Ollama e conferir serviço/versões antes de baixar modelos. A instalação do Ollama ainda não foi confirmada.

## Etapa 4 — instalação do Ollama confirmada

Saída fornecida pelo usuário:

- Ollama cliente: 0.40.10.
- Servidor: GET /api/version respondeu HTTP 200, com {"version":"0.40.10"}.
- Serviço systemd: enabled e active (running), iniciado em 2026-10-23 às 19:25:54 -04:00.
- Executável do serviço: /usr/local/bin/ollama serve.
- Commit local informado: 213b7ffccbecb669ce70344517944ed802ec7fd4. Esse hash complementa a rastreabilidade que estava pendente nas etapas anteriores.
- Log de instalação e hash do script não compartilhados; não registrados como verificados.

As linhas do journal exibidas por systemctl estavam truncadas: não permitem concluir qual backend/GPU foi selecionado. Nenhum download de modelo ou inferência confirmado. Próximo passo proposto: aplicar configuração local do serviço, verificar variáveis e listener, depois baixar o modelo. O registro de um commit local não implica que futuras atualizações desta documentação já estejam no clone.

## Etapa 5 — API local e modelo baixado

Saídas fornecidas pelo usuário ao longo da configuração:

- Listener confirmado em 127.0.0.1:11434 por ss; API respondeu versão 0.40.10 após o reinício.
- OLLAMA_HOST=127.0.0.1:11434 visível em systemctl show.
- Saída compartilhada de Environment ainda truncada após OLLA: OLLAMA_NO_CLOUD, OLLAMA_NUM_PARALLEL e OLLAMA_MAX_LOADED_MODELS ainda não confirmadas individualmente.
- ollama list: qwen2.5:3b, identificador abreviado 357c53fb659c, tamanho 1.9 GB. Digest completo ainda não compartilhado.
- ollama show: arquitetura qwen2; 3.1B parâmetros; quantização Q4_K_M; contexto declarado do modelo 32768; embedding length 2048; template go_template; capabilities completion e tools.
- System do modelo: You are Qwen, created by Alibaba Cloud. You are a helpful assistant.
- Licença exibida: Qwen RESEARCH LICENSE AGREEMENT, data de lançamento September 19, 2024.

O contexto declarado do modelo não é o contexto configurado no experimento: o piloto solicita num_ctx=4096. A capacidade tools não significa ferramentas habilitadas no teste. Próximo passo: conferir as variáveis sem truncamento e executar uma resposta curta acompanhando sensores. Nenhuma inferência ou backend efetivo confirmado até este registro.

## Etapa 6 — primeira inferência real de funcionamento

Executada pelo usuário em 2026-10-23; API registrou created_at=2026-10-23T23:40:57.175352216Z (19:40:57 -04:00).

- Modelo qwen2.5:3b; prompt: Responda somente: OK.
- Parâmetros: stream=false, keep_alive=1m, temperature=0, seed=42, num_ctx=4096, num_predict=16.
- Resposta: OK; done=true; done_reason=stop.
- Métricas reportadas pela API (não cronômetro de ponta a ponta do cliente): total_duration=42777628871 ns (42.778 s), load_duration=41103764160 ns (41.104 s), prompt_eval_count=36, prompt_eval_cached_count=0, prompt_eval_duration=1588486000 ns (1.588 s), eval_count=2, eval_duration=82229000 ns (0.082229 s).
- Taxa calculada: aproximadamente 24.32 tokens/s para apenas 2 tokens; amostra curta demais para caracterizar desempenho sustentado.
- ollama ps: 2.3 GB, PROCESSOR 59%/41% CPU/GPU, CONTEXT 4096, RUNNER llamacpp. A coluna PROCESSOR descreve alocação do modelo; não comprova divisão percentual de tempo/uso computacional.
- Temperatura informada pelo usuário: 73 °C observados; sensor específico, série temporal e método de captura não fornecidos. Não tratar como pico instrumentado ou teste de estabilidade.
- Usuário executou ollama stop qwen2.5:3b; comando retornou sem mensagem de erro. Estado descarregado ainda não confirmado por ollama ps posterior.

Conclusão limitada: inferência local funcional e backend híbrido observado. Este é um teste de funcionamento, não um resultado LOG-001. Nenhum benchmark funcional executado até esta etapa. Variáveis de serviço além de OLLAMA_HOST continuam sem saída completa compartilhada; digest completo do modelo ainda pendente. Próximo passo proposto: confirmar descarregamento e retorno térmico às condições iniciais, conferir variáveis e executar uma única rodada LOG-001 com monitoramento.

## Etapa 7 — primeiro benchmark LOG-001 real

Saída da CLI compartilhada pelo usuário, sem acesso do assistente aos artefatos locais:

- Comando: llm-lab run-ollama --case cases/LOG-001 --model qwen2.5:3b.
- Run ID: 20261023T234330Z-586fb62ab40a.
- Pasta local: results/runs/20261023T234330Z-586fb62ab40a.
- Avaliação: passed=false; valid_json=true; schema=true; events_exact=false; invalid_lines_exact=false; error=null.
- Tempo de ponta a ponta medido pelo cliente: 26.408106920003775 s.
- Velocidade de geração reportada/calculada: 10.919788993277352 tokens/s.
- CPU, RAM e temperatura no registro automático: null; sem coleta pelo executor.
- Temperatura observada e relatada pelo usuário: 86 °C. Sensor específico e série temporal não fornecidos; observação manual externa ao resultado automático.

Interpretação: resposta respeitou sintaxe e contrato estrutural, mas divergiu da referência em ambos os conjuntos de conteúdo avaliados. Não é falha de execução do comando. Resposta bruta e result.json completo ainda não compartilhados; causa exata das divergências não determinada. Não se infere throttling ou causalidade entre temperatura e erros. Este único caso não sustenta ranking ou conclusão geral sobre o modelo.

Próximo passo proposto: deixar o equipamento retornar às condições iniciais e examinar response.txt e result.json antes de repetir carga. Preservar a primeira resposta sem edição. Nenhuma nova rodada solicitada nesta etapa; artefatos brutos ainda não publicados. Backend híbrido foi observado no teste curto anterior, não confirmado por ollama ps durante este benchmark. Configuração de serviço, digest completo e demais pendências continuam conforme registros anteriores.

## Etapa 8 — configuração confirmada e retorno térmico após rodada 1

Usuário informou retorno da temperatura observada a 52 °C. Sensor específico não identificado. Em seguida compartilhou:

```text
OLLAMA_HOST=127.0.0.1:11434
OLLAMA_NO_CLOUD=1
OLLAMA_NUM_PARALLEL=1
OLLAMA_MAX_LOADED_MODELS=1
```

`ollama ps` exibiu somente o cabeçalho, confirmando ausência de modelos carregados naquele momento. Essas observações resolvem as pendências de configuração e descarregamento apontadas nos registros anteriores. Não demonstram retroativamente a alocação durante o benchmark.

Próximo passo proposto: segunda execução independente do mesmo LOG-001, sem alterar prompt, referência ou parâmetros, após resfriamento e sob observação térmica. Preservar todas as rodadas. Cada registro usa attempt=1 porque representa primeira resposta sem correções em uma requisição independente; o número da repetição deve ser registrado no diário. A repetição ainda não foi executada/confirmada.

## Etapa 9 — segunda execução independente do LOG-001

Saída fornecida pelo usuário:

- Comando: llm-lab run-ollama --case cases/LOG-001 --model qwen2.5:3b.
- Run ID: 20261023T235153Z-6e3862608160.
- Pasta local: results/runs/20261023T235153Z-6e3862608160.
- Avaliação: passed=false, valid_json=true, schema=true, events_exact=false, invalid_lines_exact=false; error=null.
- Tempo cliente: 25.72697384400817 s; geração: 11.309198944307221 tokens/s.
- Temperatura relatada: 86 °C observados; sensor e série temporal não fornecidos.
- CPU, RAM e temperatura automáticos continuam null.

Mesmas verificações falharam nas duas execuções, mas igualdade das respostas ainda não foi confirmada. Até aqui: duas reprovações funcionais em duas execuções do mesmo caso, sem inferência de capacidade geral. Nenhum teste adicional proposto antes de comparar os registros existentes e deixar a máquina esfriar. Próxima verificação é somente leitura: hashes das respostas, igualdade do conteúdo e metadados de geração/configuração. Segundo result.json completo ainda não compartilhado.

## Comparação confirmada entre as duas rodadas

O usuário executou comparação local de response.txt: respostas byte a byte idênticas. Os dois result.json reportaram o mesmo SHA-256: 9e0fd29a0995c70133da41ff03d7fbae9e8b4adba511c99a3de49b1a5be13bf8. A resposta da segunda rodada compartilhada confirma os mesmos três erros descritos na análise: inclusão de Daniel com ip vazio, linha duplicada 3 classificada como inválida e omissão da linha malformada 6.

| Campo | Rodada 1 | Rodada 2 |
| --- | --- | --- |
| Run ID | 20261023T234330Z-586fb62ab40a | 20261023T235153Z-6e3862608160 |
| Tempo cliente | 26.408106920003775 s | 25.72697384400817 s |
| Tokens/s | 10.919788993277352 | 11.309198944307221 |
| Tokens gerados | 216 | 216 |
| load_duration | 3500083821 ns | 3496190633 ns |
| done_reason | stop | stop |
| Temperatura observada | 86 °C | 86 °C |

Ambas solicitaram temperature=0.0, seed=42, num_ctx=4096, num_predict=1024. Duas execuções apresentaram repetibilidade observada nesse caso/configuração; isso não garante determinismo em futuras execuções ou plataformas. Ambas terminaram normalmente sem esgotar o limite de saída. Não há evidência de que a temperatura causou os erros. Não foi proposta uma terceira execução idêntica neste checkpoint; próximo contraste útil é aplicar o mesmo prompt exportado a outro participante, em sessão independente, preservando o protocolo.
