# ADR 001 — Primeiro ciclo completo

Status: aceito para piloto em 23/10/2026.

Decisão: Python 3.12+, JSON, CLI e pytest. Importação manual primeiro. Sem banco, dashboard ou chamadas de inferência. O armazenamento é append-only por convenção, com IDs únicos e snapshots.

Motivo: verificar o contrato de avaliação antes de automatizar geração. JSON evita dependência YAML; biblioteca padrão basta para este caso. O adaptador Ollama virá após o fluxo manual validado.

Consequências: primeira rodada comercial exige copiar respostas; não há captura automática de métricas. Execução de código gerado exigirá ambiente restrito próprio na etapa dos scripts. Não inicializar Git, criar commits, repositório remoto ou push sem confirmação específica do usuário.
