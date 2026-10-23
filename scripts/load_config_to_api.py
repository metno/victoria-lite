#!/usr/bin/env python3

import argparse
import sys
import urllib.error
import urllib.request
from pathlib import Path

# ANSI color codes
RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
NC = "\033[0m"  # No Color

CONFIGS = [
    ("palettes.json", "color-palette", "palette-names"),
    ("unit_equivalent.json", "unit-equivalent", "unit-equivalent-names"),
    ("vector_palette_config.json", "vector-palette", "vector-palette-names"),
    ("unit_style_config.json", "unit-style", "unit-style-names"),
    ("data_source_style.json", "data-source-style", "data-source-style-collection-names"),
]


def load_config(
    config_file: str, endpoint: str, check_name: str, config_dir: Path, api_url: str, force_update: bool
) -> bool:
    full_path = config_dir / config_file

    if not full_path.is_file():
        print(f"{YELLOW}Warning: Config file not found: {full_path}{NC}", file=sys.stderr)
        return False

    if not force_update and check_name:
        check_url = f"{api_url}/{check_name}"
        print(f"Checking if {config_file} config already exists...")
        try:
            with urllib.request.urlopen(check_url) as resp:
                status_code = resp.status
        except urllib.error.HTTPError as e:
            status_code = e.code
        except urllib.error.URLError as e:
            print(f"{YELLOW}Warning: Could not check existing config: {e}{NC}", file=sys.stderr)
            print(f"Proceeding with loading {config_file}...")
            status_code = None

        if status_code == 404:
            print(f"No existing config found for {config_file} (404 - Not Found).")
        elif status_code == 200:
            print(f"{YELLOW}Config already exists for {config_file}. Skipping (use -f/--force to override).{NC}")
            return True
        elif status_code is not None:
            print(f"{YELLOW}Warning: Unexpected HTTP status {status_code} from {check_url}{NC}", file=sys.stderr)
            print(f"Proceeding with loading {config_file}...")

    print(f"{GREEN}Loading {config_file} to {endpoint}...{NC}")
    try:
        data = full_path.read_bytes()
        req = urllib.request.Request(
            f"{api_url}/{endpoint}",
            data=data,
            headers={"Content-Type": "application/json"},
            method="PUT",
        )
        with urllib.request.urlopen(req):
            pass
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        print(f"{RED}Error: Failed to load {config_file}{NC}", file=sys.stderr)
        print(f"{RED}Response: {e}{NC}", file=sys.stderr)
        return False

    print(f"{GREEN}✓ Successfully loaded {config_file}{NC}")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Load configuration files to the Victoria Maps styles API.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "EXAMPLES:\n"
            "  %(prog)s\n"
            "  %(prog)s -c /path/to/config -u http://api.example.com/styles\n"
            "  %(prog)s --config-dir ./config --force\n"
            "  %(prog)s -c /custom/config -u http://localhost:8080/styles -f\n"
        ),
    )
    parser.add_argument("-c", "--config-dir", default="./config", help="Config directory (default: ./config)")
    parser.add_argument(
        "-u",
        "--url",
        default="http://localhost:8000/styles",
        help="API base URL (default: http://localhost:8000/styles)",
    )
    parser.add_argument("-f", "--force", action="store_true", help="Force update even if config already exists")
    args = parser.parse_args()

    config_dir = Path(args.config_dir)
    api_url = args.url
    force_update = args.force

    if not config_dir.is_dir():
        print(f"{RED}Error: Config directory does not exist: {config_dir}{NC}", file=sys.stderr)
        sys.exit(1)

    if not force_update:
        print("Checking API connectivity...")
        try:
            with urllib.request.urlopen(f"{api_url}/palette-names") as resp:
                status_code = resp.status
        except urllib.error.HTTPError as e:
            status_code = e.code
        except urllib.error.URLError as e:
            print(f"{RED}Error: Failed to connect to API at {api_url}: {e}{NC}", file=sys.stderr)
            sys.exit(1)
        if status_code not in (200, 404):
            print(f"{RED}Error: Failed to connect to API at {api_url} (HTTP {status_code}){NC}", file=sys.stderr)
            sys.exit(1)
        print("API is reachable.")
    else:
        print(f"{YELLOW}Force update enabled. Loading configuration files...{NC}")

    failed = []
    for config_file, endpoint, check_name in CONFIGS:
        print()
        if not load_config(config_file, endpoint, check_name, config_dir, api_url, force_update):
            failed.append(config_file)

    print()
    if failed:
        print(f"{RED}Error: The following configs failed to upload: {', '.join(failed)}{NC}", file=sys.stderr)
        sys.exit(1)
    print(f"{GREEN}All configuration files loaded successfully!{NC}")


if __name__ == "__main__":
    main()
