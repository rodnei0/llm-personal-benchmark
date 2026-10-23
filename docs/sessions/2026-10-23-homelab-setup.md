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
