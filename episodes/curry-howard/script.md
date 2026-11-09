# Proofs are programs

<!-- Code in visual lines is written in ASCII. On screen it uses Lean's usual symbols:
-> is the arrow, /\ and \/ are and/or, ~ is not, <...> are angle brackets, forall
and exists are the quantifier symbols, alpha is the Greek letter. -->

## s01 Hook
> visual: a dark code panel (the Lean style used all episode: monospace, keywords in
> the secondary color). The `toBinary` definition from s07 types itself in, about eight
> lines, with the `value` helper above it in smaller text. At "run" a line
> `#eval (toBinary 13).val` appears under it, and at "thirteen" its output
> `[1, 0, 1, 1]` appears in gold, with a small caption under it:
> "13 = 1 + 0*2 + 1*4 + 1*8" (a centered dot for times on screen).
[b1] Here's a short program. You give it a number, and it hands back that number in
binary. Let's <bookmark mark="run"/>run it on thirteen. Out comes one, zero, one, one.
That's <bookmark mark="thirteen"/>thirteen in binary, with the ones digit first.

> visual: the code stays. At "theorem" the type in the first line,
> `{ ds : List (Fin 2) // value ds = n }`, is boxed, and a plain line appears above
> the panel: "Theorem: every natural number has a binary representation." At "proof"
> a "proof" label is stamped beside the body of the code.
[b2] Now read the same code another way. Its type says that
<bookmark mark="theorem"/>every natural number has a binary representation. That's a
theorem, and this code is its <bookmark mark="proof"/>proof. A proof you can run.

> visual: a small card from the last episode's ending slides in: "a proof is a
> program; a statement is a type". At "literally" it grows to fill the frame. Title
> card at "correspondence": "Proofs are programs", with "the Curry-Howard
> correspondence" under it.
[b3] Last time I said that a proof is a program, and a statement is a type. I meant
that <bookmark mark="literally"/>literally. It's called the Curry-Howard
<bookmark mark="correspondence"/>correspondence. Let's build it up, starting from the
simplest logic there is.

## s02 Implication is a function
> visual: a code panel: `def len : String -> Nat := String.length` and under it
> `#eval len "hello"` with output `5`. At "arrow" the arrow in the type glows.
[b1] All the code here is in Lean. It's a programming language that also checks
proofs. Here's an ordinary function. It takes a string and returns its length, a
natural number. Its type is string, <bookmark mark="arrow"/>arrow, natural number.

> visual: a second panel below: `theorem modus_ponens (P Q : Prop) : (P -> Q) -> P -> Q :=`
> then on the next line `fun f p => f p`. At "statement" the part between the first
> colon and `:=` is boxed and labelled "statement". At "proof" the line after `:=` is
> boxed and labelled "proof".
[b2] And here's a theorem. P and Q are propositions, statements that could be true or
false. After the colon comes the <bookmark mark="statement"/>statement: if P implies
Q, and P is true, then Q is true. After the colon-equals comes the
<bookmark mark="proof"/>proof.

> visual: the arrow in `P -> Q` pulses, and the arrow in `String -> Nat` pulses with it.
> At "function" the word "function" appears over the theorem's arrow.
[b3] Look at the arrow. It's the same arrow as in the function's type. In Lean, a
proof that P implies Q is a <bookmark mark="function"/>function. It takes a proof of
P and gives back a proof of Q.

> visual: in `fun f p => f p`, f is labelled "proof of P -> Q" and p is labelled "proof
> of P". At "apply" an arrow carries p into f, and `f p` is labelled "proof of Q".
[b4] So the proof reads: take f, a proof that P implies Q, and p, a proof of P. Then
<bookmark mark="apply"/>apply f to p, and out comes a proof of Q. Modus ponens, one
of the oldest rules in logic, is calling a function.

> visual: the modus ponens panel shrinks up. New panel:
> `theorem chain (P Q R : Prop) : (P -> Q) -> (Q -> R) -> (P -> R) :=`
> `  fun f g p => g (f p)`
> and under it, at "same":
> `def compose (A B C : Type) : (A -> B) -> (B -> C) -> (A -> C) :=`
> `  fun f g a => g (f a)`
> The two bodies glow together.
[b5] Chaining works the same way. If P implies Q, and Q implies R, then P implies R.
The proof takes p, runs it through f, then through g. That's function composition. It's
the <bookmark mark="same"/>same code you'd write to compose two functions on data.

> visual: the panels clear. A two-column table appears, headed "logic" and "programs",
> with a caption above it: "proposition = type, proof = value of that type". At "row"
> its first row fills in: "P implies Q" | "function from P to Q".
[b6] So here's the start of a dictionary. A proposition is a type. A proof of it is a
value of that type. And <bookmark mark="row"/>"implies" means "function". To prove
something, you write a program with the right type, and Lean checks it the way it
checks the types in any program.

## s03 And, or, true, false
> visual: the table moves to the left third of the screen, small. Code panel on the
> right: `theorem and_swap (P Q : Prop) : P /\ Q -> Q /\ P :=` and
> `  fun <p, q> => <q, p>`. At "pair" the angle brackets glow. At "swap" p and q
> trade places in an animation. Table row at "and": "P and Q" | "pair".
[b1] What's a proof of P and Q? You need a proof of P and a proof of Q. So it's a
<bookmark mark="pair"/>pair. Here's a proof that you can swap the two sides: take the
pair apart, and put it back <bookmark mark="swap"/>together the other way round. So
<bookmark mark="and"/>"and" is a pair.

> visual: new panel: `theorem or_swap (P Q : Prop) : P \/ Q -> Q \/ P :=`
> `  fun h => match h with`
> `    | .inl p => .inr p`
> `    | .inr q => .inl q`
> At "which" the tags `.inl` and `.inr` glow, with labels "left: a proof of P" and
> "right: a proof of Q". At "case" the two match lines light up in turn.
[b2] "Or" is more interesting. A proof of P or Q is a proof of one of them, plus a tag
that says <bookmark mark="which"/>which one: left, here's a proof of P, or right,
here's a proof of Q. To use one, you check the tag and handle each
<bookmark mark="case"/>case.

> visual: table row at "or": "P or Q" | "tagged choice: left or right". The word
> "tag" in the row gets a gold underline that stays.
[b3] Programmers call this a tagged union. So <bookmark mark="or"/>"or" is a tagged
choice. Remember the tag. It comes back soon.

> visual: two definitions side by side: `inductive True : Prop` with one line under it,
> `| intro : True`, and `inductive False : Prop` with nothing under it. At "one" the
> `intro` line glows. At "none" a dashed empty box appears under False.
[b4] Next, true and false. In Lean, true is a type with exactly
<bookmark mark="one"/>one value, so proving it takes no work. False is a type with
<bookmark mark="none"/>no values at all. Its definition is one line with nothing after
it. There's no way to build a proof of false.

> visual: panel: `theorem explode (P : Prop) : False -> P :=` and `  fun h => nomatch h`.
> At "cases" a small checklist titled "cases to handle" appears, empty, and gets a
> tick. Small tag: "ex falso quodlibet".
[b5] But you can use one. If someone hands you a proof of false, you can prove anything
at all. As a program: to use a value, you handle every case of what it could be, and
false has <bookmark mark="cases"/>no cases. So the function is done before it starts.

> visual: definition `def Not (P : Prop) : Prop := P -> False`. At "never" a proof of
> P is fed into it and comes out as a crossed-out "proof of False". Then a panel:
> `theorem contra (P Q : Prop) : (P -> Q) -> ~Q -> ~P :=` and
> `  fun f nq p => nq (f p)`. At "through" p moves through f and then through nq.
[b6] Then "not P" is defined as "P implies false". If you ever had a proof of P, you'd
get a proof of false, so there can <bookmark mark="never"/>never be one. Here's a
proof that if P implies Q, and Q is false, then P is false. Given p, push it through
f, then <bookmark mark="through"/>through not Q, and you land on false.

> visual: table rows fill in: "true" | "a type with one value", "false" | "a type with
> no values", "not P" | "function from P to false". On the right edge a vertical ladder
> appears, labelled "the type system", with its first rung lit: "simple types:
> functions, pairs, tagged choices". Small credit at "Howard": "Curry 1934, Howard
> 1969".
[b7] That's almost all of propositional logic, the logic of and, or, not, and implies.
And it only needs <bookmark mark="simple"/>simple types from the programming language:
functions, pairs, and tagged choices. Haskell Curry noticed the first signs of this in
the nineteen thirties, and William <bookmark mark="Howard"/>Howard wrote it out in full
in nineteen sixty-nine.

## s04 Classical vs intuitionistic
> visual: the ladder and table shrink away. A truth table for "P or not P": two rows,
> P true and P false, last column true in both. At "missing" a code panel opens below:
> `theorem em (P : Prop) : P \/ ~P :=` and `  ???`, the question marks blinking.
[b1] I said almost. One law you learned in school is <bookmark mark="missing"/>missing:
P or not P. Check the truth table. Whatever P is, one side is true. So let's try to
write the program.

> visual: the ??? splits into a fork with two ends: `.inl (a proof of P)` and
> `.inr (a proof of ~P)`. The gold tag underline from s03 reappears under the fork.
> A question mark at "pick": "which one?"
[b2] Remember what a proof of "or" is: a tag, left or right, plus a proof of that side.
So the program has to <bookmark mark="pick"/>pick a side, for any P you give it. And
all it has to go on is P.

> visual: P is replaced by "machine M halts on input w", with the tape-and-head icon
> from the last episode. The fork's ends now read "halts" and "never halts". At
> "halting" the red cross from the last episode stamps over the fork.
[b3] So take a P from last time: machine M halts on input w. A program for P or not P
would take any machine and any input, and tell you which side is true. It would solve
the <bookmark mark="halting"/>halting problem, and no program can. So there's no program
for P or not P, at least not one that gives you a final answer.

> visual: panel: `theorem nn_em (P : Prop) : ~~(P \/ ~P) :=` and
> `  fun h => h (.inr (fun p => h (.inl p)))`. At "first" `.inr` glows; at "switch"
> `.inl p` glows, with an arrow from the inner p to it. A tag under the panel at
> "axioms": "uses no axioms".
[b4] But that doesn't make the law false. In fact, there's a short program proving it
can't be false. Say h claims that P or not P leads to a contradiction. Feed h the
answer <bookmark mark="first"/>"right: not P". To refute "not P", h has to come up
with a proof of P. The moment it does, <bookmark mark="switch"/>switch: answer "left",
with that proof. Now h has refuted a real proof of P or not P, and that's the
contradiction. And it uses no <bookmark mark="axioms"/>axioms.

> visual: two columns. Left: "classical logic", with "P or not P" and a tick. Right:
> "intuitionistic logic", with "P or not P" and an empty box, not a cross. At "which"
> a caption under the right column: "to prove P or Q, say which".
[b5] Logic without this law is called intuitionistic logic. It's what you get when
every proof has to be a program. It doesn't say the law is false. It only refuses to
assume it, unless you can say <bookmark mark="which"/>which side holds.

> visual: panel: `#eval if 91 % 7 = 0 then "yes" else "no"` and the output `"yes"`,
> with "91 = 7 * 13" beside it. At "decidable" a box: "Decidable P: a true-or-false
> answer, plus a proof that the answer is right".
[b6] And often you can say which. Is ninety-one divisible by seven? Compute it: yes,
it's seven times thirteen. Lean calls a proposition <bookmark mark="decidable"/>decidable
when there's a program that computes the answer, and a proof that the answer is right.
That's P or not P, as code that runs.

> visual: panel: `#check @Classical.em` with output `Classical.em : forall (p : Prop), p \/ ~p`.
> At "axiom" an arrow from it down to a box: "axiom Classical.choice", with a small
> "no code" tag.
[b7] Lean does let you use classical logic. It gives you P or not P for every P. But
it proves it from an <bookmark mark="axiom"/>axiom, called choice. And an axiom is a
proof you're told exists, with no program inside.

> visual: panel: `open Classical in` / `def decideAnything (P : Prop) : Bool :=` /
> `  if P then true else false`. At "refuses" the real error appears under it in red:
> "failed to compile definition, consider marking it as 'noncomputable' because it
> depends on 'propDecidable', which is 'noncomputable'". At "noncomputable" that word
> gets a gold underline.
[b8] So what happens if you try to run it? Here's a function that takes any
proposition and returns true or false, using classical logic to choose. Lean
<bookmark mark="refuses"/>refuses to compile it. Classical logic calls every
proposition decidable, but with no program behind it. So Lean asks you to mark the
function <bookmark mark="noncomputable"/>noncomputable.

> visual: the word "noncomputable" stays. Under it, two lines appear at the bookmarks:
> at "true" "classical proof: it's true", at "thing" "constructive proof: it's true,
> and here it is".
[b9] And that word is literal. You can still use this function inside proofs. You
can't run it and get an answer out. So that's the split. A classical proof tells you
something is <bookmark mark="true"/>true. A constructive proof also hands you the
<bookmark mark="thing"/>thing.

## s05 For all, there exists
> visual: the ladder returns on the right, rung one lit. Centre: "for every number n,
> n + 0 = n". At "mentions" the n's in the statement glow.
[b1] So far our propositions were single letters, P and Q. Real math says things about
objects. "For every number n, n plus zero is n." That statement
<bookmark mark="mentions"/>mentions n. What kind of program proves it?

> visual: panel: `theorem add_zero' : forall n : Nat, n + 0 = n :=` and `  fun n => rfl`.
> Beside it, a box with an input slot: 5 goes in and "proof that 5 + 0 = 5" comes
> out; then 12 goes in and "proof that 12 + 0 = 12" comes out.
[b2] A function. You give it a number, and it gives back a proof about
<bookmark mark="that"/>that number. Here the proof is called refl, short for
reflexivity. Lean computes n plus zero, sees that it's n, and accepts. We'll come back
to refl, because there's more to it than it looks.

> visual: two types side by side: `String -> Nat`, with "Nat" labelled "always the
> same", and `(n : Nat) -> n + 0 = n`, with an arrow from the input n into the output
> type. At "depends" that arrow glows. At "same" a line appears under them:
> `example : (forall n : Nat, n + 0 = n) = ((n : Nat) -> n + 0 = n) := rfl`.
[b3] But it's not an ordinary function. The length function always returns a number.
Here the output type <bookmark mark="depends"/>depends on the input. Put in five, and
you get a proof that five plus zero is five. Put in twelve, and the type changes too.
In Lean, "for all" and this kind of arrow are literally the
<bookmark mark="same"/>same type.

> visual: panel: `theorem six : exists n : Nat, n + n = 6 :=` and `  <3, rfl>`. At "pair"
> the angle brackets glow; 3 is labelled "witness", rfl is labelled "proof that
> 3 + 3 = 6". At "second" an arrow from the 3 into the label. At "four" the 3 changes
> to 4 and the label reads "proof that 4 + 4 = 6?" with a red question mark.
[b4] "There exists" works the same way. To prove there's a number n with n plus n
equal to six, you give a <bookmark mark="pair"/>pair: the number three, and a proof
that three plus three is six. Again, the type of the <bookmark mark="second"/>second
part depends on the first. Pick <bookmark mark="four"/>four, and you'd need a proof
that four plus four is six, which you won't find.

> visual: the table returns. New rows: "for all x, P(x)" | "dependent function", and
> "there exists x, P(x)" | "dependent pair". At "dependent" the ladder's second rung
> lights: "dependent types: types that mention values". Small credit at "Lof":
> "Per Martin-Lof, 1970s" (with the umlaut on screen).
[b5] So "for all" is a dependent function, and "there exists" is a dependent pair. To
say these things, the language needs types that can mention values, like the type
"n plus zero is n". These are called <bookmark mark="dependent"/>dependent types. Per
Martin-<bookmark mark="Lof"/>Lof built a type theory around them in the nineteen
seventies, and Lean's is a close relative.

## s06 Induction is recursion
> visual: panel: `inductive Nat where` / `  | zero : Nat` / `  | succ (n : Nat) : Nat`.
> Below, a row of beads: zero, then succ zero, then succ succ zero, each with its
> number under it, 0, 1, 2, then "...".
[b1] Where do numbers come from in Lean? They're <bookmark mark="defined"/>defined, by
two rules. Zero is a number. And if n is a number, then so is the successor of n, the
next one. Every number is zero with successor applied some number of times.

> visual: panel: `def double : Nat -> Nat` / `  | 0     => 0` / `  | n + 1 => double n + 2`.
> At "calls" an arrow loops from `double n` back to the name `double`.
[b2] To write a function on numbers, you handle each rule. Here's doubling. Double of
zero is zero. Double of n plus one is double of n, plus two. That second line
<bookmark mark="calls"/>calls the function on a smaller number. That's recursion.

> visual: under `double`, a second panel with the same layout:
> `theorem zero_add' : forall n : Nat, 0 + n = n` / `  | 0     => rfl` /
> `  | n + 1 => congrArg (. + 1) (zero_add' n)`. The two panels' case lines line up,
> with matching brackets. At "hypothesis" `zero_add' n` is labelled "induction
> hypothesis", and an arrow loops from it back to the name `zero_add'`.
[b3] Now a proof. Zero plus n is n, for every n. This one needs induction, because
Lean's addition works by recursion on the second number, and here that's the unknown
n. It has the same shape as doubling. There's a case for zero, where Lean computes it.
And a case for n plus one, which calls the theorem itself on n, and then adds one to
both sides. That recursive call is the
<bookmark mark="hypothesis"/>induction hypothesis.

> visual: `#check @Nat.rec` and its type, simplified (tag: "simplified"), over four lines:
> `{motive : Nat -> Sort u}` / `-> motive zero` / `-> ((n : Nat) -> motive n -> motive (n + 1))`
> / `-> (t : Nat) -> motive t`. At "zero" the second line is labelled "base case"; at
> "next" the third is labelled "step"; at "every" the last is labelled "for every n".
[b4] In fact, Lean doesn't treat these as different things. From the definition of the
numbers, it builds one function, called Nat dot rec, the recursor. Here's its type. A
value for <bookmark mark="zero"/>zero. A way to get from any n to the
<bookmark mark="next"/>next one. And out comes a value for <bookmark mark="every"/>every
n.

> visual: the word "motive" glows. Two arrows come out of it. At "proposition":
> "a proposition: induction". At "data": "a type of data: recursion".
[b5] Read that type as logic, and it's the principle of induction. Read it as code,
and it's recursion. What decides it is the motive, the thing you're building for each
n. Make it a <bookmark mark="proposition"/>proposition, and you're proving something by
induction. Make it a type of <bookmark mark="data"/>data, and you're writing a
recursive program.

> visual: the table returns with a new row: "induction" | "recursion". At "rung" the
> ladder's third rung lights: "inductive types: each comes with a recursor". Small
> icons for a list and a tree pop up beside it.
[b6] And it's not special to numbers. Lists, trees, anything you build out of
constructors, comes with a recursor, and the recursor's type is the induction principle
for that <bookmark mark="rung"/>shape.

## s07 A theorem you can run
> visual: split screen. Left: a textbook proof in serif type, lines lighting up as they
> are read:
> "Theorem. Every natural number n has a binary representation."
> "Proof. Strong induction on n."
> "If n = 0, take the empty string."
> "Otherwise, write n = 2q + r, with r = 0 or 1."
> "Since q < n, q has a representation."
> "Add r as the new ones digit."
> "Its value is r + 2q = n."
> The right half is empty for now.
[b1] Back to the theorem from the start. Here's the proof the way you'd write it in a
math class. It's by strong induction. You get to assume the result for every
<bookmark mark="smaller"/>smaller number, not only for n minus one.

[b2] If n is zero, the empty string works. Otherwise, divide by two. So n is two q
plus r, where the <bookmark mark="remainder"/>remainder r is zero or one. q is smaller
than n, so q has a representation. Add r as its new ones digit, and the value is r
plus two q, which is n.

> visual: the right half fills with the `value` definition:
> `def value : List (Fin 2) -> Nat` / `  | []      => 0` / `  | d :: ds => d + 2 * value ds`.
> "Fin 2" gets a small gloss: "a digit, 0 or 1".
[b3] Now the Lean version. First, what's a representation? A list of binary digits,
ones digit first, and a function that computes its <bookmark mark="value"/>value: the
first digit, plus two times the value of the rest.

> visual: below `value`, `toBinary` appears line by line, each line joined by a thin
> line to its sentence on the left:
> `def toBinary (n : Nat) : { ds : List (Fin 2) // value ds = n } :=`
> `  if h : n = 0 then <[], by simp [value, h]>` (at "zero", joined to "take the empty
> string")
> `  else`
> `    have : n / 2 < n := by omega` (at "less", joined to "Since q < n")
> `    let <ds, hds> := toBinary (n / 2)` (at "recurse", joined to "q has a
> representation")
> `    <<n % 2, by omega> :: ds, by simp [value, hds]; omega>` (at "front", joined to
> "Add r as the new ones digit")
[b4] Then the proof, and it follows the math line by line. If n is
<bookmark mark="zero"/>zero, return the empty list. Otherwise, check that n over two
is <bookmark mark="less"/>less than n. Call the function on n over
<bookmark mark="recurse"/>two. That's the induction hypothesis. And add the remainder as
the new <bookmark mark="front"/>ones digit.

> visual: the `by simp ...` and `by omega` pieces dim, joined to "Its value is
> r + 2q = n". Then at "allowed" the `have : n / 2 < n` line glows on the right and
> "Since q < n" glows on the left, with a tag between them: "why the induction is
> allowed = why the recursion stops".
[b5] The bits after "by" are the arithmetic from the last line of the math proof. Lean
<bookmark mark="arith"/>checks those with automatic tactics. Now look at the line that
checks n over two is smaller. In the math proof, that's why the induction is
<bookmark mark="allowed"/>allowed. In the program, it's why the recursion
<bookmark mark="stops"/>stops. It's the same fact doing the same job.

> visual: the textbook proof fades. `#eval (toBinary 13).val` with output
> `[1, 0, 1, 1]`. A trace builds down the left at the bookmarks: at "six"
> "13 = 2*6 + 1", at "three" "6 = 2*3 + 0", at "one" "3 = 2*1 + 1", at "bottom"
> "1 = 2*0 + 1" then "0: done". At "off" the remainders 1, 0, 1, 1 fly into the list.
[b6] So let's run it. Thirteen is two times <bookmark mark="six"/>six, plus one. Six
is two times <bookmark mark="three"/>three, plus zero. Three is two times
<bookmark mark="one"/>one, plus one. One is two times zero, plus one, and the
recursion hits <bookmark mark="bottom"/>zero. Read the remainders
<bookmark mark="off"/>off: one, zero, one, one. The proof, run on thirteen, gives you
the digits, and they're right by construction.

> visual: panel: `theorem has_binary (n : Nat) : exists ds : List (Fin 2), value ds = n :=`
> and `  <(toBinary n).val, (toBinary n).property>`, with a tick. Under it, at "back",
> `def digits (n : Nat) : List (Fin 2) :=` / `  match has_binary n with` /
> `  | <ds, _> => ds`, and the real error in red: "recursor `Exists.casesOn` can only
> eliminate into `Prop`".
[b7] One honest detail. In Lean, you'd usually state this theorem with "there exists".
That version is true, and toBinary proves it. But try to get the digits
<bookmark mark="back"/>back out of it, and Lean says no. Lean won't let you pull data
out of a proof, so that it can throw proofs away when it compiles. So a "there exists"
proof records that the digits exist, and that's all.

> visual: toBinary's type is boxed: `{ ds : List (Fin 2) // value ds = n }`, with a
> plain reading under it: "a list ds, together with a proof that value ds = n". Then
> two lines at the bookmarks: at "are" "exists ds, value ds = n: there are digits", at
> "here" "{ ds // value ds = n }: here are the digits".
[b8] That's why toBinary's type looks a little different. It asks for a list, together
with a proof that the list has the right value. It's a "there exists" that keeps the
witness. That's the same split as before, between knowing there
<bookmark mark="are"/>are digits, and being handed <bookmark mark="here"/>them. Once
proofs are programs, you get to ask for the second kind.

## s08 The equality type
> visual: the ladder on the right, rungs one to three lit. Centre: panel
> `inductive Eq : alpha -> alpha -> Prop where` / `  | refl (a : alpha) : Eq a a`, with "a = b is
> notation for Eq a b" under it. At "one" the `refl` line glows.
[b1] Now, equality. We've been using refl to prove things are equal. Here's where it
comes from. Equality is a type with <bookmark mark="one"/>one constructor, refl. It
says that anything equals itself. That's the whole definition. There's no rule at all
for "a equals b" when a and b are different.

> visual: `example : 2 + 2 = 4 := rfl`. At "same" both sides reduce on screen, "2 + 2"
> to "4", and the equation becomes "4 = 4" with refl's tick. Then a question appears
> at "use": "how do you use a proof of a = b?"
[b2] So how does Lean prove two plus two is four? It computes both sides, gets the
<bookmark mark="same"/>same number, and then refl works. That's how you make an
equality proof. The interesting part is how you <bookmark mark="use"/>use one.

> visual: left, Nat.rec's type from s06, small, with its two case lines marked. Right,
> Eq.rec's type, simplified over three lines:
> `{motive : (b : alpha) -> a = b -> Sort u}` / `-> motive a rfl` / `-> (h : a = b) -> motive b h`.
> At "case" the middle line glows, next to Nat.rec's two case lines.
[b3] Like any inductive type, equality gets a recursor. Numbers have two constructors,
so their recursor had two cases. Equality has one constructor, so its recursor has
<bookmark mark="case"/>one case.

> visual: a fixed point a on the left, a point b on the right, and a curve h from a to
> b. At "slide" b slides back along h until it sits on a, and h shrinks to a dot
> labelled "refl". Tag at "J": "J (path induction)".
[b4] Read it as logic. You want to prove something about any b, and any proof h that
a equals b. It's enough to prove it in one case: when b is a itself, and h is refl.
That's the induction principle for equality, usually called
<bookmark mark="J"/>J. In the picture, b gets to <bookmark mark="slide"/>slide back
along h until it lands on a.

> visual: panel: `theorem my_symm {a b : alpha} (h : a = b) : b = a :=` and
> `  Eq.rec (motive := fun x _ => x = a) rfl h`. At "need" the motive at a is shown:
> "a = a", proved by rfl, with a tick.
[b5] Here it is proving symmetry. If a equals b, then b equals a. By J, we only need
the case where b is a. Then we <bookmark mark="need"/>need a equals a, which is refl.
Done.

> visual: `my_trans` and `my_congr` panels stack under `my_symm`, one body line each.
> At "substitute" a fourth: `theorem my_subst (P : alpha -> Prop) {a b : alpha} (h : a = b) :
> P a -> P b`, highlighted, with a tag: "equals can be substituted for equals".
[b6] Transitivity and congruence go the same way, one line each. So does the rule
you've used since you first <bookmark mark="substitute"/>solved an equation: if a
equals b, anything true of a is true of b. None of these are axioms. They all come
out of one constructor and its induction principle.

> visual: the table returns with a new row: "a = b" | "a type with one constructor,
> refl". At "strange" the ladder's fourth rung lights: "identity types".
[b7] So that's equality, as a type. And it leads to a <bookmark mark="strange"/>strange
question.

## s09 Are all proofs of a = b the same?
> visual: two different curves, p and q, both from a to b. At "q" a question appears:
> "p = q ?"
[b1] Proofs of a equals b are values of a type. So you can ask whether two of them are
equal. Take two proofs, p and q, that a equals b. Is p equal to
<bookmark mark="q"/>q?

> visual: try J on q: b slides back to a along q, and q shrinks to refl. p gets dragged
> along and becomes a loop from a back to a. At "loop" the question becomes "loop =
> refl ?"
[b2] Let's try J. It lets b slide back to a, and then q is refl. But p comes along for
the ride, and now it's a proof that a equals a. A <bookmark mark="loop"/>loop. So the
question becomes: is every proof that a equals a the same as refl?

> visual: the loop at a, with both of its ends pinned to a by small pins. The sliding
> animation tries to run and shakes in red at "free".
[b3] And here J gets stuck. It only works when one end of the equation is
<bookmark mark="free"/>free to move. A loop has both ends pinned at a. You'd expect
some clever trick to get around that.

> visual: tag "Hofmann and Streicher, 1994". A small picture of points with several
> different arrows between the same two points, tagged "a model where p and q differ".
[b4] There isn't one. In nineteen ninety-four, Martin Hofmann and Thomas Streicher
built a <bookmark mark="model"/>model of type theory where the answer is no: two
proofs of the same equation can be different. So J alone can't prove they're always
the same.

> visual: a ring-shaped surface. A point a on it. At "space" the label "type = space";
> at "path" a curve from a to b, labelled "proof of a = b = path". At "around" a loop
> at a goes around the hole; it tries to shrink, and snags on the hole. A small loop
> beside it that doesn't go around shrinks to a point, labelled "refl".
[b5] So what would different proofs of a equals b look like? Homotopy type theory has
an answer. Treat a type as a <bookmark mark="space"/>space, and a proof that a equals
b as a <bookmark mark="path"/>path from a to b. Refl is the path that stays put. Then
a loop that goes <bookmark mark="around"/>around a hole is a proof that a equals a, and
you can't shrink it down to refl. It's a different proof.

> visual: two paths p and q from a to b, and at "deform" a shaded sheet sweeping p
> onto q, labelled "proof of p = q". Above it, faint, a stack of further sheets and
> "...".
[b6] Then a proof that p equals q is a way to <bookmark mark="deform"/>deform one path
into the other. You can ask about proofs of that too, and so on, all the way up. And
J is exactly the rule for sliding along these paths.

> visual: the type Bool as two dots, "true" and "false". At "itself" "Bool = Bool"
> with two arrows under it: "do nothing" (true to true, false to false), and at "swaps"
> "swap" (true to false, false to true). Tag: "univalence (Voevodsky)".
[b7] It gets stranger. Vladimir Voevodsky's univalence axiom says that when two types
match up one-to-one, each way of matching them is its own proof that they're equal. Now take the type with two values, true and false.
It equals <bookmark mark="itself"/>itself in two different ways. One does nothing, and
the other <bookmark mark="swaps"/>swaps true and false. Two proofs of the same
equation, and they really are different.

> visual: panel: `example (a b : Nat) (p q : a = b) : p = q := rfl`, with a tick. Then
> at "contradiction" the Bool picture returns: "swap = do nothing" gets a red cross.
[b8] Lean takes the other road. In Lean, any two proofs of the same proposition are
<bookmark mark="equal"/>equal, by definition. It's one line. That keeps things simple,
and it fits with Lean throwing proofs away when it compiles. But it means univalence
can't be added to Lean. Swapping and doing nothing would be equal, a
<bookmark mark="contradiction"/>contradiction.

## s10 Ending
> visual: the full table, ten rows, with the ladder beside it, all five rungs lit:
> "simple types", "dependent types", "inductive types", "identity types", and at
> "shape" "paths (homotopy type theory)". The rows light up in groups as they are
> named.
[b1] So here's the whole dictionary. Every time the logic wanted to say more, the type
system had to <bookmark mark="grow"/>grow. "And" and "implies" need pairs and
functions. "For all" needs types that depend on values. Induction needs types with
their own recursors. And equality turned out to have a
<bookmark mark="shape"/>shape.

> visual: below the table, two gold-circled entries appear: "P or not P (axiom)" and
> "univalence (axiom)". At "runs" a label next to univalence: "cubical type theory
> (Cohen, Coquand, Huber, Mortberg)" (umlaut on screen). At "changes" a label next to
> P or not P: "programs that can rewind (Griffin, 1990)", with a small rewind arrow.
[b2] Two things we met along the way came in as axioms, with no program inside: P or not P,
and univalence. People found programs for both anyway. Cubical type theory is a type
theory where univalence <bookmark mark="runs"/>runs. And in a language where programs
can rewind, P or not P runs too. It answers "not P", and if a proof of P ever shows up,
it goes back and <bookmark mark="changes"/>changes its answer.

> visual: the nn_em panel from s04 returns small beside the rewind arrow. At "do" the
> table, the ladder, and the panel dim, leaving the title "Proofs are programs".
[b3] That's the double negation trick from before, running for real. So which proofs
can you run? It depends on what you let a program <bookmark mark="do"/>do.

## short1 P or not P
> visual: big centered text "P or not P", with a two-row truth table under it, ticks in
> the last column.
[b1] There's a law of logic that Lean <bookmark mark="refuse"/>refuses to run. P or
not P.

> visual: a code panel: "proof of P or Q" splits into two tagged ends: "left: a proof
> of P" and "right: a proof of Q".
[b2] In languages like Lean, a proof is a program. And a proof of "P or Q" has to say
<bookmark mark="which"/>which side is true, and prove that side.

> visual: a box with "any statement P" going in and "true" or "false" coming out.
[b3] So a proof of "P or not P", for every P, would be a program that takes any
statement and <bookmark mark="tells"/>tells you whether it's true.

> visual: P becomes "this program halts". A program icon with a step counter. At
> "turing" a red cross and the tag "the halting problem: unsolvable (Turing, 1936)".
[b4] Now let P be "this program halts". Then you'd have a program that tells you, for
any program, whether it halts. That's the halting problem, and
<bookmark mark="turing"/>Turing proved no program can solve it.

> visual: Lean code `open Classical in def decideAnything (P : Prop) : Bool := if P
> then true else false`, then the real error in red: "consider marking it as
> 'noncomputable'", with "noncomputable" underlined at "noncomputable".
[b5] So Lean doesn't get P or not P for free. It gets it from an axiom. And if you try to
compute with it, Lean asks you to mark your code
<bookmark mark="noncomputable"/>noncomputable.

> visual: "P or not P" returns, with two tags: "not false" (tick) and "can't run"
> (gold).
[b6] The law isn't false. In fact, you can prove it's not false. You just can't
<bookmark mark="run"/>run it.

## short2 Induction is recursion
> visual: a code panel with `toBinary`, and above it the line "Theorem: every natural
> number has a binary representation."
[b1] This proof is also a program, and you can <bookmark mark="run"/>run it.

> visual: the textbook proof, short form: "n = 0: empty string" / "otherwise n = 2q + r,
> r = 0 or 1" / "q < n, so q has one (induction)" / "add r as the ones digit".
[b2] The theorem says every number has a binary representation. If n is zero, use the empty string. Otherwise, write n as two q plus r,
where r is zero or one. q is <bookmark mark="smaller"/>smaller, so it has a
representation. Add r as the ones digit.

> visual: the Lean code beside it, each line joined to its sentence. At "call" the
> recursive call `toBinary (n / 2)` glows, labelled "induction hypothesis".
[b3] Here's the same proof in Lean, step for step. And the induction
hypothesis, "q has a representation", is a recursive <bookmark mark="call"/>call on n
over two.

> visual: `#eval (toBinary 13).val` and a trace: "13 = 2*6 + 1", "6 = 2*3 + 0",
> "3 = 2*1 + 1", "1 = 2*0 + 1". At "out" `[1, 0, 1, 1]` appears in gold.
[b4] So run it on thirteen. Thirteen is two times six plus one. Six is two times three
plus zero. Three is two times one plus one. One is two times zero plus one. Out
<bookmark mark="out"/>come the remainders: one, zero, one, one. Thirteen in binary.

> visual: "induction = recursion" in large text, with the base case and the recursive
> call glowing in the code.
[b5] A proof by induction is a recursive program. The base case is the base case. The
induction hypothesis is the recursive call. And when you run it, you get exactly what
the theorem <bookmark mark="promised"/>promised.

## short3 Two proofs of the same equation
> visual: "a = b" in large text, with two different curves, p and q, under it, both
> from a to b. A question: "p = q ?"
[b1] Can two proofs of the same equation be <bookmark mark="different"/>different?

> visual: code panel: `inductive Eq : alpha -> alpha -> Prop where | refl (a : alpha) : Eq a a`.
[b2] In type theory, "a equals b" is a type, and its proofs are values. Equality has
one way to build a proof: <bookmark mark="refl"/>everything equals itself. And one
rule for using one: to prove something for every b and every proof that a equals b,
check the case where b is a and the proof is refl.

> visual: tag "Hofmann and Streicher, 1994: J can't prove p = q".
[b3] You'd think that rule shows every proof that a equals a is refl. But in nineteen
ninety-four, Hofmann and Streicher showed it <bookmark mark="cant"/>can't.

> visual: a ring-shaped surface with a point a; a loop around the hole, which snags
> when it tries to shrink.
[b4] Homotopy type theory says why. Treat a type as a space, and a proof that a equals
b as a path from a to b. A loop around a <bookmark mark="hole"/>hole is a proof that a
equals a, and it can't shrink down to refl.

> visual: "Bool = Bool" with two arrows: "do nothing" and, at "swap", "swap true and
> false". Tag: "univalence".
[b5] And with univalence, the type with values true and false equals itself in two
different ways: do nothing, or <bookmark mark="swap"/>swap them.

> visual: "a = b" returns, now drawn as a surface with several paths on it.
[b6] Equality, the most basic idea in math, has a <bookmark mark="shape"/>shape.
