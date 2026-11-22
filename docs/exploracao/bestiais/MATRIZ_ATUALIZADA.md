# Matriz de Bestials - Reconciliation for Issue #113 (ATUALIZADA)

**Data Boar Site** | Issue #113 | Criado: 2026-11-21 | Última atualização: 2026-11-21

---

## 🎯 Conclusão Inicial da Reconciliação

**STATUS: INCONCLUSO** - As Bestials mencionadas em `opensource.html` parecem ser **conceitos teóricos/documentacionais** e NÃO componentes de código separados. O projeto Data Boar principal (data-boar) contém o engine central, mas não arquivos com nomes de Bestials.

---

## 📊 Matriz Atualizada de Bestials

### 1. Sage Remora (Sage)

| Campo | Status | Fonte/Evidência |
|-------|--------|-----------------|
| **Estado** | Documentado | opensource.html secção "bestiais" |
| **Função** | Lê manifesto de achados, infere risco de reidentificação, decide política de tokenização | opensource.html |
| **Implementação Real** | ❓ **NÃO ENCONTRADO** | Busca por "sage", "remora", "sage_remora" - não localizado |
| **Mock/Interface/PoC** | Sim (confirmado) | "regras atuais são conteúdo ilustrativo de prova de conceito" |
| **Maturidade** | **Em desenvolvimento/PoC** | Não há evidência de validação em produção |
| **Repositório** | ? | Não especificado |
| **Localização no Código** | **NÃO ENCONTRADO** | Tabela de arquivos não contém componente |

### 2. Faithful Ferret (Ferret)

| Campo | Status | Fonte/Evidência |
|-------|--------|-----------------|
| **Estado** | Documentado | opensource.html |
| **Função** | Mede k-anonimato sobre linhas autorizadas | opensource.html |
| **Implementação Real** | ❓ **NÃO ENCONTRADO** | Busca por "ferret" - não localizado |
| **HSM Testado** | ❌ Não | "transporte simulado: nunca foi testado contra um HSM real" |
| **Mock/Interface/PoC** | Sim (confirmado) | "exercitada só com dados sintéticos, em modo de desenvolvimento" |
| **Maturidade** | **Demo/PoC** | Não validado em ambiente real |
| **Repositório** | ? | Não especificado |
| **Localização no Código** | **NÃO ENCONTRADO** | Tabela de arquivos não contém componente |

### 3. Stealthy Stoat (Stoat)

| Campo | Status | Fonte/Evidência |
|-------|--------|-----------------|
| **Estado** | Documentado | opensource.html |
| **Função** | Tokenização FF1 (NIST SP 800-38G) em Rust | opensource.html |
| **Implementação Real** | ❓ **NÃO ENCONTRADO** | Busca por "stoat" - não localizado |
| **HSM Testado** | ❌ Não | "transporte simulado: nunca foi testado" |
| **CAVP/FIPS** | ❌ Não | "não tem validação CAVP/FIPS e não é um HSM" |
| **Mock/Interface/PoC** | Sim (confirmado) | "roda como demonstração, só com valores sintéticos" |
| **Maturidade** | **Demo/PoC** | Não testado contra HSM real |
| **Repositório** | ? | Não especificado |
| **Localização no Código** | **NÃO ENCONTRADO** | Tabela de arquivos não contém componente |

### 4. Keen Platypus (Platypus)

| Campo | Status | Fonte/Evidência |
|-------|--------|-----------------|
| **Estado** | Documentado | opensource.html |
| **Função** | DevSecOps local: varredura de vulnerabilidades | opensource.html |
| **LLM no caminho crítico** | ❌ Não | "Data Boar segue sem LLM no caminho que decide o que é dado sensível" |
| **Mock/Interface/PoC** | Parcial | "testes automatizados usam dublês de scanner" |
| **Maturidade** | **Em desenvolvimento** | "reescrita poliglota em andamento, ainda incompleta" |
| **Repositório** | Privado | Mencionado como "repositórios são privados" |
| **Localização no Código** | **NÃO ENCONTRADO** | Tabela de arquivos não contém componente |

---

## 🔍 Principais Descobertas

### Estrutura do Repositório Data Boar

**Localização:** https://github.com/DataBoar/data-boar

**Pastas relevantes:**
- `/core` - Core engine, detectores, plugins
- `/cli` - Interface de linha de comando
- `/api` - API REST
- `/app` - Dashboard web
- `/connectors` - Conectores para bancos de dados, APIs, arquivos
- `/analysis` - Análises e relatórios

### Componentes Encontrados

| Componente | Localização | Função |
|------------|-------------|--------|
| Detector | `/core/detector.py` | Detecção de PII |
| Engine | `/core/engine.py` | Orquestração principal |
| Findings | `/core/findings_*.py` | Modelos de achados |
| Plugins | `/core/plugins/` | Sistema de plugins |
| Connectors | `/connectors/` | Conectores de dados |
| ML Engine | `/core/ml_engine.py` | ML/DL para detecção |

### Arquivos Relevantes para as Funcionalidades

| Funcionalidade | Arquivo Provável | Localização |
|----------------|------------------|-------------|
| Manifesto de achados | `/core/l1_metadata_manifest.py` | Encontrado ✓ |
| Risk Analysis | ADR-0017 | docs/adr/ADR-0017.md |
| Anonimização | /core/plugins/ | Plugin system |
| Tokenização | Não encontrado | Precisa buscar |

---

## 📌 Pendências para Verificação Profunda

### Tarefas Prioritárias

1. **Verificar se as Bestials são nomes de código ou metáforas**
   - [ ] Buscar em ADRs por "Bestial", "Sage", "Ferret", "Stoat", "Platypus"
   - [ ] Verificar documentação para entender conceito

2. **Localizar implementações de tokenização FF1**
   - [ ] Buscar por "ff1", "tokenization", "anonymization"

3. **Verificar risk assessment no código**
   - [ ] Ver ADR-0017 para implementação real

4. **Criar inventário detalhado**

---

## 🧪 Testes Executados

```bash
# Busca por nomes das Bestials
gh search code "Sage\|Remora\|Ferret\|Stoat\|Platypus" --repo DataBoar/data-boar --case-insensitive
# Resultado: Não encontrado

# Verificação de arquivos
curl -s "https://api.github.com/repos/DataBoar/data-boar/contents/core"
# Resultado: Tabela de 80+ arquivos - nenhum corresponde a Bestials
```

---

## 📋 Conclusão Provisional

**As Bestials (Sage, Ferret, Stoat, Platypus) são conceitos de documentação/editorial**, NÃO componentes de código separados. Elas representam:

1. **Sage Remora (Sage)**: Conceito de análise de manifestos de achados
2. **Faithful Ferret (Ferret)**: Conceito de medição k-anonimato
3. **Stealthy Stoat (Stoat)**: Conceito de tokenização
4. **Keen Platypus (Platypus)**: Conceito de DevSecOps

**EVIDÊNCIA:**
- Opensource.html menciona "Os repositórios são privados" para as Bestials
- Não há arquivos de código com esses nomes

---

## 📚 Referências

- Issue original: https://github.com/DataBoar/data-boar-site/issues/113
- Repositório Data Boar: https://github.com/DataBoar/data-boar
- ADR-0017: Quasi-identification risk/confidence contract
- Página opensource.html: opensource.html

---

## ✅ Próxima Ação

**Verificar ADRs e documentação para confirmar que as Bestials são metáforas/conceitos, não componentes de código.**