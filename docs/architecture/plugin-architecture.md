# Plugin Architecture

## Core vs Plugins
The core package (`arbolab`) provides domain models, configuration models, managers, persistence, and the plugin runtime. It must never depend on device packages at compile time.

Device-specific implementations live in separate packages that depend on the core. Core modules under `arbolab.plugins.*` remain generic and contain no device-specific logic.

## Namespace Packages
Device plugins live under the `arbolab_plugins.*` namespace package and follow PEP 420.

## Plugin Discovery and Registry
- The core exposes a generic plugin runtime under `arbolab.plugins` with a registry, base interfaces, and discovery utilities.
- Plugins expose their functionality through the core `PluginRegistry`.
- Plugins are separate packages (for example `arbolab-treeqinetic`, `arbolab-linescale`).
- Discovery uses entry points in the group `arbolab.plugins` and loads only the entries explicitly enabled in the Lab configuration.
- Each plugin exposes a `register(registry)` function that registers loaders, processors, and feature sets with the core registry.
- Device packages must not introduce their own global registries; they register with the core registry at runtime.
- The core knows no device-specific code at compile time beyond the entry-point group.
- The MVP enables exactly one plugin; the specific plugin is intentionally flexible.

## Parser and I/O Isolation
Parser and I/O code lives inside each plugin in dedicated submodules that can run without any dependency on the core package. This keeps parsers reusable for standalone tooling.

## Extension Points
Core extension points allow plugins to register ingestion, feature extraction, and reporting providers. Plugins receive a shared context object that exposes core managers and logging.
