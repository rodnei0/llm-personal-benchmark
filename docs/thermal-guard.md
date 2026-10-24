# Controle térmico durante a inferência (experimental)

Versão 0.4.0. Implementação testada com temperaturas e serviço simulados; **a parada real no homelab ainda precisa do ensaio abaixo**. Este mecanismo amostrado não é proteção de hardware nem garante que não haverá ultrapassagem do limiar.

## Escopo

Ativado explicitamente por --thermal-guard em batch-ollama ou suite-ollama. O modo de lote sem essa opção conserva apenas telemetria/recuperação entre rodadas. run-ollama não tem esse controle; use lote de um modelo para execução protegida.

O modo protegido autoriza parar **todo ollama.service**, inclusive qualquer outro cliente que o esteja usando. Exige API HTTP local na porta 11434; systemd com cgroup v2 legível; KillMode=control-group; SendSIGKILL=yes; OLLAMA_HOST=127.0.0.1:11434 declarado no serviço; leitura coretemp e temperaturas NVIDIA se nvidia-smi estiver instalado. Docker, servidor remoto e Ollama iniciado manualmente não são cobertos.

Durante geração, monitora as amostras e, por padrão, solicita parada quando CPU >=85 °C ou GPU >=80 °C. São valores conservadores iniciais da política do laboratório, não limites oficiais do componente. Configuráveis por --abort-cpu-temp e --abort-gpu-temp. Amostragem deve ser <=2 s no modo protegido, mas consultas nvidia-smi podem acrescentar até 3 s, além de agendamento do SO. A temperatura pode ultrapassar o limiar antes da reação.

Erro/perda de sensor obrigatório, monitor interrompido, falha de execução, timeout ou Ctrl+C durante inferência também solicita parada. O lote é encerrado em todos esses casos, sem tentar próximo modelo e sem reiniciar o Ollama. Não conta interrupção como resposta errada do modelo.

## Configurar permissão restrita no homelab

O programa não instala permissões e não pede senha durante uma emergência. Não rode o benchmark inteiro como root.

Confira o caminho do executável:

```bash
command -v systemctl
systemctl show ollama --property=KillMode,SendSIGKILL,ControlGroup,Environment --no-pager
```

Se o caminho for /usr/bin/systemctl, o usuário rodnei pode configurar uma regra exclusiva com o editor de sudoers:

```bash
sudo visudo -f /etc/sudoers.d/llm-lab-ollama-stop
```

Conteúdo para esse usuário e esse caminho (outros leitores devem substituir usuário/caminho pelos próprios):

```text
rodnei ALL=(root) NOPASSWD: /usr/bin/systemctl stop ollama.service
```

Valide a configuração:

```bash
sudo visudo -c
```

A regra permite somente esse comando de parada. Não autoriza start, restart, shell ou comandos arbitrários. O processo usa argumentos fixos e sudo -n, sem shell e sem armazenar senha. Para remover a autorização no futuro, remova o arquivo dedicado com sudo e valide novamente com visudo -c.

## Ensaio obrigatório sem inferência

Atualize o projeto/venv. Com o serviço ativo e sem outros clientes usando a API:

```bash
llm-lab thermal-check
ollama ps
```

Se não houver modelo carregado, execute:

```bash
llm-lab thermal-check --test-stop
```

Este comando não aquece o equipamento nem gera resposta; para o serviço e verifica seu encerramento. O resultado deve conter shutdown.confirmed=true. Envie a saída para registrar a validação de campo. Se falhar, não inicie carga pesada nem declare a proteção validada.

A confirmação exige simultaneamente serviço inactive, MainPID=0, grupo original e seus descendentes sem processos (ou removidos), e conexão recusada na API. Serviço apenas "failed", HTTP timeout ou simples término da thread Python não contam como confirmação. O stop tem timeout de 15 s, seguido de verificação por até 10 s; shutdown.confirmed=false significa que o encerramento NÃO foi comprovado. O job do systemd pode continuar parando o serviço após o timeout do cliente.

Reinicie manualmente após o ensaio, quando for adequado:

```bash
sudo systemctl start ollama
```

## Executar depois do ensaio

```bash
llm-lab batch-ollama \
  --case cases/LOG-001 \
  --models qwen2.5-coder:3b-instruct-q4_K_M \
  --thermal-guard \
  --abort-cpu-temp 85 \
  --abort-gpu-temp 80 \
  --output-root results/published/batches
```

O lote conserva mínimo de 30 s entre rodadas e barreira de recuperação; o modo protegido não permite desabilitar a barreira nem definir os limites de início acima dos de corte. Não retome automaticamente uma rodada abortada.

## Registro e limites de confirmação

batch.json registra política, preflight, motivo, estado aborted, evidência de shutdown e client_finished. telemetry.jsonl mantém as amostras. Avaliação da rodada abortada é null, não reprovação funcional. Se a resposta já foi salva antes de detectar a última amostra quente, seus arquivos podem existir, mas o lote ainda é marcado abortado; preserve tudo e não conte silenciosamente como rodada normal.

Se a solicitação foi interrompida antes de a API devolver resposta, não há garantia de texto parcial: o adaptador usa stream=false. Não inventar artefato de resposta. Encerrar por SIGKILL ou desligamento da máquina ainda pode impedir o fechamento dos registros; examine o último estado persistido.

A confirmação se limita ao serviço configurado, seu grupo de processos e endpoint. Não demonstra que outros programas no computador cessaram carga ou que o hardware esfriou. Não substitui manutenção da refrigeração. A GPU pode permanecer quente após descarregar o modelo.

Base técnica: https://www.freedesktop.org/software/systemd/man/latest/systemd.kill.html
