---
name: jira-multi-agent
description: |
  Drive a complete feature implementation from a Jira ticket or raw requirements to committed, tested code using parallel specialist agents. Use this skill whenever the user mentions a Jira ticket number (e.g. PROJ-123, ENG-456), says "implement this ticket", "work on this story", "build this feature", or pastes requirements and wants end-to-end implementation help. Also trigger when the user says things like "spin up agents to implement", "multi-agent coding", "implement this for me", or drops a feature description and asks Claude to "just build it". Handles the full lifecycle: Jira fetch → design → parallel coding → testing → commit → implementation summary — with minimal human interruption.
---

# Jira Multi-Agent Implementation Skill

This skill drives a feature from ticket (or raw requirements) all the way to committed, tested code using three specialist agents: **Design**, **Coding**, and **Testing**. You orchestrate them, keeping human interruptions to a minimum — only pause when there is a genuine blocker.

---

## Phase 0: Parse Input

Determine what the user handed you:

- **Jira ticket number** (e.g. `PROJ-123`, `ENG-456`, `STORY-789`): proceed to Phase 1.
- **Direct requirements** (text description, bullet list, user story): skip to Phase 2, using the provided text as the requirements.
- **Ambiguous input** (just a number, or something that could be either): ask once — "Is this a Jira ticket number, or do you want me to treat this as requirements directly?"

---

## Phase 1: Fetch Jira Details (skip if direct requirements given)

Try MCP Jira tools first. If not available, check for Jira credentials in the environment:

```
JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN
```

If credentials are available, fetch the ticket via the Jira REST API:
```
GET {JIRA_URL}/rest/api/3/issue/{TICKET}
```

Extract and structure:
- **Summary** (ticket title)
- **Description** (full body, strip Atlassian Document Format if needed)
- **Acceptance Criteria** (look in description, custom fields, or "Definition of Done" sub-sections)
- **Ticket type** (Bug / Story / Task / Sub-task)
- **Priority**
- **Labels / Components** (hints about which part of the codebase is affected)
- **Linked issues** (parent epic, blockers, related)

If credentials are missing and no MCP tool is available, ask the user once:
> "I need Jira credentials to fetch the ticket. Do you have `JIRA_URL`, `JIRA_EMAIL`, and `JIRA_API_TOKEN`? Or paste the ticket description here and I'll proceed without fetching."

Once requirements are in hand (from Jira or from the user), proceed.

---

## Phase 2: Design Agent

Spawn a **Design** sub-agent. Its job is to understand the codebase and produce a concrete implementation plan before any code is written.

**Spawn this agent with:**
```
Read references/agent-prompts.md → "Design Agent Prompt"
```

The Design agent must return a structured plan:
- Which files to create / modify / delete
- New functions, classes, or modules to introduce
- Data model changes (DB migrations, schema updates)
- API contract changes (new endpoints, modified payloads)
- Key risks or constraints identified in the codebase
- Suggested test scenarios

Wait for the Design agent to complete before proceeding — coding depends on the plan.

---

## Phase 3: Coding + Testing Agents (parallel where possible)

Once the design plan is ready, spawn **Coding** and **Testing** agents.

They can start work in parallel where the testing agent writes test scaffolding/stubs while the coding agent implements. If the test agent needs completed implementation to write integration tests, it should complete unit test stubs first, then finish after coding is done.

**Spawn both agents with:**
```
Read references/agent-prompts.md → "Coding Agent Prompt"
Read references/agent-prompts.md → "Testing Agent Prompt"
```

Pass each agent:
1. The full requirements (from Phase 0/1)
2. The complete design plan (from Phase 2)

### Coordination rule
If the coding agent hits an ambiguity not resolvable from the codebase or the design plan, it should surface a specific question and pause. Do not spin on it. Similarly for testing.

---

## Phase 4: Integration & Validation

After both agents complete:

1. **Review the diff** — scan the changes for obvious issues: broken imports, missing error handling at system boundaries, test files that don't actually run.
2. **Run existing tests** — execute the test suite. If tests fail, spawn a targeted fix agent (see `references/agent-prompts.md` → "Fix Agent Prompt") and pass it the failure output.
3. **Run new tests** — confirm the tests added by the Testing agent pass.
4. **Lint / type-check** — if the project has a linter or type checker configured, run it.

Iterate fix cycles up to **3 times** before escalating to the user with a clear description of what's failing.

---

## Phase 5: Commit

Stage and commit all changes to the current branch:

```bash
git add <specific files — never git add -A blindly>
git commit -m "$(cat <<'EOF'
<type>(<scope>): <concise summary from ticket/requirements>

- <bullet of key change 1>
- <bullet of key change 2>
...

Refs: <TICKET-NUMBER or 'no-ticket'>
EOF
)"
```

Use conventional commit types: `feat`, `fix`, `refactor`, `test`, `chore`.

Do **not** push unless the user explicitly asks.

---

## Phase 6: Implementation Summary

After committing, print a structured summary:

```
## Implementation Summary — <TICKET or short title>

### What was built
<2-4 sentences describing the feature/fix in plain language>

### Files changed
| File | Change type | Description |
|------|-------------|-------------|
| path/to/file.ts | Modified | <what changed and why> |
| path/to/new_file.py | Created | <purpose> |
| path/to/old_file.go | Deleted | <why removed> |

### Tests
| Test file | Coverage |
|-----------|----------|
| tests/test_foo.py | Unit tests for <component>; <N> new cases |

### Acceptance criteria status
| Criterion | Status |
|-----------|--------|
| <criterion from ticket> | Implemented / Partial / Deferred |

### Caveats & follow-ups
- <Any known limitations, deferred work, or things to watch>
```

---

## When to Pause and Ask

Only interrupt the user for:

1. **Missing Jira credentials** and they haven't offered to paste requirements.
2. **Genuinely ambiguous requirements** — two or more plausible interpretations with meaningfully different implementations, and no way to infer the right one from the codebase or ticket context.
3. **Architectural decision with no clear winner** — e.g., "should this be a new service or extend the existing one?" where the codebase gives equal evidence for both, and the choice has large blast radius.
4. **Test failures still unresolved after 3 fix cycles.**
5. **Destructive changes** — e.g., the design plan calls for deleting a module or dropping a DB table. Confirm before proceeding.

For everything else — naming conventions, minor style choices, minor gaps in acceptance criteria — make a reasonable decision, document it in the implementation summary under "Caveats", and keep moving.

---

## Reference Files

- `references/agent-prompts.md` — Detailed system prompts for Design, Coding, Testing, and Fix sub-agents. Read this before spawning each agent.
