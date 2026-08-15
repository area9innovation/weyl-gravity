#!/usr/bin/env python3
"""Certify Watson/Bessel bounds deciding the BT annealed one-loop limit."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from fractions import Fraction


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_ANNEALED_RESPONSE_WATSON_BOUND_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-annealed-response-watson-bound-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/bt-euclidean-annealed-response-watson-bound.md"
)
VERIFY_REL = (
    "reverse_physics/verify_bt_euclidean_annealed_response_watson_bound.py"
)
INPUTS = [
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_ANNEALED_RESPONSE_ONE_LOOP_V1.json"
]
SOURCE_COMMIT = "be886d401f450636443a37cfb8d6ddaa2048d79b"
W_TRUNCATION = 2500
POTENTIAL_TRUNCATION = 10


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def fraction_hash(value: Fraction) -> str:
    if hasattr(sys, "set_int_max_str_digits"):
        sys.set_int_max_str_digits(0)
    canonical = f"{value.numerator}/{value.denominator}".encode("ascii")
    return hashlib.sha256(canonical).hexdigest()


def origin_counts(limit: int) -> tuple[list[int], int]:
    """Closed 2n-step walk counts from the hypercubic LGF recurrence."""

    if limit < 1:
        return [1], 0
    counts = [1, 8]
    exact_divisions = 0
    for n in range(2, limit + 1):
        numerator = (
            4 * (2 * n - 1) ** 2 * (5 * n * n - 5 * n + 2) * counts[-1]
            - 256
            * (n - 1) ** 2
            * (2 * n - 3)
            * (2 * n - 1)
            * counts[-2]
        )
        denominator = n**4
        quotient, remainder = divmod(numerator, denominator)
        if remainder:
            raise ArithmeticError(f"nonintegral return recurrence at n={n}")
        counts.append(quotient)
        exact_divisions += 1
    return counts, exact_divisions


def scaled_partial(counts: list[int]) -> Fraction:
    numerator = 0
    for count in counts:
        numerator = 64 * numerator + count
    n = len(counts) - 1
    return Fraction(numerator, 8 * 64**n)


def diagonal_endpoint_count(n: int) -> int:
    """Number of 2n-step walks ending at (1,1,0,0)."""

    if n == 0:
        return 0
    total = Fraction()
    factorial = math.factorial
    for k in range(n):
        remaining = n - 1 - k
        odd_pair = Fraction(
            math.comb(2 * k + 2, k + 1), factorial(k) * factorial(k + 2)
        )
        even_pair = Fraction(
            math.comb(2 * remaining, remaining), factorial(remaining) ** 2
        )
        total += odd_pair * even_pair
    count = total * factorial(2 * n)
    if count.denominator != 1:
        raise ArithmeticError(f"nonintegral endpoint count at n={n}")
    return count.numerator


def potential_partial(origin: list[int], limit: int) -> tuple[Fraction, list[int]]:
    endpoints = [diagonal_endpoint_count(n) for n in range(limit + 1)]
    result = sum(
        (
            Fraction(origin[n] - endpoints[n], 8 * 64**n)
            for n in range(limit + 1)
        ),
        Fraction(),
    )
    return result, endpoints


def build() -> dict:
    counts, exact_divisions = origin_counts(W_TRUNCATION)
    w_partial = scaled_partial(counts)
    w_tail = Fraction(121, 784 * W_TRUNCATION)
    w_upper = w_partial + w_tail
    w_envelope = Fraction(15499, 100000)
    w_target = Fraction(31, 200)

    potential, endpoints = potential_partial(counts, POTENTIAL_TRUNCATION)
    potential_target = Fraction(71, 500)
    i_upper_exact = 1 - 4 * potential
    i_target = Fraction(54, 125)
    beta_upper = (
        Fraction(-85, 5184)
        + w_target / 18
        + Fraction(5, 288) * i_target
    )

    checks = {
        "return_initial_values": counts[:6]
        == [1, 8, 168, 5120, 190120, 7939008],
        "return_recurrence_exact_divisions": exact_divisions == W_TRUNCATION - 1,
        "return_counts_positive": all(value > 0 for value in counts),
        "w_partial_hash": fraction_hash(w_partial)
        == "0481e8a91c76f8aa8147f9830d639c4947d4b47a214472850f678c9e620c3cf1",
        "w_partial_digit_counts": (
            len(str(w_partial.numerator)), len(str(w_partial.denominator))
        )
        == (4511, 4511),
        "w_upper_below_orientation_envelope": w_upper < w_envelope,
        "w_strict_bound": w_upper < w_target,
        "endpoint_initial_values": endpoints
        == [
            0,
            2,
            72,
            2820,
            120400,
            5483520,
            262031616,
            12987830856,
            662444434080,
            34571972326320,
            1838441670619840,
        ],
        "termwise_potential_nonnegative": all(
            counts[n] >= endpoints[n] for n in range(POTENTIAL_TRUNCATION + 1)
        ),
        "potential_exact_value": potential
        == Fraction(2558322539133673, 18014398509481984),
        "potential_exceeds_target": potential > potential_target,
        "i_strict_bound": i_upper_exact < i_target,
        "beta_limit_upper_is_minus_37_over_129600": beta_upper
        == Fraction(-37, 129600),
        "beta_limit_strictly_negative": beta_upper < 0,
        "nonperturbative_h_minus_one_remains_open": True,
        "no_born_krein_or_lorentzian_promotion": True,
    }

    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_ANNEALED_RESPONSE_WATSON_BOUND_V1",
        "schema_version": "reverse-physics-bt-euclidean-annealed-response-watson-bound-v1",
        "created": "2026-08-16",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL", "REDUCED-MODE"],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "exact rational Watson and potential-kernel bounds deciding the large-volume BT annealed signed-response one-loop coefficient",
        "question": "Is the exact large-volume one-loop coefficient b_(2,infinity)=-85/5184+W4/18+5*I4/288 strictly negative?",
        "answer": (
            "Yes. The four-dimensional Watson moment is one eighth of the "
            "simple-walk return Green series. Its first 2501 exact terms, plus "
            "the tail p_(2n)(0)<=(121/98)/n^2, prove W4<31/200. The derivative "
            "moment obeys I4=1-4*(G(0)-G(e1+e2)). Cauchy-Schwarz makes every "
            "potential-kernel series term nonnegative, and the first eleven exact "
            "terms already prove G(0)-G(e1+e2)>71/500, hence I4<54/125. "
            "Substitution gives b_(2,infinity)<-37/129600<0. This closes "
            "nonnegative single-site annealed signed response as a volume-uniform "
            "one-loop architecture, but does not determine the resummed interacting "
            "response, heat-bath gap, or H^-1 moment."
        ),
        "watson_return_series": {
            "definition": "W4=integral_0^infinity [exp(-2t)*I0(2t)]^4 dt",
            "walk_representation": "W4=(1/8)*sum_(n>=0) A_n/64^n, where A_n counts closed 2n-step nearest-neighbor walks on Z^4",
            "coefficient_formula": "A_n=binom(2n,n)*sum_(k=0)^n binom(n,k)^2*binom(2k,k)*binom(2n-2k,n-k)",
            "recurrence": "n^4*A_n=4*(2n-1)^2*(5n^2-5n+2)*A_(n-1)-256*(n-1)^2*(2n-3)*(2n-1)*A_(n-2)",
            "initial_values": counts[:6],
            "truncation_n": W_TRUNCATION,
            "partial_fraction_sha256": fraction_hash(w_partial),
            "partial_numerator_decimal_digits": len(str(w_partial.numerator)),
            "partial_denominator_decimal_digits": len(str(w_partial.denominator)),
            "tail_proof": [
                "p_(2n)(0)=(2*pi)^-4*integral phi(k)^(2n) dk with phi=(1/4)*sum cos(k_mu)",
                "map the negative-phi region by k -> k+(pi,pi,pi,pi)",
                "on phi>=0 use 1-cos(theta)>=2*theta^2/pi^2 and u^(2n)<=exp(-2n*(1-u))",
                "the R^4 Gaussian integral gives p_(2n)(0)<=pi^2/(8*n^2)<=(121/98)/n^2 using pi<22/7",
                "sum_(n>N) n^-2 <= 1/N",
            ],
            "tail_upper": enc(w_tail),
            "computed_upper_below": enc(w_envelope),
            "certified_bound": "W4<31/200",
            "certified_upper": enc(w_target),
        },
        "derivative_moment_potential_kernel": {
            "definition": "I4=integral_0^infinity f(t)^2*f'(t)^2 dt for f(t)=exp(-2t)*I0(2t)",
            "diagonal_site": "r=e1+e2=(1,1,0,0)",
            "identity_steps": [
                "f'(t)=2*exp(-2t)*(I1(2t)-I0(2t))",
                "I4=4*(G(0)-2*G(e1)+G(e1+e2))",
                "the lattice Green equation gives G(0)-G(e1)=1/8",
                "therefore I4=1-4*(G(0)-G(e1+e2))",
            ],
            "series": "G(0)-G(r)=(1/8)*sum_(n>=0) [A_n-B_n]/64^n, where B_n counts 2n-step walks ending at r",
            "endpoint_formula": "B_n=(2n)!*sum_(k=0)^(n-1) binom(2k+2,k+1)/(k!*(k+2)!)*binom(2n-2-2k,n-1-k)/((n-1-k)!)^2",
            "nonnegative_tail_proof": "p_(2n)(r)=<p_n,tau_r p_n><=||p_n||_2^2=p_(2n)(0) by Cauchy-Schwarz",
            "truncation_n": POTENTIAL_TRUNCATION,
            "origin_counts": counts[: POTENTIAL_TRUNCATION + 1],
            "endpoint_counts": endpoints,
            "partial_potential": enc(potential),
            "partial_exceeds": enc(potential_target),
            "exact_i_upper_from_partial": enc(i_upper_exact),
            "certified_bound": "I4<54/125",
            "certified_upper": enc(i_target),
        },
        "large_volume_decision": {
            "imported_formula": "b_(2,infinity)=-85/5184+W4/18+5*I4/288",
            "substituted_strict_upper": "b_(2,infinity)<-85/5184+(31/200)/18+(5/288)*(54/125)=-37/129600",
            "upper": enc(beta_upper),
            "sign": "STRICTLY_NEGATIVE",
            "status": "LARGE_VOLUME_ONE_LOOP_SIGN_CERTIFIED",
        },
        "method_consequence": {
            "single_site_annealed_beta_nonnegative": "OBSTRUCTED_AT_LARGE_VOLUME_ONE_LOOP",
            "formal_low_momentum_effect": "the order-lambda^2 coefficient of omega is strictly negative, so the one-loop-truncated relaxation symbol is negative at sufficiently small nonzero momentum for fixed nonzero formal lambda",
            "scope": "a coefficientwise volume-uniform single-site signed-response proof cannot preserve nonnegative low-momentum relaxation",
            "does_not_extend_to": "the resummed nonperturbative beta, continuous-time heat-bath spectral gap, block conditional response, or a direct Witten/score estimate",
        },
        "method_disposition": {
            "finite_volume_os_reflection_positivity": "OBSTRUCTED_BY_IMPORTED_PROGRAM_RESULT",
            "pointwise_single_site_signed_response": "OBSTRUCTED_BY_IMPORTED_PROGRAM_RESULT",
            "annealed_single_site_signed_response_one_loop": "OBSTRUCTED_AT_LARGE_VOLUME",
            "nonperturbative_annealed_response": "OPEN",
            "block_or_multiscale_signed_response": "OPEN",
            "volume_uniform_global_poincare_or_witten": "OPEN",
            "interacting_h_minus_one_bound": "OPEN",
            "continuum_measure": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "a nonperturbative estimate or obstruction for the actual annealed response after resumming all coupling orders",
            "a block conditional-response theorem capable of replacing the obstructed single-site coefficientwise route",
            "the normalized lowest-mode and dyadic-shell interacting H^-1 upper bound or an actual Gibbs divergence sequence",
        ],
        "next_gate": "Retire coefficientwise single-site annealed contraction as the primary continuum architecture. Test a two-site or hypercube block conditional response, where the internal wrong-sign omega term may be absorbed before the block boundary symbol is formed; in parallel retain the direct zero-fiber score/Witten route. Any negative continuum conclusion still requires an actual normalized Gibbs H^-1 divergence sequence, not this perturbative method obstruction.",
        "does_not_establish": [
            "a negative nonperturbative beta_L at lambda=0.4 or any fixed coupling",
            "instability or a negative spectral gap for continuous-time heat-bath dynamics",
            "failure of block conditioning, direct score estimates, or every Witten method",
            "failure of the normalized lowest-mode or interacting Gibbs H^-1 bound",
            "absence of an interacting continuum measure beyond the already scoped ordinary-OS obstruction",
            "a new physical dimension, Born rule, Krein reconstruction, or anything LORENTZIAN-CAUSAL",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "arithmetic": "exact Python integers and Fractions for 2501 return coefficients, eleven potential-kernel coefficients, all comparisons, and the final sign; no floating-point arithmetic enters the claim",
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_annealed_response_watson_bound.py --check",
            "ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_annealed_response_watson_bound.py",
            "ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_annealed_response_watson_bound",
        ],
        "tier_receipt": {
            "tier_0": "Python compilation, strict JSON/schema parsing, exact input hashes, scoped diff check, and staged-diff inspection required",
            "tier_1": "producer recurrence, independent multinomial reconstruction, potential-kernel verifier, and mutation tests required",
            "tier_2": "the imported one-loop coefficient certificate is checked by content hash; no shared operator changes",
            "tier_3": "not applicable: this closes a perturbative method coefficient, not the actual H^-1, continuum, freeze, release, shared-core, or Lorentzian lifecycle",
            "memory_policy": "all Python commands run sequentially under a 500000 KiB virtual-memory ceiling; Go uses GOMEMLIMIT=300MiB and GOGC=50",
            "elapsed_seconds_and_peak_kib": {
                "producer_check": "0.04 s, 23320 KiB",
                "independent_verifier": "7.45 s, 32688 KiB",
                "unit_tests": "7.55 s, 33196 KiB",
            },
            "repository_audits": {
                "planning_import": "PASS: 1698 nodes, 0 invalid items, 0 malformed events; 6.57 s, 202032 KiB",
                "science_forge_shadow": "not run: the earlier memory-capped external-indexing abort remains unresolved; this skip is not a pass",
            },
        },
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [key for key, value in checks.items() if not value],
            "details": checks,
        },
        "report": REPORT_REL,
        "schema": SCHEMA_REL,
        "verifier": VERIFY_REL,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    result = build()
    if not result["checks"]["ok"]:
        print("[FAIL] internal checks", result["checks"]["failures"])
        return 1
    if args.check:
        try:
            with open(CERT_PATH, encoding="utf-8") as handle:
                current = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"[FAIL] certificate load: {exc}")
            return 1
        if current != result:
            print("[FAIL] generated certificate differs from committed certificate")
            return 1
    else:
        with open(CERT_PATH, "w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2)
            handle.write("\n")
    print(
        "[PASS] BT annealed response Watson bound "
        f"({result['checks']['passed']}/{result['checks']['total']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
