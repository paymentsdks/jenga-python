# Contributing

## Development Setup

1. Fork and clone the repository.
2. Create a virtual environment.
3. Install the project in editable mode.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

## Running Tests

Run the test suite before opening a pull request.

```bash
python -m unittest discover -s tests
```

## Pull Requests

1. Keep changes focused and minimal.
2. Add or update tests when behavior changes.
3. Update documentation when user-facing behavior changes.
4. Open a pull request with a clear description of the change.

## Notes

- CI runs automatically for pull requests.
- Markdown-only changes do not trigger the test workflow.
