# Changelog

Todas as mudanças notáveis deste SDK são documentadas aqui.

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/)
e versionamento [SemVer](https://semver.org/lang/pt-BR/).

O SDK acompanha a superfície `/v3` da API: rota nova na API vira função nova
aqui, na mesma leva. A área de legado (`client.legacy`) acompanha o contrato
antigo do gateway: quando a `/v3` ganha o equivalente de uma rota, a função
troca o transporte **sem mudar de assinatura**, e a troca é registrada aqui,
rota a rota.

---

## [Unreleased]

Tudo abaixo entra na **0.1.0**, a primeira publicação. Enquanto a tag não sai,
o conteúdo fica aqui — ver [PUBLICANDO.md](PUBLICANDO.md).

### Added

- **O cliente da `/v3`**, com os cinco recursos que a API responde hoje:
  modelos (listar com filtro de canal, buscar por id), etiquetas (listar,
  buscar), lista de permitidos (listar), frescor da carga e versão. Quem
  instala não escreve HTTP: não monta URL, não põe cabeçalho, não desembrulha
  envelope e não lê status para saber se deu certo.
- **O envelope resolvido por rota.** `templates`, `tags` e `allowlist`
  respondem `{"data": …}`; `freshness` e `version` respondem o objeto direto.
  Desembrulhar tudo, ou nada, quebra metade das chamadas — a escolha é do SDK,
  e quem chama nem sabe que existe envelope.
- **Um tipo de falha só.** Recusa do catálogo, proxy respondendo HTML no lugar
  da API e rede fora do ar chegam todos como `ApiError`. Não há erro de parser
  cru vazando para quem chamou.
- **`request_id` como campo de primeira classe**, e não detalhe enterrado: é
  o primeiro dado que o suporte pede, e um SDK que o engolisse obrigaria quem
  bateu na falha a reproduzir tudo no `curl` só para achar o número.
- **A rota aberta funciona sem credencial.** `version.get()` é pública; um
  cliente construído sem token chama ela, o que serve para conferir a
  instalação antes de ter credencial. Exigir token no construtor tornaria
  inalcançável justamente a rota que o suporte pede primeiro.
- **`Retry-After` já lido em segundos**, com `retryable` dizendo se vale
  repetir. **Repetir é decisão de quem chama** — o SDK não repete sozinho,
  porque só quem chamou sabe se a operação pode acontecer duas vezes.
- **Tipado de verdade:** `py.typed`, `mypy --strict` limpo, e `channel` é
  `Literal` — valor fora da lista o verificador recusa antes da chamada.
- **Zero dependência.** Só a biblioteca padrão (`urllib`), então o SDK nunca
  briga com o que a aplicação de quem instala já fixou.
- Os objetos são `TypedDict`, não dataclass: o que volta é o JSON já tipado,
  sem camada de conversão que possa divergir do servidor sem ninguém perceber
  — e campo novo na API continua passando em vez de estourar aqui.
- **A área de legado** (`client.legacy`): tudo o que a documentação pública do
  gateway documenta, como função tipada apontando para `api.ar-online.com.br`
  — envio multicanal (`send`), status por canal e consolidado
  (`status.email/sms/whatsapp/voz/carta/full`), comprovante com o PDF já
  decodificado do base64 (`sending_proof`), laudo pericial binário (`laudo`),
  finalizar régua (`finalizar_regua`) e os modelos do gateway
  (`templates.list/get/update/deactivate/set_status`). Endereço próprio, com
  padrão de produção, independente do endereço da `/v3`.
- **A credencial do legado é outra**, e o SDK trata as duas no mesmo cliente:
  o JWT do gateway vai **cru** no cabeçalho `authorization`, sem `Bearer` — o
  oposto da `/v3`. Nenhuma das duas vaza para a área da outra, e chamada de
  legado sem `legacy_token` falha **antes do socket**, dizendo qual token
  falta.
- **O envelope do gateway resolvido.** A família de modelos responde
  `{"data": …, "statusCode": …}` com **HTTP 200 até em erro**; o SDK lê o
  código de dentro e levanta `LegacyApiError`, que carrega `status` (o que
  vale), `http_status` (o que o fio disse) e `body` (o corpo cru). É o defeito
  nº 1 de quem integra na mão, e é exatamente o que a área abstrai.
- **Fidelidade ao contrato antigo, de propósito.** As quatro convenções de
  ausência ficam nos tipos como vêm no fio, e as duas que se pareceriam em
  Python ficam distinguíveis: chave que vem `null` é `| None`, chave que
  **some** da resposta é chave não obrigatória de um bloco `total=False`. A
  voz responde 200 com frase para uuid sem registro, e isso não é erro;
  `finalizar_regua` é GET com efeito colateral e o SDK não "conserta" para
  POST; data do legado fica `str`, porque `"18/07/2026 01:01:32"` não
  identifica um instante sem ambiguidade. Normalizar qualquer uma delas
  quebraria quem já integrou.
- **Tipos dos webhooks** (`WebhookPayloadV1`, `WebhookPayloadV2`) exportados
  para quem recebe as chamadas — o contrato pronto, sem digitar à mão.
- As rotas de versões de modelo do gateway (`/versions` e `/versions/{v}`)
  ficaram **de fora**: produção responde vazio ou 404 sempre, e função que
  nunca acha nada só convida integração contra recurso morto.

### Quality

- Portão com lint, formato, ortografia (codespell), **cobertura mínima de
  95%** e auditoria de dependência. Nada com `allow_failure`, que é a mesma
  regra do portão da API.
- Os testes falam com um **servidor de verdade numa porta livre**, não com um
  dublê de HTTP: o que um SDK precisa acertar é justamente o fio — qual rota
  embrulha, como a recusa volta, o que acontece quando algo que não é a API
  responde. Dublê provaria só que o código chama o dublê.
- CI em três sistemas operacionais × Python 3.10, 3.11, 3.12 e 3.13.
- Publicação por **Trusted Publishing** no PyPI (OIDC, sem token). O PyPI
  aceita *publisher pendente*, então até a primeira versão sai sem credencial.

- Os testes da área de legado cobrem as esquisitices uma a uma: 200-com-erro
  dos modelos, voz sem registro, as quatro convenções de ausência, base64 e
  binário, 401 cru do gateway, o token indo sem `Bearer` e as duas
  credenciais sem uma vazar na área da outra.

Hoje o portão mede: **86 testes, 100% de cobertura**.

[Unreleased]: https://github.com/AR-Online/ar-online-python/commits/main
