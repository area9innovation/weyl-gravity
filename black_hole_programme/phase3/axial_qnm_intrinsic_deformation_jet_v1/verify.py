#!/usr/bin/env python3
"""Independent verifier for the intrinsic-deformation jet certificate."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificate.json"
SCHEMA = HERE / "schema.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(value: str | int) -> sp.Expr:
    names = (
        "L S x y tau a b u v alpha beta nu "
        "A_in A_out b_in b_out "
        "A_in_bar A_out_bar b_in_bar b_out_bar "
        "z omega_j k a_2 b_1 u_0 u_tau "
        "X_H0 X_H1 X_p0 X_p1 Y_H0 Y_H1 Y_p0 Y_p1 "
        "omega omega_1 omega_2 omega_3 kappa_1 kappa_2 kappa_3 "
        "zeta inverse_zeta c d f "
        "a_1 b_1 c_1 d_1 f_1 a_2p b_2p c_2p d_2p f_2p"
    ).split()
    return sp.sympify(
        value,
        locals={name: sp.Symbol(name) for name in names},
    )


def matrix(rows: list[list[str]]) -> sp.Matrix:
    return sp.Matrix([[parse(value) for value in row] for row in rows])


def verify_document(document: dict) -> list[str]:
    errors: list[str] = []
    if document.get("schema") != (
        "phase3-axial-qnm-intrinsic-deformation-jet-v1"
    ):
        errors.append("schema drift")
    if document.get("dependency_tags") != [
        "LOCAL-ALGEBRAIC", "REDUCED-MODE"
    ]:
        errors.append("dependency-tag drift")
    if document.get("status") != (
        "EXACT_DUAL_NUMBER_JET_QNM_SHIFT_UNEVALUATED"
    ):
        errors.append("status drift")

    imported: dict[str, dict] = {}
    expected_schemas = {
        "projective_cocycle": "phase3-axial-qnm-projective-cocycle-v1",
        "local_smith_dichotomy": (
            "phase3-axial-qnm-local-smith-dichotomy-v1"
        ),
    }
    for name, expected_schema in expected_schemas.items():
        reference = document.get("imports", {}).get(name, {})
        path = ROOT / reference.get("path", "")
        if not path.is_file():
            errors.append(f"missing imported certificate: {name}")
            continue
        if sha256(path) != reference.get("sha256"):
            errors.append(f"input hash drift: {name}")
            continue
        value = json.loads(path.read_text())
        imported[name] = value
        if value.get("schema") != expected_schema:
            errors.append(f"import schema drift: {name}")
        if reference.get("schema") != expected_schema:
            errors.append(f"recorded import schema drift: {name}")
        if reference.get("status") != value.get("status"):
            errors.append(f"recorded import status drift: {name}")
    if len(imported) != 2:
        return errors
    if not imported["projective_cocycle"]["claim_flags"].get(
        "generic_rational_cocycle_nontrivial"
    ):
        errors.append("projective cocycle premise is not certified")
    if not imported["local_smith_dichotomy"]["claim_flags"].get(
        "local_smith_dichotomy_exact"
    ):
        errors.append("local Smith premise is not certified")

    schema_reference = document["provenance"]["schema"]
    if (schema_reference.get("path") != "schema.json"
            or schema_reference.get("sha256") != sha256(SCHEMA)):
        errors.append("schema provenance drift")

    tau = sp.Symbol("tau")
    L, S, x, y = sp.symbols("L S x y")
    independent_jet = sp.rem(
        sp.expand((L + tau * S) * (y + tau * x)),
        tau**2,
        tau,
    )
    if sp.expand(independent_jet - (L * y + tau * (L * x + S * y))) != 0:
        errors.append("independent operator jet derivation failed")
    if sp.expand(
        parse(document["operator_jet"]["expanded_mod_tau_squared"])
        - independent_jet
    ) != 0:
        errors.append("recorded operator jet drift")
    if not document["operator_jet"].get("identity_verified"):
        errors.append("operator jet exact flag missing")
    if document["operator_jet"].get("physical_parameter_tangent_claimed"):
        errors.append("auxiliary tau was promoted to a physical parameter")

    dual = document["dual_number_connection"]
    if dual.get("basis") != ["epsilon", "1"]:
        errors.append("dual-number basis convention drift")
    regular = matrix(dual["regular_matrix"])
    a, b, u, v = sp.symbols("a b u v")
    expected_regular = sp.Matrix([[a, b], [0, a]])
    if regular != expected_regular:
        errors.append("dual-number regular matrix drift")
    output = regular * sp.Matrix([u, v])
    recorded_output = sp.Matrix([
        parse(value) for value in dual["output_coefficients"]
    ])
    if output != sp.Matrix([a * u + b * v, a * v]):
        errors.append("independent dual-number multiplication failed")
    if recorded_output != output:
        errors.append("recorded dual-number output drift")
    if dual.get("analytic_endpoint_compatible_frames_constructed"):
        errors.append("analytic endpoint frames falsely claimed")

    shift = document["simple_zero_shift"]
    alpha, beta = sp.symbols("alpha beta")
    nu = sp.Symbol("nu")
    equation = alpha * nu + beta
    if parse(shift["chain_equation"]) != equation:
        errors.append("simple-zero chain equation drift")
    solved = -beta / alpha
    if sp.simplify(parse(shift["omega_prime"]) - solved) != 0:
        errors.append("simple-zero derivative formula drift")
    if sp.simplify(parse(shift["kappa"]) + solved) != 0:
        errors.append("kappa/shift sign drift")
    if shift.get("simple_QNM_supplied") or shift.get("beta_n_evaluated"):
        errors.append("QNM input or beta evaluation falsely claimed")

    conditional_connection = document["conditional_global_connection"]
    if conditional_connection.get("hypotheses_certified_here"):
        errors.append("global connection hypotheses falsely certified")
    if conditional_connection.get("global_b_derivative_established"):
        errors.append("global b derivative falsely established")

    flux = document["conditional_flux_variation"]
    ain, aout, bin_, bout = sp.symbols("A_in A_out b_in b_out")
    ain_bar, aout_bar, bin_bar, bout_bar = sp.symbols(
        "A_in_bar A_out_bar b_in_bar b_out_bar"
    )
    independent_flux_derivative = (
        ain_bar * bin_ + ain * bin_bar
        - aout_bar * bout - aout * bout_bar
    )
    if sp.expand(
        parse(flux["formal_derivative"]) - independent_flux_derivative
    ) != 0:
        errors.append("conditional flux derivative drift")
    if flux.get("hypotheses_certified_here"):
        errors.append("flux hypotheses falsely certified")
    if flux.get("flux_theorem_established"):
        errors.append("flux theorem falsely claimed")

    partial = document["partial_jet_functor"]
    a, b, c, d, f_scalar = sp.symbols("a b c d f")
    jet = sp.Matrix([
        [a, b, c],
        [0, a, d],
        [0, 0, f_scalar],
    ])
    if partial["ordered_basis"] != [
        "epsilon*spin2", "spin2", "spin1"
    ]:
        errors.append("partial-jet basis drift")
    if matrix(partial["jet_matrix"]) != jet:
        errors.append("partial-jet matrix drift")
    expected_inverse = sp.Matrix([
        [1 / a, -b / a**2, (b * d - a * c) / (a**2 * f_scalar)],
        [0, 1 / a, -d / (a * f_scalar)],
        [0, 0, 1 / f_scalar],
    ])
    recorded_inverse = matrix(partial["inverse"])
    if sp.simplify(jet * recorded_inverse - sp.eye(3)) != sp.zeros(3):
        errors.append("partial-jet inverse failed")
    if sp.simplify(recorded_inverse - expected_inverse) != sp.zeros(3):
        errors.append("recorded partial-jet inverse drift")
    if sp.simplify(
        matrix(partial["inverse_expected"]) - expected_inverse
    ) != sp.zeros(3):
        errors.append("recorded expected partial-jet inverse drift")

    multiplicativity = partial["multiplicativity"]
    jet1 = matrix(multiplicativity["J_C1"])
    jet2 = matrix(multiplicativity["J_C2"])
    jet_product = matrix(multiplicativity["J_C1C2"])
    if sp.simplify(jet1 * jet2 - jet_product) != sp.zeros(3):
        errors.append("partial-jet multiplicativity failed")
    if not multiplicativity.get("verified"):
        errors.append("partial-jet multiplicativity exact flag lost")
    ratios = partial["extension_ratios"]
    if (
        parse(ratios["partial_tau_inverse_a"]) != -b / a**2
        or parse(ratios["M"]) != -d / (a * f_scalar)
        or sp.simplify(
            parse(ratios["partial_tau_M"])
            - (b * d - a * c) / (a**2 * f_scalar)
        ) != 0
    ):
        errors.append("partial-jet extension ratio drift")
    if not partial.get("inverse_identity_verified"):
        errors.append("partial-jet inverse exact flag lost")
    if not partial.get("ratio_identities_verified"):
        errors.append("partial-jet ratio exact flag lost")
    for field in (
        "compatible_endpoint_partial_jet_frames_constructed",
        "matching_tau_family_constructed",
        "T_plus_recovered",
        "scattering_identity_recovered",
    ):
        if partial.get(field):
            errors.append(f"partial-jet physical field promoted: {field}")

    contour = document["conditional_contour_moments"]
    z = sp.Symbol("z")
    omega_j = sp.Symbol("omega_j")
    alpha, beta = sp.symbols("alpha beta")
    a2, b1 = sp.symbols("a_2 b_1")
    a_local = alpha * z + a2 * z**2
    b_local = beta + b1 * z
    zero_count_residue = sp.simplify(
        sp.limit(z * sp.diff(a_local, z) / a_local, z, 0)
    )
    if parse(contour["local_zero_count_residue"]) != zero_count_residue:
        errors.append("local zero-count residue drift")
    recorded_local = contour["local_model"]
    if sp.expand(parse(recorded_local["a"]) - a_local) != 0:
        errors.append("contour local a model drift")
    if sp.expand(parse(recorded_local["b"]) - b_local) != 0:
        errors.append("contour local b model drift")
    # Independently evaluate three moments.  The same local calculation gives
    # omega_j**k*beta/alpha for every nonnegative integer k.
    for power in range(3):
        residue = sp.simplify(sp.limit(
            z * (omega_j + z)**power * b_local / a_local,
            z,
            0,
        ))
        if sp.simplify(residue - omega_j**power * beta / alpha) != 0:
            errors.append(f"local contour residue failed at k={power}")
    k = sp.Symbol("k")
    if sp.simplify(
        parse(contour["local_moment_residue"])
        - omega_j**k * beta / alpha
    ) != 0:
        errors.append("recorded general contour residue drift")
    renormalization = contour["endpoint_renormalization"]
    u0, u_tau = sp.symbols("u_0 u_tau")
    a, b = sp.symbols("a b")
    quotient_shift = sp.cancel(
        (u_tau * a + u0 * b) / (u0 * a) - b / a
    )
    if sp.simplify(
        parse(renormalization["quotient_shift"]) - quotient_shift
    ) != 0:
        errors.append("endpoint-renormalization quotient drift")
    if not contour.get("identity_verified"):
        errors.append("conditional contour theorem exact flag lost")
    if contour.get("analytic_domain_supplied"):
        errors.append("analytic contour domain falsely supplied")
    if contour.get("contour_evaluated"):
        errors.append("contour moment falsely evaluated")
    if contour.get("physical_QNM_zero_count_certified"):
        errors.append("physical QNM zero count falsely certified")

    tangent = document["conditional_jost_determinant_tangent"]
    tau = sp.Symbol("tau")
    xh0, xh1, xp0, xp1 = sp.symbols("X_H0 X_H1 X_p0 X_p1")
    yh0, yh1, yp0, yp1 = sp.symbols("Y_H0 Y_H1 Y_p0 Y_p1")
    x_h = sp.Matrix([xh0, xh1])
    x_p = sp.Matrix([xp0, xp1])
    y_h = sp.Matrix([yh0, yh1])
    y_p = sp.Matrix([yp0, yp1])
    determinant_family = sp.expand(
        sp.Matrix.hstack(x_h + tau * y_h, x_p + tau * y_p).det()
    )
    determinant_tangent = determinant_family.coeff(tau, 1)
    expected_tangent = (
        sp.Matrix.hstack(x_h, y_p).det()
        + sp.Matrix.hstack(y_h, x_p).det()
    )
    if sp.expand(determinant_tangent - expected_tangent) != 0:
        errors.append("independent Jost determinant tangent failed")
    if sp.expand(
        parse(tangent["determinant_family"]) - determinant_family
    ) != 0:
        errors.append("recorded Jost determinant family drift")
    if sp.expand(parse(tangent["tangent"]) - determinant_tangent) != 0:
        errors.append("recorded Jost determinant tangent drift")
    if not tangent.get("identity_verified"):
        errors.append("Jost determinant tangent exact flag lost")
    if tangent.get("hypotheses_certified_here"):
        errors.append("analytic Jost-column hypotheses falsely certified")
    if tangent.get("physical_jost_tangent_established"):
        errors.append("physical Jost tangent falsely established")

    cluster = document["conditional_finite_cluster_algebra"]
    model = cluster["n3_exact_model"]
    omega = sp.Symbol("omega")
    roots = sp.symbols("omega_1 omega_2 omega_3")
    kappas = sp.symbols("kappa_1 kappa_2 kappa_3")
    p_model = sp.expand(sp.prod(omega - root for root in roots))
    q_model = sp.expand(sum(
        kappa * sp.prod(
            omega - other for other in roots if other != root
        )
        for root, kappa in zip(roots, kappas)
    ))
    if sp.expand(parse(model["P"]) - p_model) != 0:
        errors.append("N=3 cluster P drift")
    if sp.expand(parse(model["Q"]) - q_model) != 0:
        errors.append("N=3 cluster Q drift")

    vandermonde = sp.Matrix([
        [1, 1, 1],
        list(roots),
        [root**2 for root in roots],
    ])
    if matrix(model["vandermonde"]) != vandermonde:
        errors.append("N=3 Vandermonde matrix drift")
    determinant = sp.factor(vandermonde.det())
    expected_determinant = sp.factor(
        (roots[1] - roots[0])
        * (roots[2] - roots[0])
        * (roots[2] - roots[1])
    )
    if sp.simplify(determinant - expected_determinant) != 0:
        errors.append("independent N=3 Vandermonde determinant failed")
    if sp.simplify(
        parse(model["vandermonde_determinant"]) - determinant
    ) != 0:
        errors.append("recorded N=3 Vandermonde determinant drift")

    q_values = [
        sp.factor(q_model.subs(omega, root)) for root in roots
    ]
    expected_q_values = [
        sp.factor(
            kappa * sp.diff(p_model, omega).subs(omega, root)
        )
        for root, kappa in zip(roots, kappas)
    ]
    if any(
        sp.simplify(value - expected) != 0
        for value, expected in zip(q_values, expected_q_values)
    ):
        errors.append("independent N=3 Q interpolation failed")
    recorded_q_values = [parse(value) for value in model["Q_at_roots"]]
    if any(
        sp.simplify(value - expected) != 0
        for value, expected in zip(recorded_q_values, q_values)
    ):
        errors.append("recorded N=3 Q interpolation drift")

    resultant = sp.factor(sp.resultant(p_model, q_model, omega))
    resultant_product = sp.factor(sp.prod(q_values))
    if sp.simplify(resultant - resultant_product) != 0:
        errors.append("independent N=3 resultant product failed")
    if sp.simplify(parse(model["resultant"]) - resultant) != 0:
        errors.append("recorded N=3 resultant drift")
    if sp.simplify(
        parse(model["resultant_product"]) - resultant_product
    ) != 0:
        errors.append("recorded N=3 resultant product drift")

    exact_root_subs = dict(zip(roots, [sp.Integer(1), 2, 4]))
    p_exact = sp.Poly(p_model.subs(exact_root_subs), omega)
    patterns = {
        "three_defective": [1, 1, 1],
        "two_defective": [1, 1, 0],
        "one_defective": [1, 0, 0],
        "zero_defective": [0, 0, 0],
    }
    expected_gcd_degrees = {}
    for label, values in patterns.items():
        substitutions = {
            **exact_root_subs,
            **dict(zip(kappas, values)),
        }
        q_branch = sp.Poly(q_model.subs(substitutions), omega)
        expected_gcd_degrees[label] = int(
            sp.degree(sp.gcd(p_exact, q_branch))
        )
    if expected_gcd_degrees != {
        "three_defective": 0,
        "two_defective": 1,
        "one_defective": 2,
        "zero_defective": 3,
    }:
        errors.append("independent N=3 gcd defect count failed")
    if model["gcd_degrees"] != expected_gcd_degrees:
        errors.append("recorded N=3 gcd defect count drift")

    power_sums = {
        degree: sp.expand(sum(root**degree for root in roots))
        for degree in range(4)
    }
    e1 = power_sums[1]
    e2 = sp.expand((power_sums[1]**2 - power_sums[2]) / 2)
    e3 = sp.expand(
        (
            power_sums[1]**3
            - 3 * power_sums[1] * power_sums[2]
            + 2 * power_sums[3]
        ) / 6
    )
    newton_p = sp.expand(omega**3 - e1 * omega**2 + e2 * omega - e3)
    if sp.expand(newton_p - p_model) != 0:
        errors.append("independent N=3 Newton reconstruction failed")
    if sp.expand(parse(model["newton_P"]) - newton_p) != 0:
        errors.append("recorded N=3 Newton reconstruction drift")

    moments = {
        degree: sp.expand(sum(
            kappa * root**degree
            for root, kappa in zip(roots, kappas)
        ))
        for degree in range(3)
    }
    p_coefficients = sp.Poly(p_model, omega).all_coeffs()
    q_from_moments = sp.expand(
        moments[0] * omega**2
        + (moments[1] + p_coefficients[1] * moments[0]) * omega
        + moments[2]
        + p_coefficients[1] * moments[1]
        + p_coefficients[2] * moments[0]
    )
    if sp.expand(q_from_moments - q_model) != 0:
        errors.append("independent N=3 root-free Q reconstruction failed")
    if sp.expand(parse(model["Q_from_moments"]) - q_from_moments) != 0:
        errors.append("recorded N=3 root-free Q reconstruction drift")

    centroid = sp.expand(power_sums[1] / 3)
    centered = {
        degree: sp.expand(sum(
            kappa * (root - centroid)**degree
            for root, kappa in zip(roots, kappas)
        ))
        for degree in range(3)
    }
    centered_from_raw = {
        degree: sp.expand(sum(
            sp.binomial(degree, index)
            * (-centroid)**(degree - index)
            * moments[index]
            for index in range(degree + 1)
        ))
        for degree in range(3)
    }
    if any(
        sp.expand(centered[degree] - centered_from_raw[degree]) != 0
        for degree in range(3)
    ):
        errors.append("independent N=3 centered moment transform failed")
    recorded_centered = {
        int(degree): parse(value)
        for degree, value in model["centered_moments"].items()
    }
    if any(
        sp.expand(recorded_centered[degree] - centered[degree]) != 0
        for degree in range(3)
    ):
        errors.append("recorded N=3 centered moment drift")

    zeta = sp.Symbol("zeta")
    resolvent = sp.factor(sum(
        kappa / (zeta - root)
        for root, kappa in zip(roots, kappas)
    ))
    rational_resolvent = sp.factor(
        q_model.subs(omega, zeta) / p_model.subs(omega, zeta)
    )
    if sp.cancel(resolvent - rational_resolvent) != 0:
        errors.append("independent N=3 extension resolvent failed")
    if sp.cancel(parse(model["extension_resolvent"]) - resolvent) != 0:
        errors.append("recorded N=3 extension resolvent drift")
    if sp.cancel(
        parse(model["rational_resolvent"]) - rational_resolvent
    ) != 0:
        errors.append("recorded N=3 rational resolvent drift")

    extended_moments = {
        degree: sp.expand(sum(
            kappa * root**degree
            for root, kappa in zip(roots, kappas)
        ))
        for degree in range(7)
    }
    inverse_zeta = sp.Symbol("inverse_zeta")
    laurent = sp.expand(
        sp.series(
            resolvent.subs(zeta, 1 / inverse_zeta),
            inverse_zeta,
            0,
            7,
        ).removeO()
    )
    expected_laurent = sp.expand(sum(
        extended_moments[degree] * inverse_zeta**(degree + 1)
        for degree in range(6)
    ))
    if sp.expand(laurent - expected_laurent) != 0:
        errors.append("independent N=3 Laurent moments failed")
    if sp.expand(parse(model["laurent_through_K5"]) - laurent) != 0:
        errors.append("recorded N=3 Laurent moments drift")

    vandermonde = sp.Matrix([
        [1, 1, 1],
        list(roots),
        [root**2 for root in roots],
    ])
    kappa_diagonal = sp.diag(*kappas)
    omega_diagonal = sp.diag(*roots)
    hankel = sp.Matrix(
        3, 3, lambda row, column: extended_moments[row + column]
    )
    hankel_factor = vandermonde * kappa_diagonal * vandermonde.T
    if sp.simplify(hankel - hankel_factor) != sp.zeros(3):
        errors.append("independent N=3 Hankel factorization failed")
    if matrix(model["Hankel"]) != hankel:
        errors.append("recorded N=3 Hankel drift")
    if sp.simplify(
        matrix(model["Hankel_factor"]) - hankel_factor
    ) != sp.zeros(3):
        errors.append("recorded N=3 Hankel factor drift")
    hankel_det = sp.factor(hankel.det())
    discriminant = sp.factor(sp.discriminant(p_model, omega))
    if sp.simplify(hankel_det - discriminant * sp.prod(kappas)) != 0:
        errors.append("independent N=3 Hankel discriminant identity failed")
    if sp.simplify(hankel_det + resultant) != 0:
        errors.append("independent N=3 Hankel resultant sign failed")
    if sp.simplify(parse(model["Hankel_determinant"]) - hankel_det) != 0:
        errors.append("recorded N=3 Hankel determinant drift")
    if sp.simplify(parse(model["discriminant"]) - discriminant) != 0:
        errors.append("recorded N=3 discriminant drift")

    gram = vandermonde * vandermonde.T
    shifted_gram = vandermonde * omega_diagonal * vandermonde.T
    shifted_hankel = (
        vandermonde * kappa_diagonal * omega_diagonal * vandermonde.T
    )
    if matrix(model["G"]) != gram:
        errors.append("recorded N=3 G drift")
    if matrix(model["G1"]) != shifted_gram:
        errors.append("recorded N=3 G1 drift")
    if matrix(model["H1"]) != shifted_hankel:
        errors.append("recorded N=3 H1 drift")
    exact_roots = [sp.Integer(1), sp.Integer(2), sp.Integer(4)]
    if model["joint_operator_root_specialization"] != ["1", "2", "4"]:
        errors.append("joint-operator specialization drift")
    v_exact = vandermonde.subs(dict(zip(roots, exact_roots)))
    omega_exact = sp.diag(*exact_roots)
    gram_exact = v_exact * v_exact.T
    g1_exact = v_exact * omega_exact * v_exact.T
    h_exact = v_exact * kappa_diagonal * v_exact.T
    h1_exact = v_exact * kappa_diagonal * omega_exact * v_exact.T
    m_omega = gram_exact.inv() * g1_exact
    m_kappa = gram_exact.inv() * h_exact
    if matrix(model["M_omega"]) != m_omega:
        errors.append("recorded N=3 M_omega drift")
    if matrix(model["M_kappa"]) != m_kappa:
        errors.append("recorded N=3 M_kappa drift")
    if sp.simplify(m_omega * m_kappa - m_kappa * m_omega) != sp.zeros(3):
        errors.append("independent N=3 multiplication commutator failed")
    if matrix(model["multiplication_commutator"]) != sp.zeros(3):
        errors.append("recorded multiplication commutator is nonzero")
    if sp.simplify(h1_exact - g1_exact * gram_exact.inv() * h_exact) != (
        sp.zeros(3)
    ):
        errors.append("independent N=3 shifted Hankel join failed")
    eigenvectors = v_exact.T.inv()
    if matrix(model["joint_eigenvectors"]) != eigenvectors:
        errors.append("recorded N=3 joint eigenvectors drift")
    if sp.simplify(
        m_omega * eigenvectors - eigenvectors * omega_exact
    ) != sp.zeros(3):
        errors.append("independent N=3 omega eigenpairs failed")
    if sp.simplify(
        m_kappa * eigenvectors - eigenvectors * kappa_diagonal
    ) != sp.zeros(3):
        errors.append("independent N=3 kappa eigenpairs failed")

    recurrence_models = model["recurrence_models"]
    recorded_ranks = model["Hankel_ranks"]
    for label, values in patterns.items():
        substitutions = {
            **dict(zip(roots, exact_roots)),
            **dict(zip(kappas, values)),
        }
        active = [
            root for root, value in zip(exact_roots, values) if value != 0
        ]
        reduced = sp.expand(sp.prod(zeta - root for root in active))
        if not active:
            reduced = sp.Integer(1)
        degree = len(active)
        branch_moments = {
            index: sp.expand(extended_moments[index].subs(substitutions))
            for index in range(7)
        }
        coefficients = sp.Poly(reduced, zeta).all_coeffs()
        for start in range(7 - degree):
            value = sp.expand(sum(
                coefficients[index]
                * branch_moments[start + degree - index]
                for index in range(degree + 1)
            ))
            if value != 0:
                errors.append(f"independent recurrence failed: {label}")
                break
        rank = int(hankel.subs(substitutions).rank())
        if rank != degree:
            errors.append(f"independent Hankel rank failed: {label}")
        record = recurrence_models[label]
        if (sp.expand(
                parse(record["reduced_denominator"]) - reduced
            ) != 0
                or record["degree"] != degree
                or [parse(value) for value in record["coefficients"]]
                != coefficients):
            errors.append(f"recorded recurrence drift: {label}")
        if recorded_ranks[label] != rank:
            errors.append(f"recorded Hankel rank drift: {label}")

    left_nodes = [parse(value) for value in model["Loewner_left_nodes"]]
    right_nodes = [parse(value) for value in model["Loewner_right_nodes"]]
    c_mu = sp.Matrix([
        [1 / (node - root) for root in exact_roots]
        for node in left_nodes
    ])
    c_lambda = sp.Matrix([
        [1 / (node - root) for root in exact_roots]
        for node in right_nodes
    ])
    loewner = c_mu * kappa_diagonal * c_lambda.T
    shifted_loewner = (
        c_mu
        * sp.diag(*[
            kappa * root for root, kappa in zip(exact_roots, kappas)
        ])
        * c_lambda.T
    )
    if sp.simplify(matrix(model["Loewner"]) - loewner) != sp.zeros(3):
        errors.append("recorded N=3 Loewner drift")
    if sp.simplify(
        matrix(model["shifted_Loewner"]) - shifted_loewner
    ) != sp.zeros(3):
        errors.append("recorded N=3 shifted Loewner drift")
    pencil_ratio = sp.factor(
        (shifted_loewner - zeta * loewner).det() / loewner.det()
    )
    expected_ratio = sp.factor(sp.prod(root - zeta for root in exact_roots))
    if sp.cancel(pencil_ratio - expected_ratio) != 0:
        errors.append("independent N=3 Loewner spectrum failed")
    if sp.cancel(
        parse(model["pencil_determinant_ratio"]) - pencil_ratio
    ) != 0:
        errors.append("recorded N=3 Loewner spectrum drift")

    loewner_theorem = cluster["conditional_loewner_theorem"]
    if loewner_theorem.get("sampling_nodes_supplied"):
        errors.append("physical Loewner nodes falsely supplied")
    if loewner_theorem.get("rank_or_eigenvalues_computed"):
        errors.append("physical Loewner spectrum falsely computed")
    reality = cluster["conditional_reality_symmetry"]
    if reality.get("hypotheses_certified_here"):
        errors.append("physical reality symmetry falsely certified")
    if reality.get("physical_reality_consequences_established"):
        errors.append("physical reality consequences falsely established")

    if not model.get("identities_verified"):
        errors.append("N=3 cluster exact flag lost")
    for field in (
        "analytic_cluster_supplied",
        "actual_N_computed",
        "actual_P_D_computed",
        "actual_Q_D_computed",
        "actual_defective_count_computed",
        "actual_resolvent_computed",
        "actual_hankel_rank_computed",
        "actual_loewner_spectrum_computed",
    ):
        if cluster.get(field):
            errors.append(f"physical cluster field promoted: {field}")

    flags = document["claim_flags"]
    for name in (
        "operator_dual_number_jet_exact",
        "dual_number_regular_representation_exact",
        "simple_zero_shift_identity_exact",
        "compatible_normalization_ratio_identity_exact",
        "conditional_contour_moment_residue_identity_exact",
        "zero_free_endpoint_renormalization_invariance_exact",
        "conditional_jost_determinant_tangent_identity_exact",
        "partial_jet_functor_exact",
        "partial_jet_extension_ratio_identities_exact",
        "conditional_finite_cluster_algebra_exact",
        "n3_cluster_model_independently_exact",
        "conditional_extension_resolvent_hankel_recurrence_exact",
        "conditional_generic_loewner_theorem_exact",
    ):
        if flags.get(name) is not True:
            errors.append(f"exact flag lost: {name}")
    for name in (
        "analytic_endpoint_scalar_frames_constructed",
        "analytic_contour_domain_supplied",
        "contour_moment_evaluated",
        "physical_cluster_data_computed",
        "physical_extension_resolvent_or_hankel_computed",
        "physical_loewner_rank_or_spectrum_computed",
        "physical_reality_symmetry_certified",
        "compatible_endpoint_partial_jet_frames_constructed",
        "T_plus_recovered_by_partial_jet",
        "scattering_identity_recovered_by_partial_jet",
        "global_b_derivative_established",
        "physical_QNM_supplied",
        "beta_n_evaluated",
        "physical_QNM_smith_case_selected",
        "EP2_established",
        "physical_QNM_fredholm_realization_constructed",
        "flux_theorem_established",
    ):
        if flags.get(name) is not False:
            errors.append(f"open flag promoted: {name}")

    boundaries = " ".join(document.get("does_not_establish", []))
    for needle in (
        "beta_n",
        "exceptional point",
        "Fredholm",
        "flux theorem",
        "contour moment",
        "Jost columns",
        "cluster size",
        "extension resolvent",
        "reality symmetry",
        "outgoing map T_plus",
    ):
        if needle not in boundaries:
            errors.append(f"missing claim boundary: {needle}")
    return errors


def main() -> None:
    document = json.loads(CERTIFICATE.read_text())
    errors = verify_document(document)
    if errors:
        for error in errors:
            print("FAIL:", error)
        raise SystemExit(1)
    print("PASS: intrinsic-deformation jet certificate verified")


if __name__ == "__main__":
    main()
