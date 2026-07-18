# Circumference velocity crossed with axial `ell=2` extra modes

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

Correction class: `BOUNDED_OR_FINITE_QUASIPERIODIC`.

Direct four-dimensional bivariate linearization gives, in the action-row order
`(6E_t,-6E_x,M_t,M_x)`,

```text
S(d,e1)=(-72 i sqrt(3), 0, 0, 0),
S(d,e2)=(0, -4 i sqrt(3)/3, 0, -4 i sqrt(3)).
```

At `omega^2=16/3`, an exact adjoint basis is

```text
w1=(-1,0,1,0),
w2=(0,-1/9,0,1).
```

The resulting pairing matrix is

```text
diag(72 i sqrt(3), -104 i sqrt(3)/27),
```

with determinant `832`.  It is therefore an isomorphism from the two axial
extra amplitudes onto the complete axial p-shell adjoint cokernel.  Since `d`
is an `SO(3)` scalar, the same multiplicity matrix acts for every `m`.

This changes the cone geometry: for `d!=0`, any prescribed axial resonant
defect can be canceled algebraically by suitable `e1,e2` amplitudes.  It does
not yet solve the polar resonant conditions, stabilizer moment maps,
nonresonant rows, or the complete second-order equation.
