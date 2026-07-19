#!/usr/bin/env bash
# science-forge-shadow.sh — advisory Science Forge audit rail for this programme.
#
# Runs the Science Forge substrate's certlab audits + coverage census READ-ONLY
# over this physics tree and reports drift/findings WITHOUT failing the build.
# This is the "advisory shadow rail" adoption posture from the handoff
# (reports/science-forge-handoff-2026-07-19.md §3): audit now, flip families to
# fail-closed by gate, not by date.
#
#   DEFAULT (advisory, light): bridge certificate audit + corpus coverage census.
#     Fast (~1 min), read-only, ALWAYS exits 0 — a FAIL/timeout is reported, not fatal.
#   --fieldbv     also run the field_bv_identification external-check audit (10 sympy
#                 verifiers, minutes — off by default to keep the rail light).
#   --fleet       also replay the bounded observers-fleet SAMPLE (34 fastest --check
#                 producers, ~40s). NOT the full 60-producer fleet (see FULL COMMANDS).
#   --full        = --fieldbv --fleet.
#   --strict      fail-closed: any stage FAIL/timeout makes the script exit nonzero
#                 (for when a team chooses to gate its CI on the substrate).
#   --help        this help.
#
# The substrate lives in the tango/forge repo (NOT here). Override its location
# with FORGE_REPO=/path/to/forge; the compiled checker with FORGEBIN=/path/to/bin.
#
# Nothing is written into this physics tree or the forge tree — every receipt,
# census file, and scratch manifest goes to a private temp dir, deleted on exit.
#
# FULL COMMANDS (documented, not run by default — the heavy nightly rails):
#   full observers fleet (60 producers, ~8 min cold):
#     $CLF replay <CL>/manifest.observers-fleet.json <CL>/lock.observers-fleet.json <receipt> --stamp <s>
#   full quantum-weyl / d_quotient / remainder fleets: see forge/tools/certlab/README.md
#   full certlab end-to-end gate: forge/tools/certlab/run.sh
#   evidence-graph impact queries: forge/tools/science-forge/discover/query.py

set -uo pipefail   # deliberately NOT -e: advisory mode runs every stage and reports.

STRICT=0; DO_FIELDBV=0; DO_FLEET=0
for arg in "$@"; do
  case "$arg" in
    --strict)  STRICT=1 ;;
    --fieldbv) DO_FIELDBV=1 ;;
    --fleet)   DO_FLEET=1 ;;
    --full)    DO_FIELDBV=1; DO_FLEET=1 ;;
    --help|-h) sed -n '2,40p' "$0"; exit 0 ;;
    *) echo "unknown flag: $arg (try --help)"; exit 2 ;;
  esac
done

SELF=$(readlink -f "$0")
PHYS_ROOT=$(cd "$(dirname "$SELF")/.." && pwd)
FORGE_REPO=${FORGE_REPO:-/home/alstrup/area9/tango/forge}
CL="$FORGE_REPO/tools/certlab"
CC="$FORGE_REPO/tools/science-forge/corpus-coverage"
BIN=${FORGEBIN:-/tmp/forgebin}

# PINNED TOOLCHAIN (since 2026-07-19): the substrate now has a stamped snapshot
# release — tag forge-v0.0.1 in the tango repo (0.1.x is reserved for the
# self-hosted toolchain). A CI checkout should pin the tag rather than track a
# dev HEAD; the stamped binary self-verifies its stdlib (`forge version` prints
# "stdlib: ... verified (h1:...)" and detects FORGE_LIB skew):
#   git clone --branch forge-v0.0.1 --depth 1 <tango-remote> && cd tango/forge
#   go build -ldflags "-X main.toolchainVersion=0.0.1 \
#     -X main.stdlibHash=h1:0hip688Vp6OgC0OzaP1jG9bT+pvKheDPFPQG3ZWKk50=" \
#     -o forge ./cmd/forge
# then FORGE_REPO=<that checkout>/forge FORGEBIN=<that checkout>/forge/forge.
# Release qualification: full both-backend examples corpus + package corpus
# green; the optional FORGE_ASAN sweep has 5 named pre-existing reds, filed in
# forge/docs/limitations.md §B1 (none touch the certlab/science-forge tools).
STAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
SCRATCH=$(mktemp -d "${TMPDIR:-/tmp}/sf-shadow.XXXXXX")
trap 'rm -rf "$SCRATCH"' EXIT

export FORGE_LIB="$FORGE_REPO/lib"

echo "=== Science Forge advisory shadow rail ==="
echo "physics tree : $PHYS_ROOT"
echo "substrate    : $FORGE_REPO (tools/certlab, tools/science-forge)"
echo "mode         : $([ "$STRICT" = 1 ] && echo 'STRICT (fail-closed)' || echo 'ADVISORY (never fails the build)')"
echo "stamp        : $STAMP"
echo

fail=0
declare -a SUMMARY

record() {  # name  status  detail
  SUMMARY+=("$(printf '%-26s %-14s %s' "$1" "$2" "$3")")
  case "$2" in
    PASS|OK|INFO) ;;
    *) if [ "$STRICT" = 1 ]; then fail=1; fi ;;
  esac
}

# ---- preflight: substrate present + checker built -------------------------
if [ ! -d "$CL" ]; then
  record "preflight" "SKIP" "substrate not found at $FORGE_REPO (set FORGE_REPO)"
  printf '%s\n' "${SUMMARY[@]}"
  echo; echo "shadow rail: substrate absent — nothing audited (advisory)."
  [ "$STRICT" = 1 ] && exit 1 || exit 0
fi
if [ ! -x "$BIN" ]; then
  echo "-- building the forge checker ($BIN) --"
  if ( cd "$FORGE_REPO" && go build -o "$BIN" ./cmd/forge ) 2>"$SCRATCH/build.log"; then
    record "preflight-build" "OK" "built $BIN"
  else
    record "preflight-build" "FAIL" "go build failed (see $SCRATCH/build.log kept? no — advisory)"
    printf '%s\n' "${SUMMARY[@]}"
    [ "$STRICT" = 1 ] && exit 1 || exit 0
  fi
fi
CLF=("$BIN" -run -I "$CL" "$CL/certlab.forge" --)

# ---- stage 1: bridge certificate audit (fast) -----------------------------
echo "-- 1. bridge certificate audit (existence/drift/edges/dag/gates) --"
if out=$(cd "$CL" && timeout 180 "${CLF[@]}" audit manifest.bridge.json lock.bridge.json \
          "$PHYS_ROOT" "$STAMP" "$SCRATCH/receipt.bridge.json" "$SCRATCH/dag.bridge.dot" 2>&1); then
  verdict=$(echo "$out" | grep -oE '\-> (PASS|FAIL).*' | tail -1)
  echo "   $verdict"; record "bridge-audit" "PASS" "${verdict:-PASS}"
else
  rc=$?
  echo "$out" | tail -6
  if [ "$rc" = 124 ]; then record "bridge-audit" "TIMEOUT" "exceeded 180s"
  else record "bridge-audit" "FAIL" "audit fail-closed (exit $rc) — real drift/finding, inspect receipt"; fi
fi
echo

# ---- stage 2: corpus coverage census (fast, read-only file scan) ----------
echo "-- 2. corpus coverage census (read-only inventory of this tree) --"
if out=$(timeout 180 python3 "$CC/inventory.py" --physics-root "$PHYS_ROOT" \
          -o "$SCRATCH/coverage.json" 2>&1); then
  echo "   $(echo "$out" | tail -1)"
  # surface drift vs the committed snapshot (coverage.md headline says 820 certs)
  ncerts=$(python3 -c "import json;print(json.load(open('$SCRATCH/coverage.json'))['coverage_summary']['total_certificates'])" 2>/dev/null || echo '?')
  base=$(grep -oE '\*\*820\*\*' "$CC/coverage.md" >/dev/null 2>&1 && echo 820 || echo '?')
  if [ "$ncerts" != "?" ] && [ "$base" = 820 ] && [ "$ncerts" != 820 ]; then
    echo "   DRIFT: corpus now has $ncerts certificates vs $base in the committed snapshot (coverage.md)"
    record "coverage-census" "DRIFT" "corpus grew to $ncerts certs (snapshot: 820) — refresh coverage.md"
  else
    record "coverage-census" "PASS" "$ncerts certificates inventoried"
  fi
else
  rc=$?
  echo "$out" | tail -4
  [ "$rc" = 124 ] && record "coverage-census" "TIMEOUT" "exceeded 180s" \
                  || record "coverage-census" "FAIL" "census error (exit $rc)"
fi
echo

# ---- stage 3 (opt): field_bv external-check audit -------------------------
if [ "$DO_FIELDBV" = 1 ]; then
  echo "-- 3. field_bv_identification external-check audit (10 sympy verifiers) --"
  if out=$(cd "$CL" && timeout 600 "${CLF[@]}" audit manifest.fieldbv.json manifest.fieldbv.json \
            "$PHYS_ROOT" "$STAMP" "$SCRATCH/receipt.fieldbv.json" "$SCRATCH/dag.fieldbv.dot" 2>&1); then
    verdict=$(echo "$out" | grep -oE '\-> (PASS|FAIL).*' | tail -1)
    echo "   $verdict"; record "fieldbv-audit" "PASS" "${verdict:-PASS}"
  else
    rc=$?; echo "$out" | tail -6
    [ "$rc" = 124 ] && record "fieldbv-audit" "TIMEOUT" "exceeded 600s (slow sympy — raise cap or run nightly)" \
                    || record "fieldbv-audit" "FAIL" "audit fail-closed (exit $rc)"
  fi
  echo
fi

# ---- stage 4 (opt): observers-fleet SAMPLE replay -------------------------
if [ "$DO_FLEET" = 1 ]; then
  echo "-- 4. observers-fleet SAMPLE replay (34 fastest --check producers) --"
  python3 - "$CL/manifest.observers-fleet.json" "$CL/observers_fleet_sample_ids.json" \
            "$SCRATCH/fleet.sample.json" <<'PY'
import json,sys
mpath,idspath,outpath = sys.argv[1],sys.argv[2],sys.argv[3]
m=json.load(open(mpath)); ids=set(json.load(open(idspath)))
m["certificates"]=[c for c in m["certificates"] if c["id"] in ids]
json.dump(m,open(outpath,"w"))
print(f"   sampled {len(m['certificates'])}/{len(ids)} producers")
PY
  if out=$(cd "$CL" && timeout 300 "${CLF[@]}" replay "$SCRATCH/fleet.sample.json" \
            lock.observers-fleet.json "$SCRATCH/receipt.fleet.json" --stamp "$STAMP" 2>&1); then
    verdict=$(echo "$out" | grep -oE '(PASS|CACHED-PASS|FAIL) *[0-9]*' | tail -1)
    echo "   $verdict"; record "fleet-sample-replay" "PASS" "${verdict:-PASS}"
  else
    rc=$?; echo "$out" | tail -6
    [ "$rc" = 124 ] && record "fleet-sample-replay" "TIMEOUT" "exceeded 300s" \
                    || record "fleet-sample-replay" "FAIL" "replay fail-closed (exit $rc) — stale producer/cert"
  fi
  echo
fi

# ---- summary --------------------------------------------------------------
echo "=== summary ($([ "$STRICT" = 1 ] && echo strict || echo advisory)) ==="
printf '%s\n' "${SUMMARY[@]}"
echo
if [ "$fail" = 1 ]; then
  echo "shadow rail: FINDINGS present and --strict set -> exit 1"
  exit 1
fi
echo "shadow rail: advisory pass (exit 0). Findings above are reported, not fatal."
exit 0
