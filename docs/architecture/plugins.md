# Plugin Architecture

## Core vs. Plugins
* **Core (`arbolab`):** Defines domain models, registry, and runtime. **Never** imports device code.
* **Plugins (`arbolab-<device>`):** Depend on core. Contain strictly device-specific logic (parsers, schemas).

## Namespace & Discovery
* **Mechanism:** PEP 420 Namespace packages (`arbolab_plugins.*`).
* **Registry:** Plugins register via entry points (`arbolab.plugins`) and `PluginRegistry`.
* **Activation:** Only plugins explicitly enabled in `LabConfig` are loaded.
* **No Global State:** Plugins must not introduce their own global registries.

## Isolation Rules
1.  **I/O:** Parsers must be usable standalone (no core dependency inside parser modules).
2.  **Write Access:** Plugins write **only** via `VariantStore` (to workspace) or provided writers.
3.  **Dependencies:** Keep minimal. Heavy deps belong in the plugin, not core.

## Extension Points
Plugins receive a context object exposing:
* `WorkspaceLayout` / `ResultsLayout`
* `VariantStore`
* Logging facilities