# Lotes locais com telemetria e recuperação adaptativa

Versão 0.3.0. Linux; CPU Intel com sensor coretemp e GPU NVIDIA consultada via nvidia-smi. Procfs fornece uso global de CPU/RAM. Não requer novos pacotes Python nem scripts shell externos. GPU AMD/Intel não tem telemetria de GPU implementada nesta versão.

## Preparação

Na raiz do clone, preserve modificações versionadas antes de atualizar:

```bash
git status --short
git pull --ff-only origin feat/ollama-runner
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest -q
llm-lab batch-ollama --help
```

O comando não baixa modelos. Instale antecipadamente os participantes escolhidos com ollama pull. O lote consulta /api/tags e /api/version antes da primeira inferência e preserva os digests disponíveis. Se faltar um modelo, falha antes de executar qualquer um. Não atualize modelos ou código durante o lote. Execute apenas um lote e não envie outras requisições ao Ollama no mesmo período.

## Primeiro lote sugerido

Comece com dois modelos que já foram executados no equipamento, uma geração por participante. Isso ainda exige acompanhar a primeira validação no homelab:

```bash
llm-lab batch-ollama \
  --case cases/LOG-001-explicit \
  --models qwen2.5:3b gemma3:1b \
  --cooldown 30 \
  --repetitions 1 \
  --output-root results/published/batches
```

Para o prompt original, troque somente --case por cases/LOG-001; use outro lote. Para incluir gemma3:4b, acrescente a tag a --models em uma rodada futura: o histórico de 90 °C permanece relevante, e o intervalo não limita a temperatura durante a inferência.

## Como decide quando iniciar

1. A primeira geração espera também pelas condições de recuperação; não tem pausa mínima inicial.
2. Após cada geração, aguarda pelo menos --cooldown segundos (padrão 30; valores abaixo de 30 são rejeitados).
3. Aguarda CPU <=60 °C, todas as GPUs NVIDIA consultadas <=60 °C, uso global de CPU <=20% e uso de cada GPU <=10%.
4. Exige que as condições permaneçam atendidas por --stable-seconds (10 segundos por padrão), segundo as amostras disponíveis.
5. Se não atingir as condições dentro de --max-cooldown-wait (900 segundos após a pausa mínima), encerra e registra a falha. Dados necessários ausentes também impedem a liberação.

Os limites são uma política inicial do experimento, não limites universais de segurança. Temperatura de CPU é a maior leitura coretemp disponível. O uso de CPU é percentual agregado de todos os processadores, não percentual por núcleo. O sensor local só vale para Ollama no mesmo computador.

Opções disponíveis: --max-start-temp, --max-gpu-temp, --max-cpu-usage, --max-gpu-usage, --stable-seconds, --max-cooldown-wait e --sample-interval (padrão 2 s, intervalo aproximado, acrescido do custo de coleta). Para pausa mínima de dois minutos, use --cooldown 120; se ainda estiver quente/ocupado, o lote espera mais.

--no-temperature-check desativa a barreira de recuperação inteira (incluindo uso), mas mantém a pausa mínima e a tentativa de coleta. Use apenas com monitoramento externo ou em máquinas sem sensores suportados; indisponibilidade não é temperatura zero. Se nvidia-smi está instalado mas falha, a barreira padrão não considera a GPU liberada.

## O que salva

Cada lote cria uma pasta nova e não modifica rodadas anteriores:

- batch.json: estado, ordem, repetições, parâmetros fornecidos, política de recuperação, commit/status Git disponíveis, inventário Ollama e resumo por geração.
- summary.md: tabela de aprovação/tempo/geração, links para cada resposta e picos amostrados.
- telemetry.jsonl: uma amostra JSON por linha durante preparação, espera, inferência e recuperação; inclui horário UTC, fase e índice da rodada (base zero).
- case/: cópia congelada do manifesto, prompt, entrada e referência para todas as gerações do lote.
- runs/: registros completos produzidos pelo executor existente, com resposta original, snapshots, requisição, resposta da API, hashes e avaliação estrita.

Telemetria inclui CPU %, RAM total/usada estimada por MemAvailable, temperatura CPU, temperatura/uso/VRAM por GPU NVIDIA. Dados indisponíveis ficam nulos ou listados em errors. GPU sem coleta tem lista vazia; não significa uso zero. A primeira amostra CPU não tem percentual porque exige dois instantes. Índices de GPU não são identidades persistentes de hardware.

Picos por inferência são amostrados, podem perder transientes e não representam máximos instrumentados garantidos. A coleta e mudanças de fase têm resolução limitada; amostras na fronteira podem abranger preparação ou finalização. Uso é do sistema inteiro, incluindo desktop e demais serviços; não é atribuição exclusiva ao modelo nem medição de energia. Os campos métricos antigos de result.json permanecem como estavam: telemetria nova está no lote e no arquivo JSONL, não é inserida retroativamente nas respostas.

O comando avalia o caso automaticamente. Não repara JSON, não remove Markdown nem usa IA para julgar conteúdo. Essa análise automática cobre somente os checks do avaliador existente; análise qualitativa posterior pode acrescentar achados sem alterar a nota original.

## Falhas e interrupção

Reprovação funcional (passed=false) é um resultado válido: o lote continua após a recuperação. Falha HTTP, timeout, erro de gravação/coleta detectado ou Ctrl+C encerra o lote, registra o estado possível e não tenta automaticamente o próximo modelo. Timeout/Ctrl+C do cliente não confirmam cancelamento no servidor. Confira o serviço antes de retomar. Não existe retomada automática de lote interrompido; um novo comando cria outro lote.

**Esta versão acompanha a temperatura durante a geração, mas só controla o início da próxima rodada. Não implementa corte térmico automático durante uma requisição.** Mantenha acompanhamento na validação inicial, especialmente no equipamento com histórico de desligamento. Se precisar interromper a carga, pare o serviço em outro terminal e confirme o estado:

```bash
sudo systemctl stop ollama
systemctl is-active ollama
```

Pausa fixa ou adaptativa não garante um pico menor dentro da próxima inferência. O mecanismo também não bloqueia outros clientes ou processos externos do sistema.

## Repetições e comparação

--repetitions 2 com modelos A B produz A1, B1, A2, B2, sempre sequencial. A ordem é explícita, não aleatória; efeitos de ordem/cache não são eliminados. Cada geração conserva o protocolo first_response e attempt=1; o número da repetição está no lote. O adaptador solicita keep_alive=0; isso não elimina caches do SO nem confirma descarga em todos os cenários de falha.

Não misture os casos 1.0.0 (original) e 1.1.0 (instruções explícitas) como se fossem um único tratamento. Tokens/s entre tokenizadores diferentes não equivalem diretamente a produtividade.

## Publicar para análise

O padrão é results/runs/batches, ignorado pelo Git. O exemplo acima escolhe explicitamente results/published/batches, para publicar o lote completo. Revise os arquivos: prompts/respostas, nomes de modelos e status Git podem revelar detalhes locais. Casos sintéticos atuais usam dados fictícios; novos casos podem não usar.

Depois de conferir o caminho impresso e o resumo:

```bash
git status --short
git add results/published/batches
git diff --cached --stat
git diff --cached
```

Se o conteúdo estiver adequado:

```bash
git commit -m "results: add sequential local-model batch with telemetry"
git push origin feat/ollama-runner
```

O programa não faz commit/push. Compartilhe o hash ou caminho do lote; a análise pode ler diretamente os registros no repositório. Não é necessário colar respostas ou temperaturas no chat. Preserve também lotes com falhas; não publique somente aprovações.

## Validação de desenvolvimento

**51 testes passaram em Python 3.12.14.** Testes usam servidor HTTP simulado e amostras controladas. A validação automatizada inclui ordem sequencial, intervalos, resultados aprovados/reprovados, snapshots, digests, falhas sem retentativa, interrupção, barreira de recuperação e GPU indisponível. Não é evidência de funcionamento dos sensores do homelab; esse é o próximo teste de campo. O ramo de execução única continua disponível.
