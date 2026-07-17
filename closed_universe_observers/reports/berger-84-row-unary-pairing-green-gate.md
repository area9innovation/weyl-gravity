# Berger 84-row unary, pairing, and Green completion gate

## What closes

The complete 84-row odd pairing is nondegenerate.  More substantially, the
two memory channels can be adjoined to the certified 64-row
gravity--clock--Maxwell complex now, without waiting for the rod Hessian.
On the affected field order

```text
(A, m0, m1, p0, p1)
```

the action Hessian is

```text
[ M   0    0   -k B0*  -k B1* ]
[ 0   0    0    T0*      0    ]
[ 0   0    0     0      T1*   ]
[-kB0 T0   0     0       0    ]
[-kB1  0   T1    0       0    ]
```

The certificate multiplies this matrix on both sides by an explicit finite
advanced/retarded inverse.  Both defects vanish in the universal
noncommutative operator algebra.  The inverse terminates at order
`kappa^2`; its off-diagonal memory entries include the two physically
necessary cross-detector propagation terms

```text
kappa^2 H0 B0 G B1* J1,
kappa^2 H1 B1 G B0* J0.
```

The corresponding BV unary blocks have zero new nilpotency and cyclicity
defects.  Maxwell gauge compatibility is exact because each detector reads
`dA`, so `B_a d=0` follows from `d^2=0`, and `delta B_a*=0` follows by formal
adjunction.  On the stationary Berger background `div(n_Theta)=0`, hence
`T*=-T`; the certificate exports the two-sided clock-line Volterra formulas
for `H_ret`, `H_adv`, and `J_+/-=-H_+/-`.  Equivalently, homological
perturbation gives

```text
Lambda72,+/- = Lambda0,+/- (I + V_kappa Lambda0,+/-)^-1,
```

and its Neumann correction terminates after two readout insertions.  Together
with the base complex this certifies a 72-row causal subcomplex on rows
`0..63,70..73,80..83`.

## What does not close

The six rod wave equations cannot be appended as an independent diagonal
block.  Each certified rod background is nonconstant, hence

```text
Gamma_R(xi)_aI = Lie_xi Rbar_aI
```

is nonzero for the existing diffeomorphism ghosts.  Full BV nilpotency and
cyclicity therefore also require the cotangent adjoint, both gravity--rod
Hessian directions, the shifted metric Hessian, and a coupled causal witness.
None of those operator payloads is present in the current imports.  Calling
the diagonal scalar waves an 84-row BV complex would drop a real gauge path.

The shifted background Euler equations are certified on the separate
`(0,0)`, `(epsilon_R^2,0)`, and `(0,kappa)` axes.  The mixed
`epsilon_R^2*kappa` coefficient and all higher orders remain open.

## Next exact calculation

Export content-addressed `Gamma_R`, `Gamma_R^sharp`, `K_Rh`, `K_hR`,
`Delta_K_hh`, and the coupled causal witness `W_rod`.  Once those blocks are
available, the certified 72-row memory construction can be spliced into the
full 84-row unary and the four global identities can be replayed rather than
assumed.
