# Most strings can't be compressed

## s01 Hook
> visual: a box labelled "compressor". A text file goes in and comes out smaller. At
> "bigger" a file of random noise goes in and comes out slightly bigger, with "+1 byte" in
> red.
[b1] Every compression program like zip makes <bookmark mark="bigger"/>some files
bigger.

> visual: the box fades. Text: "not a bug".
[b2] It's not a bug. There just aren't enough short files to go around.

> visual: two strings of 100 bits, one above the other: "0101...01" and a messy string. At
> "equal" each gets the label "chance 1/2^100".
[b3] Look at these two strings of a hundred bits. Flip a coin a hundred times, and you're
<bookmark mark="equal"/>exactly as likely to get one as the other. But only one of them
looks random.

> visual: at "short" the first string collapses into the phrase "01, fifty times". The
> second string stays as it is, with a "?" next to it. Title card: "Kolmogorov
> complexity".
[b4] The first has a short description: <bookmark mark="short"/>zero one, fifty times. The
second, as far as we can tell, has no description much shorter than itself. That's going
to be what random means.

## s02 Descriptions
> visual: a code box: print("01" * 50). An arrow to its output, the 100-bit string. A label
> under the code box: "length in bits".
[b1] Let's make "description" precise. A description of a string is a program that prints
it. Pick a programming language, and write its programs in bits, zeros and ones. A
program's length is how many bits it takes.

> visual: "K(x) = length of the shortest program that prints x".
[b2] The Kolmogorov complexity of a string, <bookmark mark="K"/>K of x, is the length of
the shortest program that prints x.

> visual: K("0101...01") = small. Then "first million digits of pi" with a short program
> beside it, and K = small.
[b3] For the zero-one string, that's tiny. For the first million digits of pi,
<bookmark mark="pi"/>it's tiny too. A short program computes them.

> visual: a code box: print("1101000111..."), the messy string pasted in. Below:
> "K(x) <= length of x + c".
[b4] And every string has at least one description: <bookmark mark="print"/>print, then
the string itself. So K of x is never more than the length of x, plus a little.

> visual: a box "language A" and a box "language B", with "translator" arrows both ways
> between them. Label: "K changes by at most a fixed amount".
[b5] What about the choice of language? Switch to any other general-purpose language, and K
changes by at most a fixed amount: the size of a translator between the two. So we won't
worry about it.

> visual: "compressible: K(x) < length of x".
[b6] We'll call a string compressible if <bookmark mark="comp"/>K of x is less than its
length. Some program, shorter than the string, prints it.

## s03 Counting
> visual: right column: the eight strings of length 3. At "eight" they light up.
[b1] So how many strings are compressible? Let's count. Take strings of length three.
There are <bookmark mark="eight"/>eight of them.

> visual: left column: the empty string, 0, 1, 00, 01, 10, 11. At "seven" they light up.
> Arrows run from each to a different string on the right; one string on the right is
> left with no arrow and gets highlighted.
[b2] Now the programs shorter than three bits: one of length zero, two of length one, and
four of length two. That's <bookmark mark="seven"/>seven. Even if every one of them prints
a different string, they cover seven of the eight. One string is left over.

> visual: the general count: "2^n strings of length n", "2^n - 1 shorter programs".
[b3] The same thing happens at every length. There are two to the n strings of length n,
and only two to the n, minus one, shorter programs. So at every length,
<bookmark mark="left"/>at least one string can't be compressed at all.

> visual: a bar for all strings of length n, with a thin sliver marked "shortened by 10
> bits: fewer than 1 in 500". The rest of the bar is labelled "random".
[b4] And it gets more extreme. To shorten a string by ten bits, you need a program at least
ten bits shorter. There are enough of those for <bookmark mark="frac"/>fewer than one
string in five hundred. So almost every string has no program much shorter than itself.
Almost every string is random.

> visual: files of every length from 0 to 3 bits in columns by length, each with an arrow
> to its own output. At "shortest" one 3-bit file shrinks to a 2-bit output. The 2-bit
> file that had that output is bumped, and at "grow" it moves to a longer output, glowing
> red.
[b5] The same counting works for any compressor like zip. It has to be reversible, so
<bookmark mark="zip"/>different files need different outputs. Say it shrinks some file.
Take <bookmark mark="shortest"/>the shortest file it shrinks. If none of the files shorter
than that one grow, then between them they fill up every shorter output, and there's no
room left. So <bookmark mark="grow"/>some file has to grow.

## s04 Where compressible strings come from
> visual: palindromes of length 8 in a list: 00000000, 00011000, 00100100, ... with a
> mirror line through the middle of each.
[b1] So which strings are compressible? The ones that follow a rule, where the rule picks
out only a few strings. Take <bookmark mark="pal"/>palindromes, strings that read the same
backwards.

> visual: a big block "2^100 strings of length 100" with a tiny block inside it,
> "2^50 palindromes".
[b2] Of the two to the hundred strings of length one hundred, only
<bookmark mark="few"/>two to the fifty are palindromes. That's a tiny fraction.

> visual: the palindromes in a numbered list. One far down is circled, labelled
> "#713,402,288,515,107". A code box: "print palindrome #713,402,288,515,107 of length 100",
> with the number highlighted as "at most 50 bits".
[b3] So list them in order. To describe a palindrome, just give its position:
<bookmark mark="index"/>palindrome number such-and-such of length one hundred. There are
two to the fifty of them, so the position always fits in fifty bits. The program is the
rule, the length, and that number.

> visual: a general set of strings, drawn as a thin band inside all strings, with the
> label "at most 2^(n/2) strings of each length n". At "half" one long string from the band
> shrinks to about half its width.
[b4] For palindromes, that's no surprise. You could just give the first half. But the
trick works for any rule a computer can check. If the rule picks out at most two to the n
over two strings of each length n, then <bookmark mark="half"/>every long string that
follows it can be described in about half its length.

> visual: the compressor box with a text file shrinking, then noise growing.
[b5] Real compressors win the same way. They bet that your file is one of the few that
follow a pattern, like English text. <bookmark mark="noise"/>Hand them noise, and the bet
loses.

## s05 Why not just search?
> visual: a string x at the top. Below, a list of programs, shortest first, each one run
> in turn: some print a wrong string (cross), some spin forever (a spinner icon). The list
> ends at print("x").
[b1] So can a computer find K of x? Here's the obvious plan. <bookmark mark="try"/>Run
every program, shortest first, and stop at the first one that prints x. One of them does,
since "print x" is on the list.

> visual: the spinner on one program keeps going while a clock ticks: 1 hour, 1 day, 1
> year. Two speech bubbles: "about to print x?" and "runs forever?".
[b2] The problem is that some of those programs <bookmark mark="loop"/>never stop. If a
program has been running for a year, maybe it's about to print x, or maybe it'll run
forever. You can't tell.

> visual: a box labelled "halts?". At "box" it is plugged into the search, and the
> spinners are skipped; the search finishes.
[b3] That's the halting problem: no program can decide whether another program stops. With
<bookmark mark="box"/>a box that answered halting questions, this plan would work. Skip the
programs that never stop, and run the rest.

[b4] So the halting problem is the only thing in the way. But there's a cleaner reason
that no program computes K, and it starts with an old paradox.

## s06 The Berry paradox
> visual: the phrase "the smallest number that cannot be described in under sixty letters"
> on screen.
[b1] Think about the smallest number that cannot be described in under sixty letters. There
are only finitely many phrases that short, so most numbers can't be described that way,
and one of them is the smallest.

> visual: at "count" a letter counter runs along the phrase and stops at 57.
[b2] But I just described it, and <bookmark mark="count"/>that phrase has fewer than sixty
letters.

[b3] In English, that's a paradox, because "described" is fuzzy. With programs, nothing is
fuzzy, and the paradox becomes a proof.

> visual: a code box:
> for x in all strings, shortest first:
>     if K(x) > L: print(x); stop
> At "first" the "if K(x) > L" line lights up.
[b4] Suppose some program could compute K. Then write this one: go through strings in
order, and <bookmark mark="first"/>print the first one whose K is bigger than some number
L. Almost every string has K bigger than L, so this stops.

> visual: the code box splits into two parts, "fixed part" around the loop and the code
> for K, and "L" around the number. At "L" the number shows its binary length, "about
> log2 L bits".
[b5] How long is this program? There's a fixed part, the loop and the code for K. And
there's <bookmark mark="L"/>L itself. Written in binary, L takes about log L bits, the
number of binary digits it has.

> visual: L = 1,000,000,000 with "30 bits" under it. A bar for the program's length (fixed
> part + 30) next to a much longer bar for L.
[b6] Make L a billion. Writing it down takes about thirty bits. The fixed part doesn't
change, so once L is big enough, <bookmark mark="short"/>the whole program is shorter than
L.

> visual: the program prints a string. The string's label reads "K > L", and the program's
> label reads "length < L". A red cross between them.
[b7] But it prints a string whose shortest program is longer than L. And
<bookmark mark="contra"/>this program, shorter than L, just printed it. That's a
contradiction. So no program computes K.

## s07 You can't prove it either
> visual: a string of a million coin flips scrolling by, labelled "almost surely random".
> A question: "can we prove it?"
[b1] Fine, you can't compute it. But maybe you can prove it, one string at a time? Take a
million coin flips. The string you get is almost certainly random. Can we prove that it
is, using the usual axioms of math?

> visual: the code box changes: "for each proof, in order: if it proves K(x) > L for some
> x: print(x); stop". A box labelled "axioms + proof checker" replaces the code for K.
[b2] Run the same trick. This time the program searches through
<bookmark mark="proofs"/>every proof, in order, from some fixed list of axioms. It stops
at the first proof that says some string has K bigger than L, and prints that string.

> visual: the length split again: "axioms + checker" (fixed) plus "about log2 L bits".
[b3] Same count. This program is a fixed size, your axioms and your proof checker, plus
about log L bits. So for big L, it's shorter than L. And it prints a string that was
proven to need more than L.

> visual: red cross, then the search running forever with no proof found. Text: "no proof
> of K(x) > L, for any x".
[b4] That's a contradiction again, as long as your axioms only prove true things. So the
search never finds a proof. <bookmark mark="never"/>No specific string can be proven to
have K bigger than L.

> visual: "Gregory Chaitin, 1970s". A number line of complexity with a mark at L, "about
> the size of your axioms"; past it, a crowd of strings all labelled "true, no proof".
[b5] This is Gregory Chaitin's theorem, from the nineteen seventies. Pick your axioms,
and there's a number L, about the size of the axioms plus the proof checker, past which
they can't prove a single string is random. Even though all but finitely many strings have
K bigger than L.

> visual: a bar "usual axioms of math + checker" far shorter than a bar "1,000,000 bits".
[b6] The usual axioms of math fit in <bookmark mark="fit"/>far fewer than a million bits.
So for our million coin flips, the answer is no. It's almost surely random, and no proof
will ever say so.

> visual: a small inset of "true but unprovable" from the incompleteness episode, beside
> "this string is random".
[b7] It's a cousin of Godel's incompleteness theorem, which we got from the halting
problem in an earlier video. Here are infinitely many true statements, each one saying
<bookmark mark="random"/>this string is random, and none of them has a proof.

## s08 Ending
> visual: a wall of bit strings, almost all of them glowing faintly as random. A magnifying
> glass passes over them, and every one it stops on gets a "?".
[b1] So almost every string is random. Flip a coin enough times, and you'll almost surely
get a random one. But <bookmark mark="name"/>name a long one and prove it's random, and you
can't.

> visual: the wall fades out.
[b2] Randomness is everywhere, and you can never pin it down.

## short1 Why no compressor shrinks everything
> visual: the compressor box: a text file shrinks, then a noise file comes out bigger, "+1
> byte" in red.
[b1] Every compression program like zip makes some files bigger. It's not a bug. There
just aren't enough short files to go around.

> visual: the eight strings of length 3 on the right; the seven shorter strings on the left
> (empty, 0, 1, 00, 01, 10, 11).
[b2] Count them. There are <bookmark mark="eight"/>eight files of three bits. Shorter
ones? One empty file, two of length one, four of length two. <bookmark mark="seven"/>Seven.

> visual: files of lengths 0 to 3 in columns, each with an arrow to its own output. One
> 3-bit file shrinks to a 2-bit output; the 2-bit file that had it is bumped to a longer
> output, glowing red.
[b3] A compressor has to be reversible, so different files need different outputs. Seven
short outputs can't hold all eight files. And the short files need those outputs too. Take
the shortest file it shrinks. If no shorter file grows, they've already filled every
shorter output, so <bookmark mark="pushed"/>some file gets pushed longer.

> visual: a bar of all files of a given length with a thin sliver "shortened by 10 bits:
> fewer than 1 in 500".
[b4] It's worse than that. To save ten bits, a file needs an output ten bits shorter, and
there are only enough of those for <bookmark mark="frac"/>fewer than one file in five
hundred.

> visual: the compressor box: a text file and a spreadsheet shrink; a file of coin flips
> comes out slightly bigger.
[b5] So a compressor only shrinks the rare files with patterns, like text or repeats. Feed
it <bookmark mark="coin"/>a file of coin flips, and it won't shrink. Usually it grows a
little. Almost every file is random. Compression works because the files we care about
aren't.

## short2 The Berry paradox as a program
> visual: the phrase "the smallest number that cannot be described in under sixty letters".
> A letter counter stops at 57.
[b1] Here's a number that can't exist: the smallest number that cannot be described in
under sixty letters. Because <bookmark mark="count"/>I just described it, in under sixty
letters.

> visual: "K(x) = length of the shortest program that prints x".
[b2] Swap words for programs, and the paradox becomes a theorem. The complexity of a
string, <bookmark mark="K"/>K, is the length of the shortest program that prints it.

> visual: the code box: "for x in all strings, shortest first: if K(x) > L: print(x);
> stop".
[b3] Suppose some program computes K. Then write this one: go through strings in order,
and <bookmark mark="first"/>print the first one with K bigger than L.

> visual: the code box splits into "fixed part" and "L: about log2 L bits"; a bar for the
> program's length next to a much longer bar for L.
[b4] That program is a fixed size, plus the number L, which only takes as many bits as L
has binary digits. Make L big enough, and <bookmark mark="short"/>the program is shorter
than L.

> visual: the printed string labelled "K > L", the program labelled "length < L", a red
> cross. Text: "no program computes K".
[b5] But it prints a string whose shortest program is longer than L, and this program,
shorter than L, just printed it. That's a contradiction. So <bookmark mark="none"/>no
program can compute K. Every string has a shortest description, and no one program can
find it for every string.

## short3 You can't prove a string is random
> visual: a million coin flips scrolling by, labelled "almost surely random".
[b1] Flip a coin a million times. The string you get is almost certainly random: no
program much shorter than it prints it. But with the usual axioms of math,
<bookmark mark="never"/>you'll never prove that.

> visual: the code box: "for each proof, in order: if it proves K(x) > L for some x:
> print(x); stop". A box "axioms + proof checker".
[b2] Write a program that searches through every proof, in order, for one
that says <bookmark mark="claim"/>some string needs a program longer than L bits. When it
finds one, it prints that string.

> visual: length split: "axioms + checker" plus "about log2 L bits", shorter than a bar
> for L.
[b3] This program is a fixed size, the axioms and the proof checker, plus the number L,
which only takes as many bits as L has binary digits. Pick L big, and
<bookmark mark="short"/>the program is shorter than L bits.

> visual: the program printing a string labelled "proven: needs more than L", the program
> labelled "fewer than L bits". Red cross.
[b4] So if it ever found that proof, a program shorter than L would print a string that
was proven to need more than L. <bookmark mark="wrong"/>The proof would be wrong.

> visual: the search spinning forever. Text: "past L, no string can be proven random".
[b5] So as long as your axioms only prove true things, the search never ends. Past about
the size of the axioms, no string can be proven random. The usual axioms fit in far fewer
than a million bits. <bookmark mark="almost"/>So your million coin flips are almost surely
random, and no proof will ever say so.
