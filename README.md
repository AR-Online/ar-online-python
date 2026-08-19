# AR Online — SDK Python

Cliente oficial da API do AR Online para Python.

Você não monta URL, não escreve cabeçalho, não desembrulha envelope e não lê
status para saber se deu certo. Chama função, recebe objeto tipado, e a falha
chega como exceção.

## Instalação

```bash
pip install aronline-sdk
```

Python 3.10 ou mais novo. Tipado (`py.typed`), **zero dependência** — usa só a
biblioteca padrão, então nunca briga com o que a sua aplicação já fixou.

## Começando

```python
import os

from aronline import Client

client = Client(token=os.environ["AR_TOKEN"])

for template in client.templates.list(channel="whatsapp"):
    print(template["name"], len(template["variables"]))
```

O token é emitido pelo AR Online. Se você ainda não tem o seu, fale com o
suporte — a API só verifica token, ela não emite.

## O que dá para fazer

### Modelos

```python
todos = client.templates.list()
do_whatsapp = client.templates.list(channel="whatsapp")
um = client.templates.get("9b2f-uuid")
```

`channel` aceita `email`, `sms`, `whatsapp`, `voice` e `letter` — é um
`Literal`, então o mypy recusa qualquer outro valor antes de virar uma chamada
perdida. Em tempo de execução, `aronline.CHANNELS` tem a mesma lista.

### Etiquetas

```python
etiquetas = client.tags.list()
uma = client.tags.get("12")
```

Etiqueta é **pessoal**: essas funções respondem às etiquetas de quem está no
token. Token de integração recebe `403` dizendo isso, em vez de uma lista
vazia — que leria como "você não tem nenhuma".

### Lista de permitidos

```python
permitidos = client.allowlist.list()
```

Também pessoal, pelo mesmo motivo.

### Frescor dos dados

```python
frescor = client.freshness.get()

if frescor["worst_lag_seconds"] is not None and frescor["worst_lag_seconds"] > 900:
    print("a carga está atrasada", frescor["behind"])
```

Responde a pergunta prática de quando uma consulta devolve menos do que você
esperava: o defeito é da API, ou a carga está atrasada? Sem esse número as
duas hipóteses parecem a mesma coisa.

### Versão

```python
versao = client.version.get()
print(versao["version"], versao["environment"])
```

A única função que funciona **sem token** — é rota aberta. É o primeiro dado
que o suporte pede.

## Quando dá errado

Toda recusa da API vira `ApiError`. Chamada que não levantou, deu certo.

```python
from aronline import ApiError

try:
    client.templates.get("nao-existe")
except ApiError as error:
    print(error.code)        # 'not_found'
    print(error.status)      # 404
    print(error.request_id)  # o número que o suporte pede
```

O que vem em `ApiError`:

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

Repetir a chamada é decisão sua — o SDK não repete sozinho:

```python
import time

except ApiError as error:
    if error.retryable:
        time.sleep(error.retry_after_seconds or 5)
```

Duas coisas que **não** viram exceção estranha: rede fora do ar e resposta que
não é JSON (um proxy respondendo no lugar da API) também chegam como
`ApiError`, com `code` `unreachable` e `invalid_response`. Você tem um tipo só
para tratar — nada de `URLError` ou `JSONDecodeError` vazando.

## Configuração

```python
Client(
    token="…",                             # opcional: sem ele, só version funciona
    base_url="https://v3.ar-online.com.br",  # padrão; troque para homologação
    timeout=30.0,                          # padrão, em segundos
)
```

## Sobre o formato dos objetos

As funções devolvem `dict` tipado (`TypedDict`), não dataclass, e com os campos
**como a API os nomeia** — `provider_identifier`, `created_at`,
`worst_lag_seconds`. Duas razões: não existe camada de conversão que possa
divergir do servidor sem ninguém perceber, e campo novo na API continua
passando em vez de estourar aqui. Só o `ApiError` foge disso, porque é objeto
que o SDK constrói, não que ele repassa.

## Escopo

Este SDK fala **só a `/v3`**. As rotas `/v1` e `/v2` continuam de pé, mas elas
respondem byte a byte o que as APIs antigas respondiam, idiossincrasias
incluídas — inclusive erro com status `200`. São espelhos para ninguém
precisar migrar no mesmo dia, e um cliente tipado que as "melhorasse"
quebraria exatamente quem elas protegem.

A superfície `/v3` é só de leitura hoje. Escrita entra nos cinco SDKs na mesma
leva em que entrar na API.

Quem precisa do contrato HTTP cru — porque está escrevendo um cliente em outra
linguagem, ou depurando o que passou no fio — encontra em
[docs.ar-online.com.br](https://docs.ar-online.com.br).

## Desenvolvimento

```bash
uv sync
uv run ruff check . && uv run ruff format --check .
uv run mypy
uv run pytest
```

## Licença

[Apache 2.0](LICENSE) — © 2026 AR ONLINE TECNOLOGIA LTDA.
