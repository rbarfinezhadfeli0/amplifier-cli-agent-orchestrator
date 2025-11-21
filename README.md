# Amplifier CLI Agent Orchestrator

> **Combined system**: Multi-agent orchestration with AI-powered knowledge synthesis

This repository combines two powerful systems for AI-driven development:

1. **CLI Agent Orchestrator (CAO)** - Multi-agent orchestration system using tmux and MCP
2. **Amplifier** - Metacognitive AI development system with knowledge synthesis

## 🎯 Overview

### CLI Agent Orchestrator

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/awslabs/cli-agent-orchestrator)

A lightweight orchestration system for managing multiple AI agent sessions in tmux terminals, enabling multi-agent collaboration via Model Context Protocol (MCP) servers.

**Key Capabilities:**
- **Hierarchical orchestration** – Supervisor agents coordinate specialized worker agents
- **Session-based isolation** – Isolated tmux sessions with seamless MCP communication
- **Intelligent task delegation** – Three orchestration patterns: Handoff, Assign, Send Message
- **Flow scheduling** – Cron-like scheduling for automated workflows
- **Context preservation** – Efficient context management across agents
- **Advanced CLI integration** – Full access to Claude Code, Amazon Q, and Kiro CLI features

### Amplifier

> [!CAUTION]
> This project is a research demonstrator. It is in early development and may change significantly. Using permissive AI tools in your repository requires careful attention to security considerations and human supervision. Use with caution, at your own risk.

A coordinated development system that transforms expertise into reusable AI tools. Describe your thinking process ("metacognitive recipes"), and Amplifier builds tools that execute them reliably.

**Key Capabilities:**
- **Knowledge synthesis pipeline** – Extract concepts, relationships, patterns from content
- **Claude Code SDK integration** – Advanced automation and workflow management
- **25+ specialized AI agents** – Pre-built agents for various development tasks
- **20+ slash commands** – Document-Driven Development workflows
- **Knowledge graphs** – Visual representation and inference of knowledge relationships
- **Parallel development** – Git worktrees for simultaneous experiments

## 🚀 Quick Start

### Prerequisites

**Required:**
- Python 3.11+
- tmux 3.3+ (for CAO)
- uv (Python package manager)
- Git

**Optional (for Amplifier features):**
- Node.js (any recent version)
- pnpm (package manager)

### Installation

#### 1. Install System Dependencies

**tmux (required for CAO):**
```bash
bash <(curl -s https://raw.githubusercontent.com/awslabs/cli-agent-orchestrator/refs/heads/main/tmux-install.sh)
```

**uv (Python package manager):**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Node.js and pnpm (optional, for Amplifier features):**
```bash
# Mac
brew install node pnpm

# Ubuntu/Debian/WSL
sudo apt install nodejs npm
npm install -g pnpm
pnpm setup && source ~/.bashrc
```

#### 2. Clone and Install

```bash
# Clone this repository
git clone <repository-url> amplifier-cli-agent-orchestrator
cd amplifier-cli-agent-orchestrator

# Install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac/WSL
# .venv\Scripts\Activate.ps1  # Windows PowerShell
```

#### 3. Configure Environment

```bash
# Copy environment template (for Amplifier features)
cp .env.example .env

# Edit .env and add your API keys:
# ANTHROPIC_API_KEY=your_key_here
# OPENAI_API_KEY=your_key_here (optional)
```

## 📖 Using CLI Agent Orchestrator

### Installing Agents

CAO supports installing agents from multiple sources:

```bash
# Install built-in agents
cao install code_supervisor
cao install developer
cao install reviewer

# Install from local file
cao install ./my-custom-agent.md

# Install from URL
cao install https://example.com/agents/custom-agent.md
```

### Launching Agents

```bash
# Start the CAO server
cao-server

# In a new terminal, launch an agent
cao launch code_supervisor
```

### Orchestration Patterns

**Handoff (synchronous):**
```python
# Transfer task and wait for completion
handoff(terminal_id="agent-1", task="Review the authentication code")
```

**Assign (asynchronous):**
```python
# Spawn parallel tasks
assign(terminal_id="agent-2", task="Analyze database performance")
```

**Send Message:**
```python
# Direct agent-to-agent communication
send_message(terminal_id="agent-3", message="Status update needed")
```

### Scheduled Flows

```bash
# List available flows
cao flow list

# Start a flow
cao flow start my-workflow

# Stop a flow
cao flow stop my-workflow
```

For detailed CAO documentation, see [CODEBASE.md](CODEBASE.md) and [DEVELOPMENT.md](DEVELOPMENT.md).

## 🎨 Using Amplifier

### Start Claude Code

```bash
claude
```

### Create Your First Tool

1. **Identify a task** you want to automate
2. **Describe your thinking process** in natural language
3. **Let Amplifier build the tool** based on your description
4. **Test and refine** the tool iteratively
5. **Reuse and combine** tools for complex workflows

### Key Amplifier Commands

Amplifier provides 20+ slash commands for various workflows. Some examples:

```bash
# Document-Driven Development
/ddd-spec    # Create technical specification
/ddd-impl    # Implement from specification
/ddd-test    # Generate tests
/ddd-sync    # Sync docs with code

# Knowledge synthesis
/synthesize  # Extract and synthesize knowledge
/graph       # Generate knowledge graph

# Development workflows
/review      # Code review workflow
/refactor    # Refactoring workflow
```

For complete Amplifier documentation, see:
- [AMPLIFIER_VISION.md](AMPLIFIER_VISION.md) - Strategic vision
- [AGENTS.md](AGENTS.md) - AI agent guidance (30KB)
- [CLAUDE.md](CLAUDE.md) - Claude-specific instructions
- [DISCOVERIES.md](DISCOVERIES.md) - Pattern discoveries
- [Makefile](Makefile) - 100+ make targets

## 🔗 Integration: CAO + Amplifier

The combined system enables powerful workflows:

### Scenario 1: Distributed Knowledge Synthesis

Use CAO to orchestrate multiple Amplifier agents working on different knowledge domains in parallel:

```python
# Supervisor agent coordinates parallel synthesis
assign(terminal_id="synthesizer-1", task="Synthesize AI research papers")
assign(terminal_id="synthesizer-2", task="Synthesize development best practices")
assign(terminal_id="synthesizer-3", task="Synthesize security patterns")

# Merge results when complete
handoff(terminal_id="merger", task="Combine all synthesized knowledge")
```

### Scenario 2: Hierarchical Development

Use CAO's hierarchical structure with Amplifier's specialized agents:

```python
# Supervisor delegates to specialized Amplifier agents
handoff(terminal_id="spec-writer", task="Create API specification using /ddd-spec")
handoff(terminal_id="implementer", task="Implement using /ddd-impl")
handoff(terminal_id="tester", task="Generate tests using /ddd-test")
handoff(terminal_id="reviewer", task="Review code using /review")
```

### Scenario 3: Scheduled Knowledge Updates

Use CAO flows to run Amplifier knowledge synthesis on a schedule:

```bash
# Create a flow that runs daily knowledge synthesis
cao flow create daily-learning \
  --schedule "0 9 * * *" \
  --agent knowledge-synthesizer \
  --task "Synthesize yesterday's discoveries"
```

## 📁 Repository Structure

```
amplifier-cli-agent-orchestrator/
├── src/cli_agent_orchestrator/   # CAO source code
│   ├── api/                       # FastAPI server
│   ├── mcp_server/                # MCP server implementation
│   ├── cli/                       # CLI commands
│   ├── services/                  # Business logic
│   ├── providers/                 # CLI tool integrations
│   └── models/                    # Data models
├── amplifier/                     # Amplifier source code
│   ├── knowledge/                 # Knowledge synthesis
│   ├── tools/                     # Pre-built tools
│   ├── agents/                    # AI agent definitions
│   └── utils/                     # Utilities
├── .claude/                       # Claude Code configuration
│   ├── agents/                    # Amplifier agent profiles
│   └── commands/                  # Slash commands
├── docs/                          # CAO documentation
├── docs_amplifier/                # Amplifier documentation
├── test/                          # CAO tests
├── tests_amplifier/               # Amplifier tests
├── scenarios/                     # Example scenarios
├── tools/                         # CLI tools
├── pyproject.toml                 # Combined dependencies
├── Makefile                       # Build and workflow commands
└── README.md                      # This file
```

## 🛠️ Development

### Running Tests

```bash
# Run all tests
pytest

# Run CAO tests only
pytest test/

# Run Amplifier tests only
pytest tests_amplifier/

# Run with coverage
pytest --cov=src --cov=amplifier
```

### Code Quality

```bash
# Format code
black .
isort .

# Lint code
ruff check .

# Type checking
mypy src/
pyright amplifier/
```

### Using Make Commands

Amplifier provides extensive make targets:

```bash
# See all available commands
make help

# Install dependencies
make install

# Run tests
make test

# Code quality checks
make lint

# Knowledge management
make kb-index        # Index knowledge base
make kb-search       # Search knowledge
make kg-build        # Build knowledge graph
```

## 📚 Documentation

### CLI Agent Orchestrator
- [CODEBASE.md](CODEBASE.md) - Architecture overview
- [DEVELOPMENT.md](DEVELOPMENT.md) - Development guide
- [docs/api.md](docs/api.md) - REST API documentation
- [docs/agent-profile.md](docs/agent-profile.md) - Agent profile creation

### Amplifier
- [AMPLIFIER_VISION.md](AMPLIFIER_VISION.md) - Strategic vision and design principles
- [AGENTS.md](AGENTS.md) - Comprehensive AI agent guidance
- [CLAUDE.md](CLAUDE.md) - Claude-specific instructions
- [DISCOVERIES.md](DISCOVERIES.md) - Problem solutions and patterns
- [ROADMAP.md](ROADMAP.md) - Development roadmap
- [docs_amplifier/](docs_amplifier/) - Detailed guides and tutorials

## 🔒 Security

Both systems require careful security consideration:

### CAO Security
- Agents operate in isolated tmux sessions
- MCP communication is localhost-only by default
- Review agent profiles before installation
- See [SECURITY.md](SECURITY.md)

### Amplifier Security
- Uses permissive AI tools that modify code
- Requires human supervision for all operations
- Store API keys securely in .env (never commit)
- Review all AI-generated code before execution
- See [SECURITY.md](SECURITY.md)

## 🤝 Contributing

This is a combined research project. For contribution guidelines:

- **CLI Agent Orchestrator**: See [CONTRIBUTING.md](CONTRIBUTING.md)
- **Amplifier**: Currently not accepting external contributions (early development)

## 📄 License

- **CLI Agent Orchestrator**: Apache-2.0 License
- **Amplifier**: MIT License

See [LICENSE](LICENSE) for details.

## 📞 Support

- [SUPPORT.md](SUPPORT.md) - Getting help and community resources
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) - Community guidelines

## ⚠️ Disclaimer

This combined system is a research demonstrator in active development:

- **Experimental nature**: Both components are evolving rapidly
- **Breaking changes**: APIs and interfaces may change without notice
- **Security considerations**: AI-powered tools require careful supervision
- **Production use**: Not recommended for production environments without thorough testing
- **Risk acceptance**: Use at your own risk with appropriate precautions

## 🙏 Acknowledgments

This project combines:
- [CLI Agent Orchestrator](https://github.com/awslabs/cli-agent-orchestrator) by AWS Labs
- [Amplifier](https://github.com/microsoft/amplifier) by Microsoft Research

Both projects are used under their respective licenses.

---

**Get Started:** Choose your workflow:
- Want multi-agent orchestration? → Start with [CAO Quick Start](#-using-cli-agent-orchestrator)
- Want knowledge synthesis? → Start with [Amplifier Quick Start](#-using-amplifier)
- Want both? → Try the [integration scenarios](#-integration-cao--amplifier)
