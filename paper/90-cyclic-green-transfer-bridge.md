# From Green-hyperbolic complexes to conformal detours

*Bridge note for Lorentzian PDE, Green-hyperbolic-complex, and BGG/detour
geometry researchers. Status: theorem-extraction draft, 17 July 2026.*

## 1. Their object and the unresolved question

Benini, Musante, and Schenkel define a Green-hyperbolic complex through
retarded and advanced Green homotopies, prove uniqueness up to a contractible
space of choices, identify the causal quasi-isomorphism, and compare covariant
and fixed-time Poisson structures up to homotopy
([arXiv:2207.04069](https://arxiv.org/abs/2207.04069)). Gover, Somberg, and
Souček construct formally self-adjoint Yang--Mills detour complexes and obtain
conformal BGG-related complexes from tractor connections on Bach-flat
four-manifolds
([arXiv:math/0606401](https://arxiv.org/abs/math/0606401)). Neither scope is
being challenged here.

Our question is constructive: if a hyperbolic tractor/prolonged parent is
reduced to a fourth-order detour complex by differential contractions,
homological perturbation, and finite support-local shears, what hypotheses
ensure that retarded/advanced homotopies, cyclic adjoints, and current pairings
descend together?

```text
hyperbolic tractor parent       support-local cyclic SDR       detour/Bach complex
       15/60/60/15          ------------------------------>        4/9/9/4
             |                                                     |
       Green homotopies                                      transferred Green
       and parent current                                     and current pairing
             +------------------ exact comparison ----------------+
```

## 2. Exact dictionary

| Item | Green-hyperbolic/detour language | This project | Conversion or caveat |
|---|---|---|---|
| Differential | cochain differential | classical BV--BFV differential $q_1$ | Degree and sign conventions are fixed by the odd pairing. |
| Propagation | retarded/advanced Green homotopy | $\Lambda_\pm$ on compact or spacelike-compact support | These are chain homotopies, not an inverse of the isolated Bach operator. |
| Reduction | quasi-isomorphism or contraction | cyclic differential SDR plus curved HPL and shears | Every shear is finite order and support-local. |
| Geometric parent | bundle complex with connection | adjoint-tractor/Yang--Mills parent and curvature prolongation | The concrete theorem uses conformal flatness of the cylinder. |
| Reduced object | Green-hyperbolic complex | metric Bach detour/BV complex | The reduced central operator need not have scalar principal symbol. |
| Pairing | differential pairing and Poisson structures | odd BV pairing, Green current, and residual pairing | Equality is transported up to the declared chain homotopy. |
| Boundaries | globally hyperbolic support categories | $\mathbb R\times S^3$, no timelike boundary | Boundary flux is a separate theorem. |

## 3. Reproduced benchmark

The shared benchmark is the Green-homotopy identity and its causal difference.
On the complete 386-row prolonged cylinder complex, the repository verifies
coefficientwise that the retarded and advanced degree-minus-one maps satisfy
the chain-homotopy equations on the declared support categories. Their
difference induces the compact-to-global quasi-isomorphism, and temporal
cutoffs recover the fifteen conformal-Killing endpoint classes without
duplication. The direct current calculation transports the normalized
$H^4$ pairing to $I_2$.

This is the concrete analogue of the abstract causal quasi-isomorphism and
Poisson-compatibility statements. The benchmark is reproduced by:

```bash
python3 symbolic/verify_conformal_final_covariant_transport.py
python3 symbolic/verify_conformal_covariant_H4_proof_ledger.py --check --guards
```

The exact claim and release rail are documented in
[Paper 8](08-conformal-covariant-causal-transport.pdf) and its
[reproduction guide](../notes/conformal-publication-reproduction.md).

## 4. Added result

> **Concrete transfer theorem.** On the declared conformal-cylinder complex,
> the support-local cyclic contraction from the tractor/prolonged parent to
> the metric detour complex transfers retarded and advanced Green homotopies,
> their support properties, the causal quasi-isomorphism, and the current
> pairing. No canonical Green inverse of the isolated fourth-order metric
> operator is required.

The proof factors the construction into curvature prolongation, exact
tractor-to-BGG contraction, filtered homological perturbation, finite local
shears, and cyclic adjoint transport. Each factor has an explicit inverse or
homotopy identity and a support ledger. Generality is currently `G2`: complete
on one Lorentzian background. The abstract theorem with background-uniform
hypotheses is not yet frozen.

## 5. Consequence in their language

The example supplies a large, coefficient-level fourth-order gauge complex in
which Green hyperbolicity belongs to the complex even though a preferred
same-bundle scalar-principal factorization of its middle operator is excluded.
For detour geometry, it adds a Lorentzian propagation layer to the tractor/BGG
construction. For Green-hyperbolic complexes, it suggests a practical closure
criterion under cyclic differential SDRs rather than only an existence
definition.

## 6. Scope boundary

This note does **not** establish the abstract transfer theorem on arbitrary
globally hyperbolic manifolds. It does not cover timelike boundaries,
interactions, a Hadamard state, time-ordered products, or the quantum master
equation. The surviving $H^4$ classes are centered deformation classes, not
one-particle gravitons. A second detour consumer is still required to separate
the reusable hypotheses from cylinder-specific identities.

## 7. One useful question for adjacent experts

> Is support-preserving **cyclic** transfer already implied by the published
> Green-hyperbolic-complex hypotheses when the contraction contains
> finite-order differential shears, or is an additional wavefront/support or
> pairing-compatibility hypothesis necessary? A counterexample would be as
> useful as a positive abstraction theorem.

## Reproducibility receipt

```text
source papers: arXiv:2207.04069v2; arXiv:math/0606401v2
project source: Paper 8 artifact-ready snapshot and current master
verification: commands in section 3
dependency tag: LORENTZIAN-CAUSAL
generality level: G2_COMPLETE_ONE_BACKGROUND
lifecycle state: THEOREM_EXTRACTION
claim flag: CONCRETE_CYCLIC_CAUSAL_TRANSFER_CERTIFIED
open fields: abstract hypotheses; second consumer; boundary version
```
