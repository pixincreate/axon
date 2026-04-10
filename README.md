# axon

AI Router - Routes queries to appropriate AI tools based on content classification.

## Usage

```bash
ai "your query"         # Auto-route
ai "query" --dry-run   # Preview routing decision
ai "query" --verbose   # Show detection details
ai "query" --force local/coding/cloud  # Override routing
ai "query" --browser  # Open in browser instead of Playwright
```

## Routing Rules

| Content | Route |
|---------|-------|
| PII (email, phone, secrets) | Local (Ollama gemma4:e4b) |
| Code syntax | OpenCode |
| General | ChatGPT (Playwright auto) |

**Cloud:** Playwright by default (types query, extracts response). Use `--browser` to open manually.

## Installation

```bash
./install.sh
source ~/.zshrc
ai "hello"
```

## Config

`~/.config/ai-router/config.toml` (symlinked to repo config)

Edit patterns in `config.toml`:
- `detection.pii.patterns` - PII regex patterns
- `detection.code.keywords` - Code keywords

## Development

```bash
pip install -r requirements.txt
pytest tests/
flake8 ai_router.py
```