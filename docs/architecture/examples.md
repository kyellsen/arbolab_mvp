# Examples Layout

Each package under `packages/` owns a sibling subdirectory inside `examples/`. This keeps examples focused on the package they describe.

Current layout:

```text
examples/
├── arbolab
├── arbolab-logger/
│   └── example.py
```

The `test_*` directories belong solely to the `arbolab` examples; package-specific fixtures should live within that package's example subtree. These directories are runnable templates and documentation aids, not defaults for real projects.
