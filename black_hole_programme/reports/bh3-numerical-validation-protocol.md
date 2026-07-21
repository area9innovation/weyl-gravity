# BH-3 numerical-validation protocol (specification)

**Work item:** `black-hole-bh3-numerical-validation-protocol`
**Certificate:** `black_hole_programme/certificates/BH3_NUMERICAL_VALIDATION_PROTOCOL.json`
**Verdict token:** `BH3_NUMERICAL_VALIDATION_PROTOCOL_SPECIFIED`
**Artifact kind:** `PROTOCOL_SPECIFICATION` · **Lifecycle:** `SPECIFIED`
**Dependency tags:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

This item delivers a **specification and reproducibility contract**, not a
computation. It exists so that no BH-3 complex-frequency / quasinormal-mode
successor is ever created without a pre-declared, independent falsification rail
(the Science Forge independent-rail law). **No spectrum, quasinormal mode, or
off-real-axis solve is run here** — the protocol is the deliverable.

## What the protocol pins (by content hash)

Any prospective numerical complex-`omega` rail MUST reproduce, on the real axis,
the exact certified invariants — copied verbatim from three certificates and
re-checked by the verifier so the spec cannot drift:

1. **`BH2_SYMBOLIC_CROSS_INVARIANT`** — the axial cross scalar
   `a(omega) = i F^r(E,X)/(pi alpha)` as an **exact rational function**
   `(-1536 I w^4 - 3840 w^3 + 1632 I w^2 + 192 w)/(10 w^2 - 15 I w - 5)`, with
   poles `{i, i/2}`, zeros `{0, 2i, i/4 (double)}`, **no real poles**, no real
   zeros except the excluded origin, and the conjugate law
   `a(-omega) = -conj(a(omega))`.
2. **`BH2_GENERAL_L_STRUCTURAL`** — horizon indicial data: Einstein RW ingoing
   exponents `+-2 i m omega` (indicial `omega^2 + s^2/(4 m^2) = 0`), the
   extra-branch residue spectrum `{0 (x2), -4 i m omega, -2 - 4 i m omega}`, and
   the exceptional angular set `l in {0, 1}`.
3. **`BH2C_METRIC_ALL_ORDERS`** — the parity-unified master ODE
   `c2 F'' + c1 F' + c0 F = 0` with `[c2,c1,c0] = [r^2-2r, 2 I w r^2+2r+2,
   6 I w r-6]`, and the infinity exponents `-3` and `-4 I omega + 1`.

## The protocol

- **Problem** — the exterior complex-`omega` boundary-value problem on
  `r in (2m, infinity)` / tortoise `r_*`, ingoing at the horizon
  (`e^{-2 i m omega r_*}`), outgoing at infinity; the target functional is the
  cross pairing `a(omega)`. Axial (Regge–Wheeler), polar (parity-unified master),
  and the fourth-order Bach extra branch.
- **Numerical method — two INDEPENDENT implementations required**, and neither
  may call/reuse the symbolic producers as its own check (agreement across the
  two implementations is the evidence): **(A)** matched-asymptotic shooting in
  `r_*` with analytic Frobenius boundary series and a Wronskian match; **(B)**
  hyperboloidal/analytic Chebyshev spectral collocation with the boundary
  exponents factored out.
- **Convergence** — geometric Cauchy in `N` (spectral) / Richardson of declared
  order `p` in `h` (shooting); `tau_conv = 1e-10` relative.
- **Error control** — ODE-residual `< 1e-9`, boundary mismatch `< 1e-9`, and
  on-shell `r`-independence of the recomputed `a(omega)` across two radii.
- **Real-axis falsification gate** — before ANY off-axis value is trusted, the
  rail must reproduce `a(omega)` at real samples, the conjugate law, the absence
  of real poles, the horizon exponents, the extra residue spectrum, and the
  infinity exponents, all to `tau_conv`.
- **Continuation domain** — continuation into complex `omega` is admissible
  ONLY within a domain that **excludes the certified poles `{i, i/2}`**;
  reproducing the exact pole/zero structure is a necessary precondition. The
  continuation itself is certified/obstructed by the separate item
  `black-hole-complex-frequency-analytic-continuation-gate`.
- **Fail-closed** — any anchor not reproduced, non-converging refinement, method
  disagreement, or real pole is a FAIL and blocks BH-3 vocabulary; a skip or
  timeout is never a pass. Tightening a tolerance or adding an anchor is a new
  (append-only) protocol event.

## What is NOT established (fail-closed)

- the two numerical implementations themselves (specification only);
- any executed validation run or off-real-axis value (nothing is computed here);
- the analytic-continuation certificate (separate item);
- no complex-`omega` mode, symplectic-current continuation, spectrum,
  quasinormal mode, stability, scattering, or positivity result. The protocol is
  a precondition on a future rail, not a BH-3 result; it carries no
  `LORENTZIAN-CAUSAL` tag.

## Verification

- `python3 black_hole_programme/verify_bh3_numerical_validation_protocol.py`
  — schema + anchor content hashes; **anchor cross-consistency** (every pinned
  invariant string equals the value in the anchor certificate on disk);
  protocol completeness (two independent methods, real-axis gate, fail-closed,
  pole-excluding continuation domain); claim-boundary + vocabulary. Runs **no**
  numerics.
- `pytest black_hole_programme/tests/test_bh3_numerical_validation_protocol.py`
  — structural Tier-1 rail.

## Receipts

- Generator: `black_hole_programme/bh3_numerical_validation_protocol.py`
  (reads the three anchors, copies their exact invariants, pins their hashes).

EVIDENCE: `black_hole_programme/certificates/BH3_NUMERICAL_VALIDATION_PROTOCOL.json`

CLOSE-OUT: DONE — independent numerical-validation protocol specified and
pinned to the exact real-frequency anchors; no numerics run, as required.
