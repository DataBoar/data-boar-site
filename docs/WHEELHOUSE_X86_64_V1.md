# Wheelhouse `x86-64-v1` — release inventory (en_US / pt_BR)

Canonical tag: **`wheelhouse-x86-64-v1-2026-07-29`**
Release: <https://github.com/DataBoar/data-boar-site/releases/tag/wheelhouse-x86-64-v1-2026-07-29>

The downloadable **`README.md`** on that release is bilingual and is the user-facing install
guide. This page keeps the **in-repo** inventory aligned with what the tag actually contains.

---

## English (en_US)

**58** `.whl` assets + `SHA256SUMS` + `README.md`.

### Free-threaded SQL extras (`cp314t`) — `-nogil` image rebuild only (2026-08-18)

Four additional wheels. **PyPI publishes no free-threaded wheels** for these drivers. They exist
so the Data Boar **`-nogil` Docker image** can install SQL extras without compiling from sdist on
every rebuild. They are **not** a general-user install path.

| package | version | platform tag |
| --- | --- | --- |
| mariadb | 1.1.14 | `cp314-cp314t-linux_x86_64` |
| oracledb | 4.0.2 | `cp314-cp314t-linux_x86_64` |
| psycopg2-binary | 2.9.12 | `cp314-cp314t-linux_x86_64` |
| pymssql | 2.3.13 | `cp314-cp314t-linux_x86_64` |

The tag is **`linux_x86_64`** (compiled inside the nogil builder), not `manylinux` / `musllinux`.

**Rebuild system packages** (Debian/Ubuntu-class builder), if you must compile again:

- **`freetds-dev`** — `pymssql` needs `sqlfront.h`
- **`libkrb5-dev`** — `pymssql` links `-lkrb5`

PEP 503 stubs: `simple/mariadb/`, `simple/oracledb/`, `simple/psycopg2-binary/`, `simple/pymssql/`.

---

## Português (Brasil)

**58** arquivos `.whl` + `SHA256SUMS` + `README.md`.

### Extras SQL free-threaded (`cp314t`) — só o rebuild da imagem `-nogil` (2026-08-18)

Quatro wheels a mais. **A PyPI não publica wheel free-threaded** para esses drivers. Eles existem
para a imagem Docker **`-nogil`** do Data Boar instalar os extras SQL sem compilar do sdist a cada
rebuild. **Não** são caminho de instalação geral do usuário.

| pacote | versão | tag de plataforma |
| --- | --- | --- |
| mariadb | 1.1.14 | `cp314-cp314t-linux_x86_64` |
| oracledb | 4.0.2 | `cp314-cp314t-linux_x86_64` |
| psycopg2-binary | 2.9.12 | `cp314-cp314t-linux_x86_64` |
| pymssql | 2.3.13 | `cp314-cp314t-linux_x86_64` |

A tag é **`linux_x86_64`** (compilado dentro do builder nogil), não `manylinux` / `musllinux`.

**Pacotes de sistema para rebuild** (builder classe Debian/Ubuntu), se precisar compilar de novo:

- **`freetds-dev`** — o `pymssql` precisa de `sqlfront.h`
- **`libkrb5-dev`** — o `pymssql` liga `-lkrb5`

Stubs PEP 503: `simple/mariadb/`, `simple/oracledb/`, `simple/psycopg2-binary/`, `simple/pymssql/`.
