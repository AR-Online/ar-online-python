# AR Online — SDK Python

[![CI](https://github.com/AR-Online/ar-online-python/actions/workflows/ci.yml/badge.svg)](https://github.com/AR-Online/ar-online-python/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-3776ab.svg)](https://www.python.org/)
[![Tipado](https://img.shields.io/badge/tipado-mypy%20strict-blue.svg)](#-desenvolvimento)
[![Cobertura](https://img.shields.io/badge/cobertura-100%25-success.svg)](#-desenvolvimento)
[![Dependências](https://img.shields.io/badge/depend%C3%AAncias-0-success.svg)](#-o-que-ele-resolve)
[![Licença](https://img.shields.io/badge/licen%C3%A7a-Apache--2.0-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-n%C3%A3o%20publicado-orange.svg)](#-escopo)

Cliente oficial da API do AR Online para Python. Você não monta URL, não escreve cabeçalho, não desembrulha envelope e não lê status para saber se deu certo: chama função, recebe objeto tipado, e a falha chega como exceção.

## ✨ O que ele resolve

- **O envelope não é uniforme** — `templates`, `tags` e `allowlist` respondem `{"data": …}`; `freshness` e `version` respondem o objeto direto. Desembrulhar tudo, ou nada, quebra metade das chamadas. O SDK sabe por rota.
- **Uma exceção só** — recusa do catálogo, proxy respondendo HTML e rede fora do ar chegam todas como `ApiError`. Nada de `URLError` ou `JSONDecodeError` vazando para o seu `except`.
- **`request_id` de primeira classe** — é o primeiro dado que o suporte pede. Um SDK que o engolisse obrigaria você a reproduzir a falha no `curl` para achar o número.
- **Rota aberta funciona sem token** — `version` é pública. Cliente construído sem credencial chama ela, o que serve para conferir a instalação antes de ter token.
- **Zero dependência** — só a biblioteca padrão (`urllib`). Nunca briga com o que a sua aplicação já fixou.
- **Tipado de verdade** — `py.typed`, `mypy --strict` limpo, e `channel` é `Literal`: valor fora da lista o verificador recusa antes de virar chamada perdida.

## 🚀 Começando

### Instalação

```bash
pip install aronline-sdk
```

Python 3.10 ou mais novo.

### Primeira chamada

```python
import os

from aronline import Client

client = Client(token=os.environ["AR_TOKEN"])

for template in client.templates.list(channel="whatsapp"):
    print(template["name"], len(template["variables"]))
```

O token é emitido pelo AR Online — a API só verifica, ela não emite. Se você ainda não tem o seu, fale com o suporte.

## 🧰 O que dá para fazer

| recurso | funções | precisa de token |
|---|---|---|
| Modelos | `templates.list(channel=…)` · `templates.get(id)` | sim |
| Etiquetas | `tags.list()` · `tags.get(id)` | sim |
| Lista de permitidos | `allowlist.list()` | sim |
| Frescor dos dados | `freshness.get()` | sim |
| Versão | `version.get()` | **não** |

### Modelos

```python
todos = client.templates.list()
do_whatsapp = client.templates.list(channel="whatsapp")
um = client.templates.get("9b2f-uuid")
```

`channel` aceita `email`, `sms`, `whatsapp`, `voice` e `letter`. `aronline.CHANNELS` traz a mesma lista em tempo de execução.

### Etiquetas e lista de permitidos

```python
etiquetas = client.tags.list()
uma = client.tags.get("12")
permitidos = client.allowlist.list()
```

Ambas são **pessoais**: respondem ao que pertence a quem está no token. Token de integração recebe `403` dizendo isso — e não uma lista vazia, que leria como "você não tem nenhuma".

### Frescor dos dados

```python
frescor = client.freshness.get()

if frescor["sources_behind"] > 0:
    print(frescor["sources_behind"], "de", frescor["sources_tracked"], "atrasadas")
```

Responde a pergunta prática de quando uma consulta devolve menos do que você esperava: o defeito é da API, ou a carga está atrasada? Sem esse número as duas hipóteses parecem a mesma coisa.

Ela responde em **contagens**, não em lista de tabelas: "46 acompanhadas, 3 atrasadas" responde "está fresco?"; quarenta e seis nomes de tabela é relatório que ninguém lê na hora.

### Versão

```python
versao = client.version.get()
print(versao["version"], versao["environment"])
```

A única função que funciona **sem token**. É o primeiro dado que o suporte pede.

## ⚠️ Quando dá errado

Toda recusa vira `ApiError`. Chamada que não levantou, deu certo.

```python
from aronline import ApiError

try:
    client.templates.get("nao-existe")
except ApiError as error:
    print(error.code)  # 'not_found'
    print(error.status)  # 404
    print(error.request_id)  # o número que o suporte pede
```

| atributo | o que é |
|---|---|
| `status` | o status HTTP (`0` quando a API nem foi alcançada) |
| `code` | o código do catálogo: `not_found`, `forbidden`, `rate_limited`, … |
| `message` | a mensagem da API, em pt-BR |
| `request_id` | identifica a chamada nos nossos registros — **sempre informe num chamado** |
| `field` | o campo recusado, quando a recusa é sobre um |
| `details` | uma entrada por campo, em erro de validação |
| `retry_after_seconds` | quantos segundos esperar, em `429` e `503` |
| `retryable` | `True` em `429` e `503` |

Repetir é decisão sua — o SDK não repete sozinho, porque só quem chamou sabe se a operação pode acontecer duas vezes:

```python
import time

try:
    client.tags.list()
except ApiError as error:
    if error.retryable:
        time.sleep(error.retry_after_seconds or 5)
```

## ⚙️ Configuração

```python
Client(
    token="…",  # opcional: sem ele, só version funciona
    base_url="https://v3.ar-online.com.br",  # padrão; troque para homologação
    timeout=30.0,  # padrão, em segundos
)
```

**Sobre o formato dos objetos:** as funções devolvem `dict` tipado (`TypedDict`), não dataclass, com os campos **como a API os escreve** — `provider_identifier`, `created_at`, `worst_lag_seconds`. Duas razões: não existe camada de conversão que possa divergir do servidor sem ninguém perceber, e campo novo na API continua passando em vez de estourar aqui. Só o `ApiError` foge disso, porque é objeto que o SDK constrói.

## 🎯 Escopo

Este SDK fala **só a `/v3`**. As rotas `/v1` e `/v2` continuam de pé, mas respondem byte a byte o que as APIs antigas respondiam, idiossincrasias incluídas — inclusive erro com status `200`. São espelhos para ninguém precisar migrar no mesmo dia, e um cliente tipado que as "melhorasse" quebraria exatamente quem elas protegem.

A superfície `/v3` é **só de leitura** hoje. Escrita entra nos cinco SDKs na mesma leva em que entrar na API.

## 🧪 Desenvolvimento

```bash
uv sync
```

O portão, peça por peça:

| comando | o que cobra |
|---|---|
| `uv run ruff check .` | lint |
| `uv run ruff format --check .` | formato |
| `uv run mypy` | `mypy --strict` sobre `src/` **e** `tests/` |
| `uv run codespell` | ortografia |
| `uv run pytest` | testes — reprova abaixo de **95%** de linhas |
| `uv run pip-audit --skip-editable` | vulnerabilidade conhecida em dependência |

| métrica | valor |
|---|---|
| Testes | 38 |
| Cobertura | 100% |
| Dependências de produção | 0 |
| Vulnerabilidades conhecidas | 0 |

O `pip-audit` roda **dentro do venv do projeto**, e não solto: solto, ele audita o ambiente da máquina e reclama de pacote que não é nosso.

Os testes sobem um `http.server` **de verdade numa porta livre**, numa thread, e falam com ele por `urllib`. Não há dublê: o que este SDK precisa acertar é justamente o fio — qual rota embrulha a resposta, como a recusa volta, o que acontece quando algo que não é a API responde.

## 📚 Documentação

- [CHANGELOG](CHANGELOG.md) — o que mudou em cada versão
- [Documentação da API](https://docs.ar-online.com.br) — o contrato HTTP cru
- [Os SDKs oficiais](https://docs.ar-online.com.br) — os cinco, lado a lado
- `https://v3.ar-online.com.br/docs/openapi.json` — sempre a lista completa do que está no ar

## 📄 Licença

Apache License 2.0 — veja [LICENSE](LICENSE). © 2026 AR ONLINE TECNOLOGIA LTDA.
