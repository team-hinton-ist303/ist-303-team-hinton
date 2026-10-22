"""Tests for tools/sync_jira_reviewer.py (Jira Reviewer -> GitHub reviewer)."""
import json
from pathlib import Path

import pytest

from tools.sync_jira_reviewer import USERS_FILE, find_issue_key, pick_reviewers, run

DANIEL = {"accountId": "712020:d9371eb3-c6f2-4f17-8fef-fd053f2422a4", "displayName": "Daniel Abalusi"}
YALEI = {"accountId": "712020:3b2cc388-114e-4847-9b0e-db668a0541ca", "displayName": "Yalei Xu"}
STRANGER = {"accountId": "unknown-id", "displayName": "New Person"}
MAPPING = {DANIEL["accountId"]: "dabalus", YALEI["accountId"]: "AaronXu2026"}


def event(branch="NTT-37-editor-shell", title="Editor shell", author="VShahidzadeh", requested=()):
    return {"pull_request": {
        "number": 12, "title": title, "head": {"ref": branch},
        "user": {"login": author}, "requested_reviewers": [{"login": r} for r in requested],
    }}


@pytest.mark.parametrize("texts, expected", [
    (("NTT-37-editor-shell",), "NTT-37"),
    (("spike/NTT-46-svg",), "NTT-46"),
    (("ntt-111-fixture",), "NTT-111"),
    (("feature/no-key", "NTT-31: login route"), "NTT-31"),
    (("main", "Fix typo"), None),
])
def test_find_issue_key(texts, expected):
    assert find_issue_key(*texts) == expected


def test_pick_reviewers_maps_and_skips_author():
    picked, unmapped = pick_reviewers([DANIEL, YALEI], MAPPING, author="dabalus")
    assert picked == ["AaronXu2026"]
    assert unmapped == []


def test_pick_reviewers_skips_already_requested_case_insensitive():
    picked, _ = pick_reviewers([DANIEL], MAPPING, author="x", already_requested=["DABALUS"])
    assert picked == []


def test_pick_reviewers_reports_unmapped_users():
    picked, unmapped = pick_reviewers([STRANGER, DANIEL], MAPPING, author="x")
    assert picked == ["dabalus"]
    assert unmapped == ["New Person"]


def test_run_requests_jira_reviewer():
    calls = []
    result = run(event(), lambda key: [YALEI], lambda n, r: calls.append((n, r)), MAPPING, log=lambda m: None)
    assert result == ["AaronXu2026"]
    assert calls == [(12, ["AaronXu2026"])]


def test_run_looks_up_key_from_branch():
    seen = []
    run(event(branch="NTT-28-password-hash"), lambda key: seen.append(key) or [],
        lambda n, r: None, MAPPING, log=lambda m: None)
    assert seen == ["NTT-28"]


def test_run_does_nothing_without_key():
    def fail(*a):
        raise AssertionError("should not be called")
    assert run(event(branch="main", title="Tidy up"), fail, fail, MAPPING, log=lambda m: None) == []


def test_run_does_nothing_when_jira_reviewer_empty():
    calls = []
    assert run(event(), lambda key: [], lambda n, r: calls.append(r), MAPPING, log=lambda m: None) == []
    assert calls == []


def test_mapping_file_is_valid_and_covers_team():
    data = json.loads(Path(USERS_FILE).read_text())
    logins = {v for k, v in data.items() if not k.startswith("_")}
    assert {"dabalus", "AaronXu2026", "bjkf908-bit", "Ry-Mill66", "VShahidzadeh"} <= logins
