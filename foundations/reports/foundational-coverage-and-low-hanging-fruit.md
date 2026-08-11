# Foundational coverage and low-hanging fruit

## Result

`FOUNDATIONAL_COVERAGE_MATRIX_V0` populates the six-axis assumption atlas
with sixteen representative attempts and ranks nine bounded research
opportunities.  Its status is `LITERATURE_SCOPED` and its only dependency tag
is `LOCAL-ALGEBRAIC`.

The short answer is yes: there is a real gap, but the tractable version is
more precise than “physics without the axiom of Choice.”  Existing programmes
tend to reverse only one side of

```text
L + S + M + Enc(P) |- O.
```

Reverse mathematics varies `S` and the target theorem while holding physical
postulates fixed or absent.  Reverse physics varies `P` while leaving `L` and
`S` implicit.  Constructive and topos approaches vary `L` and representation.
Operational reconstructions vary `P` and derive parts of `M`.  Finite quantum
models vary the infinity/carrier axes.  Krein architectures vary the pairing
and adjoint but normally retain a positive Hilbert topology.  None of the
representative attempts is direct on all six axes.

This is a corpus observation, not a priority or novelty theorem.  The sources
are representative rather than exhaustive, and the matrix explicitly fails
closed on literature completeness.

## Coverage matrix

The symbols mean `D` direct, `P` partial, `A` adjacent, `-` absent, and `?`
unknown.  A `D` says what a representative source deliberately changes or
classifies; it does not say that the programme is complete on that axis.

| Attempt | Logic | Set/existence | Infinity | Carrier | Physical postulates | Target claims | Main uncovered bridge |
|---|:---:|:---:|:---:|:---:|:---:|:---:|---|
| Reverse physics | - | - | A | P | D | D | proof logic and set-existence strength |
| Second-order reverse mathematics | P | D | P | P | - | D | relativistic gauge/QFT encodings |
| Reverse separable functional analysis | A | D | P | D | - | D | concrete physics uses of separation |
| Computable functional analysis | P | D | P | D | - | D | uniform content of physics witnesses |
| Hilbert spaces in ZF | A | D | D | D | - | D | explicit physical Hilbert spaces |
| Separable C*-algebras in ZF | A | D | D | D | P | D | state/GNS/dynamics chain |
| Bishop-style constructive QM | D | P | P | D | P | D | dynamics, gauge theory, and QFT |
| Constructive/localic Gelfand duality | D | P | P | D | A | D | noncommutative local field algebras |
| Topos algebraic quantum theory | D | P | A | D | P | D | BV, anomalies, and renormalization |
| Synthetic differential geometry GR | D | D | P | D | P | D | quantum/BV Weyl theory |
| Operational reconstruction | - | ? | D | D | D | D | proof-theoretic strength of derivation |
| Finite-field quantum phase space | - | - | D | D | P | D | continuum and dynamical bridge |
| Krein/ghost-parity quantum theory | - | ? | P | D | D | D | choice cost of `J`, completion, trace |
| Repository exact BV certificates | ? | A | D | D | P | D | named weak base and checker theorem |
| Repository Lorentzian Green programme | ? | ? | D | D | D | D | PDE proof strength and construction |
| Solovay measurability model | A | D | D | A | - | D | arbitrary sets versus observables |

The detailed cells, notes, sources, and boundaries are in
[`FOUNDATIONAL_COVERAGE_MATRIX_V0.json`](../results/FOUNDATIONAL_COVERAGE_MATRIX_V0.json).

## What is genuinely weakest

Four intersections stand out.

First, reverse physics and reverse mathematics have complementary blind
spots.  The former asks which physical assumptions imply a law; the latter
asks which set-existence axioms prove a mathematical theorem.  The reviewed
literature does not yet join them over one formal base with an explicit
encoding `Enc(P)`.

Second, the logical strength of operational reconstruction is largely
unlabeled.  Hardy and Chiribella--D'Ariano--Perinotti make Hilbert structure a
conclusion rather than a primitive, which is exactly the right direction.
But continuity, compactness, real-number completeness, and separation in the
derivation have not been calibrated here.  A physical-looking postulate and a
mathematical compactness lemma must not be silently identified.

Third, constructive quantum work reaches selected Hilbert, projection,
Gleason, Gelfand, and topos-algebraic results, and synthetic differential
geometry reaches classical Einstein equations.  The conspicuous missing
middle is gauge field theory: BV complexes, Green operators, local
counterterms, anomalies, time-ordered products, and QME restoration.

Fourth, Krein work changes carrier geometry but rarely asks the weak-choice
question.  That intersection is especially attractive here because the
repository does not merely assert that a fundamental decomposition exists:
its energy-mode completion displays

```text
J = +1 on E,   J = -1 on A and L
```

block by block.  This gives us an explicit object to audit rather than an
abstract existence theorem.

## Why the local repository is unusually ready

A scoped text census at base commit
`8eb1012623d21a9958955f872bda0105b42dc16d` found:

| Topic | Files |
|---|---:|
| Krein or fundamental symmetry | 689 |
| Green operator or Green function | 296 |
| compactness or separability | 52 |
| spectral theorem or functional calculus | 45 |
| Hahn--Banach, Zorn, or axiom of Choice | 1 |

The command was

```bash
rg -l -i --glob '!foundations/**' --glob '!**/__pycache__/**' PATTERN . | wc -l
```

This is navigation evidence only.  It does not prove 688 hidden uses of
Choice.  It shows that carrier and analytic machinery is pervasive while its
foundational dependencies are almost nowhere named.

## Ranked opportunities

The numeric score is only a reproducible triage rule:

```text
leverage + repository readiness + boundedness + underexposure - dependency cost.
```

Each input is an ordinal judgment from one to five.  It is not evidence and
does not measure physical importance.

| Rank | Package | Score | First relation to test |
|---:|---|---:|---|
| 1 | weak-base audit of one finite exact BV certificate | 19 | `SUFFICIENT_OVER_BASE` |
| 2 | explicit Krein `J` choice audit | 18 | `AVOIDED_BY_REFORMULATION` |
| 3 | Hahn--Banach versus explicit witness | 17 | `AVOIDED_BY_REFORMULATION` |
| 4 | separable C*-algebra to physical-state chain | 14 | `UNKNOWN` |
| 5 | fragment the spectral theorem actually used | 14 | `USED_BY_DISPLAYED_PROOF` |
| 6 | operational reconstruction proof strength | 11 | `USED_BY_DISPLAYED_PROOF` |
| 7 | one Green-operator existence theorem | 11 | `USED_BY_DISPLAYED_PROOF` |
| 8 | finite-field versus finite-mode comparison | 9 | `UNKNOWN` |
| 9 | topos-internal Weyl BV | 7 | `UNKNOWN` |

### 1. Finite exact BV weak baseline

Start with one small certified nilpotency/contraction/cohomology calculation.
Emit its proof-dependency DAG down to finite integer or rational equality,
bounded search, Gaussian elimination, and the induction needed to check the
loops.  Then give it a deliberately small independent checker.

This is the cleanest first result because it can establish an upper bound:
a named weak base is sufficient to verify the displayed certificate.  It
cannot establish necessity without a reversal.  “Written in Python with
SymPy” is not a foundational classification; the checker and encoding are
the classified objects.

### 2. Explicit Krein `J`

Split the existing energy-mode theorem into six dependency nodes:

1. explicit finite family labels `E/A/L`;
2. finite block dimensions and signs;
3. finite truncation `J_N^2=1` and positivity of `(x,J_N y)`;
4. countable `ell^2` direct sum and density of finite support;
5. infinite-index conclusion and Sobolev completion;
6. bosonic second quantization `Gamma_s(J)`.

The finite layers appear to avoid an existential choice of a maximal positive
subspace because `J_N` is given by a formula.  The point of the audit is to
prove that avoidance at the exact layer and then stop at the first completion
principle not yet justified.  It must not jump from explicit `J_N` to “all
Krein theory is choice-free,” and it says nothing by itself about the Born
trace or physical state selection.

### 3. Hahn--Banach versus a retained dual witness

Brown--Simpson and Humphreys--Simpson provide useful controls: separable
Hahn--Banach and open-convex separation have `WKL_0` calibrations, while a
different closed-set representation reaches `ACA_0`; other weak-star closure
claims can be much stronger.  That variation is exactly why the physics proof
must be inspected rather than labeled by vocabulary.

Choose one finite no-go or cohomology calculation where the repository emits
a left-null, dual, or trivialization witness.  Verify the conclusion directly
from that rational witness.  If successful, the relation is
`AVOIDED_BY_REFORMULATION`: the concrete certificate does not need the general
separable separation theorem.  Merely failing to import Hahn--Banach is not
an avoidance proof.

## Second wave

The next useful bridge is one separable C*-algebra state chain:

```text
algebra construction
    -> positive functional exists
    -> GNS representation exists
    -> physical state selected
    -> dynamics/local normality established.
```

Recent ZF results make the first layers approachable, but algebraic functional
calculus must not be promoted to a physical state theorem.

The spectral audit can proceed in parallel conceptually, but it should classify
the exact theorem form: finite diagonalization, polynomial spectral mapping,
bounded continuous functional calculus, compact self-adjoint decomposition,
or a projection-valued spectral measure.  These are not one indivisible
“spectral theorem.”

Green operators are more important and less cheap.  The repository has 296
files touching them and a precise open analytic gate, but a full foundational
reversal would sit on top of continuum PDE existence that is itself unfinished
for the auxiliary BV blocks.  The sensible control is first to audit an
already-complete normally hyperbolic scalar or finite-rank bundle theorem.  No
finite symbol or reduced-mode result may support a `LORENTZIAN-CAUSAL` claim.

## Known-attempt source additions

The supplement adds primary representatives for:

- separable Hahn--Banach and convex separation in reverse mathematics;
- strong weak-star closure principles in separable Banach theory;
- computable Hahn--Banach;
- Bishop-style quantum foundations and constructive Gleason;
- intuitionistic synthetic differential geometry for classical GR;
- finite-field discrete quantum phase space;
- constructive non-unital Gelfand duality; and
- the algebra-first Haag--Kastler move.

Seven sources are content-pinned.  Brown--Simpson, Richman--Bridges, and
Haag--Kastler are still metadata-only and block a corpus freeze.  The source
ledger also guards a terminology trap: established “constructive QFT” often
means rigorous model construction, not intuitionistic or choice-free QFT.

See
[`FOUNDATIONAL_LITERATURE_SUPPLEMENT_KNOWN_ATTEMPTS_V1`](../literature-supplement-known-attempts-v1.json)
for the source-specific claims and boundaries.

## Recommended sequence

The first small programme should contain both a positive result and a negative
control:

1. show that a selected finite exact certificate is verifiable over a named
   weak base;
2. show that its retained rational witness avoids a general separation theorem;
3. apply the same decomposition to the finite layers of the explicit Krein
   fundamental symmetry;
4. only then cross the countable-completion boundary.

That sequence will tell us whether the proposed combined programme produces
nontrivial distinctions before we invest in spectral measures, state
selection, Green operators, or a topos-internal BV reconstruction.

## Claim boundary

This report establishes a reproducible literature map and work triage.  It
does **not** establish survey completeness, novelty, a formal reverse-
mathematics theorem, a constructive Weyl certificate, a choice-free Krein
completion, finite fundamental physics, or any `LORENTZIAN-CAUSAL` result.
