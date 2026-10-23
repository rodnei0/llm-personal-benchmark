# Registro de execução — 23/10/2026

Ambiente: workspace do ChatGPT Work, não o homelab. Python 3.12.14; pytest 9.1.1; Git 2.51.1.

Executado:

1. Instalação editável do pacote com dependências de desenvolvimento: sucesso.
2. `python -m pytest -q`: **17 passed in 0.05s**.
3. Exportação pela CLI: sucesso; prompt em results/examples/prompt-log-001.txt.
4. Importação da referência pela CLI: quatro critérios aprovados; data_kind=demonstrative; nenhuma inferência.

Os executáveis foram instalados fora do PATH deste workspace; por isso foi usada a forma `python -m llm_lab.cli`. Na instalação recomendada com venv, `llm-lab` estará disponível após ativação.

Nenhum modelo local ou comercial foi avaliado. Sem acesso ao homelab, sem telemetria, sem custo de API. Não houve inicialização Git, commit, push nem alteração externa no GitHub. Este pacote não contém a licença open source definitiva.
