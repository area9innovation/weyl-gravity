# Strict 386-row field-equation Green quotient inverse

## Outcome

The degree-one-to-zero component G_sigma of each accepted Green homotopy is now typed exactly. It is a right inverse of the 386-row field-equation operator K on Noether-compatible sources and a left inverse modulo gauge. A two-sided inverse on the full ungauge-fixed field and equation spaces is impossible: the exact complex has nonzero gauge and Noether maps with K R=0 and N K=0. Consequently the correct nonlinear gate is not a stronger unary inverse. It is coefficientwise proof that every q2/q3/higher nonlinear source is N-closed. The candidate first-order source passes; the lambda-squared source remains undecided. Gate A, Hadamard and QME remain fail closed.

## The typed complex

```text
... -> C^-1 --R--> C^0 --K--> C^1 --N--> C^2 -> ...
rows: C^0=116, C^1=116
nonzero jet coefficients: R=425, K=3264, N=425
```

## What the Green homotopy actually gives

```text
G_sigma=pr_C0 Lambda_graph,sigma inc_C1
K G_sigma + A_sigma N = identity_C1
G_sigma K + R C_sigma = identity_C0
```

Thus `G_sigma` is an exact right inverse on `ker N` and an exact left inverse on `C^0/im R`. No gauge representative is selected.

## Why the stronger inverse is impossible

- If L K=identity_C0, then R=L K R=0, contradicting the certified nonzero gauge map R.
- If K J=identity_C1, then N=N K J=0, contradicting the certified nonzero Noether map N.

This is the expected distinction between a Green operator for a nondegenerate two-term equation and a Green homotopy for a gauge complex, as formalized by Benini--Musante--Schenkel.

## Consequence for the formal response

```text
q1(x)=0 and the arity-two identity imply N s_1=0
K G_sigma(s_1)=s_1
next: At every coupling order m, the assembled nonlinear source S_m must satisfy N S_m=0; then phi_m=-G_sigma(S_m) solves K phi_m=-S_m modulo gauge.
```

The lambda-squared diagnostic remains `(1/4)(B_sigma(x,q2(x,x))+B_sigma(q2(x,x),x))`. Its source-cocycle closure is not certified.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_386_field_equation_green_quotient_inverse.py --check
python3 quantum-weyl/classical_import/check_strict_386_field_equation_green_quotient_inverse.py
python3 quantum-weyl/classical_import/verify_strict_386_field_equation_green_quotient_inverse.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_386_field_equation_green_quotient_inverse.py -v
```

## Boundaries

- This does not establish a two-sided inverse of the ungauge-fixed field-equation operator on all fields and all equation sources.
- This does not establish a selected gauge fixing, global gauge slice or representative-selection operation.
- This does not establish flattened component bytes for the nonlocal Green kernel or an effective numerical solver.
- This does not establish that the stabilized q2 candidate is the authoritative nonlinear Weyl BV operation.
- This does not establish coefficientwise nonlinear source closure beyond first order.
- This does not establish vanishing or nonvanishing of the lambda-squared B(q2) residual.
- This does not establish q3 or higher source brackets or a Weyl-BV Maurer-Cartan/Moller theorem.
- This does not establish the authoritative twenty-export classical import Gate A.
- This does not establish a Hadamard state, positivity, renormalized Lorentzian products, QME restoration, residual transfer, unitarity or a Lorentzian quantum theory.
