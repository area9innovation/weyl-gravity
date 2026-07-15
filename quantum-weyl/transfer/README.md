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
is blocked.  HT1 nevertheless imports one genuine classical block already
certified by the bridge.  The endpoint Taub map, selected BV--BFV suspension,
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
python3 -m unittest discover -s quantum-weyl/transfer/tests -v
```
