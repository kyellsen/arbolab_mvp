# User Stories

This file is the single source of truth for user-story conventions within `docs/requirements/user-stories/`.

## What is a user story?
A user story is a short, user-centered requirement that describes what a user needs and why it matters, without prescribing implementation details.

Canonical form:

```text
As a <role>
I want <capability>
So that <benefit>
```

## What belongs here?
- Draft and refined stories that describe user value and scope.
- Example-style scenarios (Given/When/Then) to clarify expected behavior.

User stories are not specifications; concrete, testable contracts belong in `docs/specs/`.

## Conventions
- One story per file: `US-<3-digit-id>-<short-slug>.md`
- Each story includes: persona, phase, statement, notes, and example scenarios.
