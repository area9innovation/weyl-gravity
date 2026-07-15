# Classical \(D\)-quotient challenge: handoff report

## Executive status

The compact vacuum-cylinder result is **sector-dependent** on two precisely
declared phase spaces:

- On the unrestricted locally reduced linearized solution space
  \(\mathcal P_{\rm lin}\), \(D\) has a nonzero, integrable quadratic Noether
  Hamiltonian. The lowest \(E\), \(A\), and \(L\) branches provide exact
  charged examples.
- Those charged vectors do not lie in the full Taub/moment-map zero fibre and
  are obstructed as isolated tangent vectors to the selected nonlinear
  closed-universe solution space.
- On the derived full moment-map zero fibre \(\mathcal P_{\rm Taub0}\), the
  pullback of \(\mu_D\) and \(d\mu_D\) vanishes. Quotienting the corresponding
  null orbit is the Paper-VII closed-universe choice.

Thus compactness alone does not make \(D\) gauge. The zero-charge/Taub
restriction does. This conclusion is not exported to matter-coupled,
deformed, dS/AdS, or asymptotically flat phase spaces.

The first matter-clock candidate was resolved negatively but constructively.
For one real conformally coupled scalar, the invariant
homogeneous variable \(\chi=aT\) is an exact local oscillator clock with
positive improved charge. It is not a consistent nonzero background on the
exact vacuum cylinder: its stress tensor is nonzero while the cylinder Bach
tensor vanishes. Around the only compatible background, \(\bar T=0\), its
linearized Diff \(\times\) Weyl incidence vanishes. This obstructs that
candidate.

A minimal two-field replacement now works on a precisely declared homogeneous
sector. Give the two conformal scalars internal signature \((+,-)\), impose
the regular neutral conditions \(H_D=0\) and \(W\ne0\), and use their
projective angle as the clock. The opposite improved stresses cancel
componentwise, so the nonzero scalar pair and the Bach-flat cylinder solve the
coupled equations. The Wronskian \(W\) is conserved, the angle has no turning
point, and the raw two-field Diff \(\times\) Weyl incidence has determinant
\(W\). On this homogeneous zero-level phase space, \(D\) is a null direction
of the pulled-back symplectic form and is therefore `D_GAUGE`.

This is reference/Krein matter, not a positive-energy matter completion. Its
local health audit is now decisive: after Weyl reduction the ratio field keeps
a derivative term with coefficient \(-\rho^2\cos(2\theta)\). Every neutral
winding clock crosses its zero four times per compact period, so the sign
alternates and the local kinetic sector degenerates. Temporal unitary gauge
transfers this dynamics to metric/constraint rows rather than deleting it.
Thus the homogeneous reference clock remains valid, but its promotion to a
globally regular positive local matter clock is obstructed.

The first positive-sign stealth repair is now exhausted on the homogeneous
sector. With the complete quartic Weyl-invariant potential, every nonzero
stress-free trajectory requires a negative quartic and is, up to sign and
time translation, \(T=\sqrt{-2/\kappa}\sec(t-t_0)\). It has positive kinetic
sign but an unbounded potential, a turning point, and finite-time poles.
Hence no globally regular homogeneous positive-sign stealth clock exists.
The inhomogeneous extension is now classified as well.  Every nowhere-zero
clock candidate has

\[
T^{-1}=A\cos t+B\sin t+C\cdot n,
\qquad
\kappa=2(|C|^2-A^2-B^2).
\]

Every nontrivial denominator vanishes somewhere on the cylinder, and every
time-dependent member has a regular point where its gradient is spacelike or
zero.  Thus the complete standard one-field stealth-clock branch is
obstructed.

The genuinely backreacted route now has a positive result. On the static
Berger cylinder

\[
g=-dt^2+a^2(\sigma_1^2+\sigma_2^2)+c^2\sigma_3^2,
\qquad q=c^2/a^2,
\]

two standard-sign conformal scalars
\(T_1=\rho\cos(\omega t)\), \(T_2=\rho\sin(\omega t)\) solve the exact
coupled Bach--scalar equations on

\[
\frac{5-\sqrt{21}}2<q<\frac14.
\]

Their target metric is positive, their phase has timelike gradient, the
quartic potential is bounded below, and their stationary stress satisfies the
dominant energy inequalities. This passes the healthy-background gate.  The
all-row BV reduction remains open, but the fixed-coupling linearized charge
verdict is now exact.

The first charge seed shows that the phase is not a cost-free gauge marker.
The scalar pair has an exact conserved global \(O(2)\) charge

\[
Q_R=16\pi^2\alpha_Bq\sqrt{1-4q}>0,
\]

and obeys \(\mathcal L_D T=\omega RT\) on the background. This establishes
genuine clock momentum.  The pure-Weyl and improved scalar presymplectic
currents combine on the background as follows.

That structural combination is now reduced exactly to

\[
\Omega_{\rm total}(\delta,\mathcal L_D)=\omega\,\delta Q_R.
\]

The stationary background relation has nonzero \(q\)-derivative at fixed
\(\alpha_B\lambda\), so the open squashing interval is not a physical tangent
inside one theory.  More decisively, varying the exact time-dependent reduced
action before fixing the lapse gives

\[
\delta E_N=-\frac{\alpha_Bq^{3/2}}2\frac{\delta Q_R}{Q_R}.
\]

Thus every homogeneous constraint-satisfying tangent has \(\delta Q_R=0\).
Compact \(SU(2)_L\times U(1)_R\) averaging preserves both the linearized
equations and \(\delta Q_R\), so the conclusion holds for the complete smooth
fixed-coupling linearized solution space.  Hence

\[
\Omega_{\rm total}(\delta,\mathcal L_D)=0,
\qquad D_{\rm compact}=D_{\rm GAUGE}
\]

on this declared Berger phase space.  The background value \(Q_R>0\) is not
contradictory: its differential vanishes after pullback to the allowed
tangent space.

The present charge audit composes the exact reduced-mode moment map with the
already-certified Lorentzian current comparison, so it is tagged
`REDUCED-MODE` and `LORENTZIAN-CAUSAL`. This does not classify any new
boundary phase space.

## Scope and conventions

### Unrestricted linearized sector

- Field space: the \(D\)-finite \(E/A/L\) linearized solution module after
  local Diff \(\times\) Weyl reduction.
- Boundary: the closed cylinder \(\mathbb R\times S^3\); no spatial boundary
  or corner term.
- Hamiltonian normalization: the action-normalized kernel
  \(M_D=-\tfrac12 JD\).
- Interpretation: a valid charge computation on \(\mathcal P_{\rm lin}\),
  not proof of nonlinear linearizability.

### Derived Taub-zero sector

- Field space: the formal common zero fibre of all fifteen quadratic
  Taub/moment-map components, with its derived residual quotient.
- Charge: \(\iota^*\mu_D=0\) and
  \(\iota^*\iota_{X_D}\Omega=d(\iota^*\mu_D)=0\).
- Interpretation: proper gauge only after the explicit zero-charge
  restriction and quotient.

## Compact-cylinder charge receipt

The exact all-energy branch formula and lowest charged representatives are
recorded in the producer certificate referenced by
`CLASSICAL_D_QUOTIENT_STATUS.json`. The decisive examples are:

| branch | energy | \(H_D\) at unit real amplitude | radial \(\delta H_D\) |
|---|---:|---:|---:|
| \(E\) | 2 | \(-1\) | \(-2\) |
| \(A\) | 3 | \(3/2\) | \(3\) |
| \(L\) | 4 | \(2\) | \(4\) |

They establish `D_CHARGED` on \(\mathcal P_{\rm lin}\). The same certificate
records why they do not establish `D_CHARGED` on
\(\mathcal P_{\rm Taub0}\).

## Residual-complex comparison

| Complex | Mathematical status | Computation status | Current result |
|---|---|---|---|
| Absolute \(SO(4,2)\) CE complex | selected Paper-VII complex | certified baseline | centered \(H^4=\mathbb C^2\), one-particle \(H^4=0\), Gram \(I_2\) |
| \(D\) global, lowering subalgebra gauged | legal closed-subalgebra comparison | partial | exact through total \(D\)-weight four; not a physical selection theorem |
| Zero-charge transformations \(\mathfrak g_{H=0}\) | closure not established | open | no complex promoted |
| Local gauge only; residual \(SO(4,2)\) global | zero residual differential | certified | full \(E/A/L\) one-particle module survives with branch Krein signs |

Deleting only the \(D\) ghost is rejected: the remaining fourteen conformal
generators are not a Lie subalgebra. The exact obstruction is

\[
\frac14\sum_a[K^-_a,K^+_a]=2D.
\]

## Background matrix

| Setting | \(D\) charge | Cartan contraction | Causal homotopy | One-particle sector | Pairing | Einstein sector |
|---|---|---|---|---|---|---|
| Vacuum cylinder | `SECTOR_DEPENDENT` on the declared sectors | certified baseline | certified baseline | zero only in selected absolute residual \(H^4\) | \(I_2\) on centered degree-four classes | open in this challenge record |
| Cylinder + scalar clock | one-real-scalar exact-cylinder candidate `OBSTRUCTED` | `OPEN` | `OPEN` | `OPEN` | `OPEN` | `OPEN` |
| Cylinder + neutral clock pair | `D_GAUGE` on `compact_neutral_clock_pair_homogeneous` | `OPEN` | `OPEN` | `OPEN` | unrestricted reference pairing is indefinite | `OPEN` |
| Positive Berger clock | `D_GAUGE` on the smooth fixed-coupling linearized phase space | portable 34-row classical unary operator and all-row contraction onto the exact 26-row retained complex certified | full 10-metric/5-ghost scalar-biwave principal completion; curved witness and total homotopy `OPEN` | `OPEN` | helical current and complete minimal cyclic pairing exact; full transport open | `OPEN` |
| Cylinder + Yang--Mills | `NOT_TESTED` | `NOT_TESTED` | `NOT_TESTED` | `NOT_TESTED` | `NOT_TESTED` | `NOT_TESTED` |
| Weakly deformed background | `NOT_TESTED` | `NOT_TESTED` | `NOT_TESTED` | `NOT_TESTED` | `NOT_TESTED` | `NOT_TESTED` |
| Lorentzian dS/AdS | `NOT_TESTED` | `NOT_TESTED` | `NOT_TESTED` | `NOT_TESTED` | `NOT_TESTED` | `NOT_TESTED` |
| Asymptotically flat | `NOT_TESTED` | `NOT_TESTED` | `NOT_TESTED` | `NOT_TESTED` | `NOT_TESTED` | `NOT_TESTED` |

The JSON certificate, rather than this prose table, is authoritative for
status promotion.

## Next gates

1. Complete `BERGER_CURVED_CLOCK_REATTACHED_WITNESS`. The retained nonzero-Weyl
   Bach PBW expansion, full minimal coefficients, spatial Noether identities,
   formal adjointness, cyclicity, and \(q_1^2=0\) are complete. Reattaching the
   certified clock doublets supplies the two missing gauge directions, and an
   exact full companion gives scalar-biwave principal symbols on all ten
   metric and five ghost directions. Lift that companion through the lower
   curved PBW orders, build the 34-row causal homotopy, transport it through
   the clock SDR, and only then add nonminimal direct summands. Nonlinear
   \(q_2\) and the arity-two \(D\)-Cartan contraction remain downstream.
   The combined contraction on all 34 minimal rows is no longer open; it is
   exported portably as `classical_unary_q1` with
   \((\iota_{\rm cl},\pi_{\rm cl},S_{\rm cl})\).
2. Decide closure of the zero-charge transformations on the chosen sector,
   allowing a field-dependent algebroid if necessary.
3. Compute the first background-deformation obstruction and a quantitative
   stability radius.
4. Treat dS/AdS and asymptotically flat boundaries as new Lorentzian phase
   spaces, not as consequences of the compact-cylinder verdict.
5. Optionally reproduce the compact current-to-moment-map equivalence in an
   independent implementation; this is a cross-check, not a missing premise.

## Verification receipts

The exact commands, elapsed times, tiers, and skipped higher-tier reasons are
stored in the machine certificate. The scoped handoff commands are:

```bash
python3 d_quotient_classical/verify_classical_status.py --guards
python3 symbolic/verify_compact_cylinder_d_charge_audit.py --check
python3 -m unittest bridge.taub_moment_map.tests.test_compact_d_charge
python3 symbolic/verify_conformal_d_global_alternatives.py --check-result
python3 d_quotient_classical/scalar_clock/conformal_scalar_clock.py --check --guards
python3 -m unittest d_quotient_classical.scalar_clock.tests.test_conformal_scalar_clock
python3 d_quotient_classical/composite_clock/neutral_conformal_clock.py --check --guards
python3 -m unittest d_quotient_classical.composite_clock.tests.test_neutral_conformal_clock
python3 d_quotient_classical/composite_clock/neutral_clock_bv_health.py --check --guards
python3 -m unittest d_quotient_classical.composite_clock.tests.test_neutral_clock_bv_health
python3 d_quotient_classical/scalar_clock/homogeneous_stealth_clock.py --check --guards
python3 -m unittest d_quotient_classical.scalar_clock.tests.test_homogeneous_stealth_clock
python3 d_quotient_classical/scalar_clock/inhomogeneous_stealth_clock.py --check --guards
python3 -m unittest d_quotient_classical.scalar_clock.tests.test_inhomogeneous_stealth_clock
python3 d_quotient_classical/backreacted_clock/positive_berger_clock.py --check --guards
python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_positive_berger_clock
python3 d_quotient_classical/backreacted_clock/berger_clock_charge_seed.py --check --guards
python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_clock_charge_seed
python3 d_quotient_classical/backreacted_clock/berger_retained_minimal_operator.py --check --guards
python3 d_quotient_classical/backreacted_clock/verify_berger_retained_minimal_operator_independent.py
python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_retained_minimal_operator
python3 d_quotient_classical/backreacted_clock/berger_linearized_bach_pbw.py --check --guards
python3 d_quotient_classical/backreacted_clock/verify_berger_retained_minimal_operator.py
python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_linearized_bach_pbw
python3 d_quotient_classical/backreacted_clock/berger_causal_witness_preflight.py --check --guards
python3 d_quotient_classical/backreacted_clock/verify_berger_causal_witness_preflight.py
python3 -m unittest d_quotient_classical.backreacted_clock.tests.test_berger_causal_witness_preflight
```

No full-suite result is implied by the scoped checks.
