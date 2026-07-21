# General-l structural extension: axial exact sequence, symbolic l

**Certificate:** `certificates/BH2_GENERAL_L_STRUCTURAL.json`
**Result token:** `BH2_GENERAL_L_AXIAL_EXACT_SEQUENCE_SYMBOLIC_L_PAIRING_NOT_ACTIVATED`
**Dependency tags:** `LOCAL-ALGEBRAIC` + `REDUCED-MODE`. **Lifecycle:** `CLASSIFIED`.
**Disposition:** `AXIAL_SYMBOLIC_L_PROVEN + PAIRING_NOT_ACTIVATED`.
**Producer:** `bh2_general_l_structural.py` ·
**Verifier:** `verify_bh2_general_l_structural.py` (l=3 independent recomputation) ·
**Fast rail:** `tests/test_bh2_general_l_structural.py`

## Stop-condition gate (fixture-only branch)

The item's stop condition is conditional on the terminal polar
universal-quantifier repair. `BH2_POLAR_QUANTIFIER_REPAIR` closed **fixture-only**
(the generic-omega inertia / no-real-exceptional-frequency statement is
fail-closed; only `a != 0` is all-omega). Per the stop condition, the generic-l
invariant **cross pairing** theorem is therefore recorded **NOT_ACTIVATED** until a
symbolic-omega polar identity exists, and **no pairing statement is extrapolated
from the l=2 samples**.

What this certificate establishes is the l-dependence that transports *without*
the omega-pairing and *without* mode sampling: the axial Ricci-to-Bach
exact-sequence operator structure as an exact function of the angular eigenvalue
`Lambda = l(l+1)`. Every angular factor is derived from the Legendre identity
`(1-x^2)P'' = 2x P' - Lambda P` applied to a generic `P_l(x)`; a finite list of l
values is never used to establish the generic statement.

## Proven (axial parity, both branches, generic l >= 2)

1. **Einstein/RW branch master potential.** Eliminating `H0` from the two
   independent axial `delta Ric` rows and setting `psi = B h1/r` gives the
   Regge-Wheeler master `B(B psi')' + (omega^2 - V)psi = 0` with
   ```
   V = B(Lambda/r^2 - 6 m/r^3),   Lambda = l(l+1),
   ```
   exact proportionality factor `-r^6` — identical to the certified l=2 reduction.
   At `Lambda = 6` this is the certified `V = B(6/r^2 - 6 m/r^3)`. The angular
   factor enters *only* as `Lambda/r^2`; the spin term `-6m/r^3` is l-independent.

2. **RW horizon indicial (ingoing dimension).** At the regular singular point
   `r = 2m`, `psi ~ (r-2m)^s` gives the indicial polynomial
   `omega^2 + s^2/(4m^2) = 0`, so `s = +- 2 i m omega`, **independent of Lambda**
   (the `Lambda/r^2` term is regular at `r=2m` and enters only at subleading
   order). The RW ingoing-regular dimension is therefore **1 for every l**.

3. **Extra branch (Ricci-to-Bach carrier).** For the trace-free divergence-free
   axial carrier `psi_ab` (`psi_vphi = p S_l`, `psi_rphi = q S_l`,
   `psi_xphi = c (Lambda P_l - 2x P_l')`, third component fixed by the divergence
   constraint), the equation `(1/2)Box psi + C psi = 0` in the ingoing EF chart
   has horizon residue spectrum
   ```
   { 0 (x2),  -4 i m omega,  -2 - 4 i m omega },   INDEPENDENT of Lambda,
   ```
   identical to the certified l=2 spectrum (BH2A stage 2). The extra-branch
   ingoing structure is thus **l-independent for all l >= 2**.

4. **Operator composition is l-generic.** The split identity
   `delta B = (1/2)Box dRic + C.dRic` (axial, `dR=0`) is background-tensorial
   (certified general, BH2B stage 1); under tensor-harmonic reduction l enters
   **only** through `Lambda = l(l+1)`.

5. **Exceptional set `{0, 1}`.** The axial vector harmonic
   `S_l = -(1-x^2) P_l'` vanishes at `l = 0` (`P_0` constant), and the
   extra-branch angular component `H2_l = Lambda P_l - 2x P_l'` vanishes at
   `l = 1` (`Lambda = 2`, `P_1 = x`). For `l >= 2` both are nonzero and
   independent, so the full exact sequence is carried. `l = 0, 1` are isolated
   exceptional representations, never folded into the generic theorem.

## NOT_ACTIVATED (this item's stop condition)

The generic-l invariant **cross pairing / cross-scalar** theorem (both parities)
is **NOT_ACTIVATED**. Activation condition: a symbolic-omega polar identity —
`BH2_POLAR_QUANTIFIER_REPAIR` **route B**, the gauge-radical identity
`Z = E - (K^{-1} a^H).X` symplectically null for all real omega (the even-parity
twin of the axial RW-null theorem). No cross-pairing rank or scalar is
extrapolated from the nine l=2 polar samples.

## Evidence and verification

- **Independent verifier** (`verify_bh2_general_l_structural.py`, 10/10). The
  decisive rail recomputes the axial reduction at a **different harmonic**,
  `l = 3` (`Lambda = 12`), with the explicit Legendre polynomial
  `P_3 = (5x^3-3x)/2` and **no symbolic Lambda**, confirming: RW potential
  `B(12/r^2 - 6m/r^3)`; extra-branch residue `{0(x2), -4imw, -2-4imw}`. Because
  `l = 3 != l = 2` and the spectrum is identical, the Lambda-independence is not
  an l=2 artifact. A second rail is the l=2 positive control against the
  certified BH2A operator/reach.
- **Fast rail** (`tests/test_bh2_general_l_structural.py`, 7/7, sub-second):
  disposition, symbolic-l RW branch, l-independent extra residue, exact
  exceptional-harmonic degeneration, stop-condition gate, no polar overclaim,
  BH-3 vocabulary lock.

## What is NOT claimed

The polar-parity detailed symbolic-`Lambda` radial reduction (Zerilli potential
and polar extra-branch residue) is **not** computed here — the same Legendre
method applies and is the immediate parallel step. `l = 0, 1` are excluded as
exceptional representations. No complex omega, asymptotic phase space, stability,
quasinormal, ringdown, scattering, positivity, particle, or nonlinear statement is
made.

CLOSE-OUT: DONE — the fixture-only branch of the stop condition is discharged.
The generic-l cross-pairing theorem is recorded NOT_ACTIVATED (activation = the
symbolic-omega polar identity, route B) with no extrapolation from l=2 samples;
and the axial Ricci-to-Bach exact-sequence structure is proved symbolically in l:
the RW master potential `B(l(l+1)/r^2 - 6m/r^3)`, the l-independent RW horizon
indicial (`s = +-2imw`, ingoing dimension 1), the l-independent extra-branch
residue spectrum `{0(x2), -4imw, -2-4imw}`, l-generic operator composition, and the
exact exceptional set `{0,1}`. Verified by an independent l=3 recomputation and a
sub-second fast rail.
EVIDENCE: black_hole_programme/certificates/BH2_GENERAL_L_STRUCTURAL.json
(symbolic-Lambda axial reduction; RW potential factor -r^6; horizon exponents
+-2imw and extra residue {0(x2),-4imw,-2-4imw} both Lambda-independent; l=3
independent recomputation matches l=2; exceptional set {0,1}; pairing
NOT_ACTIVATED with named activation identity). Dependency tags LOCAL-ALGEBRAIC +
REDUCED-MODE; lifecycle CLASSIFIED; disposition
AXIAL_SYMBOLIC_L_PROVEN + PAIRING_NOT_ACTIVATED.
