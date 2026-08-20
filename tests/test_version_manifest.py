"""A constante e o manifesto dizem a mesma versão.

Este teste existe porque a divergência já aconteceu no SDK TypeScript: a 0.2.1
foi publicada exportando ``VERSION = "0.2.0"``. Ninguém notou, porque nada
conferia — e o número que o pacote anuncia sobre si mesmo é o que o suporte
pede primeiro.

O manifesto é a fonte: é dele que o build tira a versão da roda, e é ela que o
workflow de release confere contra a tag.

Lido por expressão regular, e não com ``tomllib``: o SDK promete Python 3.10, e
o ``tomllib`` só entrou na 3.11. Depender dele aqui faria o teste quebrar
justamente na versão mínima que o manifesto promete suportar.
"""

from __future__ import annotations

import re
from pathlib import Path

import aronline

PYPROJECT = Path(__file__).resolve().parent.parent / "pyproject.toml"


def manifest_version() -> str:
    for line in PYPROJECT.read_text(encoding="utf-8").splitlines():
        found = re.fullmatch(r'version\s*=\s*"([^"]+)"', line.strip())

        if found:
            return found.group(1)

    raise AssertionError(f'nenhuma linha `version = "…"` em {PYPROJECT}')


def test_version_matches_manifest() -> None:
    assert manifest_version() == aronline.VERSION
