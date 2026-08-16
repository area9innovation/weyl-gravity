#!/usr/bin/env python3
"""Generate the Lean finite graded q1/q2/q3 evaluator and exact path values."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "physlib-demo"
HERE = ROOT / "quantum-weyl/classical_import"
SOURCE = HERE / "certificates/STRICT_MINIMAL_BV_ARITY_THREE_IDENTITY_V1.json"
Q1 = HERE / "certificates/STRICT_PORTABLE_LOCAL_Q1_AST_V1.json"
Q2 = HERE / "certificates/STRICT_SIX_ROW_SUSPENDED_Q2_AST_V1.json"
Q3 = ROOT / "d_quotient_classical/certificates/CLASSICAL_MINIMAL_BV_Q3_EXPORT_V1.json"
ENGINE = HERE / "local_q1_q2_q3_receiver.py"
LOWER_ENGINE = HERE / "local_q1_q2_receiver.py"
CUBIC_ENGINE = HERE / "pure_weyl_cubic_natural_operator.py"
JET_ENGINE = HERE / "cylinder_polarized_bach_evaluator.py"
OUTPUT = DEMO / "WeylPhyslibBridge/FiniteGradedEvaluator.lean"

GENERATORS = {
    "c": ".c",
    "omega": ".omega",
    "h": ".h",
    "h_star": ".hStar",
    "c_star": ".cStar",
    "omega_star": ".omegaStar",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lean_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def q(value: str) -> str:
    if "/" in value:
        numerator, denominator = value.split("/", 1)
        return f"({numerator} / {denominator} : ℚ)"
    return f"({value} : ℚ)"


def unary_record(item: dict[str, Any]) -> str:
    return (
        f"  {{ id := {lean_string(item['component_id'])}, input := {GENERATORS[item['input']]}, "
        f"output := {GENERATORS[item['output']]}, coefficient := {item['coefficient']} }}"
    )


def binary_record(item: dict[str, Any]) -> str:
    return (
        f"  {{ id := {lean_string(item['component_id'])}, left := {GENERATORS[item['inputs'][0]]}, "
        f"right := {GENERATORS[item['inputs'][1]]}, output := {GENERATORS[item['output']]}, "
        f"coefficient := {item['coefficient_relative_to_primary']} }}"
    )


def raw_channel_record(channel: dict[str, Any], values: list[list[str]]) -> str:
    inputs = ", ".join(GENERATORS[item] for item in channel["inputs"])
    rows = ",\n      ".join("[" + ", ".join(q(value) for value in row) + "]" for row in values)
    return (
        f"  {{ output := {GENERATORS[channel['output']]}, inputs := [{inputs}], rawPathValues := [\n"
        f"      {rows}\n    ] }}"
    )


def evaluate_raw_paths(
    source: dict[str, Any],
    q1_value: dict[str, Any],
    q2_value: dict[str, Any],
    q3_value: dict[str, Any],
) -> list[tuple[dict[str, Any], list[list[str]]]]:
    sys.path.insert(0, str(HERE))
    try:
        import cylinder_polarized_bach_evaluator as point
        import local_q1_q2_q3_receiver as receiver

        q1_by_id = {item["component_id"]: item for item in q1_value["local_q1_ast"]["components"]}
        q2_by_id = {item["component_id"]: item for item in q2_value["ordered_components"]}
        primary_by_id = {item["primary_id"]: item for item in q2_value["primary_components"]}
        background = point.flat_background(5)
        output = []
        for channel in source["channel_inventory"]["channels"]:
            values = []
            for path in channel["paths"]:
                one_path = copy.deepcopy(path)
                one_path["multiplier"] = 1
                one_channel = {
                    "output": channel["output"],
                    "inputs": channel["inputs"],
                    "paths": [one_path],
                }
                value = receiver.evaluate_channel(
                    one_channel,
                    q1_by_id,
                    q2_by_id,
                    primary_by_id,
                    q3_value["natural_operator_ast"],
                    background,
                    seeds=(1, 2, 3),
                )
                values.append(receiver.lower.serialize_field(channel["output"], value))
            output.append((channel, values))
        return output
    finally:
        sys.path.pop(0)


def render() -> str:
    source = json.loads(SOURCE.read_text())
    q1_value = json.loads(Q1.read_text())
    q2_value = json.loads(Q2.read_text())
    q3_value = json.loads(Q3.read_text())
    if source.get("result_id") != "STRICT_MINIMAL_BV_ARITY_THREE_IDENTITY_V1":
        raise ValueError("arity-three source identity drift")
    if q1_value.get("result_id") != "STRICT_PORTABLE_LOCAL_Q1_AST_V1":
        raise ValueError("q1 source identity drift")
    if q2_value.get("result_id") != "STRICT_SIX_ROW_SUSPENDED_Q2_AST_V1":
        raise ValueError("q2 source identity drift")
    if q3_value.get("result_id") != "CLASSICAL_MINIMAL_BV_Q3_EXPORT_V1":
        raise ValueError("q3 source identity drift")
    unary = q1_value["local_q1_ast"]["components"]
    binary = q2_value["ordered_components"]
    if len(unary) != 5 or len(binary) != 22:
        raise ValueError("operation signature census drift")
    nonzero_q3_rows = [
        item for item in q3_value.get("minimal_q3_support", {}).get("rows", [])
        if item.get("q3_status") == "NONZERO_NATURAL_OPERATOR"
    ]
    if (
        len(nonzero_q3_rows) != 1
        or nonzero_q3_rows[0].get("operator_root") != "q3_hstar_hhh"
        or nonzero_q3_rows[0].get("output_generator") != "g_star"
        or nonzero_q3_rows[0].get("accepted_input_generators") != ["g", "g", "g"]
    ):
        raise ValueError("q3 output signature drift")
    raw_channels = evaluate_raw_paths(source, q1_value, q2_value, q3_value)
    if len(raw_channels) != 72 or sum(len(values) for _, values in raw_channels) != 212:
        raise ValueError("raw path-evaluation census drift")

    unary_rows = ",\n".join(unary_record(item) for item in unary)
    binary_rows = ",\n".join(binary_record(item) for item in binary)
    raw_rows = ",\n".join(raw_channel_record(channel, values) for channel, values in raw_channels)
    pins = {
        path: sha256(path)
        for path in (SOURCE, Q1, Q2, Q3, ENGINE, LOWER_ENGINE, CUBIC_ENGINE, JET_ENGINE)
    }
    pin_lines = "\n".join(f"{path.relative_to(ROOT)}: {digest}" for path, digest in pins.items())

    return f'''/-
Copyright (c) 2026 Area9 Innovation. All rights reserved.
Released under Apache 2.0 license as described in the repository LICENSE.
Authors: Weyl-gravity programme contributors

GENERATED FILE. Edit `generate_finite_graded_evaluator.py`, not this file.
Input SHA-256 pins:
{pin_lines}
-/
import WeylPhyslibBridge.MinimalArityThree

/-!
# Finite graded q1/q2/q3 evaluator

Unlike the original finite replay, this module does not import the arity-three
path inventory or its already-summed defect vectors as the computed answer.
It imports five unary and twenty-two ordered binary operation signatures plus
the unique ternary signature, constructs every typed composite, computes the
suspended Koszul multipliers, and aggregates independently evaluated raw path
values. The natural differential-operator evaluations supplying those raw
values remain outside Lean and are explicitly retained as an imported premise.
-/

namespace WeylPhyslibBridge.MinimalArityThree

structure UnaryOperation where
  id : String
  input : Generator
  output : Generator
  coefficient : Int
  deriving DecidableEq, Repr

structure BinaryOperation where
  id : String
  left : Generator
  right : Generator
  output : Generator
  coefficient : Int
  deriving DecidableEq, Repr

structure TernaryOperation where
  id : String
  first : Generator
  second : Generator
  third : Generator
  output : Generator
  coefficient : Int
  deriving DecidableEq, Repr

structure TypedPath where
  output : Generator
  inputs : List Generator
  path : PathRecord
  deriving DecidableEq, Repr

structure ChannelShape where
  output : Generator
  inputs : List Generator
  paths : List PathRecord
  deriving DecidableEq, Repr

structure RawChannelValues where
  output : Generator
  inputs : List Generator
  rawPathValues : List (List ℚ)
  deriving DecidableEq, Repr

def unaryOperations : List UnaryOperation := [
{unary_rows}
]

def binaryOperations : List BinaryOperation := [
{binary_rows}
]

def ternaryOperation : TernaryOperation :=
  {{ id := "q3_hstar_hhh", first := .h, second := .h, third := .h,
    output := .hStar, coefficient := 1 }}

def grassmannOdd : Generator → Bool
  | .c | .omega | .hStar => true
  | .h | .cStar | .omegaStar => false

def swapSign (left right : Generator) : Int :=
  if grassmannOdd left && grassmannOdd right then -1 else 1

def frontSign (front first second : Generator) : Int :=
  if grassmannOdd front && Bool.xor (grassmannOdd first) (grassmannOdd second)
  then -1 else 1

def twoPrecedingSign (first second : Generator) : Int :=
  if Bool.xor (grassmannOdd first) (grassmannOdd second) then -1 else 1

def q2q2TypedPaths : List TypedPath :=
  binaryOperations.flatMap fun outer =>
    binaryOperations.flatMap fun inner =>
      if inner.output = outer.left then
        let a := inner.left
        let b := inner.right
        let last := outer.right
        let base := outer.coefficient * inner.coefficient
        [
          {{ output := outer.output, inputs := [a, b, last], path :=
            {{ kind := .q2q2, firstComponent := outer.id, secondComponent := .some inner.id,
              innerPositions := [0, 1], lastPosition := .some 2, slot := .none,
              multiplier := base }} }},
          {{ output := outer.output, inputs := [a, last, b], path :=
            {{ kind := .q2q2, firstComponent := outer.id, secondComponent := .some inner.id,
              innerPositions := [0, 2], lastPosition := .some 1, slot := .none,
              multiplier := base * swapSign b last }} }},
          {{ output := outer.output, inputs := [last, a, b], path :=
            {{ kind := .q2q2, firstComponent := outer.id, secondComponent := .some inner.id,
              innerPositions := [1, 2], lastPosition := .some 0, slot := .none,
              multiplier := base * frontSign last a b }} }}
        ]
      else []

def q1q3Path (unary : UnaryOperation) : PathRecord :=
  {{ kind := .q1q3, firstComponent := unary.id,
    secondComponent := .some ternaryOperation.id, innerPositions := [],
    lastPosition := .none, slot := .none,
    multiplier := unary.coefficient * ternaryOperation.coefficient }}

def q3q1Path (unary : UnaryOperation) (slot : Nat) (sign : Int) : PathRecord :=
  {{ kind := .q3q1, firstComponent := unary.id,
    secondComponent := .some ternaryOperation.id, innerPositions := [],
    lastPosition := .none, slot := .some slot,
    multiplier := unary.coefficient * ternaryOperation.coefficient * sign }}

def q1q3TypedPaths : List TypedPath :=
  unaryOperations.flatMap fun unary =>
    if unary.input = ternaryOperation.output then
      [{{ output := unary.output,
         inputs := [ternaryOperation.first, ternaryOperation.second, ternaryOperation.third],
         path := q1q3Path unary }}]
    else []

def q3q1TypedPaths : List TypedPath :=
  unaryOperations.flatMap fun unary =>
    if unary.output = ternaryOperation.first then
      [
        {{ output := ternaryOperation.output,
           inputs := [unary.input, ternaryOperation.second, ternaryOperation.third],
           path := q3q1Path unary 0 1 }},
        {{ output := ternaryOperation.output,
           inputs := [ternaryOperation.first, unary.input, ternaryOperation.third],
           path := q3q1Path unary 1
             (if grassmannOdd ternaryOperation.first then -1 else 1) }},
        {{ output := ternaryOperation.output,
           inputs := [ternaryOperation.first, ternaryOperation.second, unary.input],
           path := q3q1Path unary 2
             (twoPrecedingSign ternaryOperation.first ternaryOperation.second) }}
      ]
    else []

def allTypedPaths : List TypedPath :=
  q2q2TypedPaths ++ q1q3TypedPaths ++ q3q1TypedPaths

def pathsAt (output : Generator) (inputs : List Generator) : List PathRecord :=
  allTypedPaths.filterMap fun candidate =>
    if candidate.output = output && candidate.inputs = inputs then .some candidate.path else .none

def sourceChannelShapes : List ChannelShape :=
  channels.map fun channel =>
    {{ output := channel.output, inputs := channel.inputs, paths := channel.paths }}

def pathInventoryMatchesOutput (output : Generator) : Bool :=
  (sourceChannelShapes.filter fun channel => channel.output = output).all fun channel =>
    channel.paths = pathsAt channel.output channel.inputs

def rawChannelValues : List RawChannelValues := [
{raw_rows}
]

def rawCoordinates : List (Generator × List Generator) :=
  rawChannelValues.map fun channel => (channel.output, channel.inputs)

def sourceCoordinates : List (Generator × List Generator) :=
  sourceChannelShapes.map fun channel => (channel.output, channel.inputs)

def rawValueArityMatchesOutput (output : Generator) : Bool :=
  (rawChannelValues.filter fun channel => channel.output = output).all fun channel =>
    (pathsAt channel.output channel.inputs).length = channel.rawPathValues.length

def scaleVector (coefficient : Int) (value : List ℚ) : List ℚ :=
  value.map fun entry => (coefficient : ℚ) * entry

def addVectors (left right : List ℚ) : List ℚ :=
  List.zipWith (fun a b => a + b) left right

def sumVectors : List (List ℚ) → List ℚ
  | [] => []
  | first :: rest => rest.foldl addVectors first

def evaluateRawChannel (raw : RawChannelValues) : List ℚ :=
  sumVectors (List.zipWith (fun path value => scaleVector path.multiplier value)
    (pathsAt raw.output raw.inputs) raw.rawPathValues)

def evaluateDerivedChannel (channel : ChannelShape) (raw : RawChannelValues) : List ℚ :=
  sumVectors (List.zipWith (fun path value => scaleVector path.multiplier value)
    (pathsAt channel.output channel.inputs) raw.rawPathValues)

def evaluateSourceChannel (channel : ChannelShape) (raw : RawChannelValues) : List ℚ :=
  sumVectors (List.zipWith (fun path value => scaleVector path.multiplier value)
    channel.paths raw.rawPathValues)

def sourceChannelValuePairs : List (ChannelShape × RawChannelValues) :=
  List.zip sourceChannelShapes rawChannelValues

def outputPairs (output : Generator) : List (ChannelShape × RawChannelValues) :=
  sourceChannelValuePairs.filter fun pair => pair.1.output = output

def pairPathMatches (pair : ChannelShape × RawChannelValues) : Bool :=
  decide (pair.1.paths = pathsAt pair.1.output pair.1.inputs)

def pairedPathInventoryMatchesOutput (output : Generator) : Bool :=
  (outputPairs output).all pairPathMatches

def pairDerivedZero (pair : ChannelShape × RawChannelValues) : Bool :=
  (evaluateDerivedChannel pair.1 pair.2).all fun entry => entry == 0

def pairSourceZero (pair : ChannelShape × RawChannelValues) : Bool :=
  (evaluateSourceChannel pair.1 pair.2).all fun entry => entry == 0

def outputDefectsZero (output : Generator) : Bool :=
  (outputPairs output).all pairDerivedZero

def sourceOutputDefectsZero (output : Generator) : Bool :=
  (outputPairs output).all pairSourceZero

theorem unaryOperationCountCertified : unaryOperations.length = 5 := by decide
theorem binaryOperationCountCertified : binaryOperations.length = 22 := by decide
theorem sourceChannelCountCertified : sourceChannelShapes.length = 72 := by decide
set_option maxRecDepth 100000 in theorem allTypedPathCountCertified : allTypedPaths.length = 212 := by decide
theorem rawChannelCountCertified : rawChannelValues.length = 72 := by decide
theorem rawCoordinatesMatchSource : rawCoordinates = sourceCoordinates := by decide

set_option maxRecDepth 100000 in theorem pathsC : pathInventoryMatchesOutput .c = true := by decide
set_option maxRecDepth 100000 in theorem pathsCStar : pathInventoryMatchesOutput .cStar = true := by decide
set_option maxRecDepth 100000 in theorem pathsH : pathInventoryMatchesOutput .h = true := by decide
set_option maxRecDepth 100000 in theorem pathsHStar : pathInventoryMatchesOutput .hStar = true := by decide
set_option maxRecDepth 100000 in theorem pathsOmega : pathInventoryMatchesOutput .omega = true := by decide
set_option maxRecDepth 100000 in theorem pathsOmegaStar : pathInventoryMatchesOutput .omegaStar = true := by decide

set_option maxRecDepth 100000 in theorem pairedPathsC : pairedPathInventoryMatchesOutput .c = true := by decide
set_option maxRecDepth 100000 in theorem pairedPathsCStar : pairedPathInventoryMatchesOutput .cStar = true := by decide
set_option maxRecDepth 100000 in theorem pairedPathsH : pairedPathInventoryMatchesOutput .h = true := by decide
set_option maxRecDepth 100000 in theorem pairedPathsHStar : pairedPathInventoryMatchesOutput .hStar = true := by decide
set_option maxRecDepth 100000 in theorem pairedPathsOmega : pairedPathInventoryMatchesOutput .omega = true := by decide
set_option maxRecDepth 100000 in theorem pairedPathsOmegaStar : pairedPathInventoryMatchesOutput .omegaStar = true := by decide

theorem semanticPathInventoryCertified :
    allTypedPaths.length = 212 ∧
    pathInventoryMatchesOutput .c = true ∧ pathInventoryMatchesOutput .cStar = true ∧
    pathInventoryMatchesOutput .h = true ∧ pathInventoryMatchesOutput .hStar = true ∧
    pathInventoryMatchesOutput .omega = true ∧ pathInventoryMatchesOutput .omegaStar = true := by
  exact ⟨allTypedPathCountCertified, pathsC, pathsCStar, pathsH, pathsHStar, pathsOmega, pathsOmegaStar⟩

set_option maxRecDepth 100000 in theorem rawArityC : rawValueArityMatchesOutput .c = true := by decide
set_option maxRecDepth 100000 in theorem rawArityCStar : rawValueArityMatchesOutput .cStar = true := by decide
set_option maxRecDepth 100000 in theorem rawArityH : rawValueArityMatchesOutput .h = true := by decide
set_option maxRecDepth 100000 in theorem rawArityHStar : rawValueArityMatchesOutput .hStar = true := by decide
set_option maxRecDepth 100000 in theorem rawArityOmega : rawValueArityMatchesOutput .omega = true := by decide
set_option maxRecDepth 100000 in theorem rawArityOmegaStar : rawValueArityMatchesOutput .omegaStar = true := by decide

theorem semanticRawValueArityCertified :
    rawValueArityMatchesOutput .c = true ∧ rawValueArityMatchesOutput .cStar = true ∧
    rawValueArityMatchesOutput .h = true ∧ rawValueArityMatchesOutput .hStar = true ∧
    rawValueArityMatchesOutput .omega = true ∧ rawValueArityMatchesOutput .omegaStar = true := by
  exact ⟨rawArityC, rawArityCStar, rawArityH, rawArityHStar, rawArityOmega, rawArityOmegaStar⟩

theorem allZeroTransfers (pairs : List (ChannelShape × RawChannelValues))
    (hpaths : pairs.all pairPathMatches = true)
    (hsource : pairs.all pairSourceZero = true) :
    pairs.all pairDerivedZero = true := by
  induction pairs with
  | nil => simp
  | cons pair rest ih =>
      simp only [List.all_cons, Bool.and_eq_true] at hpaths hsource ⊢
      rcases hpaths with ⟨hpath, hpaths⟩
      rcases hsource with ⟨hsource, hsources⟩
      constructor
      · have hrecord : pair.1.paths = pathsAt pair.1.output pair.1.inputs := by
          exact of_decide_eq_true (by simpa [pairPathMatches] using hpath)
        simpa [pairDerivedZero, pairSourceZero, evaluateDerivedChannel,
          evaluateSourceChannel, hrecord] using hsource
      · exact ih hpaths hsources

theorem outputDefectsFromSource (output : Generator)
    (hpaths : pairedPathInventoryMatchesOutput output = true)
    (hsource : sourceOutputDefectsZero output = true) :
    outputDefectsZero output = true := by
  exact allZeroTransfers (outputPairs output) hpaths hsource

set_option maxRecDepth 100000 in theorem sourceDefectsC : sourceOutputDefectsZero .c = true := by
  norm_num [sourceOutputDefectsZero, outputPairs, sourceChannelValuePairs,
    pairSourceZero, evaluateSourceChannel, sourceChannelShapes,
    sumVectors, addVectors, scaleVector, rawChannelValues, channels]
set_option maxRecDepth 100000 in theorem sourceDefectsCStar : sourceOutputDefectsZero .cStar = true := by
  norm_num [sourceOutputDefectsZero, outputPairs, sourceChannelValuePairs,
    pairSourceZero, evaluateSourceChannel, sourceChannelShapes,
    sumVectors, addVectors, scaleVector, rawChannelValues, channels]
set_option maxRecDepth 100000 in theorem sourceDefectsH : sourceOutputDefectsZero .h = true := by
  norm_num [sourceOutputDefectsZero, outputPairs, sourceChannelValuePairs,
    pairSourceZero, evaluateSourceChannel, sourceChannelShapes,
    sumVectors, addVectors, scaleVector, rawChannelValues, channels]
set_option maxRecDepth 100000 in theorem sourceDefectsHStar : sourceOutputDefectsZero .hStar = true := by
  norm_num [sourceOutputDefectsZero, outputPairs, sourceChannelValuePairs,
    pairSourceZero, evaluateSourceChannel, sourceChannelShapes,
    sumVectors, addVectors, scaleVector, rawChannelValues, channels]
set_option maxRecDepth 100000 in theorem sourceDefectsOmega : sourceOutputDefectsZero .omega = true := by
  norm_num [sourceOutputDefectsZero, outputPairs, sourceChannelValuePairs,
    pairSourceZero, evaluateSourceChannel, sourceChannelShapes,
    sumVectors, addVectors, scaleVector, rawChannelValues, channels]
set_option maxRecDepth 100000 in theorem sourceDefectsOmegaStar : sourceOutputDefectsZero .omegaStar = true := by
  norm_num [sourceOutputDefectsZero, outputPairs, sourceChannelValuePairs,
    pairSourceZero, evaluateSourceChannel, sourceChannelShapes,
    sumVectors, addVectors, scaleVector, rawChannelValues, channels]

set_option maxRecDepth 100000 in theorem defectsC : outputDefectsZero .c = true := by
  exact outputDefectsFromSource .c pairedPathsC sourceDefectsC
set_option maxRecDepth 100000 in theorem defectsCStar : outputDefectsZero .cStar = true := by
  exact outputDefectsFromSource .cStar pairedPathsCStar sourceDefectsCStar
set_option maxRecDepth 100000 in theorem defectsH : outputDefectsZero .h = true := by
  exact outputDefectsFromSource .h pairedPathsH sourceDefectsH
set_option maxRecDepth 100000 in theorem defectsHStar : outputDefectsZero .hStar = true := by
  exact outputDefectsFromSource .hStar pairedPathsHStar sourceDefectsHStar
set_option maxRecDepth 100000 in theorem defectsOmega : outputDefectsZero .omega = true := by
  exact outputDefectsFromSource .omega pairedPathsOmega sourceDefectsOmega
set_option maxRecDepth 100000 in theorem defectsOmegaStar : outputDefectsZero .omegaStar = true := by
  exact outputDefectsFromSource .omegaStar pairedPathsOmegaStar sourceDefectsOmegaStar

theorem semanticEvaluatorDefectsZero :
    outputDefectsZero .c = true ∧ outputDefectsZero .cStar = true ∧
    outputDefectsZero .h = true ∧ outputDefectsZero .hStar = true ∧
    outputDefectsZero .omega = true ∧ outputDefectsZero .omegaStar = true := by
  exact ⟨defectsC, defectsCStar, defectsH, defectsHStar, defectsOmega, defectsOmegaStar⟩

/- The path evaluator is formal; the natural differential-operator values are imported. -/
informal_definition minimalArityThreeFiniteGradedEvaluator where
  deps := [``semanticPathInventoryCertified, ``semanticRawValueArityCertified,
    ``semanticEvaluatorDefectsZero]
  tag := "WG3A3S"

#print axioms semanticPathInventoryCertified
#print axioms semanticEvaluatorDefectsZero

end WeylPhyslibBridge.MinimalArityThree
'''


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = render()
    if args.check:
        current = OUTPUT.read_text() if OUTPUT.is_file() else None
        if current != content:
            print("PHYSLIB_FINITE_GRADED_EVALUATOR: stale")
            return 1
        print("PHYSLIB_FINITE_GRADED_EVALUATOR: generated artifact current")
        return 0
    OUTPUT.write_text(content)
    print("PHYSLIB_FINITE_GRADED_EVALUATOR: wrote " + str(OUTPUT.relative_to(ROOT)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
