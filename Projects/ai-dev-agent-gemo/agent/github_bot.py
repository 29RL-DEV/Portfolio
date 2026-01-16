import os
import requests
import base64
from datetime import datetime

GITHUB_API = "https://api.github.com"


def _get_headers():
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("Missing GITHUB_TOKEN in environment")
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _get_repo():
    repo = os.getenv("GITHUB_REPO")
    if not repo:
        raise RuntimeError("Missing GITHUB_REPO in environment (format: user/repo)")
    return repo


def _get_default_branch():
    repo = _get_repo()
    url = f"{GITHUB_API}/repos/{repo}"
    r = requests.get(url, headers=_get_headers())
    r.raise_for_status()
    return r.json()["default_branch"]


def _get_latest_commit(branch):
    repo = _get_repo()
    url = f"{GITHUB_API}/repos/{repo}/commits/{branch}"
    r = requests.get(url, headers=_get_headers())
    r.raise_for_status()
    return r.json()["sha"]


def _create_branch(branch_name, base_sha):
    repo = _get_repo()
    url = f"{GITHUB_API}/repos/{repo}/git/refs"
    data = {
        "ref": f"refs/heads/{branch_name}",
        "sha": base_sha,
    }
    r = requests.post(url, headers=_get_headers(), json=data)

    # Dacă branch-ul există deja (409), încercăm cu alt nume
    if r.status_code == 409:
        print(f"⚠️  Branch {branch_name} already exists, trying with timestamp...")
        new_branch_name = f"{branch_name}-{datetime.utcnow().strftime('%S%f')}"
        data["ref"] = f"refs/heads/{new_branch_name}"
        r = requests.post(url, headers=_get_headers(), json=data)
        return new_branch_name

    r.raise_for_status()
    return branch_name


def _get_file_sha(path, branch):
    repo = _get_repo()
    url = f"{GITHUB_API}/repos/{repo}/contents/{path}?ref={branch}"
    r = requests.get(url, headers=_get_headers())
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return r.json()["sha"]


def _update_file(path, content, branch, message):
    repo = _get_repo()
    url = f"{GITHUB_API}/repos/{repo}/contents/{path}"

    sha = _get_file_sha(path, branch)

    # GitHub API necesită content base64 encoded
    content_b64 = base64.b64encode(content.encode("utf-8")).decode("utf-8")

    payload = {
        "message": message,
        "content": content_b64,
        "branch": branch,
    }

    if sha:
        payload["sha"] = sha

    r = requests.put(url, headers=_get_headers(), json=payload)

    if r.status_code == 409:
        raise RuntimeError("Conflict: File has been modified since you last read it")

    r.raise_for_status()
    return r.json()


def _create_pull_request(branch, title, body):
    repo = _get_repo()
    url = f"{GITHUB_API}/repos/{repo}/pulls"
    payload = {
        "title": title,
        "head": branch,
        "base": _get_default_branch(),
        "body": body,
        "draft": False,  # Poți schimba în True pentru PR draft
    }

    # Verifică dacă PR există deja
    list_url = f"{GITHUB_API}/repos/{repo}/pulls?head={repo.split('/')[0]}:{branch}"
    list_r = requests.get(list_url, headers=_get_headers())

    if list_r.status_code == 200 and len(list_r.json()) > 0:
        print(f"⚠️  PR already exists for branch {branch}")
        return list_r.json()[0]["html_url"]

    r = requests.post(url, headers=_get_headers(), json=payload)

    if r.status_code == 422:
        error_data = r.json()
        if "A pull request already exists" in str(error_data):
            print("⚠️  Pull request already exists")
            return None

    r.raise_for_status()
    return r.json()["html_url"]


def _create_commit_comment(commit_sha, comment):
    repo = _get_repo()
    url = f"{GITHUB_API}/repos/{repo}/commits/{commit_sha}/comments"
    payload = {"body": comment}
    r = requests.post(url, headers=_get_headers(), json=payload)
    r.raise_for_status()


def open_pull_request(bug, before_code, new_code, diff, report):
    """
    Creates a GitHub branch, commits the fixed file, and opens a PR.
    """

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    branch_name = f"ai-fix-{bug['function']}-{timestamp}"

    print(f"🌿 Creating branch {branch_name}")

    try:
        base_branch = _get_default_branch()
        base_sha = _get_latest_commit(base_branch)
        branch_name = _create_branch(branch_name, base_sha)

        print("📄 Uploading patched file to GitHub...")

        # Asigură-te că path-ul este corect
        file_path = bug.get("file_path", "app/calculator.py")

        commit_result = _update_file(
            path=file_path,
            content=new_code,
            branch=branch_name,
            message=f"🔧 AI Fix: {bug['name']}\n\n{bug.get('description', '')}",
        )

        pr_title = f"🤖 AI Fix: {bug['name']}"
        pr_body = f"""
## AI Bug Fix Report

**Bug:** {bug['name']}  
**Function:** `{bug['function']}`  
**Signature:** `{bug['signature']}`  
**Severity:** {bug.get('severity', 'Medium')}  
**File:** `{file_path}`

---

### 📋 Problem Description
{bug.get('description', 'No description provided')}

---

### 🤖 AI Analysis Report
{report}

---

### 🔍 Changes Made
```diff
{diff}
```
"""

        print("🔗 Creating pull request...")
        pr_url = _create_pull_request(branch_name, pr_title, pr_body)

        print(f"✅ PR opened successfully: {pr_url}")
        return {
            "branch": branch_name,
            "pr_url": pr_url,
            "commit_sha": commit_result["commit"]["sha"],
        }

    except Exception as e:
        print(f"❌ Error: {e}")
        raise
