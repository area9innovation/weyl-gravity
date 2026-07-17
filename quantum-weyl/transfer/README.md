# Nonlinear homological transfer

This package starts the classical nonlinear prerequisite to the residual
quantum programme.  It transfers the Taylor coefficients of the full
classical BV vector field through the already certified free contraction:

```text
full conformal-gravity BV complex -> endpoint complex -> residual/minimal model
```

The implementation uses exact arithmetic and the suspended
graded-symmetric factorial convention.  Through arity three it computes

```text
ell_2 = pi_cl q2(iota_cl, iota_cl)
ell_3 = pi_cl [q3(iota_cl^3) - sum q2(s_cl q2(iota_cl,iota_cl),iota_cl)]
```

with the Koszul signs of the three `(2,1)` unshuffles.  The engine verifies
the full linear strong-deformation-retract identities, side conditions,
degree/parity, Koszul symmetry, `Q^2=0` for both the imported and transferred
Taylor tensors through arity three, and absence of floating-point data.

## Current boundary

The general engine is ready, but the complete conformal-gravity calculation
is blocked.  The import layer now has an executable support-local `q1`/`q2`
and `D`-action preflight that rejects finite-mode substitution and requires
complete field/ghost/antifield row ledgers, exact local-expression payloads,
pinned proof artifacts, and reproducible hashes.  No authoritative payload
currently passes that contract.  HT1 nevertheless imports one genuine
classical block already certified by the bridge.  The endpoint Taub map,
selected BV--BFV suspension,
all-energy moment map, and strict centered HPL transfer determine

```text
Omega_3 = c^A mu_A(Phi,Phi) - f^A_BC c^B c^C b_A/2.
```

The Hamiltonian vector field therefore computes and exactly normalizes
`ell_2(matter,matter)` into the residual ghost momentum,
`ell_2(ghost,matter)`, and the universal ghost brackets.  The portable exact
payload uses one ordered magnetic basis for the Taub generators and fitted
BRST structure constants, serializes all selected `q2` blocks, and verifies
the cubic BFV master equation directly with the action-scaled symplectic
pairing.  This selected residual cubic bracket is chirality diagonal and
closes as the strict CE differential.  What remains absent is a portable
support-local `q2` tensor before endpoint projection and any extra rows
outside the selected algebraic field domain.

HT1b has now started from the opposite, local side.  Its fast rail imports two
content-addressed exact curvature regressions, independently reintegrates their
stereographic radial `B^(2)(h_1,h_2)` densities, and checks the corresponding
raw-normalized HT1 residual entries.  A separate Tier-2 rail executes eight
exact curvature probes: six reconstruct both forward local Taub densities and
two verify the reverse slice-current density adjoint.  Reverse gauge probes and
hence reverse local Taub densities remain absent.  This is a mode-specialized
local metric-sector seed, not the arbitrary-input tensor
`B^(2)_{mu nu}[h_1,h_2]`; the Diff/Weyl ghost rows, antifield rows, and local
arity-two classical-master identity remain absent.

ND1 now tests the first nonlinear `D`-quotient identity on every `q2` block
available in HT1.  It derives the adjoint, coadjoint, matter-ket, and
matter-bra `D` actions from the portable payload and computes all 529,470
coefficients of the four arity-two derivation-defect tensors.  They vanish
exactly, and all 3,976 nonzero selected `q2` components conserve `D` weight.
This rules out a cubic `D`-derivation defect inside the selected residual BFV
model only.  The full support-local defect and `iota_D^(2)` remain blocked on
the arbitrary-input BV tensor and imported contraction, so the setting verdict
is still `INPUT_GATE_BLOCKED`.

ND2 now supplies the exact consumer and obstruction rail needed when the
classical support-local payload arrives.  It canonicalizes rational local
expressions, rejects unknown expression languages, independently reconstructs
finite `q1`, `q2`, and `D` tensors, and evaluates both

```text
[L_D,q2],
A_D^(2) = [q2,iota_D] - L_D^(2).
```

On the exact arity-two bilinear-map complex it solves
`[q1,iota_D^(2)] = -A_D^(2)` or retains a normalized dual obstruction
witness.  Admissibility constraints are part of the solve, so an ambient
primitive can be rejected when it is not cyclic, real, boundary-compatible,
or otherwise allowed.  Executable nonzero fixtures exercise the correction,
obstruction, mutation, and inadmissible-primitive branches.  They carry no
conformal-gravity coefficient: the support-local `q2` payload and combined
physical assembly remain absent.

The permanent ND2 engine is now separated from a versioned physical-run
contract.  A physical execution must pin four independently hashed artifacts:
the total-`D` disposition certificate, support-local `q1/q2/D` export,
classical contraction, and admissibility policy.  The declared disposition is
checked against a strict total-`D` schema and bound to its phase space,
boundary-condition hash, classical commit, dependency-tag union, and source
hashes.  Only `D_GAUGE` reaches the Cartan solver; `OPEN`, canonical
`D_CHARGED`, `SECTOR_DEPENDENT`, and `NOT_HAMILTONIAN` terminate on distinct
non-contraction routes.  The physical executor accepts only the opaque token
returned by complete manifest verification.  Expression
evaluators are registered by schema version, operator inventory, and
implementation-manifest hash.  Unknown evaluators, schema mismatches, changed
evaluator source, missing assembly adapters, and artifact hash drift all stop
before classification.

The positive Berger-clock result is now imported on its actual boundary.  In
addition to the healthy exact background and nonzero reduced internal clock
momentum, the exact fixed-coupling lapse constraint and compact averaging prove
`D_GAUGE` on the declared smooth linearized phase space.  A second immutable
import recognizes the registered exact cyclic clock-sector SDR: 8 of 34
minimal rows contract and 26 remain.  Its source exports formulas and operator
fingerprints rather than independently consumable map entries, and it does not
certify `D`-equivariance.  The companion portable receiving schema fixes the
coefficient ring, derivative-symbol convention, grading bridge, basis order,
partial maps, coverage, hashes, and the four `D` commutators required for the
next handoff.

The retained 26-row minimal `q1` is now a third immutable import.  Its theorem,
classical registration, and repaired Draft-2020-12 schema are pinned at
separate commits.  The quantum consumer parses all exact polynomial PBW
coefficients, reconstructs the noncommutative invariant-frame operators, and
independently reproduces formal self-adjointness, the dual Noether row, both
Noether compositions, cyclicity, and nilpotency.  At that import stage this
closed the retained minimal-`q1` prerequisite only; the portable clock maps,
nonminimal/all-row `q1`, complete `classical_contraction`, `q2/D`, and
admissibility artifacts were still absent.

That retained operator is now exposed through a separate content-addressed
PBW backend.  It declares the coefficient domain
`Q[alpha_B,u,v] tensor U(e_Berger)`, supports arity one, and replays the exact
import verification before returning a typed payload.  It is deliberately
not registered as the current `Fraction`-valued Cartan evaluator.  Physical
assembly therefore remains false until either the Cartan solver is extended
to the PBW-module domain or an exact finite specialization is supplied with a
`REDUCED-MODE` tag.

The later portable contraction export supersedes the earlier map-payload
blocker.  The quantum consumer now independently verifies the complete
34-row minimal unary differential and exact order-zero `iota_cl`, `pi_cl`,
and `S_cl`: nilpotency, both chain maps, the SDR identity and side conditions,
cyclicity, and the full/retained pairings all pass.  Thus the standalone ND2
`classical_contraction` artifact is satisfied.  Nonminimal rows and the
separate `q2/D` package, admissibility, compatible Cartan assembly, and causal
inputs remained open at that stage, so physical execution was still false.

The subsequent gauge-fixed export now closes the unary/nonminimal prerequisite
as well. A pinned quantum-side consumer independently parses the complete
54-row `classical_unary_q1`, verifies the finite-order BV-canonical shear,
cyclic pairing, nilpotency, and the transformed 54-to-26 contraction. This is
classical unary evidence, not the quantum correction \(\hbar Q_1\). The
complete support-local helical `D_action_cl` has now also landed.  Its pinned
consumer reconstructs the order-one PBW operator on all 54 rows and verifies
unary, contraction, and cyclic equivariance coefficientwise.  The decisive
nonlinear input remains absent: the complete support-local
`classical_binary_q2`. ND2 therefore remains fail-closed.

Reproduce the local-D import with

```bash
python3 quantum-weyl/transfer/berger_54_row_local_d_import_certificate.py --check
python3 -m unittest quantum-weyl/transfer/tests/test_berger_54_row_local_d_import.py
```

The complete-q2 arrival rail is prepared but remains `INPUT_BLOCKED`.  Its
strict portable contract accepts a sparse `[54,54,54]` bilinear PBW record in
the same Berger invariant frame and coefficient ring as the unary package.
The independent consumer binds every row and the `q1`, `D54`, `iota_cl`,
`pi_cl`, `S_cl`, and pairing hashes; it checks exact coefficients, canonical
record hashes, cohomological degree, jet bounds, output completeness, graded
symmetry, and proof-artifact hashes.  A nonzero field--field-to-equation
fixture tests the implementation only.  It cannot substitute for the
committed classical tensor, and operator-valued arity-two replay, transfer,
and the Cartan verdict remain false until that tensor arrives.

```bash
python3 quantum-weyl/transfer/berger_54_row_q2_arrival_certificate.py --check
python3 -m unittest quantum-weyl/transfer/tests/test_berger_54_row_q2_arrival.py
```

The exact operator-valued replay layer is also ready ahead of the scientific
input. It independently re-encodes the noncommutative Berger PBW algebra and
computes the arity-two `q1/q2` nilpotency defect, the `D/q2` derivation defect,
and graded BV cyclicity modulo integration by parts. A nonzero implementation
fixture passes all three identities; valid-degree output and `D`-axis
mutations produce localized exact defects, showing that the checks are
sensitive. That readiness receipt advanced the executable consumer rather
than the scientific claim; the landed tensor and its independent replay are
recorded separately below.

```bash
python3 quantum-weyl/transfer/berger_54_row_q2_replay_certificate.py --check
python3 -m unittest quantum-weyl/transfer/tests/test_berger_54_row_q2_replay.py
```

The scientific support-local q2 has now landed and is pinned independently at
classical commit `7b352307`. Its specialized `Q(sqrt(10))` payload contains
150,305 exact PBW terms across 39 nonzero output rows, with maximum total jet
order six. The quantum importer reproduces both hashes, binds the unary and
`D` dependencies, checks all 54 rows, degree, PBW ordering, statistics, and
graded Koszul symmetry, and records the exact specialization from the older
symbolic Berger ring. That import gate is now followed by the independent
scientific replay below.

The subsequent full-dimensional bare unary Cartan gate is now decided
negatively.  A pinned independent microlocal replay at the exact null covector
`zeta=(1,1,0,0)` finds symbol ranks `(3,1,3)`, cohomology dimensions
`(0,6,6,0)`, and the normalized class/dual pair `h_hat_02` and
`coefficient(h_hat_02)-coefficient(h_hat_12)`.  Since the symbol of `D` is one
there, no finite-order support-local `iota_D^(1)` exists on the bare 26-row
complex; the imported `D`-equivariant SDR transfers the no-go to the bare
54-row extension.  The next construction must use residual/BFV or causal
extension data rather than forming the bare arity-two Cartan source.

That scientific replay is now complete. A dedicated exact `Q(sqrt(10))`
backend evaluates all 150,305 landed coefficients without generic symbolic
simplification. The `q1/q2`, `D/q2`, and odd-Darboux BV-cyclicity defects all
vanish. This authorizes transfer of the classical `ell2`; it does not itself
compute that transfer or promote a quantum claim. The bare unary equation
`q1 iota_D^(1)+iota_D^(1) q1=D` is now exactly obstructed as stated above, so
the arity-two Cartan source may only be formed after a residual/BFV or causal
extension supplies a valid replacement unary homotopy.

The complete binary operation has nevertheless been transferred through the
independent 54-to-26 SDR. The exact retained operation

```text
q2_26 = pi_26 q2_54(iota_26 tensor iota_26)
```

has 54,236 canonical `Q(sqrt(10))` PBW coefficients on all 26 output rows,
through total jet order four. Its retained `q1/q2` and odd-Darboux cyclicity
defects vanish coefficientwise. This is a retained-complex operation, not yet
the minimal residual/cohomology `ell2`, and it does not bypass the bare unary
Cartan obstruction.

```bash
PYTHONPATH=quantum-weyl python3 -m transfer.berger_support_local_q2_replay_certificate --check
PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/transfer/tests/test_berger_support_local_q2_scientific_replay.py -v
PYTHONPATH=quantum-weyl python3 -m transfer.berger_unary_d_cartan_obstruction_import_certificate --check
PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/transfer/tests/test_berger_unary_d_cartan_obstruction_import.py -v
PYTHONPATH=quantum-weyl python3 -m transfer.berger_retained_26_q2_transfer_certificate --check
PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/transfer/tests/test_berger_retained_26_q2_transfer.py -v
```

The commands above validate checked receipts and run fast mutation
fixtures. Recompute the entire 150,305-term exact replay explicitly with

```bash
PYTHONPATH=quantum-weyl python3 -m transfer.berger_support_local_q2_replay_certificate --replay-check
PYTHONPATH=quantum-weyl python3 -m transfer.berger_retained_26_q2_transfer_certificate --replay-check
```

The classical gravity--clock--Maxwell extension has now landed as a sparse
64-row overlay.  Its first export exposed an exact cyclicity obstruction.
The committed convention-derived repair doubles every Maxwell-output term
and adds `[q1,F2]` for `F2(c_M)=c_M-2 i_c A`, including the complete
BV-canonical cotangent lift.  The pinned quantum acceptance consumer now
reconstructs 1,890 full coefficients and 1,474 retained coefficients.  Full
and retained `q1/q2`, full and retained odd-pairing cyclicity, and every
64-to-36 transfer comparison vanish exactly; the causal unary flags are
preserved.  The verdict is `ACCEPTED_COUPLED_Q2_CYCLIC_REPAIR`.

This accepts the classical binary vertex and opens the classical mixed-`q3`
gate.  It does not construct `q3`, compute a quantum anomaly coefficient,
restore the QME, perform residual quantum transfer, or promote a Lorentzian
or particle claim.  The legacy `D=e0` label still denotes
`K_Berger=D-omega R`; raw cylinder `D` remains affine.

```bash
PYTHONPATH=quantum-weyl python3 -m transfer.berger_coupled_64_q2_import_certificate --check
PYTHONPATH=quantum-weyl python3 -m transfer.verify_berger_coupled_64_q2_import
PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/transfer/tests/test_berger_coupled_64_q2_import.py -v
PYTHONPATH=quantum-weyl python3 -m transfer.berger_coupled_cyclicity_repair_readiness_certificate --check
PYTHONPATH=quantum-weyl python3 -m transfer.verify_berger_coupled_cyclicity_repair_readiness
PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/transfer/tests/test_berger_coupled_cyclicity_repair_readiness.py -v
```

```bash
python3 quantum-weyl/transfer/berger_support_local_q2_import_certificate.py --check
python3 -m unittest quantum-weyl/transfer/tests/test_berger_support_local_q2_import.py
```

A separate pinned consumer now imports the first action-derived nonlinear
Berger block without crossing that boundary.  The six stationary homogeneous
rows use the rational coordinate \(c=c_0(1+u)\) and normalized action density
\(L/c_0\), so the exact Hessian and cubic Taylor tensor lie in \(\mathbb Q\).
The consumer reconstructs `classical_unary_q1`, `classical_binary_q2`, the
cyclic pairing, and the centered weight-zero `D_action_cl`, then runs the ND2
arity-two engine.  All identities pass and the Cartan classification is
`ZERO_SOURCE`.  The verdict layer then sends that exact zero source through
the existing boundary solver and retains the admissible primitive
`iota_D^(2)=0`.  The six-row Koszul--Tate block is acyclic, so the primitive
introduces no negative physical direction; the two negative directions of
the unreduced stationary Hessian do not survive as cohomology.  Einstein/extra-
Weyl radiative coupling is not applicable at this non-Einstein Berger base
point.  This is an executable `REDUCED-MODE` result only; within that fixture,
support-local q2 and nonzero-weight D equivariance remain absent, and full
physical ND2 execution remains false.
Reproduce it with

```bash
python3 quantum-weyl/transfer/berger_rational_fixture_q2_d_import_certificate.py --check
python3 -m unittest quantum-weyl/transfer/tests/test_berger_rational_fixture_q2_d_import.py
python3 quantum-weyl/transfer/berger_reduced_mode_cartan_certificate.py --check
python3 -m unittest quantum-weyl/transfer/tests/test_berger_reduced_mode_cartan.py
python3 quantum-weyl/transfer/berger_nonzero_weight_no_go_import_certificate.py --check
python3 -m unittest quantum-weyl/transfer/tests/test_berger_nonzero_weight_no_go_import.py
python3 quantum-weyl/transfer/berger_all_weight_cartan_import_certificate.py --check
python3 -m unittest quantum-weyl/transfer/tests/test_berger_all_weight_cartan_import.py
```

The finite nonzero-weight continuation is obstructed before the Cartan
equation.  The action-derived Berger square map $Q(x)=q_2(x,x)$ is
anisotropic over both the reals and complexes.  A nonzero mode at weight
$w$, cyclic nondegeneracy, and q2 closure therefore force the unbounded
sequence $w,-2w,4w,-8w,\ldots$.  The first $(-1,0,+1)$ candidate leaks
into the missing $E_{u,+2}$ row with normalized dual leakage witness
$(80/27,0,0)$.  The pinned consumer independently verifies the real
positive-form and complex ideal-membership certificates.  This is a closure
no-go, not a Cartan-cohomology obstruction; the infinite all-weight and full
support-local routes were the two continuations.

The all-weight continuation is now complete on the same spatially homogeneous
Berger block.  Retaining every integer weight closes q2 by convolution.  The
Cartan source is generically nonzero, and an explicit nonzero first-order,
time-local, graded-cyclic primitive solves the arity-two identity for symbolic
input weights $k,l$.  The operator has $D$-weight zero and acts on the
$u/N/\rho$ field/equation pairs at every weight.  The weightwise complex is
acyclic, so the primitive introduces no negative physical direction.  This
is still `REDUCED-MODE`: the full four-dimensional support-local q2 and
complete 54-row Cartan contraction remain open.

The first branch-labelled support-local block is also complete on an aligned
Brinkmann pp-wave sector.  The pinned classical theorem admits arbitrary
smooth profiles, with a harmonic Ricci-flat Einstein representative and a
biharmonic non-harmonic extra-Weyl representative.  The exact Bach operator
is linear on this sector, so all Einstein--Einstein, Einstein--extra-Weyl,
and extra-Weyl--extra-Weyl entries of the restricted `q2` vanish before
projection.  Consequently the transferred `ell2` is exactly zero and
independent of the homotopy.  This is a `LOCAL-ALGEBRAIC` aligned-sector
theorem; it does not determine nonaligned vertices, the centered Weyl-square
deformation brackets, the complete BV `q2`, or a quantum correction.

Reproduce the pinned import with

```bash
python3 quantum-weyl/transfer/ppwave_branch_transfer_import_certificate.py --check
python3 -m unittest quantum-weyl/transfer/tests/test_ppwave_branch_transfer_import.py
```

N-G5 now has a fail-closed Einstein-projection adapter and an exact helicity
parity pair.  The pinned Einstein theorem supplies the solution-locus inclusion
and local helicity-$\pm2$ module.  On the holomorphic and anti-holomorphic
complex three-point branches, respectively, the stripped Einstein factors

```text
<12>^6/(<23>^2 <31>^2)
[12]^6/([23]^2 [31]^2)
```

both evaluate to one and have parity-conjugate little-group weights
`(4,4,-4)` and `(-4,-4,4)`.  Exact setting metadata routes Berger reduced-mode
inputs away from this flat scattering rail.  The imported linearized defect
preflight and reduced-TT nonzero-mass projectors are boundaries, not a
full-BV pure-Weyl projector.  Shape comparison is allowed under the locked
stripped normalization, but no conformal-gravity vertex or overall coefficient
is matched until a setting-compatible complete support-local `q2`, full-BV
nonlinear Einstein-defect map, and all normalization factors are available.

```bash
python3 quantum-weyl/transfer/einstein_projection_amplitude_fixture_certificate.py --check
python3 -m unittest quantum-weyl/transfer/tests/test_einstein_projection_amplitude_fixture.py
```

The arity-two solve also has a block-sparse exact rail.  Declared additive
labels such as `D` weight, momentum, or jet filtration must be preserved by
`q1`; the differential then splits by
`w_out-w_left-w_right`.  Sparse rational elimination runs only in occupied
blocks and reproduces the ambient correction and obstruction witness exactly.

ND3 extends the Cartan recurrence by one arity:

```text
[q1,iota_D^(3)] = -[q3,iota_D] - [q2,iota_D^(2)] + L_D^(3).
```

The engine checks `Q^2=0`, the Cartan identities, `D` equivariance, and source
closure through arity three.  Direct `q3` and exchange `[q2,iota_D^(2)]`
sources remain separate machine tensors.  Exact fixtures exercise a retained
`iota_D^(3)`, a normalized obstruction, and a broken-`D` rejection.  No
physical `q3` or quartic conformal-gravity result is inferred.

The parity combinations

```text
e = (W_+^2 + W_-^2)/sqrt(2)   dynamical Weyl-square direction
o = (W_+^2 - W_-^2)/sqrt(2)   topological/Pontryagin direction
```

are analysis outputs, not hard-coded bracket answers.  They are
particle-number-two, ghost-dressed deformation classes, so their interacting
brackets are obtained from the induced coderivation on `Sym(H)` and a
subsequent deformation-cohomology projection; they are not a two-dimensional
basis rotation on the one-particle inputs of `q2`.  HT2 computes the direct
`q3` contact term and the `q2 s_cl q2` exchange trees separately, so
centrality, inertness, and cancellations remain auditable.

The one-particle question is formulated as a particle-number filtration
question.  Interactions need not preserve particle number, so the relevant
HT3 receipt is the associated spectral sequence and its obstruction maps,
not an assertion that the free direct-summand decomposition remains literal.

Quantum `Q_1` or higher corrections are a later input.  They may be
transferred only after a separate `QME_RESTORED` certificate.  Nothing in
this package is a quantum or `LORENTZIAN-CAUSAL` result.

## Commands

```bash
python3 quantum-weyl/transfer/nonlinear_transfer_certificate.py --check
python3 quantum-weyl/transfer/residual_cubic_certificate.py --check
python3 quantum-weyl/transfer/local_bach_seed_certificate.py --check
python3 quantum-weyl/transfer/d_derivation_certificate.py --check
python3 quantum-weyl/transfer/nd2_arity_two_certificate.py --check
python3 quantum-weyl/transfer/nd2_physical_run_certificate.py --check
python3 quantum-weyl/transfer/total_d_disposition_certificate.py --check
python3 quantum-weyl/transfer/berger_clock_import_certificate.py --check
python3 quantum-weyl/transfer/berger_retained_q1_import_certificate.py --check
python3 quantum-weyl/transfer/berger_pbw_backend_certificate.py --check
python3 quantum-weyl/transfer/berger_minimal_contraction_import_certificate.py --check
python3 quantum-weyl/transfer/berger_gauge_fixed_nonminimal_import_certificate.py --check
python3 quantum-weyl/transfer/berger_54_row_local_d_import_certificate.py --check
python3 quantum-weyl/transfer/arity_three_cartan_certificate.py --check
python3 quantum-weyl/transfer/ppwave_branch_transfer_import_certificate.py --check
python3 quantum-weyl/transfer/einstein_projection_amplitude_fixture_certificate.py --check
python3 quantum-weyl/classical_import/support_local_q2_contract_certificate.py --check
python3 quantum-weyl/classical_import/verify_snapshot.py --check
python3 -m unittest discover -s quantum-weyl/transfer/tests -v
```

The expensive direct-curvature reproduction is scheduled/manual rather than a
per-commit rail:

```bash
python3 quantum-weyl/transfer/local_bach_seed_direct_audit.py --check --jobs 2
```
