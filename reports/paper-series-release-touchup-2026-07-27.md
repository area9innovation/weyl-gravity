# Paper-series public-release touch-up

Date: 27 July 2026

## Scope

This maintenance pass made no new scientific promotion. It:

- gave Papers 01--06 a public-preprint date and a common AI-authorship and
  computational-accountability disclosure;
- replaced Paper 11's obsolete pre-publication warning by an expert-review
  condition for formal submission;
- added a focused-successor map to Paper 14;
- marked the Phase-1 QNM status in Paper 15 as historical and pointed to the
  later Paper 17 result;
- updated Paper 16 to distinguish Paper 17's exact graded mass-direction
  comparison from the still-open physical coupled-system/Jost crosswalk;
- rebuilt all ten affected PDFs and refreshed manuscript-bound claim maps.

## Standalone-history provenance repair

The Paper 14 and Paper 15 claim-map programs still named commit identifiers
from the former parent repository. Those objects are not present in the
standalone filtered history. The programs and verifiers now use the exact
rewritten commits whose pinned blobs have the same recorded content hashes:

| Imported object | Former commit | Standalone commit |
| --- | --- | --- |
| Paper 14 source baseline | `936d76dbd2a9149243e57a082fa3519f0cfa8724` | `7fc9d8ca3fbd0e63ad011ad6d6b2825f029f8586` |
| Complete axial reconstruction | `d5d5d6de648795203604d62ce7bc4f4ce6fea510` | `20f37b8068879dc9cda7107c71427bf2df23882e` |
| Endpoint-flux content | `332564286df69b0638aa8c618aa64e39581ab090` | `3ae5b4ea3bf2a010d8d52c23982ecf250a889123` |
| Endpoint-flux lifecycle | `0da46f3b0916e4e53f441df37077038892cf89c3` | `fd0e82df32cf49300b73aa3c7b9ef32efed328a0` |
| Global-connection content | `54670c5e371200ee1f08b88843cb3e67b3f17b3b` | `1766ed380352327b11032e53daa9732a8878f195` |
| Global-connection lifecycle | `b1eec02b2d04e585fddbf8f6f1c2ba1d0b96c6f1` | `7a71f94c057aff37eedd514b15a4f0187527fa54` |

The content hashes in the regenerated claim maps are unchanged except for
the manuscript hashes and generated overlay hashes caused by this pass.

## Verification

- Two `pdflatex` passes succeeded for Papers 01--06, 11, and 14--16.
- The Paper 11, 14, 15, and 16 claim-map verifiers passed.
- The combined Paper 14--16 claim-map test suite passed all 38 tests,
  including fail-closed mutation tests.
- All modified JSON files parsed.
- All four manuscript-bound claim-map hashes matched their source files.
- The 24 numbered authored LaTeX documents retained the standardized
  GPT-5.6.sol / Asger Alstrup Palm authorship; Paper 00 still additionally
  credits Claude Fable 5.
- `git diff --check` passed.

The full repository certificate suite was not run because no mathematical
operator, certificate payload, or shared algebra changed. The directly
affected paper dependency chains were run instead.
