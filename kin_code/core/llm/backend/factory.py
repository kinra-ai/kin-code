from __future__ import annotations

from kin_code.core.config import Backend
from kin_code.core.llm.backend.generic import GenericBackend

BACKEND_FACTORY = {Backend.GENERIC: GenericBackend}
