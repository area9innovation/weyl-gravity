# Observer legacy receiver historical-base binding repair v1

Both legacy Observer rails now resolve the historical five-row receiver
contract as the regular Git blob at commit
`aa5ca7814798dfbcc92ee52e462d25af74806515`, repository path
`physics/symplectic-reconstruction/closed_universe_observers/certificates/CHARGED_TIME_RECEIVER_ADMISSIBILITY_CROSSWALK_V1.json`,
and SHA-256 `e2c9aad23b667ec16bbb124b72066d803f3607fc4bd89acd459b53f672a43918`.
The producer and method-distinct verifier on each rail independently check the
commit, blob type, content hash and all five historical dispositions.

The regenerated legacy replay has SHA-256 `3851a46d...`; the regenerated
frequency-ratio nonactivation theorem has SHA-256 `e0deee0f...`. The current
seven-row crosswalk imports those two certificates and has SHA-256
`78cdd185...`. Neither legacy certificate imports the mutable current
crosswalk, so the current-crosswalk-to-legacy-to-current-crosswalk cycle is
absent.

All seven scientific dispositions are unchanged. Both legacy rows remain
`NO_CERTIFIED_MAP`; the operational frequency-ratio domain remains empty; and
the exact coordinate ratio one remains a non-redshift control. Mutations for
the historical commit, path, blob hash and current-path substitution fail
closed, as do deleted legacy rows and redshift promotion.

The direct-consumer audit stopped at the first additional stale pin,
`closed_universe_observers/atlas/observer-atlas-fragment.json`. Its generator,
verifier, aggregate and tests already carry another session's resident edits
in the shared tree, so they were preserved rather than overwritten. The
dedicated post-repair Tier-3 successor owns that frontier and the uninterrupted
full traversal.

EVIDENCE: `closed_universe_observers/receipts/OBSERVER_LEGACY_RECEIVER_HISTORICAL_BASE_BINDING_REPAIR_V1_MANIFEST.json`

CLOSE-OUT: DONE — immutable historical binding repaired; dispositions preserved; first downstream stale pin recorded fail-closed
