# Causal cyclic Berger D-Cartan contraction through arity two

The complete 54-row advanced/retarded chain contractions solve the unary
Cartan equation.  For cyclic transfer, first average a unary primitive with
its convention-correct cyclic adjoint.  The result remains a contraction but
has support in the two-sided causal hull, as it must.

With this cyclic unary primitive, the binary source

```text
A_D^(2) = [q2,iota_D^(1)]
```

is both closed and cyclic.  A raw causal primitive is supplied by the Green
contraction.  Apply the finite cyclic Reynolds projector

```text
Cyc_3 = (I+tau+tau^2)/3
```

with the frozen BV/Koszul conventions.  Since `Cyc_3` commutes with the BV
cochain differential and fixes the cyclic source,

```text
delta Cyc_3(R) = -A_D^(2).
```

This is not merely a formal sign placeholder.  The frozen odd Darboux pairing
has 27 negatively oriented dual slots.  The convention

```text
(-1)^(dual(second)+degree(first)*degree(second))
```

was evaluated on all 25,543 degree-zero triples of the actual 54-row layout;
the product around every three-cycle is `+1`, so the concrete Koszul action
really defines a `C3` projector on every admissible component.

This closes the full four-dimensional arity-two D-Cartan problem on all 54
rows at the rational Berger fixture.  The precise support statement is
two-sided causal-hull support—not separate retarded cyclicity.  Arity three,
Hadamard data, QME restoration and quantum claims remain open.
