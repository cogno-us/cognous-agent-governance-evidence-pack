# Security Policy

## Scope

Agent Governance Evidence Pack is a schema definition, validator, and markdown renderer. It processes JSON input files and produces markdown output. It does not:

- Enforce runtime access control
- Connect to external services
- Store or transmit data
- Execute agent actions
- Certify compliance with any regulatory framework

It is a documentation and formatting tool.

## Security properties

- **No external calls** — the renderer and validator make no network requests.
- **No credential handling** — this package does not handle secrets, API keys, or authentication tokens. Do not put credentials in evidence pack files.
- **No code execution** — evidence pack files are declarative JSON. They are not executed.
- **Input validation** — Pydantic v2 validates all input. Invalid JSON or model violations raise clear errors.

## Recommended use

This tool should be combined with:

- Runtime policy gates and application authorization controls
- Audit logging and monitoring for agent actions
- Operational security controls for systems the agent accesses
- Legal review for regulatory compliance requirements
- Compliance review by qualified professionals

This tool does not replace any of the above.

## Reporting a vulnerability

If you discover a security vulnerability in this repository, please open a GitHub issue or contact the maintainers directly. Do not include exploit details in public issues.

For vulnerabilities in dependencies, please check the GitHub Advisory Database and open a pull request updating the affected dependency.
