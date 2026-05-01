"""Unit tests for lib.groups — GROUPS env var parser."""

from __future__ import annotations

import pytest

from lib.groups import (
    DEFAULT_GROUPS,
    KNOWN_GROUPS,
    WILDCARD_SENTINEL,
    UnknownGroupError,
    expand_wildcard,
    load_groups_from_env,
)


def test_default_when_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GROUPS", raising=False)
    assert load_groups_from_env() == list(DEFAULT_GROUPS)


def test_default_when_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GROUPS", "")
    assert load_groups_from_env() == list(DEFAULT_GROUPS)


def test_default_when_whitespace(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GROUPS", "   ")
    assert load_groups_from_env() == list(DEFAULT_GROUPS)


def test_single_group(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GROUPS", "proxy_manager")
    assert load_groups_from_env() == ["proxy_manager"]


def test_multiple_groups(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GROUPS", "account_management,proxy_manager,deep_lookup")
    assert load_groups_from_env() == [
        "account_management",
        "proxy_manager",
        "deep_lookup",
    ]


def test_groups_trimmed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GROUPS", "  account_management ,  proxy_manager  ")
    assert load_groups_from_env() == ["account_management", "proxy_manager"]


def test_groups_deduplicated(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GROUPS", "account_management,proxy_manager,account_management")
    assert load_groups_from_env() == ["account_management", "proxy_manager"]


def test_wildcard_star(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GROUPS", "*")
    assert load_groups_from_env() == [WILDCARD_SENTINEL]


def test_wildcard_all(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GROUPS", "all")
    assert load_groups_from_env() == [WILDCARD_SENTINEL]


def test_wildcard_case_insensitive(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GROUPS", "ALL")
    assert load_groups_from_env() == [WILDCARD_SENTINEL]


def test_unknown_group_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GROUPS", "nonexistent_group")
    with pytest.raises(UnknownGroupError) as excinfo:
        load_groups_from_env()
    assert "nonexistent_group" in str(excinfo.value)


def test_partial_unknown_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GROUPS", "account_management,bogus_group")
    with pytest.raises(UnknownGroupError):
        load_groups_from_env()


def test_expand_wildcard_resolves_to_all_known() -> None:
    expanded = expand_wildcard([WILDCARD_SENTINEL])
    assert expanded == list(KNOWN_GROUPS)


def test_expand_wildcard_passthrough_for_normal_lists() -> None:
    assert expand_wildcard(["account_management"]) == ["account_management"]
    assert expand_wildcard(["a", "b", "c"]) == ["a", "b", "c"]
