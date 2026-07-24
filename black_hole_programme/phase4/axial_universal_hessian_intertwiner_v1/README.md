# Universal Hessian and axial factor-intertwiner certificate

This package certifies three exact statements.

1. Modulo the four-dimensional Euler boundary/corner term, the pure-Weyl
   Hessian about any Ricci-flat background factors through the linearized
   Ricci tensor.
2. A nondegenerate restriction of the inherited Hermitian form that contains
   a null Einstein line is necessarily indefinite.
3. For the Schwarzschild axial `ell=2` scalar factors and every fixed real
   `omega>0`, no nonzero rational differential intertwiner exists in either
   direction between the spin-two and spin-one Regge--Wheeler modules.

The imported projective-cocycle certificate then gives the conditional
corollary that a rational local involution cannot assign opposite signs to
the two layers of the generic non-split spin-two extension.

Run:

```bash
python3 produce.py
python3 verify.py
python3 -m unittest -v test_structure.py
```

This package does not exclude nonlocal or pseudodifferential intertwiners,
does not identify a Mannheim dynamical `C` operator, and does not prove a
positive quantum state space.
