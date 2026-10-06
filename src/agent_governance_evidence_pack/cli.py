"""
CLI for Agent Governance Evidence Pack.

Entry point: agep
"""

from __future__ import annotations

import sys
from pathlib import Path


def _load_pack(path_str: str):
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
    for key in ("pack_id", "title", "review_status", "agent_name", "environment", "tool_count", "action_count", "privileged_action_count", "replay_bundle_count", "open_risk_count", "critical_open_risk_count"):
        print(f"{key:25}: {s[key]}")
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
        print("Usage: agep render <path/to/evidence_pack.json> [--out <output.md>] [--traceable]", file=sys.stderr)
        return 2
    path_str = args[0]
    out_path: str | None = None
    traceable = False
    i = 1
    while i < len(args):
        if args[i] == "--out" and i + 1 < len(args):
            out_path = args[i + 1]; i += 2
        elif args[i] == "--traceable":
            traceable = True; i += 1
        else:
            print(f"Unexpected argument: {args[i]}", file=sys.stderr)
            return 2
    pack = _load_pack(path_str)
    if traceable:
        from .trace_renderer import render_traceable_markdown
        md = render_traceable_markdown(pack)
    else:
        from .renderer import render_markdown
        md = render_markdown(pack)
    if out_path:
        out = Path(out_path); out.parent.mkdir(parents=True, exist_ok=True); out.write_text(md, encoding="utf-8"); print(f"Rendered to {out}")
    else:
        print(md)
    return 0


def cmd_import(args: list[str]) -> int:
    usage = "Usage: agep import --manifest <manifest.json> --reconstruction <bundle.json> --out <evidence_pack.json> [--render <output.md>]"
    manifest_path = reconstruction_path = out_path = render_path = None
    i = 0
    while i < len(args):
        flag = args[i]
        if flag in {"--manifest", "--reconstruction", "--out", "--render"} and i + 1 < len(args):
            value = args[i + 1]
            if flag == "--manifest": manifest_path = value
            elif flag == "--reconstruction": reconstruction_path = value
            elif flag == "--out": out_path = value
            elif flag == "--render": render_path = value
            i += 2
        else:
            print(usage, file=sys.stderr)
            return 2
    if not manifest_path or not reconstruction_path or not out_path:
        print(usage, file=sys.stderr)
        return 2
    from .importer import ImportContractError, build_evidence_pack_from_files
    from .loader import dump_evidence_pack
    from .trace_renderer import render_traceable_markdown
    try:
        pack = build_evidence_pack_from_files(manifest_path, reconstruction_path)
    except (FileNotFoundError, ValueError, ImportContractError) as exc:
        print(f"Import error: {exc}", file=sys.stderr)
        return 1
    dump_evidence_pack(pack, out_path)
    print(f"Imported traceable evidence pack to {out_path}")
    if render_path:
        out = Path(render_path); out.parent.mkdir(parents=True, exist_ok=True); out.write_text(render_traceable_markdown(pack), encoding="utf-8"); print(f"Rendered traceable evidence pack to {out}")
    return 0


def cmd_check_examples(args: list[str]) -> int:
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
            report = validate_evidence_pack(pack)
        except (FileNotFoundError, ValueError) as exc:
            print(f"LOAD ERROR  {file_path}: {exc}", file=sys.stderr)
            all_valid = False
            continue
        status = "VALID  " if report.valid else "INVALID"
        print(f"{status} {Path(file_path).name} ({len(report.issues)} issue(s))")
        if not report.valid:
            all_valid = False
        rendered_dir = examples_dir / "rendered"; rendered_dir.mkdir(parents=True, exist_ok=True)
        (rendered_dir / (Path(file_path).stem + ".md")).write_text(render_traceable_markdown(pack), encoding="utf-8")
    return 0 if all_valid else 1


def main() -> None:
    argv = sys.argv[1:]
    if not argv:
        print("Usage: agep <command> [args]\nCommands: validate, summarize, render, import, check-examples", file=sys.stderr)
        sys.exit(2)
    command, rest = argv[0], argv[1:]
    if command == "validate": sys.exit(cmd_validate(rest))
    if command == "summarize": sys.exit(cmd_summarize(rest))
    if command == "render": sys.exit(cmd_render(rest))
    if command == "import": sys.exit(cmd_import(rest))
    if command == "check-examples": sys.exit(cmd_check_examples(rest))
    print(f"Unknown command: {command}", file=sys.stderr)
    sys.exit(2)
