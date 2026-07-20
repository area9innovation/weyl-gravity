# Smooth active-current radicals on candidates 17 and 20

The candidate-17 and candidate-20 active resonance carriers are products of
two third-transvectant kernels.  Their positive and negative `q`-branch node
forms have opposite signs, so current nondegeneracy is not inherited from the
ambient branch blocks.

The action-derived branch normalization and the exact parity pencil make the
two transvectant eigenchannels current-orthogonal.  The two node transforms
are not scalar multiples: if (D=\operatorname{diag}(1,3)), then
`Q^T D Q=6 I`, while `P^T D P` is diagonal with two unequal positive entries.
An independent nonzero rescaling in each eigenchannel gives exactly

```text
P S = Q diag(1/4,-1/4),
(P S)^T D (P S) = 3 I/8.
```

Thus both channels reduce to the same normalized positive-to-negative current
coefficient ratio `1/16` without identifying their original normalizations.
In either normalized channel take

```text
f = (1,0,0,0,1),       g = (1,0,1,0,1).
```

This is a smooth point of `T3(f,g)=0`: the three-equation Jacobian has rank
three.  With positive-to-negative current coefficient ratio `1/16`, the
seven-dimensional tangent Gram has rank six.  An exact radical is

```text
delta f = (0,1/4,0,1/4,0),
delta g = (0,1,0,1,0).
```

It is tangent to both fixed norm levels and orthogonal to both node-phase
directions, so it survives projectivization.  The base angular norms are
`2` and `13/6`, making the corresponding absolute-current occupation ratio

```text
x_positive / x_negative = 13/192.
```

That rational ratio lies strictly inside both exact scalar cones.  On
candidate 17 it is obtained by a positive combination of active ray `R3`
and automatic ray `R1`; on candidate 20 by a positive combination of active
ray `R2` and `R1`.  The displayed even, reflection-symmetric angular vectors
have zero moments for all three rotations, and `m=0` spectators realize the
remaining occupations.  Hence both witnesses lie in the exact bounded
second-order fibre product and have all five stabilizer moment maps zero.

The conclusion is a scoped no-go for the proposed topology method: neither
active variety is a global symplectic orbifold under the restricted current,
even on its smooth locus.  The smooth-orbifold connected-fibre theorem cannot
be applied globally.  A presymplectic degeneracy-divisor analysis or further
quotient is required.  Candidate 18 remains separate and open.

## Verification

The deterministic producer, a separately implemented algebraic verifier and
three focused unit tests pass.  The verifier reconstructs the two parity
transforms, their unequal diagonal current weights and exact channel
normalization; it also rebuilds the third-transvectant Jacobian, tangent Gram,
radical and both scalar-ray mixtures from upstream certificates.  The
fail-closed atlas generator and verifier pass with 100 focused atlas tests.
Paper 13 builds in three `pdflatex` passes (27 pages); the final two passes
have no warnings, undefined references or box errors.

Verification on 2026-07-20 passed the producer, independent verifier and
three focused tests.  The direct action-current shell audit, transvectant
Jacobian/radical calculation and two exact scalar-cone lifts are reproduced
from content-addressed inputs.
