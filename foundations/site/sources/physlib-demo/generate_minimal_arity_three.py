#!/usr/bin/env python3
"""Generate the Lean finite replay of the authoritative arity-three certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "quantum-weyl/classical_import/certificates/STRICT_MINIMAL_BV_ARITY_THREE_IDENTITY_V1.json"
OUTPUT = ROOT / "physlib-demo/WeylPhyslibBridge/MinimalArityThree.lean"

GENERATORS = {
    "c": ".c",
    "omega": ".omega",
    "h": ".h",
    "h_star": ".hStar",
    "c_star": ".cStar",
    "omega_star": ".omegaStar",
}
PATH_KINDS = {"q1_q3": ".q1q3", "q2_q2": ".q2q2", "q3_q1": ".q3q1"}


def q(value: str) -> str:
    if "/" in value:
        numerator, denominator = value.split("/", 1)
        return f"({numerator} / {denominator} : ℚ)"
    return f"({value} : ℚ)"


def option(value: Any, render=str) -> str:
    return ".none" if value is None else f".some {render(value)}"


def lean_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def path_record(path: dict[str, Any]) -> str:
    kind = path["kind"]
    if kind == "q2_q2":
        first = path["outer_q2_component_id"]
        second = path["inner_q2_component_id"]
    else:
        first = path["q1_component_id"]
        second = path["q3_component_id"]
    positions = ", ".join(str(item) for item in path.get("inner_positions", []))
    return (
        f"{{ kind := {PATH_KINDS[kind]}, firstComponent := {lean_string(first)}, "
        f"secondComponent := {option(second, lean_string)}, innerPositions := [{positions}], "
        f"lastPosition := {option(path.get('last_position'))}, slot := {option(path.get('slot'))}, "
        f"multiplier := {path['multiplier']} }}"
    )


def channel_record(channel: dict[str, Any], result: dict[str, Any]) -> str:
    inputs = ", ".join(GENERATORS[item] for item in channel["inputs"])
    paths = ",\n        ".join(path_record(item) for item in channel["paths"])
    defect = ", ".join(q(item) for item in result["defect"])
    return (
        f"  {{ id := {lean_string(result['channel_id'])}, output := {GENERATORS[channel['output']]}, "
        f"inputs := [{inputs}], paths := [\n        {paths}\n      ], defect := [{defect}] }}"
    )


def mutation_record(item: dict[str, Any]) -> str:
    defect = ", ".join(q(value) for value in item["nonzero_defect"])
    return (
        f"  {{ channelId := {lean_string(item['channel_id'])}, kind := {PATH_KINDS[item['mutated_path_kind']]}, "
        f"defect := [{defect}] }}"
    )


def render() -> str:
    source = json.loads(SOURCE.read_text())
    inventory = source["channel_inventory"]
    receiver = source["exact_receiver"]
    channels = inventory["channels"]
    results = receiver["channel_results"]
    mutations = receiver["mutation_checks"]
    if source.get("result_id") != "STRICT_MINIMAL_BV_ARITY_THREE_IDENTITY_V1":
        raise ValueError("source identity drift")
    if len(channels) != 72 or len(results) != 72:
        raise ValueError("72-channel closure")
    if sum(len(item["paths"]) for item in channels) != 212:
        raise ValueError("212-path closure")
    if [item["channel_id"] for item in results] != [
        "q1q2q3__" + item["output"] + "__" + "__".join(item["inputs"])
        for item in channels
    ]:
        raise ValueError("channel/result ordering drift")
    if any(not item["defect_zero"] for item in results):
        raise ValueError("source contains nonzero channel defect")
    if len(mutations) != 3 or any(not item["detected"] for item in mutations):
        raise ValueError("mutation-witness closure")

    source_sha = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    channel_rows = ",\n".join(channel_record(channel, result) for channel, result in zip(channels, results))
    mutation_rows = ",\n".join(mutation_record(item) for item in mutations)
    return f'''/-
Copyright (c) 2026 Area9 Innovation. All rights reserved.
Released under Apache 2.0 license as described in the repository LICENSE.
Authors: Weyl-gravity programme contributors

GENERATED FILE.  Edit `generate_minimal_arity_three.py`, not this file.
Source SHA-256: {source_sha}
-/
import Mathlib.Data.Rat.Defs
import Mathlib.Tactic.NormNum
import Physlib.Meta.Informal.Basic

/-!
# Finite strict minimal-BV arity-three replay

This file imports the complete finite channel/path inventory and exact rational
receiver output from `STRICT_MINIMAL_BV_ARITY_THREE_IDENTITY_V1`.  Lean checks
the census, every serialized zero defect, and all three nonzero mutation
witnesses.  It does not formalize the natural differential operators or the
arbitrary-input differentiated-nilpotency argument.
-/

namespace WeylPhyslibBridge.MinimalArityThree

inductive Generator where
  | c | omega | h | hStar | cStar | omegaStar
  deriving DecidableEq, Repr

inductive PathKind where
  | q1q3 | q2q2 | q3q1
  deriving DecidableEq, Repr

structure PathRecord where
  kind : PathKind
  firstComponent : String
  secondComponent : Option String
  innerPositions : List Nat
  lastPosition : Option Nat
  slot : Option Nat
  multiplier : Int
  deriving DecidableEq, Repr

structure ChannelRecord where
  id : String
  output : Generator
  inputs : List Generator
  paths : List PathRecord
  defect : List ℚ
  deriving DecidableEq, Repr

structure MutationWitness where
  channelId : String
  kind : PathKind
  defect : List ℚ
  deriving DecidableEq, Repr

def sourceCertificateId : String := "STRICT_MINIMAL_BV_ARITY_THREE_IDENTITY_V1"
def sourceCertificateSha256 : String := "{source_sha}"

def channels : List ChannelRecord := [
{channel_rows}
]

def mutationWitnesses : List MutationWitness := [
{mutation_rows}
]

def pathCount : List ChannelRecord → Nat
  | [] => 0
  | channel :: rest => channel.paths.length + pathCount rest

def kindCount (kind : PathKind) : List ChannelRecord → Nat
  | [] => 0
  | channel :: rest =>
      channel.paths.foldl (fun total path => total + if path.kind = kind then 1 else 0) 0 +
        kindCount kind rest

def allChannelDefectsZero : Bool :=
  channels.all fun channel => channel.defect.all fun value => value == 0

def allMutationsDetected : Bool :=
  mutationWitnesses.all fun witness => witness.defect.any fun value => value != 0

theorem channelCountCertified : channels.length = 72 := by decide
theorem composablePathCountCertified : pathCount channels = 212 := by decide
theorem q1q3PathCountCertified : kindCount .q1q3 channels = 2 := by decide
theorem q2q2PathCountCertified : kindCount .q2q2 channels = 204 := by decide
theorem q3q1PathCountCertified : kindCount .q3q1 channels = 6 := by decide
theorem exactReceiverDefectsZero : allChannelDefectsZero = true := by decide
theorem mutationWitnessCountCertified : mutationWitnesses.length = 3 := by decide
theorem allThreeMutationsDetected : allMutationsDetected = true := by
  norm_num [allMutationsDetected, mutationWitnesses]

/-- Physical interpretation metadata; only the finite serialized replay above is formal. -/
informal_definition minimalArityThreeFiniteReplay where
  deps := [``exactReceiverDefectsZero, ``allThreeMutationsDetected]
  tag := "WG3A3"

#print axioms channelCountCertified
#print axioms composablePathCountCertified
#print axioms exactReceiverDefectsZero
#print axioms allThreeMutationsDetected

end WeylPhyslibBridge.MinimalArityThree
'''


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = render()
    if args.check:
        current = OUTPUT.read_text() if OUTPUT.is_file() else None
        if current != content:
            print("PHYSLIB_MINIMAL_ARITY_THREE: stale")
            return 1
        print("PHYSLIB_MINIMAL_ARITY_THREE: generated artifact current")
        return 0
    OUTPUT.write_text(content)
    print("PHYSLIB_MINIMAL_ARITY_THREE: wrote " + str(OUTPUT.relative_to(ROOT)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
