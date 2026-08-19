"""Status por canal: as quatro convenções de ausência e uma esquisitice por canal."""

from __future__ import annotations

import pytest

from aronline import LegacyApiError, LegacyArea
from tests.support.fake_api import FakeApi


class TestEmail:
    def test_entrega_a_resposta_como_veio_vazio_e_nulo_sao_convencoes_diferentes(
        self, api: FakeApi, legacy: LegacyArea
    ) -> None:
        fio = {
            "dateSend": "18/07/2026 01:01:32",
            "dateDelivery": "",
            "dateReading": None,
            "dateAcceptance": None,
            "error": False,
            "description": "Enviado",
            "failureReason": None,
            "customID": "pedido-4471",
            "idEmail": "c62582cc-fc79-4ef5-a20d-27a8476b651d",
        }
        api.answers(fio)

        status = legacy.status.email("c62582cc")

        assert status == fio
        assert status["dateDelivery"] == ""
        assert status["dateReading"] is None
        assert api.received.method == "GET"
        assert api.received.path == "/gw/email/c62582cc"

    def test_a_data_fica_string_nao_datetime(self, api: FakeApi, legacy: LegacyArea) -> None:
        api.answers({"dateSend": "18/07/2026 01:01:32"})

        status = legacy.status.email("c62582cc")

        assert status["dateSend"] == "18/07/2026 01:01:32"
        assert isinstance(status["dateSend"], str)

    def test_notificacao_de_outra_pessoa_chega_como_o_404_do_gateway(
        self, api: FakeApi, legacy: LegacyArea
    ) -> None:
        api.answers_json_raw(404, {"message": "E-mail não encontrado"})

        with pytest.raises(LegacyApiError) as caught:
            legacy.status.email("sumido")

        assert caught.value.status == 404
        assert caught.value.http_status == 404
        assert caught.value.message == "E-mail não encontrado"

    def test_escapa_o_id(self, api: FakeApi, legacy: LegacyArea) -> None:
        api.answers({})

        legacy.status.email("../full/x")

        assert api.received.path == "/gw/email/..%2Ffull%2Fx"


class TestSms:
    def test_answered_e_lista_de_objetos(self, api: FakeApi, legacy: LegacyArea) -> None:
        api.answers(
            {
                "description": "Entregue",
                "dateSend": "18/07/2026 01:01:32",
                "dateReading": None,
                "dateAnswered": None,
                "answered": [{"resposta": "SIM", "em": "18/07/2026 02:00:00"}],
            }
        )

        status = legacy.status.sms("c62582cc")

        assert status["answered"] == [{"resposta": "SIM", "em": "18/07/2026 02:00:00"}]
        assert api.received.path == "/gw/sms/c62582cc"


class TestWhatsapp:
    def test_data_que_nao_aconteceu_some_da_resposta_e_continua_sumida(
        self, api: FakeApi, legacy: LegacyArea
    ) -> None:
        api.answers(
            {
                "description": "Enviado",
                "dateSent": "18/07/2026 01:01:32",
                "error": False,
                "failureReason": None,
                "customID": None,
                "idEmail": "c62582cc-fc79-4ef5-a20d-27a8476b651d",
            }
        )

        status = legacy.status.whatsapp("c62582cc")

        assert "dateDelivery" not in status
        assert status["dateSent"] == "18/07/2026 01:01:32"
        assert api.received.path == "/gw/whatsapp/c62582cc"

    def test_o_custom_id_vem_sempre_nulo_nesta_rota(self, api: FakeApi, legacy: LegacyArea) -> None:
        api.answers(
            {
                "description": "Enviado",
                "error": False,
                "failureReason": None,
                "customID": None,
                "idEmail": "c62582cc",
            }
        )

        assert legacy.status.whatsapp("c62582cc")["customID"] is None


class TestVoz:
    def test_uuid_sem_registro_responde_200_com_frase_e_nao_e_erro(
        self, api: FakeApi, legacy: LegacyArea
    ) -> None:
        api.answers({"description": "Não há registro de voz para este envio"})

        status = legacy.status.voz("qualquer")

        assert status["description"] == "Não há registro de voz para este envio"
        assert "dateSuccessCall" not in status
        assert api.received.path == "/gw/voz/qualquer"

    def test_a_chamada_que_falhou_nao_traz_a_data_de_sucesso(
        self, api: FakeApi, legacy: LegacyArea
    ) -> None:
        api.answers(
            {
                "description": "Falha na ligação",
                "dateSent": "18/07/2026 01:01:32",
                "dateFailureCall": "18/07/2026 01:03:00",
            }
        )

        status = legacy.status.voz("c62582cc")

        assert status["dateFailureCall"] == "18/07/2026 01:03:00"
        assert "dateSuccessCall" not in status


class TestCarta:
    def test_entrega_as_etapas_com_os_nomes_do_contrato_nao_os_do_provedor(
        self, api: FakeApi, legacy: LegacyArea
    ) -> None:
        fio = {
            "description": "Entregue",
            "error": False,
            "dateProcessing": "05/08/2025 11:00:15",
            "datePreparation": "05/08/2025 11:02:40",
            "dateSent": "27/08/2025 15:23:57",
            "dateDelivery": "02/09/2025 10:11:00",
            "sro": "YQ694562879BR",
            "linkRastreio": "https://rastreamento.correios.com.br/YQ694562879BR",
        }
        api.answers(fio)

        status = legacy.status.carta("c62582cc")

        assert status == fio
        assert "datePrepared" not in status
        assert "dateDelivered" not in status
        assert api.received.path == "/gw/carta/c62582cc"


class TestFull:
    def test_entrega_o_consolidado_com_historico_ultimo_status_e_os_blocos(
        self, api: FakeApi, legacy: LegacyArea
    ) -> None:
        fio = {
            "codEmail": 12345,
            "statusFull": {"email": [{"label": "Enviado", "dateTime": "14/05/2025 17:04:44"}]},
            "lastStatus": {"email": {"label": "Enviado", "dateTime": "14/05/2025 17:04:44"}},
            "email": [{"subject": "Documento", "remetente": "noreply@empresa.com"}],
            "sms": [],
            "whatsapp": [],
            "voz": [],
            "carta": [],
        }
        api.answers(fio)

        full = legacy.status.full("f6cb58f2")

        assert full == fio
        assert full["lastStatus"]["email"]["label"] == "Enviado"
        assert api.received.path == "/gw/full/f6cb58f2"
