# Field-theoretic BV identification

This package addresses the remaining classical claim boundary in
`paper/conformal-residual-cohomology.tex`: how the certified algebraic bulk
BV model passes through time-slice BFV reduction and positive-frequency
polarization to the residual state complex used in the paper.

The work is intentionally staged.  The first completed milestone starts
from the quadratic minimal master action and proves an exact chain
isomorphism

```text
minimal BV tangent chain  <---->  raw G -> M -> E -> I chain
```

in the complete centered energy buffer.  It keeps both conventional BV
ghost number and the suspended local tangent degree explicit.  The maps use

```text
Omega    = omega + (partial.c)/4
tau      = tr(h)/8
tau_star = 2 tr(h_star)
i_star   = -(c_star + partial(omega_star)/4)/2
```

and obey `F Q_BV = Q_raw F`, `G Q_raw = Q_BV G`, and `FG=GF=1` with exact
rational matrices.  An explicit projector and homotopy additionally prove
`Q_raw s_tr + s_tr Q_raw = P_tr`, so the raw object is the direct sum of the
trace-free detour chain and two trace/Weyl contractible pairs.  On the
inhomogeneous low-mode block the same transformation proves
`T(ker K_BV)=ker K_raw=so(4,2)`.  The generated TSV contains one row for
every raw basis vector at energies 2--5.

Run:

```bash
python3 symbolic/verify_conformal_field_bv_dictionary.py --emit
```

Outputs:

- `certificates/minimal_bv_chain.json`
- `certificates/minimal_bv_dictionary.tsv`
- `generated_latex/minimal_bv_dictionary.tex`

This milestone does **not** yet prove the full field-domain theorem.  The
second completed milestone, an implementation corollary rather than a
premise of the minimal theorem, chooses the stationary conformal-Landau fermion

```text
Psi = integral [bar_c_perp.div(h_0) + bar_omega tau]
```

and adds the full vector and scalar antighost/multiplier sectors together
with both antifield-dual pairs.  The induced unipotent canonical shear
obeys `Q_gf=T_Psi Q_ext T_Psi^-1`; transporting the direct-sum homotopy gives
exact `p_gf`, `j_gf`, and `s_gf`.  An independent low-mode certificate proves
`P_Z Q_gf=Q_gf P_Z`, `Q_gf P_Z=0`, and `rank(P_Z)=15`.

Run:

```bash
python3 symbolic/verify_conformal_gauge_fixed_equivalence.py --emit
```

This produces an exhaustive 3,094-coordinate dictionary and separate
nonminimal-pair, contraction, and zero-mode certificates under
`gauge_fixed_equivalence/certificates/`.

The third completed milestone proves the canonical bulk endpoint theorem

```text
coker(K^sharp)  ~=  (ker K)^*
```

in the exact 65-dimensional conformal-Killing chart.  It constructs the
duality matrix `Theta`, verifies `Theta K^sharp=0`, supplies an exact quotient
section, and certifies the dual compact type `4_+1 + 7_0 + 4_-1`.  A separate
role audit keeps four objects distinct: the residual ghost `c`, the BFV
momentum `b`, the `Z*`-valued moment map `mu`, and the bulk endpoint class.
The endpoint/Taub certificate composes this quotient theorem with the
existing direct `D` and proper-conformal Bach-source normalizations.

Run:

```bash
python3 symbolic/verify_conformal_dual_zero_modes.py --emit
python3 symbolic/verify_conformal_residual_bfv_roles.py --emit
python3 symbolic/verify_conformal_taub_obstruction_map.py --emit
```

The fourth completed milestone performs the selected algebraic
BV-to-BFV suspension and positive-frequency polarization.  With the endpoint
basis normalized by `Theta`, the bulk endpoint component and the canonical
BFV equation both read `Q b_a = mu_a`; hence the equivariant suspension has
`lambda=+1` in the declared symplectic and charge conventions.  The same
certificate fixes the homogeneous `(4+7+4)` ghost orientation and gives the
centered four-ghost representative unit norm.

After time-slice reduction the physical complex splits into complementary
positive- and negative-frequency Lagrangians.  Local, trace, and nonminimal
doublets contribute only their vacuum; the endpoint class is transferred
once to the BFV momentum; and the BFV momenta act as contractions on a single
ghost exterior algebra.  The resulting state complex is therefore

```text
Sym(W_+ direct-sum W_-) tensor Lambda(so(4,2)^*)
```

The matter form induced from the canonical symplectic structure is fixed by
one action-normalized energy-two comparison and then by conformal recursion.
Together with the canonical ghost orientation it gives the field-theoretic
representative Gram matrix `I_2`.

Run:

```bash
python3 symbolic/verify_conformal_zero_mode_transgression.py --emit
python3 symbolic/verify_conformal_polarized_state_complex.py --emit
python3 symbolic/verify_conformal_polarized_pairing_transfer.py --emit
```

These commands emit three JSON certificates under
`polarized_state/certificates/` and three generated LaTeX fragments.  They
complete the selected algebraic closed-cylinder BV--BFV polarization used by
the residual theorem.  Taken by themselves, they do **not** prove:

- single-row concentration of the unpolarized bulk BV tangent complex;
- continuity, closed range, or a Hilbert/Krein completion (the separate
  `analytic_completion/` theorem now supplies the natural energy-mode
  completion, but not a covariant metric-field one);
- uniqueness among alternative boundary conditions or polarizations;
- interactions, anomalies, or quantum BRST nilpotency.
