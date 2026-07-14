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
              /                               \
             v                                 v
 exact metric/curvature slots          finite global pair g[0] + g[3]
             |                                 |
 action B=C1^# C1 + chirality                  +--> H3/Taub geometric
             |                                      identification open
             v
 smooth Bach quotient = Wgeom,+^sm + Wgeom,-^sm
             |
             v
 symbolic E/A/L intertwiners + same-block metric preimages
             |
             v
 raw polynomial metric BV -- p,j,s -- measured K defects
             |
             +--> exact cross-energy cyclic form and I^# I=1
             +--> complete centered HPL test: Q_H=d_CE
             +--> all-energy Taub/moment map from D + two B2 seeds
             |
 residual CE + canonical ghost pairing + explicit closed-S3 BFV choice
             |
             v
exact N=0,1,2 centered algebraic cohomology
             |
             v
H^4_res=span{W+^2,W-^2}, G_res=I2
             |
             v
descent + Euler--Lagrange map -> I1 dynamic + I1 topological
             |
             v
minimal field BV dictionary + gauge/nonminimal contraction
             |
             v
zero-mode suspension + positive-frequency state polarization
             |
             v
infinite-index energy-mode Krein--Fock completion
             |
             v
closed Qbar + bounded off-center Cartan contraction
             |
             v
completed H^4=span{W+^2,W-^2}, G=I2
```

The residual cohomology is exact under the explicitly selected full residual
conformal gauging.  The smooth metric-to-geometric-curvature bridge and its
finite positive-energy `E/A/L` realization are exact.  A second polynomial
calculation starts from metric/ghost/antifield rows, measures the noncompact
homotopy defects, constructs the cross-energy cyclic form, verifies the full
centered HPL transfer, and reproduces the centered ranks and `I2`.  The
closed-universe BFV choice and all-energy Taub normalization are explicit
certificates rather than hidden assumptions.  The minimal field dictionary,
specified gauge-fixed contraction, zero-mode suspension, polarized state
ledger, and field pairing transfer close the classical algebraic chain.  The
normalized energy modes now also have a certified infinite-index Krein--Fock
completion with closed residual BRST operator, closed range, and unchanged
centered cohomology.  Finite jets remain independent convention checks.
Treating `D` as gauge is a declared physical choice; if it is retained as the
cylinder Hamiltonian, this is not the relevant quotient.  A covariant
metric-field Sobolev/distributional completion remains open.

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
3. the exact classical algebraic BV--BFV identification and its natural
   infinite-index energy-mode Krein--Fock completion with closed residual
   operator;
4. the interpretation as candidate physical states under full residual
   conformal gauging.

## Claim-status table

| Claim | Status | Exact boundary |
| --- | --- | --- |
| `C1 K = 0`, `B_lin K = 0`, `K^# B_lin = 0`, formal self-adjointness | Exact formal/local theorem | Smooth formal domain with boundary terms removed |
| `B_lin = C1^# C1` in the repository action convention | Exact on the conformally flat cylinder | Formal-adjoint factorization, not a positivity factorization |
| `C1^# star C1 = 0` | Exact complex identity | Published four-dimensional deformation complex; repository script independently checks both signatures in its flat-symbol conventions |
| `H_def^q(R x S3) = (g,0,0,g,0)` | Exact smooth global theorem | Flat BGG fine resolution, trivial adjoint local system, and ordinary cohomology of `S3`; not a machine-derived or completed-Hilbert theorem |
| `ker B_lin / im K = Wgeom,+^sm + Wgeom,-^sm` | Exact smooth equivariant theorem | Uses global exactness, `B=C1^#C1`, and Lorentzian chirality; the separate energy-mode completion does not turn this into a covariant metric Sobolev theorem |
| Algebraic `E/A/L` cylinder realization | Exact symbolic theorem | Full coordinate `C1 h` at symbolic `n`, nonzero pivots, Hodge chirality, `C1^#C1h=0`, parity, same-block metric preimages, and character exhaustion |
| Polynomial detour quotient dimensions `10,40,82,136,202` | Exact for homogeneous degrees 2--6 | Euclidean finite jets only |
| Raw polynomial metric-BV retract | Exact through the complete centered buffer | Includes ghost, metric, equation-antifield and identity-antifield rows; noncompact defects are explicitly homotopic, not zero |
| Strict residual action induced from raw BV rows | Exact in energies 2--5 | All 16 `[K,P]` brackets; physical-row higher HPL terms vanish |
| Raw cross-energy cyclic form | Exact through energies 2--5 | Unique adjacent-energy contravariant recursion, expected `+E,-A,-L` inertia, cyclic raw `p,j,s`, and dressed `I^#I=1`; not an analytic field-domain theorem |
| Complete centered HPL transfer | Exact in the centered physical window | 555 allowed ordered pairs of all 15 generators on source energies 2--4; `p Delta s Delta j=s Delta s Delta j=0`, hence `Q_H=d_CE` |
| End-to-end metric-to-residual ranks | Exact algebraic integration | Vacuum `116+291=407`, one particle `520+2102=2622`, two particle rank `53/55` |
| Raw transferred parity/representative form | Exact in the centered two-class block | Parity `(-1,+1)`, raw Gram `diag(5/64,5)`, normalized representative Gram `I2` |
| Fifteen conformal-Killing zero modes | Exact global theorem and finite certificate | `H_def^0 = g`; independently recovered as the low-degree gauge-map kernel |
| Degree-three adjoint BGG sector | Exact as a 15-dimensional global cohomology group | Its geometric identification with the independently normalized oscillator Taub sector remains open |
| On-shell `W_+ + W_-` character and E/A/L inventory | Exact geometric/algebraic identification | Character and stable module action plus the all-level cylinder-preimage theorem |
| Stable proper-conformal reduced coefficients and `J`-adjoint action | Exact cutoff-stable module construction | Top buffer shell is not treated as a finite representation |
| Hamiltonian/Taub moment-map normalization | Exact symbolic all-energy reconstruction | `D` is derived from the quadratic Noether Hamiltonian; two independent direct `B^(2)` curvature seeds fix the common scale and equivariance generates all six stable families; not fifteen separate curvature integrations |
| Closed-universe residual BFV choice | Exact declared boundary model | Boundaryless `S3`, zero surface-charge rank, all 15 reducibilities constrained, and `D` included; the alternative retaining `D` is represented separately |
| Cartan homotopy reduction to total compact degree zero | Exact theorem | Requires `D` to be a residual gauge generator |
| Vacuum `H^4=0` | Exact literature theorem | Trivial coefficient module: `H*(so(4,2);C)=Lambda(u3,u5,u7)` |
| One-particle centered `H^4=0` | Exact cutoff-complete rank certificate | Global residual complex on the one-particle Weyl module |
| Two-particle centered `H^4=span{W_+^2,W_-^2}` | Exact cutoff-complete rank certificate | Global residual complex; incoming space is empty |
| Residual CE pairing `I2` | Exact in the algebraic and energy-mode completed residual complexes | Canonical complementary-degree `(4,7,4)` pairing plus exact field/raw transfer; vertex classes, not a positive particle Hilbert space |
| One-particle Krein completion | Exact energy-mode theorem | Hilbert `l2` majorant and block fundamental symmetry `+E,-A,-L`; infinite positive and negative index, hence not Pontryagin |
| Bosonic Krein--Fock completion | Exact energy-mode theorem | `Gamma_s(J_1)` on the normalized symmetric Fock completion; algebraic Fock is dense |
| Closed completed residual BRST operator | Exact maximal block theorem | Every total compact-degree block is finite; finite block support is a graph core; `Qbar` is closed and nilpotent |
| Completed cohomology and range | Exact | Bounded `iota_D/delta` gives closed off-center range; the centered block is finite and unchanged, so completed `H4=C2` and `G=I2` |
| Descent to `C^2` and `C Ctilde` | Exact residual/local descent | Lorentzian `i` phase is convention-dependent |
| Dynamical representative quotient `I1` | Exact locally | Pontryagin is only locally variationally trivial; global theta effects retained |
| Full field-theoretic pure-Weyl local-plus-residual BV/BFV result | Conditional corollary | Requires identifying the certified algebraic polynomial cyclic complex with the complete chosen gauge-fixed field-theory BV domain, with no extra rows or domain effects |
| Physical-state interpretation | Choice-dependent | Requires a boundary/gauge principle that treats all 15 generators, including `D`, as gauge |
| Quantum nilpotency, anomaly cancellation, interaction unitarity | Not claimed | Reserved for a separate quantum project |

## Included positive certificates

| Certificate | Machine output used in the paper |
| --- | --- |
| `verify_conformal_detour_action.py` | action normalization and formal/finite scalar detour identities |
| `verify_conformal_bgg_bridge.py` | signature-aware `C1^# star C1=0`, cylinder topology, chiral split, and unique bottom four-ghost scalar |
| `verify_conformal_cylinder_preimages.py` | symbolic all-energy `E/A/L` metric preimages, full Weyl/Bach tensors, chirality, pivots, parity, and dimension regressions |
| `verify_conformal_cylinder_bgg_blocks.py` | all-energy BGG split normal forms, dimension identities, and off-shell complex/factorization rails |
| `verify_conformal_free_bv_complex.py` | complete split minimal/nonminimal free-BV rows and exact CKV projector |
| `verify_conformal_cyclic_bv_retract.py` | compact-equivariant split cyclic contraction and isometry |
| `verify_conformal_residual_bfv_bridge.py` | intrinsic `4+7+4` residual algebra, Cartan identity, and top-form ghost pairing |
| `verify_conformal_raw_bv_transfer.py` | raw polynomial `p,j,s`, measured noncompact defects, strict induced brackets, and vanishing physical HPL corrections |
| `verify_conformal_cross_energy_pairing.py` | unique all-adjacent-energy contravariant form, exact inertia, raw cyclic contraction, and dressed isometry |
| `verify_conformal_full_hpl_transfer.py` | complete ordered-generator HPL correction test in the centered window |
| `verify_conformal_metric_to_residual_integration.py` | end-to-end metric-BV to residual CE ranks, parity split, and normalized representative `I2` |
| `verify_conformal_closed_universe_bfv.py` | explicit boundaryless-`S3` BFV constraint choice and alternative physical-`D` policy |
| `verify_conformal_taub_moment_map_all_levels.py` | direct `D` Hamiltonian, two direct quadratic Bach seeds, and exact all-energy equivariant Taub kernels |
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
verify_conformal_cylinder_preimages.py --claim-complete-harmonic-complex
verify_conformal_cylinder_bgg_blocks.py --claim-raw-coordinate-basis
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
verify_conformal_free_bv_complex.py --claim-full-conformal-cyclic-transfer
verify_conformal_cyclic_bv_retract.py --claim-full-so42-equivariance
verify_conformal_residual_bfv_bridge.py --claim-transferred-pure-weyl-pairing
verify_conformal_raw_bv_transfer.py --claim-strict-sdr
verify_conformal_cross_energy_pairing.py --claim-full-bv-pairing
verify_conformal_metric_to_residual_integration.py --claim-complete-bv-bfv-pairing
verify_conformal_closed_universe_bfv.py --claim-universal-D-gauging
verify_conformal_taub_moment_map_all_levels.py --claim-all-block-direct-curvature
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
- the physical interpretation of the explicitly selected closed-universe
  decision to gauge the residual cylinder conformal group;
- the identification and normalization of `H_def^3` as the dual BFV/Taub
  sector;
- integration of the common-core unbounded Lie-algebra representation to a
  global `SO(4,2)` representation;
- equivalence between the certified energy-mode completion and a covariant
  Lorentzian metric-field Sobolev or Green-hyperbolic complex;
- any quantum anomaly or interaction conclusion.

## Review focus

The highest-value remaining referee questions are:

1. Does a fully specified Lorentzian gauge-fixed metric Bach/BV complex have
   a covariant Sobolev or Green-hyperbolic completion equivalent to the
   certified energy-mode Krein completion?
2. Is the degree-three adjoint BGG group exactly the dual BFV/Taub charge
   sector geometrically, independently of the direct Noether/Taub
   normalization already certified?
3. How do distributional, spacelike-compact, or alternative boundary
   conditions change the fixed-time state complex?
4. Should the Pontryagin class remain in the residual vertex space for the
   intended cylinder boundary conditions, even though it is removed from the
   local Euler--Lagrange quotient?
5. Is the explicitly selected closed-`S3` BFV boundary problem the intended
   physical formulation, or should `D` instead remain a global Hamiltonian?
6. Do the unbounded common-core conformal generators satisfy an appropriate
   global integrability theorem, if such a group action is required?

After the literature/referee review, the programme overview was updated to
show Paper VII as a residual-cohomology branch from Paper IV rather than a
seventh step after the Paper V--VI interaction branch.  The README remains
the general programme entry point; the detailed implementation state is
tracked in `bridge/README.md`.

The post-paper implementation work is frozen separately in
`bridge/README.md`.  All five finite algebraic sprints are complete: the
all-energy same-block curvature preimages, full raw BV rows, cross-energy
cyclic retract, residual BFV/HPL transfer, and all-energy Taub comparison all
have exact certificates.  The remaining project is the field-theoretic and
analytic identification stated above; additional cutoff growth is explicitly
not a substitute for it.
