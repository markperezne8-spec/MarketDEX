## CI build acceleration — 2026-08-27

- Pull-request Windows CI now reuses a dependency-locked .venv cache.
- PyInstaller reuses its analysis cache in pull-request CI while runtime and installer verification remain required.
- The latest green baseline (run #1106) completed in about 2m19s; the Windows build was 136s, including 25s of dependency installation and 36s of PyInstaller work.
- Manual Windows RC release workflows retain clean rebuilds for reproducible release packaging.

# M1.3 Foundation Package
Includes foundation, schema, persistence scaffold, docs and tests.
