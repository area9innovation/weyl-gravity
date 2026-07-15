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
conformal-gravity coefficient: the physical evaluator and classical
`q1/q2/D/iota_cl/pi_cl/s_cl` payload remain absent.

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
`D_GAUGE` on the declared smooth linearized phase space.  The support-local
all-row BV contraction, `q1/q2/D` tensor, and admissibility artifacts remain
absent, so no physical ND2 Cartan execution has occurred.

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
python3 quantum-weyl/transfer/arity_three_cartan_certificate.py --check
python3 quantum-weyl/classical_import/support_local_q2_contract_certificate.py --check
python3 quantum-weyl/classical_import/verify_snapshot.py --check
python3 -m unittest discover -s quantum-weyl/transfer/tests -v
```

The expensive direct-curvature reproduction is scheduled/manual rather than a
per-commit rail:

```bash
python3 quantum-weyl/transfer/local_bach_seed_direct_audit.py --check --jobs 2
```
