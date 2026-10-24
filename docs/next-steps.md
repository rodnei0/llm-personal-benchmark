# Próximos passos

## Entregue na versão 0.4.0

- Lotes sequenciais com mínimo de 30 s, telemetria e recuperação adaptativa.
- Controle térmico opcional durante inferência com parada de ollama.service e registro da confirmação; testes simulados, ensaio real pendente.
- Catálogo suites/knowledge-v1.json: 12 casos de ciência, matemática, física e raciocínio. Seis objetivos automáticos e seis pendentes de revisão humana. Nenhuma inferência desses casos realizada durante o desenvolvimento.
- suite-ollama para executar casos em sequência, com snapshots, resultados e telemetria por lote.

## Agora, no homelab

1. Atualizar o código e executar os testes.
2. Configurar permissão restrita de parada e validar thermal-check --test-stop sem modelos carregados, conforme docs/thermal-guard.md.
3. Reiniciar o serviço manualmente e validar uma pergunta em modelo pequeno com --thermal-guard.
4. Só então considerar a suíte, preservando todas as respostas, interrupções e revisões humanas.

## Depois

Revisar referências/rubricas, analisar diferenças entre conhecimento e atendimento de formato, criar variações inéditas antes das próximas rodadas. Manter resultados separados do LOG-001 e não produzir ranking geral. Retomar casos de programação e infraestrutura planejados. Reavaliar refrigeração antes de novas séries pesadas com 7B ou maiores.
