# Trilha de conhecimento e raciocínio — catálogo inicial

Versão do catálogo: knowledge-reasoning-v1 1.0.0. Arquivo: suites/knowledge-v1.json. Preparado com assistência de IA e referências públicas; nenhuma resposta de modelo foi coletada antes de congelar estes casos. Referências e rubricas precisam de revisão humana antes de qualquer publicação de conclusões. Mantém-se separado dos casos de software/infraestrutura.

## Catálogo

| ID | Tema | Avaliação |
| --- | --- | --- |
| SCI-001 | Por que o céu é azul? | Rubrica humana |
| SCI-002 | Estações e hemisférios | Rubrica humana |
| SCI-003 | Metal/madeira à mesma temperatura | Rubrica humana |
| SCI-004 | Seleção de resistência em bactérias | Rubrica humana |
| MATH-001 | Equação linear | Numérica automática |
| MATH-002 | Probabilidade sem reposição | Numérica automática |
| PHYS-001 | Queda livre idealizada | Valor/unidade automáticos |
| PHYS-002 | Energia cinética clássica | Valor/unidade automáticos |
| REASON-001 | Afirmação do consequente | Booleano automático |
| REASON-002 | Contraexemplo sobre primos | Numérica automática |
| REASON-003 | Área indeterminada por perímetro | Rubrica humana |
| REASON-004 | Dedução das caixas rotuladas erradas | Rubrica humana |

Cada pasta em cases tem case.json, prompt.md, input.txt (vazio quando o enunciado está todo no prompt) e expected.json. O exportador/executor só envia prompt e entrada, nunca expected.json. A suíte copia todos os casos antes da primeira inferência; alterações futuras pedem nova versão do caso/catálogo.

## Como avaliar

Seis casos objetivos exigem JSON puro com answer; física também exige unit. Há tolerância absoluta documentada nos arquivos de referência, sem LLM avaliador. Rejeita Markdown, valores não finitos, campos extras e tipo incorreto. Resultado correto em formato proibido reprova: mede-se também atendimento do contrato. Para estudar conhecimento independente de formatação, será necessário outro protocolo, sem corrigir silenciosamente estes resultados. Os avaliadores numéricos comprovam a resposta final, não a qualidade de uma derivação, porque ela não é solicitada.

Seis casos conceituais/dedutivos exigem explicação curta. O resultado automático é passed=null, status=pending_human_review. Isso NÃO é reprovação nem aprovação. A rubrica traz conceitos obrigatórios, erros materiais e referência; aceita redação alternativa e exemplos equivalentes. Não há avaliação por palavras-chave.

O revisor deve ler a resposta original e preencher um arquivo separado de revisão com os campos listados no expected.json: reviewer, reviewed_at, criteria_evidence, major_errors_observed, passed e notes. Não editar result.json original. Cada decisão deve citar evidência do texto; referências servem como apoio, não resposta a copiar. IA pode auxiliar, mas não será o único juiz. Revisão humana ainda não tem importador/CLI específico nesta versão; mantenha o arquivo de revisão ao lado da resposta e publique-o junto.

Perguntas conhecidas podem estar nos dados de treinamento. Esses casos não provam generalização, raciocínio inédito ou ausência de memorização. Não há ranking geral. Quantidades de aprovações devem excluir casos ainda pendentes de revisão ou indicar pendências explicitamente.

## Uma pergunta primeiro

Após validar o [ensaio do controle térmico](thermal-guard.md), com serviço reiniciado e notebook resfriado:

```bash
llm-lab batch-ollama \
  --case cases/SCI-001 \
  --models qwen2.5-coder:3b-instruct-q4_K_M \
  --thermal-guard \
  --output-root results/published/batches
```

Esse primeiro caso ficará pendente de revisão humana. Você pode exportar o prompt para modelos comerciais com o comando export existente e importar respostas sem editar usando import-response. Registre modelo/interface e condições reais.

## Lote de perguntas

Depois de validar o primeiro caso, a suíte executa casos na ordem do catálogo; dentro de cada caso, modelos e repetições na ordem fornecida. Não há paralelismo. Com 12 casos e dois modelos serão 24 gerações mais os intervalos. Não começar pelo 7B neste equipamento com o histórico térmico registrado.

```bash
llm-lab suite-ollama \
  --suite suites/knowledge-v1.json \
  --models qwen2.5:3b gemma3:1b \
  --cooldown 30 \
  --repetitions 1 \
  --thermal-guard \
  --output-root results/published/suites
```

A suíte preserva casos congelados, suite.json, summary.md e todos os lotes/respostas/telemetria dentro da pasta criada. Cada novo caso também verifica recuperação térmica. O intervalo mínimo também vale entre lotes de casos. Um erro de infraestrutura ou corte encerra a suíte; falha funcional de um modelo não encerra; pending_human_review também não encerra. Não há retomada automática.

Após a execução, revise e publique a pasta results/published/suites. Compartilhe o commit para análise. Não é necessário colar cada resposta. Não misture esta trilha com LOG-001 para gerar uma nota global.

## Referências de ciência

Fontes consultadas em 2026-10-23; os links específicos constam também nas rubricas.

- Céu azul: https://spaceplace.nasa.gov/blue-sky/en/ e https://www.weather.gov/fgz/SkyBlue
- Estações: https://www.weather.gov/fsd/season
- Transferência de calor: https://www.aps.org/learning-resources/getting-warmer-colder e https://openstax.org/books/university-physics-volume-2/pages/1-6-mechanisms-of-heat-transfer
- Resistência antimicrobiana: https://www.cdc.gov/antimicrobial-resistance/about/

As explicações de referência são paráfrases curtas; SCI-004 é mecanismo evolutivo, sem aconselhamento de tratamento médico. Derivações matemáticas e hipóteses de física estão explícitas em expected.json.
