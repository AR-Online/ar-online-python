# AR Online SDK para Python

[![CI](https://github.com/AR-Online/ar-online-python/actions/workflows/ci.yml/badge.svg)](https://github.com/AR-Online/ar-online-python/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-3776ab.svg)](https://www.python.org/)
[![Licença](https://img.shields.io/badge/licen%C3%A7a-Apache--2.0-green.svg)](LICENSE)

Cliente oficial da API da AR Online para Python.

> **Status:** este SDK cobre as consultas da API /v3, que ainda não está
> publicada — o endereço `v3.ar-online.com.br` entra no ar junto com ela. O
> envio de notificações em produção é feito hoje pela API legada, que ainda não
> está neste SDK. Fale com o suporte antes de planejar uma integração em cima
> dele.

## Sobre a AR Online

A AR Online é uma plataforma brasileira de notificação eletrônica com validade
jurídica. Uma única requisição dispara a notificação em até cinco canais, e cada
etapa do percurso — envio, entrega e leitura — é registrada com carimbo do tempo
emitido por uma Autoridade de Carimbo do Tempo da ICP-Brasil. Esse registro é o
que dá à comunicação o valor de prova documental previsto na MP 2.200-2/2001, e
é o que diferencia a plataforma de um serviço comum de disparo de mensagens.

Os canais disponíveis são:

| canal | o que é |
|---|---|
| AR-Email | e-mail com comprovação de entrega e de leitura |
| AR-SMS | mensagem de texto para o celular do destinatário |
| AR-WhatsApp | notificação por WhatsApp |
| AR-Voz | chamada telefônica automatizada |
| AR-Cartas | carta física registrada, enviada pelos Correios |

Você escolhe quais canais usar em cada envio. O processamento é assíncrono: a
API confirma o recebimento na hora e devolve um identificador, que você usa
depois para consultar o status de cada canal e baixar os comprovantes.

| | |
|---|---|
| Site | <https://www.ar-online.com.br> |
| Documentação da API | <https://docs.ar-online.com.br> |
| Suporte | <suporte@ar-online.com.br> · +55 (11) 4200-7766 |

## Requisitos

- Python 3.10 ou mais novo
- Nenhuma dependência de produção: o SDK usa apenas a biblioteca padrão

## Instalação

```bash
pip install aronline-sdk
```

## Autenticação

### Token da API /v3

Solicite em <suporte@ar-online.com.br>. O token fica preso a uma entidade da sua
conta, e é ela que define quais dados ele enxerga — se você precisa consultar
mais de uma, peça um token para cada. O padrão é somente leitura.

O token tem prazo de validade. Token ausente, expirado ou revogado responde
`401`; se um token vazar, peça a revogação e ele deixa de ser aceito na chamada
seguinte.

Quando a /v3 for publicada, a emissão passa a ser por conta própria, na tela
*Gerar Token* da documentação, com o mesmo usuário e senha do portal.

## Primeiros passos

```python
import os

from aronline import Client

client = Client(token=os.environ["AR_TOKEN"])

for template in client.templates.list(channel="whatsapp"):
    print(template["name"], len(template["variables"]))
```

## Referência

Este SDK cobre hoje as consultas da API /v3.

| método | o que faz | precisa de token |
|---|---|---|
| `templates.list(channel=…)` | lista os modelos, com filtro por canal | sim |
| `templates.get(id)` | busca um modelo pelo UUID | sim |
| `tags.list()` · `tags.get(id)` | suas etiquetas | sim |
| `allowlist.list()` | seus destinatários permitidos | sim |
| `freshness.get()` | o atraso da carga de dados | sim |
| `version.get()` | qual versão da API está no ar | não |

### Modelos

```python
todos = client.templates.list()
do_whatsapp = client.templates.list(channel="whatsapp")
um = client.templates.get("9b2f-uuid")
```

O filtro `channel` aceita `email`, `sms`, `whatsapp`, `voice` e `letter`. A
constante `aronline.CHANNELS` traz a mesma lista em tempo de execução, e o tipo
é `Literal`, então o verificador estático recusa um valor fora da lista.

### Etiquetas e lista de permitidos

```python
etiquetas = client.tags.list()
uma = client.tags.get("12")
permitidos = client.allowlist.list()
```

São recursos **pessoais**: respondem o que pertence a quem está no token. Um
token de integração, que não representa uma pessoa, recebe `403` nessas rotas.

### Atraso da carga

```python
frescor = client.freshness.get()

if frescor["sources_behind"] > 0:
    print(frescor["sources_behind"], "de", frescor["sources_tracked"], "atrasadas")
```

Serve para responder uma pergunta prática: quando uma consulta devolve menos do
que você esperava, o problema é a API ou a carga de dados está atrasada?

### Versão

```python
versao = client.version.get()
print(versao["version"], versao["environment"])
```

É a única chamada que funciona sem token, útil para conferir a instalação antes
de ter uma credencial.

## Envio de notificações

O envio, a consulta de status por canal e os comprovantes estão na API legada do
gateway, que **ainda não está neste SDK** — hoje ela está disponível no
[SDK TypeScript](https://github.com/AR-Online/ar-online-typescript) e chega aqui
nas próximas versões.

Enquanto isso, o contrato HTTP está documentado em
<https://docs.ar-online.com.br>, e a credencial do gateway é emitida pelo
suporte.

## Tratamento de erros

Chamada que não levantou exceção deu certo. Você não precisa ler status HTTP nem
procurar campo de erro no corpo da resposta.

```python
from aronline import ApiError

try:
    client.templates.get("nao-existe")
except ApiError as error:
    print(error.code)  # 'not_found'
    print(error.status)  # 404
    print(error.request_id)  # informe este número ao abrir um chamado
```

| atributo | conteúdo |
|---|---|
| `status` | o status HTTP (`0` quando a API não foi alcançada) |
| `code` | o código do catálogo: `not_found`, `forbidden`, `rate_limited`, … |
| `message` | a mensagem da API, em português |
| `request_id` | identifica a chamada nos nossos registros |
| `field` | o campo recusado, quando a recusa é sobre um campo |
| `details` | uma entrada por campo, em erro de validação |
| `retry_after_seconds` | quantos segundos esperar, em `429` e `503` |
| `retryable` | `True` em `429` e `503` |

Erro de rede e resposta que não é JSON também chegam como `ApiError`: você trata
um `except`, não três.

O SDK não repete chamadas automaticamente, porque só quem chamou sabe se a
operação pode acontecer duas vezes. Quando quiser repetir:

```python
import time

try:
    client.tags.list()
except ApiError as error:
    if error.retryable:
        time.sleep(error.retry_after_seconds or 5)
```

## Configuração do cliente

```python
Client(
    token="…",  # opcional: sem ele, só version funciona
    base_url="https://v3.ar-online.com.br",  # padrão
    timeout=30.0,  # padrão, em segundos
)
```

As funções devolvem `TypedDict`, não dataclass, com os campos **como a API os
escreve** (`provider_identifier`, `created_at`). Não há camada de conversão de
nomes, para que o que você lê no SDK seja o mesmo que você vê na documentação da
API e nos nossos registros de suporte. Campo novo na API continua passando, em
vez de estourar aqui.

## Desenvolvimento

```bash
uv sync
```

| comando | o que cobra |
|---|---|
| `uv run ruff check .` | lint |
| `uv run ruff format --check .` | formato |
| `uv run mypy` | `mypy --strict` sobre `src/` e `tests/` |
| `uv run codespell` | ortografia |
| `uv run pytest` | testes, reprovando abaixo de 95% de linhas |
| `uv run pip-audit --skip-editable` | vulnerabilidade conhecida em dependência |

| métrica | valor |
|---|---|
| Testes | 38 |
| Cobertura | 100% |
| Dependências de produção | 0 |
| Vulnerabilidades conhecidas | 0 |

O `pip-audit` roda dentro do venv do projeto: solto, ele auditaria o ambiente da
máquina e reclamaria de pacotes que não são deste projeto.

Os testes sobem um `http.server` real em uma porta livre, numa thread, e falam
com ele por `urllib`. O que o SDK precisa acertar é o comportamento na rede:
qual rota embrulha a resposta, como a recusa volta e o que acontece quando algo
que não é a API responde.

Para publicar uma versão, veja [PUBLICANDO.md](PUBLICANDO.md).

## Suporte

- Dúvidas de integração e emissão de credenciais: <suporte@ar-online.com.br>
- Telefone: +55 (11) 4200-7766
- Defeitos neste SDK: [issues do repositório](https://github.com/AR-Online/ar-online-python/issues)

Ao abrir um chamado sobre uma chamada que falhou, informe o `request_id` do erro:
é com ele que localizamos a requisição nos nossos registros.

## Licença

Apache License 2.0 — veja [LICENSE](LICENSE).

© 2026 AR ONLINE TECNOLOGIA LTDA.
