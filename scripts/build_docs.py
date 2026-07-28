#!/usr/bin/env python3
"""Assemble the mdBook source tree from authoritative project documents."""

from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "docs" / "src"
CHANGES: dict[str, str] = {
    "add-rust-cli-foundation": "cli-foundation",
    "depend-on-genesis": "cli-foundation",
}


def copy_with_notice(source: Path, destination: Path, notice: str) -> None:
    if not source.is_file():
        raise FileNotFoundError(f"required documentation source is missing: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(f"{notice}\n\n{source.read_text()}")


def build_summary() -> str:
    lines = [
        "# Summary",
        "",
        "[Home](./index.md)",
        "[Project Context](./project-context.md)",
        "[EARS Specification](./specification/ears.md)",
    ]

    if CHANGES:
        lines.append("")
        lines.append("# Roadmap")
        lines.append("")
        lines.append(f"- [Overview](./roadmap/index.md)")
        for change_id in CHANGES:
            lines.append(f"  - [`{change_id}`](./roadmap/{change_id}/proposal.md)")
            lines.append(f"    - [Capability delta](./roadmap/{change_id}/spec.md)")
            if (ROOT / "openspec" / "changes" / change_id / "design.md").is_file():
                lines.append(f"    - [Design](./roadmap/{change_id}/design.md)")
            lines.append(f"    - [Tasks](./roadmap/{change_id}/tasks.md)")
    else:
        lines.append("")
        lines.append("[Roadmap](./roadmap/index.md)")

    lines.append("")
    lines.append("[Contributing](./contributing.md)")
    lines.append("")
    return "\n".join(lines)


def build_roadmap_index() -> str:
    if not CHANGES:
        return "\n".join(
            [
                "# Implementation roadmap",
                "",
                "> **Status:** No OpenSpec changes are active yet.",
                "",
            ]
        )
    rows = []
    for change_id in CHANGES:
        tasks = (ROOT / "openspec" / "changes" / change_id / "tasks.md").read_text()
        completed = tasks.count("- [x]") + tasks.count("- [X]")
        pending = tasks.count("- [ ]")
        total = completed + pending
        rows.append(
            f"| [`{change_id}`]({change_id}/proposal.md) | Active proposal | "
            f"{completed}/{total} |"
        )
    return "\n".join(
        [
            "# Implementation roadmap",
            "",
            "> **Status:** These are active, unimplemented OpenSpec changes. They become built truth only after implementation, review, and archival.",
            "",
            "| Change | Status | Tasks complete |",
            "|---|---|---:|",
            *rows,
            "",
            "Each change page includes its proposal, capability delta, design, and approval-gated tracer-bullet task plan.",
            "",
        ]
    )


def main() -> None:
    # Copy static sources
    for static_file in ("index.md", "contributing.md"):
        src = SRC / static_file
        if not src.is_file():
            raise FileNotFoundError(f"required static doc source is missing: {src}")

    # Copy EARS specification
    copy_with_notice(
        ROOT / "crua-ears-spec.md",
        SRC / "specification" / "ears.md",
        "> **Document status:** Draft, not yet approved. The source file `crua-ears-spec.md` is authoritative.",
    )

    # Copy project context
    copy_with_notice(
        ROOT / "openspec" / "project.md",
        SRC / "project-context.md",
        "> **Source:** Generated from `openspec/project.md` during the documentation build.",
    )

    # Remove old roadmap if it exists, then generate fresh
    roadmap = SRC / "roadmap"
    if roadmap.exists():
        shutil.rmtree(roadmap)
    roadmap.mkdir(parents=True, exist_ok=True)
    (roadmap / "index.md").write_text(build_roadmap_index())

    notice = (
        "> **Status:** Active OpenSpec proposal; not implemented or deployed. "
        "The source under `openspec/changes/` is authoritative."
    )
    for change_id, capability in CHANGES.items():
        source = ROOT / "openspec" / "changes" / change_id
        destination = roadmap / change_id
        for name in ("proposal", "tasks"):
            copy_with_notice(source / f"{name}.md", destination / f"{name}.md", notice)
        if (source / "design.md").is_file():
            copy_with_notice(source / "design.md", destination / "design.md", notice)
        copy_with_notice(
            source / "specs" / capability / "spec.md",
            destination / "spec.md",
            notice,
        )

    # Generate SUMMARY.md
    (SRC / "SUMMARY.md").write_text(build_summary())

    print(f"assembled documentation sources in {SRC.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
