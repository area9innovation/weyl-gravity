# Candidate-17/20 deformable-kernel incidence normal form

## Result

The remaining strict opposite-sign problem now has an invariant
necessary-and-sufficient formulation that allows arbitrary deformation of the
two third-transvectant-kernel directions.

Use the actual node amplitudes \(F,G\in\mathbb C^5\), rather than a direction
at a zero node, and set

```text
Kbar = {(F,G): T3(F,G)=0, ||F||_W<=1, ||G||_W<=1},
x = ||F||_W^2,
y = ||G||_W^2,
c(F,G) = delta+a*x-b*y,
M_K(F,G) = -a*m(F)+b*m(G).
```

The compactified direction/occupation moduli space is the stratified
semialgebraic quotient

```text
M = Kbar/(U(1)_F x U(1)_G x SO(3)_lifted).
```

This quotient retains the full phase stabilizer of a vanished node, the
common-square algebraic singular locus, and every lifted-rotation orbit type.
No division by `x` or `y` is used.

The receiving Cartan-square factor can cancel the kernel moment exactly when

```text
||M_K(F,G)|| <= |c(F,G)|.
```

Let `A` be this admissible subset of `M` and define the zero-wall incidence

```text
I = {[F,G] in A : c(F,G)=0 and M_K(F,G)=0}.
```

For `alpha*delta<0`, a rotation-zero point contracts to the connected
double-singular hub if and only if its path component in `A` meets `I`.

Necessity follows because `c` changes sign between the initial point and the
hub. At the unavoidable zero of `c`, the square contribution vanishes and
rotation zero forces `M_K=0`.

Sufficiency has three stages:

1. Follow a semialgebraic path in the admissible component to `I` and lift it
   through the Cartan-square moment map.
2. At `c=M_K=0`, move the square direction to a phase-real zero-moment
   direction.
3. Scale `(F,G)` radially to `(0,0)`. Bilinearity preserves `T3=0`,
   `M_K` stays zero and `c=(1-s)delta`.

The square-moment lift is explicit. In the Cartan model write
`z=x+i*y`, impose `x dot y=0` by projective phase, and use

```text
r(u)=3*u/(2+u^2),
u(r)=(3-sqrt(9-8*r^2))/(2*r).
```

For nonzero radius the fibre is a connected rotation orbit around the moment
axis; at zero it is the connected phase-real `RP2`. Compact-group slices
handle all nonfree orbit types.

## Boundary incidence

The incidence set is nonempty in both strict sign chambers.

If `delta<0<alpha`, then `alpha=delta+a-b>0` implies
`0<-delta/a<1`. Choose

```text
G=0,
||F||_W^2=-delta/a,
m(F)=0.
```

If `alpha<0<delta`, then `alpha=delta+a-b<0` implies
`0<delta/b<1`. Choose

```text
F=0,
||G||_W^2=delta/b,
m(G)=0.
```

These are exact one-zero-node incidence points. Their existence does not
imply that every component of `A` reaches them.

## Candidate disposition

- Candidate 17, `alpha>0`, `delta<0`: contraction is equivalent to its
  admissible component meeting the `G=0` incidence.
- Candidate 20, `alpha>0`, `delta<0`: the same normal form applies on its own
  negative-`delta` chamber.
- Candidate 20, `alpha<0`, `delta>0`: contraction is equivalent to its
  admissible component meeting the `F=0` incidence.

The candidates share a proof but not a background, coefficient stratum or
atlas identity.

## Boundary

This theorem reduces arbitrary kernel-direction deformation to an exact
compact semialgebraic component-incidence problem. It does not prove that
every admissible component meets `I`, complete either off-balance
rotation-zero fibre, glue total occupations, perform final residual descent,
or establish an all-orders, causal, observational or quantum result.

EVIDENCE:
`bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_deformable_kernel_incidence_normal_form.json`
