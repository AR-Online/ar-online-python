# Publicando no PyPI

O workflow [`release.yml`](.github/workflows/release.yml) publica por
**Trusted Publishing**: não existe token de API guardado no repositório. O PyPI
confia na identidade do runner do GitHub (OIDC), e essa confiança é declarada
uma vez, do lado do PyPI.

## O que configurar no PyPI (uma vez)

O `aronline-sdk` ainda não existe no PyPI, e isso é uma vantagem aqui: o PyPI
aceita **publisher pendente**, então dá para declarar a confiança ANTES da
primeira publicação — e a primeira já sai sem token nenhum.

Em <https://pypi.org/manage/account/publishing/>, em *Add a new pending
publisher*:

| campo | valor |
|---|---|
| PyPI Project Name | `aronline-sdk` |
| Owner | `AR-Online` |
| Repository name | `ar-online-python` |
| Workflow name | `release.yml` |
| Environment name | `pypi` |

O **Environment name** não é enfeite: é ele que impede qualquer outro workflow
do repositório de publicar. O `release.yml` declara `environment: pypi`, e as
duas pontas têm de dizer o mesmo nome.

## O que configurar no GitHub (uma vez)

Em *Settings → Environments*, crie o ambiente **`pypi`**. Ele pode ficar vazio
— não precisa de segredo, porque não há segredo. O que vale a pena ligar ali:

- **Deployment branches and tags**: restrinja a `v*`, para que só uma tag
  publique;
- **Required reviewers**: se quiser que a publicação espere aprovação humana.

## Como publicar

```bash
# 1. a versão no pyproject.toml
# 2. a tag com o MESMO número, prefixada com v
git tag v0.1.0
git push origin v0.1.0
```

O workflow roda o portão inteiro (lint, formato, mypy, testes, auditoria),
constrói o pacote, **confere que a versão do wheel é a da tag** e publica.

Tag e `pyproject.toml` divergentes reprovam antes de publicar. É de propósito:
versão publicada no PyPI **não se apaga**, e um registro que mente sobre qual
código é qual versão é um problema que não se desfaz.
