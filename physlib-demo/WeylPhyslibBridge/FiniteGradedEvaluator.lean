/-
Copyright (c) 2026 Area9 Innovation. All rights reserved.
Released under Apache 2.0 license as described in the repository LICENSE.
Authors: Weyl-gravity programme contributors

GENERATED FILE. Edit `generate_finite_graded_evaluator.py`, not this file.
Input SHA-256 pins:
quantum-weyl/classical_import/certificates/STRICT_MINIMAL_BV_ARITY_THREE_IDENTITY_V1.json: ec51e447914516164b0caa51cbecbf12f1a4b2c8b7ecfbd1303f56d17cc095b5
quantum-weyl/classical_import/certificates/STRICT_PORTABLE_LOCAL_Q1_AST_V1.json: bcd78cf73f494517304f1ae5aedffa48036443a9c45566a94b3ed972de83b338
quantum-weyl/classical_import/certificates/STRICT_SIX_ROW_SUSPENDED_Q2_AST_V1.json: 513b43a90a936e1837947078e8f72da772f37461996b0b27b7df938ab355fbb3
d_quotient_classical/certificates/CLASSICAL_MINIMAL_BV_Q3_EXPORT_V1.json: eb217d49cde1e998bec352bc82cd67b80243d849fcdcacbfb33dabbb7837eda3
quantum-weyl/classical_import/local_q1_q2_q3_receiver.py: 9c68de3981150aac2eb795d5cb032beed2d054da7f2afd75e0b0b61408fc5465
quantum-weyl/classical_import/local_q1_q2_receiver.py: d1502a51ea0947a0efadbed56c76e2d4e3b0fbf366969c58228999b4e596da68
quantum-weyl/classical_import/pure_weyl_cubic_natural_operator.py: 32e03278573a9ac0465392b3aa08c1cbc53919da100994416c53b12ec7433111
quantum-weyl/classical_import/cylinder_polarized_bach_evaluator.py: 2503bcfdeafbe1dc4fc6146ddfcb1642326e19f449bebba6fd1d7580b2cebc73
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
  { id := "q1_h_c", input := .c, output := .h, coefficient := 1 },
  { id := "q1_h_omega", input := .omega, output := .h, coefficient := 1 },
  { id := "q1_hstar_h", input := .h, output := .hStar, coefficient := 1 },
  { id := "q1_cstar_hstar", input := .hStar, output := .cStar, coefficient := 1 },
  { id := "q1_omegastar_hstar", input := .hStar, output := .omegaStar, coefficient := 1 }
]

def binaryOperations : List BinaryOperation := [
  { id := "q2_c_cc", left := .c, right := .c, output := .c, coefficient := 1 },
  { id := "q2_omega_comega__forward", left := .c, right := .omega, output := .omega, coefficient := 1 },
  { id := "q2_omega_comega__reverse", left := .omega, right := .c, output := .omega, coefficient := -1 },
  { id := "q2_h_ch__forward", left := .c, right := .h, output := .h, coefficient := 1 },
  { id := "q2_h_ch__reverse", left := .h, right := .c, output := .h, coefficient := 1 },
  { id := "q2_h_omegah__forward", left := .omega, right := .h, output := .h, coefficient := 1 },
  { id := "q2_h_omegah__reverse", left := .h, right := .omega, output := .h, coefficient := 1 },
  { id := "q2_hstar_hh", left := .h, right := .h, output := .hStar, coefficient := 1 },
  { id := "q2_hstar_chstar__forward", left := .c, right := .hStar, output := .hStar, coefficient := 1 },
  { id := "q2_hstar_chstar__reverse", left := .hStar, right := .c, output := .hStar, coefficient := -1 },
  { id := "q2_hstar_omegahstar__forward", left := .omega, right := .hStar, output := .hStar, coefficient := 1 },
  { id := "q2_hstar_omegahstar__reverse", left := .hStar, right := .omega, output := .hStar, coefficient := -1 },
  { id := "q2_cstar_hhstar__forward", left := .h, right := .hStar, output := .cStar, coefficient := 1 },
  { id := "q2_cstar_hhstar__reverse", left := .hStar, right := .h, output := .cStar, coefficient := 1 },
  { id := "q2_cstar_ccstar__forward", left := .c, right := .cStar, output := .cStar, coefficient := 1 },
  { id := "q2_cstar_ccstar__reverse", left := .cStar, right := .c, output := .cStar, coefficient := 1 },
  { id := "q2_cstar_omegaomegastar__forward", left := .omega, right := .omegaStar, output := .cStar, coefficient := 1 },
  { id := "q2_cstar_omegaomegastar__reverse", left := .omegaStar, right := .omega, output := .cStar, coefficient := 1 },
  { id := "q2_omegastar_hhstar__forward", left := .h, right := .hStar, output := .omegaStar, coefficient := 1 },
  { id := "q2_omegastar_hhstar__reverse", left := .hStar, right := .h, output := .omegaStar, coefficient := 1 },
  { id := "q2_omegastar_comegastar__forward", left := .c, right := .omegaStar, output := .omegaStar, coefficient := 1 },
  { id := "q2_omegastar_comegastar__reverse", left := .omegaStar, right := .c, output := .omegaStar, coefficient := 1 }
]

def ternaryOperation : TernaryOperation :=
  { id := "q3_hstar_hhh", first := .h, second := .h, third := .h,
    output := .hStar, coefficient := 1 }

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
          { output := outer.output, inputs := [a, b, last], path :=
            { kind := .q2q2, firstComponent := outer.id, secondComponent := .some inner.id,
              innerPositions := [0, 1], lastPosition := .some 2, slot := .none,
              multiplier := base } },
          { output := outer.output, inputs := [a, last, b], path :=
            { kind := .q2q2, firstComponent := outer.id, secondComponent := .some inner.id,
              innerPositions := [0, 2], lastPosition := .some 1, slot := .none,
              multiplier := base * swapSign b last } },
          { output := outer.output, inputs := [last, a, b], path :=
            { kind := .q2q2, firstComponent := outer.id, secondComponent := .some inner.id,
              innerPositions := [1, 2], lastPosition := .some 0, slot := .none,
              multiplier := base * frontSign last a b } }
        ]
      else []

def q1q3Path (unary : UnaryOperation) : PathRecord :=
  { kind := .q1q3, firstComponent := unary.id,
    secondComponent := .some ternaryOperation.id, innerPositions := [],
    lastPosition := .none, slot := .none,
    multiplier := unary.coefficient * ternaryOperation.coefficient }

def q3q1Path (unary : UnaryOperation) (slot : Nat) (sign : Int) : PathRecord :=
  { kind := .q3q1, firstComponent := unary.id,
    secondComponent := .some ternaryOperation.id, innerPositions := [],
    lastPosition := .none, slot := .some slot,
    multiplier := unary.coefficient * ternaryOperation.coefficient * sign }

def q1q3TypedPaths : List TypedPath :=
  unaryOperations.flatMap fun unary =>
    if unary.input = ternaryOperation.output then
      [{ output := unary.output,
         inputs := [ternaryOperation.first, ternaryOperation.second, ternaryOperation.third],
         path := q1q3Path unary }]
    else []

def q3q1TypedPaths : List TypedPath :=
  unaryOperations.flatMap fun unary =>
    if unary.output = ternaryOperation.first then
      [
        { output := ternaryOperation.output,
           inputs := [unary.input, ternaryOperation.second, ternaryOperation.third],
           path := q3q1Path unary 0 1 },
        { output := ternaryOperation.output,
           inputs := [ternaryOperation.first, unary.input, ternaryOperation.third],
           path := q3q1Path unary 1
             (if grassmannOdd ternaryOperation.first then -1 else 1) },
        { output := ternaryOperation.output,
           inputs := [ternaryOperation.first, ternaryOperation.second, unary.input],
           path := q3q1Path unary 2
             (twoPrecedingSign ternaryOperation.first ternaryOperation.second) }
      ]
    else []

def allTypedPaths : List TypedPath :=
  q2q2TypedPaths ++ q1q3TypedPaths ++ q3q1TypedPaths

def pathsAt (output : Generator) (inputs : List Generator) : List PathRecord :=
  allTypedPaths.filterMap fun candidate =>
    if candidate.output = output && candidate.inputs = inputs then .some candidate.path else .none

def sourceChannelShapes : List ChannelShape :=
  channels.map fun channel =>
    { output := channel.output, inputs := channel.inputs, paths := channel.paths }

def pathInventoryMatchesOutput (output : Generator) : Bool :=
  (sourceChannelShapes.filter fun channel => channel.output = output).all fun channel =>
    channel.paths = pathsAt channel.output channel.inputs

def rawChannelValues : List RawChannelValues := [
  { output := .c, inputs := [.c, .c, .c], rawPathValues := [
      [(-2 / 3 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(2 / 3 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)]
    ] },
  { output := .cStar, inputs := [.c, .c, .cStar], rawPathValues := [
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (2 / 9 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (-2 / 9 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)]
    ] },
  { output := .cStar, inputs := [.c, .cStar, .c], rawPathValues := [
      [(-1 : ℚ), (0 : ℚ), (-3 / 2 : ℚ), (0 : ℚ)],
      [(-1 / 3 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(-4 / 3 : ℚ), (0 : ℚ), (-3 / 2 : ℚ), (0 : ℚ)]
    ] },
  { output := .cStar, inputs := [.c, .h, .hStar], rawPathValues := [
      [(2 / 3 : ℚ), (0 : ℚ), (0 : ℚ), (-27 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (-8 / 3 : ℚ)],
      [(2 / 3 : ℚ), (0 : ℚ), (0 : ℚ), (-89 / 3 : ℚ)]
    ] },
  { output := .cStar, inputs := [.c, .hStar, .h], rawPathValues := [
      [(-8 : ℚ), (-2 : ℚ), (-3 : ℚ), (0 : ℚ)],
      [(-26 / 3 : ℚ), (5 / 2 : ℚ), (0 : ℚ), (16 : ℚ)],
      [(-50 / 3 : ℚ), (1 / 2 : ℚ), (-3 : ℚ), (16 : ℚ)]
    ] },
  { output := .cStar, inputs := [.c, .omega, .omegaStar], rawPathValues := [
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)]
    ] },
  { output := .cStar, inputs := [.c, .omegaStar, .omega], rawPathValues := [
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)]
    ] },
  { output := .cStar, inputs := [.cStar, .c, .c], rawPathValues := [
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)]
    ] },
  { output := .cStar, inputs := [.h, .c, .hStar], rawPathValues := [
      [(0 : ℚ), (10 : ℚ), (4 / 3 : ℚ), (-49 / 9 : ℚ)],
      [(-8 / 3 : ℚ), (-10 : ℚ), (0 : ℚ), (10 : ℚ)],
      [(-8 / 3 : ℚ), (0 : ℚ), (4 / 3 : ℚ), (41 / 9 : ℚ)]
    ] },
  { output := .cStar, inputs := [.h, .h, .h], rawPathValues := [
      [(1 : ℚ), (2 / 3 : ℚ), (-4 / 9 : ℚ), (-3929 / 54 : ℚ)],
      [(-44 / 3 : ℚ), (0 : ℚ), (-8 / 9 : ℚ), (889 / 9 : ℚ)],
      [(5 / 9 : ℚ), (-133 / 9 : ℚ), (-49 / 9 : ℚ), (-375 / 4 : ℚ)],
      [(118 / 9 : ℚ), (127 / 9 : ℚ), (61 / 9 : ℚ), (7315 / 108 : ℚ)]
    ] },
  { output := .cStar, inputs := [.h, .hStar, .c], rawPathValues := [
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(-20 / 9 : ℚ), (0 : ℚ), (-100 / 9 : ℚ), (0 : ℚ)],
      [(-20 / 9 : ℚ), (0 : ℚ), (-100 / 9 : ℚ), (0 : ℚ)]
    ] },
  { output := .cStar, inputs := [.h, .hStar, .omega], rawPathValues := [
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)]
    ] },
  { output := .cStar, inputs := [.h, .omega, .hStar], rawPathValues := [
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)]
    ] },
  { output := .cStar, inputs := [.hStar, .c, .h], rawPathValues := [
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (16 : ℚ)],
      [(-32 / 9 : ℚ), (-5 / 3 : ℚ), (0 : ℚ), (-6 : ℚ)],
      [(-32 / 9 : ℚ), (-5 / 3 : ℚ), (0 : ℚ), (10 : ℚ)]
    ] },
  { output := .cStar, inputs := [.hStar, .h, .c], rawPathValues := [
      [(8 / 3 : ℚ), (-8 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(-2 : ℚ), (8 : ℚ), (0 : ℚ), (8 / 3 : ℚ)],
      [(2 / 3 : ℚ), (0 : ℚ), (0 : ℚ), (8 / 3 : ℚ)]
    ] },
  { output := .cStar, inputs := [.hStar, .h, .omega], rawPathValues := [
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)]
    ] },
  { output := .cStar, inputs := [.hStar, .omega, .h], rawPathValues := [
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)]
    ] },
  { output := .cStar, inputs := [.omega, .c, .omegaStar], rawPathValues := [
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)]
    ] },
  { output := .cStar, inputs := [.omega, .h, .hStar], rawPathValues := [
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)]
    ] },
  { output := .cStar, inputs := [.omega, .hStar, .h], rawPathValues := [
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (8 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (-8 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)]
    ] },
  { output := .cStar, inputs := [.omega, .omegaStar, .c], rawPathValues := [
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)]
    ] },
  { output := .cStar, inputs := [.omegaStar, .c, .omega], rawPathValues := [
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)]
    ] },
  { output := .cStar, inputs := [.omegaStar, .omega, .c], rawPathValues := [
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)]
    ] },
  { output := .h, inputs := [.c, .c, .h], rawPathValues := [
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (-70 / 9 : ℚ), (0 : ℚ), (0 : ℚ), (-5 / 6 : ℚ), (4 / 3 : ℚ), (-5 / 4 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (-2 / 9 : ℚ), (0 : ℚ), (0 : ℚ), (-1 / 2 : ℚ), (0 : ℚ), (5 / 4 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (-8 : ℚ), (0 : ℚ), (0 : ℚ), (-4 / 3 : ℚ), (4 / 3 : ℚ), (0 : ℚ), (0 : ℚ)]
    ] },
  { output := .h, inputs := [.c, .h, .c], rawPathValues := [
      [(-2 : ℚ), (4 : ℚ), (-3 / 2 : ℚ), (0 : ℚ), (0 : ℚ), (6 : ℚ), (0 : ℚ), (0 : ℚ), (2 : ℚ), (0 : ℚ)],
      [(-4 / 3 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (-10 / 9 : ℚ), (1 / 3 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(-10 / 3 : ℚ), (4 : ℚ), (-3 / 2 : ℚ), (0 : ℚ), (0 : ℚ), (6 : ℚ), (-10 / 9 : ℚ), (1 / 3 : ℚ), (2 : ℚ), (0 : ℚ)]
    ] },
  { output := .h, inputs := [.c, .h, .omega], rawPathValues := [
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)]
    ] },
  { output := .h, inputs := [.c, .omega, .h], rawPathValues := [
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)]
    ] },
  { output := .h, inputs := [.h, .c, .c], rawPathValues := [
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (-4 / 3 : ℚ), (0 : ℚ), (2 / 3 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (4 / 3 : ℚ), (0 : ℚ), (-2 / 3 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)]
    ] },
  { output := .h, inputs := [.h, .c, .omega], rawPathValues := [
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)]
    ] },
  { output := .h, inputs := [.h, .omega, .c], rawPathValues := [
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)]
    ] },
  { output := .h, inputs := [.h, .omega, .omega], rawPathValues := [
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)]
    ] },
  { output := .h, inputs := [.omega, .c, .h], rawPathValues := [
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)]
    ] },
  { output := .h, inputs := [.omega, .h, .c], rawPathValues := [
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)]
    ] },
  { output := .h, inputs := [.omega, .h, .omega], rawPathValues := [
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)]
    ] },
  { output := .h, inputs := [.omega, .omega, .h], rawPathValues := [
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)]
    ] },
  { output := .hStar, inputs := [.c, .c, .hStar], rawPathValues := [
      [(-4 / 3 : ℚ), (5 / 2 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (-1 : ℚ), (0 : ℚ), (2 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (-1 / 3 : ℚ), (0 : ℚ), (2 / 3 : ℚ), (0 : ℚ)],
      [(-4 / 3 : ℚ), (5 / 2 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (-4 / 3 : ℚ), (0 : ℚ), (8 / 3 : ℚ), (0 : ℚ)]
    ] },
  { output := .hStar, inputs := [.c, .h, .h], rawPathValues := [
      [(64 / 27 : ℚ), (-8255 / 108 : ℚ), (23 / 18 : ℚ), (-88 / 3 : ℚ), (148 / 27 : ℚ), (-337 / 216 : ℚ), (-661 / 36 : ℚ), (97 / 27 : ℚ), (-3211 / 216 : ℚ), (-100 / 27 : ℚ)],
      [(661 / 18 : ℚ), (-3019 / 36 : ℚ), (517 / 18 : ℚ), (-331 / 18 : ℚ), (127 / 9 : ℚ), (515 / 36 : ℚ), (-223 / 18 : ℚ), (182 / 9 : ℚ), (86 / 3 : ℚ), (26 / 9 : ℚ)],
      [(92 / 9 : ℚ), (-1025 / 36 : ℚ), (73 / 18 : ℚ), (-521 / 36 : ℚ), (64 / 9 : ℚ), (629 / 216 : ℚ), (-19 / 9 : ℚ), (83 / 9 : ℚ), (337 / 216 : ℚ), (26 / 9 : ℚ)],
      [(-1559 / 54 : ℚ), (14237 / 108 : ℚ), (-467 / 18 : ℚ), (133 / 4 : ℚ), (-337 / 27 : ℚ), (-59 / 6 : ℚ), (1031 / 36 : ℚ), (-394 / 27 : ℚ), (-661 / 54 : ℚ), (100 / 27 : ℚ)]
    ] },
  { output := .hStar, inputs := [.c, .hStar, .c], rawPathValues := [
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (2 : ℚ)],
      [(2 / 3 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (-10 / 9 : ℚ), (1 / 3 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(2 / 3 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (-10 / 9 : ℚ), (1 / 3 : ℚ), (0 : ℚ), (2 : ℚ)]
    ] },
  { output := .hStar, inputs := [.c, .hStar, .omega], rawPathValues := [
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)]
    ] },
  { output := .hStar, inputs := [.c, .omega, .hStar], rawPathValues := [
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)]
    ] },
  { output := .hStar, inputs := [.h, .c, .h], rawPathValues := [
      [(401 / 36 : ℚ), (170 / 9 : ℚ), (-973 / 72 : ℚ), (1211 / 54 : ℚ), (17 / 36 : ℚ), (241 / 72 : ℚ), (-493 / 18 : ℚ), (217 / 9 : ℚ), (-119 / 9 : ℚ), (305 / 9 : ℚ)],
      [(119 / 12 : ℚ), (34 / 9 : ℚ), (-26 / 9 : ℚ), (-41 / 18 : ℚ), (113 / 36 : ℚ), (-3091 / 108 : ℚ), (25 / 36 : ℚ), (37 / 36 : ℚ), (-1445 / 108 : ℚ), (179 / 36 : ℚ)],
      [(1 / 2 : ℚ), (79 / 36 : ℚ), (49 / 24 : ℚ), (35 / 6 : ℚ), (5 / 2 : ℚ), (1 / 24 : ℚ), (-14 / 3 : ℚ), (1 / 4 : ℚ), (-211 / 9 : ℚ), (-65 / 36 : ℚ)],
      [(-185 / 9 : ℚ), (-737 / 36 : ℚ), (166 / 9 : ℚ), (-773 / 54 : ℚ), (-10 / 9 : ℚ), (1367 / 54 : ℚ), (793 / 36 : ℚ), (-224 / 9 : ℚ), (341 / 108 : ℚ), (-122 / 3 : ℚ)]
    ] },
  { output := .hStar, inputs := [.h, .h, .c], rawPathValues := [
      [(203 / 9 : ℚ), (-691 / 72 : ℚ), (203 / 36 : ℚ), (-2389 / 54 : ℚ), (22 / 9 : ℚ), (395 / 9 : ℚ), (-71 / 36 : ℚ), (95 / 9 : ℚ), (-769 / 72 : ℚ), (95 / 9 : ℚ)],
      [(-491 / 27 : ℚ), (-2459 / 216 : ℚ), (46 / 3 : ℚ), (469 / 9 : ℚ), (-421 / 27 : ℚ), (-391 / 18 : ℚ), (-19 / 2 : ℚ), (-49 / 27 : ℚ), (-64 / 3 : ℚ), (-121 / 9 : ℚ)],
      [(-40 / 3 : ℚ), (-979 / 108 : ℚ), (3 : ℚ), (-1837 / 54 : ℚ), (-80 / 9 : ℚ), (-2 / 9 : ℚ), (59 / 12 : ℚ), (-80 / 9 : ℚ), (-397 / 72 : ℚ), (-86 / 9 : ℚ)],
      [(-478 / 27 : ℚ), (143 / 12 : ℚ), (-647 / 36 : ℚ), (-377 / 9 : ℚ), (115 / 27 : ℚ), (-403 / 18 : ℚ), (295 / 18 : ℚ), (-476 / 27 : ℚ), (53 / 2 : ℚ), (-20 / 3 : ℚ)]
    ] },
  { output := .hStar, inputs := [.h, .h, .omega], rawPathValues := [
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)]
    ] },
  { output := .hStar, inputs := [.h, .omega, .h], rawPathValues := [
      [(346 / 9 : ℚ), (3 / 2 : ℚ), (-188 / 3 : ℚ), (-5 / 3 : ℚ), (292 / 9 : ℚ), (-2224 / 27 : ℚ), (76 / 9 : ℚ), (-184 / 3 : ℚ), (-47 / 18 : ℚ), (-770 / 9 : ℚ)],
      [(-38 / 3 : ℚ), (-52 / 3 : ℚ), (-326 / 9 : ℚ), (15 : ℚ), (425 / 9 : ℚ), (2 / 27 : ℚ), (52 / 9 : ℚ), (61 / 3 : ℚ), (58 / 9 : ℚ), (-749 / 9 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(-232 / 9 : ℚ), (95 / 6 : ℚ), (890 / 9 : ℚ), (-40 / 3 : ℚ), (-239 / 3 : ℚ), (2222 / 27 : ℚ), (-128 / 9 : ℚ), (41 : ℚ), (-23 / 6 : ℚ), (1519 / 9 : ℚ)]
    ] },
  { output := .hStar, inputs := [.hStar, .c, .c], rawPathValues := [
      [(4 / 3 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(-4 / 3 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)]
    ] },
  { output := .hStar, inputs := [.hStar, .c, .omega], rawPathValues := [
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)]
    ] },
  { output := .hStar, inputs := [.hStar, .omega, .c], rawPathValues := [
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)]
    ] },
  { output := .hStar, inputs := [.hStar, .omega, .omega], rawPathValues := [
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)]
    ] },
  { output := .hStar, inputs := [.omega, .c, .hStar], rawPathValues := [
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)]
    ] },
  { output := .hStar, inputs := [.omega, .h, .h], rawPathValues := [
      [(80 : ℚ), (142 / 3 : ℚ), (-70 / 9 : ℚ), (188 / 9 : ℚ), (80 : ℚ), (2 : ℚ), (-121 / 18 : ℚ), (80 : ℚ), (12 : ℚ), (40 : ℚ)],
      [(20 / 3 : ℚ), (112 / 3 : ℚ), (425 / 9 : ℚ), (-101 / 3 : ℚ), (80 : ℚ), (-92 / 9 : ℚ), (-272 / 9 : ℚ), (-200 / 3 : ℚ), (3 : ℚ), (-60 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(-260 / 3 : ℚ), (-254 / 3 : ℚ), (-355 / 9 : ℚ), (115 / 9 : ℚ), (-160 : ℚ), (74 / 9 : ℚ), (665 / 18 : ℚ), (-40 / 3 : ℚ), (-15 : ℚ), (20 : ℚ)]
    ] },
  { output := .hStar, inputs := [.omega, .hStar, .c], rawPathValues := [
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)]
    ] },
  { output := .hStar, inputs := [.omega, .hStar, .omega], rawPathValues := [
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)]
    ] },
  { output := .hStar, inputs := [.omega, .omega, .hStar], rawPathValues := [
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)],
      [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)]
    ] },
  { output := .omega, inputs := [.c, .c, .omega], rawPathValues := [
      [(0 : ℚ)],
      [(0 : ℚ)],
      [(0 : ℚ)]
    ] },
  { output := .omega, inputs := [.c, .omega, .c], rawPathValues := [
      [(0 : ℚ)],
      [(2 / 3 : ℚ)],
      [(2 / 3 : ℚ)]
    ] },
  { output := .omega, inputs := [.omega, .c, .c], rawPathValues := [
      [(0 : ℚ)],
      [(0 : ℚ)],
      [(0 : ℚ)]
    ] },
  { output := .omegaStar, inputs := [.c, .c, .omegaStar], rawPathValues := [
      [(0 : ℚ)],
      [(0 : ℚ)],
      [(0 : ℚ)]
    ] },
  { output := .omegaStar, inputs := [.c, .h, .hStar], rawPathValues := [
      [(0 : ℚ)],
      [(0 : ℚ)],
      [(0 : ℚ)]
    ] },
  { output := .omegaStar, inputs := [.c, .hStar, .h], rawPathValues := [
      [(0 : ℚ)],
      [(0 : ℚ)],
      [(0 : ℚ)]
    ] },
  { output := .omegaStar, inputs := [.c, .omegaStar, .c], rawPathValues := [
      [(0 : ℚ)],
      [(2 / 3 : ℚ)],
      [(2 / 3 : ℚ)]
    ] },
  { output := .omegaStar, inputs := [.h, .c, .hStar], rawPathValues := [
      [(80 / 3 : ℚ)],
      [(-80 / 3 : ℚ)],
      [(0 : ℚ)]
    ] },
  { output := .omegaStar, inputs := [.h, .h, .h], rawPathValues := [
      [(-1046 / 9 : ℚ)],
      [(190 / 9 : ℚ)],
      [(-403 / 6 : ℚ)],
      [(2921 / 18 : ℚ)]
    ] },
  { output := .omegaStar, inputs := [.h, .hStar, .c], rawPathValues := [
      [(0 : ℚ)],
      [(0 : ℚ)],
      [(0 : ℚ)]
    ] },
  { output := .omegaStar, inputs := [.h, .hStar, .omega], rawPathValues := [
      [(0 : ℚ)],
      [(0 : ℚ)]
    ] },
  { output := .omegaStar, inputs := [.h, .omega, .hStar], rawPathValues := [
      [(0 : ℚ)],
      [(0 : ℚ)]
    ] },
  { output := .omegaStar, inputs := [.hStar, .c, .h], rawPathValues := [
      [(16 : ℚ)],
      [(-16 : ℚ)],
      [(0 : ℚ)]
    ] },
  { output := .omegaStar, inputs := [.hStar, .h, .c], rawPathValues := [
      [(8 : ℚ)],
      [(-8 : ℚ)],
      [(0 : ℚ)]
    ] },
  { output := .omegaStar, inputs := [.hStar, .h, .omega], rawPathValues := [
      [(0 : ℚ)],
      [(0 : ℚ)]
    ] },
  { output := .omegaStar, inputs := [.hStar, .omega, .h], rawPathValues := [
      [(0 : ℚ)],
      [(0 : ℚ)]
    ] },
  { output := .omegaStar, inputs := [.omega, .h, .hStar], rawPathValues := [
      [(0 : ℚ)],
      [(0 : ℚ)]
    ] },
  { output := .omegaStar, inputs := [.omega, .hStar, .h], rawPathValues := [
      [(0 : ℚ)],
      [(0 : ℚ)]
    ] },
  { output := .omegaStar, inputs := [.omegaStar, .c, .c], rawPathValues := [
      [(0 : ℚ)],
      [(0 : ℚ)],
      [(0 : ℚ)]
    ] }
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
