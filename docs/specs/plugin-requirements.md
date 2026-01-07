# Plugin Requirements

**Binding Rules**: See `../../AGENTS.md`.

## Packaging and Namespacing
- Device plugins are separate packages that depend on the core.
- Plugin code lives under the `arbolab_plugins.<device>` namespace package (PEP 420).
- Plugin packages follow the `src/` layout and expose their plugin entry point.

## Discovery and Registration
- Discovery uses entry points in the group `arbolab.plugins`.
- Each plugin provides a `register(registry)` function that registers loaders and processors with the core registry.
- Plugins must not introduce their own global registries; they register with the core registry at runtime.

## Lab Integration Contract
- The Lab must expose a plugin discovery entry point (for example `Lab.load_plugins()`) that loads only the `arbolab.plugins` entry points explicitly enabled in configuration.
- The configuration must provide an allow list of enabled plugin entry point names; an empty list disables plugin discovery.
- Plugin discovery must surface failures (for example import or registration errors) with actionable diagnostics without preventing other plugins from loading.
- When a plugin is enabled but not installed, the Lab must report that mismatch in diagnostics.
- Plugins may contribute SQLAlchemy `MetaData` collections for domain extensions; the Lab must register these contributions and ensure the schema is materialised in the workspace database.
- Plugins may register Lab initialisation hooks; hooks must run after the workspace is prepared and after plugin metadata contributions are registered.
- The core must remain usable when no plugins are installed.

## Independence and Integration
- Parser and I/O code lives in dedicated plugin submodules and can run without any dependency on the core package.
- The core exposes a generic plugin runtime under `arbolab.plugins`; no device-specific logic is allowed in the core plugin runtime.
- Each plugin receives its own config namespace (for example `plugins.<entry_point>.*`).
- Extension points provided by the core include `arbolab.ingestion` and `arbolab.reporting`.

## Optional Extras
Device packages may be installable through core extras (for example `arbolab[treeqinetic]`). When this is supported, the core declares device dependencies under its `optional-dependencies`.
