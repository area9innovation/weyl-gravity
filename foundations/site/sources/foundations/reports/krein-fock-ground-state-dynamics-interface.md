# Certified free Krein--Fock ground-state-to-dynamics interface

**Result:** `FOUNDATIONAL_KREIN_FOCK_GROUND_STATE_DYNAMICS_INTERFACE_V1`

**Lifecycle:** `SUFFICIENCY_PROVED`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

## Result

Yes, for the free reduced-mode Krein--Fock system. Every one-particle energy is an integer n>=2, so the total occupation energy is nonnegative and vanishes only on the empty occupation. The vacuum is therefore the unique normalized vector ground state up to phase. It is also the unique normal density state of zero extended mean energy: positivity makes every excited diagonal weight nonnegative, zero mean energy kills all such weights, and the positive-form Cauchy--Schwarz inequality kills the corresponding off-diagonal entries. The same total-energy operator generates the certified Fock evolution, which fixes the vacuum exactly; hence its vector state is invariant under the induced automorphisms. This is a CONDITIONAL_BRIDGE using the free ground-state criterion, not a selection theorem for interacting, thermal, Hadamard, BRST, or Lorentzian states.

```text
CLASSICAL_STANDARD x KREIN_INDEFINITE x PHYSICAL_STATE_SELECTION
                 -- CONDITIONAL_BRIDGE -->
CLASSICAL_STANDARD x KREIN_INDEFINITE x GENERATOR_SPECTRAL_DYNAMICS
```

## Selection theorem

On the explicit occupation basis,

```text
dGamma(D)|m> = E(m)|m>,       E(m)=sum_i m(i) energy(i),
energy(i)>=2.
```

Thus `E(m)=0` exactly for the empty occupation. The kernel is the single
vacuum ray. This proves uniqueness of the normalized vector ground state
up to phase.

For a positive trace-class density `rho`, zero extended mean energy gives
`sum_m E(m) rho_mm=0`. Every excited diagonal entry is therefore zero.
The positive-form inequality `|rho_mn|^2 <= rho_mm rho_nn` removes all
off-diagonal entries attached to them, and trace one leaves
`rho=|0><0|`. This is uniqueness among normal zero-energy density states,
not among all stationary states.

## Invariance theorem

The dynamics source uses the identical total energy:

```text
U_F(t)|m> = exp(-it E(m))|m>.
```

Consequently `U_F(t)|0>=|0>` and
`omega_0(alpha_t^F(A))=omega_0(A)`. The empty occupation is also
`Gamma_s(J)`-positive, so this is the same companion-Hilbert positive
normal state constructed by the state certificate.
An energy-two rank-one projection is also stationary, providing an exact
counterexample to any claim that invariance alone selects the vacuum.

## Why the bridge is conditional

Energy selects this state because the displayed free Hamiltonian is
nonnegative and has a one-dimensional zero eigenspace. An interacting
Hamiltonian, another representation, or a thermal selection criterion may
have a different kernel or no normal ground state. Those are not imported
by analogy.

## Verification

```text
python3 foundations/build_krein_fock_ground_state_dynamics_interface.py --check
python3 foundations/check_krein_fock_ground_state_dynamics_interface.py
python3 foundations/verify_krein_fock_ground_state_dynamics_interface.py
python3 -m unittest foundations.tests.test_krein_fock_ground_state_dynamics_interface
```

## Boundaries

- This does not establish that stationarity alone selects a unique state; excited energy eigenstates and mixtures can also be stationary.
- This does not establish an interacting Weyl or Bateman--Turok ground state.
- This does not establish a KMS, Hadamard, incoming, outgoing, detector-conditioned, or BRST-compatible state.
- This does not establish selection among non-normal states without a density operator.
- This does not establish a thermodynamic limit or implementability in an inequivalent representation.
- This does not establish causal propagation, a Green operator, or a Lorentzian off-shell BV propagator.
- This does not establish a generalized Born rule, prediction chain, or empirical agreement.
- This does not establish a weakest-base reverse-mathematics theorem.
- This does not establish a gravitational, QME, residual-transfer, or LORENTZIAN-CAUSAL result.
