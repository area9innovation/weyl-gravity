# Invariant normal form of the Einstein/additional pairing extension

## Verdict

`BH2_SYMPLECTIC_EXTENSION_HYPERBOLIC_NORMAL_FORM`
(certificate `black_hole_programme/certificates/BH2_SYMPLECTIC_NORMAL_FORM.json`,
tag `LOCAL-ALGEBRAIC`, lifecycle `CLASSIFIED`).

Proof-first classification of the pairing carried by

    0 → E_Einstein → E_Weyl → E_extra → 0

under the pure-Weyl Lee–Wald pairing, with **no assumed canonical
splitting**. All of it is finite-rank linear algebra done symbolically
before any radial series; the repaired fixtures enter only as controls.

## Hypotheses (certified elsewhere, cited, not re-derived)

Work with the Hermitian form `K(u,v) = i F^r(u,v)/(πα)`:

- `K(E,E) = 0` — the Einstein line is isotropic (certified exactly, both
  parities);
- `K(G,·) = 0` — the conformal direction is in the radical (certified:
  every conformal pairing vanishes identically);
- `a = K(E,X)` — the cross scalar;
- lift ambiguity is exactly `X → X + βE + γG`.

## Theorem (a ≠ 0)

1. **a is invariant** under every admissible shear.
2. The additional self-pairing transforms as **d → d + 2 Re(β̄a)**. For
   a ≠ 0 this map is *onto* ℝ, so d can be set to any real value — in
   particular 0, via the explicit witness **β\* = −d·a/(2|a|²)**. Hence
   **d carries no invariant content whatsoever**.
3. On span(E,X) the matrix is `[[0, a],[ā, d]]` with **det = −|a|² < 0**:
   nondegenerate, rank 2, **inertia (1,1)**, normal form the
   **hyperbolic plane** `[[0,a],[ā,0]]`.
4. E is an isotropic line in a rank-2 signature-(1,1) block, hence
   **Lagrangian** (maximal isotropic) in that block.
5. On span(E,X,G) the radical is exactly span(G), and the quotient is the
   hyperbolic plane of (3).

## Degeneration (a = 0)

The shear action `2 Re(β̄a)` collapses to zero, so **d becomes
invariant**: the form is `[[0,0],[0,d]]`, rank ≤ 1, E joins the radical,
and the **sign of d is then a genuine invariant**. The two branches are
qualitatively different, so the theorem is stated conditionally on a, as
the work item requires.

## This resolves the open "invariant extra-block sign" question

Answered **negatively** for a ≠ 0: there was never anything to certify,
because every additional self-pairing datum is removable by an admissible
lift shear. The invariants are `(rank, inertia) = (2, (1,1))` and the
cross class of a. This retires the question as posed — it does not leave
it open, and it does not assign a sign.

It also explains, structurally, the empirical pattern certified in
`BH2B_COMPOSED_REPAIR`: cross constants invariant, extra-block constants
representative-dependent. That was the shadow of this normal form.

## Fixture controls

The certified repaired constants satisfy the hypotheses at both parities
and both frequencies: E self-pairing exactly zero (axial recorded as `0`;
polar absent because identically zero), and every cross entry nonzero —
so the a ≠ 0 branch is the physically realised one on all certified data.

## Decisive mutations

- **M1.** Arbitrary admissible shears move d while leaving a and det
  (hence rank and inertia) fixed — exactly the representative-dependence
  the theorem predicts.
- **M2.** At a = 0 the same shears **cannot** move d — the degeneration is
  real, not an artifact of the parametrisation.

## Verification discipline

The independent rail is independent *in method*, not just in
implementation: the producer proves the theorem by symbolic shear
algebra, while the verifier re-derives every claim by exact rational
numerical linear algebra over a deterministic sample grid (144 shear
trials), diagonalising to read inertia and testing removability
constructively. Agreement across two different methods is the evidence.

A conjugation error was caught by the producer's own assert during
development: the transformation law is `d → d + 2 Re(β̄a)`, **not**
`2 Re(βa)`. The conclusion is unchanged (the map is onto ℝ either way),
but the formula and the removal witness were corrected accordingly.

## What was NOT established

- the symbolic-frequency value of the cross scalar a — now a sharply
  targeted calculation, since a is the *only* invariant left to compute;
- general ℓ;
- any dynamical, Hilbert-space, particle or unitarity reading of the
  inertia. No sign is assigned to an additional branch from any one
  canonical lift, and no canonical direct-sum splitting is asserted.

## Receipts

```bash
python3 black_hole_programme/bh2_symplectic_normal_form.py          # producer (<1 s)
python3 black_hole_programme/verify_bh2_symplectic_normal_form.py   # independent rail (144 trials)
python3 -m pytest black_hole_programme/tests/test_bh2_symplectic_normal_form.py -q
```

## Close-out

```text
CLOSE-OUT: DONE — the complete stop condition is met. The basis-change theorem is human-verifiable and certified: rank, radical, isotropic/Lagrangian status, complete-block inertia, cross-pairing invariance, and the exact classification of which additional self-pairing data can and cannot survive X -> X + beta E and conformal shifts (none can, for a != 0). The theorem is stated conditionally on the nonzero cross scalar a and includes the a = 0 degeneration as a qualitatively distinct branch. Decisive basis-shear mutations are included in both branches, and the repaired fixtures are used as controls only, exactly as the item scopes them.
EVIDENCE: black_hole_programme/certificates/BH2_SYMPLECTIC_NORMAL_FORM.json (producer < 1 s, fast rail 7/7, independent method-distinct rail 144 exact rational shear trials, all checks passed)
```
