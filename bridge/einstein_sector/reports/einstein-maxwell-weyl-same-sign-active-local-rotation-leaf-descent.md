# Local lifted-rotation descent through current leaves

Candidates 17, 18 and 20 have smooth fixed-occupation strata on which the
node-phase-reduced Lee--Wald form has constant but nonmaximal rank.  The
current radical and the lifted rotational constraint are two different
structures and must not be silently identified.

Let `R=ker(Omega_U)` on one such stratum.  The lifted diagonal `SO(3)` action
is Hamiltonian:

```text
d<mu,xi> = i_(xi#) Omega_U.
```

Consequently, for every `r` in `R`,

```text
d<mu,xi>(r) = Omega_U(xi#,r) = 0.
```

The moment map is therefore locally constant along connected radical leaves.
The rotation action preserves the closed current and hence the radical
distribution.  On every simple saturated neighbourhood, both the current and
the moment map descend to the local symplectic leaf quotient.  Imposing
`mu=0` commutes there with removing the radical:

```text
(mu^{-1}(0) intersect U_0)/R = mu_bar^{-1}(0).
```

This closes a local proof-architecture gate for every smooth
constant-corank fixed-occupation stratum of candidates 17, 18 and 20.  It
retains the common node phases until their already certified reduction,
keeps both parity channels coupled, and keeps candidate 18's ten positive
spectators.

The theorem does not prove that a complete rotation-zero fibre is connected,
construct a global Hausdorff leaf space, reduce singular strata, glue
occupations, or perform the final residual quotient.  Those remain separate
candidatewise gates.
