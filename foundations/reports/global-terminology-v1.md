# A single global terminology and dictionary destination

The earlier extraction tool exposed a separate editorial page even though its
corpus was global. The Dictionary navigation now opens one combined destination:
explained terms, four-perspective definitions, an alphabetical searchable global
index, and optional editing tools. Source filtering is a view of the same index.
The ladder links to that view; old term-review links redirect while preserving
perspective and source parameters. Existing dictionary anchors and crosslinks
remain valid. Readers see Definition pending for unexplained phrases; related
entries do not imply a verified contextual match.

The whole-project index loads a compressed global shard; page-specific shards
remain available when a source filter is selected. This increases the default
index download, but the static explained-term links and definitions render
immediately and work without JavaScript. Extraction remains deliberately broad
and noisy, especially for papers. The reader list filters symbolic/parser
fragments unless they match an existing dictionary entry; editing tools
expose the unfiltered candidates. This lexical filter is not semantic review. This change does not approve candidate terms,
write missing definitions, or promote any scientific claim.

The ladder-link source hash required refreshing extraction provenance; the
extraction algorithm and scientific corpus are unchanged. Scoped checks cover
default global scope, alphabetical ordering, hidden editorial controls, legacy
redirects, source filters, context highlights, four-perspective brief export,
existing dictionary navigation, and mobile layout. The site verification chain
checks generated artifacts and provenance. Commands, timings and artifact hashes
are in `../receipts/global-terminology-v1.json`. Tier 3 is not required: no
mathematical input, theorem or lifecycle changed.
