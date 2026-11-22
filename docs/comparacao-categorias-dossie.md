# Dossiê — Comparação por categoria (entregável 7 / issue #110)

Escopo: comparar **scanner local de descoberta técnica** com três categorias que a FAQ já cita sem nome:
1. mapeamento por autodeclaração (plataformas de privacy management / questionários),
2. DPO-as-a-Service,
3. planilha/modelo da ANPD (ROPA).

Regra (`.agents/product-marketing.md`): todo claim sobre categoria de terceiros é **datado e com fonte pública**, reconhece a força da categoria, e não cita fabricante nem produto pelo nome. Evidência, não conclusão jurídica.

---

## Fatos públicos verificados (com data e fonte)

### Categoria 3 — planilha / modelo da ANPD (ROPA)

- **Fato (jun/2023):** a ANPD publicou o **modelo definitivo de ROPA** (Registro das Operações de Tratamento de Pessoais) para agentes de tratamento de pequeno porte, depois de consulta pública, conforme art. 9º da Resolução ANPD nº 2/2022. Fonte: Mayer Brown, "Modelo Definitivo de ROPA para Agentes de Pequeno Porte", 29 jun 2023 — https://www.mayerbrown.com/pt/insights/publications/2023/06/anpd-publishes-record-of-processing-activities-ropa-template-for-small-processing-agents
- **Fato (jun/2023):** o ROPA é **documento essencial e obrigatório** (art. 37 da LGPD, Lei 13.709/2018) e reflete o mapeamento das atividades de tratamento de controladores e operadores. **Mesma fonte.**
- **Fato (jun/2023):** o modelo da ANPD inclui campos como finalidade, categorias de titulares, categorias de dados, compartilhamentos com terceiros, medidas de segurança e período de armazenamento. **Mesma fonte.**
- **Fato (jun/2023):** a ANPD indicou bases legais em exemplos do modelo, mas o próprio artigo observa que essas escolhas **"possuem controvérsias e não devem ser tomadas como vinculantes"**. **Mesma fonte.**
- **Força da categoria:** é o instrumento oficial, gratuito e obrigatório — dá forma e linguagem comuns ao inventário. É o ponto de partida correto para quem está começando.

### Categoria 2 — DPO-as-a-Service

- **Fato (jan/2022):** a **Resolução CD/ANPD nº 2, de 27/01/2022** dispensa agentes de tratamento de pequeno porte da nomeação de encarregado, e prevê que a indicação do encarregado é considerada política de boas práticas e governança (art. 52, §1º, IX da LGPD). Fonte oficial: https://www.gov.br/anpd/pt-br/documentos-e-publicacoes/regulamentacoes-da-anpd/resolucao-cd-anpd-no-2-de-27-de-janeiro-de-2022
- **Fato (2021+):** a ANPD mantém **guia oficial sobre a atuação do encarregado** pelo tratamento de dados pessoais. Fonte: http://www.gov.br/anpd/pt-br/centrais-de-conteudo/materiais-educativos-e-publicacoes/copy_of_guia_da_atuacao_do_encarregado_anpd.pdf
- **Força da categoria:** leva responsabilidade regulatória, interface com a autoridade e a titulares, e interpretação jurídica — coisas que uma ferramenta de varredura não faz nem deveria fazer.
- **Qualificador obrigatório:** DPO-as-a-Service **não dispensa** o controlador de suas responsabilidades; a delegação da função não transfere a responsabilidade legal.

### Categoria 1 — mapeamento por autodeclaração

- **Fato (2018+):** a **LGPD art. 37** exige que controlador e operador mantenham registro das operações de tratamento — é um dever de registro, não de varredura técnica. Fonte: Lei 13.709/2018 (texto oficial).
- **Fato (2026):** o **PPSI 2.0** do Governo Federal publica guia para elaboração do ROPA, com aderência ao FCI da ANPD (campos sobre dados pessoais afetados em incidentes espelham o inventário). Fonte: Guia para Elaboração do Registro das Operações de Tratamento v1.0, 01/07/2026 — https://www.gov.br/governodigital/pt-br/privacidade-e-seguranca/ppsi-2.0/arquivos/guia-para-elaboracao-do-registro-das-operacoes-de-tratamento-v1-0-01072026.pdf
- **Força da categoria:** captura **contexto que a varredura não vê** — finalidade, base legal, prazo de retenção, contratos, decisões humanas. É o que dá significado jurídico ao inventário.
- **Limite honesto:** depende do que as áreas declaram; o que não foi declarado não aparece. Reconhecer isso é reconhecer a força da descoberta técnica, não diminuir a autodeclaração.

### Scanner local de descoberta técnica (nosso)

- **Fato (verificável no código aberto):** o DataBoar varre alvos configurados e produz **metadados e achados estruturados** com regras, validação e referência normativa; o conteúdo dos dados não sai do ambiente no caminho de decisão. Fontes: repositório público e `docs/MAP.md`.
- **Limite honesto:** achado é **sinal de inventário e triagem**, não conclusão jurídica; cobertura é parcial e depende de conectores e configuração; o teste documentado é de resolução/achado, não de instalação em todas as plataformas.

---

## Matriz de leitura rápida (rascunho para a página)

| Dimensão | Scanner local | Autodeclaração | DPO-as-a-Service | Planilha ANPD |
|---|---|---|---|---|
| O que entrega | Sinais técnicos de onde dados vivem | Registro declarativo de tratamentos | Responsabilidade e interpretação regulatória | Modelo obrigatório de registro |
| Fonte do dado | Varredura do ambiente | Questionário/entrevista | Análise jurídica | Preenchimento manual |
| Força | Encontra o que ninguém declarou | Dá contexto (finalidade, base legal) | Decide e representa | É o instrumento oficial |
| Limite | Não decide, cobertura parcial | Depende do que foi dito | Não substitui o controlador | Estático, depende de manutenção |
| Preço | — (fora de escopo) | — (fora de escopo) | — (fora de escopo) | Gratuito (modelo público) |

---

## Tom da redação na página (aprovado em conversa)

Comparar com as ferramentas comerciais **sem nome e sem divulgação**, em termos genéricos mas claros:

> "Grandes ferramentas de descoberta de PII costumam exigir agente instalado, índice centralizado e classificação por modelo de linguagem. Nossa opção é determinística, roda no ambiente do cliente e produz achados com regra, validação e referência normativa. Cada caminho tem seu lugar — a escolha é do controlador, com o DPO e o jurídico."

Este é o tom. Não usar "alternativa a X", nomes de fabricante, superlativo ("melhor", "líder") ou "nunca mais". O "por quê do nosso jeito" vem com evidência verificável, não com promessa.

**Princípio do operador (22/nov/2026):** *quem já conhece as ferramentas entende a comparação pelo padrão descrito; quem não conhece, não pretendemos divulgar.* Nomear terceiro não acrescenta clareza para o público-alvo e ainda transfere para nós o ônus de provar afirmações específicas sobre a empresa — o padrão de categoria, sim, é documentável com fonte. Mantemos a comparação reconhecível sem fazer divulgação gratuita de ninguém.

## Claims que **NÃO** entram (sem fonte ou fora de escopo)

- Nenhum nome de fabricante/produto (BigID, OneTrust, Collibra, Thales, etc.). Vale para **todos** — inclusive nomes ligados à trajetória do operador (ex-empregadores, parceiros, clientes). Nenhum terceiro vira slogan/divulgação gratuita.
- "Alternativa a X", "X vs Y", superlativos ("melhor", "líder"), "nunca mais".
- Preço de concorrente ou qualquer comparação de preço.
- Depoimento de migração, seção de migração, parceiros, clientes, planos.
- Número de desempenho 1.7.4 vs 1.8.0 (não medido). Único número citável: 4,69× do filtro Rust isolado — e mesmo assim só se couber com fonte.

## Pendência de aprovação (7.6)

Antes do merge, o operador deve aprovar:
1. Os quatro "Força da categoria" acima.
2. Os quatro "Limite" acima.
3. A frase de fechamento: "Nenhuma categoria substitui as outras — elas respondem perguntas diferentes. A escolha é do controlador, com o DPO e o jurídico."
