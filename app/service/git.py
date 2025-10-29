import subprocess
import requests
import xml.etree.ElementTree as ET

OWNER = "purplemashu"
REPO  = "me-cli"
BRANCH = "main"

def get_local_commit():
    """Return current local commit hash, or None if not in a git repo."""
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        return None

def get_latest_commit_atom():
    """Return the latest commit SHA from GitHub via the Atom feed (no auth)."""
    url = f"https://github.com/{OWNER}/{REPO}/commits/{BRANCH}.atom"
    r = requests.get(url, timeout=5)
    r.raise_for_status()
    root = ET.fromstring(r.text)
    ns = {"a": "http://www.w3.org/2005/Atom"}
    entry = root.find("a:entry", ns)
    if entry is None:
        return None
    entry_id = entry.find("a:id", ns)
    if entry_id is None or not entry_id.text:
        return None
    # The SHA is the last path segment of the <id> URL
    return entry_id.text.rsplit("/", 1)[-1]

def check_for_updates():
    local = get_local_commit()
    try:
        remote = get_latest_commit_atom()
    except Exception:
        remote = None

    if not remote:
        # Could not fetch remote commit
        return False

    if not local:
        # Not a git repo
        return False

    if local != remote:
        print(f"⚠️  A newer version is available (remote {remote[:7]} vs local {local[:7]}).")
        print("   Run: git pull --rebase to update.")
        return True
    else:
        # Up to date
        return False
