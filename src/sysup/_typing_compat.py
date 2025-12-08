"""Typing compatibility module for Python 3.11+."""

import sys

if sys.version_info >= (3, 12):
    from typing import override as override
else:
    try:
        from typing_extensions import override as override  # type: ignore[assignment,unused-ignore]
    except ImportError:
        from typing import TypeVar

        _F = TypeVar("_F")

        def override(func: _F) -> _F:
            """Override decorator fallback."""
            return func


__all__ = ["override"]
