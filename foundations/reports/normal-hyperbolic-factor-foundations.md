# Normally-hyperbolic factor: foundations and literature atlas

**Result:** `FOUNDATIONAL_NORMAL_HYPERBOLIC_FACTOR_ATLAS_V1`

## Answer

Classical existence and strict causal support are directly established in the reviewed smooth and metric-graph literature. Computable solution operators are directly established for represented symmetric-hyperbolic systems, but the reviewed computability papers do not construct globally hyperbolic advanced/retarded Green maps. No direct second-order-arithmetic reversal or Bishop-style global Green theorem was located in the bounded search. Choice-sensitive Hilbert-space results show that the ambient operator theory cannot be treated as automatically choice-free. Exact finite graph-step Green kernels are separately certified locally.

## Framework findings

| Framework | Finding | Evidence | What is established | Boundary |
|---|---|---|---|---|
| `CLASSICAL_STANDARD` | `DIRECT_RESULT` | `baer-2015`, `muehlhoff-2010` | Cauchy existence; uniqueness; continuous dependence for symmetric hyperbolic systems; advanced/retarded Green maps for normally/prenormally hyperbolic operators; strict causal support | weakest base; choice avoidance; full Weyl BV propagator |
| `COMPUTABLE_TTE` | `DIRECT_UPPER_BOUND_IN_REPRESENTATION` | `weihrauch-zhong-2002`, `selivanova-selivanov-2013`, `selivanova-selivanov-2018` | computable wave or symmetric-hyperbolic solution operators under specified representations and regularity; effective finite-difference convergence in the stated cube systems | Bishop constructive derivability; RCA_0 proof; advanced/retarded maps on globally hyperbolic manifolds; strict causal-support computability |
| `BISHOP_CONSTRUCTIVE` | `BOUNDED_SEARCH_NO_DIRECT_THEOREM` | None assigned | No positive theorem assigned. | literature absence; impossibility; a constructive no-go |
| `REVERSE_MATHEMATICS` | `BOUNDED_SEARCH_NO_DIRECT_REVERSAL` | `brown-simpson-1986`, `humphreys-simpson-1996`, `humphreys-simpson-1999`, `brattka-2008` | nearby Banach/Hilbert principles have representation-sensitive strengths ranging from WKL_0 to stronger comprehension | an RCA_0 upper bound; a WKL_0 or ACA_0 lower bound for hyperbolic PDE |
| `ZF_WITHOUT_COUNTABLE_CHOICE` | `ADJACENT_OPERATOR_THEORY_ONLY` | `blackadar-farah-karagila-2026` | substantial Hilbert/operator theory can be developed in ZF and familiar basis behavior can fail without countable Choice | ZF construction of Sobolev spaces and Green maps; choice-free hyperbolic PDE |
| `FINITE_OR_DISCRETE` | `THREE_DISTINCT_RESULTS` | `FOUNDATIONAL_FINITE_GRAPH_WAVE_CAUSALITY_V1`, `kostrykin-potthoff-schrader-2011`, `nachtergaele-raz-schlein-sims-2007` | exact graph-step support for the local finite recurrence; strict finite propagation for specified metric-graph waves; exponential Lieb-Robinson cones for specified lattice systems | that these three support notions are equivalent; a continuum limit; Lorentzian Green support from a Lieb-Robinson tail |

## Dependency chain

| Stage | Classical | Computable | Reverse mathematics | Choice |
|---|---|---|---|---|
| globally hyperbolic spacetime, Cauchy surface, finite-rank bundle and causal relation | `USED` | `MANIFOLD_VERSION_NOT_FOUND` | `NOT_FORMALIZED` | `NOT_CLASSIFIED` |
| normally/symmetric-hyperbolic operator with domains and coefficient representation | `EXPLICIT` | `DIRECT_FOR_CUBE_SYSTEMS` | `NOT_FORMALIZED` | `ZF_HILBERT_ADJACENT_ONLY` |
| local and finite-slab energy estimate | `DIRECT` | `EFFECTIVE_ESTIMATES_IN_REPRESENTED_SYSTEM` | `NO_SUBSYSTEM_BOUND` | `NOT_CLASSIFIED` |
| global solution for compactly supported Cauchy data | `DIRECT` | `DIRECT_FOR_CUBE_SYSTEMS` | `NO_SUBSYSTEM_BOUND` | `NOT_CLASSIFIED` |
| Cauchy uniqueness | `DIRECT` | `USED_AND_EFFECTIVE_IN_SCOPE` | `NO_SUBSYSTEM_BOUND` | `NOT_CLASSIFIED` |
| continuous dependence in declared topologies | `DIRECT` | `DIRECT_IN_TTE_REPRESENTATIONS` | `REPRESENTATION_NOT_CODED` | `COMPLETION_DEPENDENCE_OPEN` |
| strict support inside the causal cone | `DIRECT` | `NOT_A_STATED_OUTPUT_OF_REVIEWED_TTE_THEOREM` | `NOT_FORMALIZED` | `NOT_CLASSIFIED` |
| advanced and retarded right/left inverses on test sections | `DIRECT` | `NOT_LOCATED` | `NOT_FORMALIZED` | `NOT_CLASSIFIED` |
| continuous extension and formal-adjoint reversal | `DIRECT` | `NOT_LOCATED` | `NOT_FORMALIZED` | `DUALITY_AND_COMPLETION_OPEN` |

## Immediate cube impact

| Coordinate | Old | New | Why |
|---|---|---|---|
| `CLASSICAL_STANDARD|HILBERT_OPERATOR|CAUSAL_PROPAGATION_GREEN` | `NOT_MAPPED` | `LITERATURE_RESULT` | Self-adjoint Hilbert-space Laplacians on metric graphs have well-posed wave evolution and strict finite propagation. |
| `FINITE_DISCRETE|HILBERT_OPERATOR|EVOLUTION_WELLPOSEDNESS` | `NOT_MAPPED` | `LITERATURE_RESULT` | The metric-graph theorem proves existence and uniqueness for the specified finite/network geometry. |
| `FINITE_DISCRETE|HILBERT_OPERATOR|CAUSAL_PROPAGATION_GREEN` | `NOT_MAPPED` | `LITERATURE_RESULT` | The same theorem proves strict finite propagation under its local boundary conditions. |
| `WEAK_ARITHMETIC|HILBERT_OPERATOR|GENERATOR_SPECTRAL_DYNAMICS` | `NOT_MAPPED` | `PIECES_ONLY` | Effective evolution and reverse functional-analysis ingredients exist, but no coded generator theorem or subsystem calibration was located. |
| `WEAK_ARITHMETIC|HILBERT_OPERATOR|EVOLUTION_WELLPOSEDNESS` | `NOT_MAPPED` | `PIECES_ONLY` | Computable solution operators are adjacent, but no second-order-arithmetic upper bound or reversal was located. |
| `WEAK_ARITHMETIC|HILBERT_OPERATOR|CAUSAL_PROPAGATION_GREEN` | `NOT_MAPPED` | `PIECES_ONLY` | Classical support and effective evolution exist separately; their combination has not been formalized over a weak subsystem. |
| `CONSTRUCTIVE_COMPUTABLE|SMOOTH_DISTRIBUTIONAL|GENERATOR_SPECTRAL_DYNAMICS` | `PRIORITY_GAP` | `PIECES_ONLY` | A represented symmetric-hyperbolic solution operator is computable, but an explicit computable generator/domain/spectral theorem is still missing. |
| `WEAK_CHOICE_ZF|HILBERT_OPERATOR|CAUSAL_PROPAGATION_GREEN` | `NOT_MAPPED` | `PIECES_ONLY` | ZF Hilbert theory and classical causal PDE are known separately; the Sobolev/Green construction has not been proved choice-free. |
| `FINITE_DISCRETE|FINITE_EXACT|CAUSAL_PROPAGATION_GREEN` | `PIECES_ONLY` | `LOCAL_RESULT` | Exact rational retarded/advanced kernels have a certified graph-step support cone on the displayed finite fixtures. |

## New primary-source corpus

| ID | Primary record | Content pin | Direct point |
|---|---|---|---|
| `baer-2015` | [Christian Bär, Green-hyperbolic operators on globally hyperbolic spacetimes, Communications in Mathematical Physics 333 (2015), 1585-1615.](https://arxiv.org/abs/1310.0738) | `879948318de8b4a5a74b52179f78120d074bc7773734b82495b6db4c363f4c99` | Normally hyperbolic wave operators are Green-hyperbolic on globally hyperbolic spacetimes; advanced and retarded maps have the declared support and extend continuously to several support classes. |
| `muehlhoff-2010` | [Rainer Mühlhoff, Cauchy Problem and Green's Functions for First Order Differential Operators and Algebraic Quantization, Journal of Mathematical Physics 52 (2011), 022303.](https://arxiv.org/abs/1001.4091) | `5854613e375d64cfddf98ced287f12a8819a21a48db4bf89f24fa8ed0040cda7` | Prenormally hyperbolic first-order operators have unique advanced and retarded Green functions and a globally well-posed Cauchy problem under the stated globally hyperbolic hypotheses. |
| `selivanova-selivanov-2013` | [Svetlana Selivanova and Victor Selivanov, Computing Solution Operators of Boundary-value Problems for Some Linear Hyperbolic Systems of PDEs, Logical Methods in Computer Science 13(4:13) (2017).](https://arxiv.org/abs/1305.2494) | `71a4628b9e151eeb444f4db3c2d87cd2ad2f7d86e404bea9b3662da570f568be` | For symmetric hyperbolic systems on a cube with computable coefficients, the Cauchy solution operator is computable in the stated TTE representations; dissipative boundary-value problems are also treated under additional hypotheses. |
| `selivanova-selivanov-2018` | [Svetlana Selivanova and Victor Selivanov, Bit Complexity of Computing Solutions for Symmetric Hyperbolic Systems of PDEs with Guaranteed Precision, 2020.](https://arxiv.org/abs/1807.03140) | `9943569bd492d28d2ad8c70b30e4f85a852fe0e5c9fc7b7e034186691fd5893c` | The symmetric-hyperbolic computability programme admits explicit bit-complexity upper bounds under the paper's representations and coefficient hypotheses. |
| `kostrykin-potthoff-schrader-2011` | [Vadim Kostrykin, Jürgen Potthoff, and Robert Schrader, Finite propagation speed for solutions of the wave equation on metric graphs, 2011.](https://arxiv.org/abs/1106.0817) | `53c5f52ca32e7b9a0839287c154109d3bc04650f1eb11ceecea195fca5d33f47` | A class of self-adjoint Laplace operators on metric graphs has existence and uniqueness for the wave equation and strict finite propagation, proved by localized energy methods. |
| `nachtergaele-raz-schlein-sims-2007` | [Bruno Nachtergaele, Hillel Raz, Benjamin Schlein, and Robert Sims, Lieb-Robinson Bounds for Harmonic and Anharmonic Lattice Systems, Communications in Mathematical Physics 286 (2009), 1073-1098.](https://arxiv.org/abs/0712.3820) | `613ff5cc8af3f7b9734a2ca1912f33624b59050204e108071c4d200285179114` | Harmonic and specified anharmonic lattice systems satisfy Lieb-Robinson bounds, including exponentially small commutators outside an effective cone for Weyl observables. |

## Bounded negative findings

The search did not locate a direct reverse-mathematical subsystem theorem or a Bishop-style globally hyperbolic Green theorem. This is a bounded corpus result, not an absence or impossibility claim.

The search screened **13 primary records** and retained **6 new records**. Queries: `reverse mathematics wave equation`; `reverse mathematics partial differential equations`; `constructive mathematics hyperbolic partial differential equations existence`; `computable symmetric hyperbolic systems`; `Choice Hilbert spaces operator theory`; `finite propagation discrete wave equation graph`.

## Reproduction

```text
python3 foundations/build_normal_hyperbolic_factor_atlas.py --check
python3 foundations/check_normal_hyperbolic_factor_atlas.py
python3 foundations/verify_normal_hyperbolic_factor_atlas.py
```

## Boundaries

- This does not establish literature completeness.
- This does not establish a weakest subsystem.
- This does not establish an RCA_0, WKL_0 or ACA_0 equivalence.
- This does not establish a Bishop-constructive globally hyperbolic Green theorem.
- This does not establish Choice avoidance for Sobolev/distribution theory.
- This does not establish a continuum limit from finite graphs.
- This does not establish a full off-shell Weyl metric BV propagator.
- This does not establish a BRST-compatible Hadamard state.
- This does not establish renormalized Lorentzian products or a Lorentzian QME.
