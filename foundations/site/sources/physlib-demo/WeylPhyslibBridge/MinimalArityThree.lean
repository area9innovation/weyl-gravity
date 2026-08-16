/-
Copyright (c) 2026 Area9 Innovation. All rights reserved.
Released under Apache 2.0 license as described in the repository LICENSE.
Authors: Weyl-gravity programme contributors

GENERATED FILE.  Edit `generate_minimal_arity_three.py`, not this file.
Source SHA-256: ec51e447914516164b0caa51cbecbf12f1a4b2c8b7ecfbd1303f56d17cc095b5
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
def sourceCertificateSha256 : String := "ec51e447914516164b0caa51cbecbf12f1a4b2c8b7ecfbd1303f56d17cc095b5"

def channels : List ChannelRecord := [
  { id := "q1q2q3__c__c__c__c", output := .c, inputs := [.c, .c, .c], paths := [
        { kind := .q2q2, firstComponent := "q2_c_cc", secondComponent := .some "q2_c_cc", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_c_cc", secondComponent := .some "q2_c_cc", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := -1 },
        { kind := .q2q2, firstComponent := "q2_c_cc", secondComponent := .some "q2_c_cc", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := 1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__c_star__c__c__c_star", output := .cStar, inputs := [.c, .c, .cStar], paths := [
        { kind := .q2q2, firstComponent := "q2_cstar_ccstar__forward", secondComponent := .some "q2_c_cc", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_cstar_ccstar__reverse", secondComponent := .some "q2_cstar_ccstar__forward", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_cstar_ccstar__reverse", secondComponent := .some "q2_cstar_ccstar__forward", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := -1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__c_star__c__c_star__c", output := .cStar, inputs := [.c, .cStar, .c], paths := [
        { kind := .q2q2, firstComponent := "q2_cstar_ccstar__forward", secondComponent := .some "q2_c_cc", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_cstar_ccstar__reverse", secondComponent := .some "q2_cstar_ccstar__forward", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_cstar_ccstar__reverse", secondComponent := .some "q2_cstar_ccstar__reverse", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := -1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__c_star__c__h__h_star", output := .cStar, inputs := [.c, .h, .hStar], paths := [
        { kind := .q2q2, firstComponent := "q2_cstar_hhstar__forward", secondComponent := .some "q2_h_ch__forward", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_cstar_hhstar__reverse", secondComponent := .some "q2_hstar_chstar__forward", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_cstar_ccstar__reverse", secondComponent := .some "q2_cstar_hhstar__forward", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := -1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__c_star__c__h_star__h", output := .cStar, inputs := [.c, .hStar, .h], paths := [
        { kind := .q2q2, firstComponent := "q2_cstar_hhstar__forward", secondComponent := .some "q2_h_ch__forward", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_cstar_hhstar__reverse", secondComponent := .some "q2_hstar_chstar__forward", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_cstar_ccstar__reverse", secondComponent := .some "q2_cstar_hhstar__reverse", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := -1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__c_star__c__omega__omega_star", output := .cStar, inputs := [.c, .omega, .omegaStar], paths := [
        { kind := .q2q2, firstComponent := "q2_cstar_ccstar__reverse", secondComponent := .some "q2_cstar_omegaomegastar__forward", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := -1 },
        { kind := .q2q2, firstComponent := "q2_cstar_omegaomegastar__forward", secondComponent := .some "q2_omega_comega__forward", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_cstar_omegaomegastar__reverse", secondComponent := .some "q2_omegastar_comegastar__forward", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := 1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__c_star__c__omega_star__omega", output := .cStar, inputs := [.c, .omegaStar, .omega], paths := [
        { kind := .q2q2, firstComponent := "q2_cstar_ccstar__reverse", secondComponent := .some "q2_cstar_omegaomegastar__reverse", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := -1 },
        { kind := .q2q2, firstComponent := "q2_cstar_omegaomegastar__forward", secondComponent := .some "q2_omega_comega__forward", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_cstar_omegaomegastar__reverse", secondComponent := .some "q2_omegastar_comegastar__forward", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__c_star__c_star__c__c", output := .cStar, inputs := [.cStar, .c, .c], paths := [
        { kind := .q2q2, firstComponent := "q2_cstar_ccstar__forward", secondComponent := .some "q2_c_cc", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_cstar_ccstar__reverse", secondComponent := .some "q2_cstar_ccstar__reverse", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_cstar_ccstar__reverse", secondComponent := .some "q2_cstar_ccstar__reverse", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := -1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__c_star__h__c__h_star", output := .cStar, inputs := [.h, .c, .hStar], paths := [
        { kind := .q2q2, firstComponent := "q2_cstar_hhstar__forward", secondComponent := .some "q2_h_ch__reverse", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_cstar_hhstar__reverse", secondComponent := .some "q2_hstar_chstar__forward", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_cstar_ccstar__reverse", secondComponent := .some "q2_cstar_hhstar__forward", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := -1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__c_star__h__h__h", output := .cStar, inputs := [.h, .h, .h], paths := [
        { kind := .q2q2, firstComponent := "q2_cstar_hhstar__reverse", secondComponent := .some "q2_hstar_hh", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_cstar_hhstar__reverse", secondComponent := .some "q2_hstar_hh", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_cstar_hhstar__reverse", secondComponent := .some "q2_hstar_hh", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := 1 },
        { kind := .q1q3, firstComponent := "q1_cstar_hstar", secondComponent := .some "q3_hstar_hhh", innerPositions := [], lastPosition := .none, slot := .none, multiplier := 1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__c_star__h__h_star__c", output := .cStar, inputs := [.h, .hStar, .c], paths := [
        { kind := .q2q2, firstComponent := "q2_cstar_hhstar__forward", secondComponent := .some "q2_h_ch__reverse", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := -1 },
        { kind := .q2q2, firstComponent := "q2_cstar_hhstar__reverse", secondComponent := .some "q2_hstar_chstar__reverse", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := -1 },
        { kind := .q2q2, firstComponent := "q2_cstar_ccstar__reverse", secondComponent := .some "q2_cstar_hhstar__forward", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__c_star__h__h_star__omega", output := .cStar, inputs := [.h, .hStar, .omega], paths := [
        { kind := .q2q2, firstComponent := "q2_cstar_hhstar__forward", secondComponent := .some "q2_h_omegah__reverse", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := -1 },
        { kind := .q2q2, firstComponent := "q2_cstar_hhstar__reverse", secondComponent := .some "q2_hstar_omegahstar__reverse", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := -1 },
        { kind := .q2q2, firstComponent := "q2_cstar_omegaomegastar__reverse", secondComponent := .some "q2_omegastar_hhstar__forward", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__c_star__h__omega__h_star", output := .cStar, inputs := [.h, .omega, .hStar], paths := [
        { kind := .q2q2, firstComponent := "q2_cstar_hhstar__forward", secondComponent := .some "q2_h_omegah__reverse", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_cstar_hhstar__reverse", secondComponent := .some "q2_hstar_omegahstar__forward", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_cstar_omegaomegastar__reverse", secondComponent := .some "q2_omegastar_hhstar__forward", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := -1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__c_star__h_star__c__h", output := .cStar, inputs := [.hStar, .c, .h], paths := [
        { kind := .q2q2, firstComponent := "q2_cstar_hhstar__forward", secondComponent := .some "q2_h_ch__forward", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := -1 },
        { kind := .q2q2, firstComponent := "q2_cstar_hhstar__reverse", secondComponent := .some "q2_hstar_chstar__reverse", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := -1 },
        { kind := .q2q2, firstComponent := "q2_cstar_ccstar__reverse", secondComponent := .some "q2_cstar_hhstar__reverse", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := 1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__c_star__h_star__h__c", output := .cStar, inputs := [.hStar, .h, .c], paths := [
        { kind := .q2q2, firstComponent := "q2_cstar_hhstar__forward", secondComponent := .some "q2_h_ch__reverse", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := -1 },
        { kind := .q2q2, firstComponent := "q2_cstar_hhstar__reverse", secondComponent := .some "q2_hstar_chstar__reverse", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := -1 },
        { kind := .q2q2, firstComponent := "q2_cstar_ccstar__reverse", secondComponent := .some "q2_cstar_hhstar__reverse", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__c_star__h_star__h__omega", output := .cStar, inputs := [.hStar, .h, .omega], paths := [
        { kind := .q2q2, firstComponent := "q2_cstar_hhstar__forward", secondComponent := .some "q2_h_omegah__reverse", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := -1 },
        { kind := .q2q2, firstComponent := "q2_cstar_hhstar__reverse", secondComponent := .some "q2_hstar_omegahstar__reverse", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := -1 },
        { kind := .q2q2, firstComponent := "q2_cstar_omegaomegastar__reverse", secondComponent := .some "q2_omegastar_hhstar__reverse", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__c_star__h_star__omega__h", output := .cStar, inputs := [.hStar, .omega, .h], paths := [
        { kind := .q2q2, firstComponent := "q2_cstar_hhstar__forward", secondComponent := .some "q2_h_omegah__forward", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := -1 },
        { kind := .q2q2, firstComponent := "q2_cstar_hhstar__reverse", secondComponent := .some "q2_hstar_omegahstar__reverse", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := -1 },
        { kind := .q2q2, firstComponent := "q2_cstar_omegaomegastar__reverse", secondComponent := .some "q2_omegastar_hhstar__reverse", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := 1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__c_star__omega__c__omega_star", output := .cStar, inputs := [.omega, .c, .omegaStar], paths := [
        { kind := .q2q2, firstComponent := "q2_cstar_ccstar__reverse", secondComponent := .some "q2_cstar_omegaomegastar__forward", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_cstar_omegaomegastar__forward", secondComponent := .some "q2_omega_comega__reverse", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := -1 },
        { kind := .q2q2, firstComponent := "q2_cstar_omegaomegastar__reverse", secondComponent := .some "q2_omegastar_comegastar__forward", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := -1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__c_star__omega__h__h_star", output := .cStar, inputs := [.omega, .h, .hStar], paths := [
        { kind := .q2q2, firstComponent := "q2_cstar_hhstar__forward", secondComponent := .some "q2_h_omegah__forward", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_cstar_hhstar__reverse", secondComponent := .some "q2_hstar_omegahstar__forward", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_cstar_omegaomegastar__reverse", secondComponent := .some "q2_omegastar_hhstar__forward", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := -1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__c_star__omega__h_star__h", output := .cStar, inputs := [.omega, .hStar, .h], paths := [
        { kind := .q2q2, firstComponent := "q2_cstar_hhstar__forward", secondComponent := .some "q2_h_omegah__forward", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_cstar_hhstar__reverse", secondComponent := .some "q2_hstar_omegahstar__forward", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_cstar_omegaomegastar__reverse", secondComponent := .some "q2_omegastar_hhstar__reverse", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := -1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__c_star__omega__omega_star__c", output := .cStar, inputs := [.omega, .omegaStar, .c], paths := [
        { kind := .q2q2, firstComponent := "q2_cstar_ccstar__reverse", secondComponent := .some "q2_cstar_omegaomegastar__forward", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_cstar_omegaomegastar__forward", secondComponent := .some "q2_omega_comega__reverse", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := -1 },
        { kind := .q2q2, firstComponent := "q2_cstar_omegaomegastar__reverse", secondComponent := .some "q2_omegastar_comegastar__reverse", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := -1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__c_star__omega_star__c__omega", output := .cStar, inputs := [.omegaStar, .c, .omega], paths := [
        { kind := .q2q2, firstComponent := "q2_cstar_ccstar__reverse", secondComponent := .some "q2_cstar_omegaomegastar__reverse", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := -1 },
        { kind := .q2q2, firstComponent := "q2_cstar_omegaomegastar__forward", secondComponent := .some "q2_omega_comega__forward", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_cstar_omegaomegastar__reverse", secondComponent := .some "q2_omegastar_comegastar__reverse", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__c_star__omega_star__omega__c", output := .cStar, inputs := [.omegaStar, .omega, .c], paths := [
        { kind := .q2q2, firstComponent := "q2_cstar_ccstar__reverse", secondComponent := .some "q2_cstar_omegaomegastar__reverse", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_cstar_omegaomegastar__forward", secondComponent := .some "q2_omega_comega__reverse", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := -1 },
        { kind := .q2q2, firstComponent := "q2_cstar_omegaomegastar__reverse", secondComponent := .some "q2_omegastar_comegastar__reverse", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := -1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__h__c__c__h", output := .h, inputs := [.c, .c, .h], paths := [
        { kind := .q2q2, firstComponent := "q2_h_ch__forward", secondComponent := .some "q2_c_cc", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_h_ch__reverse", secondComponent := .some "q2_h_ch__forward", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_h_ch__reverse", secondComponent := .some "q2_h_ch__forward", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := -1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__h__c__h__c", output := .h, inputs := [.c, .h, .c], paths := [
        { kind := .q2q2, firstComponent := "q2_h_ch__forward", secondComponent := .some "q2_c_cc", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_h_ch__reverse", secondComponent := .some "q2_h_ch__forward", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_h_ch__reverse", secondComponent := .some "q2_h_ch__reverse", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := -1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__h__c__h__omega", output := .h, inputs := [.c, .h, .omega], paths := [
        { kind := .q2q2, firstComponent := "q2_h_ch__reverse", secondComponent := .some "q2_h_omegah__reverse", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := -1 },
        { kind := .q2q2, firstComponent := "q2_h_omegah__forward", secondComponent := .some "q2_omega_comega__forward", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_h_omegah__reverse", secondComponent := .some "q2_h_ch__forward", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__h__c__omega__h", output := .h, inputs := [.c, .omega, .h], paths := [
        { kind := .q2q2, firstComponent := "q2_h_ch__reverse", secondComponent := .some "q2_h_omegah__forward", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := -1 },
        { kind := .q2q2, firstComponent := "q2_h_omegah__forward", secondComponent := .some "q2_omega_comega__forward", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_h_omegah__reverse", secondComponent := .some "q2_h_ch__forward", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := 1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__h__h__c__c", output := .h, inputs := [.h, .c, .c], paths := [
        { kind := .q2q2, firstComponent := "q2_h_ch__forward", secondComponent := .some "q2_c_cc", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_h_ch__reverse", secondComponent := .some "q2_h_ch__reverse", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_h_ch__reverse", secondComponent := .some "q2_h_ch__reverse", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := -1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__h__h__c__omega", output := .h, inputs := [.h, .c, .omega], paths := [
        { kind := .q2q2, firstComponent := "q2_h_ch__reverse", secondComponent := .some "q2_h_omegah__reverse", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := -1 },
        { kind := .q2q2, firstComponent := "q2_h_omegah__forward", secondComponent := .some "q2_omega_comega__forward", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_h_omegah__reverse", secondComponent := .some "q2_h_ch__reverse", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__h__h__omega__c", output := .h, inputs := [.h, .omega, .c], paths := [
        { kind := .q2q2, firstComponent := "q2_h_ch__reverse", secondComponent := .some "q2_h_omegah__reverse", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_h_omegah__forward", secondComponent := .some "q2_omega_comega__reverse", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := -1 },
        { kind := .q2q2, firstComponent := "q2_h_omegah__reverse", secondComponent := .some "q2_h_ch__reverse", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := -1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__h__h__omega__omega", output := .h, inputs := [.h, .omega, .omega], paths := [
        { kind := .q2q2, firstComponent := "q2_h_omegah__reverse", secondComponent := .some "q2_h_omegah__reverse", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_h_omegah__reverse", secondComponent := .some "q2_h_omegah__reverse", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := -1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__h__omega__c__h", output := .h, inputs := [.omega, .c, .h], paths := [
        { kind := .q2q2, firstComponent := "q2_h_ch__reverse", secondComponent := .some "q2_h_omegah__forward", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_h_omegah__forward", secondComponent := .some "q2_omega_comega__reverse", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := -1 },
        { kind := .q2q2, firstComponent := "q2_h_omegah__reverse", secondComponent := .some "q2_h_ch__forward", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := -1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__h__omega__h__c", output := .h, inputs := [.omega, .h, .c], paths := [
        { kind := .q2q2, firstComponent := "q2_h_ch__reverse", secondComponent := .some "q2_h_omegah__forward", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_h_omegah__forward", secondComponent := .some "q2_omega_comega__reverse", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := -1 },
        { kind := .q2q2, firstComponent := "q2_h_omegah__reverse", secondComponent := .some "q2_h_ch__reverse", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := -1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__h__omega__h__omega", output := .h, inputs := [.omega, .h, .omega], paths := [
        { kind := .q2q2, firstComponent := "q2_h_omegah__reverse", secondComponent := .some "q2_h_omegah__forward", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_h_omegah__reverse", secondComponent := .some "q2_h_omegah__reverse", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := -1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__h__omega__omega__h", output := .h, inputs := [.omega, .omega, .h], paths := [
        { kind := .q2q2, firstComponent := "q2_h_omegah__reverse", secondComponent := .some "q2_h_omegah__forward", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_h_omegah__reverse", secondComponent := .some "q2_h_omegah__forward", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := -1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__h_star__c__c__h_star", output := .hStar, inputs := [.c, .c, .hStar], paths := [
        { kind := .q2q2, firstComponent := "q2_hstar_chstar__forward", secondComponent := .some "q2_c_cc", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_hstar_chstar__reverse", secondComponent := .some "q2_hstar_chstar__forward", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_hstar_chstar__reverse", secondComponent := .some "q2_hstar_chstar__forward", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := -1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__h_star__c__h__h", output := .hStar, inputs := [.c, .h, .h], paths := [
        { kind := .q2q2, firstComponent := "q2_hstar_hh", secondComponent := .some "q2_h_ch__forward", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_hstar_hh", secondComponent := .some "q2_h_ch__forward", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_hstar_chstar__reverse", secondComponent := .some "q2_hstar_hh", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := -1 },
        { kind := .q3q1, firstComponent := "q1_h_c", secondComponent := .some "q3_hstar_hhh", innerPositions := [], lastPosition := .none, slot := .some 0, multiplier := 1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__h_star__c__h_star__c", output := .hStar, inputs := [.c, .hStar, .c], paths := [
        { kind := .q2q2, firstComponent := "q2_hstar_chstar__forward", secondComponent := .some "q2_c_cc", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := -1 },
        { kind := .q2q2, firstComponent := "q2_hstar_chstar__reverse", secondComponent := .some "q2_hstar_chstar__forward", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := -1 },
        { kind := .q2q2, firstComponent := "q2_hstar_chstar__reverse", secondComponent := .some "q2_hstar_chstar__reverse", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := 1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__h_star__c__h_star__omega", output := .hStar, inputs := [.c, .hStar, .omega], paths := [
        { kind := .q2q2, firstComponent := "q2_hstar_chstar__reverse", secondComponent := .some "q2_hstar_omegahstar__reverse", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_hstar_omegahstar__forward", secondComponent := .some "q2_omega_comega__forward", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := -1 },
        { kind := .q2q2, firstComponent := "q2_hstar_omegahstar__reverse", secondComponent := .some "q2_hstar_chstar__forward", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := -1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__h_star__c__omega__h_star", output := .hStar, inputs := [.c, .omega, .hStar], paths := [
        { kind := .q2q2, firstComponent := "q2_hstar_chstar__reverse", secondComponent := .some "q2_hstar_omegahstar__forward", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := -1 },
        { kind := .q2q2, firstComponent := "q2_hstar_omegahstar__forward", secondComponent := .some "q2_omega_comega__forward", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_hstar_omegahstar__reverse", secondComponent := .some "q2_hstar_chstar__forward", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := 1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__h_star__h__c__h", output := .hStar, inputs := [.h, .c, .h], paths := [
        { kind := .q2q2, firstComponent := "q2_hstar_hh", secondComponent := .some "q2_h_ch__forward", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_hstar_hh", secondComponent := .some "q2_h_ch__reverse", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_hstar_chstar__reverse", secondComponent := .some "q2_hstar_hh", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := -1 },
        { kind := .q3q1, firstComponent := "q1_h_c", secondComponent := .some "q3_hstar_hhh", innerPositions := [], lastPosition := .none, slot := .some 1, multiplier := 1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__h_star__h__h__c", output := .hStar, inputs := [.h, .h, .c], paths := [
        { kind := .q2q2, firstComponent := "q2_hstar_hh", secondComponent := .some "q2_h_ch__reverse", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_hstar_hh", secondComponent := .some "q2_h_ch__reverse", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_hstar_chstar__reverse", secondComponent := .some "q2_hstar_hh", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := -1 },
        { kind := .q3q1, firstComponent := "q1_h_c", secondComponent := .some "q3_hstar_hhh", innerPositions := [], lastPosition := .none, slot := .some 2, multiplier := 1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__h_star__h__h__omega", output := .hStar, inputs := [.h, .h, .omega], paths := [
        { kind := .q2q2, firstComponent := "q2_hstar_hh", secondComponent := .some "q2_h_omegah__reverse", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_hstar_hh", secondComponent := .some "q2_h_omegah__reverse", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_hstar_omegahstar__reverse", secondComponent := .some "q2_hstar_hh", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := -1 },
        { kind := .q3q1, firstComponent := "q1_h_omega", secondComponent := .some "q3_hstar_hhh", innerPositions := [], lastPosition := .none, slot := .some 2, multiplier := 1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__h_star__h__omega__h", output := .hStar, inputs := [.h, .omega, .h], paths := [
        { kind := .q2q2, firstComponent := "q2_hstar_hh", secondComponent := .some "q2_h_omegah__forward", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_hstar_hh", secondComponent := .some "q2_h_omegah__reverse", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_hstar_omegahstar__reverse", secondComponent := .some "q2_hstar_hh", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := -1 },
        { kind := .q3q1, firstComponent := "q1_h_omega", secondComponent := .some "q3_hstar_hhh", innerPositions := [], lastPosition := .none, slot := .some 1, multiplier := 1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__h_star__h_star__c__c", output := .hStar, inputs := [.hStar, .c, .c], paths := [
        { kind := .q2q2, firstComponent := "q2_hstar_chstar__forward", secondComponent := .some "q2_c_cc", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_hstar_chstar__reverse", secondComponent := .some "q2_hstar_chstar__reverse", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_hstar_chstar__reverse", secondComponent := .some "q2_hstar_chstar__reverse", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := -1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__h_star__h_star__c__omega", output := .hStar, inputs := [.hStar, .c, .omega], paths := [
        { kind := .q2q2, firstComponent := "q2_hstar_chstar__reverse", secondComponent := .some "q2_hstar_omegahstar__reverse", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := -1 },
        { kind := .q2q2, firstComponent := "q2_hstar_omegahstar__forward", secondComponent := .some "q2_omega_comega__forward", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_hstar_omegahstar__reverse", secondComponent := .some "q2_hstar_chstar__reverse", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__h_star__h_star__omega__c", output := .hStar, inputs := [.hStar, .omega, .c], paths := [
        { kind := .q2q2, firstComponent := "q2_hstar_chstar__reverse", secondComponent := .some "q2_hstar_omegahstar__reverse", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_hstar_omegahstar__forward", secondComponent := .some "q2_omega_comega__reverse", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := -1 },
        { kind := .q2q2, firstComponent := "q2_hstar_omegahstar__reverse", secondComponent := .some "q2_hstar_chstar__reverse", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := -1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__h_star__h_star__omega__omega", output := .hStar, inputs := [.hStar, .omega, .omega], paths := [
        { kind := .q2q2, firstComponent := "q2_hstar_omegahstar__reverse", secondComponent := .some "q2_hstar_omegahstar__reverse", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_hstar_omegahstar__reverse", secondComponent := .some "q2_hstar_omegahstar__reverse", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := -1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__h_star__omega__c__h_star", output := .hStar, inputs := [.omega, .c, .hStar], paths := [
        { kind := .q2q2, firstComponent := "q2_hstar_chstar__reverse", secondComponent := .some "q2_hstar_omegahstar__forward", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_hstar_omegahstar__forward", secondComponent := .some "q2_omega_comega__reverse", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := -1 },
        { kind := .q2q2, firstComponent := "q2_hstar_omegahstar__reverse", secondComponent := .some "q2_hstar_chstar__forward", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := -1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__h_star__omega__h__h", output := .hStar, inputs := [.omega, .h, .h], paths := [
        { kind := .q2q2, firstComponent := "q2_hstar_hh", secondComponent := .some "q2_h_omegah__forward", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_hstar_hh", secondComponent := .some "q2_h_omegah__forward", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_hstar_omegahstar__reverse", secondComponent := .some "q2_hstar_hh", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := -1 },
        { kind := .q3q1, firstComponent := "q1_h_omega", secondComponent := .some "q3_hstar_hhh", innerPositions := [], lastPosition := .none, slot := .some 0, multiplier := 1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__h_star__omega__h_star__c", output := .hStar, inputs := [.omega, .hStar, .c], paths := [
        { kind := .q2q2, firstComponent := "q2_hstar_chstar__reverse", secondComponent := .some "q2_hstar_omegahstar__forward", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := -1 },
        { kind := .q2q2, firstComponent := "q2_hstar_omegahstar__forward", secondComponent := .some "q2_omega_comega__reverse", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_hstar_omegahstar__reverse", secondComponent := .some "q2_hstar_chstar__reverse", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := 1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__h_star__omega__h_star__omega", output := .hStar, inputs := [.omega, .hStar, .omega], paths := [
        { kind := .q2q2, firstComponent := "q2_hstar_omegahstar__reverse", secondComponent := .some "q2_hstar_omegahstar__forward", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := -1 },
        { kind := .q2q2, firstComponent := "q2_hstar_omegahstar__reverse", secondComponent := .some "q2_hstar_omegahstar__reverse", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := 1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__h_star__omega__omega__h_star", output := .hStar, inputs := [.omega, .omega, .hStar], paths := [
        { kind := .q2q2, firstComponent := "q2_hstar_omegahstar__reverse", secondComponent := .some "q2_hstar_omegahstar__forward", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_hstar_omegahstar__reverse", secondComponent := .some "q2_hstar_omegahstar__forward", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := -1 }
      ], defect := [(0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] },
  { id := "q1q2q3__omega__c__c__omega", output := .omega, inputs := [.c, .c, .omega], paths := [
        { kind := .q2q2, firstComponent := "q2_omega_comega__forward", secondComponent := .some "q2_c_cc", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_omega_comega__reverse", secondComponent := .some "q2_omega_comega__forward", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_omega_comega__reverse", secondComponent := .some "q2_omega_comega__forward", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := -1 }
      ], defect := [(0 : ℚ)] },
  { id := "q1q2q3__omega__c__omega__c", output := .omega, inputs := [.c, .omega, .c], paths := [
        { kind := .q2q2, firstComponent := "q2_omega_comega__forward", secondComponent := .some "q2_c_cc", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := -1 },
        { kind := .q2q2, firstComponent := "q2_omega_comega__reverse", secondComponent := .some "q2_omega_comega__forward", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := -1 },
        { kind := .q2q2, firstComponent := "q2_omega_comega__reverse", secondComponent := .some "q2_omega_comega__reverse", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := 1 }
      ], defect := [(0 : ℚ)] },
  { id := "q1q2q3__omega__omega__c__c", output := .omega, inputs := [.omega, .c, .c], paths := [
        { kind := .q2q2, firstComponent := "q2_omega_comega__forward", secondComponent := .some "q2_c_cc", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_omega_comega__reverse", secondComponent := .some "q2_omega_comega__reverse", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_omega_comega__reverse", secondComponent := .some "q2_omega_comega__reverse", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := -1 }
      ], defect := [(0 : ℚ)] },
  { id := "q1q2q3__omega_star__c__c__omega_star", output := .omegaStar, inputs := [.c, .c, .omegaStar], paths := [
        { kind := .q2q2, firstComponent := "q2_omegastar_comegastar__forward", secondComponent := .some "q2_c_cc", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_omegastar_comegastar__reverse", secondComponent := .some "q2_omegastar_comegastar__forward", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_omegastar_comegastar__reverse", secondComponent := .some "q2_omegastar_comegastar__forward", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := -1 }
      ], defect := [(0 : ℚ)] },
  { id := "q1q2q3__omega_star__c__h__h_star", output := .omegaStar, inputs := [.c, .h, .hStar], paths := [
        { kind := .q2q2, firstComponent := "q2_omegastar_hhstar__forward", secondComponent := .some "q2_h_ch__forward", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_omegastar_hhstar__reverse", secondComponent := .some "q2_hstar_chstar__forward", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_omegastar_comegastar__reverse", secondComponent := .some "q2_omegastar_hhstar__forward", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := -1 }
      ], defect := [(0 : ℚ)] },
  { id := "q1q2q3__omega_star__c__h_star__h", output := .omegaStar, inputs := [.c, .hStar, .h], paths := [
        { kind := .q2q2, firstComponent := "q2_omegastar_hhstar__forward", secondComponent := .some "q2_h_ch__forward", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_omegastar_hhstar__reverse", secondComponent := .some "q2_hstar_chstar__forward", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_omegastar_comegastar__reverse", secondComponent := .some "q2_omegastar_hhstar__reverse", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := -1 }
      ], defect := [(0 : ℚ)] },
  { id := "q1q2q3__omega_star__c__omega_star__c", output := .omegaStar, inputs := [.c, .omegaStar, .c], paths := [
        { kind := .q2q2, firstComponent := "q2_omegastar_comegastar__forward", secondComponent := .some "q2_c_cc", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_omegastar_comegastar__reverse", secondComponent := .some "q2_omegastar_comegastar__forward", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_omegastar_comegastar__reverse", secondComponent := .some "q2_omegastar_comegastar__reverse", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := -1 }
      ], defect := [(0 : ℚ)] },
  { id := "q1q2q3__omega_star__h__c__h_star", output := .omegaStar, inputs := [.h, .c, .hStar], paths := [
        { kind := .q2q2, firstComponent := "q2_omegastar_hhstar__forward", secondComponent := .some "q2_h_ch__reverse", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_omegastar_hhstar__reverse", secondComponent := .some "q2_hstar_chstar__forward", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_omegastar_comegastar__reverse", secondComponent := .some "q2_omegastar_hhstar__forward", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := -1 }
      ], defect := [(0 : ℚ)] },
  { id := "q1q2q3__omega_star__h__h__h", output := .omegaStar, inputs := [.h, .h, .h], paths := [
        { kind := .q2q2, firstComponent := "q2_omegastar_hhstar__reverse", secondComponent := .some "q2_hstar_hh", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_omegastar_hhstar__reverse", secondComponent := .some "q2_hstar_hh", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_omegastar_hhstar__reverse", secondComponent := .some "q2_hstar_hh", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := 1 },
        { kind := .q1q3, firstComponent := "q1_omegastar_hstar", secondComponent := .some "q3_hstar_hhh", innerPositions := [], lastPosition := .none, slot := .none, multiplier := 1 }
      ], defect := [(0 : ℚ)] },
  { id := "q1q2q3__omega_star__h__h_star__c", output := .omegaStar, inputs := [.h, .hStar, .c], paths := [
        { kind := .q2q2, firstComponent := "q2_omegastar_hhstar__forward", secondComponent := .some "q2_h_ch__reverse", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := -1 },
        { kind := .q2q2, firstComponent := "q2_omegastar_hhstar__reverse", secondComponent := .some "q2_hstar_chstar__reverse", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := -1 },
        { kind := .q2q2, firstComponent := "q2_omegastar_comegastar__reverse", secondComponent := .some "q2_omegastar_hhstar__forward", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 }
      ], defect := [(0 : ℚ)] },
  { id := "q1q2q3__omega_star__h__h_star__omega", output := .omegaStar, inputs := [.h, .hStar, .omega], paths := [
        { kind := .q2q2, firstComponent := "q2_omegastar_hhstar__forward", secondComponent := .some "q2_h_omegah__reverse", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := -1 },
        { kind := .q2q2, firstComponent := "q2_omegastar_hhstar__reverse", secondComponent := .some "q2_hstar_omegahstar__reverse", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := -1 }
      ], defect := [(0 : ℚ)] },
  { id := "q1q2q3__omega_star__h__omega__h_star", output := .omegaStar, inputs := [.h, .omega, .hStar], paths := [
        { kind := .q2q2, firstComponent := "q2_omegastar_hhstar__forward", secondComponent := .some "q2_h_omegah__reverse", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_omegastar_hhstar__reverse", secondComponent := .some "q2_hstar_omegahstar__forward", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := 1 }
      ], defect := [(0 : ℚ)] },
  { id := "q1q2q3__omega_star__h_star__c__h", output := .omegaStar, inputs := [.hStar, .c, .h], paths := [
        { kind := .q2q2, firstComponent := "q2_omegastar_hhstar__forward", secondComponent := .some "q2_h_ch__forward", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := -1 },
        { kind := .q2q2, firstComponent := "q2_omegastar_hhstar__reverse", secondComponent := .some "q2_hstar_chstar__reverse", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := -1 },
        { kind := .q2q2, firstComponent := "q2_omegastar_comegastar__reverse", secondComponent := .some "q2_omegastar_hhstar__reverse", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := 1 }
      ], defect := [(0 : ℚ)] },
  { id := "q1q2q3__omega_star__h_star__h__c", output := .omegaStar, inputs := [.hStar, .h, .c], paths := [
        { kind := .q2q2, firstComponent := "q2_omegastar_hhstar__forward", secondComponent := .some "q2_h_ch__reverse", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := -1 },
        { kind := .q2q2, firstComponent := "q2_omegastar_hhstar__reverse", secondComponent := .some "q2_hstar_chstar__reverse", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := -1 },
        { kind := .q2q2, firstComponent := "q2_omegastar_comegastar__reverse", secondComponent := .some "q2_omegastar_hhstar__reverse", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 }
      ], defect := [(0 : ℚ)] },
  { id := "q1q2q3__omega_star__h_star__h__omega", output := .omegaStar, inputs := [.hStar, .h, .omega], paths := [
        { kind := .q2q2, firstComponent := "q2_omegastar_hhstar__forward", secondComponent := .some "q2_h_omegah__reverse", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := -1 },
        { kind := .q2q2, firstComponent := "q2_omegastar_hhstar__reverse", secondComponent := .some "q2_hstar_omegahstar__reverse", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := -1 }
      ], defect := [(0 : ℚ)] },
  { id := "q1q2q3__omega_star__h_star__omega__h", output := .omegaStar, inputs := [.hStar, .omega, .h], paths := [
        { kind := .q2q2, firstComponent := "q2_omegastar_hhstar__forward", secondComponent := .some "q2_h_omegah__forward", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := -1 },
        { kind := .q2q2, firstComponent := "q2_omegastar_hhstar__reverse", secondComponent := .some "q2_hstar_omegahstar__reverse", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := -1 }
      ], defect := [(0 : ℚ)] },
  { id := "q1q2q3__omega_star__omega__h__h_star", output := .omegaStar, inputs := [.omega, .h, .hStar], paths := [
        { kind := .q2q2, firstComponent := "q2_omegastar_hhstar__forward", secondComponent := .some "q2_h_omegah__forward", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_omegastar_hhstar__reverse", secondComponent := .some "q2_hstar_omegahstar__forward", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := 1 }
      ], defect := [(0 : ℚ)] },
  { id := "q1q2q3__omega_star__omega__h_star__h", output := .omegaStar, inputs := [.omega, .hStar, .h], paths := [
        { kind := .q2q2, firstComponent := "q2_omegastar_hhstar__forward", secondComponent := .some "q2_h_omegah__forward", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_omegastar_hhstar__reverse", secondComponent := .some "q2_hstar_omegahstar__forward", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 }
      ], defect := [(0 : ℚ)] },
  { id := "q1q2q3__omega_star__omega_star__c__c", output := .omegaStar, inputs := [.omegaStar, .c, .c], paths := [
        { kind := .q2q2, firstComponent := "q2_omegastar_comegastar__forward", secondComponent := .some "q2_c_cc", innerPositions := [1, 2], lastPosition := .some 0, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_omegastar_comegastar__reverse", secondComponent := .some "q2_omegastar_comegastar__reverse", innerPositions := [0, 1], lastPosition := .some 2, slot := .none, multiplier := 1 },
        { kind := .q2q2, firstComponent := "q2_omegastar_comegastar__reverse", secondComponent := .some "q2_omegastar_comegastar__reverse", innerPositions := [0, 2], lastPosition := .some 1, slot := .none, multiplier := -1 }
      ], defect := [(0 : ℚ)] }
]

def mutationWitnesses : List MutationWitness := [
  { channelId := "q1q2q3__omega_star__h__h__h", kind := .q1q3, defect := [(2921 / 18 : ℚ)] },
  { channelId := "q1q2q3__h_star__c__h__h", kind := .q3q1, defect := [(-1559 / 54 : ℚ), (14237 / 108 : ℚ), (-467 / 18 : ℚ), (133 / 4 : ℚ), (-337 / 27 : ℚ), (-59 / 6 : ℚ), (1031 / 36 : ℚ), (-394 / 27 : ℚ), (-661 / 54 : ℚ), (100 / 27 : ℚ)] },
  { channelId := "q1q2q3__c__c__c__c", kind := .q2q2, defect := [(-2 / 3 : ℚ), (0 : ℚ), (0 : ℚ), (0 : ℚ)] }
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
