"""Request the Jira "Reviewer" as the GitHub reviewer when a PR opens.

Run by .github/workflows/jira-reviewer.yml. Steps:
  1. Find the Jira key (e.g. NTT-37) in the PR's branch name, or else its title.
  2. Read that issue's Reviewer field from Jira.
  3. Map each Jira user to a GitHub username (tools/jira_github_users.json).
  4. Request them as reviewers on the PR (skipping the PR author).

It never fails the PR: anything missing is logged and skipped.
Standard library only, so the workflow needs no pip install.
"""
import base64
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ISSUE_KEY = re.compile(r"\b(NTT-\d+)\b", re.IGNORECASE)
REVIEWER_FIELD = "customfield_10043"
USERS_FILE = Path(__file__).with_name("jira_github_users.json")


# ---- pure logic (unit tested) ------------------------------------------

def find_issue_key(*texts):
    """First Jira key found in the given strings, upper-cased, or None."""
    for text in texts:
        match = ISSUE_KEY.search(text or "")
        if match:
            return match.group(1).upper()
    return None


def pick_reviewers(jira_users, mapping, author, already_requested=()):
    """GitHub usernames to request: mapped, not the author, not already requested."""
    skip = {author.lower(), *(r.lower() for r in already_requested)}
    picked, unmapped = [], []
    for user in jira_users or []:
        login = mapping.get(user.get("accountId"))
        if not login:
            unmapped.append(user.get("displayName", user.get("accountId")))
        elif login.lower() not in skip and login not in picked:
            picked.append(login)
    return picked, unmapped


def run(event, fetch_jira_reviewers, request_github_reviewers, mapping, log=print):
    pr = event["pull_request"]
    key = find_issue_key(pr["head"]["ref"], pr.get("title", ""))
    if not key:
        log("No NTT-### key in branch name or title; nothing to do.")
        return []

    jira_users = fetch_jira_reviewers(key)
    if not jira_users:
        log(f"{key} has no Reviewer set in Jira; nothing to do.")
        return []

    already = [r["login"] for r in pr.get("requested_reviewers", [])]
    reviewers, unmapped = pick_reviewers(jira_users, mapping, pr["user"]["login"], already)
    for name in unmapped:
        log(f"No GitHub username for Jira user '{name}'. Add them to {USERS_FILE.name}.")
    if not reviewers:
        log(f"{key}: no one new to request.")
        return []

    request_github_reviewers(pr["number"], reviewers)
    log(f"{key}: requested review from {', '.join(reviewers)}.")
    return reviewers


# ---- network (GitHub Actions only) -------------------------------------

def _call(url, headers, data=None):
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method="POST" if body else "GET")
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read() or b"null")


def jira_fetcher(base_url, email, token):
    auth = base64.b64encode(f"{email}:{token}".encode()).decode()
    headers = {"Authorization": f"Basic {auth}", "Accept": "application/json"}

    def fetch(key):
        data = _call(f"{base_url}/rest/api/3/issue/{key}?fields={REVIEWER_FIELD}", headers)
        return (data.get("fields") or {}).get(REVIEWER_FIELD) or []

    return fetch


def github_requester(repo, token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
    }

    def request(number, reviewers):
        _call(f"https://api.github.com/repos/{repo}/pulls/{number}/requested_reviewers",
              headers, {"reviewers": reviewers})

    return request


def main():
    env = os.environ
    missing = [v for v in ("JIRA_BASE_URL", "JIRA_EMAIL", "JIRA_API_TOKEN", "GITHUB_TOKEN") if not env.get(v)]
    if missing:
        print(f"::warning::Skipping Jira reviewer sync, missing: {', '.join(missing)}")
        return 0

    event = json.loads(Path(env["GITHUB_EVENT_PATH"]).read_text())
    mapping = {k: v for k, v in json.loads(USERS_FILE.read_text()).items() if not k.startswith("_")}
    try:
        run(event,
            jira_fetcher(env["JIRA_BASE_URL"].rstrip("/"), env["JIRA_EMAIL"], env["JIRA_API_TOKEN"]),
            github_requester(env["GITHUB_REPOSITORY"], env["GITHUB_TOKEN"]),
            mapping)
    except urllib.error.HTTPError as e:
        print(f"::warning::Jira reviewer sync failed: HTTP {e.code} {e.read().decode(errors='replace')[:300]}")
    except urllib.error.URLError as e:
        print(f"::warning::Jira reviewer sync failed: {e.reason}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
