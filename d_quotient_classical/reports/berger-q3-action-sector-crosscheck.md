# Independent Berger action-to-`q3` sector cross-check

`BERGER_Q3_ACTION_SECTOR_CROSSCHECK` crosses the most important producer
boundary identified during the Paper IX review.  The checker does not import
the 5.8-million-term `q3` producer.  It writes the homogeneous reduced action
density independently in the two dressed variables

```text
h = h_hat_00,
R = dressed radial/Weyl fluctuation,
```

takes the eight required fourth action derivatives, and compares them with
all sixteen ordered zero-jet coefficients in output rows `h_hat_star_00` and
`R_star` of the frozen portable `q3` payload.

The direct density is

```text
N k^(3/2) [ alpha_B Cbar^2/(8 k^2)
            + rho^2 omega^2/(2 N^2)
            - Rbar rho^2/(12 k)
            - lambda rho^4/4 ],

N   = sqrt(1-h-2R),
k   = 1-2R,
rho = 1+R.
```

The exact derivative values are:

| output | inputs `(h,R)` | coefficient |
|---|---:|---:|
| `h_hat_star_00` | `(0,3)` | `-27` |
| `h_hat_star_00` | `(1,2)` | `27/8` |
| `h_hat_star_00` | `(2,1)` | `81/16` |
| `h_hat_star_00` | `(3,0)` | `405/128` |
| `R_star` | `(0,3)` | `-1071/40` |
| `R_star` | `(1,2)` | `-27` |
| `R_star` | `(2,1)` | `27/8` |
| `R_star` | `(3,0)` | `81/16` |

Every ordered permutation agrees exactly.  The result is intentionally
scoped: it is a strategic second derivation in the lapse and dressed
radial/Weyl sector, not a complete independent reconstruction of all
5,812,130 coefficients.

## Replay

```bash
PYTHONPATH=. python3 \
  d_quotient_classical/backreacted_clock/\
  berger_q3_action_sector_crosscheck.py --check --guards

PYTHONPATH=. python3 \
  d_quotient_classical/backreacted_clock/\
  verify_berger_q3_action_sector_crosscheck.py

PYTHONPATH=. pytest -q \
  d_quotient_classical/backreacted_clock/tests/\
  test_berger_q3_action_sector_crosscheck.py
```

The focused replay passes in roughly eight seconds on the development
machine.  No Tier-2 rebuild is required because the frozen `q3` artifact is
consumed by content hash rather than regenerated.
