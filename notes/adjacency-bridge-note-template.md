# Two-page adjacency bridge note

Use this template before contacting an adjacent group or turning a bridge into
a paper section. The note should be understandable without the rest of this
repository and should normally fit on two pages excluding the reproducibility
receipt.

## Title

Name their familiar object and the layer being added. Avoid project-internal
gate names in the title.

## 1. Their object and the unresolved question

- Cite the precise theorem, construction, or fixture being used.
- State its original hypotheses and conclusion accurately.
- Identify one question that the source leaves open and that our machinery can
  actually address.
- State explicitly what the source does not claim; do not create a conflict
  where the scopes merely differ.

## 2. Exact dictionary

| Item | External convention | This project | Conversion or caveat |
|---|---|---|---|
| action and curvature sign | | | |
| fields and real form | | | |
| gauge group and residual symmetries | | | |
| generator \(D,H,P_0,\ldots\) | | | |
| couplings and global charges | | | |
| boundary/initial data | | | |
| state or cohomology object | | | |
| symplectic/inner product | | | |
| quantum regulator and measure | | | |

Do not merge generators because they have similar names. Do not identify a
Fock state, BV class, centered deformation class, or asymptotic state without
an explicit intertwiner.

## 3. Reproduced benchmark

Give one equation, mode, charge, coefficient, amplitude, or Green identity
from the external work and reproduce it in both conventions. Include:

- the smallest input fixture;
- exact or controlled analytic arithmetic;
- the expected output;
- an independent command or notebook entry;
- hashes and dependency tag.

If the benchmark does not reproduce, stop and report the convention mismatch
before drawing a new conclusion.

## 4. Added result

State one theorem or normalized obstruction. It should have this shape:

> Under hypotheses ..., the external object ... admits/fails ... because ... .

Provide the proof skeleton and point to the minimal certificate. Label the
generality level and lifecycle state. Distinguish an on-shell inclusion,
off-shell chain map, causal theorem, nonlinear closure, and quantum theorem.

## 5. Consequence in their language

Explain what changes for the adjacent programme without requiring its authors
to accept the \(D\)-quotient or this repository's interpretation. Examples:

- a detour complex inherits retarded/advanced homotopies;
- a boundary-selected branch is or is not causally preserved;
- a fixed-charge tangent violates a Taub constraint;
- a standard anomaly coefficient does or does not reach the \(D\)-defect;
- a positive metric does or does not descend through BRST and the first
  interaction.

## 6. Scope boundary

List the nearest stronger claims that are **not** established. At minimum
separate:

- fixture versus open background class;
- reduced mode versus support-local complex;
- Euclidean spectral versus Lorentzian causal;
- linear versus nonlinear;
- local anomaly classification versus restored QME;
- boundary selection versus gauge quotient.

## 7. One useful question for the adjacent experts

Ask one falsifiable question that could break or strengthen the bridge. It
should concern a convention, missing hypothesis, counterexample, or extension,
not request general endorsement.

Example:

> Is the support-preserving cyclic transfer used here already implied by your
> Green-hyperbolic-complex hypotheses, or does your framework admit a
> counterexample when the reduction contains differential shears?

## Reproducibility receipt

```text
source paper/version:
source equations/pages:
external convention commit:
project source commit:
input hashes:
verification command:
elapsed time:
test tier:
dependency tag:
generality level:
lifecycle state:
claim flag:
known open fields:
```
