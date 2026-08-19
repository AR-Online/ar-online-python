"""Envio: a rota multicanal, apesar do caminho dizer e-mail."""

from __future__ import annotations

import json

import pytest

from aronline import EnvioRequest, LegacyApiError, LegacyArea
from tests.support.fake_api import FakeApi


class TestSend:
    def test_posta_o_corpo_como_json_e_devolve_o_id_email(
        self, api: FakeApi, legacy: LegacyArea
    ) -> None:
        api.answers({"idEmail": "8c4813f5-8430-4ad4-ab72-19d7eed39731"})

        envio: EnvioRequest = {
            "nameTo": "João da Silva",
            "to": "joao@exemplo.com",
            "subject": "Documento importante",
            "content": "<p>Você recebeu um documento.</p>",
            "sms": {"number": "11999998888", "typeSend": "1"},
        }

        enviado = legacy.send(envio)

        assert enviado == {"idEmail": "8c4813f5-8430-4ad4-ab72-19d7eed39731"}
        assert api.received.method == "POST"
        assert api.received.path == "/gw/email"
        assert api.received.content_type == "application/json"
        assert json.loads(api.received.body) == envio

    def test_leva_os_cinco_canais_no_mesmo_corpo(self, api: FakeApi, legacy: LegacyArea) -> None:
        api.answers({"idEmail": "qualquer"})

        envio: EnvioRequest = {
            "nameTo": "João da Silva",
            "to": "joao@exemplo.com",
            "subject": "Aviso",
            "content": "<p>Conteúdo.</p>",
            "customID": "contrato-4471",
            "attachments": [{"name": "contrato.pdf", "base64": "JVBERi0x"}],
            "validation": {"question": "Seu CPF?", "reply": "12345678901"},
            "sms": {"number": "11999998888", "typeSend": "2"},
            "whatsapp": {"number": "11999998888", "variables": {"template": "aviso_01"}},
            "voz": {"number": "1133334444", "template": "aviso_voz"},
            "carta": {"name": "João da Silva", "modelo": "padrao"},
        }

        legacy.send(envio)

        assert json.loads(api.received.body) == envio

    def test_recusa_do_gateway_vira_erro_tipado_com_o_corpo_cru(
        self, api: FakeApi, legacy: LegacyArea
    ) -> None:
        corpo = {
            "statusCode": 400,
            "message": "O número do destinatário informado é inválido, Verifique o número.",
        }
        api.answers_json_raw(400, corpo)

        with pytest.raises(LegacyApiError) as caught:
            legacy.send({"nameTo": "A", "subject": "B", "content": "C"})

        assert caught.value.status == 400
        assert caught.value.http_status == 400
        assert caught.value.message == corpo["message"]
        assert caught.value.body == corpo

    def test_401_cru_do_gateway(self, api: FakeApi, legacy: LegacyArea) -> None:
        corpo = {"message": "Unauthorized", "statusCode": 401}
        api.answers_json_raw(401, corpo)

        with pytest.raises(LegacyApiError) as caught:
            legacy.send({"nameTo": "A", "subject": "B", "content": "C"})

        assert caught.value.status == 401
        assert caught.value.http_status == 401
        assert caught.value.message == "Unauthorized"
        assert caught.value.body == corpo
