# BH-3 exterior complex-frequency BVP well-posedness gate

**Work item:** `black-hole-exterior-boundary-wellposedness-gate`
**Certificate:** `black_hole_programme/certificates/BH3_EXTERIOR_BVP_WELLPOSEDNESS_GATE.json`
**Verdict token:** `BH3_EXTERIOR_BVP_EINSTEIN_WELLPOSED_MODULO_DISCRETE_ADDITIONAL_LOGTAIL_OBSTRUCTED`
**Dependency tags:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE` · **Lifecycle:** `CLASSIFIED`

States the Schwarzschild exterior complex-`omega` boundary-value problem
precisely and disposes of its well-posedness branch by branch, exactly and
without solving any single frequency.

## The BVP

- **Domain**: `r in (2m, infinity)`, tortoise `r_* in (-infinity, +infinity)`.
- **Operator**: the parity-unified master ODE `c2 F'' + c1 F' + c0 F = 0`
  (Einstein branch); the fourth-order Bach system (additional branch).
- **Horizon condition**: ingoing/regular, `F ~ e^{-2 i m omega r_*}` (the
  certified indicial roots `±2 i m omega`).
- **Outer condition**: outgoing/radiation, `F ~ e^{+ i omega r_*}` (standard,
  log-free form).

## Einstein branch (log-free) — well-posed modulo a discrete set

The homogeneous formal systems are log-free (`BH2C_ASYMPTOTIC_JORDAN`), so the
Einstein two-ended BVP is standard and Fredholm. A nontrivial solution exists
iff the horizon-ingoing and infinity-outgoing solutions are linearly dependent,
i.e. iff the **connection Wronskian `W_E(omega) = 0`**. `W_E` is analytic in
`omega` on the declared domain (`BH3_ANALYTIC_CONTINUATION_GATE`: both boundary
solutions continue analytically) and is **not identically zero** (the two
boundary solutions are generically independent), so its zero set is **discrete**.

**Disposition:** existence and uniqueness hold on the declared complex-`omega`
domain **minus the discrete zero set of `W_E`**; on that set the homogeneous BVP
acquires a nontrivial kernel (uniqueness fails). That exceptional set is exactly
the transcendental (confluent-Heun) connection object left open by the endpoint
assembly; it is **not computed here** — computing it is the forbidden
quasinormal problem.

## Additional branch (log-tailed) — obstruction

The certified composed (extra-branch) metric carries **logarithmic tails** at
infinity (`BH2C_FLUX_CLASS`: pure-power ansatz inconsistent, single-log ansatz
consistent with nonzero log part). The additional branch shares the Einstein
infinity oscillation rate (`BH2C_METRIC_ALL_ORDERS` oscillatory exponent
`-4 i omega + 1`), so `e^{i omega r_*} r^s` and `e^{i omega r_*} r^s log r` are
**both outgoing**: the standard outgoing radiation condition does **not**
separate the log tail and fixes no unique outgoing amplitude.

**First failed hypothesis:** the outgoing condition is **ill-defined** for the
additional sector; the additional-branch BVP is **not well-posed** with the
standard radiation condition. Resolving it requires a modified
(log-renormalized) outgoing condition — a declared missing object.

## Einstein vs additional

The Einstein-branch BVP is log-free and standard (well-posed modulo the discrete
`W_E` zeros); the additional-branch BVP is log-tailed and obstructed at the
outgoing condition. The two BVPs are structurally distinct — precisely the
distinction the stop condition required.

## What is NOT established (fail-closed)

- the connection Wronskian `W_E`, its zeros, or any discrete spectrum;
- a resolved additional-branch (log-renormalized) outgoing condition;
- the polar-sector BVP beyond the parity-unified fixture level; general `l`;
- no quasinormal, stability, ringdown, scattering, positivity, particle, or
  quantum claim; no well-posedness from any single solved frequency (none is
  solved).

## Verification

- `python3 black_hole_programme/verify_bh3_exterior_bvp_wellposedness_gate.py`
  — schema + six anchor hashes; cross-consistency of the certified log tails /
  log-free contrast, the Einstein oscillatory exponent and the horizon ingoing
  exponents; disposition coherence (Einstein modulo the discrete Wronskian
  zeros; additional-branch ill-defined outgoing condition); claim boundary +
  vocabulary. Solves nothing.
- `pytest black_hole_programme/tests/test_bh3_exterior_bvp_wellposedness_gate.py`
  — structural Tier-1 rail.

## Receipts

- Generator: `black_hole_programme/bh3_exterior_bvp_wellposedness_gate.py` —
  imports six anchors by content hash and ties the disposition to the certified
  log tails, oscillatory exponent, and horizon indicial.

EVIDENCE: `black_hole_programme/certificates/BH3_EXTERIOR_BVP_WELLPOSEDNESS_GATE.json`

CLOSE-OUT: DONE — exterior BVP stated precisely; Einstein branch well-posed
modulo a discrete exceptional set (the connection-Wronskian zeros); the
additional-branch outgoing condition certified as the first well-posedness
obstruction (ill-defined by the certified log tails).
