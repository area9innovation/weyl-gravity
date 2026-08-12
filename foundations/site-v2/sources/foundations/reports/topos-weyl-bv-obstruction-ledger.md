# Topos-internal Weyl BV: glossary before construction

**Result:** `FOUNDATIONAL_TOPOS_WEYL_BV_OBSTRUCTION_LEDGER_V0`

**Lifecycle:** `LITERATURE_SCOPED`

**Dependency:** `LOCAL-ALGEBRAIC`

## Outcome

There is a credible sequence of adjacent bridges, but there is not yet a
topos-internal Weyl-gravity BV theory. Constructive Gelfand duality replaces a
point-set commutative spectrum by a locale. Topos algebraic quantum theory
places an algebraic quantum system in intuitionistic internal logic. Synthetic
differential geometry supplies a route to formal manifolds and intuitionistic
classical general relativity. None of those results supplies the distribution,
causal, indefinite-completion, renormalization, or comparison layers needed to
compose the three programmes into Weyl QFT.

This is deliberately the first artifact prescribed for
`OP-TOPOS-WEYL-BV`: a glossary and obstruction ledger, not a formal
construction.

## Translation glossary

| Ordinary object | Candidate internal object | Present status |
|---|---|---|
| Boolean logic | Heyting internal logic | literature bridge |
| set, subset, predicate | object, subobject, generalized truth value | standard translation |
| point-set Gelfand spectrum | locale/internal localic spectrum | literature bridge |
| represented observable algebra | internal algebra assembled from contexts | literature bridge |
| smooth Lorentzian manifold | formal manifold/synthetic smooth object | literature bridge only for adjacent classical geometry |
| bundle section | internal section of an internal bundle or sheaf | candidate translation |
| finite BV algebra | internal graded algebra object and equations | candidate internalization |
| differential operator | morphism defined through selected smooth structure | open bridge |
| test functions/distributions | internal topological test object and dual | open bridge |
| retarded/advanced Green operator | solution morphism with internal causal support | open bridge |
| Krein completion | internal indefinite module/Hilbert object with symmetry | open bridge |
| state and Born probability | internal state or locale valuation | open bridge |
| BRST cohomology | internal kernel/image quotient plus comparison | candidate internalization |
| renormalized products and QME | internal renormalization data and QME equality | open bridge |
| hashes and verifier receipts | external metatheoretic evidence | external only |

The warnings in the machine result are part of the glossary. In particular,
an internal object may have no usable global points; an internal cohomology
object need not agree with cohomology of external global sections; and a localic
spectrum is neither finite nor a physical state-selection theorem.

## Obstruction DAG

The only root is selection of an ambient topos (`O1`). From it, the programme
splits into a finite algebraic rail (`O3`) and a smooth Lorentzian rail (`O2`).
The finite rail must solve internal/external cohomology comparison (`O4`). The
smooth rail must construct function spaces (`O5`), then microlocal control
(`O6`) and Green operators (`O7`). Krein/BRST completion (`O8`) uses both rails.
Physical state selection (`O9`) additionally needs the Green layer;
renormalized products (`O10`) additionally need microlocal control. Only then
can an internal QME (`O11`) and an external physical comparison theorem (`O12`)
be attempted.

`O3-FINITE-BV-ALGEBRA` is the lowest-risk candidate because finite algebraic
equations do not require topology, completion, integration, support, or causal
propagation. The external witness
`FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1` supplies a small exact presentation,
but it has **not** been internalized here.

## Literature boundary

The pinned sources support four adjacent bridges:

- Coquand–Spitters: constructive point-free commutative Gelfand duality;
- Heunen–Landsman–Spitters: a topos formulation of an algebraic quantum system;
- Henry: the non-unital/local-compact extension of constructive duality;
- Grinkevich: synthetic differential geometry as a route to intuitionistic
  models of classical general relativity.

The corpus does not contain their composition into a gauge-fixed Weyl BV
complex, a causal QFT, or a quantum master equation. The repository therefore
keeps all construction flags false.

## What this does not establish

There is no selected ambient topos, internal Weyl BV complex, constructive
distribution or wavefront theory, internal Green operator, Krein completion,
physical state, renormalized product, restored QME, or external equivalence
theorem. In particular, this artifact establishes nothing tagged
`LORENTZIAN-CAUSAL`.

The next bounded experiment is to select one ambient topos and internalize only
the fixed finite BV presentation, with a separate external/internal comparison
ledger.

## Verification

```bash
python3 foundations/check_topos_weyl_bv_obstructions.py
python3 foundations/verify_topos_weyl_bv_obstructions.py
python3 -m unittest foundations.tests.test_topos_weyl_bv_obstructions
```
