# Extra fourth-order modes: axial current and polar module audits

*Bridge note for conformal-gravity, higher-derivative quantization, and
Einstein-from-conformal researchers. Status: compact classical theorem,
17 July 2026.*

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
classical current direction lie? The axial block now answers the full current
question; the polar block supplies an independent off-shell equation-module
comparison whose direct current remains the next gate.

```text
H^0(Einstein--Maxwell)  --injects-->  H^0(Weyl--Maxwell)
          |                                |
          | standard image                 +--> Q_extra = two axial directions
          |                                +--> two polar equation directions
          |                                |
          +---------- direct Lee--Wald matrix ---------+
                    image signs (1,1), extra signs (2,0)
                            full axial signature (3,1)
```

## 2. Exact dictionary

| Item | Adjacent usage | This project | Conversion or caveat |
|---|---|---|---|
| Theory | pure conformal gravity or Einstein branch | tuned Weyl--Maxwell versus Einstein--Maxwell | Matter and compact flux are part of the fixture. |
| Background | dS/EAdS, flat Fock vacuum, or higher-derivative vacuum | $\mathbb R\times S^1\times S^2$ product with fixed $U(1)$ bundle | No conformal continuation to an asymptotic vacuum is assumed. |
| Extra mode | fourth-order pole/Jordan/Fock excitation | quotient $Q_{\rm extra}=H^0_{WM}/i_*H^0_{EM}$ | Quotient solution directions are not yet particles. |
| Gauge | BRST physical-state quotient or boundary selection | local Diff $\times$ Weyl $\times U(1)$, before final residual quotient | Boundary selection is not identified with gauge quotienting. |
| Form | Dirac, $PT$, or Fock inner product | classical covariant Lee--Wald current | A classical sign is not a quantum norm. |
| Selection | boundary condition or quartet mechanism | compact harmonic regularity and fixed bundle | Causal boundary admissibility is open. |

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
```

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
harmonic norms. This is not yet a polar current theorem: the direct polar
Lee--Wald form, ungauged BV/Noether lift, and residual descent remain open.

## 5. Consequence in their language

The result does not choose between $PT$, Fock--BRST, or boundary-selected
quantization. It says that any comparison must account for an explicit
classical carrier space in both parities. In the axial block, “extra branch”
and “negative direction” are demonstrably not synonymous; the polar current
will test whether that separation persists. A successful boundary or quantum
prescription must explain which standard and extra compact directions survive
its own quotient and why its inner product is the transported form appropriate
to that state space.

For Einstein-from-conformal work, this is a Lorentzian/nonlinear complement:
linear Einstein inclusion holds, but the identity inclusion is not symplectic
and selected real tangents fail the second-order compact Taub test. That does
not refute the EAdS/dS boundary theorem; it asks whether its selection is
causally preserved and symplectically appropriate in real time.

## 6. Scope boundary

The results are `LOCAL-ALGEBRAIC/REDUCED-MODE` on a compact product
background. They are not a positive-frequency Hilbert norm, a BRST/Fock
theorem, a $PT$ metric comparison, a quantum ghost result, or an S-matrix
statement. The polar extra current and ungauged lift, final residual quotient,
literal second expansion of the four-dimensional action density, and
causal/asymptotic boundary phase spaces remain open. The compact negative
direction may be removed, retained, or reinterpreted by those later gates.

## 7. One useful question for adjacent experts

> Is there an admissible Lorentzian boundary or BRST selection that removes
> the negative Einstein-image master direction while treating the two
> positive extra directions consistently, and can that selection be expressed
> as a causal symplectic subquotient rather than a condition imposed at both
> temporal ends?

**Reproducibility receipt.** Sources: arXiv:1105.5632v2,
arXiv:2109.12743v1, arXiv:2202.08298v2. Certificates:
`AXIAL_LEE_WALD_COMPLETION`, `POLAR_PHYSICAL_COMPLETION`; verification commands
are in section 3. Tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`. Open: polar
current/lift, residual descent, causal boundaries, and quantum state.
