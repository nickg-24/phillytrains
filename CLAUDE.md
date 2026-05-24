
You are helping me build PhillyTrains.

This project uses a structured AI-assisted development system defined below. Follow these definitions exactly — do not infer behavior from general conventions.

## Modes of Interaction

**Exploration Mode** (default): normal development work — designing, coding, debugging, iterating.

**Command Mode**: invoked explicitly at key moments using the commands below.

## Commands

### START_OF_DAY
Read ARCHITECTURE.md in full. Read the Summary section of PROGRESS.md and the last 3-5 entries of the Session Log.

If PROGRESS.md is empty or contains only template placeholders, skip the recap and ask:
> "What are you building and what do you want to work on first?"

Otherwise, summarize current state in 2-3 sentences and propose a focus:
> "Here's where things stand: [summary]. Last session you finished [X] and wanted to pick up [Y] next. Want to continue with that, or is there something else on your mind?"

Wait for confirmation or redirection before doing anything. Do not write any files.

### PLAN
Take a description of what to build or solve. Break it into concrete steps. Surface relevant decisions and unknowns. Confirm the plan before any implementation begins. Do not write any files — this is a thinking step only.

### IMPLEMENT
Execute the planned work step by step. Surface decisions as they come up. Confirm significant choices before proceeding.

### END_OF_DAY
Summarize what was completed and any decisions made. Then update files:

**ARCHITECTURE.md** — update if any architectural decisions were made this session:
- New components added → update the Components table
- Key choices resolved → add a row to Key Decisions with the date
- Open questions answered → remove or update them
- New open questions raised → add them

**PROGRESS.md** — always update in two steps:
1. Rewrite the Summary section — everything above the `---` separator. Keep it to one short paragraph reflecting current project state.
2. Append a new entry to the Session Log — below the `---` separator — in this format:

```
### [YYYY-MM-DD]
**Focus:** [what was worked on]
**Done:** [what was completed]
**Next:** [what to pick up next]
**Notes:** [decisions, blockers, open questions — omit if none]
```

## Key Files
- ARCHITECTURE.md — system design and decisions
- PROGRESS.md — project state and session history

## How Progress Is Tracked

PROGRESS.md has two sections separated by `---`:

**Summary** (above `---`) — one short paragraph of current project state. Rewritten each END_OF_DAY. Read this first at START_OF_DAY.

**Session Log** (below `---`) — one entry per session, append-only. At START_OF_DAY, read only the last 3-5 entries. Do not load the full history.

## Rules
- Always propose before implementing
- Favor clarity over completeness
- Avoid unnecessary complexity

Read ARCHITECTURE.md and PROGRESS.md now, then confirm you're ready.

