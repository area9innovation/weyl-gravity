# Exact finite-operator closure of ten empty cells

**Result:** `FOUNDATIONAL_FINITE_OPERATOR_TEN_CELL_CLOSURE_V1`

**Lifecycle:** `SUFFICIENCY_PROVED`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

## Outcome

Ten emitted NOT_MAPPED cells can be classified. Six receive a genuine finite interaction under Hilbert or Krein realizations, two receive a constructive finite-corner state representation and probability rule, one receives a complete parity-preserving correction-space classification for the fixed two-qubit model, and one receives only a pieces-level regulated-product result. Nine are LOCAL_RESULT and one is PIECES_ONLY. Every conclusion remains scoped to named finite matrices.

This audit exploits an exact relation that the earlier migration pass did not
yet certify: the labelled Gaussian-rational matrices are simultaneously finite
arrays, bounded operators on the named finite Hilbert space, and—after adding
the displayed `J`—operators on a named finite Krein space. This is an
object-level realization, not an equivalence of carrier categories.

## Ten coordinate decisions

| # | Coordinate | New status | Exact reason | Boundary |
|---:|---|---|---|---|
| 1 | `CLASSICAL_STANDARD × HILBERT_OPERATOR × INTERACTION_CONSTRUCTION` | `LOCAL_RESULT` | The named M_4(Q(i)) Hamiltonian H=Z tensor Z is a bounded operator on C^4, is not a sum of one-body terms, and exactly maps a product state to a state with reduced density I/2. | This is one finite two-qubit interaction, not a Weyl-gravity vertex, continuum interaction, scattering construction, or thermodynamic limit. |
| 2 | `CONSTRUCTIVE_COMPUTABLE × HILBERT_OPERATOR × INTERACTION_CONSTRUCTION` | `LOCAL_RESULT` | The named M_4(Q(i)) Hamiltonian H=Z tensor Z is a bounded operator on C^4, is not a sum of one-body terms, and exactly maps a product state to a state with reduced density I/2. Every operation is a finite Gaussian-rational algorithm. | This is one finite two-qubit interaction, not a Weyl-gravity vertex, continuum interaction, scattering construction, or thermodynamic limit. |
| 3 | `FINITE_DISCRETE × HILBERT_OPERATOR × INTERACTION_CONSTRUCTION` | `LOCAL_RESULT` | The named M_4(Q(i)) Hamiltonian H=Z tensor Z is a bounded operator on C^4, is not a sum of one-body terms, and exactly maps a product state to a state with reduced density I/2. | This is one finite two-qubit interaction, not a Weyl-gravity vertex, continuum interaction, scattering construction, or thermodynamic limit. |
| 4 | `WEAK_CHOICE_ZF × HILBERT_OPERATOR × INTERACTION_CONSTRUCTION` | `LOCAL_RESULT` | The named M_4(Q(i)) Hamiltonian H=Z tensor Z is a bounded operator on C^4, is not a sum of one-body terms, and exactly maps a product state to a state with reduced density I/2. The labelled finite construction invokes no choice operation. | This is one finite two-qubit interaction, not a Weyl-gravity vertex, continuum interaction, scattering construction, or thermodynamic limit. |
| 5 | `CLASSICAL_STANDARD × KREIN_INDEFINITE × INTERACTION_CONSTRUCTION` | `LOCAL_RESULT` | On the same finite carrier, J=Z tensor I and H=Z tensor Z satisfy H^sharp=H; the exact entangling evolution is therefore a genuine scoped Krein interaction. | This is one finite two-qubit interaction, not a Weyl-gravity vertex, continuum interaction, scattering construction, or thermodynamic limit. J-self-adjointness alone is not a physical-state or unitarity theorem. |
| 6 | `WEAK_CHOICE_ZF × KREIN_INDEFINITE × INTERACTION_CONSTRUCTION` | `LOCAL_RESULT` | The labelled finite J and interaction H obey H^sharp=H by exact matrix arithmetic and require no choice operation. | This is one finite two-qubit interaction, not a Weyl-gravity vertex, continuum interaction, scattering construction, or thermodynamic limit. No infinite Krein completion is inferred. |
| 7 | `CONSTRUCTIVE_COMPUTABLE × KREIN_INDEFINITE × STATE_REPRESENTATION` | `LOCAL_RESULT` | The explicit J-even finite corner P defines rho=P and omega_P(T)=Tr(PTP)/Tr(P); all entries and normalization are computable rationals. | This represents a named finite companion-Hilbert positive state, not every Krein state or an interacting physical state. |
| 8 | `CONSTRUCTIVE_COMPUTABLE × KREIN_INDEFINITE × PROBABILITY_RULE` | `LOCAL_RESULT` | For the certified finite Krein process fixture, the computable corner rule yields exact probabilities 9/25, 16/25, and 0, summing to one. | The rule is conditional on the five finite-corner hypotheses and is not an unconditional probability rule for arbitrary Krein operators. |
| 9 | `FINITE_DISCRETE × HILBERT_OPERATOR × COUNTERTERM_CLASSIFICATION` | `LOCAL_RESULT` | For the declared two-qubit parity P=Z tensor Z, the sixteen Pauli words form a complete Hermitian operator basis and exactly eight commute with P; these eight span every parity-preserving Hermitian correction. | This is a complete counterterm-space classification only for the fixed finite two-qubit model and declared parity, not for Weyl gravity, locality, power counting, or a continuum limit. |
| 10 | `FINITE_DISCRETE × HILBERT_OPERATOR × RENORMALIZED_PRODUCTS` | `PIECES_ONLY` | All 256 products of Pauli basis operators close exactly up to phases in {1,-1,i,-i}; finite-cutoff products and traces are therefore defined without coincident-point singularities. | A regulated finite product is only an ingredient. No subtraction prescription, regulator-independent limit, microlocal extension, or continuum renormalized product is constructed. |

## Exact controls

The independent checker reconstructs all sixteen two-qubit Pauli words over
Gaussian rationals. Their Hilbert--Schmidt Gram matrix is `4 I`, so they form
a complete operator basis. The interaction has
`i[Z tensor Z, X tensor I]=-2 Y tensor Z`, and its displayed finite-time
output has reduced density `I/2`. With `J=Z tensor I`, it also satisfies
`H^sharp=H`.

Exactly eight Pauli words commute with the declared parity `P=Z tensor Z`;
they span every parity-preserving Hermitian correction in this fixed model.
All 256 basis products close up to `1,-1,i,-i`. That latter fact is deliberately
graded `PIECES_ONLY`: cutoff products do not become continuum renormalized
products by a change of vocabulary.

The constructive Krein corner independently reproduces probabilities
`9/25`, `16/25`, and `0`, with sum one.

## Verification

```text
python3 foundations/build_finite_operator_ten_cell_closure.py --check
python3 foundations/check_finite_operator_ten_cell_closure.py
python3 foundations/verify_finite_operator_ten_cell_closure.py
python3 -m unittest foundations.tests.test_finite_operator_ten_cell_closure
```

## Boundaries

- This does not establish equivalence of finite exact, Hilbert, and Krein carrier classes beyond the named finite realization.
- This does not establish an infinite-dimensional or continuum interacting theory.
- This does not establish a Weyl-gravity or Bateman--Turok interaction vertex.
- This does not establish Weyl counterterm or anomaly classification.
- This does not establish a continuum renormalized product or regulator-independent limit.
- This does not establish QME restoration or residual quantum transfer.
- This does not establish a general constructive probability rule for arbitrary Krein processes.
- This does not establish a weakest mathematical base or reverse-mathematics lower bound.
- This does not establish causal propagation, empirical agreement, or a LORENTZIAN-CAUSAL result.
