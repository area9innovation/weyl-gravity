# Energy-mode Krein completion

This directory certifies the first infinite-dimensional completion of the
classical pure-Weyl residual complex.  It completes cylinder-energy modes,
not arbitrary covariant metric fields.

The theorem has two layers:

1. the parity-complete one-particle `E/A/L` module and its bosonic symmetric
   Fock space have canonical infinite-index Krein completions;
2. after tensoring the finite residual ghost factor, the algebraic BRST
   differential closes to a maximal block-direct-sum operator.  A bounded
   Cartan homotopy contracts every nonzero total compact degree, so completed
   cohomology is forced into the unchanged finite centered block.

The result is

```text
H^4_completed = span([W_+^2], [W_-^2]),   G_completed = I_2.
```

These are two classical ghost-dressed vertex classes, not a two-state
graviton Hilbert space.

## Proof architecture

### One particle

The Hilbert majorant declares the normalized cylinder basis orthonormal:

```text
H_1 = l2-direct-sum_{n>=2} H_n.
```

The bounded block-diagonal involution is `+1` on `E` and `-1` on `A,L` in
both chiralities.  Its positive and negative eigenspaces are both
infinite-dimensional, so the correct classification is an infinite-index
Krein space, not a Pontryagin space.  The weighted energy norms
`sum_n (1+n)^(2s) ||u_n||^2` provide the common Sobolev scale used for the
unbounded generators.

The proper conformal coefficients obey the symbolic all-level estimate
`|c_family(n)| <= 2(1+n)`.  Fixed Clebsch--Gordan component maps are exact
partial weighted permutations of norm at most one.  Thus `K+` and `K-` are
finite-band matrix-weighted shifts of energy order one.  Their minimal
finite-support realizations are closable; energy truncations are graph
cores; and their closures equal the maximal square-summability domains.
The equality `(closure K-)^sharp = closure K+` includes equality of maximal
domains—it is not inferred from a formal matrix adjoint.

The Lie brackets are asserted only on the common finite-energy invariant
core.  We do not infer a globally exponentiated `SO(4,2)` representation.
This boundary matters for unbounded Lie-algebra representations; see
[Jorgensen and Tian](https://arxiv.org/abs/1406.6966).

### Bosonic Fock and ghosts

The Fock Hilbert space is `Gamma_s(H_1)` and its fundamental symmetry is
the genuine bosonic second quantization `Gamma_s(J_1)`.  The certificate
checks normalized symmetric occupation states, not merely unsymmetrized
tensor powers.

The residual exterior algebra is finite-dimensional and receives its own
positive Hilbert topology.  The state-space fundamental symmetry is
`Gamma_s(J_1) tensor 1`.  The centered middle-determinant insertion remains
a bounded complementary-degree cohomological pairing with normalized
four-ghost overlap one.  It is deliberately not advertised as a
nondegenerate Krein metric on the entire ghost algebra.

### Finite total-degree blocks

The matter generating series is

```text
product_{n>=2} (1-q^n)^(-dim H_n).
```

Residual ghost compact degrees lie in `[-4,4]`.  For fixed total degree
`delta`, matter energy therefore belongs to a finite interval.  Fixed matter
energy bounds particle number by `N <= E/2`, uses only the finitely many
one-particle blocks `n <= E`, and has finitely many partitions.  Hence every
total-degree block is finite-dimensional.

For `delta=0`, matter energy is at most four.  The exact dimensions are:

```text
matter Fock: E=0:1, E=1:0, E=2:10, E=3:40, E=4:137
total centered block: 103296
ghost numbers 3,4,5: 727, 3084, 8532
```

The last three numbers are exactly the sums of the already-certified
vacuum, one-particle, and two-particle algebraic coefficient blocks.

### Closed BRST operator and Cartan homotopy

Each total-degree restriction `Q_delta` is a finite nilpotent matrix.  The
completed operator is its maximal Hilbert direct sum, with domain
`sum_delta ||Q_delta psi_delta||^2 < infinity`.  Componentwise convergence
proves closedness, total-degree truncation proves the graph-core statement,
and blockwise nilpotency proves both domain preservation and `Qbar^2=0`.

Off center, define `h_delta=iota_D/delta`.  Exterior contraction is a
norm-one operator and nonzero `delta` is integral, so `||h||<=1`.  The
domain estimate

```text
||Q_delta h_delta psi_delta||
  <= ||psi_delta|| + ||h_delta|| ||Q_delta psi_delta||
```

proves `h Dom(Qbar) subset Dom(Qbar)` and extends the Cartan identity to
`Qbar h + h Qbar = 1-P_0` on the actual maximal domain.  It follows that
the off-center image equals the closed kernel.  The centered image is
finite-dimensional, hence the total image is closed and ordinary and
reduced cohomology agree.

## Reproduce

```bash
python3 symbolic/verify_conformal_analytic_completion.py --emit --guards
```

Generated theorem statements are under `analytic_completion/generated/`;
machine-readable proof summaries are under
`analytic_completion/certificates/`.

## Deliberate boundary

This package by itself does not prove a covariant Sobolev or distributional
theorem for the metric Bach/BV complex.  The companion
`covariant_completion/` package now proves the reduced Lorentzian
tensor/vector Cauchy--Sobolev realization, the exact ghost biwave, an exact
ordinary-derivative four-row symbol witness, and an exact $66$-to-$30$
Fourier-complex retract with support-local formulas.  The curved lower-order
witness/retract table, the
complete covariant/Cauchy pairing comparison, Hadamard states, and an
integrated conformal-group representation remain outside that theorem.  A
direct same-bundle metric factorization is optional.  Green-hyperbolic operators are
stable under direct sums and composition
([Bär](https://arxiv.org/abs/1310.0738)), while Green-hyperbolic complexes
provide retarded/advanced homotopies and covariant/fixed-time comparisons
([Benini, Musante, and Schenkel](https://arxiv.org/abs/2207.04069)).  The
known conformal higher-spin factorization on `S^1 x S^3`, including the Weyl
graviton, is relevant evidence but is not itself that Lorentzian theorem
([Beccaria, Bekaert, and Tseytlin](https://arxiv.org/abs/1406.3542)).
