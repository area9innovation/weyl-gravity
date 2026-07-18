"""BH-2A stage 4: nonzero Einstein x extra horizon flux (fixture level).

Fail-closed builder for
`black_hole_programme/certificates/BH2A_CROSS_FLUX.json`.

Verdict: BH2A_CROSS_BLOCK_NONZERO_HORIZON_FLUX_FIXTURES.

Method (m = 1, l = 2, ingoing-analytic modes, exact series arithmetic,
NORD = 16): the composition route of `axial_flux_modes.py` builds the
ingoing Regge--Wheeler mode from the certified master equation and the
ingoing extra-branch modes by forward recurrence of dRic[h] = psi with the
certified carrier solutions as source; conjugate (-omega) partners are
exact complex conjugates, so pairings are Hermitian data.  The certified
Lee--Wald bilinear F^r (BH2A_FLUX_MATRIX) is evaluated at two interior
radii; on-shell conservation makes it r-independent, and the in-run
RW x RW null control (certified to vanish exactly) bounds the truncation
error.

Certified fixture facts, at omega in {3/5, 2/7} and radii {65/32, 33/16}:

1. null control: |F^r(RW, conj RW)| < 1e-12 |F^r(extra, conj extra)|;
2. extra-branch Hermitian horizon-flux norm: F^r(extra, conj extra) is
   exactly imaginary with Im < 0, stable across radii to < 2 percent:
   i F^r = +|value| pi alpha > 0 for alpha > 0 at both frequencies
   (no ghost-null degeneracy of the ingoing extra family at the horizon;
   the physical sign convention for alpha remains a theory-level choice
   recorded open since BH-0);
3. Einstein x extra cross pairing: |F^r(RW, conj extra)| is nonzero
   (bounded below by |ee|/10) at both frequencies: the branches exchange
   symplectic flux through the horizon; with the certified null RW block,
   ALL horizon flux pairing lives in the mixed and extra sectors.

NOT claimed: exact symbolic omega-dependence, general l or m, amplitude-
normalization-independent value of the cross phase, outer-boundary
counterpart, causal disposition, stability, ringdown.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import sympy as sp

from axial_flux_modes import run_pipeline

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "certificates" / "BH2A_CROSS_FLUX.json"
SCHEMA_PATH = HERE / "schema" / "bh2a-cross-flux-v1.schema.json"
FLUX_CERT = HERE / "certificates" / "BH2A_FLUX_MATRIX.json"
REACH_CERT = HERE / "certificates" / "BH2A_HORIZON_REACH.json"

SCHEMA_NAME = "pure-weyl-bh2a-cross-flux-v1"
RESULT_ID = "PURE_WEYL_BH2A_CROSS_FLUX"
RESULT_TOKEN = "BH2A_CROSS_BLOCK_NONZERO_HORIZON_FLUX_FIXTURES"

FREQS = [sp.Rational(3, 5), sp.Rational(2, 7)]
NORD = 16


class CrossFluxError(RuntimeError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise CrossFluxError(msg)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_certificate() -> dict:
    alpha = sp.Symbol("alpha")
    fixtures = []
    receipts = {}
    for wnum in FREQS:
        t0 = time.time()
        out = run_pipeline(wnum, NORD=NORD)
        receipts[f"omega_{wnum}"] = round(time.time() - t0, 1)
        print(f"[omega={wnum}] pipeline {receipts[f'omega_{wnum}']} s", flush=True)
        ctrl = [sp.simplify(v / (sp.pi * alpha)) for v in out["control"]]
        cross = [sp.simplify(v / (sp.pi * alpha)) for v in out["cross"]]
        ee = [sp.simplify(v / (sp.pi * alpha)) for v in out["ee"]]
        for e in ee:
            _require(sp.re(e) == 0, "extra-extra pairing not exactly imaginary")
            _require(sp.im(e) < 0, "extra-extra pairing sign unexpected")
        for c, e in zip(ctrl, ee):
            _require(
                sp.Abs(c) ** 2 * sp.Integer(10) ** 24 < sp.Abs(e) ** 2,
                "null control exceeds 1e-12 of the signal",
            )
        stab = sp.Abs(ee[0] - ee[1]) ** 2 * sp.Integer(2500)
        _require(stab < sp.Abs(ee[0]) ** 2, "extra-extra not radius-stable to 2 percent")
        for c in cross:
            _require(sp.Abs(c) ** 2 * sp.Integer(100) > sp.Abs(ee[0]) ** 2,
                     "cross pairing not bounded below")
        fixtures.append({
            "omega": str(wnum),
            "radii": ["65/32", "33/16"],
            "control_over_pi_alpha_float": [str(complex(sp.N(c, 6))) for c in ctrl],
            "cross_over_pi_alpha_float": [str(complex(sp.N(c, 8))) for c in cross],
            "ee_over_pi_alpha_float": [str(complex(sp.N(e, 8))) for e in ee],
            "ee_im_sign": "negative (i*F^r positive for alpha > 0)",
        })
    certificate = {
        "schema": SCHEMA_NAME,
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": RESULT_ID,
        "result_token": RESULT_TOKEN,
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "declaration": {
            "theory": "pure-Weyl gravity L = alpha C_abcd C^abcd",
            "background_family": "Schwarzschild, m = 1 fixture",
            "conformal_frame": "working gauge; t-chart bilinear with exact e^{i omega r*} mode factors",
            "generator": "none; bilinear pairings of ingoing-analytic modes",
            "phase_space": "axial l = 2 ingoing modes at omega in {3/5, 2/7}; conjugate partners exact",
            "horizon_condition": "ingoing analyticity (certified BH2A_HORIZON_REACH families)",
            "infinity_condition": "none; interior-radius evaluation via on-shell r-independence",
            "lifecycle": "CLASSIFIED",
        },
        "method": {
            "pipeline": "black_hole_programme/axial_flux_modes.py (composition route)",
            "series_order": NORD,
            "validation": "in-run RW x RW null control (certified exact zero) bounds truncation at < 1e-12 relative; radius stability < 2 percent; conjugate-basis Hermitian pairing",
        },
        "fixtures": fixtures,
        "conclusions": {
            "extra_norm": "the ingoing extra-branch family carries a nonzero Hermitian horizon-flux norm, i F^r(extra, conj extra) = +|v| pi alpha > 0 for alpha > 0, at both frequencies",
            "cross": "the Einstein x extra cross pairing is nonzero at both frequencies: the branches exchange symplectic flux through the horizon",
            "structure": "with the certified null RW block, all horizon flux pairing lives in the mixed and extra sectors",
        },
        "claim_flags": {
            "null_control_certified": True,
            "extra_norm_nonzero_certified": True,
            "extra_norm_sign_certified": True,
            "cross_nonzero_certified": True,
            "frequency_robustness_two_points": True,
            "symbolic_omega_dependence_certified": False,
            "general_l_or_m_certified": False,
            "outer_boundary_counterpart_certified": False,
            "causal_disposition_decided": False,
            "stability_or_ringdown_certified": False,
        },
        "missing_objects": [
            "exact symbolic omega-dependence of the flux blocks",
            "general l, general m, polar sector",
            "outer-boundary flux counterpart and falloff domains",
            "causal disposition of the extra branch (BH-2A closure)",
            "any stability or ringdown statement",
        ],
        "stage_seconds": receipts,
        "provenance": {
            "generator_path": "black_hole_programme/bh2a_cross_flux.py",
            "pipeline_path": "black_hole_programme/axial_flux_modes.py",
            "pipeline_sha256": _sha256(HERE / "axial_flux_modes.py"),
            "flux_certificate": str(FLUX_CERT.relative_to(ROOT)),
            "flux_certificate_sha256": _sha256(FLUX_CERT),
            "reach_certificate": str(REACH_CERT.relative_to(ROOT)),
            "reach_certificate_sha256": _sha256(REACH_CERT),
        },
        "verification_command": "python3 black_hole_programme/verify_bh2a_cross_flux.py",
    }
    return certificate


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    certificate = build_certificate()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
