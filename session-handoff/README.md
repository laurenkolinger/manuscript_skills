# session-handoff

The handoff discipline for a multi-session manuscript round. It leaves a resume
that a fresh context window or a different agent picks up in one read, without
re-deriving state.

## Contents

```text
session-handoff/
├── README.md   # this file
└── SKILL.md    # behavior rules Claude follows
```

## When to use

Reach for this at every stopping point in a long round: a session close, a version
state boundary, or the moment work is handed to a fresh context window or a
different agent. It applies to the edit layer (a version parked at SENT, LISTED,
REVIEW_DONE, or REFLECTED) and to the submit layer (work parked between submit
steps). The plain triggers are "write a handoff", "instructions for the next
agent", and "where did I stop off".

## What it does

The skill produces a resumable handoff in three artifacts, each carrying the
handoff a different distance. The resume pointer (STATE.md) holds the machine-clean
state: one state, the current item, the blocker, the wait, and a single next
action, always current. The narrative handoff (HANDOFF_{date}.md) tells the story
at a state boundary: what exists and is verified, the findings that need
attention, how to resume, and what is out of scope. The directive next-agent
kickoff (NEXT_AGENT_START_HERE.md) is a self-contained briefing for a fresh window
or a different agent, with the task, the startup sequence, the loop, the hard
rules, a complete file map, pointers to the detailed instructions, and a
copy-paste prompt the user drops into the new window.

## How it fits a scientific-manuscript workflow

A coauthor round or a submission spans days to months and changes hands often. The
layer orchestrators (`manuscript-revision-roundtrip` and `manuscript-submit`) build
the resume discipline into their state machines; this skill is the shared standard
for the artifacts those stops produce, so a handoff reads the same in either layer.
It keeps every number an inline R expression rather than a frozen literal, resolves
cross-layer paths from the manifest rather than guessing, and holds to house style.
The file map and the paste prompt are the two parts a handoff most often omits, and
the two that most determine whether the next worker resumes cleanly or re-derives
the project from scratch.
