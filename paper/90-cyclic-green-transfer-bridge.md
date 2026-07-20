# From Green-hyperbolic complexes to conformal detours

*Bridge note for Lorentzian PDE, Green-hyperbolic-complex, and BGG/detour
geometry researchers. Status: sharp abstract transfer theorem certified with
an exact toy, the full conformal-cylinder construction, and curved unit
Nariai as direct consumers, 20 July 2026.*

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

> **Abstract cyclic causal-transfer theorem.** Let $(C,q_C)$ support-locally
> and cyclically deformation-retract onto $(E,q_E)$ through $(i,p,h)$.  If
> $E$ has advanced and retarded Green homotopies, then
> \[
> \Lambda_{C,\pm}=h+i\Lambda_{E,\pm}p
> \]
> are advanced and retarded Green homotopies on $C$.  Their same-sided
> support and complementary-degree cyclic adjoint relation are preserved.
> The property is also closed under finite direct sums and finite-order
> support-local cyclic shears with finite-order inverses.

The proof is algebraic once endpoint propagation exists:
\[
q_C\Lambda_{C,\pm}+\Lambda_{C,\pm}q_C
=(1-ip)+i(q_E\Lambda_{E,\pm}+\Lambda_{E,\pm}q_E)p=1.
\]
Support follows because $i,p,h$ do not enlarge support.  Taking the graded
adjoint proves advanced/retarded reversal from
$i^\sharp=p$ and the pairing-derived degreewise sign involutions:
\[
h^\sharp=\Sigma_C h\Sigma_C^{-1},\qquad
\Lambda_{E,+}^\sharp=\Sigma_E\Lambda_{E,-}\Sigma_E^{-1}.
\]
Thus no uniform scalar sign is assumed across all degrees.

The same cyclic SDR also transfers an already constructed parent homotopy
downward:
\[
\Lambda_{E,\pm}=p\Lambda_{C,\pm}i,
\qquad
q_E\Lambda_{E,\pm}+\Lambda_{E,\pm}q_E
=p(q_C\Lambda_{C,\pm}+\Lambda_{C,\pm}q_C)i=1_E.
\]
This is the direction used by differential tractor/BGG compression.

The sharp version also makes the causal-difference and pairing statements
explicit.  Since the local contraction term is independent of the causal
side,
\[
\Delta_C:=\Lambda_{C,+}-\Lambda_{C,-}
=i(\Lambda_{E,+}-\Lambda_{E,-})p=i\Delta_Ep.
\]
On the compact-to-spacelike-compact support complexes this gives
\[
[\Delta_C]=[i_{\rm sc}]\,[\Delta_E]\,[p_{\rm c}].
\]
Thus the full causal map is a quasi-isomorphism whenever the endpoint map is.
Moreover, \(i^\sharp=p\) yields the representative-level Green-pairing
identity
\[
\langle f,\Delta_Cg\rangle_C
=\langle pf,\Delta_Epg\rangle_E.
\]
An endpoint Green-current comparison therefore transfers on cohomology.

These statements and their hypotheses are now sharp rather than merely
sufficient.  Seven exact rational counterexamples separately show failure
after dropping the chain maps, deformation identity, retraction, support
locality, inclusion/projection adjointness, endpoint adjoint reversal, or
fixed-sign intertwining.  The normalizations \(h^2=hi=ph=0\) are identified
correctly as strong-retract side conditions, not ingredients of the one-step
chain calculation.  Likewise global hyperbolicity, absence of timelike
boundary, finite rank, and filtration nilpotence are stated with their precise
replaceable alternatives.

The machine-readable sharp theorem, independent replay, and counterexample
ledger are recorded in the
[sharp theorem certificate](../d_quotient_classical/certificates/GREEN_HYPERBOLIC_CYCLIC_TRANSFER_THEOREM_V1.json).

The content-addressed first consumer is the Berger gravity--clock complex:

```text
54 = 28 algebraic + 26 causal,
Lambda54,+/- = S_cl + iota_cl Lambda26,+/- pi_cl.

64 = 28 algebraic + (26 gravity-clock + 10 Maxwell),
Lambda64,+/-
  = S64 + iota64 (Lambda26,+/- direct-sum LambdaM,+/-) pi64.
```

The exact certificate and independent replay are
[`ABSTRACT_CYCLIC_CAUSAL_TRANSFER`](../d_quotient_classical/certificates/ABSTRACT_CYCLIC_CAUSAL_TRANSFER.json).
New applications must first satisfy the strict
[`consumer contract`](../d_quotient_classical/schema/abstract-cyclic-causal-transfer-consumer-v1.schema.json),
which requires typed operator domains, boundary conditions, pairing-derived
sign data, the exact cyclic SDR, causal-input Green data, and finite local inverses
for all shears.  The accepted Berger adapter is
[`BERGER_ABSTRACT_CAUSAL_TRANSFER_CONSUMER`](../d_quotient_classical/certificates/BERGER_ABSTRACT_CAUSAL_TRANSFER_CONSUMER.json).
The theorem is background-uniform as a conditional statement. The prior
portable-consumer rail certifies three scoped `G2` consumers: the Berger lift
above, a non-cylinder parent-to-endpoint descent on Minkowski, and a curved
Nariai parent-detour-to-metric descent. The sharp certificate additionally
hash-consumes the original conformal-cylinder construction as a direct
same-background consumer. The Minkowski consumer doubles the flat
adjoint-tractor detour with opposite normalization, applies a cyclic triangular
flavor shear, and descends the parent Hodge homotopy through the exact flat
differential BGG retract. Its proof and portable adapter are
[`MINKOWSKI_DOUBLED_ADJOINT_TRACTOR_MIXED_DETOUR`](../d_quotient_classical/certificates/MINKOWSKI_DOUBLED_ADJOINT_TRACTOR_MIXED_DETOUR.json)
and
[`MINKOWSKI_DOUBLED_ADJOINT_TRACTOR_CAUSAL_TRANSFER_CONSUMER`](../d_quotient_classical/certificates/MINKOWSKI_DOUBLED_ADJOINT_TRACTOR_CAUSAL_TRANSFER_CONSUMER.json).
The mixed unary presentation has a nonzero off-diagonal block, but is linearly
equivalent to two free copies; it is a portability test, not an interacting
model.

The Nariai consumer is the first substantial curved portability test. Its
repaired ten-block parent-detour cone has degree ranks
`15/140/140/15`, hence 310 components in total, and retracts cyclically and
support-locally onto an independently certified 26-component metric Bach
endpoint. Exact operator-polynomial replay verifies all ten blocks,

```text
Lambda_310,+/- = H + I Lambda_metric,+/- P,
Q_310 Lambda_310,+/- + Lambda_310,+/- Q_310 = 1_310,
P Lambda_310,+/- I = Lambda_metric,+/-.
```

The advanced/retarded support and complementary-degree adjoint relation are
preserved. The certificate and independent replay are
[`NARIAI_REPAIRED_310_ALL_ROW_GREEN_TRANSFER_V1`](../d_quotient_classical/certificates/NARIAI_REPAIRED_310_ALL_ROW_GREEN_TRANSFER_V1.json)
and its [result-boundary report](../d_quotient_classical/reports/nariai-repaired-310-all-row-green-transfer.md).
This closes one curved single-background `G2` gate; it is not a uniform
open-family theorem. No open `G3` background family has yet been proved to
satisfy the analytic hypotheses uniformly.

The earlier conformal-cylinder construction remains the motivating detour
example:

> **Concrete transfer theorem.** On the declared conformal-cylinder complex,
> the support-local cyclic contraction from the tractor/prolonged parent to
> the metric detour complex transfers retarded and advanced Green homotopies,
> their support properties, the causal quasi-isomorphism, and the current
> pairing. No canonical Green inverse of the isolated fourth-order metric
> operator is required.

Its proof factors the construction into curvature prolongation, exact
tractor-to-BGG contraction, filtered homological perturbation, finite local
shears, and cyclic adjoint transport. Each factor has an explicit inverse or
homotopy identity and a support ledger.  The sharp theorem certificate now
hash-consumes the complete 386-row homotopy, causal quasi-isomorphism, and
Green-current comparison without rerunning their producers.  This closes the
standalone conformal-cylinder consumer while keeping it distinct from the
flat Minkowski and curved Nariai carriers.

## 5. Consequence in their language

The example supplies a large, coefficient-level fourth-order gauge complex in
which Green hyperbolicity belongs to the complex even though a preferred
same-bundle scalar-principal factorization of its middle operator is excluded.
For detour geometry, it adds a Lorentzian propagation layer to the tractor/BGG
construction. For Green-hyperbolic complexes, it suggests a practical closure
criterion under cyclic differential SDRs rather than only an existence
definition.

## 6. Scope boundary

The abstract result is conditional: it does **not** establish endpoint Green
hyperbolicity on a proposed background. It does not cover timelike boundaries,
interactions, a Hadamard state, time-ordered products, or the quantum master
equation. The surviving $H^4$ classes are centered deformation classes, not
one-particle gravitons. Flat Minkowski and curved Nariai now supply two
non-Berger consumers, but uniform `G3` background dependence and
timelike-boundary domains remain open.

## 7. One useful question for adjacent experts

> Can the same consumer contract be verified uniformly on a nontrivial open
> family of curved backgrounds, including stable operator domains and
> degreewise Green estimates?

## Reproducibility receipt

```text
source papers: arXiv:2207.04069v2; arXiv:math/0606401v2
project source: Paper 8 artifact-ready snapshot and current master
verification: commands in section 3
dependency tag: LORENTZIAN-CAUSAL
generality level: ABSTRACT_CONDITIONAL_THEOREM; G0 EXACT FIXTURE; SCOPED G2 CONSUMERS
lifecycle state: SHARP_ABSTRACT_THEOREM_WITH_TOY_CYLINDER_AND_CURVED_CONSUMERS
claim flag: GREEN_HYPERBOLIC_CYCLIC_TRANSFER_THEOREM_V1
open fields: G3 family; boundary version; Hadamard transfer
```
