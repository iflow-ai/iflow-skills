# iflow Skills

> This repository contains [iflow](https://iflow.cn)'s official [Agent Skills](https://agentskills.io) for AI agents. Each skill enables agents to interact with iflow's platform capabilities in a repeatable, standardized way.

## What Are Skills

Skills are folders of instructions, scripts, and resources that AI agents load dynamically to perform specialized tasks. They follow the open [Agent Skills](https://agentskills.io) standard and work across multiple agent platforms.

## Available Skills

| Skill | Description |
|-------|-------------|
| [iflow-nb](skills/iflow-nb/) | Knowledge base management, file import, content generation (PDF/PPT/podcast/mind map/video), web search & deep research, semantic search |

## Quick Start

### 1. Install a Skill

| Agent | Install Method |
|-------|---------------|
| [Claude Code](https://docs.anthropic.com/en/docs/claude-code) | Copy to `~/.claude/skills/` or `.claude/skills/` |
| [OpenClaw](https://github.com/openclaw/openclaw) | `npx clawhub@latest install iflow-nb` |
| [Devin](https://devin.ai) | Commit to `.agents/skills/` in your repo |
| [Windsurf](https://windsurf.com) | Copy to `.windsurf/skills/` |
| [CrewAI](https://www.crewai.com) | `skills=["./skills/iflow-nb"]` |

> For any agent that supports the Agent Skills standard, place the skill directory under the agent's skill discovery path.

### 2. Configure Credentials

Each skill documents its own setup requirements. For example, **iflow-nb** requires an [iflow API key](https://iflow.cn/?open=api-key):

```bash
# Option A - Config file (recommended)
mkdir -p ~/.config/iflow-nb && echo "your_api_key" > ~/.config/iflow-nb/api-key

# Option B - Environment variable
export IFLOW_API_KEY="your_api_key"
```

### 3. Use It

Just talk to your agent naturally:

```
You: Create a KB called "Research Papers", upload these PDFs, and generate a literature review.

You: Search for recent papers on LLM agents and create a summary report.

You: Share the "Research Papers" notebook with my team.
```

## Repository Structure

```
iflow-skill/
├── README.md
├── LICENSE
└── skills/
    └── iflow-nb/           # Knowledge base skill
        ├── SKILL.md         # Skill entry point
        ├── knowledge-base/  # KB & file management APIs
        ├── reports/         # Content generation APIs
        ├── search/          # Web search APIs
        ├── scripts/         # Pipeline scripts (Python)
        ├── examples/        # Usage examples
        └── references/      # Full API reference
```

## Contributing

We welcome contributions! To add a new skill:

1. Create a new directory under `skills/` with a descriptive name
2. Add a `SKILL.md` with the required frontmatter (`name`, `description`)
3. Include scripts, examples, and references as needed
4. Submit a pull request

See the [Agent Skills spec](https://agentskills.io) for the full skill format.

## License

[MIT](LICENSE)
