"""A lista de canais é duplicada do servidor — este teste é o que torna a
duplicação segura. Canal novo lá e não aqui faria o SDK recusar valor que a
API aceita, e quem chamou culparia o SDK, com razão."""

from __future__ import annotations

from aronline import CHANNELS


def test_e_exatamente_o_que_a_v3_aceita() -> None:
    assert CHANNELS == ("email", "sms", "whatsapp", "voice", "letter")


def test_nao_traz_o_carta_do_espelho() -> None:
    assert "carta" not in CHANNELS
