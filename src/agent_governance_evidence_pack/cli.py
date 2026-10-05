"""
CLI for Agent Governance Evidence Pack.

Entry point: agep
"""

from __future__ import annotations

import sys
from pathlib import Path


def _load_pack(path_str: str):
    """Load a pack, printing errors and exiting on failure."""
    from .loader import load_evidence_pack

    try:
        return load_evidence_pack(path_str)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(2)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(2)


def cmd_validate(args: list[str]) -> int:
    if not args:
        print("Usage: agep validate <path/to/evidence_pack.json>", file=sys.stderr)
        return 2

    pack = _load_pack(args[0])

    from .validator import validate_evidence_pack

    report = validate_evidence_pack(pack)

    print(f"Pack ID : {report.pack_id}")
    print(f"Valid   : {report.valid}")
    print(f"Issues  : {len(report.issues)}")

    if report.issues:
        for issue in report.issues:
            location = f" [{issue.path}]" if issue.path else ""
            print(f"  [{issue.severity.value.upper()}] {issue.code}{location}: {issue.message}")

    return 0 if report.valid else 1


def cmd_summarize(args: list[str]) -> int:
    if not args:
        print("Usage: agep summarize <path/to/evidence_pack.json>", file=sys.stderr)
        return 2

    pack = _load_pack(args[0])

    from .summary import summarize_evidence_pack

    s = summarize_evidence_pack(pack)

    print(f"pack_id                : {s['pack_id']}")
    print(f"title                  : {s['title']}")
    print(f"review_status          : {s['review_status']}")
    print(f"agent_name             : {s['agent_name']}")
    print(f"environment            : {s['environment']}")
    print(f"tool_count             : {s['tool_count']}")
    print(f"action_count           : {s['action_count']}")
    print(f"privileged_action_count: {s['privileged_action_count']}")
    print(f"replay_bundle_count    : {s['replay_bundle_count']}")
    print(f"open_risk_count        : {s['open_risk_count']}")
    print(f"critical_open_risk_count: {s['critical_open_risk_count']}")

    trace = pack.metadata.get("traceable_import") if isinstance(pack.metadata, dict) else None
    if isinstance(trace, dict):
        counts = trace.get("derived_counts", {})
        lifecycle = trace.get("lifecycle_summary", {})
        print(f"distinct_effect_count  : {counts.get('distinct_effect_count', 'n/a')}")
        print(f"cp_attempt_count       : {counts.get('control_plane_attempt_count', 'n/a')}")
        print(f"executor_attempt_count : {counts.get('executor_attempt_count', 'n/a')}")
        print(f"destination_observed   : {lifecycle.get('destination_observed', 'n/a')}")

    return 0


def cmd_render(args: list[str]) -> int:
    if not args:
        print(
            "Usage: agep render <path/to/evidence_pack.json> [--out <output.md>] [--traceable]",
            file=sys.stderr,
        )
        return 2

    path_str = args[0]
    out_path: str | None = None
    traceable = False

    i = 1
    while i < len(args):
        if args[i] == "--out" and i + 1 < len(args):
            out_path = args[i + 1]
            i += 2
        elif args[i] == "--traceable":
            traceable = True
            i += 1
        else:
            value = args[i]
            if value.startswith("-"):
                print(f"Unknown flag: {value}", file=sys.stderr)
            else:
                print(f"Unexpected argument: {value}", file=sys.stderr)
            print(
                "Usage: agep render <path/to/evidence_pack.json> [--out <output.md>] [--traceable]",
                file=sys.stderr,
            )
            return 2

    pack = _load_pack(path_str)

    if traceable:
        from .trace_renderer import render_traceable_markdown
        md = render_traceable_markdown(pack)
    else:
        from .renderer import render_markdown
        md = render_markdown(pack)

    if out_path:
        out = Path(out_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(md, encoding="utf-8")
        print(f"Rendered to {out}")
    else:
        print(md)

    return 0


def cmd_import(args: list[str]) -> int:
    usage = (
        "Usage: agep import --manifest <manifest.json> --reconstruction <bundle.json> "
        "--out <evidence_pack.json> [--render <output.md>] [--generated-at <iso8601>]"
    )
    manifest_path: str | None = None
    reconstruction_path: str | None = None
    out_path: str | None = None
    render_path: str | None = None
    generated_at = "1970-01-01T00:00:00Z"

    i = 0
    while i < len(args):
        flag = args[i]
        if flag in {"--manifest", "--reconstruction", "--out", "--render", "--generated-at"} and i + 1 < len(args):
            value = args[i + 1]
            if flag == "--manifest":
                manifest_path = value
            elif flag == "--reconstruction":
                reconstruction_path = value
            elif flag == "--out":
                out_path = value
            elif flag == "--render":
                render_path = value
            elif flag == "--generated-at":
                generated_at = value
            i += 2
        else:
            print(usage, file=sys.stderr)
            return 2

    if not manifest_path or not reconstruction_path or not out_path:
        print(usage, file=sys.stderr)
        return 2

    from .importer import ImportErrorDetail, build_evidence_pack_from_files
    from .loader import dump_evidence_pack
    from .trace_renderer import render_traceable_markdown

    try:
        pack = build_evidence_pack_from_files(
            manifest_path,
            reconstruction_path,
            generated_at=generated_at,
        )
    except (FileNotFoundError, ValueError, ImportErrorDetail) as exc:
        print(f"Import error: {exc}", file=sys.stderr)
        return 1

    dump_evidence_pack(pack, out_path)
    print(f"Imported traceable evidence pack to {out_path}")

    if render_path:
        out = Path(render_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render_traceable_markdown(pack), encoding="utf-8")
        print(f"Rendered traceable evidence pack to {out}")

    return 0


def cmd_check_examples(args: list[str]) -> int:
    """Validate all examples/*.json and render each to examples/rendered/<stem>.md."""
    import glob as _glob

    repo_root = Path(__file__).parent.parent.parent
    examples_dir = repo_root / "examples"

    example_files = sorted(_glob.glob(str(examples_dir / "*.json")))
    if not example_files:
        print("No example files found.", file=sys.stderr)
        return 1

    from .loader import load_evidence_pack
    from .validator import validate_evidence_pack
    from .trace_renderer import render_traceable_markdown

    all_valid = True
    for file_path in example_files:
        try:
            pack = load_evidence_pack(file_path)
        except (FileNotFoundError, ValueError) as exc:
            print(f"LOAD ERROR  {file_path}: {exc}", file=sys.stderr)
            all_valid = False
            continue

        report = validate_evidence_pack(pack)
        status = "VALID  " if report.valid else "INVALID"
        error_count = sum(1 for i in report.issues if i.severity.value == "error")
        print(f"{status} {Path(file_path).name} ({error_count} error(s), {len(report.issues) - error_count} warning(s))")

        if not report.valid:
            all_valid = False
            for issue in report.issues:
                if issue.severity.value == "error":
                    print(f"  [ERROR] {issue.code}: {issue.message}")

        md = render_traceable_markdown(pack)
        rendered_dir = examples_dir / "rendered"
        rendered_dir.mkdir(parents=True, exist_ok=True)
        out_path = rendered_dir / (Path(file_path).stem + ".md")
        out_path.write_text(md, encoding="utf-8")

    return 0 if all_valid else 1


def main() -> None:
    argv = sys.argv[1:]
    if not argv:
        print(
            "Usage: agep <command> [args]\n"
            "Commands: validate, summarize, render, import, check-examples",
            file=sys.stderr,
        )
        sys.exit(2)

    command = argv[0]
    rest = argv[1:]

    if command == "validate":
        sys.exit(cmd_validate(rest))
    elif command == "summarize":
        sys.exit(cmd_summarize(rest))
    elif command == "render":
        sys.exit(cmd_render(rest))
    elif command == "import":
        sys.exit(cmd_import(rest))
    elif command == "check-examples":
        sys.exit(cmd_check_examples(rest))
    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        sys.exit(2)
