"""Comprovante, laudo e a régua: base64, binário e um GET que escreve."""

from __future__ import annotations

import pytest

from aronline import LegacyApiError, LegacyArea
from tests.support.fake_api import FakeApi


class TestSendingProof:
    def test_decodifica_o_base64_e_deixa_o_cru_acessivel(
        self, api: FakeApi, legacy: LegacyArea
    ) -> None:
        # 'JVBERi0x' é '%PDF-1' — o começo de qualquer PDF de verdade.
        api.answers({"content": "JVBERi0x"})

        comprovante = legacy.sending_proof("f6cb58f2")

        assert comprovante["content_base64"] == "JVBERi0x"
        assert comprovante["message"] is None
        assert comprovante["pdf"] == b"%PDF-1"
        assert api.received.path == "/gw/sending-proof/f6cb58f2"

    def test_sem_status_de_entrega_vem_mensagem_e_nao_e_erro(
        self, api: FakeApi, legacy: LegacyArea
    ) -> None:
        api.answers(
            {"message": "O comprovante para e-mail consultado ainda não possui o status de entrega"}
        )

        comprovante = legacy.sending_proof("f6cb58f2")

        assert comprovante["pdf"] is None
        assert comprovante["content_base64"] is None
        assert "ainda não possui o status" in (comprovante["message"] or "")

    def test_corpo_sem_content_nem_message_resolve_com_os_tres_nulos(
        self, api: FakeApi, legacy: LegacyArea
    ) -> None:
        api.answers({})

        assert legacy.sending_proof("f6cb58f2") == {
            "pdf": None,
            "content_base64": None,
            "message": None,
        }

    def test_base64_ilegivel_vira_erro_do_sdk_nao_excecao_crua(
        self, api: FakeApi, legacy: LegacyArea
    ) -> None:
        api.answers({"content": "%%%não-é-base64%%%"})

        with pytest.raises(LegacyApiError) as caught:
            legacy.sending_proof("f6cb58f2")

        assert "base64" in caught.value.message
        assert caught.value.body == {"content": "%%%não-é-base64%%%"}


class TestLaudo:
    def test_entrega_os_bytes_do_pdf_binario_como_vieram(
        self, api: FakeApi, legacy: LegacyArea
    ) -> None:
        api.answers_raw(200, "%PDF-1.4 laudo", "application/pdf")

        laudo = legacy.laudo("f6cb58f2")

        assert laudo == b"%PDF-1.4 laudo"
        assert api.received.path == "/gw/email/laudo/f6cb58f2"

    def test_registro_que_nao_existe_responde_404_em_json(
        self, api: FakeApi, legacy: LegacyArea
    ) -> None:
        api.answers_json_raw(404, {"statusCode": 404, "message": "Registro não encontrado"})

        with pytest.raises(LegacyApiError) as caught:
            legacy.laudo("sumido")

        assert caught.value.status == 404
        assert caught.value.message == "Registro não encontrado"


class TestFinalizarRegua:
    def test_e_get_com_efeito_colateral_e_o_sdk_nao_conserta(
        self, api: FakeApi, legacy: LegacyArea
    ) -> None:
        api.answers({"message": "Regua de notificação finalizada com sucesso"})

        resultado = legacy.finalizar_regua("f6cb58f2")

        assert resultado["message"] == "Regua de notificação finalizada com sucesso"
        assert api.received.method == "GET"
        assert api.received.path == "/regua-notificacao/finalizar/f6cb58f2"
