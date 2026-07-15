# Einstein sector of pure Weyl gravity

## Status and dependency boundary

This is the separate Einstein-sector theorem requested by the classical
programme.  Its exact nonlinear solution statement is `LOCAL-ALGEBRAIC`; its
cylinder mode and residual-state statements are `REDUCED-MODE`.  It is not a
`LORENTZIAN-CAUSAL` scattering theorem, a Hadamard theorem, or a quantum master
equation result.

The machine-readable theorem ledger is
`bridge/certificates/einstein_sector_theorem.json`.  It is fail-closed against
the certified free BV, cylinder-preimage, helicity, metric-to-residual, and
completed-residual inputs.

## Theorem — Einstein locus and closed-cylinder state separation

Let `(M,g)` be a smooth four-dimensional pseudo-Riemannian manifold and let
the pure-Weyl equation be `B_mn(g)=0`.  If

```text
Ric(g) = Lambda g,
```

then `B_mn(g)=0`.  Consequently every four-dimensional Einstein solution
defines a pure-Weyl solution.  After quotienting the two theories by their
respective gauge groups, the precise statement is a natural map from the
Einstein solution locus to the conformally-Einstein locus of the Bach-flat
moduli problem.  Set-theoretic injectivity after quotienting is not asserted.

The map is generally not onto.  Bach-flat metrics need not be conformally
Einstein, and the certified linear cylinder solution space contains the `A`
and `L` conformal-gravity towers in addition to the Einstein-root `E` tower.
Thus Einstein gravity is an exact, generally proper solution sector.  It is
not an equality of theories and it is not a global Weyl gauge slice.

### Proof of the local implication

In four dimensions the Bach tensor is, up to the repository's overall sign
convention,

```text
B_mn = (nabla^r nabla^s + 1/2 Ric^rs) C_mrns.
```

For an Einstein metric, `R=4 Lambda` and the Schouten tensor is parallel.
The contracted Bianchi identity therefore makes the Weyl tensor
divergence-free, so its double-divergence contribution vanishes.  The second
term is `Lambda` times a trace of the Weyl tensor and also vanishes.  Hence
`B_mn=0`.

This proves a statement about equations and solution loci.  It does not by
itself identify actions, symplectic forms, gauge quotients, observables, or
boundary-value problems.

## Where the helicity-two waves are

Before the final residual quotient, the certified local one-particle BV
cohomology is

```text
H(q)_one-particle = W+ direct-sum W-.
```

The exact null-symbol quotient is two-dimensional and carries little-group
weights `+2` and `-2`.  On the cylinder these radiative modes occur in the
parity-complete `E` tower, beginning at energy two.  This is where the usual
helicity-`±2` gravitational waves live in the present structure: in local
oscillator/BV cohomology and in the unreduced energy-mode module.

The larger Weyl solution space also contains the `A` and `L` towers.  Their
presence is dynamical extra content of the fourth-order equation, not a Weyl
gauge copy of the Einstein tower.

## Why one-particle residual cohomology vanishes

The final residual calculation answers a different question.  It selects the
closed cylinder and gauges all fifteen residual `SO(4,2)` generators,
including the cylinder time translation `D`.  The Cartan identity then
contracts every cochain of nonzero total compact degree.  The exact centered
one-particle window consequently has `H4=0`.

This does not say that the local helicity-two curvature is zero or locally
BRST-exact.  It says that no one-particle class survives a particular global
absolute residual quotient in which time translation is itself treated as
gauge.  The two surviving classes `[W_+^2]` and `[W_-^2]` are two-particle,
ghost-dressed deformation/vertex classes, not gravitons.

Therefore the apparent paradox is a category error:

| Question | Answer in this programme |
|---|---|
| Are there local radiative helicity-`±2` modes? | Yes: `W+ direct-sum W-`, realized by the `E` tower. |
| Are there one-particle states after gauging the full closed-cylinder residual group? | No, in the selected absolute residual degree. |
| Does the latter erase observed radiation? | No. Scattering/Cauchy problems retain time translation and asymptotic symmetries as physical charges and require a different BFV complex. |

## Which proposed relation is true?

| Proposed relation | Verdict |
|---|---|
| Einstein solutions are contained in conformal-gravity solutions | **Established**, understood as a map to the conformally-Einstein Bach-flat locus, with the quotient caveat above. |
| Einstein observables are contained in reduced conformal observables | **Not established.** The gauge groups and residual reductions differ; an observable comparison needs an explicit symplectic/BFV map and boundary conditions. |
| Einstein gravity is a phase | Not intrinsically. This can become meaningful only after a compensator, matter vacuum, or other scale-setting data are supplied. |
| Einstein gravity is a Weyl gauge slice | **False in general.** Non-conformally-Einstein Bach-flat solutions cannot be reached this way. |
| Einstein gravity is a boundary-condition sector | **Yes conditionally.** It is established in the asymptotically dS/Euclidean-AdS semiclassical setting, not yet for the repository's Lorentzian scattering problem. |
| Einstein gravity is an exact solution sector | **Yes.** This is the unconditional theorem proved above. |

The safest summary is:

> Four-dimensional Einstein gravity is an exact, generally proper solution
> sector of pure Weyl gravity.  It becomes a standalone physical sector only
> after additional boundary, charge, and scale data select it.

Equivalently, the hierarchy is

```text
Einstein solutions  proper-subset  pure-Weyl solutions
```

generically, but not

```text
Einstein gravity = Weyl gravity / Weyl gauge.
```

## Boundary and Cauchy-data programme

The known control case is Maldacena's asymptotically de Sitter or Euclidean
anti-de Sitter construction: a Neumann boundary condition selects the
Einstein branch for the semiclassical/tree-level wavefunction.  This is a
boundary projection, not a proof that the full conformal theory and Einstein
theory have identical observables.

Conventional asymptotically flat scattering needs a new
`LORENTZIAN-CAUSAL` theorem with at least these ingredients:

1. retain Poincare/BMS generators as asymptotic charges rather than residual
   gauge;
2. formulate fourth-order Cauchy data and the nonlinear constraint that
   removes `A/L` data while retaining the `E` helicities;
3. prove that the Bach evolution preserves that Einstein constraint;
4. compare the restricted Weyl symplectic current with the Einstein
   symplectic current, including boundary terms and normalization; the flat
   TT Schwartz-core comparison is now a scoped no-go rather than an open
   equivalence;
5. construct the boundary BFV map and prove injectivity/surjectivity on the
   intended observable algebra;
6. only then state an Einstein scattering or Cauchy equivalence theorem.

The load-bearing question for that theorem is

> **Is the Einstein sector dynamically and causally closed under the chosen
> Lorentzian radiative boundary conditions?**

Existence of the Einstein solution locus does not answer this.  The theorem
must determine whether retarded/advanced Bach evolution preserves Einstein
initial data without imposing nonlocal future conditions.  Even if it does,
causal closure alone is no longer sufficient for an honest Einstein
scattering sector: the restricted pairing and charges must be nondegenerate
and match Einstein-Hilbert gravity.  The flat TT Schwartz-core certificate
finds the pure-Weyl restriction identically zero while the Einstein-Hilbert
pairing is nonzero.  A full null-infinity extension must either preserve this
obstruction or identify and justify new corner data.  If causal closure fails
as well, Einstein data can access the larger Bach-flat solution space and the
relationship is only a solution-locus inclusion.

### Commissioned asymptotically flat theorem

The next theorem is explicitly commissioned as follows.

> On declared asymptotically flat function spaces, construct an Einstein
> radiative subcomplex of the Bach complex.  Prove that causal evolution,
> boundary BFV reduction, and the radiative symplectic form restrict to this
> subcomplex; determine the quotient's helicity content and classify every
> complementary Bach-flat asymptotic channel.

Its fail-closed obligations are:

| ID | Required result |
|---|---|
| `AF-E1` | Specify asymptotically flat function spaces and complete fourth-order data. |
| `AF-E2` | Construct retarded and advanced complexes with null-infinity boundary data. |
| `AF-E3` | Separate charged asymptotic conformal transformations from gauge. |
| `AF-E4` | Exclude the non-Einstein branch causally, not by nonlocal future data. |
| `AF-E5` | Prove nonlinear preservation of the Einstein initial-data constraint. |
| `AF-E6` | Identify the Green/current pairing with symplectic flux at null infinity. |
| `AF-E7` | Recover, or refute recovery of, the ordinary helicity-`±2` scattering space. |
| `AF-E8` | Classify extra Weyl solutions as radiative channels or non-radiative data. |

At commissioning, all eight obligations were `OPEN`.  The theorem ledger
refuses the claims that the Einstein sector is causally closed, that ordinary
graviton scattering has been recovered, or that the extra Weyl channels have
been classified.

The first follow-on bootstrap is now recorded in
`notes/conformal-asymptotically-flat-einstein-bootstrap.md`.  It proves exact
linearized nonzero-mode preservation of the Einstein Cauchy-data kernel and
marks `AF-E1`, `AF-E3`, and `AF-E5` as `PARTIAL`; it does not alter any full
`LORENTZIAN-CAUSAL` claim flag.

On the closed cylinder, the corresponding alternative must use a relative or
boundary BFV complex in which `D` is the Hamiltonian.  Simply deleting the
`D` ghost from the absolute complex is not a proof.

## Einstein-Hilbert scale

Pure four-dimensional Weyl gravity has a dimensionless coupling and no
intrinsic Einstein-Hilbert mass scale.  A scale can arise in an enlarged
model from a Weyl compensator with a `phi^2 R` coupling and a nonzero
gauge-fixed value, from matter expectation values/spontaneous Weyl breaking,
or from boundary/background curvature data.  None of those mechanisms is
part of pure Weyl gravity.

The minimal compensator mechanism is now certified separately in
`notes/conformal-compensator-einstein-phase.md`.  A constant nonzero
Stueckelberg frame generates `c1=zeta v^2`, restores the flat TT massless-root
pairing, and leaves an opposite-residue massive spin-2 branch.  The exact
gauge-fixed theory is therefore Einstein--Weyl gravity, not pure Einstein
gravity.  It does not define the D-quotient programme's monotone scalar clock
and does not establish causal removal of the extra branch, nonlinear closure,
scattering equivalence, anomaly cancellation, or spontaneous breaking.

The subsequent flat TT theorem in
`notes/conformal-compensated-einstein-causal-subsector.md` now establishes a
scoped causal removal: on source-free real-time Schwartz data, the local
constraints `chi=0` and `n.chi=0` propagate and select a nondegenerate
Einstein-Hilbert helicity-`+/-2` phase space.  This does not remove the massive
branch from the full theory or establish sourced, nonlinear, BV, boundary, or
scattering closure.

The local projector hardening in
`notes/conformal-compensated-einstein-local-projectors.md` further gives the
explicit on-shell differential splitting
`Pi_E=1+Box/M^2`, `Pi_M=-Box/M^2`.  It is support-nonincreasing and
symplectically block diagonal on already-TT fields, but it neither makes the
spatial TT reduction local nor preserves an Einstein-only sector under a
generic source.

The sourced-defect preflight in
`notes/conformal-compensated-einstein-sourced-defect-preflight.md` sharpens
that source caveat.  In the linearized compensated theory, conventional
same-source Einstein closure is equivalent to the independent differential
condition `Q(T)=0`; stress-tensor conservation and the Weyl trace Ward identity
are not sufficient.  Arbitrary same-source closure is therefore refuted on
flat space.  Fixed-source solutions form an affine sector, so a genuine BV
subcomplex must include the matter fields and extend the now-certified vacuum
minimal complex.

The local minimal compensated BV theorem in
`notes/conformal-compensated-quadratic-minimal-bv.md` now supplies the vacuum
metric--scalar complex.  In the `v!=0` invariant chart it splits exactly into
the Einstein--Weyl metric--Diff minimal complex and a contractible Weyl
Stueckelberg doublet, with nilpotency, formal cyclicity, chain contraction, and
nondegenerate reduced pairing certified.  Physical cohomology, global zero
modes, the nonminimal causal complex, dynamical matter, and the full classical
import freeze remain open.

## Background inventory

All smooth four-dimensional Einstein metrics survive the pure-Weyl equation,
including Ricci-flat and nonzero-cosmological-constant families, subject of
course to the chosen global and boundary regularity conditions.  Their Weyl
transforms are also pure-Weyl solutions.

The additional solution space contains both conformally-Einstein metrics and
Bach-flat metrics that are not conformally Einstein.  At the certified
linearized cylinder level, the extra content is visible as the `A` and `L`
towers alongside `E`.  A complete nonlinear classification of all extra
Bach-flat solutions is not claimed.

## Plain-language conclusion

Einstein gravity sits exactly inside conformal gravity as one class of
solutions, but conformal gravity generally has additional solutions that
cannot be removed by a Weyl transformation.  Under certain de Sitter or
Euclidean anti-de Sitter boundary conditions, those extra solutions can be
excluded and Einstein gravity is recovered.  Whether the same happens for
real-time asymptotically flat physics and gravitational scattering remains a
separate causal problem.

## Sources and verification

Primary external controls:

- Juan Maldacena, *Einstein Gravity from Conformal Gravity*,
  <https://arxiv.org/abs/1105.5632>.
- H.-S. Liu, H. Lu, C. N. Pope, and J. Vazquez-Poritz, *Not
  Conformally-Einstein Metrics in Conformal Gravity*,
  <https://arxiv.org/abs/1303.5781>.

Deterministic verification:

```bash
python3 -m bridge.einstein_sector.certificate --verify bridge/certificates/einstein_sector_theorem.json
python3 -m unittest bridge.einstein_sector.tests.test_certificate
```

The verifier checks content hashes and theorem-bearing fields of every
imported certificate.  It deliberately fails if one-particle residual
cohomology is promoted, the E/A/L inventory changes, the helicity quotient
ceases to be exact, or a false scattering flag is inserted.
