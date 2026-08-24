# Audit playbooks

Use one primary playbook and any secondary playbook that the failure crosses. Do not run every check mechanically. The common output is:

1. `CONTRACT` — literal request and observed failure.
2. `DIVERGENCE POINT` — earliest relevant conversation turn (quote plus timestamp/order), the mismatch introduced there, and the corresponding diff/commit evidence. If history is incomplete, use `not established`.
3. `FACTS` — each fact names a conversation or repository artifact.
4. `HYPOTHESES` — at least two competing causes unless direct evidence is conclusive.
5. `DISCRIMINATING CHECK` — smallest check that produces different expected results for the causes. During a read-only stop, inspect existing evidence only; prescribe any new run/mutation as a post-ack next check.
6. `PREVIOUS AUDIT` — quote any earlier causal conclusion, its current status, and the evidence gate it skipped.
7. `WRONG BELIEF` — established only after that check; otherwise `not established`.
8. `STATUS` — `CONFIRMED`, `PARTIAL`, `UNVERIFIED`, or `DISPROVED`.
9. `OUTCOME GATE` — exact user-visible artifact that proves the requested result.

For every playbook, inspect the session chronology before interpreting runtime artifacts. Map request/decision/action turns to working-tree and staged diffs and to timestamped commits. Context explains why an artifact exists; the artifact proves what actually changed. Neither evidence track may replace the other.

## Code and runtime

Use for bugs, tests, services, containers, deploys, and “works locally but not for the user.”

- Reproduce the exact failing path, not a nearby unit or helper.
- Find the conversation turn that selected or justified the failing implementation, then match it to the diff/commit that introduced it.
- Map the request to the process that actually handles it. Enumerate duplicate local and in-scope server processes, containers, ports, routes, images, worktrees, and credentials.
- Compare source → built artifact → installed/deployed artifact by version or hash.
- Treat a passing unit test, green healthcheck, or quiet log as intermediate evidence only.
- Outcome gate: the original failing request succeeds against the exact serving runtime.

Example: “the new code is deployed” is a hypothesis until the process receiving a traced request reports the intended commit/image and produces the corrected response.

## Config, hooks, instructions, and environment

Use for AGENTS.md, skills, hooks, config files, PATH, env variables, and startup settings.

- Find the active home/config root, including overrides such as `KIMI_CODE_HOME` or container env.
- Match the conversation's claimed target path and reload assumption to the actual config diff and commit chronology.
- Prove the host parsed and registered the entry with its own diagnostics/list command.
- Identify reload semantics: immediate, new process, new session, or full restart.
- Run a unique canary through the host boundary and find the corresponding hook/log/incident artifact.
- Outcome gate: the target process consumes the intended value and changes behavior.

Example: a TOML block existing under `~/.kimi-code` does not prove Kimi loaded it when `KIMI_CODE_HOME` points elsewhere.

## Git and remote state

Use for commits, pushes, branches, PRs, and “my changes disappeared.”

- Record worktree status, current branch, upstream, remotes, and ahead/behind state.
- Align commit timestamps and diffs with the session turn that requested or claimed each change; do not infer intent from Git alone.
- Distinguish working-tree content, index content, local commit, remote branch, and PR head.
- Verify the remote object after push (`ls-remote`, provider API, or fresh fetch), not only the local command's exit code.
- Check that ignored/untracked/generated files required by the contract are actually included.
- Outcome gate: the requested commit/content is reachable from the exact remote ref or PR the user named.

## Content and specification

Use for articles, prompts, plans, translations, summaries, structured output, and literal formatting constraints.

- Build a requirement → output-evidence table. Include voice, audience, length, format, forbidden material, and every literal constraint.
- Trace each requirement to the first session turn where it was accepted, changed, omitted, or contradicted.
- Separate source-backed claims from invented claims. Flag fabricated first-person experience, metrics, quotes, links, or product behavior.
- Compare action density with introductory/background “water”; ensure the deliverable starts where the user asked it to start.
- Verify physical formatting when relevant (one line, JSON schema, headings, character limit), not just semantic intent.
- Outcome gate: every requirement has a concrete location in the final artifact and no unsupported claims remain.

## Active context

Use when multiple workflows, models, branches, hosts, tabs, files, servers, or user personas are in play.

- Quote the last explicit selection and timestamp/order: workflow, model/checkpoint, branch/worktree, host, tab, target file, account, or environment.
- Start from the original request and find the earliest unapproved context switch, then match it to subsequent file or commit changes.
- Compare it with the target of every subsequent action. Do not infer a switch from convenience or recency.
- When UI and filesystem disagree, inspect both and identify which one the action actually mutated.
- Outcome gate: the final artifact comes from the explicitly selected context, or the user explicitly approves a switch.

## Stochastic and gen-media pipelines

Use for image, audio, video, LLM sampling, and any non-deterministic output.

- The user's bad output is a `FACT` about the symptom. Its cause remains a `HYPOTHESIS`.
- Capture the exact workflow file/hash, seed, input, checkpoint/model, VAE/encoder, LoRA stack and weights, sampler/scheduler, steps, CFG, dimensions, and post-processing.
- Confirm the workflow that executed, not merely the workflow open in the UI.
- Inspect existing same-seed A/B artifacts that change one variable at a time. If none exist, keep causality `UNVERIFIED` and prescribe the A/B as a post-ack next check. If determinism is unavailable, the later run needs a declared sample size and distribution comparison rather than cherry-picked outputs.
- Do not claim “LoRA caused it,” “CFG is too high,” or similar causality without A/B or direct artifact evidence.
- Outcome gate: a controlled comparison improves the named defect without regressing the user's other constraints.

## UI and external state

Use for browser/UI operations, dashboards, third-party APIs, messages, uploads, and settings changed outside the repository.

- Record the target identity (account, workspace, page/object ID) before mutation.
- After mutation, reload or read back through an independent path; stale local UI state is not proof.
- Capture a screenshot, API response, object version, delivery receipt, or server-side log tied to the target.
- Distinguish “click succeeded” from “state persisted” and “request accepted” from “downstream effect completed.”
- Outcome gate: an independent read confirms the intended external state for the exact target.
