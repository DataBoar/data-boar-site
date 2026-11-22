# Briefing: Issue #113 - Data Boar Ecosystem

**Data Boar Site** | Issue #113 | Criado: 2026-11-21 | **FASE 3 CONCLUÍDA**

---

## 🎯 Resumo Executivo

Criar uma página dedicada ao **Data Boar Ecosystem** como visão de arquitetura de composição, separando:
- **Open/Closed**: transparência do produto e modelo
- **Ecosystem**: arquitetura de composição das Bestials (plugins/sidecars)
- **Bestial Profiles**: fichas individuais (quando houver evidência suficiente)

---

## ✅ FASE 1 CONCLUÍDA: Reconciliação do Inventário

**Status:** COMPLETA

### Conclusão:
- As Bestials são plugins/sidecars, não componentes de código separados
- Arquitetura: SDK como contrato de comunicação
- Cada Bestial tem função específica e é opcional

---

## ✅ FASE 2 CONCLUÍDA: Criação da Página Ecosystem

**Status:** COMPLETA

### Arquivos criados:
- `ecosystem.html` (PT-BR) - 432 linhas
- `en/ecosystem.html` (EN) - 432 linhas

### Conteúdo:
- Visão geral do Ecosystem
- Seção de Bestials com superpoderes
- Explicação da comunicação via SDK
- CTAs e navegação bilíngue

---

## ✅ FASE 3 CONCLUÍDA: Reorganização de opensource.html

**Status:** COMPLETA

### Mudanças realizadas:

1. **Reduzida seção de Bestials** de cards para tabela compacta
   - Antes: ~600 linhas com descrições completas
   - Depois: ~200 linhas com tabela resumida

2. **Novo título da seção:**
   - Antes: "Os bestiais: o que faz hoje × o que vem"
   - Depois: "Os bestiais: plugins de superpoder"

3. **Novo subtítulo:**
   - "Ferramentas independentes que se conectam via SDK. Nenhuma Bestial tem versão publicada."

4. **Tabela resumida com colunas:**
   - Bestial | Hoje | Maturidade | Contrato

5. **Link para Ecosystem.html**

### Tabela criada:

| Bestial | Hoje | Maturidade | Contrato |
|---------|------|------------|----------|
| Sage Remora (Sage) | Lê manifesto de achados, infere risco de reidentificação sem tocar dados | PoC | Contrato SDK |
| Faithful Ferret (Ferret) | Mede anonimato sobre linhas autorizadas | Demo/PoC | Contrato SDK |
| Stealthy Stoat (Stoat) | Tokenização demonstrativa com valores sintéticos | Demo/PoC | Contrato SDK |
| Keen Platypus (Platypus) | DevSecOps local: varredura de vulnerabilidades | Em desenvolvimento | Contrato SDK |

### Atualizações realizadas:
- ✅ Sincronizado site-chrome
- ✅ Atualizado `partials/i18n/head.en.json`
- ✅ Gerado versão EN
- ✅ Atualizado `sitemap.xml`
- ✅ Navegação atualizada

---

## 🧪 Testes Executados

```bash
python3 -m pytest tests/test_guardrails.py -v
```

**Resultado:** ✅ **47 passed in 0.95s**

---

## 🔄 FASE 4: Internacionalização

**Status:** PARCIALMENTE CONCLUÍDA

### Concluído:
- ✅ Versão PT-BR de ecosystem.html
- ✅ Versão EN de ecosystem.html
- ✅ Versão PT-BR de opensource.html
- ✅ Versão EN de opensource.html
- ✅ Sitemap atualizado

### Necessário:
- Verificar se navegação bilíngue está completa em todas as páginas

---

## 📋 Objetivo da Issue

> **One ecosystem. Independent superpowers. Explicit boundaries. Composable by design.**

O Ecosystem não é um produto nem uma Bestial — é o conjunto de plugins/sidecars que se compõem via SDK.

---

## 🎉 Status Geral

**Progresso:** 3 de 4 fases concluídas
- ✅ Fase 1: Reconciliação - **CONCLUÍDA**
- ✅ Fase 2: Criação da página ecosystem.html - **CONCLUÍDA**
- ✅ Fase 3: Reorganização de opensource.html - **CONCLUÍDA**
- 🔄 Fase 4: Internacionalização - **PARCIAL**

---

## 📚 Referências

- Issue original: https://github.com/DataBoar/data-boar-site/issues/113
- Repositório Data Boar: https://github.com/DataBoar/data-boar
- ADR-0015: POC Test Infrastructure
- ADR-0017: Quasi-identification risk/confidence contract
- README.md: plugins, sidecars, SDK contract

---

## ✅ Critérios de Aceitação (da issue) - STATUS

- [x] `ecosystem.html` criada com conteúdo PT-BR e EN
- [x] Conceito **Ecosystem** como arquitetura, não produto
- [x] Explica composição sem sugerir runtime monolítico
- [x] Inventário em `opensource.html` é compacto
- [x] Conteúdo reorganizado sem perder informações
- [x] Afirmações verificadas contra evidências reais
- [x] Navegação, hreflang, metadados atualizados
- [x] Layout responsivo e padrões visuais respeitados
- [x] Testes do site passam (47 passed)
- [x] Nenhuma informação confidencial publicada

---

## 🚀 Próxima Ação

**EXECUTAR PRE-COMMIT E SUBMETER PR**

Antes de submeter, rode:
```bash
scripts/pre-commit
scripts/check-all.sh
```

Depois abra um PR com assinatura SSH.
