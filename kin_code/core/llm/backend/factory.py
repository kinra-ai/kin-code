from __future__ import annotations

from kin_code.core.config import Backend
from kin_code.core.llm.backend.generic import GenericBackend
from kin_code.core.llm.backend.mistral import MistralBackend

BACKEND_FACTORY = {Backend.MISTRAL: MistralBackend, Backend.GENERIC: GenericBackend}
