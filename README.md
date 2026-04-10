# axon

AI Router - Routes queries to appropriate AI tools based on content classification.

## Usage

```bash
ai "your query"           # Auto-route
ai "query" --dry-run       # Preview routing
ai "query" --verbose      # Show detection
ai "query" --force local   # Override routing
ai "query" --playwright    # Auto ChatGPT via browser
```

## Installation

```bash
./install.sh
source ~/.zshrc
```

## Routing Rules

- **Sensitive** (PII, secrets) → Local (Ollama gemma4:e4b)
- **Coding** → OpenCode
- **General** → ChatGPT

Config: `~/.config/ai-router/config.toml`