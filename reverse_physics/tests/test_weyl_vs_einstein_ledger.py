"""Falsification tests for the Weyl-vs-Einstein comparison ledger.

The ledger's value is entirely in its rails, so these tests attack the rails
rather than the rows: each check must reject a row that violates it, and the
checker must not pass anything by accident.  The emitted certificate is also
compared against a freshly built one, so a stale certificate fails.
"""

from __future__ import annotations

import json
import os
import unittest

from reverse_physics.weyl_vs_einstein_ledger import (
    ALL_ASSUMPTIONS,
    BASE_ASSUMPTIONS,
    CERT_PATH,
    COLUMNS,
    DIRECTIONS,
    LEVELS,
    ROWS,
    STATUSES,
    build_certificate,
    check_rows,
    content_hash,
    negative_controls,
    row,
)


def _control(**over):
    base = row(
        id="X", direction="OPENS", level="L0", column="MATHEMATICS",
        status="PROVED", claim="control", traces_to=["RP-WEYL"],
        sources=["reverse_physics/reports/PHYSICS-VS-MATH.md"],
    )
    base.update(over)
    return base


class TestLedgerPasses(unittest.TestCase):
    def test_shipped_rows_have_no_failures(self):
        fails, _ = check_rows(ROWS)
        self.assertEqual(fails, [], "shipped ledger must be clean")

    def test_every_in_repo_source_resolves(self):
        repo = os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))))
        for r in ROWS:
            for s in r["sources"]:
                self.assertTrue(os.path.exists(os.path.join(repo, s)),
                                "%s cites missing %s" % (r["id"], s))

    def test_row_ids_are_unique(self):
        ids = [r["id"] for r in ROWS]
        self.assertEqual(len(ids), len(set(ids)))

    def test_every_direction_is_populated(self):
        for d in DIRECTIONS:
            self.assertTrue(any(r["direction"] == d for r in ROWS),
                            "no %s rows -- the axis would be decorative" % d)

    def test_open_rows_are_reported_not_buried(self):
        _, stats = check_rows(ROWS)
        self.assertEqual(
            sorted(stats["open_rows"]),
            sorted(r["id"] for r in ROWS if r["status"] == "OPEN"))
        self.assertTrue(stats["open_rows"], "an all-closed ledger is suspect")


class TestRailsRejectViolations(unittest.TestCase):
    """Each rail must actually fail.  A rail that cannot fail is not a rail."""

    def _expect(self, code, rows):
        fails, _ = check_rows(rows)
        self.assertTrue(any(f.startswith(code) for f in fails),
                        "%s not tripped; got %r" % (code, fails))

    def test_c1_rejects_invented_vocabulary(self):
        self._expect("C1", [_control(status="MOSTLY_TRUE")])
        self._expect("C1", [_control(level="L9")])
        self._expect("C1", [_control(column="VIBES")])
        self._expect("C1", [_control(direction="SIDEWAYS")])

    def test_c2_rejects_a_dangling_citation(self):
        self._expect("C2", [_control(sources=["reverse_physics/nope.md"])])

    def test_c3_forbids_citing_into_the_mathematics_column(self):
        self._expect("C3", [_control(status="CITED", literature=["x"])])
        self._expect("C3", [_control(status="OPEN")])
        self._expect("C3", [_control(sources=[])])

    def test_c4_requires_a_counterfactual_for_physics(self):
        self._expect("C4", [_control(column="PHYSICS", status="CITED",
                                     literature=["x"], contingent_on="")])

    def test_c5_requires_literature_for_cited(self):
        self._expect("C5", [_control(column="PHYSICS", status="CITED",
                                     contingent_on="an experiment")])

    def test_c6_rejects_undeclared_assumptions(self):
        self._expect("C6", [_control(traces_to=["RP-INVENTED"])])
        self._expect("C6", [_control(traces_to=[])])

    def test_c7_level_flips_must_be_mutual_cross_level_and_opposed(self):
        self._expect("C7", [_control(flips_with="ABSENT")])
        self._expect("C7", [_control(id="A", flips_with="B"),
                            _control(id="B", direction="CHALLENGES",
                                     flips_with="A")])          # same level
        self._expect("C7", [_control(id="A", flips_with="B"),
                            _control(id="B", level="L3",
                                     flips_with="A")])          # same direction
        self._expect("C7", [_control(id="A", flips_with="B"),
                            _control(id="B", level="L3",
                                     direction="CHALLENGES")])  # not mutual

    def test_c8_trade_edges_must_resolve_and_point_the_other_way(self):
        self._expect("C8", [_control(paid_for_by="ABSENT")])
        self._expect("C8", [_control(buys="ABSENT")])
        self._expect("C8", [_control(buys="A")])   # buys on an OPENS row
        self._expect("C8", [_control(id="A", direction="CHALLENGES",
                                     paid_for_by="A")])

    def test_c9_shared_rows_may_not_be_differentiators(self):
        self._expect("C9", [_control(direction="SHARED",
                                     traces_to=["RP-WEYL"])])

    def test_shared_exemption_needs_a_flip_partner(self):
        """A SHARED row tracing to a differentiator is allowed only when it
        says WHY -- because the differentiator stops differentiating at that
        level -- which it declares with flips_with."""
        ok = [_control(id="A", direction="SHARED", level="L1",
                       traces_to=["RP-PARITY"], flips_with="B"),
              _control(id="B", direction="OPENS", level="L0",
                       traces_to=["RP-PARITY"], flips_with="A")]
        fails, _ = check_rows(ok)
        self.assertEqual([f for f in fails if f.startswith("C9")], [])

    def test_all_shipped_negative_controls_are_rejected(self):
        passed, total, detail = negative_controls()
        self.assertEqual(passed, total,
                         [d for d in detail if not d["rejected"]])


class TestCertificate(unittest.TestCase):
    def test_emitted_certificate_is_current(self):
        with open(CERT_PATH) as fh:
            on_disk = json.load(fh)
        fresh = build_certificate()
        self.assertEqual(on_disk["rows_sha256"], fresh["rows_sha256"],
                         "certificate is stale -- re-run with --emit")
        self.assertEqual(on_disk["rows_sha256"], content_hash(ROWS))

    def test_certificate_declares_its_boundary(self):
        fresh = build_certificate()
        self.assertTrue(fresh["checks"]["passed"])
        self.assertTrue(fresh["checks"]["negative_controls_all_rejected"])
        self.assertTrue(fresh["does_not_establish"])
        joined = " ".join(fresh["does_not_establish"]).lower()
        self.assertIn("lorentzian-causal", joined,
                      "the certificate must disclaim promotion explicitly")

    def test_swap_is_over_a_shared_base(self):
        fresh = build_certificate()
        swap = fresh["swap"]
        self.assertEqual(set(swap["shared_base"]), set(BASE_ASSUMPTIONS))
        self.assertFalse(set(swap["einstein_adds"]) & set(swap["weyl_adds"]),
                         "the two additions must be disjoint or it is not a swap")
        for a in swap["jointly_unsatisfiable"]:
            self.assertIn(a, ALL_ASSUMPTIONS)


if __name__ == "__main__":
    unittest.main()
