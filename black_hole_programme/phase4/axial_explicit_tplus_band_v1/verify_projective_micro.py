#!/usr/bin/env python3
"""Independent structural and point audit of the projective microfactor."""

from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

from black_hole_programme.phase4.axial_explicit_tplus_band_v1 import (
    produce_projective_micro as producer,
)
from black_hole_programme.phase4.axial_explicit_tplus_band_v1.interaction_picture import (
    _coefficient_functions,
    _solve,
)

HERE = Path(__file__).resolve().parent
if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode()
    ).hexdigest()


def central_complex_columns(document: dict, name: str) -> np.ndarray:
    model = document["payload"][name]
    real = np.array(
        [
            [float(Fraction(value)) for value in row]
            for row in model["coefficients"][0]
        ],
        dtype=float,
    )
    return real[:4, :] + 1j * real[4:, :]


def point_microfactor() -> dict[str, float]:
    r0 = float(Fraction(3895, 128))
    r1 = float(Fraction(1947, 64))
    w = float(Fraction(8193, 16384))

    def rhs(r: float, state: np.ndarray) -> np.ndarray:
        base, tangent = _coefficient_functions(r, w)
        matrices = [
            state[index : index + 4].reshape((2, 2))
            for index in range(0, 20, 4)
        ]
        P, R, J, K, dotK = matrices
        A, D, Ax = base[:2, :2], base[:2, 2:], base[2:, 2:]
        # The pinned outgoing rail stores the intrinsic coefficient source
        # in the historical 1/512 normalized tangent convention and restores
        # the physical column tangent at emission.
        E, C = 512.0 * tangent[:2, :2], 512.0 * tangent[:2, 2:]
        Pinv = np.linalg.inv(P)
        drive = Pinv @ D @ R
        return np.concatenate(
            [
                (A @ P).reshape(-1),
                (Ax @ R).reshape(-1),
                (Pinv @ E @ P).reshape(-1),
                drive.reshape(-1),
                (Pinv @ C @ R - J @ drive).reshape(-1),
                np.array([np.trace(A), np.trace(Ax)], dtype=complex),
            ]
        )

    zero = np.zeros((2, 2), dtype=complex)
    identity = np.eye(2, dtype=complex)
    initial = np.concatenate(
        [
            identity.reshape(-1),
            identity.reshape(-1),
            zero.reshape(-1),
            zero.reshape(-1),
            zero.reshape(-1),
            np.zeros(2, dtype=complex),
        ]
    )
    final = _solve(rhs, (r0, r1), initial)
    P, R, J, K, dotK = [
        final[index : index + 4].reshape((2, 2))
        for index in range(0, 20, 4)
    ]
    logw2, logw1 = final[20:22]
    return {
        "pinv_margin": float(abs(np.linalg.det(P)) ** 2),
        "p00": float(abs(P[0, 0]) ** 2),
        "p11": float(abs(P[1, 1]) ** 2),
        "r00": float(abs(R[0, 0]) ** 2),
        "r11": float(abs(R[1, 1]) ** 2),
        "wronskian2_residual": float(abs(np.linalg.det(P) - np.exp(logw2))),
        "wronskian1_residual": float(abs(np.linalg.det(R) - np.exp(logw1))),
        "interaction_norm": float(
            max(np.max(np.abs(J)), np.max(np.abs(K)), np.max(np.abs(dotK)))
        ),
    }


def successor_point_residual() -> float:
    predecessor = json.loads(producer.INPUT.read_text())
    successor = json.loads(producer.CHECKPOINT.read_text())
    base0 = central_complex_columns(predecessor, "base")
    tangent0 = central_complex_columns(predecessor, "tangent")
    expected_base = central_complex_columns(successor, "base")
    expected_tangent = central_complex_columns(successor, "tangent")
    r0 = float(Fraction(3895, 128))
    r1 = float(Fraction(1947, 64))
    w = float(Fraction(8193, 16384))

    def rhs(r: float, state: np.ndarray) -> np.ndarray:
        base_generator, tangent_generator = _coefficient_functions(r, w)
        base = state[:8].reshape((4, 2))
        tangent = state[8:].reshape((4, 2))
        return np.concatenate(
            (
                (base_generator @ base).reshape(-1),
                (
                    base_generator @ tangent
                    + 512.0 * tangent_generator @ base
                ).reshape(-1),
            )
        )

    initial = np.concatenate((base0.reshape(-1), tangent0.reshape(-1)))
    final = _solve(rhs, (r0, r1), initial)
    actual_base = final[:8].reshape((4, 2))
    actual_tangent = final[8:].reshape((4, 2))
    return float(
        max(
            np.max(np.abs(actual_base - expected_base)),
            np.max(np.abs(actual_tangent - expected_tangent)),
        )
    )


def main() -> int:
    certificate = json.loads(producer.CERTIFICATE.read_text())
    manifest = json.loads(producer.MANIFEST.read_text())
    checkpoint = json.loads(producer.CHECKPOINT.read_text())
    receipt = json.loads(producer.RECEIPT.read_text())

    if certificate["status"] != "PROJECTIVE_INTERACTION_MICRO_PASS_R4_OPEN":
        raise AssertionError("certificate is not passing")
    if canonical_sha256(checkpoint["payload"]) != checkpoint["payload_sha256"]:
        raise AssertionError("checkpoint payload hash drift")
    if certificate["successor"]["checkpoint_sha256"] != sha256(producer.CHECKPOINT):
        raise AssertionError("checkpoint file hash drift")
    if certificate["successor"]["manifest_sha256"] != sha256(producer.MANIFEST):
        raise AssertionError("manifest file hash drift")
    if receipt["certificate_sha256"] != sha256(producer.CERTIFICATE):
        raise AssertionError("receipt/certificate hash drift")
    if manifest["checkpoint_payload_sha256"] != checkpoint["payload_sha256"]:
        raise AssertionError("manifest/checkpoint hash drift")
    if checkpoint["payload"]["start_radius"] != "3895/128":
        raise AssertionError("radial start drift")
    if checkpoint["payload"]["radius"] != "1947/64":
        raise AssertionError("radial end drift")

    gates = certificate["validated_gates"]
    for key in (
        "interaction_reconstruction",
        "projective_multiplicative_reconstruction",
        "spin_two_wronskian",
        "spin_one_wronskian",
    ):
        if not gates[key]:
            raise AssertionError(f"failed certified gate: {key}")
    for value in gates["inverse_and_chart_margins"].values():
        if float(value) <= 0.0:
            raise AssertionError("nonpositive chart margin")
    summary = gates["direct_boundary_summary"]
    if not (summary["coefficients"] and summary["containment"]):
        raise AssertionError("direct boundary audit failed")
    diagnostic = certificate["accumulated_frame_chart_diagnostic"]
    if not diagnostic["spin_two_R_column"][
        "rectangular_enclosure_excludes_zero"
    ]:
        raise AssertionError("expected resolved accumulated R pivot")
    if diagnostic["spin_one_S_column"][
        "rectangular_enclosure_excludes_zero"
    ]:
        raise AssertionError("expected unresolved accumulated S pivot")

    point = point_microfactor()
    certified = gates["inverse_and_chart_margins"]
    for key in ("pinv_margin", "p00", "p11", "r00", "r11"):
        if point[key] < float(certified[key]):
            raise AssertionError(f"point value fell below interval margin: {key}")
    if point["wronskian2_residual"] > 2.0e-12:
        raise AssertionError("spin-two Wronskian point audit failed")
    if point["wronskian1_residual"] > 2.0e-12:
        raise AssertionError("spin-one Wronskian point audit failed")
    if successor_point_residual() > 2.0e-6:
        raise AssertionError("successor center point audit failed")

    print("PROJECTIVE_MICRO_INDEPENDENT_AUDIT_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
