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

That hash freezes the residual cohomology results on which the first
drafting pass was based.  The global BGG bridge revision begins from paper
snapshot commit

```text
c471b99f5e3708e692b1c25238f6272c9e29b48f
```

and adds one theorem-level literature input plus a convention/topology
certificate.  The distinction matters: the published flat-BGG
fine-resolution theorem proves the global smooth exactness, while the new
script audits the repository's Lorentzian star, adjoint, topology, chiral
split, and ghost-grading conventions.  It does not machine-prove the BGG
theorem.

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
Gover--Peterson/Cap flat BGG theorem + M ~ S3 topology
                             |
                             v
       H_def^(0,1,2,3,4) = (g,0,0,g,0)
              /                              \
             v                                v
 exact metric and curvature slots      finite global pair g[0] + g[3]
             |                                |
 action B=C1^# C1 + chirality                 +--> open BFV/Taub dual
             |                                     identification and norm
             v                                            |
 smooth Bach quotient = Wgeom,+^sm + Wgeom,-^sm           |
             |                                            |
             v                                            |
 algebraic cylinder realization (conditional)             |
 E/A/L intertwiner + finite-mode metric potentials        |
             |                                            |
      +------+----------------+                           |
      |                       |                           |
      v                       v                           |
residual CE complex      invariant form J_conf            |
      |                       |                           |
      v                       |                           |
Cartan homotopy reduction    |                           |
      |                       |                           |
      v                       |                           |
exact N=0,1,2 centered cohomology                         |
      +-----------------------+                           |
      |                                                   |
      v                                                   |
H^4_res = span{W+^2,W-^2}, G_res=I2                      |
      |                                                   |
      v                                                   |
descent + Euler--Lagrange map                             |
      |                                                   |
      v                                                   |
I1 dynamical + I1 topological                            |
                                                          |
finite polynomial jets (degrees 2--6) --------------------+
  independent convention/regression audit                 |
                                                          v
                                    filtered local/residual bicomplex
                                    + full SO(4,2)-equivariant cyclic split
                                    + strictness and row control
                                    + residual BFV polarization
                                                          |
                                                          v
                             conditional full local-plus-residual BV result
```

The right branch through residual cohomology is exact under full residual
conformal gauging.  The smooth local metric-to-geometric-curvature bridge is
also exact.  Its restriction to finite cylinder modes, the full cyclic BV
transfer, and the residual BFV polarization remain conditional.  Finite jet
agreement is an independent audit of conventions and low levels, not the
proof of smooth or algebraic-mode exactness.  Treating `D` as gauge is a
physical choice; if it is retained as the cylinder Hamiltonian, this is not
the relevant quotient.

## Priority positioning

Hamada and collaborators already established the cylinder conformal
algebra, the residual BRST framework, the product of four proper-conformal
ghosts, the weight-four scalar condition, and a Weyl-square state.  The
draft claims novelty only for the parity-complete **absolute** exhaustion:
the incoming-image calculation, vacuum and one-particle vanishing, exactly
two surviving two-particle classes, their normalized residual CE pairing,
and the dynamical/topological split.

Four statements are kept separate throughout the manuscript:

1. the exact algebraic residual theorem;
2. the exact smooth Bach-to-geometric-curvature theorem;
3. the conditional transfer to the strict pure-Weyl algebraic BV complex;
4. the interpretation as candidate physical states under full residual
   conformal gauging.

## Claim-status table

| Claim | Status | Exact boundary |
| --- | --- | --- |
| `C1 K = 0`, `B_lin K = 0`, `K^# B_lin = 0`, formal self-adjointness | Exact formal/local theorem | Smooth formal domain with boundary terms removed |
| `B_lin = C1^# C1` in the repository action convention | Exact on the conformally flat cylinder | Formal-adjoint factorization, not a positivity factorization |
| `C1^# star C1 = 0` | Exact complex identity | Published four-dimensional deformation complex; repository script independently checks both signatures in its flat-symbol conventions |
| `H_def^q(R x S3) = (g,0,0,g,0)` | Exact smooth global theorem | Flat BGG fine resolution, trivial adjoint local system, and ordinary cohomology of `S3`; not a machine-derived or completed-Hilbert theorem |
| `ker B_lin / im K = Wgeom,+^sm + Wgeom,-^sm` | Exact smooth equivariant theorem | Uses global exactness, `B=C1^#C1`, and Lorentzian chirality; algebraic positive-energy exactness and analytic completions remain separate |
| Polynomial detour quotient dimensions `10,40,82,136,202` | Exact for homogeneous degrees 2--6 | Euclidean finite jets only |
| Fifteen conformal-Killing zero modes | Exact global theorem and finite certificate | `H_def^0 = g`; independently recovered as the low-degree gauge-map kernel |
| Degree-three adjoint BGG sector | Exact as a 15-dimensional global cohomology group | Its identification and normalization as the BFV/Taub dual sector remain conditional |
| On-shell `W_+ + W_-` character and E/A/L inventory | Exact abstract coefficient-module theorem | Its all-level curvature intertwiner and finite-mode metric potentials are the algebraic-cylinder hypothesis |
| Stable proper-conformal reduced coefficients and `J`-adjoint action | Exact cutoff-stable module construction | Top buffer shell is not treated as a finite representation |
| Hamiltonian moment-map normalization | Exact through source energy four | A finite jet; its Taub interpretation is tested in selected kernels, not a general local-BV theorem |
| Cartan homotopy reduction to total compact degree zero | Exact theorem | Requires `D` to be a residual gauge generator |
| Vacuum `H^4=0` | Exact literature theorem | Trivial coefficient module: `H*(so(4,2);C)=Lambda(u3,u5,u7)` |
| One-particle centered `H^4=0` | Exact cutoff-complete rank certificate | Global residual complex on the one-particle Weyl module |
| Two-particle centered `H^4=span{W_+^2,W_-^2}` | Exact cutoff-complete rank certificate | Global residual complex; incoming space is empty |
| Residual CE pairing `I2` | Exact in the chosen residual complex | Canonical complementary-degree pairing with the normalized `(4,7,4)` polarization; vertex classes, not a particle Hilbert space or yet the transferred pure-Weyl BV pairing |
| Descent to `C^2` and `C Ctilde` | Exact residual/local descent | Lorentzian `i` phase is convention-dependent |
| Dynamical representative quotient `I1` | Exact locally | Pontryagin is only locally variationally trivial; global theta effects retained |
| Full pure-Weyl local-plus-residual BV result | Conditional corollary | Requires algebraic cylinder realization, a full `SO(4,2)`-equivariant cyclic BV transfer with row control, and the selected residual BFV polarization and normalization |
| Physical-state interpretation | Choice-dependent | Requires a boundary/gauge principle that treats all 15 generators, including `D`, as gauge |
| Quantum nilpotency, anomaly cancellation, interaction unitarity | Not claimed | Reserved for a separate quantum project |

## Included positive certificates

| Certificate | Machine output used in the paper |
| --- | --- |
| `verify_conformal_detour_action.py` | action normalization and formal/finite scalar detour identities |
| `verify_conformal_bgg_bridge.py` | signature-aware `C1^# star C1=0`, cylinder topology, chiral split, and unique bottom four-ghost scalar |
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
verify_conformal_bgg_bridge.py --claim-machine-proof-of-bgg
verify_conformal_bgg_bridge.py --claim-completed-domain
verify_conformal_bgg_bridge.py --claim-algebraic-mode-exactness
verify_conformal_bgg_bridge.py --claim-eal-intertwiner
verify_conformal_bgg_bridge.py --claim-taub-identification
verify_conformal_bgg_bridge.py --claim-completed-bv-transfer
verify_conformal_bgg_bridge.py --claim-pure-weyl-bfv-pairing
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
- the Gover--Peterson/Cap flat-BGG fine-resolution theorem and its global
  sheaf-cohomology consequence;
- the nonlinear Weyl-square Euler--Lagrange identity and the assumptions in
  the Boulanger--Henneaux uniqueness theorem;
- the semisimple trivial-coefficient Lie-algebra cohomology theorem;
- the physical decision to gauge the residual cylinder conformal group;
- exactness of the BGG sequence on the algebraic positive-energy metric-mode
  complex and the all-level `E/A/L` curvature intertwiner;
- the identification and normalization of `H_def^3` as the dual BFV/Taub
  sector;
- the full pure-Weyl BV zero-mode transfer;
- extension to an infinite Hilbert/Krein completion;
- any quantum anomaly or interaction conclusion.

## Review focus

The highest-value remaining referee questions are:

1. Does the smooth BGG isomorphism restrict to the `D`-finite,
   `SO(4)`-finite cylinder category without secular or infinite-mode metric
   potentials, and do the explicit `E/A/L` curvatures give the required
   graded intertwiner?
2. Is the residual ghost polarization appropriate for strict pure-Weyl BV
   after the canonical `g[0] + g[3]` global pair is split?
3. Is the degree-three adjoint BGG group exactly the dual BFV/Taub charge
   sector, and does one normalized component fix the equivariant map?
4. Does the explicit filtered bicomplex inventory all local ghost/antifield
   rows and higher transferred operations capable of entering or leaving
   `(p,q)=(4,0)`?
5. Should the Pontryagin class remain in the residual vertex space for the
   intended cylinder boundary conditions, even though it is removed from the
   local Euler--Lagrange quotient?
6. What boundary or background-independence principle makes cylinder time
   translation a gauge generator rather than a global Hamiltonian?
7. Which algebraic result, if any, extends continuously to the intended
   Hilbert or Krein completion?

After the literature/referee review, the programme overview was updated to
show Paper VII as a residual-cohomology branch from Paper IV rather than a
seventh step after the Paper V--VI interaction branch.  The README remains
untouched in this snapshot.

The post-paper implementation work is frozen separately in
`bridge/README.md`.  Its blocking deliverable is an exact all-energy,
same-cylinder-block right inverse of the linearized Weyl map on every
`E/A/L` tower.  Additional cutoff growth is explicitly not a substitute for
that theorem.
