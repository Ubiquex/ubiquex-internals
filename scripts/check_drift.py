#!/usr/bin/env python3
"""UBI-191 sync-drift check.

This site mirrors ubiquex's docs/architecture.md, docs/schema.md, and
docs/plan.md as distilled narrative prose, not a copy. sync-state.json
records the ubiquex commit each was last reviewed against. This script
clones ubiquex fresh, checks whether any of those files gained real
commits since, and reports the drift so a person reviews and re-syncs
the narrative side -- it never regenerates or edits content itself,
matching the coverage-watch.yml precedent in ubiquex-docs (surface,
never silently fix).

Usage: check_drift.py --sync-state sync-state.json --ubiquex-clone <path>
Exit 0: no drift. Exit 1: real drift found. Exit 2: could not run.
"""
import argparse
import json
import subprocess
import sys


def git_log_since(repo_dir, sha, path):
    result = subprocess.run(
        ["git", "-C", repo_dir, "log", "--format=%H %s", f"{sha}..HEAD", "--", path],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git log failed for {path}: {result.stderr}")
    lines = [l for l in result.stdout.splitlines() if l.strip()]
    return lines


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sync-state", required=True)
    parser.add_argument("--ubiquex-clone", required=True, help="path to a real, up-to-date ubiquex checkout")
    args = parser.parse_args()

    try:
        sync_state = json.load(open(args.sync_state))
    except (OSError, json.JSONDecodeError) as e:
        print(f"could not read {args.sync_state}: {e}", file=sys.stderr)
        return 2

    drift = {}
    for path, sha in sync_state.items():
        try:
            commits = git_log_since(args.ubiquex_clone, sha, path)
        except RuntimeError as e:
            print(str(e), file=sys.stderr)
            return 2
        if commits:
            drift[path] = commits

    if not drift:
        print("no drift: every mirrored source file matches its recorded sync-state.json commit")
        return 0

    print(f"drift found in {len(drift)} of {len(sync_state)} mirrored source files:")
    for path, commits in drift.items():
        print(f"\n{path} (recorded: {sync_state[path]}), {len(commits)} new commit(s):")
        for c in commits:
            print(f"  {c}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
