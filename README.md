# Git Commit History Backfill

Backfill your git repository with a consistent commit history from a start year through today. Ensures **each day has at least** a given number of commits (e.g. 30) by adding only as many as needed. Uses `GIT_AUTHOR_DATE` and `GIT_COMMITTER_DATE` so commits appear on the correct dates.

## Requirements

- Python 3.9+
- Git

No extra Python packages required (stdlib only).

## Usage

From this directory (or any folder you want to use as the repo):

```bash
# Default: 2020 through today, ensure at least 30 commits per day
python backfill_history.py

# Custom start year and minimum commits per day
python backfill_history.py --start-year 2019 --commits-per-day 10

# See what would be done without running git
python backfill_history.py --dry-run

# Test with just 2 days first
python backfill_history.py --max-days 2

# Run in a specific directory
python backfill_history.py /path/to/repo
```

### Options

| Option | Default | Description |
|--------|--------|-------------|
| `--start-year` | 2020 | First year to generate commits |
| `--commits-per-day` | 30 | Minimum commits per day; only adds enough to reach this |
| `--dry-run` | false | Print plan only, no git commands |
| `--seed` | 42 | Random seed for commit messages |
| `--max-days` | (none) | Limit to this many days (for testing) |
| `directory` | `.` | Target repo path |

## Behavior

- If the directory is **not** a git repo, it runs `git init` and creates an initial commit with a README.
- If the directory **is** a repo and has uncommitted changes, the script exits with an error (commit or stash first).
- For each day in the range, it checks how many commits already exist on that day. It then adds only enough commits so the day has at least the requested minimum (e.g. 30). Days that already meet the minimum are left unchanged.
- Each commit updates `history.txt` (one line per commit) and uses the corresponding date for both author and committer.

## Note

From 2020 through late Feb 2025 this is ~1,865 days. If every day needed the full minimum, that would be ~56,000 commits. The script only adds what’s needed, so re-running it or using a repo that already has some history will add fewer commits.
