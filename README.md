# 🤖 Build Your Own Agent — Starter Kit

A hands-on starting point for building your **own** AI agent — one that remembers things,
has a personality, and can be extended with new skills. It runs on **free and open**
tools, so you can build all day without a bill.

You don't need to be a hardcore coder. If you can edit a text file and run a command in a
terminal, you can build an agent. This kit gives you a working agent on minute one, then
shows you how to make it yours.

---

## What even *is* an agent?

Strip away the hype and an AI agent is a **loop** with five parts:

| Part | What it is | In this kit |
|---|---|---|
| 🧠 **Model** | The brain that reasons and writes | An open-weight model (Qwen / DeepSeek) via OpenRouter |
| 🔁 **Harness** | The loop that lets the model read, think, and act | **OpenCode** (open-source, runs in your terminal) |
| 📜 **Instructions** | Who the agent is and how it behaves | `AGENTS.md` |
| 🛠️ **Skills** | Reusable "how to do X" recipes | `.opencode/skills/` |
| 💾 **Memory** | What it remembers between sessions | the `memory/` folder |

A chatbot answers and forgets. An **agent** has instructions, can *do* things (skills),
and *remembers* (memory). That's the whole difference, and this kit hands you all five.

### The two open pieces

- **The harness — [OpenCode](https://opencode.ai).** Properly open source. It's the loop
  that turns a model into an agent: it reads your files, runs your skills, uses tools.
- **The model — open-weight, via [OpenRouter](https://openrouter.ai).** OpenRouter is one
  API key that reaches dozens of models, including free open-weight ones like
  **Qwen3 Coder** and **DeepSeek**. The free tier gives you ~50 requests/day with no
  credit card. (OpenRouter itself is a paid gateway — but the *models* it serves are open,
  and the free tier costs nothing.)

---

## Quick start (about 5 minutes)

### 1. Install OpenCode

```bash
curl -fsSL https://opencode.ai/install | bash
```

(Other install options — Homebrew, npm — are in the [OpenCode docs](https://opencode.ai/docs/).)

### 2. Get a free OpenRouter key

Sign up at **<https://openrouter.ai>**, then create a key at
<https://openrouter.ai/keys>. No credit card needed for the free tier.

### 3. Add your key

```bash
cp .env.example .env
```

Open `.env` and paste your key after `OPENROUTER_API_KEY=`.

### 4. Run your agent

```bash
opencode
```

Then talk to it. Try this, in order, to see all five parts working:

1. *"Remember that our demo is on Friday."* → it uses the **capture-note** skill and a new
   file appears in `memory/`.
2. Quit (`Ctrl-C`) and start `opencode` again — a totally fresh session.
3. *"What do you know about the demo?"* → it uses the **recall** skill and answers from
   `memory/`, even though the conversation is gone. **That's persistence.**

If that worked: congratulations, you have a working agent. Now make it yours. 🎉

> **Heads-up on cheap models:** free open-weight models are brilliant value but a little
> less reliable at multi-step tool use than the big paid ones. If your agent gets confused,
> try a stronger model (see *Switching models* below) — or just give it a clearer
> instruction. This is normal; it's part of the craft.

---

## Make it yours

Here's the whole repo and what each piece is for:

```
agent-starter-kit/
├── AGENTS.md              ← your agent's constitution (start here)
├── opencode.json          ← config: which model, which MCP servers
├── .env                   ← your secret API key (you create this)
├── memory/                ← long-term memory (also an Obsidian/Logseq vault)
├── .opencode/
│   ├── agents/            ← personas (researcher.md is an example)
│   └── skills/            ← skills (capture-note, recall)
└── docs/
    ├── persistence.md     ← choosing Notion vs Obsidian vs Logseq
    └── ideas.md           ← a menu of things to build next
```

### Step 1 — Give it a personality (`AGENTS.md`)

This file is read at the start of every session. Open it and rewrite the *"Who this agent
is"* section. Give it a name, a job, an attitude. This is the fastest way to make the
agent feel like *yours* — do it first.

### Step 2 — Teach it a skill

A **skill** is a Markdown recipe for one task. The agent reads a skill's one-line
`description` and, when a request matches, follows its steps. Look at
`.opencode/skills/capture-note/SKILL.md` — that's the whole pattern.

To add your own, create `.opencode/skills/<your-skill>/SKILL.md`:

```markdown
---
name: your-skill
description: Use when the user wants to <the trigger>. Be specific — this is how the agent decides to use it.
---

# Your Skill

## When to use this
<the situations that should trigger it>

## Procedure
1. <step one>
2. <step two>
3. Tell the user what you did.
```

That's it. Restart OpenCode and your skill is live. The `description` matters most — write
it like the moment you'd want the agent to reach for this.

### Step 3 — Give it a persona (optional)

A **persona** is a focused mindset, defined in `.opencode/agents/<name>.md`. The example
`researcher.md` is a subagent your main agent can call to dig into a question. Copy it,
rename it, rewrite the instructions. `mode: subagent` = a helper the agent calls;
`mode: primary` = an agent you talk to directly.

### Step 4 — Give it hands (MCP, optional)

**MCP** lets your agent reach the outside world — Notion, Slack, GitHub, databases.
`opencode.json` already has a Notion server stubbed (disabled). To use it, flip
`"enabled": true` and follow the login prompt. More in `docs/persistence.md`.

---

## Memory & the persistence layer

This is worth a real decision, so it has its own guide: **[`docs/persistence.md`](docs/persistence.md)**.

The short version: by default your agent's memory is **plain Markdown files in `memory/`**,
which is *also* a valid **Obsidian** and **Logseq** vault. Open that folder in either app
and you and your agent literally share one knowledge base — it writes notes, you read and
edit them, and vice versa. If you'd rather use **Notion** (better for teams and
databases), the guide shows how to switch — you only rewrite the two memory skills.

---

## Switching models

Edit the `"model"` line in `opencode.json`. The format is `openrouter/<author>/<model>`.
Some good ones to try (check <https://openrouter.ai/models> for current names and which
are free):

- `openrouter/qwen/qwen3-coder` — strong free coding model, big context (default here)
- `openrouter/deepseek/deepseek-chat` — strong reasoning
- a `:free` suffix on a model name (e.g. `...:free`) forces the no-cost variant

---

## What to build next

Open **[`docs/ideas.md`](docs/ideas.md)** — it's a menu of skills, personas, and MCP
connections, roughly easiest-first, with demo tips at the bottom. Don't build all of it.
Pick the one or two that make *your* agent genuinely useful to *you*, and go deep.

Have fun. Build something that helps you. 💜

---

### Useful links

- OpenCode docs — <https://opencode.ai/docs/>
- OpenCode Skills — <https://opencode.ai/docs/skills/>
- OpenCode Agents — <https://opencode.ai/docs/agents/>
- OpenRouter models & pricing — <https://openrouter.ai/models>
- MCP server directory — <https://github.com/modelcontextprotocol/servers>
- Obsidian — <https://obsidian.md> · Logseq — <https://logseq.com>
