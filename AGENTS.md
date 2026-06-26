# Repository Guidelines

## Project Structure & Module Organization

Each IP module (ACM, DCI, CSC, Sharp, CFA, CGC) follows a uniform five-layer architecture:

| Layer | Location |
|-------|----------|
| Config | `script/config_def/module_config_*.py` |
| Register | `script/reg_def/module_reg_*.py` |
| CLI | `script/cli_helper/cli_helper_*.py` |
| Algorithm | `script/<module>/` |
| C Verification | `src/<module>/` |

Shared utilities live in `src/utils/` (C) and the root `script/` directory (Python). GUI tools reside in `script/verify_tool_app/`. Prebuilt libraries are at `prebuilt/`, build scripts at `project/`, and documentation at `doc/`.

## Build, Test, and Development Commands

```bash
# Build (Windows, MinGW)
project/build_win32_mingw.cmd

# Build (Linux/WSL, target RK3572)
bash project/build_linux_host.sh Debug RK3572

# Run CLI interactive tool
python script/cli_helper_main.py [RK3572|RK3576|RK3538]

# Run PQ GUI verification tool
python script/verify_tool_app/pq_verify_tool.py
```

Output lands in `output/`. A `compile_commands.json` is generated at the repo root for clangd/IDE use.

## Coding Style & Naming Conventions

- **C/C++**: Microsoft-style (`.clang-format` at repo root), English comments only
- **Python**: Chinese comments, descriptive variable names
- **File naming**: `snake_case` for scripts, PascalCase for classes (`ModuleHelperCore`)
- Do not edit files under `script/verify_tool_app/ui_gen/` — they are auto-generated. Modify `ui_impl/` instead.

## Testing Guidelines

Tests are located alongside source code. C verification is done through `*_verify_demo` executables. There is no centralized test runner; run individual module tests as needed.

## Commit & Pull Request Guidelines

- Branch from `master`, work in feature branches, merge back when complete
- Commit format: `type[scope]: summary` followed by bullet points
- Types: `fix`, `feat`, `refactor`, `style`, `test`, `docs`, `perf`, `chore`
- Scopes: `acm`, `csc`, `dci`, `sharp`, `cfa`, `cgc`, `acm_ui`, etc.
- Do not commit: `script/verify_tool_app/ui_gen/`, `build/`, `dist/`, `output/`, or `*.json` test data files

## graphify

This project maintains a code knowledge graph at `graphify-out/` with god nodes, community structure, and cross-file relationships.

When exploring the codebase, prefer `graphify query "<question>"` and `graphify explain "<concept>"` over broad grep searches. Run `graphify update .` after modifying code to keep the graph current (AST-only, no API cost).

Rules:

- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
