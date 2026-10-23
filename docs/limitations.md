# Limitações

- Um único caso não representa capacidade geral nem suporta ranking de modelos.
- Nenhum modelo foi executado nesta entrega. Exemplos usam fixtures.
- O avaliador compara com referência fixa; seu acerto depende da qualidade do caso.
- O catálogo é público: há risco de contaminação. Variantes futuras devem ser congeladas antes da rodada.
- O importador confia nos metadados declarados e não audita o conteúdo de uma sessão comercial.
- Não existe isolamento para execução de código gerado, porque esta versão não executa código de participantes.
- O executor ainda não registra status de inferência, commit Git ou inventário do homelab; não há inferência nesta versão.
- O esquema é documentado pelos registros e pelo código; validação JSON Schema e migrações ficam para expansão.
- O homelab, GPU, sensores, limites térmicos e comportamento de cancelamento ainda não foram inspecionados.
- Nenhum custo elétrico foi medido. Não há suposição de equivalência entre tokens de diferentes modelos.
