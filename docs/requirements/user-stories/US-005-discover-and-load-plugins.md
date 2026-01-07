# US-005: Discover and load installed plugins

- ID: US-005
- Title: Discover and load installed plugins
- Persona: researcher-student
- Phase: mvp

## Story
As a researcher/student working with multiple sensor types and analysis workflows
I want ArboLab to discover and load installed plugins that I have explicitly enabled
So that device-specific ingestion and reporting capabilities become available without manual wiring

## Notes / open questions
- Plugins are optional; the core must remain usable without device packages installed.
- Plugins may contribute database schema (metadata tables) and runtime hooks.
- Plugin discovery must provide actionable diagnostics when plugins fail to load.
- Plugin activation is explicit via a configuration allow list of entry point names.

## Example scenarios (Given/When/Then)
```text
Scenario: Enabled plugins are discovered on Lab initialisation
  Given I have installed one or more device plugins that expose an entry point
  And I have enabled them in my Lab configuration
  When I open a Lab
  Then ArboLab discovers and registers the enabled plugins and exposes them via a plugin registry

Scenario: Plugin discovery reports failures without hiding them
  Given an installed plugin that fails to import or register
  When I open a Lab
  Then ArboLab reports the failure in a human-readable way and continues loading other plugins

Scenario: Enabled plugin is missing
  Given I have enabled a plugin that is not installed
  When I open a Lab
  Then ArboLab reports that the enabled plugin is missing and continues without it
```
