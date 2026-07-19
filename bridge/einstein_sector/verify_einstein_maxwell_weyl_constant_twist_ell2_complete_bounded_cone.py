"""Independent verifier for the complete constant-twist plus ell2 cone."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_constant_twist_ell2_complete_bounded_cone.json"
SCHEMA = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_weyl_constant_twist_ell2_complete_bounded_cone.schema.json"


def main() -> None:
    value = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    assert value["schema_sha256"] == hashlib.sha256(SCHEMA.read_bytes()).hexdigest()
    provenance = value["provenance"]
    assert provenance["generator_sha256"] == hashlib.sha256((ROOT / provenance["generator_path"]).read_bytes()).hexdigest()
    for record in provenance["inputs"].values():
        assert record["sha256"] == hashlib.sha256((ROOT / record["path"]).read_bytes()).hexdigest()

    root = sp.sqrt(3)
    frequencies = {"minus": 6 - 2 * root, "extra": sp.Rational(16, 3), "plus": 6 + 2 * root}
    for shell, mu in frequencies.items():
        for output_ell, eigenvalue in ((1, 2), (3, 12)):
            p_value = sp.factor(mu - eigenvalue + sp.Rational(2, 3))
            q_value = sp.factor(mu**2 - 2 * eigenvalue * mu + eigenvalue * (eigenvalue - 2))
            assert p_value != 0 and q_value != 0
            if output_ell == 1:
                axial_determinant = sp.factor(mu * (mu - 4) * (3 * mu - 4))
                polar_determinant = sp.factor((mu - 4) * (3 * mu - 4) / 2)
            else:
                axial_determinant = polar_determinant = sp.factor(p_value**2 * q_value)
            ledger = value["nonresonant_output_ledger"][shell][f"L{output_ell}"]
            assert ledger["p"] == str(p_value) and ledger["q"] == str(q_value)
            assert ledger["axial_reduced_determinant"] == str(axial_determinant)
            assert ledger["polar_reduced_determinant"] == str(polar_determinant)
            assert axial_determinant != 0 and polar_determinant != 0

    ell = 2
    raising = sp.zeros(5)
    for column, m in enumerate(range(-ell, ell)):
        raising[column + 1, column] = sp.sqrt((ell - m) * (ell + m + 1))
    generators = ((raising + raising.T) / 2, (raising - raising.T) / (2 * sp.I), sp.diag(-2, -1, 0, 1, 2))
    off_axis = sp.Matrix([1, 0, 0, 0, 1])
    assert [sp.simplify((sp.conjugate(off_axis).T * generator * off_axis)[0]) for generator in generators] == [0, 0, 0]
    minus_occupation = sp.factor(2 * frequencies["extra"] / frequencies["minus"])
    witness = value["independence_witnesses"]["off_axis_survivor"]
    assert witness["balancing_Einstein_minus_m0_occupation"] == str(minus_occupation)
    assert witness["action_normalized_extra_occupation"] == "18"
    assert witness["action_normalized_balancing_Einstein_minus_occupation"] == "24+8*sqrt(3)"
    assert sp.simplify(2 * frequencies["extra"] - frequencies["minus"] * minus_occupation) == 0

    classification = value["classification"]
    assert classification["bounded_zero_locus_necessary_and_sufficient"] is True
    assert classification["twist_velocity_or_other_global_tangents_classified"] is False
    assert value["correction_classes"]["CAUSAL_RETARDED"]["status"] == "NO_CERTIFIED_MAP"
    assert value["quadratic_Noether_compatibility"]["axial_and_polar_ungauged_complexes_imported"] is True
    print("EINSTEIN_MAXWELL_WEYL_CONSTANT_TWIST_ELL2_COMPLETE_BOUNDED_CONE independent verification: PASS")


if __name__ == "__main__":
    main()
