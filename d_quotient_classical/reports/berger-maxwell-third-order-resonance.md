# Berger Maxwell third-order resonance

## Outcome

The retained order-two standing-wave correction lifts to the authoritative
54-row gravity complex and solves the full unary Maurer--Cartan equation.
The exact lift is

```text
h54^(2)=iota_cl h26^(2)-1/2 S_cl q2(A_st,A_st)
```

For this physical source `S_cl q2(A_st,A_st)=0`; the full correction has
nonzero rows

```text
[{'index': 5, 'row_id': 'h_hat_00', 'coefficient': '5120/567'}, {'index': 9, 'row_id': 'h_hat_11', 'coefficient': '-2466560/147819'}, {'index': 12, 'row_id': 'h_hat_22', 'coefficient': '-76705280/4582389'}, {'index': 14, 'row_id': 'h_hat_33', 'coefficient': '-14080/1953'}]
```

and induces no nonminimal component.  The 54-row source-closure,
Maurer--Cartan, and projection residuals vanish coefficientwise.

## First physical mixed Maxwell block

Varying `d star_g d A_st` in the displayed diagonal metric correction gives

```text
q2(h^(2),A_st)|e023 = 564428800*cos(2*sqrt(10)*t/3)/35920017
```

The same coefficient follows from varying the reduced electric kinetic and
magnetic coefficients.  Their relative dispersion difference is
`-7055360/3991113`.

At fixed `beta`, the cosine/sine unary matrix is zero while the source vector
is `['564428800/35920017', '0']`.  The normalized dual witness
`['35920017/564428800', '0']` pairs to one.  Therefore there is no
periodic order-three primitive at the unshifted frequency.

This is a frequency resonance, not a failure of nonlinear continuation.
The exact Poincare--Lindstedt correction is

```text
delta beta = -7055360*sqrt(10)/11973339
A^(3)_1 = 14110720*sqrt(10)*t*sin(2*sqrt(10)*t/3)/11973339
```

and `q1 A^(3)+q2(h^(2),A_st)=0` exactly.

## Scope and health

The block has D-weight zero and accesses only the stationary homogeneous
diagonal metric and horizontal Maxwell direction.  It does not classify the
radiative Einstein-like/extra-Weyl branches.  The resonance changes the
frequency inside the already positive Maxwell phase plane and introduces no
negative physical direction.

The complete coupled Maxwell BV q2, localized apparatus, retarded signal,
and all-orders continuation remain open.  Machine-readable result:
`d_quotient_classical/certificates/BERGER_MAXWELL_THIRD_ORDER_RESONANCE.json`.
