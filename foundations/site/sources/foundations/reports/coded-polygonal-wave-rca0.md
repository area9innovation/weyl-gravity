# Coded polygonal scalar wave over RCA₀

**Result:** `FOUNDATIONAL_CODED_POLYGONAL_WAVE_RCA0_V1`

## Theorem

RCA_0 suffices for the represented mean-zero scalar wave Cauchy theorem on the coded circle completion of Q/Z: the dense carrier is rational periodic polygonal chiral data, completed states and real times are fast Cauchy names with prescribed rates, and the solution is the unique continuous isometric extension of exact rational translations.

This closes the previous L2 formalization target for the declared representation. The supplied fast Cauchy rate is mathematical data; no modulus is extracted from bare convergence.

## Representation

- **Geometry:** The spatial circle is the complete separable metric space coded by dense Q/Z with circular rational distance; time reals are fast Cauchy sequences of rationals.
- **Dense State:** A pair (a,b) of zero-mean rational step functions on one finite rational partition. Their rational polygonal primitives are the right- and left-moving H1 profiles.
- **Completed State:** A fast Cauchy sequence of dense pairs in the chiral L2 energy metric, coded by the rational condition d(p_i,p_j)^2<=4^-i for i<=j, supplied as part of the name.
- **Solution:** S_t(a,b)=(T_t a,T_-t b), corresponding to u(t,x)=f(x-t)+g(x+t) modulo the fixed mean-zero convention.
- **Energy:** E=integral(a^2+b^2)=one half integral(u_x^2+u_t^2).
- **Continuity Name:** Each finite code supplies C_p and a minimum cell width. These give an explicit time modulus; a primitive-recursive diagonal combines it with the two input Cauchy rates.

## Proof ledger

| Stage | Base | Statement |
|---|---|---|
| `FINITE_CODE` | `PRA` | Finite rational partitions, zero-mean step pairs, exact L2 inner products, polygonal primitives, and rational translations are primitive-recursively coded. |
| `RATIONAL_GROUP` | `PRA` | S_q(a,b)=(T_q a,T_-q b) is a rational-time group action on the dense code and preserves zero mean. |
| `ENERGY_ISOMETRY` | `PRA` | The chiral energy d^2=integral(|a-a'|^2+|b-b'|^2) is exactly translation invariant; equivalently one half of integral(u_x^2+u_t^2) is conserved. |
| `CODE_MODULUS` | `PRA` | For a finite step pair p, d(S_q p,S_r p)^2 <= C_p |q-r| below half the minimum cell width, with primitive-recursive rational C_p and a displayed binary modulus. |
| `COMPLETION_NAME` | `RCA_0` | A completed energy state is a fast Cauchy sequence of dense rational codes with d(p_i,p_j)^2<=4^-i for i<=j; applying a fixed rational translation termwise preserves its prescribed rate. |
| `REAL_TIME_EXTENSION` | `RCA_0` | Given fast Cauchy names for a state and a real time, finite-code moduli provide a primitive-recursive diagonal name for S_t p. |
| `CAUCHY_EXISTENCE_UNIQUENESS` | `RCA_0` | The diagonal name exists, is independent of representatives, conserves energy, has the initial value, obeys the group law, and is the unique continuous isometric extension of the dense rational-time action. |

## The diagonal construction

- **Inputs:** A state name (p_n) with d(p_i,p_j)<=2^-i and a real-time name (q_n) with |q_i-q_j|<=2^-i for i<=j.
- **Index Rule:** Choose a strictly increasing primitive-recursive m(k)>=k+4 so that, for the computed constants of p_(k+3) and p_(k+4), C*2^-m(k)<=2^-2(k+3).
- **Output:** z_k=S_q(m(k)) p_(k+3).
- **Adjacent Bound:** d(z_k,z_(k+1)) <= d(p_(k+3),p_(k+4)) + sqrt(C_(p_(k+4))*|q_m(k)-q_m(k+1)|) <= 2^-(k+2).
- **Fast Cauchy Bound:** For i<=j, telescoping the adjacent bounds gives d(z_i,z_j)<=2^-(i+1)<=2^-i.
- **Independence:** Interleave equivalent state or time names and repeat the same isometry/modulus estimate; the output distance is zero.
- **Logical Boundary:** All searches are bounded number searches over rational inequalities with supplied rates. No tree, subsequence, compactness, basis selection, or convergence-modulus extraction is used.

The adjacent estimate telescopes to the required fast Cauchy rate. Isometry makes the output independent of the chosen state representative; the same estimate makes it independent of the real-time name. The group law and energy identity hold first on rational dense codes and pass to names by this uniqueness argument.

## Exact regression fixtures

| Fixture | Chiral energies | Total | Moduli checked |
|---|---|---|---:|
| `TRIANGLE_RIGHT` | `[[1, 1], [0, 1]]` | `[1, 1]` | 8 |
| `QUARTER_MIXED` | `[[3, 2], [1, 1]]` | `[5, 2]` | 8 |
| `NONUNIFORM_MIXED` | `[[9, 4], [5, 1]]` | `[29, 4]` | 8 |

## Coding context

[David Fernández-Duque, Paul Shafer, and Keita Yokoyama, Ekeland's variational principle in weak and strong systems of arithmetic, Selecta Mathematica 26 (2020), 68.](https://arxiv.org/abs/1902.03915) records the RCA₀ fast-Cauchy completion convention and a rational polygonal dense presentation. Its consulted PDF is pinned as `72579f36f47d21861a878568ee5d5199609a00e197e2d25e422011d387349638`. It does not prove this wave theorem.

## Reproduction

```text
python3 foundations/build_coded_polygonal_wave_rca0.py --check
python3 foundations/check_coded_polygonal_wave_rca0.py
python3 foundations/verify_coded_polygonal_wave_rca0.py
```

## Boundaries

- This does not establish that RCA_0 is necessary or the weakest base.
- This does not establish a WKL_0, ACA_0, or Choice lower bound.
- This does not establish the same upper bound for bare finite-energy existence without a fast Cauchy name.
- This does not establish representation invariance.
- This does not establish a localized spacetime-distribution theorem.
- This does not establish finite propagation or an advanced/retarded Green map.
- This does not establish a variable-coefficient or curved-spacetime Cauchy theorem.
- This does not establish the biwave or metric-BV propagator.
- This does not establish a new LORENTZIAN-CAUSAL result.
