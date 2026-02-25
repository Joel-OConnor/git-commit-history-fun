#!/usr/bin/env python3
"""
Backfill git commit history from a start year through today with a fixed number
of commits per day. Uses GIT_AUTHOR_DATE and GIT_COMMITTER_DATE to set commit times.
"""

import argparse
import os
import random
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional


def run_git(args: List[str], cwd: Path, env: Optional[dict] = None) -> subprocess.CompletedProcess:
    result = subprocess.run(
        ["git"] + args,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
    )
    return result


def is_git_repo(cwd: Path) -> bool:
    return (cwd / ".git").is_dir()


def init_repo(cwd: Path) -> None:
    run_git(["init"], cwd=cwd)
    if not (cwd / "README.md").exists():
        (cwd / "README.md").write_text("# Git Commit History\n\nBackfilled commit history.\n")
        run_git(["add", "README.md"], cwd=cwd)
        run_git(["commit", "-m", "Initial commit"], cwd=cwd)


def commits_for_day(base_date: datetime, count: int) -> List[datetime]:
    """Return `count` commit timestamps spread across the given day."""
    start = base_date.replace(hour=8, minute=0, second=0, microsecond=0)
    end = base_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    span_seconds = (end - start).total_seconds()
    if count <= 1:
        return [start] if count else []
    steps = span_seconds / (count - 1)
    return [start + timedelta(seconds=steps * i) for i in range(count)]


def make_commit(cwd: Path, commit_time: datetime, message: str, data_path: Path, index: int) -> bool:
    """Append a line to the data file and commit with the given timestamp."""
    ts = commit_time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"{ts} | commit #{index}\n"
    content = data_path.read_text(encoding="utf-8") if data_path.exists() else ""
    data_path.write_text(content + line, encoding="utf-8")

    env = {
        **os.environ,
        "GIT_AUTHOR_DATE": ts,
        "GIT_COMMITTER_DATE": ts,
    }
    run_git(["add", str(data_path.name)], cwd=cwd)
    result = run_git(
        ["commit", "-m", message],
        cwd=cwd,
        env=env,
    )
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
    return result.returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Backfill git history with N commits per day from start year to today."
    )
    parser.add_argument(
        "--start-year",
        type=int,
        default=2020,
        help="First year to generate commits (default: 2020)",
    )
    parser.add_argument(
        "--commits-per-day",
        type=int,
        default=30,
        help="Number of commits per day (default: 30)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be done without running git",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for commit message variety (default: 42)",
    )
    parser.add_argument(
        "--max-days",
        type=int,
        default=None,
        help="Limit to this many days (for testing; default: no limit)",
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Repository directory (default: current directory)",
    )
    args = parser.parse_args()

    cwd = Path(args.directory).resolve()
    if not cwd.is_dir():
        print(f"Error: directory does not exist: {cwd}", file=sys.stderr)
        return 1

    if not args.dry_run:
        if not is_git_repo(cwd):
            init_repo(cwd)
        elif run_git(["status", "--short"], cwd=cwd).stdout.strip():
            print("Error: working tree has uncommitted changes. Commit or stash them first.", file=sys.stderr)
            return 1

    data_path = cwd / "history.txt"
    if not data_path.exists() and not args.dry_run:
        data_path.write_text("")

    today = datetime.now().date()
    start_date = datetime(args.start_year, 1, 1).date()
    total_days = (today - start_date).days + 1
    if args.max_days is not None:
        total_days = min(total_days, args.max_days)
    total_commits = total_days * args.commits_per_day

    messages = [
        "Update config",
        "Fix typo",
        "Refactor module",
        "Add tests",
        "Docs",
        "Bump version",
        "Cleanup",
        "Optimize",
        "WIP",
        "Minor fix",
    ]
    random.seed(args.seed)

    print(f"Planned: {total_days} days, {total_commits} commits ({args.commits_per_day}/day)")
    if args.dry_run:
        print("Dry run — no git commands will be run.")
        return 0

    day_count = 0
    commit_count = 0
    for day_offset in range(total_days):
        base = start_date + timedelta(days=day_offset)
        base_dt = datetime.combine(base, datetime.min.time())
        times = commits_for_day(base_dt, args.commits_per_day)
        for i, t in enumerate(times):
            msg = random.choice(messages) + f" ({t.strftime('%Y-%m-%d %H:%M')})"
            make_commit(cwd, t, msg, data_path, commit_count + 1)
            commit_count += 1
        day_count += 1
        if day_count % 100 == 0:
            print(f"  {day_count} days, {commit_count} commits...")

    print(f"Done. {day_count} days, {commit_count} commits.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
