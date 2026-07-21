# Extra fourth-order modes: compact currents and black-hole endpoint tests

*Bridge note for conformal-gravity, higher-derivative quantization, and
Einstein-from-conformal researchers. Status: compact axial-and-polar classical
current theorem and scoped Schwarzschild endpoint-nonselection result,
21 July 2026.*

## 1. Their object and the unresolved question

Three adjacent programmes ask different questions. Maldacena uses a Neumann
boundary condition in asymptotically de Sitter or Euclidean anti-de Sitter
settings to select the Einstein solution in a tree-level computation
([arXiv:1105.5632](https://arxiv.org/abs/1105.5632)). Mannheim argues for a
positive $PT$-based inner product in higher-derivative gravity
([arXiv:2109.12743](https://arxiv.org/abs/2109.12743)). Kubo and Kuntz use a
BRST/Fock construction and find an indefinite transverse spin-two sector and
scattering-unitarity failure
([arXiv:2202.08298](https://arxiv.org/abs/2202.08298)). These results concern
different boundaries, state spaces, and inner products.

Our narrower classical question is prior to all three quantum conclusions:
on one compact common Einstein--Maxwell/Weyl--Maxwell background, are the
extra fourth-order roots actual gauge-quotient solution directions, are they
radical under the action-derived current, and where does the negative
classical current direction lie? The generic axial and polar blocks now answer
the full current question before final residual descent. A second, independent
Schwarzschild laboratory asks whether future-horizon analyticity and the
presently tested leading outer asymptotics force the Ricci carrier to vanish.
In the axial fixture they do not. This is an endpoint diagnostic, not a no-go
against every local causal restriction.

```text
H^0(Einstein--Maxwell)  --injects-->  H^0(Weyl--Maxwell)
          |                                |
          | standard image                 +--> Q_extra = two axial directions
          |                                +--> two polar current directions
          |                                |
          +---------- direct Lee--Wald matrix ---------+
                    image signs (1,1), extra signs (2,0)
                       full parity-block inertia (3,1)
```

## 2. Exact dictionary

| Item | Adjacent usage | This project | Conversion or caveat |
|---|---|---|---|
| Theory | pure conformal gravity or Einstein branch | tuned Weyl--Maxwell versus Einstein--Maxwell | Matter and compact flux are part of the fixture. |
| Background | dS/EAdS, flat Fock vacuum, or higher-derivative vacuum | compact $\mathbb R\times S^1\times S^2$ product with fixed $U(1)$ bundle; separately, Schwarzschild exterior | Results are compared, not identified, across these two laboratories. |
| Extra mode | fourth-order pole/Jordan/Fock excitation | quotient $Q_{\rm extra}=H^0_{WM}/i_*H^0_{EM}$ | Quotient solution directions are not yet particles. |
| Gauge | BRST physical-state quotient or boundary selection | local Diff $\times$ Weyl $\times U(1)$, before final residual quotient | Boundary selection is not identified with gauge quotienting. |
| Form | Dirac, $PT$, or Fock inner product | classical covariant Lee--Wald current | A classical sign is not a quantum norm. |
| Selection | boundary condition or quartet mechanism | compact harmonic regularity and fixed bundle; horizon analyticity and a leading-symbol test on Schwarzschild | The tested endpoints do not force the Ricci carrier to vanish; Jordan structure, metric falloff, finite asymptotic flux, and general causal selection remain open. |

The bridge lifecycle is deliberately split:

| Component | Lifecycle | Missing gate |
|---|---|---|
| Compact axial and polar Lee--Wald comparison | **Landed** | final residual descent and quantum interpretation |
| Compact charge-fibre/nonlinear comparison | **Landed in Paper 91** | all-orders and causal extension |
| Schwarzschild axial endpoint comparison | **Partial** | Jordan form, metric reconstruction, finite asymptotic flux, rigorous pairing bounds |
| Schwarzschild polar comparison | **Partial** | polar current, outer behavior, and Zerilli control |
| Lorentzian Einstein-from-conformal bridge | **Open** | differentiable exterior phase space and an admissible Einstein-sector boundary operator |

## 3. Reproduced benchmark

The current engine first reproduces the independent Einstein--Maxwell
Lee--Wald current, the repository's Bach convention, a pure-Weyl gauge kernel,
the flat transverse-traceless zero-restriction control, and exact current
conservation. It then compares the reduced self-adjoint Hessian current with a
literal variation of the four-dimensional Weyl--Maxwell curvature-momentum
current. For arbitrary $\ell\ge2$ and spherical multiplicity $m$, their
integrated currents agree up to the positive harmonic normalization
$N_{\ell m}$.

The replay commands are:

```bash
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_axial_lee_wald_completion \
  --verify bridge/certificates/einstein_maxwell_weyl_axial_lee_wald_completion.json
python3 -m bridge.einstein_sector.weyl_maxwell_axial_general_lee_wald_fixture \
  --verify bridge/certificates/weyl_maxwell_axial_general_lee_wald_fixture.json
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_polar_full_tensor \
  --verify bridge/certificates/einstein_maxwell_weyl_polar_full_tensor.json
python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_polar_full_tensor.py
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_polar_physical_completion \
  --verify bridge/certificates/einstein_maxwell_weyl_polar_physical_completion.json
python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_polar_physical_completion.py
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_polar_direct_lee_wald_completion \
  --verify bridge/certificates/EINSTEIN_MAXWELL_WEYL_POLAR_DIRECT_LEE_WALD_COMPLETION_V1.json
python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_polar_direct_lee_wald_completion.py
python3 black_hole_programme/verify_bh2a_cross_flux.py
python3 black_hole_programme/verify_bh2a_causal_disposition.py
python3 black_hole_programme/verify_bh2b_polar_split.py
python3 black_hole_programme/verify_bh2b_polar_reach.py
```

The file named `BH2A_CAUSAL_DISPOSITION` is imported only for its certified
real-frequency characteristic polynomial and formal exponent data. Its older
interpretive phrase “no local causal truncation” is not used: Paper 14's
claim map explicitly narrows that interpretation to endpoint nonselection.

## 4. Added result

> **Generic compact axial Lee--Wald theorem.** For each physical compact axial
> harmonic with $\ell\ge2$, the Weyl--Maxwell solution module strictly
> contains the Einstein--Maxwell image by two exact polarizations. The direct
> four-dimensional Lee--Wald form is nondegenerate on the extra quotient with
> signature $(2,0)$. The complete generic axial target has signature
> $(3,1)$, and its negative direction lies on one Einstein-image master
> branch rather than on either extra direction.

Algebraically, the invariant factors separate the standard Einstein master
polynomial from a doubled extra primary factor. Direct mixed Lee--Wald blocks
between the standard and extra primary shells vanish. The extra determinant is
positive throughout the physical $\ell\ge2$ domain. This rules out three
simple explanations of the extra root on this fixture: determinant
multiplicity only, local gauge, and a presymplectic radical.

The nonlinear compact test adds an important qualification. The real
$\ell=2,k=0$ extra span has a definite Taub obstruction at fixed bundle
charges, so the linearly measurable extra directions are linearization
unstable in that declared sector. This is selection by nonlinear constraint,
not disappearance from the linear current.

The independent polar calculation now establishes the corresponding
equation-level decomposition. A formally self-adjoint four-by-four target
Hessian obeys the exact polynomial Einstein square

\[
H_P S_P=J_P E_P,
\]

without dividing by momentum or either characteristic factor. On every
declared physical $\ell\geq2$ compact-momentum fibre, including $k=0$, its
invariant factors are $1,1,p,pq$. The Einstein image is the complete
$q$-primary summand, the canonical extra quotient is
$(K[\omega]/(p))^2$, and the action row weights
$(-1,2,-1,2\lambda)$ are derived from the four-dimensional variation and
harmonic norms.

The direct polar current is now independently complete. Literal variation of
the four-dimensional curvature-momentum potential, including the full
$\delta(\nabla C)$ term, produces exact coordinate matrices at
$\ell=2,3,4$. Their degree-two spectral interpolation gives the generic
current before the reduced Hessian is consulted; the result then agrees
exactly with the reduced Green form. On the two $p$-primary representatives
its Hermitian Gram determinant is

\[
9\lambda^2(\lambda-2)(9\lambda-2)
(3k^2+3\lambda-2)(6k^2+3\lambda-2)^2,
\]

which never vanishes for physical $\lambda=\ell(\ell+1)\geq6$ and real
compact momentum. The extra polar inertia is $(2,0)$, the Einstein--extra
cross block vanishes, and the complete generic polar inertia is $(3,1)$.
These agree with the axial inertia data without identifying the two parity
carriers. The omitted-$\delta(\nabla C)$ mutation is detected already by the
$\ell=2$ $(A_t,B)$ entry, where its nonzero remainder at $k=1$ is
$-7i\pi/5$. The ungauged BV/Noether lift and residual descent remain open.

The subsequent ungauged audit separates two statements. The natural local
ghost--field--equation--identity chain map exists and all its squares close.
However, it cannot be enhanced to a strict cyclic BV morphism while holding
the physical identity field inclusion and the two standard action pairings
fixed. On generic polar cohomology the cyclic defect is

\[
D=R-I=\begin{pmatrix}0&-3\lambda\\-3/2&0\end{pmatrix},
\qquad D^2=\frac92\lambda I,
\]

so it is nonradical for every physical $\lambda\ge6$. Moreover the five
connected background stabilizers are global charged symmetries, not universal
presymplectic null directions. Final residual dimensions therefore require a
separately declared common moment-map-zero derived carrier; without it they
remain undefined. This obstruction leaves corrected nonidentity maps and
cyclic chain homotopies open.

Combining both parities gives a maximal exact statement despite that
obstruction. On every separately certified harmonic stratum,

\[
0\longrightarrow H^0_{\rm EM}\longrightarrow H^0_{\rm WM}
\longrightarrow H^0_{\rm extra}\longrightarrow0
\]

is exact before global residual reduction. For a generic parity fibre the
coefficient-field dimensions are $4\to8\to4$, the pairing ranks are
$4\to8\to4$, and all three radicals vanish. This does not produce a
degreewise short exact BV sequence: the all-row object is a noncyclic mapping
cofiber, and its equation/identity maps are not injective. Nor does it produce
an after-residual sequence, because no authorized common moment-map-zero
quotient functor exists. Exactness, splitting, cyclicity and residual descent
are therefore four distinct assertions.

## 5. Independent Schwarzschild boundary test

The black-hole programme supplies a second laboratory in which boundary
admissibility is a physical part of the question rather than a compact-mode
regularity convention. For axial $\ell=2$ on Schwarzschild, it supplies three
separately typed results:

1. the Einstein/Regge--Wheeler block is symplectically null in the pure-Weyl
   action current for conjugate wave pairs;
2. controlled order-16 ingoing-series fixtures give nonzero
   Einstein--additional and additional--additional horizon pairing at
   $\omega=3/5$, $2/7$, with an independent gate at $1/2$; this is not a
   symbolic all-frequency or interval-certified theorem;
3. the curvature carrier $\psi_{ab}=\delta R_{ab}$ has a two-dimensional
   analytic ingoing horizon family for nonzero real frequency, while the
   leading outer characteristic polynomial is repeated and shares the
   Einstein characteristic.

The invariant solution-space statement is an exact sequence from Bach
solutions to the realized Ricci image, not a canonical Einstein/additional
direct sum. The repeated outer root may carry Jordan partners, and the
certificate does not yet reconstruct their metric falloff or finite flux at
null infinity. The justified conclusion is therefore

\[
\boxed{\text{horizon analyticity plus the tested leading outer symbol}
       \not\Rightarrow \delta R_{ab}=0.}
\]

This endpoint-nonselection result does not exclude every local causal
truncation. At linear order, the Cauchy restriction
$\psi|_\Sigma=\nabla_n\psi|_\Sigma=0$ propagates the Einstein kernel. Whether
that restriction is interaction-stable or selected by a differentiable
asymptotic phase space remains open.

The polar audit has now advanced one step further. The trace-coupled Ricci
carrier is exact on the certified $\ell=2$ system, and for real
$\omega\ne0$ its horizon analysis leaves a two-parameter physical
ingoing-regular family after quotienting the regular conformal-gauge
direction. Polar Lee--Wald pairing, the Zerilli benchmark, the outer Jordan
and metric analysis, stability, and ringdown remain open.

## 6. Consequence in their language

The result does not choose between $PT$, Fock--BRST, or boundary-selected
quantization. It says that any comparison must account for an explicit
classical carrier space in both parities. In both generic parity blocks,
“extra branch” and “negative direction” are demonstrably not synonymous: the
extra blocks have inertia $(2,0)$, while the negative direction belongs to the
Einstein image. A successful boundary or quantum
prescription must explain which standard and extra compact directions survive
its own quotient and why its inner product is the transported form appropriate
to that state space.

For Einstein-from-conformal work, this is a Lorentzian/nonlinear complement:
linear Einstein inclusion holds, but the identity inclusion is not symplectic
and selected real tangents fail the second-order compact Taub test. That does
not refute the EAdS/dS boundary theorem; it asks whether its selection is
causally preserved and symplectically appropriate in real time.

The Schwarzschild result sharpens that question. A Maldacena-type selection
may still define a valid sector, but ordinary horizon analyticity and the
currently tested leading outer symbol do not implement it automatically.
The missing comparison is whether a precise local differential boundary
operator or finite-flux asymptotic phase space selects the Ricci-flat kernel
while retaining a nondegenerate physical pairing. That distinction matters
whenever a Euclidean or two-boundary prescription is interpreted as a
real-time Lorentzian sector.

## 7. Scope boundary

The results are `LOCAL-ALGEBRAIC/REDUCED-MODE` on a compact product
background. They are not a positive-frequency Hilbert norm, a BRST/Fock
theorem, a $PT$ metric comparison, a quantum ghost result, or an S-matrix
statement. A strict fixed-identity cyclic polar lift is obstructed; corrected
maps or cyclic homotopies and the final residual quotient,
literal second expansion of the four-dimensional action density, and
causal/asymptotic boundary phase spaces remain open. The compact negative
direction may be removed, retained, or reinterpreted by those later gates.
The black-hole result is a `REDUCED-MODE` endpoint audit: axial $\ell=2$,
nonzero real frequency, exact horizon-carrier data, controlled flux fixtures,
and a leading asymptotic symbol. It is not `LORENTZIAN-CAUSAL`, and it is not
a theorem about complex frequencies, arbitrary multipoles, a complete metric
falloff class, the full exterior initial-boundary problem, nonlinear
stability, ringdown, Hawking states, or asymptotic particles. The polar
horizon-reach result is likewise mode-level and does not close the
outer-boundary chain.

## 8. One useful question for adjacent experts

> Is there a local differential or finite-flux Lorentzian boundary condition
> that selects the Ricci-flat kernel and yields a nondegenerate physical
> symplectic subquotient, and how does it compare with the Einstein-branch
> condition used in Euclidean AdS or de Sitter constructions?

**Reproducibility receipt.** Sources: arXiv:1105.5632v2,
arXiv:2109.12743v1, arXiv:2202.08298v2. Certificates:
`AXIAL_LEE_WALD_COMPLETION`, `POLAR_PHYSICAL_COMPLETION`,
`EINSTEIN_MAXWELL_WEYL_POLAR_DIRECT_LEE_WALD_COMPLETION_V1`,
`EINSTEIN_MAXWELL_WEYL_POLAR_UNGAUGED_BV_RESIDUAL_DESCENT_OBSTRUCTION_V1`,
`EINSTEIN_WEYL_PARITY_COMPLETE_RESIDUAL_EXACT_SEQUENCE_MAXIMAL_V1`,
`BH2A_CROSS_BLOCK_NONZERO_HORIZON_FLUX_FIXTURES`, and
the symbol/exponent payload of
`BH2A_AXIAL_CAUSAL_DISPOSITION_EXTRA_BRANCH_UNAVOIDABLE`, narrowed by the
Paper 14 claim map; the polar horizon input is
`BH2B_POLAR_EXTRA_BRANCH_REACHES_HORIZON_LINEAR_MODE_LEVEL`. Verification
commands are in section 3. Tags: `LOCAL-ALGEBRAIC` and `REDUCED-MODE`.
Open: asymptotic Jordan form, metric reconstruction, rigorous flux bounds,
polar cyclic-lift repair, moment-map-zero residual descent, full causal boundary phase spaces,
stability, and quantum state.
