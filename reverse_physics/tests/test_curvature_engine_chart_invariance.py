"""Chart audit of the pinned curvature engine — does it produce TENSORS?

WHY THIS EXISTS.  REVERSE_PHYSICS_PARITY_SCALAR_CONTROL_V1 found eight
contractions in the Forge parity gate that were not tensor contractions at all:
they summed a repeated index over two lower or two upper slots with no metric
between them, and returned coordinate-dependent numbers that passed every
conformal and weight check the apparatus had.  Nothing anywhere asked whether a
candidate was a TENSOR.

That defect class is not specific to Forge, so the engines this stream depends
on need the same question asked of them.
`black_hole_programme/weyl_geometry.py` is first because the reverse-physics work
item names it as a pinned dependency: "the exact
Christoffel/Riemann/Ricci/Weyl/Bach engine, frozen BH-0 conventions, pinned by
hash.  NOT written by this stream."

WHAT IS TESTED, AND WHY THIS SHAPE.  The first draft checked that the engine's
scalar invariants agree across charts.  That timed out at 900 s, and a timeout is
not a pass.  Profiling located the cost precisely: the curvature stages are cheap
(Christoffel 0.1 s, Riemann 2.1 s, Ricci 0.1 s, Weyl 1.3 s) and `invariants()` is
the whole bottleneck — it is an O(N^8) symbolic contraction with `simplify` on
top.

So this tests the TRANSFORMATION LAW componentwise instead, which is both cheaper
and a sharper statement than scalar invariance — a scalar can come out right
through cancelling errors, a tensor law cannot:

    R'_{abcd}(0) = A^p_a A^q_b A^r_c A^s_d R_{pqrs}(0)

evaluated at the base point with exact rationals, for Riemann, Ricci and Weyl.
It audits `_christoffel`, `_riemann`, `_ricci` and `_weyl` directly.
`invariants()` itself is NOT covered here — see the boundary note at the bottom.

THE FIXTURE.  g = L S L^T with L unit lower-triangular and polynomial, so
det g = -1 exactly and the inverse stays POLYNOMIAL.  Without that the symbolic
4x4 inverse produces rational functions and every stage downstream inherits the
blowup.  Same trick the Forge fixtures use, for the same reason.
"""

from __future__ import annotations

import os
import sys
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

try:
    import sympy as sp
    from black_hole_programme.weyl_geometry import Geometry, N
    HAVE = True
except Exception:  # pragma: no cover - environment without sympy
    HAVE = False

# THIS AUDIT TAKES ~19 MINUTES and is therefore OPT-IN.  The scoped suite is a
# fast falsification rail -- about 35 seconds -- and a twenty-minute member would
# either be normalised away or quietly skipped, and a skip is not a pass.  So it
# is explicit:
#
#     WEYL_SLOW_AUDIT=1 python -m pytest reverse_physics/tests/test_curvature_engine_chart_invariance.py
#
# Last full run: 11 passed in 1153 s.  Riemann, Ricci and Weyl each obey the
# tensor transformation law at the base point under all three SL(4, Z) charts,
# and the scalar curvature is invariant.
SLOW = os.environ.get("WEYL_SLOW_AUDIT") == "1"
RUN = HAVE and SLOW


def charts():
    """Three elements of SL(4, Z): unit lower-triangular, unit upper-triangular,
    and their product, which is triangular in neither direction.  Agreement
    across all three is agreement under a generic element rather than under a
    shear in one direction."""
    lower = sp.Matrix(4, 4, lambda a, b:
                      1 if a == b else (0 if a < b else ((a * 3 + b * 2) % 3) - 1))
    upper = sp.Matrix(4, 4, lambda a, b:
                      1 if a == b else (0 if a > b else ((a * 2 + b * 5) % 3) - 1))
    return [lower, upper, upper * lower]


def fixture():
    """g = L S L^T: non-diagonal, curvature nonzero, det g = -1, and crucially an
    inverse that stays polynomial."""
    t, x, y, z = sp.symbols("t x y z", real=True)
    coords = [t, x, y, z]
    L = sp.Matrix([[1, 0, 0, 0],
                   [x, 1, 0, 0],
                   [y, z, 1, 0],
                   [0, x, y, 1]])
    g = sp.expand(L * sp.diag(-1, 1, 1, 1) * L.T)
    return coords, g


def rechart(coords, g, A):
    """g'(y) = A^T g(A y) A, with x = A y."""
    subs = {coords[i]: sum(A[i, j] * coords[j] for j in range(N))
            for i in range(N)}
    g_at = g.applyfunc(lambda e: e.subs(subs, simultaneous=True))
    return sp.expand(A.T * g_at * A)


def at0(expr, coords):
    return sp.nsimplify(sp.expand(expr).subs({c: 0 for c in coords}))


@unittest.skipUnless(RUN, "slow audit; set WEYL_SLOW_AUDIT=1 (~19 min)")
class TestTheEngineProducesTensors(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.coords, cls.g = fixture()
        cls.A = charts()
        cls.base = Geometry(cls.coords, cls.g)
        cls.transformed = [Geometry(cls.coords, rechart(cls.coords, cls.g, A))
                           for A in cls.A]

    # -- the rig itself ---------------------------------------------------

    def test_the_charts_are_unimodular(self):
        """det A = 1 exactly, so the volume element survives and a density-valued
        quantity would be expected to be invariant too."""
        for A in self.A:
            self.assertEqual(sp.expand(A.det()), 1)

    def test_the_fixture_has_unit_determinant_so_the_inverse_stays_polynomial(self):
        """The reason the first draft timed out: a symbolic 4x4 inverse with a
        non-trivial determinant produces rational functions, and every stage
        downstream inherits the blowup."""
        self.assertEqual(sp.expand(self.g.det()), -1)
        self.assertTrue(all(e.is_polynomial() for e in sp.expand(self.g.inv())))

    def test_the_fixture_is_actually_curved(self):
        """Zero curvature cannot distinguish a correct contraction from a broken
        one."""
        R = self.base.Riemann
        nz = [(a, b, c, d) for a in range(N) for b in range(N)
              for c in range(N) for d in range(N)
              if at0(R[a][b][c][d], self.coords) != 0]
        self.assertGreater(len(nz), 0, "Riemann vanishes at the base point")

    def test_the_charts_MOVE_the_metric(self):
        """The calibration.  If a chart change leaves the metric alone it is
        inert, and every agreement below is silence rather than evidence."""
        base = [at0(self.g[a, b], self.coords) for a in range(N) for b in range(N)]
        for i, G in enumerate(self.transformed):
            got = [at0(G.g[a, b], self.coords) for a in range(N) for b in range(N)]
            self.assertNotEqual(base, got, f"chart {i} left the metric unchanged")

    def test_a_MALFORMED_contraction_moves(self):
        """A deliberately non-covariant quantity: the sum of squared Riemann
        components with no inverse metric anywhere.  It must move, or the rig
        cannot detect the defect it was built for."""
        def bad(G):
            return sum(at0(G.Riemann[a][b][c][d], self.coords) ** 2
                       for a in range(N) for b in range(N)
                       for c in range(N) for d in range(N))
        base = bad(self.base)
        moved = [bad(G) != base for G in self.transformed]
        self.assertTrue(any(moved),
                        "no chart moved a manifestly non-covariant quantity")

    # -- the audit --------------------------------------------------------

    def _check_rank2(self, name, pick):
        """M'_{ab}(0) = A^p_a A^q_b M_{pq}(0)."""
        base = [[at0(pick(self.base)[p, q], self.coords) for q in range(N)]
                for p in range(N)]
        for i, (A, G) in enumerate(zip(self.A, self.transformed)):
            for a in range(N):
                for b in range(N):
                    want = sum(A[p, a] * A[q, b] * base[p][q]
                               for p in range(N) for q in range(N))
                    got = at0(pick(G)[a, b], self.coords)
                    self.assertEqual(sp.expand(got - want), 0,
                                     f"{name}[{a}][{b}] breaks the tensor law "
                                     f"under chart {i}")

    def _check_rank4(self, name, pick):
        """T'_{abcd}(0) = A^p_a A^q_b A^r_c A^s_d T_{pqrs}(0)."""
        base = [[[[at0(pick(self.base)[p][q][r][s], self.coords)
                   for s in range(N)] for r in range(N)]
                 for q in range(N)] for p in range(N)]
        for i, (A, G) in enumerate(zip(self.A, self.transformed)):
            for a in range(N):
                for b in range(N):
                    for c in range(N):
                        for d in range(N):
                            want = sum(
                                A[p, a] * A[q, b] * A[r, c] * A[s, d]
                                * base[p][q][r][s]
                                for p in range(N) for q in range(N)
                                for r in range(N) for s in range(N)
                                if base[p][q][r][s] != 0)
                            got = at0(pick(G)[a][b][c][d], self.coords)
                            self.assertEqual(sp.expand(got - want), 0,
                                             f"{name}[{a}][{b}][{c}][{d}] breaks "
                                             f"the tensor law under chart {i}")

    def test_riemann_obeys_the_tensor_law(self):
        self._check_rank4("Riemann", lambda G: G.Riemann)

    def test_weyl_obeys_the_tensor_law(self):
        self._check_rank4("Weyl", lambda G: G.Weyl)

    def test_ricci_obeys_the_tensor_law(self):
        self._check_rank2("Ricci", lambda G: G.Ricci)

    def test_the_scalar_curvature_is_invariant(self):
        """R is the one scalar cheap enough to check directly here, and it is a
        fully contracted quantity — so it exercises the raise that the rank-2 and
        rank-4 laws above do not."""
        base = at0(self.base.Rscalar, self.coords)
        self.assertNotEqual(base, 0)
        for i, G in enumerate(self.transformed):
            self.assertEqual(sp.expand(at0(G.Rscalar, self.coords) - base), 0,
                             f"the scalar curvature moved under chart {i}")


@unittest.skipUnless(HAVE, "sympy or the curvature engine is unavailable")
class TestTheBoundaryOfThisAudit(unittest.TestCase):  # cheap: stays in the fast suite
    """What this does NOT cover, kept as an executable reminder rather than a
    comment, because the gap is the interesting part."""

    def test_invariants_is_not_covered_and_the_reason_is_recorded(self):
        """`Geometry.invariants()` is a separate contraction site and is NOT
        audited here: it is an O(N^8) symbolic contraction with `simplify` on
        top, and the first draft of this file timed out at 900 s inside it.  A
        timeout is not a pass.  The tensors it contracts ARE audited above, and
        its raises are written with explicit `ginv[...]` factors at the point of
        use — the safe idiom — but neither of those is a test of it."""
        import inspect
        from black_hole_programme import weyl_geometry
        src = inspect.getsource(weyl_geometry.Geometry.invariants)
        self.assertIn("ginv", src)

    def test_the_rest_of_the_python_corpus_is_not_swept(self):
        """Over two thousand files mention curvature.  This audits ONE engine,
        the one the work item pins.  The argument that the rest uses the safe
        idiom is an argument, not a sweep — and 'conformally invariant by
        construction' was also true, and also missed the point."""
        self.assertTrue(os.path.exists(
            os.path.join(REPO_ROOT, "black_hole_programme", "weyl_geometry.py")))


if __name__ == "__main__":
    unittest.main()
