#!/usr/bin/env python3
"""Fail fast when a claim map's manuscript or compiled-PDF hash drifts.

This is deliberately narrower than a general current-path audit: historical
and superseded evidence pins are allowed to differ from the working tree.
Only claim-map fields that explicitly bind their own manuscript/PDF are
checked here.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PAPER = ROOT / "paper"


class PinDriftError(AssertionError):
    pass


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _manuscript_path(claim_map: Path, value: dict) -> Path | None:
    declared = value.get("manuscript")
    if isinstance(declared, str):
        return ROOT / declared
    if "paper_sha256" in value:
        stem = claim_map.name.removesuffix("-claim-map.json")
        candidate = PAPER / f"{stem}.tex"
        return candidate if candidate.is_file() else None
    return None


def verify() -> list[tuple[str, str]]:
    checked: list[tuple[str, str]] = []
    for claim_map in sorted(PAPER.glob("*-claim-map.json")):
        value = json.loads(claim_map.read_text(encoding="utf-8"))
        manuscript = _manuscript_path(claim_map, value)
        manuscript_sha = value.get("paper_sha256", value.get("manuscript_sha256"))
        if manuscript is not None and isinstance(manuscript_sha, str):
            if not manuscript.is_file():
                raise PinDriftError(f"missing manuscript: {manuscript}")
            actual = _sha256(manuscript)
            if actual != manuscript_sha:
                raise PinDriftError(
                    f"{claim_map.relative_to(ROOT)} manuscript pin drift: "
                    f"{manuscript.relative_to(ROOT)} expected {manuscript_sha}, "
                    f"got {actual}"
                )
            checked.append((str(claim_map.relative_to(ROOT)), "manuscript"))

        compiled_pdf = value.get("compiled_pdf")
        compiled_pdf_sha = value.get("compiled_pdf_sha256")
        if isinstance(compiled_pdf, str) and isinstance(compiled_pdf_sha, str):
            path = ROOT / compiled_pdf
            if not path.is_file():
                raise PinDriftError(f"missing compiled PDF: {path}")
            actual = _sha256(path)
            if actual != compiled_pdf_sha:
                raise PinDriftError(
                    f"{claim_map.relative_to(ROOT)} PDF pin drift: "
                    f"{path.relative_to(ROOT)} expected {compiled_pdf_sha}, "
                    f"got {actual}"
                )
            checked.append((str(claim_map.relative_to(ROOT)), "compiled_pdf"))

    if not checked:
        raise PinDriftError("no manuscript or PDF claim-map pins were discovered")
    return checked


def main() -> None:
    checked = verify()
    print(
        "PAPER MANUSCRIPT PIN AUDIT: PASS "
        f"({len(checked)} explicit manuscript/PDF bindings)"
    )


if __name__ == "__main__":
    main()
