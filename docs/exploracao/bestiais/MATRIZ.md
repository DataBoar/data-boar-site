# Matriz de Bestials - Reconciliation for Issue #113

**Data Boar Site** | Issue #113 | Criado: 2026-11-21 | Última atualização: 2026-11-21

---

## 🎯 Objetivo

Reconciliar o inventário público de Bestials em `opensource.html` com a evidência real disponível nos repositórios do Data Boar, distinguiendo:
- Implementações reais vs mocks/interfaces
- Evidências verificáveis vs planejamentos
- Estado de maturidade real vs declarado

---

## 📊 Matriz de Bestials

### 1. Sage Remora (Sage)

| Campo | Status | Fonte/Evidência |
|-------|--------|-----------------|
| **Estado** | Hoje | Documentado em opensource.html |
| **Função** | Lê manifesto de achados, infere risco de reidentificação, decide política de tokenização | opensource.html secção "bestiais" |
| **Evidência Verificável** | ❓ **NÃO VERIFICADO** - Precisa revisar código-fonte | Links: https://github.com/DataBoar/data-boar (repositório mencionado) |
| **Repositório** | ? | Não especificado em opensource.html - verificar data-boar-core |
| **Mock/Interface/PoC** | Sim (rótulo) | "Regras atuais são conteúdo ilustrativo de prova de conceito" |
| **Maturidade** | **Em desenvolvimento** - PoC | Não há evidência de validação em produção |
| **Dados que toca** | Metadados (nunca valores) | Recusa manifesto com valor cru |
| **Autorização** | ? | Não especificado |
| **Links externos** | GitHub DataBoar | https://github.com/DataBoar/data-boar |

**Observações:**
- Declaração clara: "regras atuais são conteúdo ilustrativo de prova de conceito, não um conjunto de regras validado"
- **NÃO** é produto final - é demonstração

---

### 2. Faithful Ferret (Ferret)

| Campo | Status | Fonte/Evidência |
|-------|--------|-----------------|
| **Estado** | Hoje | Documentado em opensource.html |
| **Função** | Mede k-anonimato sobre linhas autorizadas | opensource.html secção "bestiais" |
| **Evidência Verificável** | ❓ **NÃO VERIFICADO** - Precisa revisar código-fonte | |
| **Repositório** | ? | Não especificado |
| **Mock/Interface/PoC** | Sim (rótulo) | "exercitada hoje só com dados sintéticos, em modo de desenvolvimento" |
| **Maturidade** | **Demo/PoC** | Não validado em ambiente real |
| **Dados que toca** | Linhas já autorizadas (não se conecta a banco) | |
| **Autorização** | Sim (grant explícito) | |
| **HSM testado** | ❌ Não | "cliente de HSM tem transporte simulado: nunca foi testado contra um HSM real" |
| **Links externos** | GitHub DataBoar | |

**Observações:**
- Limiares são "de prova de conceito, não uma metodologia certificada"
- **NÃO** é produto maduro

---

### 3. Stealthy Stoat (Stoat)

| Campo | Status | Fonte/Evidência |
|-------|--------|-----------------|
| **Estado** | Hoje | Documentado em opensource.html |
| **Função** | Tokenização FF1 (NIST SP 800-38G) em Rust | opensource.html secção "bestiais" |
| **Evidência Verificável** | ❓ **NÃO VERIFICADO** - Precisa revisar código-fonte | |
| **Repositório** | ? | Não especificado |
| **Mock/Interface/PoC** | Sim (rótulo) | "roda como demonstração, só com valores sintéticos" |
| **Maturidade** | **Demo/PoC** | Não testado contra HSM real |
| **Dados que toca** | Valores sensíveis (tokenização) | |
| **HSM testado** | ❌ Não | "transporte simulado: nunca foi testado contra um HSM real" |
| **CAVP/FIPS** | ❌ Não | "não tem validação CAVP/FIPS e não é um HSM" |
| **Links externos** | GitHub DataBoar | |

**Observações:**
- Usa algoritmo FF1 padronizado, mas **não é HSM**
- **NÃO** é implementação de produção

---

### 4. Keen Platypus (Platypus)

| Campo | Status | Fonte/Evidência | |
|-------|--------|-----------------|
|-------|--------|-----------------|
| **Estado** | Hoje | Documentado em opensource.html |
| **Função** | DevSecOps local: varredura de vulnerabilidades, revisão de código e cadeia de suprimentos | opensource.html secção "bestiais" |
| **Evidência Verificável** | ❓ **NÃO VERIFICADO** - Precisa revisar código-fonte | |
| **Repositório** | ? | Não especificado (menciona "repositórios são privados") |
| **Mock/Interface/PoC** | Parcial | "testes automatizados usam dublês de scanner" |
| **Maturidade** | **Em desenvolvimento** | "reescrita poliglota em andamento, ainda incompleta" |
| **LLM no caminho crítico** | ❌ Não | "Data Boar segue sem LLM no caminho que decide o que é dado sensível" |
| **Pentest completo** | ❌ Não | "apenas correlação - não é um pentest completo" |
| **Links externos** | GitHub DataBoar | |

**Observações:**
- **NÃO** faz pentest completo
- Segrega papel do Data Boar (sem LLM)

---

## 🔗 Pipeline Mencionado

> **Ordem no pipe:** `Boar → Sage → Ferret`; a Sage também alimenta o Stoat (`boar | sage > stoat`)

**Importante:** As saídas são evidência técnica para uma **pessoa decidir**, não um veredito automático.

---

## 📋 Tarefas de Reconciliação Pendentes

### Para Validar/E auditorar:

1. **Sage Remora (Sage)**
   - [ ] Verificar código no repositório `data-boar`
   - [ ] Confirmar implementações real vs mock
   - [ ] Verificar testes automatizados
   - [ ] Identificar limiares e como são validados

2. **Faithful Ferret (Ferret)**
   - [ ] Verificar código
   - [ ] Confirmar implementação do k-anonimato
   - [ ] Verificar se há integração real com outros componentes
   - [ ] Identificar HSM simulado

3. **Stealthy Stoat (Stoat)**
   - [ ] Verificar código Rust
   - [ ] Confirmar implementação FF1
   - [ ] Verificar testes contra vetores NIST
   - [ ] Identificar HSM simulado

4. **Keen Platypus (Platypus)**
   - [ ] Verificar código
   - [ ] Confirmar análise de código e supply chain
   - [ ] Verificar dublês de scanner
   - [ ] Identificar limites de pentest

---

## 📍 Próximos Passos

1. **Verificar repositórios oficiais** do Data Boar
   - `https://github.com/DataBoar/data-boar`
   - Possíveis sub-repositórios

2. **Criar inventário detalhado** com:
   - SHA ou versão do código
   - Testes associados
   - Documentação disponível
   - Status de maturidade real (não declarado)

3. **Atualizar esta matriz** com evidências verificáveis

4. **Criar página ecosystem.html** com:
   - Matriz compacta de Bestials
   - Links para perfis individuais (quando criados)

---

## ⚠️ Alertas

- **Não confundir planejamento com implementação**
- **Não inferir integração end-to-end** de READMEs e mocks
- **Verificar todas as afirmações** contra código fonte
- **Respeitar a distinção** entre evidência técnica e hipótese

---

## 📚 Referências

- Issue original: https://github.com/DataBoar/data-boar-site/issues/113
- Página opensource.html: opensource.html
- ADR-0001: docs/adr/ADR-0001-guardrails-constitution.md