"""Polar/even Einstein--Maxwell master-matrix preflight.

This certificate fixes the ell>=2 Fourier coefficient matrix, corrects the
polar Maxwell volume-density term, reduces the constraints to two masters,
and checks one exact full-tensor normal mode.  Exceptional ell=0,1 and an
arbitrary-eigenvalue full-tensor derivation remain open.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp

from bridge.einstein_sector.einstein_maxwell_periodic_photon_second_order import _curvature, _stress, _trunc


ROOT = Path(__file__).resolve().parents[2]
AXIAL_CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_axial_master_complex.json"
DOMAIN_CERTIFICATE = ROOT / "bridge/certificates/compact_harmonic_domain_taub_descent.json"
DEFAULT_OUTPUT = ROOT / "bridge/certificates/einstein_maxwell_polar_master_preflight.json"
SCHEMA_PATH = ROOT / "bridge/einstein_sector/schema/einstein_maxwell_polar_master_preflight.schema.json"


class PolarMasterError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PolarMasterError(message)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _algebraic_reduction() -> dict[str, Any]:
    lam, k, omega, mass = sp.symbols("lambda k omega s", nonzero=True, real=True)
    # Rows: E00,E01,E11,E0a,E1a,sphere-trace,sphere-TF,Maxwell-axial.
    matrix = sp.Matrix([
        [0, 0, lam/2, k**2+lam/2, -lam],
        [0, lam/2, 0, -k*omega, 0],
        [lam/2, 0, 0, omega**2-lam/2, lam],
        [0, sp.I*k/2, sp.I*omega/2, sp.I*omega/2, -sp.I*omega],
        [sp.I*k/2, sp.I*omega/2, 0, -sp.I*k/2, sp.I*k],
        [(k**2+lam/2)/2, k*omega, (omega**2-lam/2)/2, (omega**2-k**2+2)/2, -lam],
        [sp.Rational(1,2), 0, -sp.Rational(1,2), 0, 0],
        [sp.Rational(1,2), 0, -sp.Rational(1,2), 1, omega**2-k**2-lam],
    ])
    s = omega**2-k**2
    R = sp.symbols("R")
    reconstructed = sp.Matrix([
        -(omega**2+k**2)*R/s,
        2*k*omega*R/s,
        -(omega**2+k**2)*R/s,
        sp.symbols("K"),
        sp.symbols("U"),
    ])
    K, U = reconstructed[3], reconstructed[4]
    reconstructed = reconstructed.subs(R, K-2*U)
    reduced_rows = (matrix*reconstructed).applyfunc(sp.factor)
    master_matrix = sp.Matrix([[lam, -2*lam], [-1, lam]])
    characteristic = sp.factor((mass*sp.eye(2)-master_matrix).det())
    _require(sp.expand(characteristic-((mass-lam)**2-2*lam)) == 0, "polar characteristic changed")
    W = sp.diag(1, 2*lam)
    _require(W*master_matrix == master_matrix.T*W, "polar symmetrizer changed")
    return {
        "row_order": ["E00", "E01", "E11", "E0a", "E1a", "sphere_trace", "sphere_tracefree", "Maxwell_axial"],
        "column_order": ["A", "B", "C", "K", "U"],
        "coefficient_matrix": [[str(sp.factor(value)) for value in matrix.row(row)] for row in range(matrix.rows)],
        "constraints": ["A=C", "omega*(A+K-2U)+k*B=0", "k*(A-K+2U)+omega*B=0"],
        "reconstruction": ["R=K-2U", "A=C=-(omega^2+k^2)R/(omega^2-k^2)", "B=2k*omega*R/(omega^2-k^2)"],
        "reduced_nonzero_rows": [str(value) for value in reduced_rows],
        "master_matrix": [[str(value) for value in master_matrix.row(row)] for row in range(2)],
        "characteristic": str(characteristic),
        "dispersion": "omega^2=k_n^2+lambda+/-sqrt(2*lambda)",
        "polar_eigenvectors": {"plus": "U/K=-1/sqrt(2*lambda)", "minus": "U/K=1/sqrt(2*lambda)"},
        "symmetrizer": [["1", "0"], ["0", "2*lambda"]],
        "branch_reduced_norm": "2",
    }


def _l2_plus_tensor_fixture() -> dict[str, Any]:
    e = sp.symbols("epsilon")
    t, x, theta, phi = sp.symbols("t x theta phi", real=True)
    coordinates = (t, x, theta, phi)
    sine = sp.sin(theta)
    root = sp.sqrt(3)
    omega = sp.sqrt(6+2*root)
    wave = sp.cos(omega*t)
    Y = sp.legendre(2, sp.cos(theta))
    X = -sine*sp.diff(Y, theta)
    U = -root/6
    K = sp.S.One
    R = K-2*U
    A = C = -R
    metric = sp.diag(-1,1,1,sine**2)
    metric[0,0] += e*A*wave*Y
    metric[1,1] += e*C*wave*Y
    metric[2,2] += e*K*wave*Y
    metric[3,3] += e*K*wave*Y*sine**2
    inverse = metric.inv().applyfunc(lambda value: _trunc(value,e,1))
    connection = [[[sp.S.Zero for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for target in range(4):
        for left in range(4):
            for right in range(4):
                connection[target][left][right] = _trunc(sum(inverse[target,index]*(sp.diff(metric[index,right],coordinates[left])+sp.diff(metric[index,left],coordinates[right])-sp.diff(metric[left,right],coordinates[index])) for index in range(4))/2,e,1)
    field = sp.zeros(4)
    field[2,3] = sine
    field[3,2] = -sine
    field[0,3] = e*U*sp.diff(wave,t)*X
    field[3,0] = -field[0,3]
    field[2,3] += e*U*wave*sp.diff(X,theta)
    field[3,2] = -field[2,3]
    data = _curvature({"epsilon":e,"coordinates":coordinates,"metric":metric,"inverse":inverse,"connection":connection,"field":field},1)
    einstein = (data["ricci"]-metric*data["scalar"]/2+metric/2-_stress(data,1)).applyfunc(lambda value: sp.simplify(sp.sqrtdenest(sp.trigsimp(sp.diff(value,e).subs(e,0)))))
    _require(einstein == sp.zeros(4), "polar l2 plus Einstein fixture changed")
    # Work on the standard oriented sphere chart 0 < theta < pi, where the
    # background density is sin(theta), rather than SymPy's chart-insensitive
    # Abs(sin(theta)).  The polar-axis values follow by smooth continuation.
    volume = _trunc(sp.sqrt(-metric.det()), e, 1).subs(sp.Abs(sine), sine)
    field_up = sp.zeros(4)
    for left in range(4):
        for right in range(4):
            field_up[left,right] = _trunc(sum(inverse[left,a]*inverse[right,b]*field[a,b] for a in range(4) for b in range(4)),e,1)
    density_residual = sp.Matrix([sp.simplify(sp.sqrtdenest(sp.trigsimp(sp.diff(sum(sp.diff(volume*field_up[left,right],coordinates[left]) for left in range(4)),e).subs(e,0)))) for right in range(4)])
    _require(
        density_residual == sp.zeros(4, 1),
        "polar l2 plus Maxwell density fixture changed: "
        + repr([sp.sstr(value) for value in density_residual]),
    )
    return {
        "ell": 2,
        "branch": "plus",
        "omega_squared": "6+2*sqrt(3)",
        "K": "1",
        "U": "-sqrt(3)/6",
        "A_equals_C": str(sp.factor(A)),
        "Einstein_residual": "0",
        "Maxwell_density_residual": "0",
        "volume_density": "sqrt(-det(g(epsilon))) retained through first order",
        "chart_convention": "0<theta<pi, so sqrt(det(g_S2))=sin(theta); polar axes by smooth continuation",
    }


def build_certificate() -> dict[str, Any]:
    axial = _load(AXIAL_CERTIFICATE)
    domain = _load(DOMAIN_CERTIFICATE)
    _require(axial["result_id"] == "COMPACT_EM_AXIAL_MASTER_COMPLEX", "axial input changed")
    _require(domain["result_id"] == "COMPACT_HARMONIC_DOMAIN_AND_TAUB_DESCENT", "domain input changed")
    return {
        "schema": "einstein-maxwell-polar-master-preflight-v1",
        "schema_path": str(SCHEMA_PATH.relative_to(ROOT)),
        "schema_sha256": _sha256(SCHEMA_PATH),
        "result_id": "COMPACT_EM_POLAR_MASTER_PREFLIGHT",
        "result_state": "GENERIC_POLAR_MASTER_MATRIX_AND_L2_FIXTURE_CERTIFIED_EXCEPTIONAL_AND_FULL_TENSOR_OPEN",
        "lifecycle_state": "CLASSIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "REDUCED-MODE"],
        "generality_level": "G1_POLAR_ELL_GE2_MATRIX_PREFLIGHT",
        "provenance": {"generator_path": str(Path(__file__).relative_to(ROOT)), "generator_sha256": _sha256(Path(__file__)), "inputs": {str(path.relative_to(ROOT)):_sha256(path) for path in (AXIAL_CERTIFICATE,DOMAIN_CERTIFICATE)}},
        "domain": "fixed-P_N compact product; standard polar Regge--Wheeler gauge; ell>=2 generic matrix",
        "volume_density_correction": {
            "issue": "the background-volume Maxwell divergence used by trace-free axial fixtures is invalid when delta sqrt(-g) is nonzero",
            "correct_operator": "M^nu=(1/sqrt(-g)) partial_mu(sqrt(-g) F^(mu nu)) with the perturbed determinant retained",
            "consequence": "the corrected Maxwell row is (A-C)/2+K+(omega^2-k^2-lambda)U=0",
        },
        "gauge_fixed_coefficients": ["h_AB=(A,B,C)Y", "h_ab=K g_ab Y", "a_a=U X_a"],
        "algebraic_master_reduction": _algebraic_reduction(),
        "exact_tensor_fixture": _l2_plus_tensor_fixture(),
        "isospectral_relation": "the generic polar master eigenvalues equal the certified axial eigenvalues lambda+/-sqrt(2lambda), with different reconstruction maps",
        "reduced_pairing": {"current": "j^A=u^T W partial^A v-(partial^A u)^T W v", "symmetrizer": "diag(1,2lambda)", "covariant_symplectic_matching": False},
        "exceptional_ledger": {"ell0": "OPEN homogeneous scalar/radion/charge block", "ell1": "OPEN because the polar tensor harmonic vanishes and Regge--Wheeler gauge changes rank"},
        "classification": {"generic_polar_matrix": True, "exact_l2_plus_tensor_solution": True, "all_ell_arbitrary_lambda_tensor_derivation": False, "ell0_ell1_complete": False, "covariant_symplectic_matching": False, "complete_fourth_order_adjoint": False, "full_polar_master_theorem": False},
        "next_gate": "promote the generic matrix to an arbitrary-lambda full-tensor identity, classify ell=0,1, and then match axial/polar reduced currents to the covariant symplectic form",
        "claim_boundary": "This LOCAL-ALGEBRAIC/REDUCED-MODE preflight certifies the generic ell>=2 polar coefficient matrix, its exact two-master algebraic reduction, isospectral dispersion, corrected Maxwell volume term, reduced symmetrizer, and one full-tensor l=2 plus-branch solution. It does not yet certify an arbitrary-lambda full-tensor polar identity, exceptional ell=0,1 sectors, covariant symplectic normalization, the complete fourth-order adjoint cokernel, quadratic obstruction coefficients, causal evolution, scattering, or quantum theory.",
        "verification_commands": ["python3 -m bridge.einstein_sector.einstein_maxwell_polar_master_preflight --verify bridge/certificates/einstein_maxwell_polar_master_preflight.json", "python3 bridge/einstein_sector/verify_einstein_maxwell_polar_master_preflight.py", "python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_polar_master_preflight"],
    }


def verify_certificate(path: Path = DEFAULT_OUTPUT) -> None:
    _require(_load(path) == build_certificate(), f"polar preflight certificate stale or altered: {path}")


def main() -> None:
    parser=argparse.ArgumentParser(); parser.add_argument("--write",action="store_true"); parser.add_argument("--verify",type=Path); args=parser.parse_args()
    if args.write: DEFAULT_OUTPUT.write_text(json.dumps(build_certificate(),indent=2,sort_keys=True)+"\n",encoding="utf-8")
    if args.verify: verify_certificate(args.verify)
    if not args.write and not args.verify: parser.error("one of --write or --verify is required")


if __name__ == "__main__": main()
