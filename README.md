# Git Commit History Backfill

Backfill your git repository with a consistent commit history from a start year through today (e.g. 30 commits per day from 2020 onward). Uses `GIT_AUTHOR_DATE` and `GIT_COMMITTER_DATE` so commits appear on the correct dates.

## Requirements

- Python 3.9+
- Git

No extra Python packages required (stdlib only).

## Usage

From this directory (or any folder you want to use as the repo):

```bash
# Default: 2020 through today, 30 commits per day
python backfill_history.py

# Custom start year and commits per day
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
| `--commits-per-day` | 30 | Number of commits per day |
| `--dry-run` | false | Print plan only, no git commands |
| `--seed` | 42 | Random seed for commit messages |
| `--max-days` | (none) | Limit to this many days (for testing) |
| `directory` | `.` | Target repo path |

## Behavior

- If the directory is **not** a git repo, it runs `git init` and creates an initial commit with a README.
- If the directory **is** a repo and has uncommitted changes, the script exits with an error (commit or stash first).
- For each day in the range, it creates the requested number of commits with timestamps spread between 08:00 and 23:59.
- Each commit updates `history.txt` (one line per commit) and uses the corresponding date for both author and committer.

## Note

From 2020 through late Feb 2025 this is ~1,865 days × 30 ≈ **56,000 commits**. Running the script will take a while and the repo will be large. Use `--commits-per-day` or `--dry-run` to experiment first.
