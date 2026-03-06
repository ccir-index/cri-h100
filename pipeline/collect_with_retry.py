"""
CRI Collection Wrapper — Auto-retry for thin H100 SXM observation counts
=========================================================================
Runs collect.py, then checks the h100-sxm-us observation count from the
day's meta.json. If fewer than MIN_OBSERVATIONS qualifying observations
were recorded, waits RETRY_WAIT_MINUTES and tries again.

Retries up to MAX_RETRIES times. Each retry overwrites the day's CSV and
meta.json with a fresh collection (same behaviour as running collect.py
manually a second time).

Usage:
    python collect_with_retry.py [--date YYYY-MM-DD] [--data-dir PATH] [--auto-push]

    --auto-push   After hitting threshold, git commit and push data/ to origin/main.
                  Use for local Task Scheduler runs so the best dataset is always
                  in the repo before the GitHub Actions workflow fires.

Typical use: replace your daily Task Scheduler invocation of collect.py with
this script, adding --auto-push so local data lands in the repo ahead of GHA.
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MIN_OBSERVATIONS   = 8     # Threshold — below this, retry
MAX_RETRIES        = 3     # Maximum additional attempts after the first run
RETRY_WAIT_MINUTES = 30    # Wait between retries

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def read_h100_obs_count(data_dir: Path, date_str: str) -> int:
    """Read h100-sxm-us observation count from today's meta.json."""
    meta_path = data_dir / "h100-sxm-us" / f"{date_str}.meta.json"
    if not meta_path.exists():
        return 0
    try:
        with open(meta_path) as f:
            meta = json.load(f)
        return meta.get("price_summary", {}).get("n", 0)
    except (json.JSONDecodeError, KeyError):
        return 0


def run_collect(collect_script: Path, extra_args: list) -> int:
    """Run collect.py and return exit code."""
    cmd = [sys.executable, str(collect_script)] + extra_args
    result = subprocess.run(cmd)
    return result.returncode


def auto_push(repo_root: Path, date_str: str, n: int) -> None:
    """Commit data/ and push to origin/main."""
    print("\nAuto-push enabled — committing data/ to origin/main...")
    cmds = [
        ["git", "add", "data/"],
        ["git", "commit", "-m",
         f"[collect] {date_str} -- daily snapshot (local auto-push, {n} obs)"],
        ["git", "push", "origin", "main"],
    ]
    for cmd in cmds:
        result = subprocess.run(cmd, cwd=str(repo_root))
        if result.returncode != 0:
            print(f"WARNING: Command failed: {' '.join(cmd)}")
            print("  Check PAT auth — run: git remote -v  and verify token is embedded in URL.")
            return
    print(f"✓ Pushed to origin/main ({n} obs)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Run collect.py with automatic retry if H100 SXM obs < threshold"
    )
    parser.add_argument("--date",      default=datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    parser.add_argument("--data-dir",  default=None)
    parser.add_argument("--auto-push", action="store_true",
                        help="Git commit and push data/ after successful collection")
    args, unknown = parser.parse_known_args()

    date_str = args.date

    # Resolve paths — this script should live in the pipeline/ subdirectory
    script_dir     = Path(__file__).resolve().parent
    repo_root      = script_dir.parent
    collect_script = script_dir / "collect.py"

    if not collect_script.exists():
        print(f"ERROR: collect.py not found at {collect_script}")
        sys.exit(1)

    # data_dir: use --data-dir if provided, else repo_root/data
    if args.data_dir:
        data_dir   = Path(args.data_dir)
        extra_args = ["--date", date_str, "--data-dir", str(data_dir)]
    else:
        data_dir   = repo_root / "data"
        extra_args = ["--date", date_str]

    # Pass any extra unknown args through to collect.py
    extra_args += unknown

    attempt = 0
    threshold_met = False

    while True:
        attempt += 1
        print(f"\n{'=' * 60}")
        print(f"Collection attempt {attempt} of {MAX_RETRIES + 1} — {date_str}")
        print(f"{'=' * 60}")

        rc = run_collect(collect_script, extra_args)

        if rc != 0:
            print(f"\nWARNING: collect.py exited with code {rc}.")

        n = read_h100_obs_count(data_dir, date_str)
        print(f"\nH100 SXM qualifying observations: {n}")

        if n >= MIN_OBSERVATIONS:
            print(f"✓ Threshold met ({n} >= {MIN_OBSERVATIONS}). Done.")
            threshold_met = True
            break

        if attempt > MAX_RETRIES:
            print(f"\nWARNING: Exhausted {MAX_RETRIES} retries. "
                  f"Final count: {n} observations (below threshold of {MIN_OBSERVATIONS}).")
            print("  Proceeding with low-confidence data. "
                  "Low-confidence flag will be set in calculate.py output.")
            break

        print(f"\n  Below threshold ({n} < {MIN_OBSERVATIONS}). "
              f"Retrying in {RETRY_WAIT_MINUTES} minutes "
              f"(attempt {attempt + 1} of {MAX_RETRIES + 1})...")
        print(f"  Next attempt at: "
              f"{datetime.now().strftime('%H:%M:%S')} + {RETRY_WAIT_MINUTES}m")

        time.sleep(RETRY_WAIT_MINUTES * 60)

    # Auto-push: only on threshold success. Low-confidence data is intentionally
    # left for the GHA workflow to handle and flag.
    if args.auto_push:
        if threshold_met:
            auto_push(repo_root, date_str, n)
        else:
            print("\nAuto-push skipped — threshold not met. "
                  "GHA workflow will handle low-confidence commit.")


if __name__ == "__main__":
    main()
