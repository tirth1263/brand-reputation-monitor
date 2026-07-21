# Contributing

Thanks for helping improve Brand Reputation Monitor.

1. Fork the repository and create a focused branch: `git checkout -b feature/my-improvement`.
2. Create a Python 3.11 virtual environment and install `requirements-dev.txt`.
3. Keep credentials in `.env`; never commit keys, scraped private data, or `memori.db`.
4. Run `ruff check .` and `pytest` before opening a pull request.
5. In the pull request, describe the user-facing change, tests performed, and any new environment variables.

Source provenance is a product invariant: model output must never be allowed to introduce or replace article URLs.

