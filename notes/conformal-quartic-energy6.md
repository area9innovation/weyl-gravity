# Conformal P4: compact-energy-six quartic block

## Status

This is a staged calculation, **not yet a Weyl-gravity quartic
certificate**.  Its `AA/EA/EL` target is a provisional oscillator block;
the compact conformal/Taub audit has not yet shown that these individual
states survive the full global BRST reduction.  The executable staging rail is
`symbolic/verify_conformal_quartic_energy6.py`.  It fixes the target
representation, shell pairing, exchange sign, exact reduced-resolvent
convention, archive schema and complete reduced cokernel coordinates.  It
fails closed when asked for a physics certificate without complete exact
contact/current data.

## The generator is compact `D`, not flat `P_0`

C1a established that the flat time-translation generator `P_0` has the
rank-two Jordan algebra used in C0c, while compact cylinder time translation
`D` is diagonal on the normalizable oscillator towers:

```text
E_J: Delta=2J,
A_J: Delta=2J+1,
L_J: Delta=2J+2.
```

The proposed energy-six effective Hamiltonian is a `D`-shell calculation.
At the oscillator level, a semisimple intermediate block of energy `lambda`
has

```text
(H0_lambda-6)^(-1) = 1/(lambda-6),
```

not a flat-Jordan nilpotent series.  The general identity

```text
[(lambda-6)I+N]^(-1)
  = sum_{r=0}^{k-1} (-1)^r N^r/(lambda-6)^(r+1),  N^k=0,
```

is exact and is tested by the staging script, but a nonzero `N` is rejected
for a cylinder block unless a separate gauge-fixed derivation supplies its
basis and proves that it is genuinely nonsemisimple.  Importing the flat
`P_0` nilpotent here would mix two deformation complexes.

## Which energy-six block?

Use doubled-spin labels for `SO(4)=SU(2)_L x SU(2)_R`.  The relevant one-
particle chiral irreps are

```text
E2: (4,0) + (0,4),
A3: (3,1) + (1,3),
A4: (4,2) + (2,4),
L4: (4,0) + (0,4).
```

The exact tensor-product enumerator finds that the only irrep common to

```text
Sym^2 A3,  E2 tensor A4,  E2 tensor L4
```

is twice-spin `(4,4)`, i.e. ordinary spin `(2,2)`.  Before parity its
multiplicities in those three sectors are `(1,2,2)`.  Parity exchanges the
two copies in each `E2 X4` sector, so a fixed parity matching the `A3 A3`
state leaves one copy of each.  The reduced Wigner--Eckart basis is therefore

```text
( |A3 A3>, |E2 A4>, |E2 L4> ),
```

with

```text
H0,6 = 6 I3,
J6 = diag(+1,-1,-1).
```

The `(2,2)` irrep has dimension 25, so this reduced matrix represents a
75-dimensional magnetic oscillator block with inherited signature `(25,50)`.
This `J_6` and target projector are provisional until global reduction.

This is **not** the complete energy-six oscillator shell.  The latter contains the
partitions `6`, `2+4`, `3+3`, and `2+2+2`, has dimension 2062 and signature
`(1166,896)`.  There are additional `A3 A3 <-> E2 A4` and
`A3 A3 <-> E2 L4` reduced irreps enumerated by the script.  A theorem about
the full shell must compute those blocks too, as well as the remaining
one-/three-particle and spectator sectors.  The three-channel block is the
first joint `A4/L4` diagnostic, not the whole `P_6` matrix.

## Exact assembly convention

For exact reduced contact data `C` and intermediate blocks `lambda`, the
staged engine evaluates the **normal-ordered connected tree** operator

```text
Veff,6 = C - sum_lambda L_lambda
                       (H0_lambda-6)^(-1)
                       R_lambda,

S6 = J6 Veff,6 - Veff,6^dagger J6.
```

Here the exchange sum means the finite one-internal-line contribution after
connected Wick selection, cancellation of the disconnected vacuum factor,
and subtraction/LSZ normalization of reducible external-state corrections.
It is not the unqualified quantum Feshbach operator.  The latter also has
infinite affine three-particle self-energy tails and requires a regulated
spectral sum, counterterms, and state renormalization; this distinction is
proved by `symbolic/verify_conformal_quartic_intermediates.py` and recorded
in `notes/conformal-quartic-intermediates.md`.

The algebraic identification with the metric-deformation complex is proved
separately in `notes/conformal-deformation-bridge.md` and checked by
`symbolic/verify_conformal_deformation_bridge.py`:

```text
P S2 P=J_P Veff,6-Veff,6^dagger J_P.
```

It is conditional on using the same stationary normalization and subtraction
convention in both terms. Ambiguity-independence additionally follows from
the stronger complete-shell statement `P V3 P=0`; first-order
`J`-pseudo-Hermiticity alone is insufficient.

Since `H0,6=6 I`, the compact-shell metric-deformation map vanishes.  Every
entry of the anti-Hermitian `S6` is therefore a cokernel coordinate.  The
script returns all nine real coordinates: three imaginary diagonal entries
and the real and imaginary parts of the three independent off-diagonal
entries.  A synthetic exact-rational fixture verifies the assembly signs,
ordinary denominators and coordinate reconstruction.  It is visibly labelled
as synthetic and is not used as Weyl data.

## Chosen field-level formulation

The cleanest primary calculation is the original metric fourth-order Weyl
action on the cylinder.  The quartic contact follows directly from the
four-wave coefficient of

```text
sqrt(-g) (R_mn R^mn - R^2/3).
```

Exchange should be assembled from cubic currents and the complete
gauge-fixed/bordered quadratic metric Hessian in an `S^3` harmonic basis.
This automatically retains lapse, shift, longitudinal and Weyl-constraint
components needed to cancel gauge dependence.  Faddeev--Popov ghosts do not
form a tree exchange between purely bosonic external states, but BRST closure
and representative independence must still be checked.  An independent
ordinary-derivative auxiliary/Stueckelberg calculation would be a valuable
equivalence rail, not a source of omitted contributions in the primary
metric computation.

The existing C1b perturbiner already supplies exact curved-cylinder
geometry, normalized `E/A/L` harmonics, and cubic coefficients, but it is
hard-coded to three multilinear waves.  P4 requires:

1. extend the subset algebra to four waves;
2. add the fourth-order determinant term

   ```text
   (tr A)^4/384 -(tr A)^2 tr(A^2)/32 +tr(A^2)^2/32
   +tr A tr(A^3)/12 -tr(A^4)/8;
   ```
3. expose the quadratic Hessian and cubic currents in an import-safe module;
4. invert each internal cylinder harmonic block with diffeomorphism plus
   Weyl gauge constraints;
5. assemble every crossing/time ordering and the independently constructed
   reverse block.

The determinant formula is independently verified in exact algebra by the
staging script.

## Fail-closed acceptance rails

An actual archive is accepted only if all of the following are certified:

1. external harmonic normalization;
2. external equations of motion and BRST closure;
3. compact global conformal/Taub/linearization-stability reduction, including
   survival and pairing of the proposed external target and treatment of the
   Hessian-null t block;
4. quartic contact with all multilinear orderings;
5. cubic currents for all pairings;
6. the internal inverse-Gram/index-raising convention;
7. complete internal metric harmonic content;
8. constraint and auxiliary-component contributions;
9. internal-gauge independence;
10. external Ward identities;
11. Bose, parity and `SO(4)` covariance;
12. an independently assembled reverse/`J`-adjoint block;
13. an explicit map from covariant action coefficients and bordered Hessians
    to the stationary Born operator, including the overall `i` convention,
    derivative-interaction contact terms, both time orderings, state/LSZ
    normalization and compact-energy denominators;
14. an explicit normal-ordering and connected-one-line projection;
15. cancellation/exclusion of vacuum, loop and self-energy contractions;
16. subtraction of reducible external-state corrections.

The archive must use exact SymPy-readable entries; floating-point vertex
data are rejected.  It must also carry a 64-character SHA-256 digest for
each independently generated input in this concrete manifest:

| artifact under `build/conformal-p4/energy6/` | required content |
| --- | --- |
| `target_basis.json` | normalized parity-projected `(2,2)` Clebsch--Gordan basis and `J_6` |
| `global_constraint_reduction.json` | compact BRST/Taub reduction, external-state survival/pairing and Hessian-null t-block disposition |
| `contact_forward.json` | all directed entries of the exact four-wave contact block |
| `contact_reverse.json` | independently assembled physical-adjoint contact block |
| `quadratic_hessian_de_donder_weyl.json` | every internal harmonic Hessian, gauge border and exact inverse residual |
| `cubic_currents_all_pairings.json` | left/right currents for every external pairing and internal harmonic |
| `exchanges_forward.json` | all channel/order contributions and their sum |
| `exchanges_reverse.json` | independently assembled reverse exchanges |
| `ward_and_gauge_variants.json` | pure-gauge external replacements and a second internal gauge |
| `stationary_born_mapping.json` | covariant-to-stationary phase, normalization, time-ordering and denominator bridge |
| `connected_tree_scope.json` | normal ordering, connected Wick selection, vacuum cancellation and loop/self-energy scope |
| `external_state_subtractions.json` | reducible/external-leg terms removed in the effective Hamiltonian convention |

The combined archive must declare

```text
operator_scope = connected_tree_contact_plus_one_line_exchange
```

and the staging script recomputes every artifact SHA-256 rather than merely
checking its shape.  The stationary-Born artifact also duplicates the exact
contact/intermediate inputs and the canonical `Veff`, source and nine
cokernel coordinates.  It also records the digest of every source artifact.
The loader cross-links those inputs to the combined archive and all source
hashes, then recomputes every output, so a newly hashed but stale or unrelated
matrix is rejected.  Until all rails, files, semantic links and matching
digests are present, the script prints

```text
P4 STATUS: STAGED, NOT A WEYL QUARTIC CERTIFICATE.
```

## Genuine blockers

The following data do not yet exist in a complete importable exact form:

* the remaining entries of the now-operational four-wave contact engine;
* the compact global BRST/Taub reduction of the provisional target and the
  Hessian-null t channel (no ordinary t inverse exists);
* the remaining non-null gauge-bordered exchange data for s and u;
* the complete cubic-current table connecting all target and finite
  one-internal-line tree modes;
* a proof that the target archive exhausts contractible/gauge components;
* explicit connected-tree/normal-ordering and external-state subtraction
  records (the full unqualified quantum Feshbach sum is an infinite,
  separately regulated object);
* the covariant-action-to-stationary-Born normalization and time-ordering
  certificate required to apply the abstract deformation bridge;
* the remaining reduced irreps and spectator sectors needed to upgrade the
  75-dimensional target certificate to the full 2062-dimensional shell.

No contact-only or TT-only number should be interpreted as a quartic
obstruction before these items close.  In particular, the ordinary cylinder
denominator correction above must be preserved: inserting a flat Jordan
nilpotent would produce a formally elaborate but physically mismatched
answer.

`symbolic/verify_conformal_quartic_contact.py` loads the verified C1b
jet/harmonic core without executing its top-level calculation, extends the
inverse metric and determinant algebra to four waves, and constructs exact
normalized parity-fixed `(2,2)` representatives.  Two forward contact data
are currently fixed:

```text
C_AA,AA^(4)=1009/(20250 pi^2),
C_EL,AA^(4)=1099/(43200 pi^2).
```

The branch-changing value includes the matching-parity partner; its raw
chiral seed is `1099 sqrt(2)/(86400 pi^2)`. Every external harmonic norm and
all 16 inverse-metric subsets pass exactly. The independently assembled
reverse curvature run has the identical complete radial density and real
coefficient. On the ordered `(AA,EL)` block this gives the contact-only
source

```text
[1099/(21600 pi^2)] [[0,1],[-1,0]].
```

These entries validate the four-wave engine and begin the forward/reverse
contact artifacts. The displayed source is an exchange-cancellation target,
not an obstruction; it remains non-diagnostic until the complete exchange
artifacts close.
