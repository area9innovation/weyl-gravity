# Symplectic Reconstruction of the Pais–Uhlenbeck PT Metric

Verification project and paper series on the PT-symmetric Pais–Uhlenbeck
oscillator, the fourth-order scalar field, and quadratic gravity. Started
from the audit spec in `../Symplectic Reconstruction.md`; grew into eight
papers (an expository introduction, five technical papers on the free
theories, and two interaction papers), a Lean formalization, and a
machine-checked verification pipeline.

## Overview

The series does not propose a new free-theory cure for the
higher-derivative ghost. It classifies and canonically reconstructs the
known Bender--Mannheim positive quantization, relates it to the
Bateman--Turok Krein construction through a common **free complex spectral
covariance**, and separates the additional choices of real form,
involution, observable algebra, and completion. The free positive metric
is geometrically canonical, but that kinematic optimality does not imply
interacting stability: Paper 5 finds on-shell conversion obstructions to
its analytic deformation. At the split rational shell the same on-shell
matrix is exactly Krein-pseudo-Hermitian; the stronger one-sided
charge-null mechanism emerges only at the massless perfect-square
boundary. Paper 4 adds gauge reduction and Lorentz covariance and
classifies two free Einstein--Weyl real forms. Paper 6 then tests those
forms against the complete tree-level cubic and quartic vertex content:
cubic order is protected, while the physical `MM -> Mh` channel gives a
nonzero second-order deformation cocycle. The canonical
particle-number-diagonal Krein lift does not make that block null.

## The papers (`paper/`)

| # | File | Title | Status |
|---|------|-------|--------|
| 0 | `ghosts-geometry-reality.tex` / `.pdf` | **Ghosts, Geometry, and Reality in Fourth-Order Quantum Theories** (expository introduction to the series, incl. the interaction results) | draft (28 pp.) |
| 1 | `symplectic-diagonalization.tex` / `.pdf` | **Canonical Positive Symplectic Diagonalization of the Pais–Uhlenbeck Oscillator** | frozen, tag `paper1-v1.2` (17 pp.) |
| 2 | `variational-fock.tex` / `.pdf` | **The Pais–Uhlenbeck Metric as a Minimum-Distortion Principle, and the Representation Problem for the Fourth-Order Field** | frozen, tag `paper2-v1.3` (14 pp.) |
| 3 | `fourth-order-vacuum.tex` / `.pdf` | **The Universal Vacuum of the Fourth-Order Scalar Field: Metric Orbits, Fock Sectors, and the Krein Boundary** | frozen, tag `paper3-v1.3` (13 pp.) |
| 4 | `fourth-order-gravity.tex` / `.pdf` | **Gauge Reduction and the Completion Problem in Fourth-Order Gravity: PU Pairing, Covariant Real Forms, and the Conformal Jordan Boundary** | frozen, tag `paper4-v1.1` (15 pp.) |
| 5 | `interaction-obstructions.tex` / `.pdf` | **Interaction Obstructions, Resonant PT Breaking, and Doubled Jordan Symmetry in Fourth-Order Theories** | frozen, tag `paper5-v1.1` (17 pp.; accepted by team referee, then extended: 5:1 confirmation, Krein separation, literature repositioning, charge-null lemma + regulated-embedding proposition) |
| 6 | `einstein-weyl-interaction-obstructions.tex` / `.pdf` | **Interaction Obstructions in Einstein–Weyl Gravity: Cubic Protection, Second-Order Metric Failure, and Krein Visibility** | draft, major-review revision (30 pp.) |
| 7 | `conformal-residual-cohomology.tex` / `.pdf` | **Residual $SO(4,2)$ Cohomology of Free Weyl Gravity on the Conformal Cylinder** | draft; covariant causal BV bridge, residual $H^4\cong\mathbb C^2$, and $I_2$ pairing certified |

Also: `theorem_statements.tex` — paper-1 theorem list with verification
cross-references.

Publication and reproduction instructions for Paper 7 are collected in
[`notes/conformal-publication-reproduction.md`](notes/conformal-publication-reproduction.md),
including the fast required rail, exhaustive scheduled rail, scoped legacy
flags, and publication artifact procedure.
The referee major-revision plan separating the residual theorem, causal
bridge, and computational supplement is
[`notes/conformal-paper-split-roadmap.md`](notes/conformal-paper-split-roadmap.md).
The itemized response, including what remains genuinely open before
submission, is
[`notes/conformal-referee-major-revision.md`](notes/conformal-referee-major-revision.md).

General-audience article:
[`Before Worrying About a Gravitational Ghost, Ask Whether It Is Really There`](paper/before-worrying-about-a-gravitational-ghost.md)
explains the completed classical pure-Weyl BV–BFV result without assuming
advanced mathematics or physics.

Video orientation:
[`Conformal ghosts, fourth-order gravity, and quantum completion`](paper/video-background-guide.md)
is a guided viewing and reading route through the main competing approaches
to the higher-derivative ghost problem and their relation to this programme.

Quantum programme:
[`quantum-weyl/README.md`](quantum-weyl/README.md) separates the classical
import gate, exact local BV/cohomology work, cylinder restriction, reduced
and Euclidean spectral checks, Lorentzian causal construction, and eventual
quantum residual transfer.  The bootstrap is deliberately fail-closed:
Gate A is not frozen, the local package currently certifies only the minimal
Diff `x` Weyl coordinate-jet rows plus a finite exact curvature/Bianchi/IBP
quotient, and the reduced `E/A/L` ledger computes no determinant or one-loop
coefficient.

Energy-mode analytic completion:
[`analytic_completion/README.md`](analytic_completion/README.md) documents
the infinite-index one-particle and bosonic Krein completions, closed
residual BRST operator, bounded Cartan contraction, and proof that completed
centered cohomology and its $I_2$ Gram matrix are unchanged.  It deliberately
does not claim a covariant metric-field Sobolev or Green-hyperbolic theorem.

Lorentzian cylinder field realization:
[`covariant_completion/README.md`](covariant_completion/README.md) proves the
tensor/vector curl identities, the local Green-hyperbolic factorization of
the reduced physical system, the exact field origin of the `E/A/L` towers,
and the field-induced branch Cauchy--Sobolev topology.  Its harmonic
transform is Krein-unitary onto the energy-mode one-particle completion.
The complete covariant BV Green theorem and distributional/Hadamard theory
are now separated more sharply.  A support-local ordinary-derivative
auxiliary BV realization has a certified four-row symbol witness and an
exact $66$-to-$30$ Fourier-complex deformation retract whose formulas are
support local.  The curved workstreams now additionally certify the exact
covariant action, gauge map and expanded action Hessian, including exhaustive
cancellation of all third- and fourth-order jets and exact formal
adjointness.  The nonlinear BV-canonical auxiliary shift gives the complete
local curved SDR, and the curved presymplectic comparison closes off shell up
to the certified improvement terms.  An exact null-symbol rank obstruction
rules out the original 24-field/9-gauge scalar-symbol witness for every
pointwise nondegenerate fibre pairing and every first-order companion: at a
null covector the Hessian and gauge symbols have ranks 11 and 9.  The
rank-two obstruction is the physical helicity-two module, not missing gauge
freedom.  The linearized Weyl symbol induces the exact isomorphism
`(1/4) I2` from the reduced Hessian quotient to the two-dimensional Weyl
helicity quotient.  The exact curved Bianchi--Bach decomposition now requires
the ten electric/magnetic Weyl components together with a sixteen-component
Cotton slot.  Its 34 covariant rows have temporal rank 26 and eight primary
constraints, and exhaustive comparison on all 150 Weyl two-jets proves the
curved equations and this local first-order closure.  Formal integrability
adds six secondary constraints.  The constraint-adjusted 26-state system is
exactly equivalent as a differential ideal, symmetric hyperbolic with causal
speeds, and has a complete sourced subsidiary identity.  The corrected
fibre-identified curved projections close the odd BV mapping cylinder.  Its
all-row prolongation retract, prolonged BV operator identity, and off-shell
prolonged/auxiliary current comparison are exact.  A local cyclic projector
contracts 356 of 386 prolonged components to the 30-component
metric--curvature graph.  Curved adjoint-tractor BGG/HPL transfer, followed by
the explicit trace/Weyl shear, gives retarded and advanced all-row homotopies
with `Q Lambda_± + Lambda_± Q = 1` and the graded adjoint relation.  The causal
quasi-isomorphism, recovery of the fifteen residual endpoints,
`SO(4,2)`-equivariant transfer, and causal/current pairing comparison are now
certified.  Distributional/Hadamard theory remains open.  A direct
same-bundle factorization of `B_lin+K T/2` is an optional strengthening, not a
hidden premise.

The retained metric endpoint is now coefficient-complete as the exact curved
complex `G_met[5] -> h[10] -> Ebar_met[10] -> I_met[5]`, with differential
orders `1/4/1`, nilpotency, formal adjoints, odd cyclicity, and the local graph
intertwiners checked coefficientwise.  Its canonical upper curvature lift is
exact.  The canonical middle Weyl--Cotton lift is obstructed at rank five,
while the corresponding full relative cyclic saddle exists but has exactly
zero endpoint Schur correction.  Therefore the canonical metric endpoint
diagonal witness `W_0` still has no certified same-sided inverse.  The proved
direct tractor causal route does not require or assert that stronger
implementation.

The generated
[`final_claim_dependencies.md`](covariant_completion/generated/final_claim_dependencies.md)
records the current fail-closed result:

```text
curved_operator_identity       = true
curved_deformation_retract     = true
curved_current_comparison      = true
final_covariant_H4             = true
```

There are zero atomic blockers.  The transported theorem is
`H^4_cov=span{[W_+^2],[W_-^2]}` with Gram matrix `I_2`.  The negative rank
certificate and the positive reduced Weyl-symbol isomorphism remain exposed
independently.

The selected curvature route is split into explicit fail-closed flags:

```text
curved_EB_equations                = true
curved_EB_first_order_closure      = true
curved_EB_symmetric_hyperbolicity = true
curved_sourced_constraint_identity= true
curved_constraint_propagation     = true
EAL_curvature_spectrum_match       = true
support_local_prolongation_retract= true
prolonged_BV_operator_identity     = true
prolonged_green_witness            = false
curvature_causal_green_operators  = false
direct_tractor_causal_homotopy     = true
causal_green_homotopy              = true
causal_quasi_isomorphism           = true
residual_endpoint_recovery         = true
SO42_equivariant_transport         = true
prolonged_current_comparison       = true
direct_causal_pairing_transport    = true
pairing_compatibility              = true
```

The two false flags are scoped legacy implementation flags: the direct
tractor route proves the required causal homotopy without claiming a
canonical endpoint inverse or monolithic prolonged witness.  The `SO(4,2)`
item is an exact recognition/transport theorem rather than an independent
coefficient calculation.  For the cutoff inverse
`kappa=[Q,chi]` and every local conformal chain generator `rho`, the explicit
homotopy is `[kappa,rho]=[Q,[chi,rho]]`; its support is compact on the
cylinder.  The causal quasi-isomorphism and residual endpoint recovery now
supply its certified premises.

The exact all-level curvature audit is also complete: symbolic BGG rank and
character identities show that the 26-state covariant equations carry
precisely the parity-complete `E/A/L` towers and that the Cotton graph adds no
second copy.  This is not inferred from a finite harmonic cutoff.

The human-readable [covariant H4 proof ledger](covariant_completion/generated/covariant_H4_proof_ledger.md)
maps all 23 terminal requirements to authoritative hashes, reproduction
commands, scoped caveats, and an independent-review checklist.  Check it with
`python3 symbolic/verify_conformal_covariant_H4_proof_ledger.py --check --guards`.

The BV-canonical Weyl/Cotton graph SDR, autonomous curvature compatibility
complex `26 -> 40 -> 14` with cotangent adjoint, causal curvature-block
solution operators, and analytic block Green witness are exact subtheorems.
The state map `T=(C1,div C1)` and an order-two equation map satisfy
`E_curv T=A_eq E_aux` on the exhaustive 700-dimensional metric four-jet
fibre.  The apparent rank-four defect in the next square was a coordinate
error: that diagnostic inserted the flat-Fourier equation projection into
the curved fibre-identified cotangent row.  Reconstructing the actual curved
projections `p_E=(D^-1 S_h^sharp D,1,0)` and `p_I` gives
`A_eq=A_core p_E`, `B_id=B_core p_I` and
`N_curv A_eq=B_id C_aux` exactly.  The resulting sixteen-block cotangent
mapping cylinder is coefficientwise nilpotent and odd cyclic, enumerates
every field/equation/identity and dual row, and satisfies
`PI=1`, `IP-1=QH+HQ` by finite-order local maps.  Thus the all-row local
prolongation and BV operator flags are now true.  The prolonged current
certificate is rebound to the curved core-chain provenance and proves the
off-shell `d+Q` comparison exactly; the direct causal pairing certificate
now proves Green/current equality.  The support-local cyclic hybrid projector also contracts 356
prolonged components and retains the 30-component metric--curvature graph.
The exact curved endpoint is emitted coefficientwise in the ordered
`5 -> 10 -> 10 -> 5` metric rows, rather than inferred from the flat-Fourier
regression hashes; its graph maps and all three curved arrows intertwine
exactly.  Its canonical endpoint witness and same-sided inverses remain
unconstructed, but are not required by the direct tractor homotopy.  The construction
does not use the scalar-wave-obstructed auxiliary block $E_{\rm aux}+KC$ as
an endpoint witness; the next operator is
$L_{\rm end}=QW_{\rm end}+W_{\rm end}Q$ on the retained metric--curvature
graph.  The upper canonical curvature backward map lifts exactly by a
support-local rank-four algebraic map.  The middle canonical map does not:
`T_core=J_WC W_EB`, `pi_EB J_WC=1`, `pi_EB A_F=0`, and `rank(A_F)=5`
give an exact leading-page contradiction to `T_core S=A_F`.  This scoped
graph-lift no-go does not extend to relative witnesses.  In fact the full
`386 -> 30` projectors admit the rank-five cyclic two-way relative incidence,
but its minimal Schur correction is identically zero:
`P_end L_AF P_alg L_AF P_end=0`.  It introduces no new obstruction and
cannot improve the endpoint diagonal.  Two further fail-closed diagnostics
sharpen this optional canonical-witness step.

### Historical alternative-witness diagnostics

The following factorization, saddle and first-order searches remain useful
scoped no-go/design receipts.  Their open or false flags refer to those
stronger implementations, not to the certified direct tractor causal route
or the final covariant theorem.

At an arbitrary covector the auxiliary prenormal principal symbol
satisfies `(P2-q I)^2=0`, with Smith multiplicities `6/12/6` for the
algebraic/wave/biwave factors.  The formal lower factor `2q I-P2` is exact at
principal level, but its naive frozen lower-order completion has nonzero
orders zero through two, so it is not yet a local Green factorization.  The
complete invariant correction spaces have `dim D0=38` and `dim D1=93`.
Exact simultaneous cubic divisibility of both `DP` and `PD` leaves a
45-parameter family, so there is no cubic obstruction.  Restoring the two
independent 93-parameter factor splittings and the five 38-parameter
algebraic terms gives 421 nonlinear unknowns after the cubic gate.  That
complete system is now assembled exactly as a sparse quadratic
symmetrized-PBW system: orders zero, one and two contain respectively
`240/960/2484` coefficient rows.  At order two the fixed 190-column
algebraic matrix has rank 100 and cokernel dimension 2384, leaving 90 free
algebraic variables.  Its exact Schur projection has 2,130 nonzero
polynomial constraints (365 up to scale) and no constant obstruction.  The
projected polynomial system and orders one and zero remain unsolved, so this
is an assembly and elimination theorem, not a factorization.  A backend
audit corrected a mixed time--space curvature sign: raised curvature indices
must use the spatial projector.  Focused `Box^2` and Weitzenbock coordinate-jet
tests now pass.  Exact triangular symmetrized-jet PBW inversion exhausts all
1,680 four-jet basis elements, passes 504 ordered-word round trips and
certifies associativity, so the quadratic-factor composition backend is
ready.  A naive transpose/reversal of the already sorted table has a 48-entry
defect because derivative-index slots were suppressed.  This is not a
primal-composition counterexample.  The pairing-aware adjoint backend is now
exact in the symmetrized-PBW representation.  With the action pairing,
`P^sharp=P`, a self-adjoint complement reduces the invariant first/zeroth
families from `93/38` to `44/24`, and the cubic gate has rank 116 on 137
variables, leaving 21 parameters.  Setting
`R_minus=L_plus^sharp`, `R_plus=L_minus^sharp` makes the right product the
adjoint of the left and reduces the remaining nonlinear problem to 214
parameters.  Its complete order-two system is now exact: 1,242 rows, a
`1242 x 100` algebraic matrix of rank 52, and 1,050 nonzero Schur-projected
constraints (179 up to scale), again with no constant obstruction.  The
179 normalized constraints are all genuinely quadratic: their 1,497
quadratic monomials have coefficient rank 124, and the 55-dimensional left
kernel produces no nonzero affine-linear consequence.  Thus no variable can
be removed by linear span reduction; nonlinear ideal solving and orders one
and zero remain open.

A first exact lower-order branch has now been exhausted: in all four
left/right orientations with one
factor equal to the literal rough `Box`, the 159-variable system has
`rank(A)=159` and `rank([A|b])=160`.  The common obstruction is the
symmetrized `nabla_(0)nabla_(1)` coefficient mapping `f_01` to `f_00`, whose
required value is `-8` while every correction column vanishes.  This rules
out only the bare-`Box` branch.  In the general branch the bilinear
`A_minus A_plus` term explicitly repairs this row and its complete
`SO(3)` orbit `f_0i -> f_00`; the support-minimal zero-sum assignment uses
two invariant directions.  That particular fixed split nevertheless fails
the complete simultaneous order-two system even after all 190 algebraic
variables are admitted: `rank(A)=100`, `rank([A|b])=101`, with a one-row
left-null witness on `nabla_(0)nabla_(1): h_22 -> f_01` and right-hand side
16.  This is a no-go only for that fixed minimal split, not for the general
421-variable family or its 214-parameter sharp subfamily.

For that sharp subfamily, the exact degree-one Macaulay screen has 136,585
monomial rows and 20,585 multiplier columns.  A denominator-safe
finite-field minor proves the degree-three rational-rank bounds
`12861 <= rank_Q <= 14136`.  The full rational ranks, constant-ideal question,
and low-degree elimination dimensions remain undecided; the screen promotes
no factorization or Green claim.

Among the nine
allowed odd-adjoint relative pairs, no single pair gives reciprocal
coupling; the smallest two-way saddle uses pairs 4 and 5.  Its exact core is
the coupled `(M_aux,X_U,Y_U_sharp)` block with off-diagonal maps `R,S` and
their odd adjoints.  Its formal Schur complement contains curvature Green
operators and is therefore nonlocal, while the unreduced saddle is order two
and still lacks the required local first-order reduction.  The natural local
instantiation `A_F=pF A_eq`, `S=A_F^sharp`, `R=A_F^sharp J_U` is now ruled out
exactly: its balanced Douglis temporal principal matrix has rank at most
`107/116`, hence defect at least nine, zero temporal leading coefficient and
no positive symmetrizer.  This no-go applies only to that smallest pair-4+5
ansatz, not to larger relative witnesses or an additional local first-order
prolongation.  The expanded-relative audit now exhausts all nine
odd-adjoint pairs and the 162-dimensional Hom family.  An independent exact
commutant calculation now constructs all three rotation generators on every
one of the sixteen blocks and recovers the nine Hom nullities
`4/18/4/36/14/14/22/36/14` coefficientwise.  It finds
three reciprocal two-pair candidates (`1+6`, `1+7`, `2+7`), but the maximum
central cross-ranks are only `21/24` on each of the two central blocks.  The
three missing directions are rotation scalars.  Consequently a witness that
demotes the entire central auxiliary diagonal has temporal rank defect at
least three; a viable expanded witness must retain or locally prolong those
scalar directions.  This is a scoped design theorem, not a Green no-go.
The displayed pair-`1+6` maps, the temporal `K` and `Ncurvsharp` coefficients,
their vector projector and the retained scalar diagonal all have zero
rotation-generator intertwining defect.
The scalar directions are now identified exactly as `h_00`, `f_00`, and
`v_0`; the corresponding rank-three restriction of `K C` has determinant
`-1`.  Explicit pair-`1+6` coefficient maps satisfy the local numerator
identity `K R1 Ncurv^sharp R6^sharp = -Pi_vector`, with the minus sign forced
by the first-order compact-support adjoint.  Inserting the actual
curvature temporal diagonal
`D(dt)=diag(I_26,-I_40,-I_26)` gives `D^-1=D` and the exact Schur term
`B D^-1 C=+Pi_vector`; the field Schur block is therefore
`Eaux_2+Dscalar-Pi_vector`.  With the retained scalar diagonal, the complete
`116 x 116` temporal Douglis matrix has rank 116 and determinant one.  This
closes only the timelike temporal-invertibility gate: `R6sharp` still lacks
its three spatial first-order coefficients, and the scalar diagonal still
lacks its cyclic all-row lift.  Thus the arbitrary-covector symbol,
characteristics, positive
symmetrizer and lower-order completion remain open.
**Historical checkpoint.** These are diagnostics, not theorem promotions: at
that intermediate stage the six causal/transport flags remained false on
this superseded route.  The direct tractor route described above subsequently
closed the causal theorem.

The complete equivariant `R6sharp` audit now finds 22 temporal and 46
spatial parameters.  With the certified temporal normalization fixed, the
intrinsic aligned polynomial Jordan chain survives all 46 spatial
directions (both exact sensitivity maps have rank zero).  Thus this specific
pair-`1+6`, cyclic `-2 Pi` family has no semisimple faithful strong
linearization or positive symmetrizer.  The result is deliberately scoped;
other incidences, temporal normalizations, larger witnesses, and generalized
Green realizations remain open.

The follow-up homological and triangular audits locate the rigid chain
precisely.  Its `f_23` vector belongs to the already contractible shifted
auxiliary pair, while `h_23` carries nonzero physical Weyl helicity two; the
extension splits after the certified support-local BV shift and vanishes as
an extension on cohomology.  On the aligned physical symbol it is the usual
triangular biwave block, which has an exact recursive causal inverse.  Thus
the Jordan block is not itself a Green no-go.  A local full-bundle split is
still missing: the refined unsplit support graph retains a reciprocal
rank-34 `(h,f,C#)` component.  Alternative incidences `1+7` and `2+7` pass
the first sensitivity screen (joint rank 16) and proceed to semisimplicity
testing.  Their smallest temporally regular slices have determinant `8` and
only real causal roots, but remain nonsemisimple at speeds `0,+1,-1`; one
directly sensitive spatial perturbation does not repair them.  This rejects
those slices only.  The canonical 16-parameter subfamily spanning the full
sensitivity image is also uniformly non-semisimple: pair `1+7` has zero-root
valuation at least `40` but kernel dimension at most `33`, while pair `2+7`
has valuation `48` and kernel dimension at most `47`.  This still does not
rule out the raw 122-parameter families or generalized Green extensions.

On the same aligned channel, the certified BV shift gives the exact complex
split `diag(L^2,-1)` with `L=1-z^2`, while the witness remains the closed
triangular block `[[L,0],[4,L]]`.  Its inverse
`[[G,0],[-4 G^2,G]]` is exact and uses no inverse curl, Laplacian, TT, or
helicity projector.  Embedding this filtration into all 116 rows remains the
open local-extension step.

On the exact TT-plus-shifted-auxiliary operator subcomplex this promotes
`physical_biwave_block_green_hyperbolic=true` and
`physical_Jordan_extension_causal=true`: the restricted witness has
`P=diag(B_TT,1,B_TT,1)` and an exact restricted
`Q Lambda + Lambda Q=1`.  That intermediate route did not promote the
all-row Green flags because its projector-free relative rank-14 equation-cone
contraction inside the rank-34 reciprocal block remained open.

A projector-free differential-module audit further reduces the reciprocal
rank-34 block.  A presented rank-12 gauge/subsidiary submodule has an exact
recursive Green inverse; its rank-22 quotient contains a closed rank-8
symmetric-hyperbolic constraint quotient and one unresolved rank-14 field
cokernel.  The local identity `(C1,div C1) K=0` makes curvature descend to
that cokernel.  Constructing its induced biwave intertwiner/inverse is now
the central Route-A problem.  The raw off-diagonal ideal is not nilpotent, so
a naive finite Neumann series is unavailable.

The remaining rank-four vector singleton is completely contractible after
the same shift.  On `(eta,v,v#,eta#)` a replacement witness gives
`P=I_16`, `G_+=G_-=I_16`, and `Lambda_+=Lambda_-=W`, with both Green
homotopy defects zero.  Its causal propagator vanishes.  These scoped vector
flags are true; the all-row problem is now concentrated in the rank-14 field
cokernel and its insertion into the complete witness.

That insertion is now formalized as an exact conditional all-row theorem.
The ledgers `116=34+4+26+26+26` and `34=12+8+14` cover every analytic row
once, and all 16 mapping-cylinder BV blocks are bound coefficientwise.  Given
the rank-14 package, the assembled algebra already verifies two-sided `G`,
`QG=GQ`, and `Q(WG)+(WG)Q=1`.  The only missing package is the complete
curved rank-14 operator and adjoint, compatible-source Green maps, and the
two residual source lifts through the rank-8/rank-12 extension.

`curved_rank14_weyl_cotton_input_manifest.json` is the compact handoff for
that last calculation.  It content-addresses the ordered rank-14 filtration
maps, complete 26-state evolution and lower-order matrices, 14 source
constraints and subsidiary operators, both symmetrizers, all 16 BV rows,
formal adjoints, and current conventions without duplicating the large
tables.  Its verifier checks 36 cross-hash and mutation guards.

The first rank-14 calculation is positive but changes the target.  A local
projector-free principal presentation splits into rank-10 light and rank-4
zero-speed sectors and has exact same-sided Green algebra with causal
temporal source lifting.  The raw `(C1,div C1)` symbol has rank `5` and
kernel rank `9` on the rank-14 cokernel, whereas the weighted Weyl--Cotton
compatible-source kernel has rank `12`.  More decisively, the raw image is
not contained in that kernel off shell: its generic compatibility defect has
rank `3` (rank `1` on the aligned null cone).  Thus the tempting quotient
`V7=K12/I5` is not defined.  The exact operator replacement is the equation cone
`That=(T,E_aux)`, `Khat=(K_state,-A_C)`, for which
`Khat That=K_state T-A_C E_aux=0`.  The required bridge is therefore an
equation-level SDR using the full `(L_WC,K_state)` rows, not a direct state
retraction.  The full graded audit restores the incoming gauge row and has
degree ranks `9 -> 24 -> 50 -> 49 -> 14`.  It also distinguishes the
ordinary BV identity layer `K_ordinary(-zeta)^T J` from both the exact curved
identity and the Green-witness companion.  The currently mixed leading
tables do not yet form one associated-graded complex: the internal square
defects have ranks `11,4` generically and `7,4` at null.  Symbol cohomology
is therefore deliberately left undefined.  A common componentwise
Douglis/Rees weight system is already feasible and an integer representative
is certified.  The next gate is complete associated-graded coefficient
extraction, especially lower `A` and weighted zeroth WC blocks; the equation
SDR, curved `L14`, `V14`, adjoint completion and Green operators remain false.

The residual calculation is already complete: `residual_H4_is_C2` and
`residual_gram_is_I2` are inputs to the terminal transport gate.  The missing
theorem is a pairing-compatible causal BV bridge from compactly supported
metric/auxiliary data through an all-row curvature prolongation to Cauchy
data, the `E/A/L` module, and the residual endpoints.  It must include
compatible inhomogeneous sources and degree-`-1` retarded/advanced maps
`Lambda_±` with `Q Lambda_± + Lambda_± Q = 1`; symmetric hyperbolicity alone
does not establish this identity.

**Paper 1** (the audit paper): the Bender–Mannheim generator Q is
*reconstructed* from the normal-form data (G, J, G₀) + positivity rather than
assumed; unique Hermitian-positive diagonalizer; stabilizer SO(2,ℂ)²
(unitary part generically ℤ₂² in the canonical coordinates, never the
full U(1)²);
corrected claims (canonical rescaling d_xd_y = γω₁ω₂, polar-factor
non-uniqueness); metric classification η′ = ρ†Wρ; distance d(I, M_obs) = 2r;
exact equal-frequency divergence; Lean-formalized Jordan no-go theorem.

**Paper 2**: minimum-distortion theorem — F(S) = ‖log S†S‖² ≥ 4r² over the
diagonalizer coset with exact closed form arccosh(cosh r cosh b) ± a
(mixed hyperbolic/flat Pythagoras); recognized as an orthogonal Cartan-norm
projection principle via the canonical compatible hull C_θ(H) = SL(2,ℂ)²
(totally geodesic ℍ³×ℍ³), proved in iff form, with the Sp(2n,ℂ) inter-mode
theorem. Plus the field-theory part: exact PT ground state, fidelity → √3/2,
occupation → 1/3 per UV mode pair, and disjoint auxiliary standard-CCR
product representations under the identity embedding in every d ≥ 1;
the physical Dyson-transported completions are instead pointed-unitarily
equivalent.

**Paper 3**: the three-geometries separation (metric ≠ vacuum ≠ dynamical);
Cartan–parabolic decoupling (beam-splitter identity, analytic no-frame
lemma); orbit constancy ⇒ universal Fock obstruction Θ(VΛ^d) for *all*
admissible positive metrics on the common auxiliary algebra; terminating
ultraviolet sector hierarchy (no UV invariant for d ≤ 3; Σ for
4 ≤ d < 8; the unordered mass pair (Σ,Π) for d ≥ 8). Global
equivalence involving the doubly massless □² vacuum requires a separate
infrared analysis and is not claimed;
**spectral bridge theorem**: the selected vacuum's Wightman function is the
spectral two-point functional of the fourth-order operator for all Δ ≥ 0,
whose confluent limit is the Bateman–Turok Krein vacuum (arXiv:2607.00096) —
same quasifree functional, different completion; fourth-order Hadamard
theorem (WF = 𝒞⁺, log ρ singularity with universal coefficient 1/(8π²),
±KG-Hadamard split structure).

**Paper 4** (the gravity lift): within translation-invariant, quasifree,
mode-local constructions satisfying the spectral condition and Poincaré
covariance, a classification and covariance-obstruction theorem for free
scalar-free Einstein–Weyl gravity (α = −3β).
Diffeomorphism reduction stratifies the phase space — PU pairing survives
exactly at helicity ±2 (γ = α/2, masses (M,0), M² = c₁/α); helicities
±1, 0 are *unpaired* massive ghosts subject to a completion trilemma
(positive norm / positive energy / standard reality: any two). Schur ⇒ no
covariant helicity-hybrid completion; exactly two covariant real forms
(positive pseudo-Hermitian with uniformly rotated massive reality, Krein
with standard gravitational reality) sharing one complex spectral quasifree
functional (covariant projector reassembly ½ : M²/2 : 1/6, 𝒩 = 4/c₁);
M-regular gauge-invariant Weyl correlator (DΠ^{(2,M)}D = DΠ₀D); conformal
boundary c₁ → 0 sectorwise (TT → □² Jordan, vectors → massless ghosts,
scalar → Weyl-null; count 4+2+0 = 6) at which the positive form terminates
(cond(N) → ∞) and only the Krein form continues.

**Paper 5** (the interaction paper): deformation and obstruction theory
for the interacting completions. Three levels of failure of the positive
construction — geometric (the fixed-order deformation generators become
singular toward the Jordan boundary; the general Rₙ ~ ε^{−3n/2} law is
conjectural),
cohomological (exact on-shell conversion classes at ω₁ = 3ω₂, order 2,
and ω₁ = (3/2)ω₂, order 3, gauge-independent, with a transfer-lattice
selection rule), and spectral (a complex-conjugate pair in the E = 27ω₂
multiplet's effective resonant-shell matrix, exact by Sturm certificate;
formally defined PT breaking with 𝒜 = Π∘Θ constructed; persistence
for the full unbounded operator remains open). In the perfect-square field
theory an even-ghost
rule protects the positive metric at first order, but the momentum
continuum makes branch-changing H+L → L+L shells generic and the
analytic deformation of the canonical pointed metric is obstructed on a
nonempty open shell subset (exact value 401√6/(39424g²) at a rational
kinematic point). What survives at
the massless boundary is the exact two-field exchange U↔V of
ℒ = −∂U·∂V + (λ²/2)U²V² (the Bateman–Turok O(1,1) embedding; they
identified the exchange as ghost parity) — a sector-exchanging
involution between two oppositely oriented interaction-generated
Jordan sectors, whose linearization is the bounded confluent limit of
the regulated branch parity on the doubled space. The hierarchy
conjecture's first prediction is confirmed computationally: 5:1 is
unobstructed through order 3 and obstructed at order 4 by exactly
−(203125√5/2341011456)(a₁a₂†⁵−a₁†a₂⁵). And the two completions
*separate* in the verified perturbative setting: at the rational shell
point the complete reachable on-shell T is exactly ghost-parity (Krein)
pseudo-Hermitian and the obstruction lives entirely in its κ-odd block,
while the analytic positive pointed-metric deformation is obstructed. The
result does not exclude a nonanalytic or differently pointed positive
completion. In the cross-paired charge frame the mapped split vacuum has
both charge directions, with the exact ratio
S_UU/S_VV = (δ/2g)² = ε/g. One-sided charge nullity holds exactly on the
ε = 0 confluent line; the Bateman–Turok massless point additionally has
μ² = 0.

**Paper 6** (the interacting-gravity paper): applies Paper 5's
deformation complex to the two covariant free real forms classified in
Paper 4. The exact Einstein consistent truncation kills all tree
amplitudes with one massive and otherwise massless external legs, while
equal-mass kinematics closes the remaining odd-massive cubic channel, so
the first-order obstruction vanishes. At second order the open process
`MM -> Mh` has a nonzero complete tree amplitude: an independent
Einstein-frame rail gives pole residue `sqrt(3)/8`, and the original
fourth-order perturbiner gives the exact interior-shell reduced
certificate `7881241032/5584765625`. A Born--deformation identity now
proves that the anti-Hermitian part of this stationary Born block is the
full metric-deformation cocycle, including both quartic contact and
two-cubic exchange terms. Within the explicitly stated natural,
particle-number-diagonal, cluster-multiplicative class, the induced Krein
grading is `(-1)^N_M`; the obstruction is non-null, survives physical
BRST cohomology, and admits no uniform abelian charge-null analogue.

**Paper 7** (the residual conformal branch): starts from pure-Weyl metric
fields on the conformal cylinder, derives the minimal and gauge-fixed
BV--BFV state complex, and gauges all fifteen residual conformal generators
for the selected closed-universe boundary problem.  The centered
one-particle cohomology vanishes; exactly the two ghost-dressed chiral
curvature-square vertex classes `[W_+^2]` and `[W_-^2]` survive, with
field-induced Gram matrix `I2`.  The normalized `E/A/L` module now has an
infinite-index energy-mode Krein completion, its symmetric bosonic Fock
space has fundamental symmetry `Gamma_s(J)`, and the residual differential
has a closed maximal block realization.  A bounded Cartan contraction
proves closed range and reduces completed cohomology to the unchanged finite
centered block.  This is not a positive graviton Hilbert-space theorem or a
quantum anomaly result.  The separate direct tractor construction now proves
the full free covariant BV causal theorem, but not a canonical endpoint Green
inverse or Hadamard theory.  At the reduced one-particle level, the Lorentzian tensor/vector fields have an
exact Cauchy--Sobolev realization: the TT branches use
`H^1 + L^2`, the vector branch uses `H^(3/2) + H^(1/2)`, and the resulting
harmonic transform is Krein-unitary onto the completed `E/A/L` module.

## Reports (`reports/`)

- `verification.md` — paper-1 audit report: confirmed / corrected /
  unproved / failed, plus answers to the spec's 12 research questions.
- `variational-and-field-theory.md` — running log for papers 2–3: theorem
  statements, refuted claims (with what replaced them), freeze passes.
- `verification.json`, `regression.json` — machine-readable claim tables.

## Verification pipeline (`symbolic/`, `numeric/`, `lean/`)

Symbolic (SymPy):
- `verify_sympy.py` — paper-1 audit, 51 claims (Verifications A–L of the spec).
- `verify_variational_fock.py` — paper-2 claims (20 checks): distortion
  closed form, PT ground state, fidelity/occupation, r(k) identity.
- `verify_paper3_audit.py` — paper-3 claims (P1–P10): beam splitter, orbit
  constancy, sector expansions (coefficients 1/12 and 29/576), bridge
  Wightman functions, no-frame lemma.
- `verify_hadamard.py` — Hadamard audit (H1–H6): bisolution, commutator
  normalization, log-coefficient 1/(8π²), IR smoothness, ±Hadamard split.
- `verify_wolfram.wl` — independent Wolfram rail (not run: no Mathematica).
- `gravity_engine.py` — O(ε²) second variation of √−g(c₁R + αR²_μν + βR²)
  around flat space, per helicity sector (shared engine for G-checks).
- `verify_gravity_reduction.py` — paper-4 G1–G7: TT PU blocks, vector/scalar
  unpaired ghosts, scalaron decoupling, mode count, stabilizer 4→16.
- `verify_gravity_completion.py` — paper-4 G8–G9: quarter-turn trilemma,
  T₀·SO(2,ℂ) real-form coset, Schur no-hybrid, covariant D_tot, TT assembly.
- `verify_gravity_spectral.py` — paper-4 G10–G12: helicity kernels with
  symplectic residues, covariant projector reassembly, Weyl-correlator
  M-regularity, sectorwise conformal limits + cond(N) divergence.
- `gravity_perturbiner.py` — shared exact multi-wave Einstein–Weyl
  perturbiner used by the cubic and four-point checks.
- `gravity_four_point.py` — import-safe exact four-point assembler exposing
  the quartic contact and all three gauge-fixed exchange channels.
- `verify_gravity_cubic.py` — gravity G13–G14 in the original
  fourth-order variables: exact multi-wave perturbiner, one-massive-leg
  cubic rule, Ward identities, nonzero `MMM`/`MMh` amplitudes and
  massive-pole factorization.
- `verify_gravity_factorization.py` — independent Einstein-frame G14
  rail: cubic-potential cancellation, exact amplitudes
  `A3(MMM)=-sqrt(6)/8` and `A3(MMh)=-sqrt(2)/8`, symbolic Ward identity,
  complete five-polarization residue numerator `sqrt(3)/32`, and explicit
  massive inverse-kernel normalization.
- `verify_gravity_g15.py` — exact real-shell `MM -> Mh` certificate with
  quartic contact plus all exchanges, Ward/Bose/internal-gauge checks, and
  pole-factorization regression.
- `verify_gravity_obstruction.py` — gravity G17: termwise uniform
  quarter-turn of the full connected second-order Born operator,
  reversed-process physical adjoint, shell projection, the exact nonzero
  obstruction `-2i A_K`, first-order metric-ambiguity independence, and
  the exact Born--deformation-source identity.
- `verify_gravity_krein.py` — gravity G18: covariant one-particle grading
  commutant, cluster-factorizing Fock lift, exact non-null Krein quadratic
  block, continuous-charge no-go, and BRST-cohomology survival.
- `verify_gravity_paper6.py` — one-command Paper-6 reproduction driver;
  use `--quick` to omit only the slower G15 pole regression.
- `verify_paper1_referee.py`, `verify_paper2_referee.py`,
  `verify_paper3_referee.py` — referee-round claim verification
  (spectrum of Q, normalization proposition; pointed-unitary identity;
  bridge signs, Hadamard remainder, IR anchor, Cartan convention).
- `verify_interaction_deformation.py` (ID1–ID10),
  `verify_interaction_order3.py` (SR/O3), `verify_pt_breaking.py`
  (PT/PS), `verify_perfect_square.py` (PS-A–H), `verify_two_field.py`
  (TF1–TF7), `verify_sector_obstruction.py` (SO1–SO7),
  `verify_hardening.py` (HX1–HX3) — paper-5 interaction-deformation
  program: cubic PU deformation through third order, 3:1/3:2
  obstructions, spectral PT-breaking, selection rules, perfect-square
  field theory, exact two-field rewriting and sector-exchange κ₀,
  sectorwise second-order obstruction (exact value 401√6/39424),
  confluent parity theorem.
- `verify_doubled_theory.py` (DQ1–DQ9) — doubled/Krein structure:
  O(1,1) hyperbolic-polar form and Noether current, mirror-adjoint
  relation H_B = WH_A†W† exact with W = ι∘(−1)^{N_ghost} (= Krein
  pseudo-Hermiticity), graph theorem (positive invariant half ⇔
  pointed positive metric), finite-time paired pseudo-unitarity,
  κ-odd localization of the on-shell obstruction, classical Ward
  identity with exact regulator breaking.
- `verify_obstruction_null.py` (ON1–ON4) — obstruction-to-null program:
  finite-particle charge-null lemma (graded Krein trace), canonical
  Bogoliubov map of the regulated split theory onto the cross-paired
  Bateman–Turok charge basis, exact law S_UU/S_VV = ε/g for the mapped
  vacuum's charged squeezing (one-sided iff ε = 0; the BT massless point
  also has μ² = 0), confluent coefficient −g/(4w²) (−1/(4w²) at g = 1),
  exact reference-dispersion no-go, and residual-frame runaway evidence.
- `verify_51_order4.py` (FO1–FO9) — order-4 machinery (programmatic
  adjoint-series word generation, re-derives orders 2–3 exactly):
  5:1 obstruction confirmed at order 4, ω₂⁻⁹ scaling, gauge
  independence, R₄ = O(ε⁻⁶).

Numeric (mpmath/numpy):
- `regression.py` — paper-1 regression, 4 parameter triples at 50–80 digits.
- `distortion_scan.py` — global optimization test of the minimum-distortion
  conjecture + invariant cross-checks.
- `cartan_checks.py` — hull Lie-closure dims, inter-mode normal space,
  first-variation identity, normalization dictionary.

Lean 4 + Mathlib v4.29.0 (`lean/`, builds with **zero `sorry`**):
- `PaisUhlenbeck/Definitions.lean` — J, G, G₀, M, K, N, S; K = J·M.
- `PaisUhlenbeck/Symplectic.lean` — K² = −(αβ)I; N² = 1; SᵀJS = J; det S = 1.
- `PaisUhlenbeck/NormalForm.lean` — SᵀGS = G₀ (division-free certificates).
- `PaisUhlenbeck/JordanObstruction.lean` — full 2×2 Jordan no-go theorem.

## Reproduce

```bash
cd symbolic && python3 verify_sympy.py             # paper 1 (~4 min)
cd symbolic && python3 verify_variational_fock.py  # paper 2
cd symbolic && python3 verify_paper3_audit.py      # paper 3
cd symbolic && python3 verify_hadamard.py          # paper 3, Hadamard
cd symbolic && python3 verify_gravity_reduction.py   # paper 4, G1–G7
cd symbolic && python3 verify_gravity_completion.py  # paper 4, G8–G9
cd symbolic && python3 verify_gravity_spectral.py    # paper 4, G10–G12
cd symbolic && python3 verify_gravity_paper6.py       # paper 6, full suite
cd symbolic && python3 verify_conformal_paper_free.py --required   # paper 7, fast required rail
cd symbolic && python3 verify_conformal_paper_free.py --reproduce  # paper 7, exhaustive publication rail
cd numeric  && python3 regression.py && python3 distortion_scan.py && python3 cartan_checks.py
cd lean     && lake exe cache get && lake build    # zero sorry
cd symbolic && for f in verify_interaction_deformation verify_interaction_order3 verify_pt_breaking verify_perfect_square verify_two_field verify_sector_obstruction verify_hardening verify_doubled_theory verify_51_order4 verify_obstruction_null; do python3 $f.py; done   # paper 5
cd paper    && for f in symplectic-diagonalization variational-fock fourth-order-vacuum fourth-order-gravity ghosts-geometry-reality interaction-obstructions einstein-weyl-interaction-obstructions conformal-residual-cohomology; do pdflatex $f.tex; done
```

Release tags: `paper1-v1.2`, `paper2-v1.3`, `paper3-v1.3`,
`paper4-v1.1`, `paper5-v1.1` (current freezes; earlier tags remain for
history). Before submission: replace
"companion paper" citations with arXiv IDs, check the "to appear"
references, match IR-extension conventions noted in paper 3's bridge
theorem, mint a DOI for the archived commit.
