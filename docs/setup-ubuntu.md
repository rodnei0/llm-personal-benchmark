# Do zero ao primeiro experimento no Ubuntu

Este guia permite preparar e executar o LLM Lab sem assistência de IA. Todos os comandos são executados **no computador que rodará os modelos**, em um terminal Bash do Ubuntu, como usuário comum. Use sudo somente onde indicado. Conexão SSH funciona; não exige interface gráfica.

Escopo: Ubuntu com systemd, Python 3.12 ou superior e um modelo local via Ollama. Windows, macOS, containers e instalação de drivers de GPU não são cobertos. O ambiente de referência informado é um ASUS GL552VW, i7-6700HQ, 16 GB e Ubuntu Desktop 26.04.1; sua configuração atual ainda precisa ser confirmada. Ter hardware diferente é permitido: registre-o.

**Estado da validação:** o código passou em 30 testes com Python 3.12.14, incluindo um servidor Ollama simulado. Este roteiro ainda não foi executado no homelab. Os registros de instalação devem ser preenchidos após cada etapa; instruções não são evidência de execução.

## 1. Identificar o computador

Execute e examine cada saída:

```bash
cat /etc/os-release
uname -r
uname -m
lscpu
free -h
df -h / "$HOME"
lsblk -o NAME,SIZE,FSTYPE,MOUNTPOINTS
command -v python3
python3 --version
command -v ollama
```

Resultado esperado: distribuição Ubuntu; arquitetura x86_64 no notebook de referência; memória e disco identificados. Ausência de Ollama é normal nesta fase. Se Python não existir, prossiga para instalar os pacotes. Se o Python instalado for anterior a 3.12, pare antes de instalar o projeto: este guia não orienta substituir o Python do sistema.

Planeje pelo menos 10 GB livres no filesystem dos modelos como margem operacional inicial, não como requisito universal. Pesos, bibliotecas, cache e ambiente Python ocupam espaços diferentes. O tamanho do arquivo de um modelo não representa seu consumo de RAM. Não use o disco externo com falha de leitura como destino dos modelos ou resultados.

Se quiser identificar GPU sem instalar driver:

```bash
lspci | grep -Ei 'vga|3d|display'
command -v nvidia-smi
```

Se nvidia-smi já estiver instalado, execute-o e registre a saída. Não presuma uma GPU específica pelo nome do notebook. A instalação inicial seguirá com o backend que o Ollama detectar; confirme CPU/GPU em execução na etapa 7.

**Checkpoint:** registre SO, kernel, CPU, RAM, espaço livre e GPU detectada no diário. Não publique identificadores de máquina ou endereços privados desnecessários.

## 2. Instalar ferramentas básicas

Estes comandos atualizam o índice do apt e instalam os pacotes listados; não fazem uma atualização geral do sistema:

```bash
sudo apt update
sudo apt install git curl ca-certificates python3 python3-venv python3-pip lm-sensors pciutils zstd
python3 --version
git --version
sensors
```

Esperado: Python >=3.12, Git disponível e leituras de sensores. Se sensores de CPU não aparecerem, interrompa os testes de carga até resolver a monitorização. Não execute sensores-detect automaticamente: ele exige avaliação própria do hardware.

No notebook com histórico de desligamento térmico, mantenha os ajustes já adotados, ventilação desobstruída e alimentação conectada. Registre tampa, turbo, energia e outros serviços ativos. Observe a temperatura em repouso antes de inferência. Não execute stress tests para preparar o benchmark. Não existe um limite térmico universal neste guia: use os limites do hardware e uma política conservadora documentada antes da primeira carga.

Em um segundo terminal, acompanhe:

```bash
watch -n 2 sensors
```

Ctrl+C encerra o monitor. Se já usa Grafana, pode acompanhar também o dashboard existente. Esta etapa oferece observação manual, não proteção térmica automática.

## 3. Obter a versão correta do projeto

O adaptador e este guia estão na branch feat/ollama-runner, proposta no PR #1. Enquanto o PR não estiver integrado, clonar somente a main não disponibiliza run-ollama.

```bash
mkdir -p "$HOME/projetos"
cd "$HOME/projetos"
git clone --branch feat/ollama-runner https://github.com/rodnei0/llm-personal-benchmark.git
cd llm-personal-benchmark
git status --short
git rev-parse HEAD
```

Esperado: clone sem autenticação por ser público, status vazio e um hash de commit. Guarde esse hash: branches mudam. Se o diretório já existir, entre nele e confira git status antes de qualquer troca de branch; não apague alterações para seguir o tutorial.

Após a integração do PR, novos leitores podem clonar a main. Para reproduzir uma rodada antiga, use o hash completo registrado nela com `git checkout --detach HASH_DO_COMMIT` (substitua o marcador). Não atualize código no meio de uma rodada.

## 4. Criar o ambiente Python e testar o executor

Na raiz do repositório:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest -q
llm-lab --help
llm-lab run-ollama --help
```

Esperado nesta versão: 30 testes passando e o comando run-ollama na ajuda. Os testes não baixam nem executam modelos. O ambiente virtual evita instalar dependências Python globalmente. O projeto usa biblioteca padrão em execução; pytest é usado para desenvolvimento.

Ao abrir outro terminal ou sessão SSH, volte à pasta do projeto e execute `source .venv/bin/activate`. Para sair do ambiente: `deactivate`.

Crie um diário local e registre dependências:

```bash
mkdir -p results/runs/setup
cp docs/templates/session.md results/runs/setup/session.md
python -m pip freeze > results/runs/setup/python-packages.txt
git rev-parse HEAD > results/runs/setup/commit.txt
```

Se os arquivos já existirem, use outra pasta de sessão para preservar o registro anterior. A lista pip freeze descreve o ambiente instalado; o projeto ainda não fornece lockfile que fixe todas as dependências.

## 5. Instalar o Ollama

Baixe o instalador oficial para um arquivo, examine-o e depois execute:

```bash
curl -fL https://ollama.com/install.sh -o /tmp/llm-lab-ollama-install.sh
less /tmp/llm-lab-ollama-install.sh
sha256sum /tmp/llm-lab-ollama-install.sh
sh /tmp/llm-lab-ollama-install.sh
```

Saia do less com q. O script pede privilégios para instalar binários e configurar o serviço; pode configurar grupos e detectar componentes de GPU. Em caso de erro, examine a mensagem antes de repetir. O hash identifica o arquivo baixado, mas não é uma verificação independente de autenticidade.

O fluxo acima obtém a versão disponibilizada no momento. Registre a versão efetivamente instalada. Para replicar uma versão anterior, a instalação oficial aceita `OLLAMA_VERSION`: use `OLLAMA_VERSION=VERSAO_REGISTRADA sh /tmp/llm-lab-ollama-install.sh`, substituindo o marcador por uma release existente. Não reinstale ou atualize durante uma rodada comparativa.

```bash
ollama --version
sudo systemctl status ollama --no-pager
curl --fail --silent --show-error http://127.0.0.1:11434/api/version
```

Esperado: serviço active (running) e JSON com versão do servidor. Se o cliente alertar divergência de versão, registre e resolva antes da rodada. Não execute ollama serve em paralelo ao serviço: isso pode causar conflito de porta.

## 6. Configurar execução local e uma requisição por vez

O arquivo abaixo é específico do laboratório. Se já existir, leia-o antes de substituir.

```bash
sudo mkdir -p /etc/systemd/system/ollama.service.d
sudo tee /etc/systemd/system/ollama.service.d/llm-lab.conf > /dev/null <<'CONFIG'
[Service]
Environment="OLLAMA_HOST=127.0.0.1:11434"
Environment="OLLAMA_NO_CLOUD=1"
Environment="OLLAMA_NUM_PARALLEL=1"
Environment="OLLAMA_MAX_LOADED_MODELS=1"
CONFIG
sudo systemctl daemon-reload
sudo systemctl restart ollama
sudo systemctl show ollama --property=Environment
ss -ltn 'sport = :11434'
curl --fail --silent --show-error http://127.0.0.1:11434/api/version
```

Esperado: variáveis aplicadas e listener em 127.0.0.1:11434. Cloud desativado não impede o download dos modelos. O limite do serviço não substitui o protocolo: não envie outras requisições durante o experimento.

Não abra a porta 11434 no roteador ou firewall para este fluxo. Execute a CLI no homelab via SSH; não é necessário expor a API na rede. Os modelos ficam normalmente em /usr/share/ollama/.ollama/models no Linux instalado pelo script. Confira o espaço desse filesystem:

```bash
df -h /usr/share/ollama
```

Se faltar espaço, pare e escolha um destino antes de baixar. A variável OLLAMA_MODELS permite alterar o diretório, com permissões para o usuário do serviço; essa alteração deve entrar no diário.

## 7. Baixar um modelo e fazer um teste curto

Primeiro modelo do piloto: Qwen2.5 3B. O catálogo consultado em 2026-10-23 lista aproximadamente 1,9 GB e quantização Q4_K_M para a tag; confirme os dados baixados. A tag é mutável. O modelo possui licença própria Qwen, distinta da licença futura do código deste projeto.

```bash
ollama pull qwen2.5:3b
ollama list
ollama show qwen2.5:3b
curl --fail --silent --show-error http://127.0.0.1:11434/api/tags > results/runs/setup/ollama-tags.json
ollama --version > results/runs/setup/ollama-version.txt
```

Espere o download completar. O JSON de tags preserva o digest completo; anote-o no diário. Não distribua pesos junto ao repositório.

Com monitor térmico aberto, envie somente este teste de funcionamento:

```bash
curl --fail --silent --show-error http://127.0.0.1:11434/api/generate \
  -H 'Content-Type: application/json' \
  -d '{"model":"qwen2.5:3b","prompt":"Responda somente: OK","stream":false,"keep_alive":"1m","options":{"temperature":0,"seed":42,"num_ctx":4096,"num_predict":16}}'
ollama ps
```

Esperado: JSON com done=true e texto de resposta. O texto pode divergir de OK: o objetivo aqui é verificar inferência. Em ollama ps, PROCESSOR indica CPU, GPU ou combinação enquanto o modelo está carregado. Execute rapidamente, dentro do minuto; se não houver linha, ele pode já ter sido descarregado. Registre o backend observado sem presumir aceleração.

```bash
ollama stop qwen2.5:3b
ollama ps
```

Espere a máquina voltar às condições de repouso registradas antes do benchmark. Esse teste não é um resultado do LOG-001. Não baixe Gemma nem rode lotes nesta fase.

## 8. Executar o primeiro caso real

Ainda na raiz, com o ambiente virtual ativo:

```bash
llm-lab run-ollama --case cases/LOG-001 --model qwen2.5:3b
```

O comando envia a primeira resposta do caso, sem ferramentas, histórico ou correções. A referência esperada não é enviada ao modelo. Ele imprime o caminho criado em results/runs, a avaliação e métricas.

Padrões do adaptador: temperatura 0, seed 42, contexto 4096 e até 1024 tokens de saída. O modelo pode manter template/system próprios. Seed não assegura determinismo entre versões e plataformas. Confira a ajuda para alterar parâmetros e registre toda alteração; não mude apenas para melhorar uma resposta na mesma rodada.

Na pasta indicada, examine result.json e response.txt. O registro também contém prompt e snapshots. O campo inference armazena payload e resposta completa da API. `passed=false` é um resultado legítimo: preserve a resposta sem editar. Tempo total inclui a requisição; tokens/s corresponde somente à geração informada pela API. CPU, RAM e temperatura ainda não são coletadas pelo executor.

O adaptador pede descarregamento ao concluir. Confira ollama ps depois. Anote temperatura inicial/final, pico observado, backend, duração, status e interferências no diário. Não confunda um pico observado manualmente com uma medição contínua.

## 9. Interromper e investigar falhas

Não há proteção térmica automática neste executor. Se houver comportamento térmico anormal ou você precisar interromper, em outro terminal:

```bash
sudo systemctl stop ollama
sudo systemctl is-active ollama
ollama ps
```

Esperado: serviço inactive e cliente sem conexão. Confira também o monitor de recursos e sensores para confirmar cessação da carga. Ctrl+C ou timeout do cliente não comprovam cancelamento no servidor. Reinicie o serviço somente depois de conferir as condições:

```bash
sudo systemctl start ollama
```

Falhas de transporte não geram uma pasta de resultado nesta versão. Registre no diário inclusive horário, comando, mensagem, causa conhecida ou desconhecida e qualquer repetição. Não conte falha de infraestrutura como resposta errada do modelo nem a exclua silenciosamente do relatório.

| Sintoma | Verificação e ação |
| --- | --- |
| llm-lab não encontrado | Ative .venv e repita a instalação editável na raiz. |
| run-ollama ausente | Confira a branch/commit; a main inicial só tem importação manual. |
| ensurepip/venv indisponível | Confira a instalação de python3-venv para o Python em uso. |
| Connection refused | Veja status do serviço e /api/version; confirme host/porta. |
| Porta já em uso | Não inicie outro ollama serve; identifique o listener com ss. |
| Modelo não encontrado | Confirme a tag em ollama list e conclua ollama pull. |
| Download falha | Confira conectividade e disco; preserve a mensagem, sem desativar TLS. |
| Execução demora/timeout | Examine temperatura, memória e logs; não aumente timeout nem repita às cegas. |
| Processo termina/serviço cai | Examine journal e mensagens do kernel para OOM ou falha do backend. |
| Resposta truncada ou Markdown | Preserve-a; é avaliada como recebida. Registre limite de saída. |

Logs úteis (revise antes de publicar):

```bash
sudo journalctl -u ollama -n 100 --no-pager
sudo journalctl -k -n 100 --no-pager
```

## 10. Documentar e compartilhar

Preencha o modelo docs/templates/session.md. Os registros locais em results/runs são ignorados pelo Git. Não use git add -f em toda essa pasta: ela pode conter metadados locais ou respostas que precisam de revisão.

Para publicar uma rodada, copie apenas os artefatos revisados para uma pasta dedicada sob results/published/ e inclua o diário. Registre qualquer anonimização; nunca modifique uma resposta bruta para fazê-la passar. Caso uma resposta contenha dados privados, retenha o original local e publique uma cópia identificada como redigida, informando a limitação de auditoria. Faça git diff --cached antes do commit.

A documentação deve dizer se houve IA na instalação, implementação ou avaliação, e qual foi a intervenção. IA não é requisito para seguir este guia. Nenhum avaliador deste caso usa IA. Durante a resposta do benchmark, mantenha o protocolo de primeira resposta.

Um repositório público não concede automaticamente licença de uso/modificação. A licença do código ainda está pendente; registre sua escolha em LICENSE antes de anunciar o projeto como open source licenciado. Licenças de modelos são independentes.

## Fontes e manutenção

Consultadas em 2026-10-23. Instalações futuras podem exigir ajustes. Registre versões efetivas e apresente correções com saídas reproduzíveis, sem credenciais.

- Instalação Linux: https://docs.ollama.com/linux
- Serviço, variáveis, armazenamento e execução local: https://docs.ollama.com/faq
- API de geração: https://docs.ollama.com/api/generate
- Modelo e licença: https://ollama.com/library/qwen2.5:3b
- Código proposto: https://github.com/rodnei0/llm-personal-benchmark/pull/1
