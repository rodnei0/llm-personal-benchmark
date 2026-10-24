# Limitações

- Um único caso não representa capacidade geral nem suporta ranking de modelos.
- Nenhum modelo real foi executado na validação de desenvolvimento. Exemplos usam fixtures; o adaptador HTTP foi testado com servidor simulado.
- O avaliador compara com referência fixa; seu acerto depende da qualidade do caso.
- O catálogo é público: há risco de contaminação. Variantes futuras devem ser congeladas antes da rodada.
- O importador confia nos metadados declarados e não audita o conteúdo de uma sessão comercial.
- Não existe isolamento para execução de código gerado, porque esta versão não executa código de participantes.
- O adaptador registra somente inferências concluídas. Falhas HTTP, timeout e interrupções ainda exigem diário manual. Não registra commit Git, digest do modelo, versão do Ollama ou inventário do homelab automaticamente.
- O esquema é documentado pelos registros e pelo código; validação JSON Schema e migrações ficam para expansão.
- O homelab, GPU, sensores, limites térmicos e comportamento de cancelamento ainda não foram inspecionados.
- Nenhum custo elétrico foi medido. Não há suposição de equivalência entre tokens de diferentes modelos.

