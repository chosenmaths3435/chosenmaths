# The function no for-loop can compute

## s01 Hook
> visual: a ladder of three rungs, built from the bottom. At "add" the bottom rung reads
> "3 + 4 = 1 + 1 + 1 + 1 + 3" (repeated counting). At "mult" the next rung "3 x 4 = 3 + 3 +
> 3 + 3". At "pow" the next "3^4 = 3 x 3 x 3 x 3".
[b1] <bookmark mark="add"/>Addition is repeated counting. <bookmark mark="mult"/>Multiplication
is repeated addition. <bookmark mark="pow"/>Powers are repeated multiplication.

> visual: more rungs appear above, faster and faster, with "?" on each, the ladder running
> off the top of the screen.
[b2] What happens if you <bookmark mark="keep"/>keep going?

> visual: the ladder shrinks to the side. "A(4, 2)" appears, then a counter of its digits
> running up to "19,729 digits". Then "A(4, 3)" with "more digits than atoms in the
> universe".
[b3] You get a function that climbs one rung for every step. Feed it four and two, and the
answer has <bookmark mark="digits"/>almost twenty thousand digits. Feed it four and three,
and the answer has <bookmark mark="atoms"/>more digits than there are atoms in the
universe.

> visual: a code box with a for-loop, crossed out in red. Title card: "The Ackermann
> function".
[b4] And there's something stranger. No program built from <bookmark mark="loop"/>for-loops
can compute it.

## s02 Bounded loops
> visual: a code box:
> repeat n times:
>     x = x + 1
> with "n is fixed before the loop starts" under it.
[b1] First, what kind of for-loop do I mean? One that says up front how many times it'll
run. Repeat n times, where n is fixed <bookmark mark="fixed"/>before the loop starts.

> visual: a second code box, "while x != 0: ...", labelled "not allowed".
[b2] No while-loops, no "keep going until something happens", and no function calling
itself. Just loops that know when they'll stop.

> visual: three nested code boxes. "add(a, b)": repeat b times: a = a + 1. At "mult",
> "mult(a, b)": repeat b times: add a. At "pow", "pow(a, b)": repeat b times: multiply by
> a. Each box wraps the one before.
[b3] That's still a lot. Start with adding one. A loop around that
<bookmark mark="add"/>gives you addition. A loop around addition
<bookmark mark="mult"/>gives multiplication. Another loop <bookmark mark="pow"/>gives
powers.

> visual: a box labelled "bounded loops" filling with examples: "n!", "is n prime?",
> "a < b", "the n-th prime", "gcd".
[b4] Factorials, checking for primes, comparing numbers, the n-th prime. Almost anything
you'd want to compute <bookmark mark="box"/>fits in this box.

> visual: a tick next to "every program stops". Label on the box: "primitive recursive".
[b5] And there's a nice bonus. Every loop knows how many times it'll run, so every program
in this language <bookmark mark="stops"/>stops. Functions you can build this way are called
primitive recursive.

[b6] So, is that everything? Is every function a computer can compute, and that always
gives an answer, in this box?

## s03 The Ackermann function
> visual: the three rules, one per line:
> A(0, n) = n + 1
> A(m + 1, 0) = A(m, 1)
> A(m + 1, n + 1) = A(m, A(m + 1, n))
[b1] Here's the function from the start, called the Ackermann function. It takes two
numbers, m and n, and it's defined by <bookmark mark="rules"/>three rules.

> visual: the first rule lights up.
[b2] If m is zero, <bookmark mark="r1"/>add one to n. That's just counting, the ground
the ladder stands on.

> visual: a worked computation, one line at a time, each line tagged with the rule it uses:
> A(1, 1) = A(0, A(1, 0))   (rule 3)
>         = A(0, A(0, 1))   (rule 2)
>         = A(0, 2)         (rule 1)
>         = 3               (rule 1)
[b3] Let's try one by hand. A of one and one. Rule three says it's
<bookmark mark="r3"/>A of zero, and A of one and zero. Rule two turns A of one and zero
into <bookmark mark="r2"/>A of zero and one, which is two. So we need A of zero and two,
which is <bookmark mark="three"/>three. A kid could do this. It's just slow.

> visual: a table with rows m = 0, 1, 2, 3, 4 and columns n = 0, 1, 2, 3, 4. At "row" the
> row m = 1 fills in from left to right: each entry computed by applying row 0 to the
> previous one, with arrows showing it.
[b4] Otherwise, the other two rules say this. To get row m plus one, start at one, and
apply row m over and over, n plus one times. <bookmark mark="row"/>Each row repeats the
row above it.

> visual: rows fill in: row 1 "n + 2", row 2 "2n + 3", row 3 "2^(n+3) - 3", row 4 "towers
> of 2s". Each row gets a plain label on the right: "adds", "doubles", "powers of 2",
> "towers of 2s".
[b5] So row one adds. Row two, <bookmark mark="r2"/>roughly, doubles. Row three makes
<bookmark mark="r3"/>powers of two. Row four makes <bookmark mark="r4"/>towers of twos, a
two to the two to the two, as high as you like. There's a stray three here and there, but
that's noise.

> visual: the tower for A(4, 2): 2^2^2^2^2 - 3, with its digit count 19,729. Then A(4, 3)
> as a taller tower.
[b6] Row four at two is a tower of five twos, minus three. That's the number with
<bookmark mark="twenty"/>almost twenty thousand digits. One more step along the row, and
the tower gets one taller.

> visual: row 5 appears: its first entry 65533, the rest "?". Label: "row 5: towers of
> towers".
[b7] And row five repeats row four. Good luck picturing that.

## s04 Why no loop keeps up
> visual: a loop program as nested boxes, three deep. Beside it, the table rows. At
> "climb" each nested loop is matched to a step down the table.
[b1] Why can't a loop program compute this? Think about what one loop does. It repeats
what's inside it a fixed number of times. That's about the same move that takes you
<bookmark mark="climb"/>one row down the table.

> visual: the program's growth curve and row m's curve, with the program's curve below
> forever. Label: "every loop program is beaten by some row m".
[b2] A program has a fixed number of loops, nested a fixed number deep. So it can only go a
fixed number of rows down. However clever it is, there's some row m that
<bookmark mark="beat"/>grows faster than it, for every input. I'm skipping the careful
version, but that's the idea.

> visual: the diagonal of the table highlighted: A(0, 0), A(1, 1), A(2, 2), A(3, 3), ...
> Label: "D(n) = A(n, n)".
[b3] Now walk down the table diagonally: <bookmark mark="diag"/>A of zero and zero, A of
one and one, A of two and two. Each step drops a row. Call that D of n.

> visual: a hypothetical loop program "P = D". At "m" it is beaten by row m. At "plug",
> n = m is plugged in: "D(m) < A(m, m)" and "D(m) = A(m, m)" side by side, a red cross.
[b4] Suppose some loop program computed D. It's beaten by <bookmark mark="m"/>some row,
say row m. So D of n is less than A of m and n, for every n. Now
<bookmark mark="plug"/>plug in m. D of m is A of m and m. And it's also less than A of m
and m. That's a contradiction.

[b5] So no loop program computes D. And if one computed the Ackermann function, you'd get D
for free, by feeding it n twice. So <bookmark mark="none"/>no program built from bounded
loops computes the Ackermann function. The diagonal always outruns whatever row you're
stuck in.

## s05 But it always stops
> visual: a code box with a while-loop and a stack (a list of numbers), computing A(2, 1)
> step by step: the stack grows and shrinks.
[b1] But it is computable. A program with a <bookmark mark="while"/>while-loop and a stack
of numbers runs the three rules directly. The question is whether it always stops. A
while-loop doesn't promise that.

> visual: the three rules again. Under rule 2, "(m + 1, 0) -> (m, ...)": the first number
> drops. Under rule 3, inner call "(m + 1, n + 1) -> (m + 1, n)": first stays, second
> drops; outer call "-> (m, ...)": first drops. A key: "first number drops, or first stays
> and second drops".
[b2] Look at what each rule calls. Either <bookmark mark="first"/>the first number goes
down, or the first number stays the same and <bookmark mark="second"/>the second goes
down.

> visual: two dials, like a two-digit odometer: left dial m, right dial n. The right dial
> counts down; when the left dial drops by one, the right dial jumps to a huge number and
> counts down again. The left dial reaches 0, then the right dial runs out.
[b3] That's like a countdown on two dials. The second dial counts down. Every so often,
the first dial drops by one, and the second dial can <bookmark mark="jump"/>jump up to
anything, however huge. But it's still a countdown. And the first dial can only drop so
many times.

> visual: a chain of calls, each pair smaller in this dictionary order, ending. Text: "every
> chain of calls ends".
[b4] So every chain of calls has to end. And each call splits into at most two more, so the
whole tree of calls is finite. The Ackermann function <bookmark mark="halts"/>always stops. It's
just that no bounded loop can tell you in advance how long it'll take.

## s06 Ending
> visual: a note card, handwritten style: "Does this mean the Ackermann function can't be
> defined with only these loops?"
[b1] When I first learned this, I wrote a question in my notes: so is the Ackermann
function impossible in any language where every loop is bounded?

> visual: a code box where the loop builds a function:
> f = add_one
> repeat m times:
>     f = repeat_it(f)
> return f(n)
> with a note: "repeat_it(g) = the function that starts at 1 and applies g, n + 1 times".
> At "functions" the line "f = repeat_it(f)" lights up. Small credit: "Godel's System T".
[b2] It turns out it isn't. Suppose a loop can build <bookmark mark="functions"/>functions,
not just numbers. Then "each row repeats the row above it" is one more loop. Start with
add one, and m times, replace the function with "repeat it". Every loop is still bounded,
and Ackermann fits.

> visual: a bigger box around "loops over functions", with a new arrow escaping it,
> labelled "?".
[b3] But then something bigger escapes. In fact, <bookmark mark="every"/>every real
language where every program stops is missing something. By real, I mean a computer can
list its programs and run them.

> visual: a list of programs P1, P2, P3, ... in a column, and a table of their outputs on
> inputs 1, 2, 3, .... The diagonal entries light up, and a new row "D" appears, each entry
> the diagonal entry plus one.
[b4] Here's why. List all its programs. <bookmark mark="list"/>Program one, program two,
and so on. Now make a new function: on input n, run program n on n, and add one. Every
program stops, so this stops too. An ordinary computer can run it. But it
<bookmark mark="differs"/>differs
from program n at input n, for every n. So it's not on the list.

> visual: text "to compute everything computable, some programs must be allowed to run
> forever". A small inset of the halting problem from the earlier episode.
[b5] So if you want to compute everything that can be computed, you have to allow programs
that might never stop. And once you do, you get the halting problem: no way to tell, in
general, which ones will.

## short1 Too big for any for-loop
> visual: the ladder: "3 + 4", "3 x 4", "3^4", then rungs running off the top.
[b1] Addition is repeated counting. Multiplication is repeated addition. Powers are
repeated multiplication. Keep going, and you get the <bookmark mark="ack"/>Ackermann
function.

> visual: the table, rows labelled "adds", "doubles", "powers of 2", "towers of 2s".
[b2] Its rows climb the ladder. Row one adds. Row two doubles. Row three makes powers of
two. Row four makes <bookmark mark="towers"/>towers of twos. A of four and three has more
digits than there are atoms in the universe.

> visual: a for-loop code box with "repeat n times", then nested boxes matched to rows.
[b3] And no program built from for-loops, loops that fix their count before they start, can
compute it. Each loop repeats what's inside it, which is worth about
<bookmark mark="row"/>one row.
A program has a fixed number of loops, so it's stuck below some row m.

> visual: the diagonal A(0, 0), A(1, 1), A(2, 2), ... lit up. Then "D(m) < A(m, m)" and
> "D(m) = A(m, m)" with a red cross.
[b4] But walk the table diagonally, one row down each step. If a loop program computed the
diagonal, it'd be beaten by some row m. Plug in m, and the diagonal at m is
<bookmark mark="less"/>less than itself.

> visual: the table with the diagonal running off the bottom. Text: "computable, always
> stops, no for-loop".
[b5] So here's a function that always stops, that a computer can compute, and that no
for-loop program ever will.

## short2 Why the Ackermann function always stops
> visual: the three rules.
[b1] This function, the Ackermann function, calls itself on bigger and bigger numbers. Its
answers get so big that A of four and three has more digits than atoms in the universe. So
does it <bookmark mark="stop"/>always stop?

> visual: under the rules, the moves: "first drops" and "first stays, second drops".
[b2] Look at what each rule calls. Either the first number <bookmark mark="first"/>goes
down, or the first stays the same and the second goes down.

> visual: two dials. The right one counts down; when the left one drops, the right jumps
> to a huge number and counts down again.
[b3] That's a countdown on two dials. The second dial ticks down. Every so often, the
first dial drops by one, and the second dial can <bookmark mark="jump"/>jump up to anything,
however huge.

> visual: the left dial at 0, the right dial running out. Text: "every chain of calls
> ends".
[b4] But a huge countdown still ends. And the first dial can only drop so many times. So
every chain of calls <bookmark mark="ends"/>ends, and the function always stops.

> visual: a for-loop crossed out next to the dials.
[b5] What you can't do is know in advance how long it'll take. And that's a hint at why
for-loops, which fix their count before starting, can't keep up with it.

## short3 Every safe language is missing something
> visual: a box labelled "a language where every program stops".
[b1] Take any programming language where every program is guaranteed to stop, and a
computer can list the programs and run them. It's <bookmark mark="miss"/>missing
something. Here's why.

> visual: a column of programs P1, P2, P3, ... and a table of their outputs on inputs 1,
> 2, 3, ....
[b2] List all its programs: <bookmark mark="list"/>program one, program two, and so on.
Make a table of what each one outputs on each input.

> visual: the diagonal entries light up; a new row D appears below, each entry the
> diagonal entry plus one.
[b3] Now make a new function. On input n, run program n on n, and
<bookmark mark="plus"/>add one. Every program stops, so this always stops too. An ordinary
computer can run it.

> visual: D compared with each row; at each diagonal position a red "!=".
[b4] But it differs from program one at input one, from program two at input two, from
<bookmark mark="every"/>every program somewhere. So it's not in the language.

> visual: text "to compute everything computable, programs must be allowed to run
> forever".
[b5] So to compute everything that can be computed, you have to allow programs that might
<bookmark mark="forever"/>never stop. And then you can't always tell which ones will.
