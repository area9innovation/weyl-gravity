# Closed-\(S^3\) relative-phase clock quotient atlas

## Result

`CLOSED_S3_RELATIVE_PHASE_CLOCK_ATLAS_V1` turns the general compact-Gauss
structure theorem into a complete exact atlas for two and three homogeneous
phase fields.  It remains within the `LOCAL-ALGEBRAIC` dependency boundary.

For an integer charge matrix

\[
Q\in {\rm Mat}_{n\times r}(\mathbb Z),\qquad k={\rm rank}_{\mathbb Q}Q,
\]

the producer computes a Smith decomposition

\[
UQV=D=\operatorname{diag}(d_1,\ldots,d_k,0),
\qquad U\in GL(n,\mathbb Z),\quad V\in GL(r,\mathbb Z).
\]

Let \(E_{\rm g}\) and \(E_{\rm rel}\) select the first \(k\) and last
\(n-k\) canonical coordinates.  The exact basis-change witnesses are

\[
J=U^{-1}E_{\rm g},\qquad
B=U^{-1}E_{\rm rel},\qquad
N=U^TE_{\rm rel}.
\]

Here:

- \(J\) is a primitive cocharacter basis for the connected gauge image;
- \(B\) is a primitive tangent basis for the quotient torus;
- \(N\) is the dual relative-character basis;
- \(Q V=J\,{\rm diag}(d_i)\), followed by zero redundant columns;
- \(N^TJ=0\) and \(N^TB=1\).

The compact gauge orbit has dimension \(k\).  Its stabilizer has identity
component \(T^{r-k}\) and component group

\[
\bigoplus_{d_i>1}\mathbb Z/d_i.
\]

The product of the nonunit Smith factors is the index of the raw charge
lattice in its primitive saturation.  It changes finite isotropy, not the
dimension or multiplicity of the physical relative torus.

## Zero-charge fibre and clock criterion

On closed source-free \(S^3\), the exact Gauss fibre is

\[
Q^Tp=0.
\]

The atlas proves and checks case by case that

\[
Q^Tp=0
\quad\Longleftrightarrow\quad
p=N\Pi .
\]

Consequently,

\[
\boxed{
\text{a nonzero physical relative momentum at zero total compact charge exists}
\iff n-k>0\ \text{and}\ \Pi\ne0 .
}
\]

This is not the assertion that zero total charge is itself a gauge quotient.
The charge fibre, connected gauge orbit and quotient lattice are stored as
three separate objects.

The exact component-support criteria from the predecessor remain in force:

\[
\exists p\in\ker Q^T,\ p_i\ne0\ \forall i\in S
\iff e_i\notin{\rm im}_{\mathbb R}Q\ \forall i\in S,
\]

and

\[
\exists v\in\ker(Q^TM),\ v_i\ne0\ \forall i\in S
\iff e_i\notin{\rm im}_{\mathbb R}(MQ)\ \forall i\in S.
\]

## Reduced kinetic form and exact sign

For symmetric nonsingular phase inertia \(M\),

\[
A=N^TM^{-1}N,\qquad
\dot\psi=A\Pi.
\]

On a regular relative stratum,

\[
\boxed{G_{\rm rel}=A^{-1}.}
\]

For \(M>0\), \(A\) and \(G_{\rm rel}\) are positive definite on every
nonzero relative stratum.  For a declared-indefinite \(M\), the result uses
the exact characteristic polynomial over \(\mathbb Q\) to count positive,
negative and zero eigenvalues of \(A\):

```text
POSITIVE
NEGATIVE
INDEFINITE_KREIN
DEGENERATE_DIRAC_REQUIRED
```

No sign is assigned before quotienting.  A singular \(A\) is not called a
regular reduced kinetic form; it is sent fail-closed to an additional Dirac
reduction.

The raw homogeneous phase moment map restricts to

\[
\frac{D_{\rm phase}}{{\rm Vol}(S^3)}
=p^TM^{-1}p
=\Pi^TA\Pi.
\]

For a uniform helical motion the phase contribution to
\(K_{\rm Berger}=D-R_w\) vanishes only when
\(w=\dot\psi\) belongs to the continuous stabilizer of the potential.  Since
this item does not select a potential, the unmatched \(K_{\rm Berger}\)
status remains `NO_MODEL_SPECIFIC_POTENTIAL_SELECTED`.

## Complete two- and three-field strata

The machine-readable census has twelve parametric strata:

| fields | rank | Smith locus | relative dimension | positive-\(M\) sign |
|---:|---:|---|---:|---|
| 2 | 0 | no nonzero factors | 2 | positive |
| 2 | 1 | all factors unit | 1 | positive |
| 2 | 1 | at least one nonunit factor | 1 | positive |
| 2 | 2 | all factors unit | 0 | not applicable |
| 2 | 2 | at least one nonunit factor | 0 | not applicable |
| 3 | 0 | no nonzero factors | 3 | positive |
| 3 | 1 | all factors unit | 2 | positive |
| 3 | 1 | at least one nonunit factor | 2 | positive |
| 3 | 2 | all factors unit | 1 | positive |
| 3 | 2 | at least one nonunit factor | 1 | positive |
| 3 | 3 | all factors unit | 0 | not applicable |
| 3 | 3 | at least one nonunit factor | 0 | not applicable |

The continuous stabilizer dimension is always \(r-k\).  The tables are
parametric in the divisibility locus
\(0<d_1\mid\cdots\mid d_k\), rather than a finite sampling of integer
matrices.

Nineteen exact rational fixtures independently exercise:

- every rank for \(n=2,3\);
- primitive and nonprimitive stabilizers;
- a two-field equal-charge counterflow;
- a charged-plus-neutral direction;
- the first nontrivial three-field/two-gauge quotient
  \(Q=((1,0),(0,1),(1,1))^T\), with
  \(N=(-1,-1,1)^T\);
- positive, negative, indefinite and singular relative kinetic signs.

For the three-field/two-gauge witness with
\(M=\operatorname{diag}(2,3,5)\),

\[
A=\frac{31}{30},
\qquad
G_{\rm rel}=\frac{30}{31}.
\]

## Residual atlas boundary

The generated residual fragment contains one row per stratum.  It marks the
finite charge/symplectic quotient `CERTIFIED`, while causal, quantum and
physical carrier identification are `NO_CERTIFIED_MAP`.

These rows are structural quotient carriers, not:

- pure-Weyl residual modes;
- one-particle states;
- the centered deformation classes \([W_+^2]\), \([W_-^2]\);
- cross-background mode identifications;
- a repaired scale compensator.

No entry acquires a frequency or causal dispersion by matching a name.

## Conflux disposition

The oracle-free raw export contains only:

```text
case_id
field_count
gauge_generator_count
input_class
Q
M
relative_momentum_coordinates_Pi
```

It deliberately excludes ranks, Smith factors, stabilizers, quotient
dimensions, reduced metrics, signs, moment-map verdicts and claim fields.
The payload is therefore suitable for an independent exact importer.

The generic exact symplectic/moment-map request M39 is `ACCEPTED` but not
`LANDED`.  The resident Conflux policy also has no declaration for this
consumer.  A narrowly scoped consumer request was filed at
`planning/forge-requests/closed-s3-relative-phase-clock-atlas-conflux-consumer.json`.

Therefore the current lifecycle status is:

```text
NO_CERTIFIED_CONFLUX_IMPORTER
```

The raw payload is not called a Conflux identification.  The Science Forge
work item must remain blocked until a consumer-specific typed importer,
policy gate and independent rediscovery receipt land.

## Claim boundary

This result certifies an exact finite-dimensional classical quotient atlas
for two and three homogeneous phase fields on closed source-free \(S^3\).
It establishes the charge homomorphism, primitive lattices, compact
stabilizers, zero-charge fibres, quotient kinetic signs and phase-sector raw
moment-map restrictions.

It does **not** establish:

- a selected model-specific pure-Weyl action;
- a repair of the failed scale-gauge compensator;
- an arbitrary-\(n\) atlas beyond the imported structural formulas;
- a nonhomogeneous PDE or causal parent;
- a full BV complex;
- a physical residual-mode crosswalk;
- a Hadamard state, QME, particle, scattering, unitarity or quantum theorem;
- a certified Conflux map.

## EVIDENCE

- Result:
  `d_quotient_classical/compensator/CLOSED_S3_RELATIVE_PHASE_CLOCK_ATLAS_V1.json`
- Oracle-free raw export:
  `d_quotient_classical/compensator/CLOSED_S3_RELATIVE_PHASE_CLOCK_CONFLUX_EXPORT_V1.json`
- Producer:
  `d_quotient_classical/compensator/closed_s3_relative_phase_clock_atlas.py`
- Independent replay:
  `d_quotient_classical/compensator/verify_closed_s3_relative_phase_clock_atlas.py`
- Current-source Forge rail:
  `d_quotient_classical/compensator/closed_s3_relative_phase_clock_atlas_check.forge`
- Mutation suite:
  `d_quotient_classical/compensator/tests/test_closed_s3_relative_phase_clock_atlas.py`
- Strict schemas:
  `d_quotient_classical/schema/closed-s3-relative-phase-clock-atlas-v1.schema.json`
  and
  `d_quotient_classical/schema/closed-s3-relative-phase-clock-conflux-export-v1.schema.json`
- Residual fragment:
  `residual_atlas/closed-s3-relative-phase-clock-fragment-v1.json`
- Consumer request:
  `planning/forge-requests/closed-s3-relative-phase-clock-atlas-conflux-consumer.json`

## CLOSE-OUT

The exact physics atlas is complete for the declared two- and three-field
class.  Its Conflux stop condition is not complete: M39 and the
consumer-specific importer/policy/gate remain external prerequisites.  Close
the scientific package as a certified local-algebraic result, but block the
Science Forge work item on `NO_CERTIFIED_CONFLUX_IMPORTER`; do not activate
the causal-parent successor from the raw export alone.
