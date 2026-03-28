# MISTAKES.md — f1-fantasy

## Lessons From This Build

### 2026-03-28/29

**CSS theme defined but never applied**

A dark theme was fully written in `styles.py` with `apply_f1_dark_theme()`. `app.py` imported `styles` but never called the function. Result: white background for the entire session. Amy's AI caught it from a screenshot.

**Root cause:** Function definition ≠ function execution. `import styles` only loads the module. The function existed; zero CSS was injected.

**Rule:** Every `def` that produces side effects (CSS injection, initialization, registration) must be explicitly called after import. Not just defined.

**TDD done backwards for 8 requirements**

Dark theme, refresh button, telemetry selector chain — all shipped without tests. Tests added after the fact. 43 tests existed but the critical path had no coverage.

**Rule:** TDD sequence is non-negotiable. Write test, watch fail, write code. Never move to the next feature until the test passes.

**Parallel agents without integration step**

Three agents ran concurrently. Each completed a "unit." The units connected at assembly — and the connection was broken. The CSS never made it from styles.py into the app.

**Rule:** After parallel agents finish, one agent verifies the assembly. Or: sequential builds with integration verification between steps.

**Verification theater**

"43/43 tests passing" was reported. The deployed app was broken. Test count is not proof of working software.

**Rule:** Post-deploy verification is mandatory. Screenshot, smoke test, or human check — something that proves the assembled product works, not just the units.

---

**Every AI working on this project must read this file before starting.**
