"""Templates do gateway: o envelope que responde 200 até em erro."""

from __future__ import annotations

import json

import pytest

from aronline import GW_TEMPLATE_TYPES, LegacyApiError, LegacyArea
from tests.support.fake_api import FakeApi

GW_TEMPLATE = {
    "id": "9b2f-uuid",
    "templateId": "hx_boleto_01",
    "nome": "Aviso de boleto",
    "tipo": "whatsapp",
    "conteudo": "Olá {{1}}, …",
    "variaveis": [{"type": "body", "parameters": [{"name": "1"}]}],
    "metadata": None,
    "ativo": True,
    "versao": 1,
    "criadoEm": "2024-10-12T17:11:13.000Z",
    "atualizadoEm": None,
    "criadoPor": None,
}


class TestOsCodigosDeTipo:
    def test_sao_os_quatro_do_legado(self) -> None:
        assert GW_TEMPLATE_TYPES == ("1", "2", "3", "4")


class TestList:
    def test_desembrulha_o_envelope_e_devolve_a_lista(
        self, api: FakeApi, legacy: LegacyArea
    ) -> None:
        api.answers({"data": [GW_TEMPLATE], "statusCode": 200})

        assert legacy.templates.list() == [GW_TEMPLATE]
        assert api.received.path == "/gw/templates"

    def test_leva_o_codigo_legado_como_filtro_de_query(
        self, api: FakeApi, legacy: LegacyArea
    ) -> None:
        api.answers({"data": [], "statusCode": 200})

        legacy.templates.list(type="1")

        assert api.received.path == "/gw/templates?type=1"

    def test_omite_o_filtro_quando_o_tipo_nao_vem(self, api: FakeApi, legacy: LegacyArea) -> None:
        api.answers({"data": [], "statusCode": 200})

        legacy.templates.list(type=None)

        assert api.received.path == "/gw/templates"

    def test_envelope_sem_status_code_conta_como_200(
        self, api: FakeApi, legacy: LegacyArea
    ) -> None:
        api.answers({"data": [GW_TEMPLATE]})

        assert legacy.templates.list() == [GW_TEMPLATE]

    def test_resposta_sem_o_envelope_prometido_vira_erro_nao_none(
        self, api: FakeApi, legacy: LegacyArea
    ) -> None:
        api.answers([GW_TEMPLATE])

        with pytest.raises(LegacyApiError) as caught:
            legacy.templates.list()

        assert "envelope" in caught.value.message


class TestGet:
    def test_http_200_com_erro_dentro_do_envelope_vira_erro_tipado(
        self, api: FakeApi, legacy: LegacyArea
    ) -> None:
        fio = {"data": {"error": "Template não encontrado"}, "statusCode": 404}
        api.answers(fio)

        with pytest.raises(LegacyApiError) as caught:
            legacy.templates.get("sumido")

        assert caught.value.status == 404
        assert caught.value.http_status == 200
        assert caught.value.message == "Template não encontrado"
        assert caught.value.body == fio

    def test_template_de_outra_entidade_responde_o_403_do_envelope(
        self, api: FakeApi, legacy: LegacyArea
    ) -> None:
        api.answers({"data": {"error": "Acesso negado ao template"}, "statusCode": 403})

        with pytest.raises(LegacyApiError) as caught:
            legacy.templates.get("9b2f-uuid")

        assert caught.value.status == 403
        assert caught.value.http_status == 200
        assert caught.value.message == "Acesso negado ao template"

    def test_id_que_nao_e_uuid_responde_o_500_do_envelope(
        self, api: FakeApi, legacy: LegacyArea
    ) -> None:
        api.answers({"data": {"error": "Erro ao buscar template(s)"}, "statusCode": 500})

        with pytest.raises(LegacyApiError) as caught:
            legacy.templates.get("torto")

        assert caught.value.status == 500
        assert caught.value.http_status == 200

    def test_recusa_sem_mensagem_dentro_ainda_diz_o_codigo(
        self, api: FakeApi, legacy: LegacyArea
    ) -> None:
        api.answers({"data": None, "statusCode": 502})

        with pytest.raises(LegacyApiError) as caught:
            legacy.templates.get("9b2f-uuid")

        assert caught.value.status == 502
        assert "502" in caught.value.message

    def test_busca_pelo_uuid_publico_escapado(self, api: FakeApi, legacy: LegacyArea) -> None:
        api.answers({"data": GW_TEMPLATE, "statusCode": 200})

        assert legacy.templates.get("9b2f-uuid") == GW_TEMPLATE
        assert api.received.path == "/gw/templates/9b2f-uuid"

    def test_escapa_o_id(self, api: FakeApi, legacy: LegacyArea) -> None:
        api.answers({"data": GW_TEMPLATE, "statusCode": 200})

        legacy.templates.get("../../gw/full/x")

        assert api.received.path == "/gw/templates/..%2F..%2Fgw%2Ffull%2Fx"


class TestEscrita:
    def test_update_manda_put_com_so_o_que_o_gateway_deixa_editar(
        self, api: FakeApi, legacy: LegacyArea
    ) -> None:
        api.answers({"data": {"ok": True}, "statusCode": 200})

        resultado = legacy.templates.update(
            "9b2f-uuid", {"nome": "Novo nome", "compartilhadoComEntidade": True}
        )

        assert resultado == {"ok": True}
        assert api.received.method == "PUT"
        assert api.received.path == "/gw/templates/9b2f-uuid"
        assert json.loads(api.received.body) == {
            "nome": "Novo nome",
            "compartilhadoComEntidade": True,
        }

    def test_deactivate_e_delete_sem_corpo(self, api: FakeApi, legacy: LegacyArea) -> None:
        api.answers({"data": {"ok": True}, "statusCode": 200})

        legacy.templates.deactivate("9b2f-uuid")

        assert api.received.method == "DELETE"
        assert api.received.path == "/gw/templates/9b2f-uuid"
        assert api.received.body == ""

    def test_set_status_e_patch_em_status_com_ativo(self, api: FakeApi, legacy: LegacyArea) -> None:
        api.answers({"data": {"ok": True}, "statusCode": 200})

        legacy.templates.set_status("9b2f-uuid", ativo=False)

        assert api.received.method == "PATCH"
        assert api.received.path == "/gw/templates/9b2f-uuid/status"
        assert json.loads(api.received.body) == {"ativo": False}


class TestACredencialDoGateway:
    def test_sem_token_o_gateway_responde_o_401_dele_com_o_corpo_cru(
        self, api: FakeApi, legacy: LegacyArea
    ) -> None:
        fio = {"message": "Unauthorized", "statusCode": 401}
        api.answers_json_raw(401, fio)

        with pytest.raises(LegacyApiError) as caught:
            legacy.templates.list()

        assert caught.value.status == 401
        assert caught.value.http_status == 401
        assert caught.value.message == "Unauthorized"
        assert caught.value.body == fio
