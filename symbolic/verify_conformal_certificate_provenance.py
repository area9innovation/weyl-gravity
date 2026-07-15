#!/usr/bin/env python3
"""Mutation-test the shared certificate provenance helper."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from covariant_completion.certificate_provenance import (
    DigestMode,
    ProvenanceInput,
    digest_file,
    digest_inputs,
    digest_json_object,
    load_json_object,
    validate_digest_ledger,
)


def _rejects(action: object) -> bool:
    try:
        action()  # type: ignore[operator]
    except (TypeError, ValueError, FileNotFoundError, json.JSONDecodeError):
        return True
    return False


def main() -> int:
    checks: dict[str, bool] = {}
    with TemporaryDirectory() as temporary:
        root = Path(temporary)
        first = root / "first.json"
        second = root / "second.json"
        first.write_text('{"b": 2, "a": 1}\n', encoding="utf-8")
        second.write_text('{\n  "a": 1,\n  "b": 2\n}\n', encoding="utf-8")

        canonical_first = digest_file(
            first, mode=DigestMode.CANONICAL_JSON, root=root
        )
        canonical_second = digest_file(
            second, mode=DigestMode.CANONICAL_JSON, root=root
        )
        raw_first = digest_file(first, mode=DigestMode.RAW_FILE, root=root)
        raw_second = digest_file(second, mode=DigestMode.RAW_FILE, root=root)
        checks["canonical_ignores_presentation"] = canonical_first == canonical_second
        checks["raw_binds_presentation"] = raw_first != raw_second
        checks["canonical_value_api_matches_file"] = canonical_first == (
            digest_json_object(load_json_object(first, root=root))
        )

        inputs = {
            "semantic": ProvenanceInput(first, DigestMode.CANONICAL_JSON),
            "bytes": ProvenanceInput(first, DigestMode.RAW_FILE),
        }
        expected_keys = ("semantic", "bytes")
        ledger = digest_inputs(inputs, expected_keys=expected_keys, root=root)
        checks["exact_ledger_accepts"] = validate_digest_ledger(
            ledger, ledger, expected_keys=expected_keys
        )
        checks["missing_key_rejected"] = not validate_digest_ledger(
            {"semantic": ledger["semantic"]}, ledger, expected_keys=expected_keys
        )
        checks["extra_key_rejected"] = not validate_digest_ledger(
            {**ledger, "extra": ledger["bytes"]}, ledger, expected_keys=expected_keys
        )
        mutated = dict(ledger)
        mutated["semantic"] = "0" * 64
        checks["digest_mutation_rejected"] = not validate_digest_ledger(
            mutated, ledger, expected_keys=expected_keys
        )
        checks["implicit_mode_rejected"] = _rejects(
            lambda: digest_file(first, mode="raw", root=root)  # type: ignore[arg-type]
        )
        outside = root.parent / "outside-provenance.json"
        outside.write_text("{}\n", encoding="utf-8")
        try:
            checks["root_escape_rejected"] = _rejects(
                lambda: digest_file(
                    outside, mode=DigestMode.RAW_FILE, root=root
                )
            )
            link = root / "escape.json"
            link.symlink_to(outside)
            checks["symlink_escape_rejected"] = _rejects(
                lambda: digest_file(link, mode=DigestMode.RAW_FILE, root=root)
            )
        finally:
            outside.unlink(missing_ok=True)

        first.write_text('{"b": 3, "a": 1}\n', encoding="utf-8")
        checks["content_mutation_changes_canonical_digest"] = (
            digest_file(first, mode=DigestMode.CANONICAL_JSON, root=root)
            != canonical_first
        )

    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise AssertionError("certificate provenance guards failed: " + ", ".join(failed))
    print(f"CERTIFICATE PROVENANCE GUARDS: {len(checks)}/{len(checks)} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
