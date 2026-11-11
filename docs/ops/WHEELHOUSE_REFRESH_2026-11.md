# Wheelhouse x86-64-v1 — refresh de novembro/2026

**Status:** em andamento (Release nova ainda não publicada; `simple/` ainda aponta para a tag antiga).
**Issue de referência:** [DataBoar/data-boar#2218](https://github.com/DataBoar/data-boar/issues/2218)
**Inventário da Release atual:** [../WHEELHOUSE_X86_64_V1.md](../WHEELHOUSE_X86_64_V1.md)

## Por que

A Release `wheelhouse-x86-64-v1-2026-07-29` está defasada em relação aos pins do 1.8.0. O `simple/` é gerado a partir dos assets de uma Release (`scripts/build-wheelhouse-index.py`), então **o índice só muda depois que a Release nova existe**. Os `pandas`, `scikit-learn` e `scipy` mais novos que aparecem em `simple/` são wheels do **Haiku**, não do x86-64-v1.

## Delta medido (pins do `requirements.txt` × Release atual)

| Pacote | Pin (main) | Pin (v1.8.0) | Release atual |
| --- | --- | --- | --- |
| numpy | 2.5.4 | 2.5.4 | 2.5.1 |
| scipy | 1.18.1 | 1.18.1 | 1.18.0 |
| scikit-learn | 1.9.1 | 1.9.1 | 1.9.0 |
| pandas | 3.1.1 | 3.1.0 | 3.0.5 |
| joblib | 1.6.0 | 1.6.0 | 1.5.3 |
| narwhals | 2.28.0 | 2.27.1 | 2.24.0 |
| packaging | 26.3 | 26.3 | 26.2 |
| python-dateutil | 4.0.0 | 2.9.0.post0 | 2.9.0.post0 |
| threadpoolctl | 3.8.0 | 3.7.0 | 3.6.0 |
| tzdata | 2026.6 | 2026.5 | 2026.3 |

`main` e `v1.8.0` divergem em pandas e em quatro pacotes puros. A Release nova deve cobrir as duas versões desses.

## Procedimento

Receita documentada do produto (`scripts/wheelhouse/`, `recipe-manifest.yaml`), rodada **localmente**, sem CI: numpy, scipy e scikit-learn compilados do sdist; pandas e os wheels puros baixados do PyPI.

- numpy com `-Dcpu-baseline=none -Dcpu-dispatch=none`; imagens `python:<versão>-alpine` (musl) e `manylinux_2_28` (glibc).
- Gates: `popcnt == 0` e `_multiarray_umath*.so` abaixo de 8 000 000 bytes; o wheel do scipy não pode embutir `libscipy_openblas`.
- O manifesto usa faixas (`>=`); a execução usou uma **cópia local com pins exatos** (`==`) tirados do `requirements.txt`. O repositório do produto não foi alterado.

## Resultado até agora

| Célula | Resultado |
| --- | --- |
| musl, Python 3.12 (canário) | OK: numpy 2.5.4 (`_multiarray_umath` com 5 310 041 B e `popcnt=0`), scipy 1.18.1 sem `libscipy_openblas`, scikit-learn 1.9.1, pandas 3.1.1; import offline OK |
| glibc 3.12, musl 3.13, glibc 3.13, musl 3.14, glibc 3.14 | Enfileiradas, uma de cada vez |

## O que travou ou ficou de fora

- **Podman rootless com `userns = keep-id`:** o container roda com o uid do host e o `apk add` falha com "Unable to open log: Permission denied". Contorno só para este build: `CONTAINERS_CONF` apontando para um arquivo vazio. Nenhuma configuração global foi alterada.
- **scikit-learn `cp314t` musllinux:** o upstream não publica esse wheel (só manylinux) e a receita automática não cobre o interpretador free-threaded. Fica pendente.
- **`cp314t` de numpy, scipy e pandas:** re-hospedagem dos wheels do upstream (decisão já registrada: sem rebuild x86-64-v1 para free-threaded).
- **O que o gate prova:** `popcnt=0` num host com AVX prova que a flag de build foi aplicada, **não** a execução em CPU sem AVX. A prova de execução é rodar `pip install` e `import` numa máquina sem AVX.
- **A Release nova precisa ser completa**, não só o delta: o `apply_wheelhouse_v1.sh` do produto resolve tudo de uma única tag. Os assets inalterados da Release antiga (SQL extras, `boar_fast_filter`, etc.) entram conferidos contra o `SHA256SUMS` dela.

## Próximos passos

1. Terminar as células restantes e montar o staging com `SHA256SUMS` e `README`.
2. O operador publica o upload da Release.
3. Regenerar `simple/` com `scripts/build-wheelhouse-index.py --tags …` (sem apagar os índices Haiku e da tag antiga) e atualizar o inventário.
4. No produto, apontar o `WHEELHOUSE_TAG` padrão para a tag nova (cabe ao executor).
