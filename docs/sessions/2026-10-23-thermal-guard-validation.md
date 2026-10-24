# Validação de campo do controle térmico — 2026-10-23

## Checagem prévia

Usuário executou llm-lab thermal-check e compartilhou a saída. Horário da amostra: 2026-10-24T02:13:31.726157+00:00 (2026-10-23 22:13:31 America/Cuiaba).

- Preflight concluído sem erro: serviço ollama.service ativo, KillMode=control-group, ControlGroup=/system.slice/ollama.service, gpu_required=true.
- CPU: 56 °C; GPU NVIDIA: 49 °C, 0% utilização, 4 MiB de 2048 MiB ocupados.
- Nenhum erro de coleta na amostra.
- cpu_percent=null é esperado na primeira amostra: o percentual exige dois instantes de /proc/stat, não indica ausência de temperatura.

Essa checagem verifica condições de configuração e consulta não interativa de permissão conforme implementadas; não executa stop e não comprova encerramento real dos processos. Saída não informa qual mecanismo concedeu a permissão; não se presume alteração de sudoers pelo usuário. Commit local e versão instalada não foram compartilhados nesta verificação.

## Pendente

Conferir ollama ps sem modelos carregados e executar llm-lab thermal-check --test-stop. Confirmar shutdown.confirmed=true antes de considerar o caminho de parada validado no equipamento. Não há inferência nem teste de limite térmico real confirmado nesta sessão. Nenhuma das 12 perguntas novas foi executada até este registro.

## Ensaio de parada: falha inicial de permissão

Após ollama ps exibir apenas o cabeçalho, o primeiro thermal-check --test-stop falhou: sudo exigiu autenticação interativa; stop_returncode=1, serviço active, PID ainda no grupo e API respondendo. Nenhuma carga de modelo foi executada no ensaio. A checagem sudo -n -l do preflight não comprovou autorização efetiva sem senha para o stop: é uma limitação observada, e o ensaio real continua necessário. Foi orientada regra sudoers restrita ao comando systemctl stop ollama.service; não foi compartilhado o conteúdo efetivamente instalado.

## Ensaio de parada confirmado

Usuário repetiu llm-lab thermal-check --test-stop e compartilhou saída em 2026-10-24T02:16:51.834406+00:00 (2026-10-23 22:16:51 America/Cuiaba).

- CPU 57 °C, GPU 49 °C; errors=[].
- shutdown.confirmed=true.
- stop_returncode=0; active_state=inactive; main_pid=0.
- remaining_pids=[]; api_connection_refused=true.

O ensaio resolveu a pendência de parada sem carga no equipamento. Não demonstra cancelamento durante geração real, tempo de reação sob carga ou contenção de pico térmico. Próximo passo: reinício manual do serviço, conferência de versão e uma execução SCI-001 com modelo pequeno e --thermal-guard, acompanhada. Não forçar aquecimento para testar corte. Novas perguntas ainda não executadas até este registro.
