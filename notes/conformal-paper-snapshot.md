# Free conformal paper review snapshot

## Frozen scope

Manuscript:

- `paper/conformal-residual-cohomology.tex`
- generated review PDF: `paper/conformal-residual-cohomology.pdf`

Review title:

> **Residual SO(4,2) Cohomology of Free Weyl Gravity on the Conformal
> Cylinder: Cartan Homotopy, Weyl-Square Classes, and Their Residual Pairing**

Scientific input commit:

```text
e928f257c25099eb534eb34109dfc1dc6a3127a1
```

That hash freezes the research results on which the first drafting pass is
based.  The later paper-draft commit contains editorial files and the paper
runner; it does not silently strengthen the scientific input.

Environment used for the review battery:

```text
CPython 3.14.4
SymPy 1.14.0
pdfTeX 3.141592653-2.6-1.40.28 (TeX Live 2025/Debian)
```

The Python dependency is frozen in
`symbolic/conformal-paper-requirements.txt`.  File hashes are stored in
`symbolic/conformal-paper-verification.sha256`.

## One-command reproduction

From `physics/symplectic-reconstruction`:

```bash
python3 symbolic/verify_conformal_paper_free.py
```

This runs every positive certificate used by the manuscript.  For a shorter
smoke test:

```bash
python3 symbolic/verify_conformal_paper_free.py --quick
```

To add the declared overclaim guards, each of which must exit nonzero:

```bash
python3 symbolic/verify_conformal_paper_free.py --guards
```

After a positive battery has already been run, the guard-only shortcut is:

```bash
python3 symbolic/verify_conformal_paper_free.py --guards-only
```

Compile the manuscript with two ordinary passes:

```bash
cd paper
pdflatex -interaction=nonstopmode -halt-on-error conformal-residual-cohomology.tex
pdflatex -interaction=nonstopmode -halt-on-error conformal-residual-cohomology.tex
```

## Theorem dependency graph

```text
Branson--Gover detour theorem + action Hessian
                    |
                    v
   formal identities C1 K=0, B=C1^# C1
                    |
        +-----------+-------------------+
        |                               |
        v                               v
finite polynomial jets            on-shell Weyl module
(degrees 2--6)                     character + E/A/L action
        |                               |
        |                     +---------+----------+
        |                     |                    |
        |                     v                    v
        |               residual CE complex   invariant form J_conf
        |                     |                    |
        |                     v                    |
        |          Cartan homotopy reduction      |
        |                     |                    |
        |                     v                    |
        |      exact N=0,1,2 centered cohomology  |
        |                     +---------+----------+
        |                               |
        |                               v
        |                 H^4_res = span{W+^2,W-^2}, G_rep=I2
        |                               |
        |                               v
        |                    descent + Euler--Lagrange map
        |                               |
        |                               v
        |                    I1 dynamical + I1 topological
        |
        +----> open all-level Lorentzian local-kernel theorem
                              |
                 filtered local/residual bicomplex
                 + cyclic D-equivariant BV transfer
                 + row and higher-operation control
                              |
                              v
          conditional full local-plus-residual pure-Weyl corollary
```

The right branch through residual cohomology is exact under full residual
conformal gauging.  The bottom bridge is conditional.  Finite jet agreement
is evidence for that bridge, not a proof of it.  Treating `D` as gauge is a
physical choice; if it is retained as the cylinder Hamiltonian, this is not
the relevant quotient.

## Priority positioning

Hamada and collaborators already established the cylinder conformal
algebra, the residual BRST framework, the product of four proper-conformal
ghosts, the weight-four scalar condition, and a Weyl-square state.  The
draft claims novelty only for the parity-complete **absolute** exhaustion:
the incoming-image calculation, vacuum and one-particle vanishing, exactly
two surviving two-particle classes, their normalized representative Gram
matrix, and the dynamical/topological split.

Three statements are kept separate throughout the manuscript:

1. the exact algebraic residual theorem;
2. the conditional transfer to the strict pure-Weyl local BV complex;
3. the interpretation as candidate physical states under full residual
   conformal gauging.

## Claim-status table

| Claim | Status | Exact boundary |
| --- | --- | --- |
| `C1 K = 0`, `B_lin K = 0`, `K^# B_lin = 0`, formal self-adjointness | Exact formal/local theorem | Smooth formal domain with boundary terms removed; no global Lorentzian exactness inferred |
| `B_lin = C1^# C1` in the repository action convention | Exact on the conformally flat cylinder | Formal-adjoint factorization, not a positivity factorization |
| Polynomial detour quotient dimensions `10,40,82,136,202` | Exact for homogeneous degrees 2--6 | Euclidean finite jets only |
| Fifteen conformal-Killing zero modes | Exact finite certificate | Kernel of the low-degree local gauge map |
| On-shell `W_+ + W_-` character and E/A/L inventory | Exact coefficient-module theorem | Does not itself prove equality with local metric cohomology |
| Stable proper-conformal reduced coefficients and `J`-adjoint action | Exact cutoff-stable module construction | Top buffer shell is not treated as a finite representation |
| Hamiltonian moment-map normalization | Exact through source energy four | A finite jet; its Taub interpretation is tested in selected kernels, not a general local-BV theorem |
| Cartan homotopy reduction to total compact degree zero | Exact theorem | Requires `D` to be a residual gauge generator |
| Vacuum `H^4=0` | Exact literature theorem | Trivial coefficient module: `H*(so(4,2);C)=Lambda(u3,u5,u7)` |
| One-particle centered `H^4=0` | Exact cutoff-complete rank certificate | Global residual complex on the one-particle Weyl module |
| Two-particle centered `H^4=span{W_+^2,W_-^2}` | Exact cutoff-complete rank certificate | Global residual complex; incoming space is empty |
| Residual representative Gram `I2` | Exact for the normalized residual representatives | Hermitian/sesquilinear representative matrix; vertex classes, not a particle Hilbert space |
| Descent to `C^2` and `C Ctilde` | Exact residual/local descent | Lorentzian `i` phase is convention-dependent |
| Dynamical representative quotient `I1` | Exact locally | Pontryagin is only locally variationally trivial; global theta effects retained |
| Full pure-Weyl local-plus-residual BV result | Conditional corollary | Requires the stated Lorentzian kernel theorem, row inventory, strict higher-operation control, cyclic transfer, and zero-mode polarization |
| Physical-state interpretation | Choice-dependent | Requires a boundary/gauge principle that treats all 15 generators, including `D`, as gauge |
| Quantum nilpotency, anomaly cancellation, interaction unitarity | Not claimed | Reserved for a separate quantum project |

## Included positive certificates

| Certificate | Machine output used in the paper |
| --- | --- |
| `verify_conformal_detour_action.py` | action normalization and formal/finite scalar detour identities |
| `verify_conformal_detour_polynomial.py` | finite homogeneous-jet ranks and the 15-dimensional reducibility kernel |
| `verify_conformal_weyl_module.py` | Weyl character and E/A/L tower equality |
| `verify_conformal_cylinder_form.py` | uniqueness and signature of the standard invariant cylinder form |
| `verify_conformal_generator_all_levels.py` | stable reduced coefficients and conformal brackets |
| `verify_conformal_oscillator_pairing.py` | normalized one-particle form and convention conversion |
| `verify_conformal_moment_map_energy4.py` | 15-component Hamiltonian moment-map jet |
| `verify_conformal_relative_brst_weight4.py` | two-dimensional relative primary kernel and matter `I2` |
| `verify_conformal_fock_energy4.py` | complete weight-four Fock inventory and second quantization |
| `verify_conformal_global_brst_window.py` | exact absolute one- and two-particle kernel/image ranks |
| `verify_conformal_residual_ghost_pairing.py` | normalized centered residual ghost overlap |
| `verify_conformal_cartan_contraction.py` | chain-level Cartan identity and explicit homotopy |
| `verify_conformal_cartan_transfer.py` | nontrivially dressed equivariant-transfer fixture |
| `verify_conformal_cyclic_hpl.py` | exact cyclic HPL isometry fixture |
| `verify_conformal_vertex_descent.py` | weight-four state--operator descent and parity basis |
| `verify_conformal_dynamical_topological.py` | Chern--Weil transgression and rank-one dynamical quotient |

## Expected-failing guards

These are intentional rejections, not test failures.  The paper runner checks
them with `--guards`.

```text
verify_conformal_detour_action.py --require-explicit-cylinder-c1
verify_conformal_detour_polynomial.py --claim-all-levels
verify_conformal_detour_polynomial.py --claim-lorentzian-eal
verify_conformal_weyl_module.py --claim-exact-sequence
verify_conformal_generator_all_levels.py --require-infinite-module
verify_conformal_moment_map_energy4.py --require-physical-cohomology
verify_conformal_relative_brst_weight4.py --claim-absolute-cohomology
verify_conformal_fock_energy4.py --require-local-global-brst
verify_conformal_global_brst_window.py --require-local-brst
verify_conformal_global_brst_window.py --require-physical-cohomology
verify_conformal_cartan_contraction.py --claim-local-bv
verify_conformal_cartan_contraction.py --treat-d-as-physical-hamiltonian
verify_conformal_cartan_transfer.py --claim-pure-weyl-bv
verify_conformal_cyclic_hpl.py --claim-pure-weyl-bv
verify_conformal_vertex_descent.py --claim-particle-hilbert
verify_conformal_dynamical_topological.py --claim-pontryagin-globally-trivial
verify_conformal_dynamical_topological.py --claim-theta-has-no-observables
verify_conformal_dynamical_topological.py --claim-two-local-dynamics
```

## Normalization conventions

- Cylinder radius: `1`; signature: `(-,+,+,+)`.
- Compact energy: eigenvalue of `D=i partial_t` in oscillator conventions.
- `SO(4)=SU(2)_L x SU(2)_R`; parity exchanges the two factors.
- Normalized module form: `J_conf = +I_E + (-I_A) + (-I_L)`.
- Repository curvature action:
  `S_red = int sqrt(-g) (R_mn R^mn - R^2/3) = (C^2-E4)/2`.
- Residual generator compact grades: `(0^7,-1^4,+1^4)`; dual ghosts have opposite grades.
- Centered residual ghost representative: ghost number `4`, compact ghost degree `-4`, normalized overlap `+1`.
- Chiral states are ordered `(W_+^2,W_-^2)`; parity states are
  `(C^2,C Ctilde)` up to the Lorentzian self-duality phase.
- Good-prime rank field: `F_241` with
  `i->64`, `sqrt(2)->22`, `sqrt(3)->56`, `sqrt(5)->103`.

## Machine output versus interpretation

Machine-certified statements are ranks, kernels, dimensions, exact matrix
identities, character identities, symplectic/adjoint relations, the Cartan
homotopy, Chern--Weil algebra, and the displayed Gram matrices.

The following are theorem dependencies or interpretation, and are not
silently presented as machine outputs:

- the Branson--Gover all-signature formal detour theorem;
- the nonlinear Weyl-square Euler--Lagrange identity and the assumptions in
  the Boulanger--Henneaux uniqueness theorem;
- the semisimple trivial-coefficient Lie-algebra cohomology theorem;
- the physical decision to gauge the residual cylinder conformal group;
- the all-level Lorentzian local-kernel identification;
- the full pure-Weyl BV zero-mode transfer;
- any quantum anomaly or interaction conclusion.

## Review focus

The highest-value remaining referee questions are:

1. Is the residual ghost polarization appropriate for strict pure-Weyl BV
   after the conformal-Killing zero-mode split?
2. Can the all-level Lorentzian map
   `ker B_lin / im K -> W_+ + W_-` be proved without importing an elliptic
   Riemannian argument?
3. Does the explicit filtered bicomplex inventory all local ghost/antifield
   rows and higher transferred operations capable of entering or leaving
   `(p,q)=(4,0)`?
4. Should the Pontryagin class remain in the residual vertex space for the
   intended cylinder boundary conditions, even though it is removed from the
   local Euler--Lagrange quotient?
5. What boundary or background-independence principle makes cylinder time
   translation a gauge generator rather than a global Hamiltonian?

After the literature/referee review, the programme overview was updated to
show Paper VII as a residual-cohomology branch from Paper IV rather than a
seventh step after the Paper V--VI interaction branch.  The README remains
untouched in this snapshot.
