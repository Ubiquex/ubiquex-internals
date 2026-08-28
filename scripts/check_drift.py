#!/usr/bin/env python3
"""UBI-191 sync-drift check.

This site mirrors real design-doc prose and, since the Provider system
and SDK/codegen sections, real source-code comments too -- from ubiquex
and now ubx-provider-dynamic -- as distilled narrative, not a copy.
sync-state.json records, per repo, the commit each mirrored file was
last reviewed against. This script clones each repo fresh, checks
whether any tracked file gained real commits since, and reports the
drift so a person reviews and re-syncs the narrative side -- it never
regenerates or edits content itself, matching the coverage-watch.yml
precedent in ubiquex-docs (surface, never silently fix).

sync-state.json shape: {"<repo-name>": {"<path>": "<sha>", ...}, ...}.
Each repo name must be a real, public github.com/Ubiquex/<repo-name>.

Usage: check_drift.py --sync-state sync-state.json --clone-dir <dir>
  --clone-dir is a directory this script clones every tracked repo into
  (as --clone-dir/<repo-name>), or reuses if already present and a real
  git checkout of the matching repo.
Exit 0: no drift. Exit 1: real drift found. Exit 2: could not run.
"""
import argparse
import json
import os
import subprocess
import sys


def ensure_clone(repo_name, clone_dir):
    repo_path = os.path.join(clone_dir, repo_name)
    if os.path.isdir(os.path.join(repo_path, ".git")):
        result = subprocess.run(["git", "-C", repo_path, "fetch", "origin", "main"], capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"git fetch failed for {repo_name}: {result.stderr}")
        result = subprocess.run(["git", "-C", repo_path, "reset", "--hard", "origin/main"], capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"git reset failed for {repo_name}: {result.stderr}")
        return repo_path
    result = subprocess.run(
        ["git", "clone", f"https://github.com/Ubiquex/{repo_name}.git", repo_path],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git clone failed for {repo_name}: {result.stderr}")
    return repo_path


def git_log_since(repo_dir, sha, path):
    result = subprocess.run(
        ["git", "-C", repo_dir, "log", "--format=%H %s", f"{sha}..HEAD", "--", path],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git log failed for {path}: {result.stderr}")
    return [l for l in result.stdout.splitlines() if l.strip()]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sync-state", required=True)
    parser.add_argument("--clone-dir", required=True, help="directory to clone/refresh each tracked repo into")
    args = parser.parse_args()

    try:
        sync_state = json.load(open(args.sync_state))
    except (OSError, json.JSONDecodeError) as e:
        print(f"could not read {args.sync_state}: {e}", file=sys.stderr)
        return 2

    os.makedirs(args.clone_dir, exist_ok=True)

    total_tracked = 0
    drift = {}
    for repo_name, files in sync_state.items():
        try:
            repo_path = ensure_clone(repo_name, args.clone_dir)
        except RuntimeError as e:
            print(str(e), file=sys.stderr)
            return 2
        for path, sha in files.items():
            total_tracked += 1
            try:
                commits = git_log_since(repo_path, sha, path)
            except RuntimeError as e:
                print(str(e), file=sys.stderr)
                return 2
            if commits:
                drift[f"{repo_name}/{path}"] = commits

    if not drift:
        print(f"no drift: every one of {total_tracked} mirrored source files matches its recorded sync-state.json commit")
        return 0

    print(f"drift found in {len(drift)} of {total_tracked} mirrored source files:")
    for key, commits in drift.items():
        print(f"\n{key}, {len(commits)} new commit(s):")
        for c in commits:
            print(f"  {c}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
