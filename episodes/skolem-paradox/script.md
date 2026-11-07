# Are the real numbers uncountable?

## s01 Hook
> visual: a solid real number line, labelled R. Large text above it: "uncountable".
[b1] Are the real numbers uncountable? Yes. <bookmark mark="unless"/>Unless you're
standing outside the universe.

> visual: at "unless" (end of b1) the camera starts pulling back. The line shrinks into
> one dot, labelled R, inside a large rounded region full of dots, labelled "a universe
> of sets". The R dot keeps a small "uncountable" tag. At "list" the camera pulls back
> further. Every dot in the region flies out into one long numbered row, 1, 2, 3, ...,
> with the R dot somewhere in it. Then the title card: "Skolem's paradox".
[b2] If set theory never contradicts itself, then there's a universe where every one
of its theorems is true, including the one that says the real numbers can't be listed.
But from outside, <bookmark mark="list"/>that whole universe fits on one list.

## s02 Bigger infinities
> visual: a column of slots numbered 1, 2, 3, ... down the left. Items drop into the
> slots one by one. Tag: "countable: fits on one list".
[b1] First, what uncountable means. A set is countable if you can list it. First,
second, third, and so on, with every member somewhere on the list.

> visual: a numbered list of six decimals with "..." below: 0.1415926..., 0.0500000...,
> 0.7182818..., 0.4142135..., 0.3333333..., 0.6180339...
[b2] The real numbers can't be listed. Even the ones between zero and one can't.
Here's Georg Cantor's proof. Suppose someone hands you a list of them, written as
decimals.

> visual: the diagonal digits light up gold: 1, 5, 8, 2, 3, 3. At "change" each one
> changes, and they assemble into a new number at the bottom: d = 0.545555... Small footnote: "only 4s and 5s, so d has just one decimal form".
[b3] Go down the diagonal. Take the first digit of the first number, the second digit
of the second number, and so on. <bookmark mark="change"/>Change each one. Make it a
five, or a four if it was already five.

> visual: d is compared with each row in turn. The differing digit flashes red on each
> row. At "miss" a big cross over the list: d is not on it.
[b4] The new number differs from the first number in its first digit, from the second
number in its second digit, and from every number on the list somewhere. So
<bookmark mark="miss"/>it's not on the list. Every list misses a real number.

> visual: text "uncountable = no list exists". The words "no list exists" glow.
[b5] Notice what the word means. Uncountable doesn't count anything. It says
<bookmark mark="nolist"/>no list exists. Hold on to that.

## s03 A universe of sets
> visual: icons for a number, a function graph, a line, and a triangle. Each dissolves
> into nested braces, like {{}, {{}}}.
[b1] Almost all of mathematics can be built out of sets. Numbers, functions, and the
real line are all sets, of sets, of sets.

> visual: a scroll titled "ZFC" with plain-language lines: "two sets with the same
> members are equal", "there is an infinite set", "every set has a set of all its
> subsets", "...". The list keeps scrolling to show there are infinitely many.
[b2] The standard rules for sets are called <bookmark mark="zfc"/>ZFC. There are
infinitely many rules, but each one is a single sentence, like "every set has a set of
all its subsets".

> visual: a rounded region full of dots, labelled "universe". Arrows run between some
> dots, and one arrow is labelled "is a member of". At "obeys" each line of the ZFC scroll
> gets a check mark.
[b3] A universe of sets is any collection of things, with arrows between them that we
read as "is a member of". If the collection <bookmark mark="obeys"/>obeys every rule of
ZFC, then all of set theory works inside it.

> visual: the symbols \in, =, \land, \lnot, \forall, \exists appear, each with its word
> below it. Then one statement in symbols, \exists x \forall y \lnot (y \in x), with
> "there is a set with no members" below it.
[b4] Inside a universe, you can make statements. They use "is a member of" and
"equals", plus "and", "not", "for every", and "there exists". That's all.

> visual: at "every" a spotlight sweeps over the dots inside the region and stops at its
> border. A few faint dots outside the region stay dark.
[b5] Here's the detail everything depends on. When a statement says
<bookmark mark="every"/>"for every set", it means every set in this universe. Nothing
outside is in view.

> visual: the text "the reals are uncountable" turns into "no set in this universe is a
> list of the reals".
[b6] So "the reals are uncountable" becomes a statement inside the universe. It says
<bookmark mark="nolist"/>no set in here is a list of the reals.

## s04 Shrinking the real line
> visual: the solid real line again, with "+  x  <" in the corner.
[b1] Before set theory, let's try something smaller. Take the real numbers, with
plus, times, and less than. Statements about them use those, plus the same logic words
as before.

> visual: the line goes faint. At "seed" two bright dots appear, at 0 and 1.
[b2] We'll build a countable set of reals that agrees with the whole line on every
statement. Start with two numbers, <bookmark mark="seed"/>zero and one.

> visual: a "there exists" statement appears in a box, with a slot for a number. At
> "add" a dot drops into the slot and onto the line.
[b3] Now look at every "there exists" statement that uses only the numbers we have, and
that's true in the reals. For each one, <bookmark mark="add"/>add one number that makes
it true.

> visual: three statements, one at a time, each with its dot dropping onto the line:
> \exists y\, (y + 1 = 0) gives -1 at "neg"; \exists y\, (y \cdot y = 1 + 1) gives
> sqrt(2) at "root"; \exists y\, (1 < y < 1 + 1) shows many candidates flickering, and
> one, 1.5, is kept at "pick".
[b4] There's a y with y plus one equal to zero, so add <bookmark mark="neg"/>negative
one. There's a y with y times y equal to one plus one, so add
<bookmark mark="root"/>the square root of two. There's a y between one and one plus one.
Lots of numbers work, so <bookmark mark="pick"/>pick any one.

> visual: rings of new dots, each round in a slightly different color, land on the line
> in bursts. The line gets denser each round, but stays a dust of points.
[b5] That's one round. Now we have more numbers, so there are new statements to
satisfy. <bookmark mark="rounds"/>Do another round, and another, forever. Any statement
mentions only finitely many numbers. So by some round we have them all, and the next
round answers it.

> visual: statements stream past as strings of symbols, numbered 1, 2, 3, ... At "count"
> the dots from every round merge into one numbered list. Label: "C".
[b6] Each statement is a finite string of symbols, so there are only countably many of
them, even with our numbers plugged in. Each round adds one number per statement.
Countably many rounds of countably many numbers is <bookmark mark="count"/>still
countable. Call the result C.

## s05 Why nothing changes
> visual: C as a dust on a faint real line. The statement "every positive number has a square
> root" appears, with "true in R" and "true in C" both ticked.
[b1] C is countable, but every statement that's true of the real numbers is true in C.
For example, every positive number in C has a square root in C.

> visual: the fact 1 + 1 > 1 lights up in R and in C at "simple".
[b2] Here's why. Every statement is built up from simple facts, like one plus one
is more than one. Sums and products stay in C, because "there's a y equal to a plus b"
is one of our statements. So <bookmark mark="simple"/>simple facts come out the same.

> visual: "and" and "not" join two simple facts, with both ticks unchanged. Then
> \forall rewrites as \lnot \exists \lnot.
[b3] "And" and "not" don't change anything either. And "for every" is just "not, there
exists, not".

> visual: a "there exists" statement, with the only witness outside C flashing red at
> "out". Then a witness inside C lights up gold at "inside".
[b4] That leaves "there exists". It's the only way C could disagree with the reals.
The statement could be true in the reals, while <bookmark mark="out"/>every number that
makes it true is outside C. But we ruled that out. We put a number that works
<bookmark mark="inside"/>inside C, every time. What's left after "there exists" is a
shorter statement, so the same argument covers it.

> visual: tag "Lowenheim-Skolem theorem". A big region with a small region inside it,
> with "same statements true" between them.
[b5] This is the Lowenheim-Skolem theorem. Any structure described with countably
many symbols has a countable part where <bookmark mark="same"/>exactly the same
statements are true.

> visual: zoom into C's dust, which stays thick at every zoom level because C holds
> every fraction. At "hole" one single missing point gets a ring, with a question mark
> that fades.
[b6] Most real numbers are missing from C, so C is full of holes. But C can't say
<bookmark mark="hole"/>"I have a hole". That takes a statement about a whole set of
numbers. These statements range over numbers, never over sets of numbers.

## s06 The paradox
> visual: the big region again, seen from outside, labelled "big universe". At "suppose"
> the word "suppose" gets a gold underline and moves to a corner, where it stays for the
> rest of the video.
[b1] Now do the same thing to a universe of sets. <bookmark mark="suppose"/>Suppose
there's a universe where every rule of ZFC holds. Picture it from outside, and call it
the big universe. We'll come back to that word, "suppose".

> visual: rings of witnesses grow inside the big universe. Statements drop dots: "a set
> with no members" gives an empty-set dot; "the set of natural numbers" gives N; "the set of real
> numbers" gives R. The rings settle into a small region inside it, labelled M.
[b2] This time there's only one symbol, "is a member of". The same rounds of
witnesses build a countable piece of the big universe. Call it M.

> visual: M on its own. Cantor's theorem as text, "the reals are uncountable", with "true
> in M" ticked at "cantor".
[b3] M agrees with the big universe on every statement, so every theorem of set
theory is true in M. That includes Cantor's theorem. Inside M,
<bookmark mark="cantor"/>the real numbers are uncountable.

> visual: everything in M lines up into a numbered list. Then the R dot opens. Its
> members that are in M appear as a thin dust, numbered 1, 2, 3, ...
[b4] But M is countable. It holds only countably many things in total. So M's set of
real numbers has <bookmark mark="few"/>only countably many members in M.

> visual: split screen. Left, inside M: "no list of the reals". Right, out with us: the
> numbered list of M's reals. Then the text "Thoralf Skolem, 1922".
[b5] So M believes its reals can't be listed, and we're holding a list of them. Thoralf
Skolem pointed this out in nineteen twenty-two. It's called Skolem's paradox.

## s07 The list isn't in M
> visual: M's border. Inside it, the text "no set in M is a list of M's reals".
[b1] Remember what uncountable means inside M. It means there's no set
<bookmark mark="inm"/>in M that's a list of M's reals.

> visual: our list drawn as a scroll, out with us, beyond every border. At "notin" an
> arrow tries to carry the scroll into M and bounces off.
[b2] Our list is out here with us. But <bookmark mark="notin"/>it's not in M. If it
were, M would contain a list of its own reals. Cantor's theorem is true in M, and it
says there's no such list.

> visual: two speech bubbles. Inside M: "no list exists", with a tick. Outside: "here's
> a list", with a tick. At "two" the word "uncountable" splits into two labels: "no list
> in M" and "no list at all".
[b3] So nobody is wrong. Inside M, "uncountable" means M has no list, and that's true.
From outside, we have a list, and that's true too. The same word stands for
<bookmark mark="two"/>two different things. It's a paradox only in the sense that it's
surprising.

> visual: the decimal diagonal from s02, run on a list labelled "M's reals". At "new" the
> number d appears, then lands on the full real line, outside M's dust.
[b4] Cantor's argument still works out here. Run the diagonal on our list of M's reals.
It builds <bookmark mark="new"/>a real number that isn't on the list, so that number
isn't in M.

> visual: the full real line, with M's reals as a thin dust. Zoom out until the dust is
> almost invisible.
[b5] M is missing real numbers, almost all of them. It can't notice, because the
missing ones aren't there to talk about.

> visual: M's set labelled "all subsets of N" opens to a countable handful of subsets.
> Outside it, many more subsets of N stay faint.
[b6] The same goes for subsets. M has a set it calls "all subsets of the natural
numbers". Inside M, its only members are the subsets that are in M, a countable handful.

## s08 What can't we see from inside?
> visual: a set in M with seventeen members, all ticked. At "empty" an empty set, ticked.
[b1] Some things M gets exactly right. If M says a set has
<bookmark mark="seventeen"/>exactly seventeen members, it does. If M says a set is
<bookmark mark="empty"/>empty, it is.

> visual: "exactly 17 members" (ticked) beside "uncountable", which gets a crack at
> "breaks". Then the ZFC scroll swaps for other scrolls, each with a small countable
> universe inside.
[b2] Countable versus uncountable is <bookmark mark="breaks"/>where it breaks.
Being uncountable inside M only means that M has no list. A list can still exist
outside. And it isn't a flaw in ZFC. Any rules written in this kind of language have the
same problem. If some universe obeys them, a countable universe does too.

> visual: the quote "relativity of set-theoretic notions", attributed to Skolem.
[b3] Skolem's conclusion was that <bookmark mark="relative"/>ideas like "countable" are
relative. Whether a set can be listed depends on which lists exist, and that depends on
the universe.

> visual: the natural numbers 0, 1, 2, 3, ... stretching right. Past every one of them,
> faint extra dots appear at "extra", labelled "?".
[b4] Other ideas slip too. There are universes of sets where the natural numbers
have <bookmark mark="extra"/>extra members, bigger than zero, one, two, three, and every
ordinary natural number. From inside, they look like ordinary natural numbers.

> visual: many universe regions side by side, none highlighted. At "listed" one whole
> universe gets listed, one, two, three, as seen from another universe.
[b5] Some set theorists take this all the way. Joel David Hamkins argues that there
are many universes of sets, with no single true one. Every universe, he says, is
<bookmark mark="listed"/>countable as seen from another.

> visual: our universe as a region, with a faint outline of a larger region around it,
> and an eye at the edge. At "tell" the eye fades and a question mark stays.
[b6] So here's the question. We do math inside some universe of sets. If someone
outside looked in, would our real numbers fit on a list? No statement we write from in
here could <bookmark mark="tell"/>tell us.

## s09 Ending
> visual: the "suppose" from the corner moves back to the center.
[b1] This all started with a <bookmark mark="suppose"/>"suppose". Suppose some
universe obeys the rules of ZFC. Godel's completeness theorem says that's the same as
saying the rules never lead to a contradiction.

> visual: text "second incompleteness theorem, 1931": "if ZFC never contradicts itself,
> it can't prove that". Then
> a stack of rule scrolls, each stronger one proving the one below it, with a question
> mark at the top.
[b2] Can we prove that? In nineteen thirty-one, Godel showed that if ZFC never
contradicts itself, it can't prove that it never contradicts itself. Stronger rules
could prove it. But then <bookmark mark="stack"/>you'd have to trust those rules, and
they can't prove it about themselves either.

> visual: M inside the big universe, then our universe inside a faint outline. Both borders glow, then
> fade to black.
[b3] M can't see from inside that its reals can be listed. We can't prove from inside
that our own rules are safe. In both cases, <bookmark mark="outside"/>the view from
outside is the one we never get.

## short1 Uncountable from the inside
> visual: a solid real line, labelled R, with "uncountable" above it. At "unless" the
> camera pulls back fast.
[b1] Are the real numbers uncountable? Yes. <bookmark mark="unless"/>Unless you're
standing outside the universe.

> visual: Cantor's diagonal on a short list of decimals, quickly. The new number gets a
> red cross against every row.
[b2] Uncountable means no list of them exists. Georg Cantor proved that
<bookmark mark="diag"/>every list of real numbers misses one.

> visual: a region of dots labelled M, with R inside it. At "list" every dot of M flies
> into one numbered row, R's members among them.
[b3] But if set theory never contradicts itself, logic gives us a universe of sets,
call it M, where every theorem is true, Cantor's included. And M is countable. From
outside, <bookmark mark="list"/>we can list everything in it, including its real
numbers.

> visual: our list as a scroll outside M's border. An arrow tries to carry it in and
> bounces off at "notin".
[b4] That's not a contradiction. Inside M, uncountable means there's no list in M. Our
list exists, but <bookmark mark="notin"/>it isn't in M.

> visual: the diagonal runs on our list. The new number lands on the full real line,
> outside M's thin dust.
[b5] And Cantor still wins. Run his diagonal on our list, and you get
<bookmark mark="new"/>a real number that isn't in M. M is missing almost every real
number. It can't tell, because the missing ones aren't there to talk about.

> visual: the word "uncountable" splits into "no list in M" and "no list at all".
[b6] So uncountable isn't an absolute size. It depends on
<bookmark mark="where"/>which lists exist where you stand.

## short2 A countable copy of the reals
> visual: the solid real line. Most of it dissolves to a dust at "away", and the label
> "+  x  <" stays.
[b1] You can throw <bookmark mark="away"/>almost every real number away, and no
statement about plus, times, and order will notice.

> visual: two dots, at 0 and 1. Statements appear, and each drops its dot: -1, sqrt(2).
[b2] Start with zero and one. Find every "there exists" statement that's true in the
reals and uses only numbers you have. For each one, add a number that makes it true.
<bookmark mark="drops"/>Negative one. The square root of two.

> visual: rings of new dots land in bursts. Then all the dots merge into a numbered
> list labelled C.
[b3] Repeat with the new numbers, <bookmark mark="rounds"/>forever. There are only
countably many statements, so every round adds countably many numbers. The result, call
it C, can still be listed.

> visual: a simple fact, then "and", "not", then a "there exists" with its witness
> inside C lighting up gold.
[b4] Now every statement true of the reals is true in C. Simple facts can't change.
"And" and "not" can't change them. The only risk is a "there exists" whose number is
missing, and <bookmark mark="witness"/>we added a number for every one.

> visual: C's dust, with "every positive number has a square root" and "a number between
> any two different numbers" ticked. Tag: "Lowenheim-Skolem theorem".
[b5] So C has a square root for every positive number. It's missing almost every real,
but no statement can say so. That's the <bookmark mark="ls"/>Lowenheim-Skolem theorem.