import os
import sys
import subprocess
from datetime import datetime

# ============================================================
# CONFIGURATION — update these if anything changes
# ============================================================
GITHUB_REPO   = "https://github.com/great-commission/gcbc-brochure.git"
BRANCH        = "main"
COMMIT_PREFIX = "Update brochure"   # prefix for auto commit messages
# ============================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def run(cmd, check=True):
    """Run a shell command, print it, and return the output."""
    print(f"  > {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=SCRIPT_DIR, capture_output=True, text=True)
    if result.stdout.strip():
        print(f"    {result.stdout.strip()}")
    if result.returncode != 0:
        if check:
            print(f"  ERROR: {result.stderr.strip()}")
            sys.exit(1)
        else:
            return None
    return result.stdout.strip()


def check_git():
    result = subprocess.run(["git", "--version"], capture_output=True, text=True)
    if result.returncode != 0:
        print("\n  Git is not installed or not on PATH.")
        print("  Download it from: https://git-scm.com/download/win")
        print("  After installing, restart VS Code and try again.\n")
        sys.exit(1)


def setup_repo():
    """Initialise git repo and remote if this folder isn't already one."""
    git_dir = os.path.join(SCRIPT_DIR, ".git")
    if not os.path.exists(git_dir):
        print("\nNo git repo found — setting one up...")
        run(["git", "init", "-b", BRANCH])
        run(["git", "remote", "add", "origin", GITHUB_REPO])
        print("  Repo initialised.")
    else:
        # Make sure the remote is pointing to the right place
        existing = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=SCRIPT_DIR, capture_output=True, text=True
        )
        if existing.returncode != 0:
            run(["git", "remote", "add", "origin", GITHUB_REPO])


def generate():
    """Run generate_brochure.py to rebuild index.html first."""
    print("\nStep 1 — Generating index.html ...")
    script = os.path.join(SCRIPT_DIR, "generate_brochure.py")
    result = subprocess.run(
        [sys.executable, script],
        cwd=SCRIPT_DIR, capture_output=True, text=True
    )
    if result.stdout.strip():
        print(f"  {result.stdout.strip()}")
    if result.returncode != 0:
        print(f"  ERROR generating HTML:\n{result.stderr}")
        sys.exit(1)


def deploy():
    check_git()
    setup_repo()
    generate()

    print("\nStep 2 — Staging files ...")
    # Stage everything relevant (skip Python cache folders)
    run(["git", "add",
         "index.html",
         "events_data.json",
         "icons",
         "Images",
         "slideshow_folder",
         "generate_brochure.py",
         "deploy.py"
    ])

    # Commit only if something changed since last commit
    staged = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=SCRIPT_DIR, capture_output=True
    )
    if staged.returncode != 0:
        print("\nStep 3 — Committing ...")
        timestamp = datetime.now().strftime("%d %b %Y, %I:%M %p")
        message = f"{COMMIT_PREFIX} — {timestamp}"
        run(["git", "commit", "-m", message])
    else:
        print("\n  No file changes — skipping commit.")

    # Always push in case a previous push failed
    print("\nStep 4 — Pushing to GitHub ...")
    result = subprocess.run(
        ["git", "push", "--set-upstream", "origin", BRANCH],
        cwd=SCRIPT_DIR, capture_output=True, text=True
    )
    if result.returncode != 0:
        # Remote has unrelated history (e.g. first push from a new machine).
        # Force-push so our local version becomes the live version.
        print("  Remote has different history — force-pushing to overwrite...")
        run(["git", "push", "--force", "--set-upstream", "origin", BRANCH])
    else:
        if result.stdout.strip():
            print(f"  {result.stdout.strip()}")

    print(f"\nDone! Live at: https://great-commission.github.io/gcbc-brochure/")
    print(f"(GitHub Pages can take 1-2 minutes to reflect the change.)\n")


if __name__ == "__main__":
    deploy()
