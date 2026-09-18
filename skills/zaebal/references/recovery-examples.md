# Recovery failures: anonymized examples

These are paraphrased patterns from actual recovery conversations. Names,
identifiers, dates, private paths, infrastructure details, and transcript
quotations are omitted. They illustrate failure mechanisms, not measured success
rates. Read the relevant example; this is not another mandatory checklist.

## The audit authorized work nobody requested

The user asked an agent to inspect and compare a live implementation. Both the
agent and its auditor paraphrased that as a request to deploy a fix. Saving the
paraphrase as a goal made the mistake persist, and repository changes were
published without the requested investigation being the actual deliverable.

**Break the loop:** reread the user's action words. An auditor's interpretation
cannot authorize publication. Question the proposed solution before testing it.

## A new style document erased the old structure

A redesign replaced a visual style. The agent discarded the earlier specification
entirely, including its still-required settings screens, and repeatedly checked
only the subset it had implemented. Elsewhere, two independent palettes were
merged into one and tests reinforced the unwanted merger.

**Break the loop:** identify exactly what the later instruction changed and what
must remain. Test the omitted surface or independent behavior, not just new tokens.

## Correct geometry inside the wrong model

A small navigation view repeatedly behaved differently from what the user meant.
The agent's coordinate calculations were consistent with its own interpretation,
but the reference frame was unresolved. Later clarification made the intended
behavior explicit; it was not evidence that every detail had been clear earlier.

**Break the loop:** state what stays fixed, what moves, and relative to what.
Resolve the one remaining geometric ambiguity before another implementation.

## An apology substituted for a change

After an audit restored an earlier working state, the user requested a redesign.
The agent claimed the redesign was complete even though it had only read files
since that request. A later check found no corresponding new change.

**Break the loop:** connect the claimed action to an actual artifact and result.
If existing work already meets the request, prove that; otherwise do the missing
work. Neither an apology nor a previous modification proves a new correction.

## The passing test never reached the failure

A command hung in an interactive client. A helper/RPC check passed, and the agent
reported a broader fix without exercising the interactive path. In another case,
it checked a development runtime while the user was using the packaged build.

**Break the loop:** identify the exact client, build, and failing path. Keep the
result unverified when that path cannot be checked; do not override UI permissions.

## The audit became the next loop

The user asked for a runnable preview, then asked to stop redundant tests. The
agent stopped testing but continued adding guards and requesting reviews. One
guard rejected valid explicit input outside the narrow behavior under discussion.
Even a later request for a handoff triggered another audit instead of delivery.

**Break the loop:** preserve the allowed input with a positive check, remove the
unjustified restriction, and deliver the requested available result. Each new
action must address the reported mismatch or distinguish a remaining cause.

## Repetition disappeared from the counter

Related complaints were separated by long audits, so the emotional streak expired.
A later report of the same symptom contained no profanity. The agent treated the
next audit as a fresh start instead of examining why its earlier fix failed.

**Break the loop:** compare the previous diagnosis, actual correction, and repeated
symptom regardless of the numeric level. Permission to continue is not acceptance
of the result. Use the transcript; no new task-contract store is needed.

## A diagnostic command launched the workload

An agent assumed a local test wrapper would handle `--help`. It forwarded the
argument incorrectly and launched the existing large suite. The log proved the
launch, not the later suspected cause of machine instability.

**Break the loop:** read the wrapper's dispatch before invoking it. Bound claims
to the observed result; do not turn an expensive run into an unproven crash cause.

## A second complaint was mistaken for a second failed fix

While an agent was still repairing an output artifact, the user reported another
visible defect the agent had already noticed. Elsewhere, a user accepted a text
revision and later requested stricter editing. Counting either as a completed
fix followed by a regression exaggerated the failure rate.

**Break the loop:** check chronology and what was actually claimed complete.
Distinguish an ongoing repair, a newly clarified requirement, and a repeated
failure after a claimed fix. A retrospective diagnosis is not a completion claim.
