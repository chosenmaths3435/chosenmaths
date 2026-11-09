-- Every Lean snippet from the video, in order. Check with: lean CurryHoward.lean
-- (Definitions that shadow Lean's own, like Nat and Eq, are shown in the video
-- but left out here; they match Lean's core library.)

variable {α β : Type}

def len : String → Nat := String.length
#eval len "hello"

theorem modus_ponens (P Q : Prop) :
    (P → Q) → P → Q :=
  fun f p => f p

theorem chain (P Q R : Prop) :
    (P → Q) → (Q → R) → (P → R) :=
  fun f g p => g (f p)

def compose (A B C : Type) :
    (A → B) → (B → C) → (A → C) :=
  fun f g a => g (f a)

theorem and_swap (P Q : Prop) :
    P ∧ Q → Q ∧ P :=
  fun ⟨p, q⟩ => ⟨q, p⟩

theorem or_swap (P Q : Prop) :
    P ∨ Q → Q ∨ P :=
  fun h => match h with
    | .inl p => .inr p
    | .inr q => .inl q

theorem explode (P : Prop) :
    False → P :=
  fun h => nomatch h

theorem contra (P Q : Prop) :
    (P → Q) → ¬Q → ¬P :=
  fun f nq p => nq (f p)

theorem nn_em (P : Prop) : ¬¬(P ∨ ¬P) :=
  fun h => h (.inr (fun p => h (.inl p)))

#eval if 91 % 7 = 0 then "yes" else "no"

#check @Classical.em

theorem add_zero' : ∀ n : Nat, n + 0 = n :=
  fun n => rfl

example : (∀ n : Nat, n + 0 = n) =
    ((n : Nat) → n + 0 = n) := rfl

theorem six : ∃ n : Nat, n + n = 6 :=
  ⟨3, rfl⟩

def double : Nat → Nat
  | 0     => 0
  | n + 1 => double n + 2

theorem zero_add' : ∀ n : Nat, 0 + n = n
  | 0     => rfl
  | n + 1 => congrArg (· + 1) (zero_add' n)

def value : List (Fin 2) → Nat
  | []      => 0
  | d :: ds => d + 2 * value ds

def toBinary (n : Nat) :
    { ds : List (Fin 2) // value ds = n } :=
  if h : n = 0 then ⟨[], by simp [value, h]⟩
  else
    have : n / 2 < n := by omega
    let ⟨ds, hds⟩ := toBinary (n / 2)
    ⟨⟨n % 2, by omega⟩ :: ds,
     by simp [value, hds]; omega⟩

#eval (toBinary 13).val

theorem has_binary (n : Nat) :
    ∃ ds : List (Fin 2), value ds = n :=
  ⟨(toBinary n).val, (toBinary n).property⟩

example : 2 + 2 = 4 := rfl

theorem my_symm {a b : α} (h : a = b) :
    b = a :=
  Eq.rec (motive := fun x _ => x = a) rfl h

theorem my_trans {a b c : α}
    (h1 : a = b) (h2 : b = c) : a = c :=
  Eq.rec (motive := fun x _ => a = x) h1 h2

theorem my_congr (f : α → β) {a b : α}
    (h : a = b) : f a = f b :=
  Eq.rec (motive := fun x _ => f a = f x) rfl h

theorem my_subst (P : α → Prop) {a b : α}
    (h : a = b) : P a → P b :=
  fun pa => Eq.rec (motive := fun x _ => P x) pa h

example (a b : Nat) (p q : a = b) : p = q := rfl

namespace Portrait

def toBinary (n : Nat) :
    {ds : List (Fin 2) //
      value ds = n} :=
  if h : n = 0 then
    ⟨[], by simp [value, h]⟩
  else
    have : n / 2 < n := by omega
    let ⟨ds, hds⟩ := toBinary (n / 2)
    ⟨⟨n % 2, by omega⟩ :: ds,
     by simp [value, hds]; omega⟩

#eval (toBinary 13).val

end Portrait
