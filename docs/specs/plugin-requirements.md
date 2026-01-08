# Plugin Requirements & Ingestion Protocol

**Binding Rules**: See `../../AGENTS.md`.

## 1. Packaging & Discovery
- **Namespace**: `arbolab.plugins` (Entry Point Group).
- **Code implementation**: `arbolab_plugins.<device>` (Namespace Package).
- **Registration**: Plugins expose a `register(registry)` function.
- **Isolation**: Plugins MUST NOT import from other plugins. Dependencies on `arbolab` core only.

## 2. Ingestion Protocol
Plugins implementing data ingestion MUST follow this pipeline:

1. **Scan**: Identify relevant files in `input_root` matching the plugin's pattern.
2. **Parse**: Read manufacturer-specific binary/text formats.
3. **Normalize**:
    - Convert timestamps to UTC.
    - Map columns to standard `ColumnSpec` (See `data-model.md`).
4. **Yield**: Produce standardized chunks (Arrow/Pandas) for the Core to write.

**Constraint**: Plugins **NEVER** write to disk directly. They yield data frames to the Lab Runtime.

## 3. Metadata Extension
- Plugins MAY contribute SQLAlchemy `MetaData` for device-specific tables.
- Tables MUST be namespaced (e.g., `plugin_ls3_settings`).
- The Core responsible for migration application.
