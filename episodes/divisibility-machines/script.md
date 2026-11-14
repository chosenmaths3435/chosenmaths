# A divisibility test for any number

## s01 Hook
> visual: three lines appear one at a time, left aligned: "3: add the digits", "5: look at
> the last digit", "7: ?".
[b1] To check whether a number is divisible by three, you add up its digits. For five, you
look at the last digit. But what about <bookmark mark="seven"/>seven?

> visual: the lines clear. The 7-state machine appears: seven dots labelled 0 to 6 on a
> circle, every arrow drawn faint. The number 1729 sits above it. At "feed" the digits light
> up one at a time; for each, the arrow taken lights up and a glow moves along it to the next
> dot (0 -> 1 -> 3 -> 4 -> 0). The final dot 0 pulses.
[b2] Here's a divisibility test for any number. This one is for seven. Let's
<bookmark mark="feed"/>feed it one thousand seven hundred twenty-nine, one digit at a time.
It lands on zero, so seven divides it.

> visual: title card "A divisibility test for any number".
[b3] By the end, you'll be able to build one of these for any number you like, and you'll
see what this kind of machine can't do.

## s02 The machine for 3
> visual: three dots labelled 0, 1, 2 at the corners of a triangle. Arrows appear around the
> triangle in one direction (0 -> 1 -> 2 -> 0) labelled "1, 4, 7", then arrows the other
> way (0 -> 2 -> 1 -> 0) labelled "2, 5, 8", then a self-loop on every dot labelled
> "0, 3, 6, 9". A small arrow from nowhere points into dot 0, marked "start".
[b1] Let's start with three. Here's the whole test, drawn as a diagram: three dots,
labelled zero, one and two, with arrows between them. From any dot, the digits
<bookmark mark="one"/>one, four and seven take you one step around. Two, five and eight
<bookmark mark="two"/>take you two steps. And zero, three, six and nine
<bookmark mark="loop"/>leave you where you are.

> visual: the number 4812 above the diagram. Digit by digit, the digit lights up, the arrow
> taken lights up, and the glow moves: 0 -> 1 (4), 1 -> 0 (8), 0 -> 1 (1), 1 -> 0 (2).
[b2] To use it, start at zero and read the number from left to right. For each digit,
follow the arrow with that label. Take four thousand eight hundred twelve. Four takes us
<bookmark mark="d1"/>to one. Eight takes us <bookmark mark="d2"/>to zero. One,
<bookmark mark="d3"/>to one. And two, <bookmark mark="d4"/>back to zero.

> visual: dot 0 pulses. Text under the diagram: "4812 = 3 x 1604".
[b3] The dot you end on is the remainder when you divide by three. We ended at zero, so
three divides four thousand eight hundred twelve.

> visual: the diagram shrinks to the left. On the right a column builds, one row per digit
> read: "4 -> remainder 1", "48 -> remainder 0", "481 -> remainder 1", "4812 -> remainder 0",
> each row in the color of the dot it matches.
[b4] Why does this work? Each dot stands for a remainder. After reading some of the digits,
you're sitting on the remainder of the number you've read so far. Four leaves
<bookmark mark="r1"/>one. Forty-eight leaves <bookmark mark="r2"/>zero. Four hundred
eighty-one leaves <bookmark mark="r3"/>one.

> visual: the column clears. "x" then "x d" (the digits of x followed by a digit d), then
> "10x + d". At "nine" the line "10x = 9x + x" appears, with "9x" underlined and labelled
> "multiple of 3". Then "r --d--> remainder of r + d".
[b5] Reading one more digit d turns a number x into <bookmark mark="tenx"/>ten x plus d.
And ten x is <bookmark mark="nine"/>nine x plus x, where nine x is a multiple of three. So
ten x leaves the same remainder as x, and the new remainder is
<bookmark mark="plus"/>just the old one plus the digit. That's exactly what the arrows do.

> visual: the diagram slides back to the center, and the words "digit sum" appear under it.
[b6] So walking this diagram is adding up the digits, keeping only the remainder. It's the
digit-sum rule, with the reason it works built in.

## s03 Any number
> visual: the 3-dot diagram fades. A row of dots appears labelled 0, 1, 2, ..., n-1. One
> arrow from dot "r" to dot "(10r + d) mod n", labelled "d". The rule is written below:
> "r --d--> remainder of 10r + d".
[b1] Nothing here was special about three. For any number n, draw n dots, one for each
remainder, from zero up to n minus one. The arrow for digit d goes from r to
<bookmark mark="rule"/>the remainder of ten r plus d. The same reason works: reading a
digit turns x into ten x plus d, and the remainder of that depends only on the remainder of
x. So the dots keep track of the remainder.

> visual: five dots 0 to 4 on a circle, with the rule "r --d--> remainder of 10r + d" still
> below. At "drops" the "10r" in the rule crosses out.
> Then arrows labelled "3, 8" from every one of the five dots converge on dot 3, drawn
> together. Then the arrows labelled "0, 5" from every dot converge on dot 0.
[b2] Try five. Ten r is always a multiple of five, so it <bookmark mark="drops"/>drops
out. The arrow for d goes to the remainder of d, no matter where it starts. Every
<bookmark mark="three"/>three and every eight lands on three. Every
<bookmark mark="zero"/>zero and every five lands on zero.

> visual: "last digit 0 or 5" appears next to dot 0.
[b3] So this machine forgets everything except the last digit. You end on zero exactly
when the last digit is zero or five. That's the rule from school, and the machine found it
on its own.

> visual: the full 7-state machine: seven dots on a circle with every arrow drawn, a dense
> tangle (digits with the same arrow share it, like "0, 7"). Below it, "10 -> remainder 3",
> then the rule "r --d--> remainder of 3r + d".
[b4] Now seven. Ten leaves remainder three, so the rule becomes: triple where you are, add
the digit, and keep the remainder. Here's the <bookmark mark="whole"/>whole machine: seven
dots, with ten digits leaving each one.

> visual: the tangle dims to faint. 1729 reruns: each step lights one arrow and shows the
> arithmetic beside it: "3 x 0 + 1 = 1", "3 x 1 + 7 = 10 -> 3", "3 x 3 + 2 = 11 -> 4",
> "3 x 4 + 9 = 21 -> 0".
[b5] There's no simple pattern in these arrows, and you don't need to memorize them. You
just follow them. One thousand seven hundred twenty-nine: one <bookmark mark="d1"/>takes
us to one. Then three plus seven <bookmark mark="d2"/>is ten, which leaves three. Nine
plus two <bookmark mark="d3"/>is eleven, which leaves four. And twelve plus nine
<bookmark mark="d4"/>is twenty-one, which leaves zero.

> visual: eleven dots on a circle, arrows faint. The rule "10 -> -1" then
> "r --d--> remainder of d - r". The number 1331 runs: 0 -> 1 -> 2 -> 1 -> 0. Under it, one
> line per step, the newest digit always with a plus sign: "1", "3 - 1 = 2",
> "3 - 3 + 1 = 1", "1 - 3 + 3 - 1 = 0".
[b6] One more. For eleven, ten leaves remainder ten, which is the same as
<bookmark mark="minus"/>minus one. So the rule is: flip the sign of where you are, add the digit,
and keep the remainder. Run it on <bookmark mark="run"/>thirteen thirty-one, and the signs alternate:
one minus three plus three minus one. That's the old test for eleven, where you add and
subtract the digits in turn.

## s04 Finite state machines
> visual: the 7-state machine returns, clean. Labels point at its parts as they're named:
> "states" (the dots), "input" (the digits 1729 in a row), "transitions" (one arrow),
> "accept" (dot 0, now drawn with a double circle).
[b1] Every diagram so far is a finite state machine. It has a fixed set of
<bookmark mark="states"/>states, the dots. It reads its <bookmark mark="input"/>input one
symbol at a time, and each symbol moves it <bookmark mark="arrow"/>along an arrow. When the
input runs out, the state it's in decides the answer: <bookmark mark="accept"/>yes or no.

> visual: a very long number scrolls through above the machine, digits streaming in from
> the right, while a glow hops between dots. A counter reads "digits read: 1,000,000".
[b2] Notice what the machine doesn't do. It never stores the number. Feed it a number with
a million digits, and at every moment, all it remembers is one of seven dots.

> visual: the 7-state machine shrinks into a corner. A 4-state machine in a row: "start",
> "c", "ca", "cat" (double circle). Arrows labelled "c", "a", "t" go along the row, a
> self-loop on "cat" labelled "anything", and faint arrows back to "start" labelled
> "anything else" (a self-loop on "start"; the "c" arrows back to the "c" state shown faint
> too). Then a separate 2-state machine "even" (start, double circle) and "odd", with arrows
> labelled "1" between them and self-loops labelled "0".
[b3] These machines show up everywhere. Searching a text for the word
<bookmark mark="cat"/>"cat" takes four states: nothing yet, seen a c, seen c a, and found
it. Checking whether a string of bits has an <bookmark mark="even"/>even number of ones
takes two.

> visual: the word "language" appears with three examples under it, each with its machine as
> a small icon: "{0, 7, 14, 21, ...}" (in base 10), "strings containing cat", "bit strings
> with an even number of 1s". At "regular" a bracket groups them under "regular languages".
[b4] The set of inputs a machine says yes to is called its language. The multiples of
seven are one. Strings that contain "cat" are another. Any language that some finite state
machine can recognize is called <bookmark mark="regular"/>regular.

## s05 What they can't do
> visual: three small machines from earlier (mod 7, "cat", even ones), each with a caption of
> what it remembers: "the remainder", "the last few letters", "even or odd so far".
[b1] So which languages are regular? The machine's only memory is the state it's in, and
there are finitely many states. So it can handle anything where you only need to remember
a bounded amount: a remainder, the last few letters, whether you've seen an even or odd
number of ones.

> visual: the three machines clear. Two strings: "(()())" with a green check, "(()" with a red
> cross.
[b2] Here's something it can't do: check that parentheses are balanced, so that every open
parenthesis gets closed.

> visual: a machine drawn as a box with k dots inside, labelled "k states". Strings stack up
> on the left: "(", "((", "(((", ..., "(" repeated k+1 times. Each sends a glow into the box
> and lands on a dot. At "same" two of them land on the same dot, which turns yellow, and
> their strings are labelled "i" and "j".
[b3] Suppose some machine did it, with k states. Feed it one open parenthesis, then two,
then three, all the way up to k plus one. That's more inputs than there are states, so
<bookmark mark="same"/>two of them must land on the same state. Say one has i open
parentheses and the other has j, with i less than j.

> visual: both strings get i closing parentheses appended. From the shared yellow dot, both
> glows follow the same arrows to the same final dot. Then labels: "i open, i closed:
> balanced" with a check, and "j open, i closed: not balanced" with a cross. The final dot
> flashes red.
[b4] Now add i close parentheses to both. From the same state, the same symbols follow the
same arrows, so both end up in the same place and get the same answer. But one is
<bookmark mark="bal"/>balanced, and the other still has <bookmark mark="open"/>j minus i
parentheses left open. The machine is wrong about one of them.

> visual: "no finite state machine checks balanced parentheses" in a box. Then the 7-state
> machine fades in beside it with the caption "7 is fixed in advance".
[b5] So no finite state machine checks parentheses. It can count up to any fixed number,
but never without limit. That's also why the divisibility machines work: the seven is
<bookmark mark="fixed"/>fixed before you build the machine, so seven dots are always enough.

## s06 Ending
> visual: the 3-dot machine with one glowing path. Then a new small diagram where one dot
> has two arrows with the same label "a" leaving it. At "many" the glow reaches that dot and
> splits into two glows, one along each arrow.
[b1] Every machine here follows exactly one path through its diagram. What if it could
follow <bookmark mark="many"/>many paths at once, and say yes if any of them does?
Surprisingly, that doesn't let it recognize anything new. But it can make the machine
exponentially smaller.

## short1 A divisibility test for 7
> visual: portrait. The 7-state machine, every arrow faint, with "divisible by 7?" above it.
[b1] Here's a divisibility test for seven. Seven dots, one for each remainder, and an arrow
for each of the ten digits leaving every dot.

> visual: 1729 above the machine. Each digit lights up, its arrow lights up, and the glow
> moves: 0 -> 1 -> 3 -> 4 -> 0, the step's arithmetic beside it ("3 x 1 + 7 = 10 -> 3").
> Dot 0 pulses, then "1729 = 7 x 247".
[b2] Start at zero and read the number left to right, following the arrow for each digit.
Let's try one thousand seven hundred twenty-nine. One takes us <bookmark mark="d1"/>to one.
Seven, <bookmark mark="d2"/>to three. Two, <bookmark mark="d3"/>to four. And nine,
<bookmark mark="d4"/>to zero. We ended at zero, so seven divides it.

> visual: "x  ->  10x + d" then "10 -> remainder 3" then "r --d--> remainder of 3r + d".
[b3] So where do the arrows go? Each dot is the remainder of the number read so far. Call
that number x. Reading a digit turns x into ten x plus the digit, and ten leaves remainder
three. So the rule is: triple where you are, add the digit, and keep the remainder.

> visual: the machine stays, and "any n: r --d--> remainder of 10r + d" appears under it.
[b4] For any other number, send digit d from r to the remainder of ten r plus d, and the
same recipe builds a test. It never has to remember the number, only which dot it's on.

## short2 Why adding the digits works
> visual: portrait. "3 | 4812 ?" at the top. The 3-dot triangle with its arrows labelled
> "1, 4, 7", "2, 5, 8", and self-loops "0, 3, 6, 9".
[b1] Why does adding up the digits tell you whether a number is divisible by three? Here's a
machine that checks it. Three dots, for the remainders zero, one and two. From any dot,
one, four and seven move you <bookmark mark="one"/>one step. Two, five and eight move you
<bookmark mark="two"/>two. And zero, three, six and nine <bookmark mark="loop"/>stay put.

> visual: 4812 runs, each digit lighting up as its arrow lights: 0 -> 1 -> 0 -> 1 -> 0.
> Dot 0 pulses.
[b2] Start at zero and follow the digits of four thousand eight hundred twelve. Four takes
you <bookmark mark="d1"/>to one, eight <bookmark mark="d2"/>to zero, one
<bookmark mark="d3"/>to one, and two <bookmark mark="d4"/>to zero. You end at zero, so
three divides it.

> visual: "x  ->  10x + d", then "10x = 9x + x" with "9x" labelled "multiple of 3", then
> "r --d--> remainder of r + d".
[b3] The dot you're on is always the remainder of the number read so far. Call that number
x. Reading a digit turns x into ten x plus the digit. And ten x is nine x plus x, so it leaves the same
remainder as x. The remainder just goes up by the digit.

> visual: "digit sum" under the machine.
[b4] So walking this diagram is adding up the digits, keeping only the remainder. That's
the rule, and that's why it works.

## short3 No finite machine can check parentheses
> visual: portrait. "(()())" with a check and "(()" with a cross.
[b1] Here's something no finite state machine can do: check that parentheses are balanced.

> visual: a box with k dots, labelled "k states". The strings "(", "((", ..., up to k+1
> open parentheses, each sending a glow to a dot. Two land on the same dot, which turns
> yellow, labelled "i" and "j".
[b2] A finite state machine reads one symbol at a time, only remembers which state it's
in, and answers based on the state it ends in. Suppose one did this, with k states. Feed it
one open parenthesis, then two, then three, up to k plus one. That's more inputs than
states, so <bookmark mark="same"/>two of them land on the same state. Say i open
parentheses and j, with i less than j.

> visual: i close parentheses appended to both. Both glows follow the same arrows to the
> same dot. Labels "balanced" (check) and "not balanced" (cross). The dot flashes red.
[b3] Now add i close parentheses to both. From the same state, the same symbols lead to
the same place, so the machine gives both the same answer. But one is balanced, and the
other isn't. So the machine is wrong about one of them.

> visual: "count to any fixed number, never without limit".
[b4] However many states you give it, a finite machine can count up to a fixed number, but
never without limit.
