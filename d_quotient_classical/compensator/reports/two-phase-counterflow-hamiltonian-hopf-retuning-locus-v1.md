# Two-phase counterflow Hamiltonian--Hopf retuning locus

Result: `OBSTRUCTED_NO_STABLE_JHALF_RETUNING_ON_CONNECTED_TRACE_HEALTHY_FAMILY`.

The exact stationary equations reduce the smallest same-field, same-derivative-order
retuning family to positive coordinates `(q,x,C)` with

```text
alpha_B = 2*C/(q*x^2)
M2      = 2*C*(4*q-1)/(3*q*x)
V0      = -C*(q^2-5*q+1)/(3*q).
```

After quotienting scale and phase normalization, only `q` changes the spectral
shape.  The positive homogeneous-trace component is

```text
(13-3*sqrt(17))/4 < q < 1/4.
```

The complete 14-by-14 `j=1/2` both-weight physical quotient factors as
`product(F_i(q,w)^2)`, with `w=z^2/x`.  Its load-bearing quartic is

```text
F2 = 16*q^2*w^2 + (-48*q^3+72*q)*w + 32*q^3-108*q^2+81,
disc_w(F2) = 256*q^5*(9*q-8).
```

The discriminant is strictly negative everywhere in the declared component.
Thus every admissible retuning retains a genuine multiplicity-two
Hamiltonian--Hopf quartet.  The modular residue pairing is nondegenerate and
the real unstable sector has constant inertia `(4,4,0)`, so this sector is not
gauge, charge, radical or a deleted clock orbit.

Three exact stable-sector cross-factor collisions are isolated by rational
intervals in the payload.  They cannot restore health because `F2` remains
unstable; their full polynomial Jordan types are left fail-closed.

This is a `LOCAL-ALGEBRAIC` / `REDUCED-MODE` decision theorem with an imported
selected-fixture `LORENTZIAN-CAUSAL` parent.  A familywide Green homotopy,
all-isotype health, nonlinear stability, Hadamard, QME, particles, positivity
and unitarity are not established.

## Verification

```bash
python3 d_quotient_classical/compensator/two_phase_counterflow_hamiltonian_hopf_retuning_locus.py --check
python3 d_quotient_classical/compensator/verify_two_phase_counterflow_hamiltonian_hopf_retuning_locus.py
python3 d_quotient_classical/compensator/two_phase_counterflow_hamiltonian_hopf_retuning_locus.py --full-residue --check
```
