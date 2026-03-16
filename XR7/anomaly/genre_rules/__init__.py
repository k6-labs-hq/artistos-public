from __future__ import annotations

from typing import Callable


_GENRE_RULES: dict[str, Callable[[dict], dict]] = {}


def register_genre_rule(name: str, fn: Callable[[dict], dict]) -> None:
    _GENRE_RULES[name.strip().lower()] = fn


def get_genre_rule(name: str) -> Callable[[dict], dict] | None:
    return _GENRE_RULES.get(name.strip().lower())


def apply_genre_rule(name: str, payload: dict) -> dict:
    fn = get_genre_rule(name)
    return fn(payload) if fn else payload


# Example pluggable rule for new genres like Afrofuturism.
def _afrofuturism_rule(payload: dict) -> dict:
    payload = dict(payload)
    payload.setdefault("genre_adjustment", {})
    payload["genre_adjustment"]["afrofuturism_sync_weight"] = 1.12
    return payload


register_genre_rule("afrofuturism", _afrofuturism_rule)
