# BT perturbative coisometry rigidity

**Result:** `CLASSIFIED`

The apparent range obstruction disappears on the formal perturbative BT
branch.  With the repaired Appendix C labels,

\[
A_\Upsilon=a_1,
\qquad
A_\Omega^\dagger\supset\frac{a_2^\dagger}{4E^2},
\]

so the published Jordan commutator gives

\[
[A_\Upsilon,A_\Omega^\dagger]
=\frac{(2E)^3}{4E^2}=2E\,1.
\]

But the homomorphism and (RR^\dagger=1) give the same commutator as
(2E\Pi), where (Pi=R^\dagger R).  Therefore (Pi_0=1).

Now expand the support projection formally:

\[
\Pi(\lambda)=1+\sum_{n\ge1}\lambda^n\Pi_n,
\qquad \Pi^2=\Pi.
\]

At every positive order,

\[
\Pi_n=-\sum_{k=1}^{n-1}\Pi_k\Pi_{n-k}.
\]

Thus (Pi_1=0), and induction gives (Pi_n=0) for all (n).  The BT map is
two-sided order by order in perturbation theory.  A discontinuous or
nonperturbative defect is not excluded.

This restricts the preceding finite coisometry certificate to
nonperturbative/disconnected branches.  Its general theorem remains correct,
but its defect family cannot represent the analytic BT branch once the free
cross-CCR is imposed.

The useful consequence is that formal inversion of (R_t) is cleared.  The
three endpoint constants must now be determined by distributional preservation
of the oscillator CCR and projector idempotence—not by an arbitrary range
overlap.  The `1/48` coefficient and complete probability are still open.

Verification:

```text
ulimit -v 500000; python3 reverse_physics/bt_perturbative_coisometry_rigidity.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_perturbative_coisometry_rigidity.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_perturbative_coisometry_rigidity
```

This exact `LOCAL-ALGEBRAIC`/`REDUCED-MODE` result makes no convergence,
nonperturbative, gravitational, or `LORENTZIAN-CAUSAL` claim.  Primary source:
[Bateman--Turok](https://arxiv.org/abs/2607.00096), Appendix C.
