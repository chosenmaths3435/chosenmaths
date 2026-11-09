"""Every Lean snippet shown on screen, exactly as shown.

`python lean_code.py` writes CurryHoward.lean next to this file from the snippets that
should compile, and lean checks it. Snippets in SHOWN_ONLY are simplified types or
deliberate errors; they are not compiled.
"""

import sys
from pathlib import Path

CODE = {
    "len": ['def len : String \u2192 Nat := String.length', '#eval len "hello"'],
    "mp": ["theorem modus_ponens (P Q : Prop) :", "    (P \u2192 Q) \u2192 P \u2192 Q :=", "  fun f p => f p"],
    "chain": ["theorem chain (P Q R : Prop) :", "    (P \u2192 Q) \u2192 (Q \u2192 R) \u2192 (P \u2192 R) :=",
              "  fun f g p => g (f p)"],
    "compose": ["def compose (A B C : Type) :", "    (A \u2192 B) \u2192 (B \u2192 C) \u2192 (A \u2192 C) :=",
                "  fun f g a => g (f a)"],
    "and_swap": ["theorem and_swap (P Q : Prop) :", "    P \u2227 Q \u2192 Q \u2227 P :=",
                 "  fun \u27e8p, q\u27e9 => \u27e8q, p\u27e9"],
    "or_swap": ["theorem or_swap (P Q : Prop) :", "    P \u2228 Q \u2192 Q \u2228 P :=", "  fun h => match h with",
                "    | .inl p => .inr p", "    | .inr q => .inl q"],
    "true": ["inductive True : Prop where", "  | intro : True"],
    "false": ["inductive False : Prop"],
    "explode": ["theorem explode (P : Prop) :", "    False \u2192 P :=", "  fun h => nomatch h"],
    "not": ["def Not (P : Prop) : Prop :=", "  P \u2192 False"],
    "contra": ["theorem contra (P Q : Prop) :", "    (P \u2192 Q) \u2192 \u00acQ \u2192 \u00acP :=",
               "  fun f nq p => nq (f p)"],
    "em": ["theorem em (P : Prop) : P \u2228 \u00acP :=", "  ???"],
    "nn_em": ["theorem nn_em (P : Prop) : \u00ac\u00ac(P \u2228 \u00acP) :=",
              "  fun h => h (.inr (fun p => h (.inl p)))"],
    "dec": ['#eval if 91 % 7 = 0 then "yes" else "no"'],
    "emcheck": ["#check @Classical.em"],
    "decide_any": ["open Classical in", "def decideAnything (P : Prop) : Bool :=", "  if P then true else false"],
    "add_zero": ["theorem add_zero' : \u2200 n : Nat, n + 0 = n :=", "  fun n => rfl"],
    "pi_eq": ["example : (\u2200 n : Nat, n + 0 = n) =", "    ((n : Nat) \u2192 n + 0 = n) := rfl"],
    "six": ["theorem six : \u2203 n : Nat, n + n = 6 :=", "  \u27e83, rfl\u27e9"],
    "nat": ["inductive Nat where", "  | zero : Nat", "  | succ (n : Nat) : Nat"],
    "double": ["def double : Nat \u2192 Nat", "  | 0     => 0", "  | n + 1 => double n + 2"],
    "zero_add": ["theorem zero_add' : \u2200 n : Nat, 0 + n = n", "  | 0     => rfl",
                 "  | n + 1 => congrArg (\u00b7 + 1) (zero_add' n)"],
    "natrec": ["Nat.rec : {motive : Nat \u2192 Sort u}", "  \u2192 motive zero",
               "  \u2192 ((n : Nat) \u2192 motive n \u2192 motive (n + 1))", "  \u2192 (t : Nat) \u2192 motive t"],
    "value": ["def value : List (Fin 2) \u2192 Nat", "  | []      => 0", "  | d :: ds => d + 2 * value ds"],
    "toBinary": ["def toBinary (n : Nat) :", "    { ds : List (Fin 2) // value ds = n } :=",
                 "  if h : n = 0 then \u27e8[], by simp [value, h]\u27e9", "  else",
                 "    have : n / 2 < n := by omega", "    let \u27e8ds, hds\u27e9 := toBinary (n / 2)",
                 "    \u27e8\u27e8n % 2, by omega\u27e9 :: ds,", "     by simp [value, hds]; omega\u27e9"],
    "eval13": ["#eval (toBinary 13).val"],
    "has_binary": ["theorem has_binary (n : Nat) :", "    \u2203 ds : List (Fin 2), value ds = n :=",
                   "  \u27e8(toBinary n).val, (toBinary n).property\u27e9"],
    "digits": ["def digits (n : Nat) : List (Fin 2) :=", "  match has_binary n with",
               "  | \u27e8ds, _\u27e9 => ds"],
    "eq": ["inductive Eq : \u03b1 \u2192 \u03b1 \u2192 Prop where", "  | refl (a : \u03b1) : Eq a a"],
    "twotwo": ["example : 2 + 2 = 4 := rfl"],
    "eqrec": ["Eq.rec : {motive : (b : \u03b1) \u2192 a = b \u2192 Sort u}", "  \u2192 motive a rfl",
              "  \u2192 (h : a = b) \u2192 motive b h"],
    "symm": ["theorem my_symm {a b : \u03b1} (h : a = b) :", "    b = a :=",
             "  Eq.rec (motive := fun x _ => x = a) rfl h"],
    "trans": ["theorem my_trans {a b c : \u03b1}", "    (h1 : a = b) (h2 : b = c) : a = c :=",
              "  Eq.rec (motive := fun x _ => a = x) h1 h2"],
    "congr": ["theorem my_congr (f : \u03b1 \u2192 \u03b2) {a b : \u03b1}", "    (h : a = b) : f a = f b :=",
              "  Eq.rec (motive := fun x _ => f a = f x) rfl h"],
    "subst": ["theorem my_subst (P : \u03b1 \u2192 Prop) {a b : \u03b1}", "    (h : a = b) : P a \u2192 P b :=",
              "  fun pa => Eq.rec (motive := fun x _ => P x) pa h"],
    "pirr": ["example (a b : Nat) (p q : a = b) : p = q := rfl"],
}

# Outputs printed by #eval / #check, and the error messages, as shown.
OUT = {
    "len": "5",
    "dec": '"yes"',
    "emcheck": "Classical.em : \u2200 (p : Prop), p \u2228 \u00acp",
    "eval13": "[1, 0, 1, 1]",
}
ERR = {
    "decide_any": ["failed to compile definition, consider marking it",
                   "as 'noncomputable' because it depends on",
                   "'propDecidable', which is 'noncomputable'"],
    "digits": ["recursor `Exists.casesOn` can only", "eliminate into `Prop`"],
}

# Portrait (shorts) layouts of the same code: narrower lines, same Lean.
CODE_P = {
    "toBinary": ["def toBinary (n : Nat) :", "    {ds : List (Fin 2) //", "      value ds = n} :=",
                 "  if h : n = 0 then", "    \u27e8[], by simp [value, h]\u27e9", "  else",
                 "    have : n / 2 < n := by omega", "    let \u27e8ds, hds\u27e9 := toBinary (n / 2)",
                 "    \u27e8\u27e8n % 2, by omega\u27e9 :: ds,", "     by simp [value, hds]; omega\u27e9"],
    "decide_any": ["open Classical in", "def decideAnything (P : Prop) :", "    Bool :=",
                   "  if P then true else false"],
}
ERR_P = {
    "decide_any": ["failed to compile definition,", "consider marking it as", "'noncomputable' because it",
                   "depends on 'propDecidable',", "which is 'noncomputable'"],
}

SHOWN_ONLY = {"em", "decide_any", "natrec", "digits", "eqrec", "nat", "true", "false", "not", "eq"}


def lean_file():
    out = ["-- Every Lean snippet from the video, in order. Check with: lean CurryHoward.lean",
           "-- (Definitions that shadow Lean's own, like Nat and Eq, are shown in the video",
           "-- but left out here; they match Lean's core library.)", "",
           "variable {\u03b1 \u03b2 : Type}", ""]
    for k, lines in CODE.items():
        if k in SHOWN_ONLY:
            continue
        out += lines + [""]
    out += ["namespace Portrait", ""] + CODE_P["toBinary"] + ["", "#eval (toBinary 13).val", "", "end Portrait", ""]
    return "\n".join(out)


if __name__ == "__main__":
    p = Path(__file__).parent / "CurryHoward.lean"
    p.write_text(lean_file())
    print(p)
    sys.exit(0)
