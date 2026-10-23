# Metodologia v0.1

## Unidade de comparação

Participante = modelo informado + interface + configuração + data. Interfaces comerciais incluem condições internas não controláveis; o experimento compara utilidade prática nessas condições, não somente pesos de modelos.

## Protocolo inicial

Uma resposta por conversa nova, sem correções ou edição humana; tentativa 1, intervenções 0. Os comandos desta versão só representam esse protocolo. Resultados assistidos não devem ser importados como primeira resposta. Se memória, ferramentas ou contexto não puderem ser desativados, registre explicitamente.

O prompt público e a entrada são congelados por versão. O hash da referência é separado e a referência nunca entra no prompt. Alterações de comportamento exigem nova versão do caso/avaliador. Não selecionar a melhor resposta nem descartar falhas. Repetições futuras terão conversas independentes e todas serão preservadas.

## LOG-001

Sete linhas fictícias; IPs de documentação. Duas falhas completas únicas, uma duplicata, duas falhas inválidas, dois sucessos. A referência foi escrita explicitamente e o avaliador faz comparação estrutural, sem chamar LLM. A ordem das chaves não importa; a ordem dos eventos e linhas inválidas importa. Espaços JSON não importam. Markdown, chaves duplicadas, campos extras, NaN, campos não string e booleanos usados como números são rejeitados.

Aprovação funcional = JSON válido + contrato válido + eventos exatos + linhas inválidas exatas. Não há crédito parcial agregado nesta versão. Checks individuais são evidência diagnóstica. Os testes do avaliador incluem mutações de respostas, entrada inválida, rastreabilidade e proteção contra sobrescrita do prompt exportado.

## Métricas

Tempo manual é opcional e declarado, sem inferência de tokens. CPU, RAM, temperatura e taxa de geração são nulos porque não medidos. Clareza, segurança e confiabilidade não recebem notas artificiais nesta etapa; o avaliador comprova apenas o contrato de extração. Resultado demonstrativo não deve integrar comparações reais.

Versão do executor, avaliador, caso, configuração declarada, hashes e snapshots permitem rastrear o experimento. A identidade exata de modelos comerciais e parâmetros ocultos não pode ser garantida pelo importador. Os metadados manuais dependem do responsável pelo experimento.
