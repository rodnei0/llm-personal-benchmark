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
