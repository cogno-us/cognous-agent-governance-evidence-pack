# Contributing

Thank you for your interest in contributing to Agent Governance Evidence Pack.

## What this project is

A public reference schema, validator, and markdown renderer for AI-agent governance evidence. Contributions should stay within this scope.

## What contributions are welcome

- Bug fixes in the validator, renderer, loader, or CLI
- Additional validation rules or warnings that are clearly justified
- New example evidence packs for additional industries or use cases
- Improvements to JSON schemas
- Documentation improvements
- Additional tests

## What is out of scope

- Agent frameworks or model runtimes
- Hosted services or dashboards
- Compliance certification tooling
- Features that would add heavy external dependencies

## Getting started

```bash
git clone https://github.com/cogno-us/cognous-agent-governance-evidence-pack.git
cd cognous-agent-governance-evidence-pack
pip install -e ".[dev]"
pytest
```

## Testing

```bash
pytest
agep check-examples
```

All tests must pass before opening a pull request.

## Pull requests

- Keep changes focused and minimal.
- Add tests for new functionality.
- Update documentation if you change behavior.
- Run `agep check-examples` before submitting.

## Code of conduct

See `CODE_OF_CONDUCT.md`.

## License

By contributing, you agree that your contributions will be licensed under the Apache-2.0 license.
