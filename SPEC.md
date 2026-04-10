# AI Router - Specification Document

## 1. Project Overview

**Project Name:** ai-router  
**Type:** CLI Tool (Python)  
**Core Functionality:** Automatically route user queries to the appropriate AI tool based on content classification (sensitive/coding/general)  
**Target Users:** Developers who use multiple AI tools (Ollama, OpenCode, ChatGPT, Copilot)

---

## 2. Routing Rules

### 2.1 Classification Categories

| Category | Trigger Conditions | Target Tool |
|----------|-------------------|-------------|
| **SENSITIVE** | Contains PII (emails, phones, IDs, financial, medical, secrets) | Ollama (local) |
| **CODING** | Contains code syntax (def, class, function, import, {}, etc.) | OpenCode |
| **GENERAL** | Everything else | ChatGPT Web |
| **FALLBACK** | Uncertainty | Ollama (local) |

### 2.2 PII Detection Patterns

```python
# Phone numbers (various formats)
r"\b\d{10}\b"                           # 1234567890
r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b"   # 123-456-7890

# Email
r"\b[\w\.-]+@[\w\.-]+\.\w{2,}\b"

# Secrets/Keys
r"\b(?:api_key|apikey|api-key|secret|password|passwd|pwd)\s*[:=]\s*['\"]?\S+['\"]?"
r"\b(?:Bearer\s+)?[A-Za-z0-9_-]{20,}\b"  # JWT tokens, long API keys

# Government IDs (generic patterns)
r"\b\d{12}\b"              # Aadhaar-like
r"\b[A-Z]{1,2}\d{6,9}\b"  # Passport-like

# Financial
r"\b\d{16}\b"              # Credit card
r"\b(?:INR|USD|EUR|GBP)\s*\d+[\d,]*(?:\.\d{2})?\b"

# Names (common patterns)
r"\b(?:Mr\.|Ms\.|Mrs\.|Dr\.)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b"
```

### 2.3 Code Detection Patterns

```python
CODE_KEYWORDS = [
    "def ", "class ", "function ", "import ", "from ",
    "const ", "let ", "var ", "return ", "export ",
    "public ", "private ", "protected ", "async ", "await ",
    "interface ", "type ", "enum ", "struct ", "impl ",
    "fn ", "pub ", "mod ", "use ", "package ", "namespace ",
    "<?php", "<?=", "<%", "%>", "<!", "-->",
    "SELECT ", "INSERT ", "UPDATE ", "DELETE ", "CREATE TABLE",
    "{", "}", "();", "=>", "->", "::", "##"
]
```

---

## 3. Technical Specification

### 3.1 File Structure

```
ai-router/
├── ai_router/
│   ├── __init__.py
│   ├── classifier.py      # PII & code detection
│   ├── router.py          # Routing logic
│   ├── runners.py         # Tool execution
│   └── cli.py             # CLI entry point
├── pyproject.toml
├── setup.sh               # Installation script
└── README.md
```

### 3.2 CLI Interface

```bash
# Basic usage
ai "your query here"

# With flags
ai "query" --force local    # Force specific route
ai "query" --dry-run       # Show routing decision only
ai "query" --verbose       # Show detection details

# Install
./install.sh              # Add to PATH
```

### 3.3 Configuration

Config file: `~/.ai-router/config.yaml`

```yaml
tools:
  local:
    model: "gemma"
    command: "ollama run {model}"
  coding:
    command: "opencode"
  cloud:
    url: "https://chat.openai.com"

routing:
  priority:
    - sensitive
    - coding
    - general
  fallback: "local"
```

---

## 4. Acceptance Criteria

1. **PII Detection:** Correctly identifies emails, phone numbers, API keys/secrets in text
2. **Code Detection:** Correctly identifies code snippets vs natural language
3. **Routing:** Routes to correct tool based on classification
4. **CLI:** Executable from terminal with proper argument parsing
5. **Extensibility:** Easy to add new detection patterns or tools
6. **Fallback:** Uncertain queries default to local (Ollama)
7. **Privacy:** Sensitive data never leaves local machine

---

## 5. Implementation Notes

- Use `argparse` for CLI
- Use `pyyaml` for config
- Use `subprocess` for tool execution
- Include `--dry-run` to preview routing decision
- Include `--force` to override automatic routing
- Support piped input: `echo "query" | ai`
