# Observer Tier-3 fixed point after legacy crosswalk extension v2

The exact committed programme subtree at
`d33c8e33371f0a073a59beeb54238ceafdcab9da` was materialized in a detached
worktree. All 11,184 regular-file and symlink Git blobs matched that commit;
the shared resident worktree was not used or overwritten.

One fail-fast Observer Tier-3 traversal was run from the beginning. It passed
398 tests, then stopped at
`test_berger_legacy_receiver_admissibility_replay.py::test_census_is_complete_and_fail_closed`.
The legacy replay producer still requires the historical five-row receiver
contract hash `e2c9aad2...`, while the current path correctly contains the
terminal seven-row extension `ec6ad915...`.

This is not a changed receiver disposition. The legacy replay certificate is
a historical extension source certified against the five-row base blob. A
direct relock to the current crosswalk would change the legacy certificate
hash and then the crosswalk hash, producing a recursive content-address
cycle. The smallest successor must make both legacy producer/verifier rails
resolve the exact historical base by commit plus hash, preserve their
`NO_CERTIFIED_MAP` conclusions, audit the two legacy consumers, and only then
start a new complete Tier-3 traversal.

No producer or scientific certificate was modified after the first failure.
The corpus-wide fixed point is not green and the Paper 9 freeze gate remains
inactive.

EVIDENCE: closed_universe_observers/receipts/OBSERVER_TIER3_FIXED_POINT_AFTER_LEGACY_CROSSWALK_EXTENSION_V2_OBSTRUCTION.json

CLOSE-OUT: OBSTRUCTED — historical-base/current-path binding conflict after 398 passing tests
