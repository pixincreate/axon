#!/usr/bin/env python3
"""AI Router - Route queries to appropriate AI tools."""

import re
import sys
import argparse
import subprocess
from pathlib import Path
from typing import Tuple, List, Dict, Any

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None

SCRIPT_DIR = Path(__file__).parent
CONFIG_PATH = SCRIPT_DIR / "config.toml"
USER_CONFIG = Path.home() / ".config" / "ai-router" / "config.toml"

DEFAULT_CONFIG: Dict[str, Any] = {}

PII_PATTERNS = []
CODE_KEYWORDS = []


def load_config() -> Dict[str, Any]:
    if tomllib is None:
        print(
            "Warning: tomllib/tomli not installed. Using default config.",
            file=sys.stderr,
        )
        return DEFAULT_CONFIG

    config_file = USER_CONFIG if USER_CONFIG.exists() else CONFIG_PATH

    if not config_file.exists():
        print(
            f"Warning: Config not found at {config_file}. Using defaults.",
            file=sys.stderr,
        )
        return DEFAULT_CONFIG

    with open(config_file, "rb") as f:
        return tomllib.load(f)


def compile_patterns(config: Dict[str, Any]) -> None:
    global PII_PATTERNS, CODE_KEYWORDS

    detection = config.get("detection", {})
    pii_list = detection.get("pii", {}).get("patterns", [])
    code_list = detection.get("code", {}).get("keywords", [])

    PII_PATTERNS = [
        (re.compile(p["regex"], re.IGNORECASE), p["label"]) for p in pii_list
    ]
    CODE_KEYWORDS = code_list


def detect_pii(text: str) -> Tuple[bool, List[str]]:
    detected = []
    for pattern, label in PII_PATTERNS:
        if pattern.search(text):
            detected.append(label)
    return len(detected) > 0, list(set(detected))


def detect_code(text: str) -> Tuple[bool, List[str]]:
    detected = [k for k in CODE_KEYWORDS if k in text]
    return len(detected) > 0, detected


def classify(query: str, verbose: bool = False) -> str:
    has_pii, pii_types = detect_pii(query)
    is_code, code_types = detect_code(query)

    if verbose:
        pii_msg = "[DEBUG] No PII"
        if pii_types:
            pii_msg = f"[DEBUG] PII: {pii_types}"
        code_msg = "[DEBUG] No code"
        if code_types:
            code_msg = f"[DEBUG] Code: {code_types}"
        print(pii_msg)
        print(code_msg)

    if has_pii:
        return "sensitive"
    elif is_code:
        return "coding"
    return "general"


def get_tool_for_route(route: str, config: Dict[str, Any]) -> Tuple[str, str]:
    tools = config.get("tools", {})

    if route == "sensitive":
        local = tools.get("local", {})
        cmd = local.get("command", "ollama run {model}")
        model = local.get("model", "gemma4:e4b")
        return "local", cmd.format(model=model)
    elif route == "coding":
        return "coding", tools.get("coding", {}).get("command", "opencode")
    elif route == "general":
        url = tools.get("cloud", {}).get("url", "https://chat.openai.com")
        return "cloud", url
    else:
        local = tools.get("local", {})
        cmd = local.get("command", "ollama run {model}")
        model = local.get("model", "gemma4:e4b")
        return "local", cmd.format(model=model)


def run_local(command: str, query: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        command.split(),
        input=query.encode(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def run_coding(command: str, query: str) -> None:
    subprocess.Popen(command.split(), stdin=subprocess.PIPE)
    print(f"-> Opened {command} for coding task")


def run_cloud(url: str) -> None:
    subprocess.run(["open", url])
    print(f"-> Opened {url} in browser")


def run_cloud_playwright(url: str, query: str) -> str:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(
            "Error: playwright not installed. Run: pip install playwright",
            file=sys.stderr,
        )
        print("Falling back to browser open.", file=sys.stderr)
        run_cloud(url)
        return ""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url)

        msg = "-> Opening ChatGPT (no login needed), sending query..."
        print(msg)

        page.wait_for_selector("textarea", timeout=30000)
        page.fill("textarea", query)
        page.click("button:has-text('Send')")

        print("-> Waiting for response...")
        sel = "[data-message-author-role='assistant']"
        page.wait_for_selector(sel, timeout=60000)

        response = page.locator(sel).last.inner_text()
        browser.close()

        return response


def main():
    parser = argparse.ArgumentParser(
        description="AI Router - Route queries to appropriate AI tools"
    )
    parser.add_argument("query", nargs="?", help="Query to route")
    parser.add_argument(
        "-f",
        "--force",
        choices=["local", "coding", "cloud"],
        help="Force specific route",
    )
    parser.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        help="Show routing decision without executing",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Show detection details"
    )
    parser.add_argument(
        "-i", "--interactive", action="store_true", help="Interactive mode"
    )
    parser.add_argument(
        "-p",
        "--playwright",
        action="store_true",
        help="Use Playwright for cloud queries",
    )

    args = parser.parse_args()

    if not sys.stdin.isatty():
        query = sys.stdin.read().strip()
    elif args.query:
        query = args.query
    elif args.interactive:
        query = input("Enter your prompt: ").strip()
    else:
        parser.print_help()
        return

    if not query:
        print("Error: Empty query", file=sys.stderr)
        return 1

    config = load_config()
    compile_patterns(config)

    if args.force:
        route = args.force
        if route == "cloud":
            route = "general"
    else:
        route = classify(query, verbose=args.verbose)

    tool_name, tool_cmd = get_tool_for_route(route, config)

    route_names = {
        "sensitive": "LOCAL (Ollama)",
        "coding": "CODING (OpenCode)",
        "general": "CLOUD (ChatGPT)",
    }
    print(f"-> Routing to: {route_names.get(route, route)}")

    if args.dry_run:
        return 0

    if tool_name == "local":
        result = run_local(tool_cmd, query)
        if result.returncode == 0:
            print(result.stdout.decode())
        else:
            print(f"Error: {result.stderr.decode()}", file=sys.stderr)
    elif tool_name == "coding":
        run_coding(tool_cmd, query)
    else:
        if args.playwright:
            response = run_cloud_playwright(tool_cmd, query)
            if response:
                print(response)
        else:
            run_cloud(tool_cmd)

    return 0


if __name__ == "__main__":
    sys.exit(main())
