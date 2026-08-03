"""Rail B: brute-force confirmation of the general-n closed forms.

This rail uses NONE of the structural argument. It builds the defining
constraint systems directly and computes exact ranks by fraction-free
elimination, then compares against the closed forms rail A derived. A slip in
the bijection argument and a slip in the elimination would have to coincide to
survive both.

Usage:
    PYTHONPATH=. python3 -m reverse_physics.verify_hamiltonian_privilege_general_n
"""

from __future__ import annotations

import json

from reverse_physics.exact_linalg import rank_bareiss
from reverse_physics.hamiltonian_privilege_general_n import (
    OUTPUT,
    RESULT_ID,
    codim_sp_in_liouville,
    codim_sp_in_marginal,
    dim_liouville,
    dim_marginal,
    dim_symplectic,
)
from reverse_physics.hamiltonian_privilege_linear_g0 import (
    liouville_constraints,
    marginal_constraints,
    symplectic_constraints,
)

# Brute force is cubic in the ambient dimension 4n^2; this range keeps the rail
# inside the Tier 1 fast-feedback budget while still covering four values of n
# beyond the G0 certificate's reach.
BRUTE_FORCE_RANGE = range(1, 7)

FAILURES: list[str] = []


def check(condition: bool, message: str) -> None:
    if not condition:
        FAILURES.append(message)


def brute_force_dimension(constraints, dof: int) -> int:
    ambient = (2 * dof) ** 2
    return ambient - rank_bareiss(constraints(dof))


def main() -> int:
    if not OUTPUT.exists():
        print(f"{RESULT_ID}: FAIL (certificate missing at {OUTPUT})")
        return 1
    certificate = json.loads(OUTPUT.read_text(encoding="utf-8"))
    table = certificate["dimension_table"]

    for dof in BRUTE_FORCE_RANGE:
        sp = brute_force_dimension(symplectic_constraints, dof)
        marginal = brute_force_dimension(marginal_constraints, dof)
        liouville = brute_force_dimension(liouville_constraints, dof)

        check(sp == dim_symplectic(dof), f"n={dof}: sp brute={sp} closed={dim_symplectic(dof)}")
        check(marginal == dim_marginal(dof), f"n={dof}: marginal brute={marginal} closed={dim_marginal(dof)}")
        check(liouville == dim_liouville(dof), f"n={dof}: sl brute={liouville} closed={dim_liouville(dof)}")

        check(
            marginal - sp == codim_sp_in_marginal(dof),
            f"n={dof}: marginal codimension brute={marginal - sp} closed={codim_sp_in_marginal(dof)}",
        )
        check(
            liouville - sp == codim_sp_in_liouville(dof),
            f"n={dof}: Liouville codimension brute={liouville - sp} closed={codim_sp_in_liouville(dof)}",
        )

        # The inclusion chain, independent of any closed form.
        check(sp <= marginal <= liouville, f"n={dof}: inclusion chain broken by brute force")

        # The threshold statement, restated from brute force alone.
        if dof == 1:
            check(marginal - sp == 0, "n=1 separated under brute force but must not")
        else:
            check(marginal - sp > 0, f"n={dof} failed to separate under brute force")

        recorded = table.get(f"n_{dof}")
        if recorded is None:
            FAILURES.append(f"n={dof}: absent from the certificate dimension table")
            continue
        check(recorded["hamiltonian_sp_dimension"] == sp, f"n={dof}: certificate sp disagrees")
        check(recorded["marginal_dimension"] == marginal, f"n={dof}: certificate marginal disagrees")
        check(recorded["liouville_sl_dimension"] == liouville, f"n={dof}: certificate sl disagrees")
        check(recorded["separation_exists"] == (marginal - sp > 0), f"n={dof}: certificate separation flag disagrees")

    # The G0 certificate's two data points must survive as special cases.
    check(dim_symplectic(2) == 10 and dim_marginal(2) == 14 and dim_liouville(2) == 15,
          "the closed forms do not reproduce the G0 n=2 numbers")
    check(dim_symplectic(1) == dim_marginal(1) == dim_liouville(1) == 3,
          "the closed forms do not reproduce the G0 n=1 degeneracy")

    if FAILURES:
        print(f"{RESULT_ID}: FAIL")
        for failure in FAILURES:
            print(f"  - {failure}")
        return 1
    print(
        f"{RESULT_ID}: independent rail PASS "
        f"(brute-force ranks match the closed forms for n = {min(BRUTE_FORCE_RANGE)}..{max(BRUTE_FORCE_RANGE)})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
