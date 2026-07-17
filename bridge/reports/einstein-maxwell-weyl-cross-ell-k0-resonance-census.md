# Exact cross-ell `k=0` resonance census

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

The first distinct-input-`ell` gate has been audited exactly.  For every

```text
2 <= ell_1 < ell_2 <= 96,
```

all three Einstein-minus, extra, and Einstein-plus input primaries were
paired with all three target primaries, both temporal sum/difference
channels, and an angular superset covering both parity choices.  There are
no distinct-`ell` frequency collisions and no target-shell resonances.

The audit does not use floating point to decide equality.  If `A`, `B`, and
`C` are the squared input and target frequencies, resonance requires

```text
(C-A-B)^2 - 4*A*B = 0.
```

Every such expression was expanded canonically over `Q` in square roots of
distinct squarefree positive integers.  The exact audit contains 40,185
frequency-collision checks and 723,330 squared-resonance checks.  Uniform
branch bounds reduce the angular audit to

```text
sum:        L = ell_1+ell_2-2, ell_1+ell_2-1, ell_1+ell_2;
difference: L = ell_2-ell_1,   ell_2-ell_1+1, ell_2-ell_1+2.
```

The closest numerical channel is

```text
extra(ell=5) x Einstein-plus(ell=34), difference
  -> Einstein-minus(L=30),
```

with frequency defect approximately `4.5469744254234e-05`.  Its exact
squared-resonance polynomial is nonzero, so this is a near-miss rather than
a hidden resonance.

This is a `G2` finite-window result.  It does not promote the unbounded
cross-`ell` cone.  The next gate is to turn the six boundary-offset families
into a uniform Diophantine/nonresonance proof and then compute the mixed
source projections.  Within the certified window, any second-order failure
must be a source/cokernel effect rather than a nonzero-frequency determinant
zero.

## Verification receipt

Date: 2026-07-18.

- Tier 0: scoped Python compilation, JSON parsing, and diff checks passed in
  `0.06 s`.
- Tier 1: the full exact producer replay, separately implemented full exact
  verifier, and four fast certificate-contract tests passed in `51.0 s`.
- Tier 2 was not run because this adds no shared operator or changed upstream
  input and promotes only a fail-closed `G2` finite window.
- Tier 3 was not run because the unbounded theorem and mixed source remain
  explicitly open.
