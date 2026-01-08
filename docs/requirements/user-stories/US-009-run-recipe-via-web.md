# US-009: Create a Workspace and run a Recipe via the Web App

- ID: US-009
- Title: Create a Workspace and run a Recipe via the Web App
- Persona: saas-user
- Phase: mvp

## Story
As a SaaS user
I want to create and configure a Workspace and execute a Recipe
So that I can run reproducible ingest and analysis without writing Python

## Notes / open questions
- The Web App requires a Recipe for any ingest or analysis execution.
- Workspace creation must respect the input/workspace/results root rules.
- Direct Python usage of the Lab API must remain possible without Recipes.

## Example scenarios (Given/When/Then)
```text
Scenario: Create a Workspace in the Web App
  Given I am signed in
  When I provide the required storage roots
  Then the Web App provisions a Workspace and persists its configuration

Scenario: Run a Recipe through the Web App
  Given a Workspace exists
  And a valid Recipe is stored for that Workspace
  When I run the Recipe
  Then the steps execute in order and outputs are persisted under results_root

Scenario: Re-run a Recipe
  Given a Workspace and Recipe
  When I run the Recipe again
  Then execution is idempotent and does not duplicate persisted state
```
