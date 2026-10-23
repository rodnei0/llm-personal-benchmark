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
