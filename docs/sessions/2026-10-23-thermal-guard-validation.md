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
