# Quantum team brief: does the \(D\)-contraction survive quantization?

## Commission

Answer one question:

\[
\boxed{
\text{Is }D\text{ genuinely gauge after adding clocks, interactions, quantization, or boundaries?}
}
\]

Your task is **not** to assume the classical quotient and decorate it with loop
corrections.  Construct the strongest possible quantum obstruction to the
\(D\)-Cartan identity, then determine whether it is absent, removable, or a
nontrivial anomaly.

The classical baseline is schematically

\[
[Q,\iota_D]=\mathcal L_D.
\]

The quantum question is whether renormalized operators exist with

\[
Q_\hbar=Q+\hbar Q_1+\cdots,
\qquad
\iota_{D,\hbar}=\iota_D+\hbar\iota_1+\cdots,
\]

such that

\[
[Q_\hbar,\iota_{D,\hbar}]=\mathcal L_{D,\hbar}
\]

on the declared quantum observable algebra.  First define the renormalized
Ward operator \(\mathcal L_{D,\hbar}\); do not assume without proof that the
right-hand side receives no operator, boundary, or central correction.

The centered classical classes \([W_+^2]\) and \([W_-^2]\) are
deformation/vertex classes, not one-particle gravitons.

## Work package Q-D1: classify the obstruction

Define the defect

\[
\mathcal A_D=
[Q_\hbar,\iota_{D,\hbar}]-\mathcal L_{D,\hbar}.
\]

At first order, expose every term:

\[
\mathcal A_D^{(1)}=
[Q,\iota_1]+[Q_1,\iota_D]-\mathcal L_D^{(1)}.
\]

Derive its consistency condition from \(Q_\hbar^2=0\) and the Ward algebra,
identify the exact local/relative cohomology group in which it lives, and
classify the most general candidate before computing a coefficient.  Include
bulk, boundary, corner, zero-mode, measure, and central-extension candidates.

For each candidate determine exactly one status:

1. `ZERO`: the candidate vanishes by an exact identity;
2. `EXACT_REMOVABLE`: it is quantum-BRST exact and an allowed finite
   counterterm restores the identity;
3. `NONTRIVIAL_ANOMALY`: its cohomology class is nonzero;
4. `UNDEFINED_ANALYTICALLY`: the required renormalized operator algebra has
   not been constructed, so no anomaly-freedom claim is permitted.

The strongest counterexample is a nonzero consistent class with a computed
coefficient in an admissible renormalization scheme, or a boundary/zero-mode
central term that cannot be removed while preserving the other Ward identities.

## Work package Q-D2: restore or obstruct the QME

Solve the renormalized quantum master equation in the required order:

\[
\frac12(S,S)-i\hbar\Delta S=0.
\]

Start with pure Weyl gravity and then add a conformally coupled scalar.  Keep
the following ledgers separate:

- local Weyl anomaly;
- diffeomorphism anomaly;
- residual \(SO(4,2)\) anomaly;
- the component specifically obstructing \(D\);
- boundary and corner anomalies;
- regularization and finite-counterterm dependence;
- zero-mode, Jacobian, and measure contributions.

Classify local counterterms and anomaly cohomology before calculating
determinants or coefficients.  A trace anomaly, beta function, background
determinant, or vanishing local gauge anomaly is not by itself the residual
\(D\)-anomaly.  Do not infer residual anomaly freedom from local anomaly
freedom.

Respect the lifecycle without implicit promotion:

```text
CLASSIFIED
COEFFICIENT_COMPUTED
QME_RESTORED
RESIDUAL_TRANSFERRED
LORENTZIAN_CERTIFIED
```

No residual quantum transfer or quantum pairing claim may precede
`QME_RESTORED`.  No Lorentzian claim may be inferred from a reduced cylinder
or Euclidean spectral calculation.

## Work package Q-D3: quantum cohomology and pairing

Only after the applicable QME is restored, transfer the corrected differential
through the independently verified classical contraction using `pi_cl` for the
homological projection.  Compute whether quantum corrections:

- regenerate one-particle classes;
- mix \([W_+^2]\) and \([W_-^2]\);
- turn a topological direction into a dynamical direction;
- change ghost number, Hermiticity, or positivity properties;
- create a new boundary or zero-mode sector.

Compute the quantum-deformed Gram matrix

\[
G(\hbar)=I_2+\hbar G_1+\hbar^2G_2+\cdots
\]

with the order, scheme, real structure, and normalization stated.  Supply exact
or symbolically certified expressions for \(G_k\), its Hermiticity defect,
eigenvalue/signature data, and changes under allowed counterterms.  Do not
hard-code \(I_2\) as the computed answer.

The critic wins this rail if the Cartan identity has a nontrivial anomaly, if
the QME cannot be restored, or if a transferred correction creates a physical
negative or non-Hermitian direction.  The construction survives only after a
restored QME and certified residual transfer.

## Work package Q-D4: matter-content selection

After the scalar test, evaluate combinations of:

1. conformal scalars;
2. Weyl and Dirac fermions;
3. Abelian and non-Abelian Yang--Mills multiplets;
4. conformal compensators.

For each spectrum compute the coefficient of the actual obstruction class
\([\mathcal A_D]\), not merely familiar trace-anomaly coefficients.  Record
statistics, reality conditions, representations, multiplicities, regulator,
and boundary conditions.  Determine whether cancellation is accidental,
scheme-independent, compatible with all Ward identities, and stable under
allowed masses or interactions.

Treat anomaly cancellation as a possible selection principle only after the
cohomology class and coefficient map are certified.  Report inconsistent or
empty solution sets just as prominently as successful spectra.

## Clock and boundary challenge

Repeat the first-obstruction analysis with a conformally coupled scalar used as
a relational clock.  Separate gauge fixing from anomaly cancellation.  Test
whether the clock measure or the choice of relational time produces a \(D\)
Ward defect even when the unclocked local theory is anomaly-free.

At dS/AdS and asymptotically flat boundaries, include boundary observables and
charges in the quantum algebra.  If \(D\) is classically charged there, do not
seek a contracting homotopy that would erase its charged action; instead test
the quantum representation and possible central extension of the physical
symmetry.

## Generalization programme

Begin this rail after the current paper-improvement investigation and its
immediate certificate repairs are frozen.

Use this promotion ladder for quantum claims:

```text
G0  truncated candidate or coefficient fixture
G1  complete local quotient in one antifield sector
G2  complete local BRST/BV anomaly cohomology
G3  locally covariant result over a background class
G4  restored QME and quantum Cartan theorem
G5  Lorentzian causal and boundary-certified quantum theory
```

The even AFN0 dimension-four quotient is `G1`: structural, but not a complete
anomaly or (D)-anomaly theorem.

### Work package Q-G1: complete the local anomaly complex

Extend beyond even AFN0 to antifield/Koszul--Tate sectors, odd parity,
pure-Diff and mixed rows, generalized connections, and all required
lower-form carriers.  Quotient exact tensor graphs by Bianchi, Grassmann,
integration-by-parts, and four-dimensional identities.  Construct the map
from local anomaly densities to admissible degree-zero Cartan defects.

Keep relative forms, integrated local functionals, and residual-state
cohomology as distinct result kinds.  Return an explicit primitive or dual
witness for every surviving class.

### Work package Q-G2: coefficient universality

Compute coefficients in a locally covariant renormalization framework and
compare the cylinder, a conformally flat globally hyperbolic background, one
conformally Einstein background, and the Berger clock where applicable.
Separate universal local coefficients from spectral normalization, zero
modes, boundaries, and measure terms.  Agreement of selected Euclidean
determinants does not by itself prove local covariance.

Compute the pure-Weyl \(a,c\) coefficients by two genuinely independent
presentations: the generated BV/descent calculation and a heat-kernel,
determinant, or index calculation with matched zero-mode and measure ledgers.
Reproduce one standard literature coefficient before interpreting a
disagreement. The acceptance target is presentation-independent coefficients
and an exact account of every normalization or scheme transformation, not
numerical agreement on a single background.

### Work package Q-G3: isolate the actual (D)-anomaly

Construct the explicit coefficient-bearing map to

\[
\mathcal A_D=[Q_\hbar,\iota_{D,\hbar}]-\mathcal L_D.
\]

Separate local Weyl anomaly, residual-generator anomaly, clock/measure
effects, boundary extensions, and cases where (D) is classically charged.
Do not infer the (D)-verdict directly from nonzero coefficients of
`omega C2` or `omega E4`.

### Work package Q-G4: background and matter stability

After QME restoration, prove or disprove uniformity of the corrected Cartan
identity over an open class of backgrounds and matter spectra.  If a
Riegert/Wess--Zumino or matter completion cancels the obstruction, compare
the original and extended BV cohomologies and verify that no new negative
physical direction is introduced.

### External bridge Q-X: convert the certificates into literature consequences

Prioritize Fradkin--Tseytlin coefficient calculations, Riegert/Mottola
Wess--Zumino anomaly actions, and Mannheim's antilinear quantum framework.
For each bridge:

1. reproduce one standard coefficient or Wess--Zumino identity in matched
   conventions;
2. identify its exact class in the generated BV quotient;
3. state whether it contributes to the QME defect, the (D)-Cartan defect,
   both, or neither;
4. explain the consequence in the adjacent language of anomaly
   cancellation, compensator trivialization, or positive metric.

The desired output is a result adjacent researchers can use: for example,
which matter spectra cancel the coefficient-bearing classes, whether the WZ
field trivializes the actual obstruction, or whether an antilinear metric is
BRST-compatible.  Do not demand adoption of the residual quotient as a
premise, and do not overstate what the source paper originally proved.

Defer the three-way Mannheim/PT, Fock-BRST, and causal-BV comparison until the
QME and Lorentzian asymptotic-state gates are closed. Its eventual common
benchmark must compare the phase space, residual quotient, state definition,
Jordan/log modes, inner products, BRST descent, and first physical vertex.
Use the adjacent-work portfolio in
[`universe-building-roadmap.md`](universe-building-roadmap.md) for sequencing and
[`adjacency-bridge-note-template.md`](adjacency-bridge-note-template.md) for
the outward-facing note.

## Common background matrix

Complete every cell established by your work; write `OPEN`, `NOT TESTED`, or
`NOT APPLICABLE` rather than extrapolating.

| Setting | \(D\) charge | Cartan contraction | Causal homotopy | One-particle sector | Pairing | Einstein sector |
|---|---|---|---|---|---|---|
| Vacuum cylinder | classical target; quantum status to compute | classical target; compute defect | proved only classically | zero classically in stated complex; quantum open | \(I_2\) classically; \(G(\hbar)\) open | proper classical solution sector |
| Cylinder + scalar clock | open | primary quantum test | open | open | open | open |
| Cylinder + Yang--Mills | open | open after scalar | open | open | open | open |
| Weakly deformed background | open | open | open | open | open | open |
| Lorentzian dS/AdS | boundary-dependent | open | open | open | open | selected-sector question open |
| Asymptotically flat | physical charge expected | contraction likely inappropriate for charged \(D\) | open | expected nonzero; compute | open | decisive |

## Priority and stop/go decisions

1. Classify the first possible \(\mathcal A_D^{(1)}\) before computing its
   coefficient.
2. Compute the pure-Weyl coefficient and its counterterm dependence.
3. Establish the local QME status without conflating anomaly types.
4. Add the conformal scalar clock and recompute the obstruction.
5. Transfer \(Q_1\) and \(G_1\) only if the QME gate passes.
6. Add Yang--Mills and broader matter spectra only after the scalar rail is
   understood.

Keep the quantum construction representation-neutral until the physical
pairing is computed: a Hilbert, Krein, BRST, or Fock completion is an outcome
to certify, not an input to assume.  Particle and graviton claims remain
inactive until the local QME/Ward gate, a Lorentzian causal state framework,
physical cohomology, and its pairing all pass.  Cosmological or dark-sector
quantum work begins only after a stable classical clocked cosmology exists.
The complete activation sequence is in
[`universe-building-roadmap.md`](universe-building-roadmap.md).

Escalate immediately on a nontrivial \(D\)-anomaly, a conflict between Ward
identities, or a negative/non-Hermitian pairing correction.  A certified
obstruction is a successful result.

## Required handoff

Deliver one human-readable report and machine-readable certificates containing:

- the `G0`--`G5` generality level and exact evidence for every promotion;
- the adjacent-work convention dictionary, reproduced coefficient/identity,
  and consequence for that framework's anomaly or inner-product question;
- the renormalized observable algebra and analytic framework;
- the cohomology group containing \(\mathcal A_D\), generated candidates, and
  trivialization witnesses;
- coefficients, regulators, counterterms, scheme transformations, and Ward
  consistency checks;
- separate local, residual, boundary, zero-mode, and measure ledgers;
- QME lifecycle state and fail-closed residual-transfer flag;
- quantum cohomology representatives and \(G(\hbar)\), if legally reached;
- the strongest attempted counterexample in every setting;
- hashes, provenance, exact commands, elapsed times, and test tiers;
- one verdict per setting: `CARTAN_QUANTUM_EXACT`, `CARTAN_RESTORED`,
  `CARTAN_ANOMALOUS`, or `ANALYTIC_FRAMEWORK_MISSING`.

Every result must carry at least one exact dependency tag:
`LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`, `REDUCED-MODE`, or
`LORENTZIAN-CAUSAL`.  The first three do not establish a Lorentzian QME or
causal quantum theory.

## Cross-team contribution contract

Submit new results through
[`d_quotient_programme/`](../d_quotient_programme/README.md).  Every quantum
row must import the exact classical generator and phase-space certificate by
content hash and retain `ANALYTIC_FRAMEWORK_MISSING` until the renormalized
observable algebra and applicable QME/Ward gates are actually constructed.
