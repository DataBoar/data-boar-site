# Lab wheelhouses — Haiku, FreeBSD, NetBSD, OpenBSD (en_US / pt_BR)

Sister inventory of [`WHEELHOUSE_X86_64_V1.md`](WHEELHOUSE_X86_64_V1.md). The code is the source of
truth: `scripts/build-wheelhouse-index.py` generates `simple/` from the Release assets, and this
page states only what those Releases contain. Checked on **2026-11-13** (issue #104).

**Posture:** these are **lab wheelhouses**: wheels compiled in a VM per OS, with a published
`SHA256SUMS`. They are **not a supported channel**. The recipe was validated in the lab (VM); no
claim about other hosts, other patch levels or production is made here.

---

## English (en_US)

| OS | Release tag | Wheels | Python | Platform tag |
| --- | --- | :-: | --- | --- |
| Haiku R1/beta6 | `wheelhouse-haiku-2026-11-04` | 23 | 3.14 | `haiku_r1~beta6_x86_64` |
| FreeBSD 15.1 | `wheelhouse-freebsd-2026-11-04` | 3 | 3.12 | `freebsd_15_1_release_p6_amd64` |
| NetBSD 11.1 | `wheelhouse-netbsd-2026-11-05` | 20 | 3.12 | `netbsd_11_1_amd64` |
| OpenBSD 8.0 | `wheelhouse-openbsd-2026-11-05` | 20 | 3.14 | `openbsd_8_0_amd64` |
| illumos / OmniOS | — | 0 | — | no wheel was kept (`pip` discarded the builds) |

Every Release holds the `.whl` files and a `SHA256SUMS`. All 66 wheels were checked with
`sha256sum -c` locally and their GitHub digests match; the `#sha256=` in `simple/` equals that sum.

Contents (name version):

- **Haiku:** cbor2 6.1.5, cffi 2.1.1, contourpy 1.4.0, cryptography 50.0.2, greenlet 3.5.6,
  hypothesis 6.170.9, kiwisolver 1.5.1, librt 0.16.0, lxml 6.1.3, markupsafe 3.0.4, matplotlib
  3.11.2, maturin 1.15.0, odfpy 1.4.1, pandas 3.1.0, pillow 13.0.0, pydantic_core 2.50.1, pyyaml
  6.0.3, rapidfuzz 3.14.6, red_black_tree_mod 1.22, regex 2026.9.29, rpds_py 0.30.0, scikit_learn
  1.9.1, scipy 1.18.1.
- **FreeBSD:** boar_fast_filter 0.1.0, numpy 2.5.4, pandas 3.1.1.
- **NetBSD:** backports_zstd 1.8.0, cbor2 6.2.0.post2, cffi 2.1.1, greenlet 3.5.6, inflate64
  1.0.4, markupsafe 3.0.4, maturin 1.16.0, ninja 1.13.2, numpy 2.5.4, odfpy 1.4.1, psutil 7.2.2,
  pybcj 1.0.8, pycryptodomex 3.24.1, pymongo 4.19.0, pyppmd 1.3.1, pyyaml 6.0.3,
  red_black_tree_mod 1.22, regex 2026.9.29, rpds_py 2026.9.1, scikit_learn 1.9.1.
- **OpenBSD:** cbor2 6.2.0.post2, cffi 2.1.1, contourpy 1.4.0, cryptography 50.0.2, greenlet
  3.5.6, inflate64 1.0.4, kiwisolver 1.5.1, maturin 1.16.0, odfpy 1.4.1, psutil 7.2.2, pybcj
  1.0.8, pycryptodomex 3.24.1, pydantic_core 2.50.2, pymongo 4.19.0, pyppmd 1.3.1, pyyaml 6.0.3,
  red_black_tree_mod 1.22, regex 2026.9.29, rpds_py 2026.9.1, scikit_learn 1.9.1.

### Install

`simple/` is **exclusive**: use `--index-url`, never `--extra-index-url` (that merges PyPI and
opens dependency confusion, #69). Pip must report the platform tag above (FreeBSD: exactly
15.1-RELEASE-p6).

```
pip install --index-url https://databoar.com.br/simple/ --only-binary=:all: numpy   # FreeBSD, NetBSD
pip install --index-url https://databoar.com.br/simple/ --only-binary=:all: pymongo # OpenBSD
```

**Haiku does not resolve through the index** (see limits). Download, restore the `~`, verify, then
install from the folder:

```
B=https://github.com/DataBoar/data-boar-site/releases/download/wheelhouse-haiku-2026-11-04
mkdir wheelhouse-haiku && cd wheelhouse-haiku && curl -fsSLO $B/SHA256SUMS
for f in $(sed 's/^[0-9a-f]*  *\*\{0,1\}//; s/~/./' SHA256SUMS); do
  curl -fsSLO "$B/$f"; n=$(printf %s "$f" | sed 's/haiku_r1\.beta6/haiku_r1~beta6/')
  [ "$f" = "$n" ] || mv "$f" "$n"
done
sha256sum -c SHA256SUMS
pip install --no-index --find-links . scikit-learn
```

### What was tested (2026-11-13, pip 25.1.1 on Linux, not on the BSD/Haiku hosts)

Resolution against a local copy of the regenerated `simple/`, with `pip download --platform …`:
FreeBSD `numpy` and `pandas` (dependencies close: 4 wheels), NetBSD `numpy`, OpenBSD `pymongo`
(2 wheels) resolve and download from the Release URLs. Haiku through the index: no match (below);
the download-rename-verify route above ran in full (23 wheels, `sha256sum -c` clean, `scikit-learn`
resolved with the Haiku tag). Installing on the real VMs was **not** repeated in this task.

### Limits (stated, not hidden)

- **Haiku tag mangling.** GitHub rewrites `~` to `.` in asset names, so `haiku_r1~beta6_x86_64`
  is stored as `haiku_r1.beta6_x86_64`, and pip reads that as two tags (`haiku_r1`, `beta6_x86_64`).
  `pip` on Haiku asks for `haiku_r1~beta6_x86_64`, so the index links never match. `SHA256SUMS`
  keeps the original names. Re-uploading does not help; hosting the files elsewhere is an open
  decision (cost: ~71 MB).
- **FreeBSD is pinned to the patch level** (`p6` is in the tag). After `freebsd-update` to another
  patch level, pip will not select these wheels.
- **The sets are partial.** `simple/` serves wheels for the platform tag; whatever is missing for
  a package (for example `scipy` on NetBSD/OpenBSD, `numpy` on OpenBSD) does not resolve. On
  NetBSD and OpenBSD, `scikit-learn` fails index-only for that reason.
- **OpenBSD `cryptography` is not portable** (lab runbook).
- **NetBSD wheels may link libraries of the build host.**
- **Pure-Python wheels** (`odfpy`, `red_black_tree_mod`) exist in several Releases with the same
  file name and different digests (non-reproducible builds). The builder keeps the first tag
  passed (Haiku) and warns about the others.

### Pending

- **illumos / OmniOS:** no wheel kept; nothing to publish until the cell is rebuilt.
- **`x86-64-v1` refresh:** wheels lost when the build host rebooted (11/Nov 17:03, `/tmp` is
  tmpfs); recompile tracked in DataBoar/data-boar#2218; separate PR. See
  [`ops/WHEELHOUSE_REFRESH_2026-11.md`](ops/WHEELHOUSE_REFRESH_2026-11.md).
- **scikit-learn `cp314t` musllinux:** upstream publishes no such wheel and the automatic recipe
  does not cover the free-threaded interpreter.
- **Haiku wheels stay on the GitHub Release** (operator decision, 2026-11-13): no wheel is hosted
  on Pages, so the manual download-rename-verify step above stays. The Release
  `wheelhouse-haiko-2026-11-04` (typo in the tag) was removed on 2026-11-13, after the live index
  pointed only to `wheelhouse-haiku-2026-11-04` and its 23 links returned 200 with matching hashes.

---

## Português (Brasil)

**Postura:** são **wheelhouses de laboratório**: wheels compilados numa VM por SO, com
`SHA256SUMS` publicado. **Não** são canal suportado. A receita foi validada em laboratório (VM);
aqui não se afirma nada sobre outros hosts, outros níveis de patch ou produção. O código é a fonte
da verdade: `scripts/build-wheelhouse-index.py` gera o `simple/` a partir dos assets das Releases,
e esta página diz só o que essas Releases contêm. Conferido em **13/nov/2026** (issue #104).

| SO | Tag da Release | Wheels | Python | Tag de plataforma |
| --- | --- | :-: | --- | --- |
| Haiku R1/beta6 | `wheelhouse-haiku-2026-11-04` | 23 | 3.14 | `haiku_r1~beta6_x86_64` |
| FreeBSD 15.1 | `wheelhouse-freebsd-2026-11-04` | 3 | 3.12 | `freebsd_15_1_release_p6_amd64` |
| NetBSD 11.1 | `wheelhouse-netbsd-2026-11-05` | 20 | 3.12 | `netbsd_11_1_amd64` |
| OpenBSD 8.0 | `wheelhouse-openbsd-2026-11-05` | 20 | 3.14 | `openbsd_8_0_amd64` |
| illumos / OmniOS | — | 0 | — | nenhum wheel foi guardado (o `pip` descartou os builds) |

Cada Release tem os `.whl` e um `SHA256SUMS`. Os 66 wheels foram conferidos com `sha256sum -c`
localmente e o digest do GitHub bate; o `#sha256=` do `simple/` é igual a essa soma. A lista de
pacotes e versões de cada SO está na seção em inglês acima (mesmos nomes).

### Instalação

O `simple/` é **exclusivo**: use `--index-url`, nunca `--extra-index-url` (esta mistura a PyPI e
abre confusão de dependências, #69). O pip precisa informar a tag de plataforma acima (FreeBSD:
exatamente 15.1-RELEASE-p6).

```
pip install --index-url https://databoar.com.br/simple/ --only-binary=:all: numpy   # FreeBSD, NetBSD
pip install --index-url https://databoar.com.br/simple/ --only-binary=:all: pymongo # OpenBSD
```

**No Haiku o índice não resolve** (veja os limites). Baixe, devolva o `~`, confira e instale da
pasta, com o mesmo bloco de comandos da seção em inglês (`SHA256SUMS`, laço de `curl`/`mv`,
`sha256sum -c`, `pip install --no-index --find-links .`).

### O que foi testado (13/nov/2026, pip 25.1.1 no Linux, não nos hosts BSD/Haiku)

Resolução contra uma cópia local do `simple/` regenerado, com `pip download --platform …`:
`numpy` e `pandas` no FreeBSD (as dependências fecham: 4 wheels), `numpy` no NetBSD e `pymongo` no
OpenBSD (2 wheels) resolvem e baixam das URLs das Releases. Haiku pelo índice: sem correspondência
(abaixo); o caminho baixar-renomear-conferir rodou inteiro (23 wheels, `sha256sum -c` limpo,
`scikit-learn` resolvido com a tag do Haiku). A instalação nas VMs reais **não** foi repetida
nesta tarefa.

### Limites (ditos, não escondidos)

- **A tag do Haiku é alterada pelo GitHub.** O GitHub troca `~` por `.` no nome do asset
  (`haiku_r1~beta6_x86_64` vira `haiku_r1.beta6_x86_64`) e o pip lê isso como duas tags. O `pip`
  do Haiku pede `haiku_r1~beta6_x86_64`, então os links do índice nunca casam. O `SHA256SUMS`
  mantém os nomes originais. Subir de novo não resolve; hospedar os arquivos em outro lugar é
  decisão em aberto (custo: ~71 MB).
- **FreeBSD fica preso ao patch** (`p6` está na tag). Depois de um `freebsd-update` para outro
  patch, o pip não escolhe estes wheels.
- **Os conjuntos são parciais.** O `simple/` serve os wheels da tag de plataforma; o que falta
  (por exemplo `scipy` no NetBSD/OpenBSD, `numpy` no OpenBSD) não resolve. No NetBSD e no OpenBSD,
  o `scikit-learn` falha só pelo índice por esse motivo.
- **`cryptography` do OpenBSD não é portável** (runbook do laboratório).
- **Wheels do NetBSD podem ligar bibliotecas do host de build.**
- **Wheels puro-Python** (`odfpy`, `red_black_tree_mod`) estão em várias Releases com o mesmo nome
  e digests diferentes (builds não reprodutíveis). O gerador fica com a primeira tag passada
  (Haiku) e avisa das demais.

### Pendências

- **illumos / OmniOS:** nenhum wheel guardado; nada a publicar até a célula ser refeita.
- **Refresh do `x86-64-v1`:** wheels perdidos quando o host de build reiniciou (11/nov, 17:03; o
  `/tmp` é tmpfs); recompilação em DataBoar/data-boar#2218; PR separada. Veja
  [`ops/WHEELHOUSE_REFRESH_2026-11.md`](ops/WHEELHOUSE_REFRESH_2026-11.md).
- **scikit-learn `cp314t` musllinux:** o upstream não publica esse wheel e a receita automática
  não cobre o interpretador free-threaded.
- **Os wheels do Haiku ficam na Release do GitHub** (decisão do operador, 13/nov/2026): nenhum
  wheel é hospedado no Pages, então o passo manual de baixar, renomear e conferir o hash segue
  valendo. A Release `wheelhouse-haiko-2026-11-04` (typo na tag) foi removida em 13/nov/2026,
  depois de o índice no ar apontar só para `wheelhouse-haiku-2026-11-04` e os 23 links
  responderem 200 com os hashes conferidos.
