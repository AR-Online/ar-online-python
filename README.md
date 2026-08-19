# AR Online SDK para Python

[![CI](https://github.com/AR-Online/ar-online-python/actions/workflows/ci.yml/badge.svg)](https://github.com/AR-Online/ar-online-python/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-3776ab.svg)](https://www.python.org/)
[![Licença](https://img.shields.io/badge/licen%C3%A7a-Apache--2.0-green.svg)](LICENSE)

Cliente oficial da API da AR Online para Python.

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

A plataforma tem duas superfícies de API, e cada uma usa uma credencial
diferente. O SDK aceita as duas no mesmo cliente e envia cada uma no formato que
a sua superfície espera.

### Token do gateway (API legada)

É a credencial que você usa para enviar notificações e consultar status hoje.
Solicite em <suporte@ar-online.com.br>. No SDK, ela vai em `legacy_token`.

### Token da API /v3

Solicite em <suporte@ar-online.com.br>. O token fica preso a uma entidade da sua
conta, e é ela que define quais dados ele enxerga — se você precisa consultar
mais de uma, peça um token para cada. O padrão é somente leitura.

O token tem prazo de validade. Token ausente, expirado ou revogado responde
`401`; se um token vazar, peça a revogação e ele deixa de ser aceito na chamada
seguinte.

> **A /v3 ainda não está publicada.** O endereço `v3.ar-online.com.br`, que é o
> padrão do SDK para essa superfície, entra no ar junto com ela — assim como a
> emissão de token por conta própria, com o mesmo usuário e senha do portal. Até
> lá, a parte da /v3 deste SDK serve para desenvolver contra um ambiente de
> teste, e é o `client.legacy` que fala com a API em produção.

## Primeiros passos

O envio de notificações é feito hoje pela API legada, exposta no SDK em
`client.legacy`:

```python
import os

from aronline import Client

client = Client(legacy_token=os.environ["AR_GW_TOKEN"])

enviado = client.legacy.send(
    {
        "nameTo": "João da Silva",
        "to": "joao@exemplo.com",
        "subject": "Notificação de vencimento",
        "content": "<p>Prezado João, identificamos uma pendência em seu contrato.</p>",
        "sms": {"number": "11999998888"},
    }
)

print("notificação aceita:", enviado["idEmail"])
```

Guarde o `idEmail`: é com ele que você consulta o status de qualquer canal e
baixa os comprovantes.

```python
status = client.legacy.status.email(enviado["idEmail"])

print(status["description"])  # 'Processado', 'Enviado', 'Entregue', 'Lido'
```

## Referência

### Envio e acompanhamento (`client.legacy`)

| método | o que faz |
|---|---|
| `legacy.send(envio)` | envia a notificação em um ou mais canais |
| `legacy.status.email(id)` | status do AR-Email |
| `legacy.status.sms(id)` | status do AR-SMS |
| `legacy.status.whatsapp(id)` | status do AR-WhatsApp |
| `legacy.status.voz(id)` | status do AR-Voz |
| `legacy.status.carta(id)` | status do AR-Cartas, com o rastreio dos Correios |
| `legacy.status.full(id)` | dados de perícia de todos os canais numa chamada |
| `legacy.sending_proof(id)` | comprovante de envio em PDF |
| `legacy.laudo(id)` | laudo pericial em PDF |
| `legacy.finalizar_regua(id)` | encerra a régua de notificação do envio |
| `legacy.templates.list(type=…)` | lista os modelos da sua entidade |
| `legacy.templates.get(id)` | busca um modelo |
| `legacy.templates.update(id, campos)` | edita nome e compartilhamento |
| `legacy.templates.deactivate(id)` | desativa um modelo |
| `legacy.templates.set_status(id, ativo=…)` | ativa ou desativa um modelo |

Envio multicanal: cada canal é um bloco opcional no corpo.

```python
client.legacy.send(
    {
        "nameTo": "João da Silva",
        "to": "joao@exemplo.com",
        "subject": "Notificação de vencimento",
        "content": "<p>Conteúdo em HTML.</p>",
        "customID": "contrato-4471",  # sua referência, devolvida na consulta de status
        "attachments": [{"name": "contrato.pdf", "base64": "…"}],
        "sms": {
            "number": "11999998888",
            "typeSend": "1",  # '1' só se o e-mail não for entregue; '2' sempre
            "customMessage": "Você recebeu um AR-Email. Acesse: {SHORT_LINK}",
        },
        "whatsapp": {"number": "11999998888", "variables": {"template": "aviso_01"}},
        "voz": {"number": "1133334444", "template": "aviso_voz"},
        "carta": {"name": "João da Silva", "modelo": "padrao"},
    }
)
```

Comprovantes: o comprovante de envio chega em base64 dentro de um JSON e o SDK
já o decodifica; o laudo pericial chega como PDF binário.

```python
from pathlib import Path

comprovante = client.legacy.sending_proof(id_email)

if comprovante["pdf"] is not None:
    Path("comprovante.pdf").write_bytes(comprovante["pdf"])
else:
    print(comprovante["message"])  # ainda sem status de entrega

Path("laudo.pdf").write_bytes(client.legacy.laudo(id_email))
```

Os objetos de status vêm com os campos **como o gateway os escreve**
(`dateSend`, `customID`, `idEmail`), e as ausências ficam como vieram. Onde o
contrato responde `""` ou `None`, o campo existe com esse valor; onde a data que
ainda não aconteceu **some da resposta**, a chave não existe — WhatsApp, voz e
carta fazem isso. Pergunte `"dateDelivery" in status`, não
`status["dateDelivery"] is None`.

As datas do legado são `str` no formato `"18/07/2026 01:01:32"`, sem fuso. O SDK
não as converte para `datetime`: o formato não identifica um instante sem
ambiguidade, e uma conversão aqui seria um chute com cara de precisão.

### Consultas da API /v3 (`client.*`)

A /v3 é a API nova, com contrato limpo e validação estrita. Hoje ela é somente
de leitura.

| método | o que faz | precisa de token |
|---|---|---|
| `templates.list(channel=…)` | lista os modelos, com filtro por canal | sim |
| `templates.get(id)` | busca um modelo pelo UUID | sim |
| `tags.list()` · `tags.get(id)` | suas etiquetas | sim |
| `allowlist.list()` | seus destinatários permitidos | sim |
| `freshness.get()` | o atraso da carga de dados | sim |
| `version.get()` | qual versão da API está no ar | não |

#### Modelos

```python
todos = client.templates.list()
do_whatsapp = client.templates.list(channel="whatsapp")
um = client.templates.get("9b2f-uuid")
```

O filtro `channel` aceita `email`, `sms`, `whatsapp`, `voice` e `letter`. A
constante `aronline.CHANNELS` traz a mesma lista em tempo de execução, e o tipo
é `Literal`, então o verificador estático recusa um valor fora da lista.

#### Etiquetas e lista de permitidos

```python
etiquetas = client.tags.list()
uma = client.tags.get("12")
permitidos = client.allowlist.list()
```

São recursos **pessoais**: respondem o que pertence a quem está no token. Um
token de integração, que não representa uma pessoa, recebe `403` nessas rotas.

#### Atraso da carga

```python
frescor = client.freshness.get()

if frescor["sources_behind"] > 0:
    print(frescor["sources_behind"], "de", frescor["sources_tracked"], "atrasadas")
```

Serve para responder uma pergunta prática: quando uma consulta devolve menos do
que você esperava, o problema é a API ou a carga de dados está atrasada?

#### Versão

```python
versao = client.version.get()
print(versao["version"], versao["environment"])
```

É a única chamada que funciona sem token, útil para conferir a instalação antes
de ter uma credencial.

## Tratamento de erros

Chamada que não levantou exceção deu certo. Você não precisa ler status HTTP nem
procurar campo de erro no corpo da resposta.

A /v3 levanta `ApiError`:

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

A API legada levanta `LegacyApiError`, com os campos do contrato antigo:

```python
from aronline import LegacyApiError

try:
    client.legacy.templates.get("nao-existe")
except LegacyApiError as error:
    print(error.status)  # 404 — o código que vale
    print(error.http_status)  # 200 — o que o protocolo respondeu
    print(error.body)  # o corpo cru, como chegou
```

| atributo | conteúdo |
|---|---|
| `status` | o código que vale, mesmo quando o HTTP respondeu 200 |
| `http_status` | o status que veio no protocolo (`0` quando o gateway não foi alcançado) |
| `message` | a mensagem do gateway, em português |
| `body` | o corpo da resposta, exatamente como chegou |

Os dois casos que essa separação existe para resolver: a família de templates
responde **HTTP 200 até em erro**, com o código de verdade dentro do envelope
`{"data": …, "statusCode": …}`, e o SDK levanta a exceção pelo código de dentro.
Já a consulta de voz responde 200 com uma frase quando o uuid não tem registro —
isso **não** é erro, e volta como resposta normal.

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
    token="…",  # credencial da /v3
    legacy_token="…",  # credencial do gateway
    base_url="https://v3.ar-online.com.br",  # padrão
    legacy_base_url="https://api.ar-online.com.br",  # padrão
    timeout=30.0,  # padrão, em segundos, vale para as duas superfícies
)
```

Cada credencial é opcional: informe só a da superfície que você vai usar. Os
endereços podem ser trocados para apontar a um ambiente de teste, e um não mexe
no outro. O token do gateway vai **cru** no cabeçalho `authorization`, sem
`Bearer` — o oposto da /v3 —, e o SDK cuida disso; uma área nunca manda a
credencial da outra.

As funções devolvem `TypedDict`, não dataclass, com os campos **como a API os
escreve** (`provider_identifier`, `created_at`, `customID`). Não há camada de
conversão de nomes, para que o que você lê no SDK seja o mesmo que você vê na
documentação da API e nos nossos registros de suporte. Campo novo na API
continua passando, em vez de estourar aqui.

## Webhooks

Em vez de consultar o status repetidamente, você pode receber uma chamada `POST`
a cada mudança. A configuração é feita com o suporte, que cadastra o seu endpoint
e os parâmetros de autenticação. O SDK não recebe a requisição por você, mas
exporta os tipos do payload:

```python
from aronline import WebhookPayloadV1, WebhookPayloadV2
```

Veja <https://docs.ar-online.com.br/webhooks/visao-geral> para o fluxo completo,
incluindo a política de retentativas.

## As duas superfícies, e o caminho entre elas

A **API legada** é a que está em produção hoje e concentra envio, status e
comprovantes. A **/v3** é a API nova, para onde as funcionalidades estão sendo
migradas aos poucos.

Quando uma rota ganha equivalente na /v3, a função correspondente de
`client.legacy` passa a falar com a /v3 internamente, **sem mudar de
assinatura**. Na prática, você migra atualizando o pacote, não reescrevendo a sua
integração. Cada troca dessas é registrada no [CHANGELOG](CHANGELOG.md).

O equivalente de hoje: a leitura de modelos do gateway tem a `/v3`
(`client.templates`); envio, status e provas ainda não têm.

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
| Testes | 86 |
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

Ao abrir um chamado sobre uma chamada da /v3 que falhou, informe o `request_id`
do erro: é com ele que localizamos a requisição nos nossos registros. Na API
legada, o `idEmail` do envio faz esse papel.

## Licença

Apache License 2.0 — veja [LICENSE](LICENSE).

© 2026 AR ONLINE TECNOLOGIA LTDA.
