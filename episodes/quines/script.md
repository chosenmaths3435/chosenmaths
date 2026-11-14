# Can a program print itself?

## s01 Hook
> visual: an editor window titled "self.py", empty, with a blinking cursor. Below it a
> terminal prompt "$ python self.py". At "character" the editor fills with lines of
> placeholder code and an arrow labelled "=" points from the editor to the terminal output.
[b1] Can a program print its own source code? Not some other program. Its own text,
<bookmark mark="character"/>character for character.

> visual: the editor shows "print(open(__file__).read())". The terminal runs it and prints the
> same line. At "cheating" a red line strikes through the code and the word "cheating" appears.
[b2] There's an obvious way. Open the file the program is saved in, and print what's inside.
But that's <bookmark mark="cheating"/>cheating. The program didn't produce itself. It just
looked itself up.

> visual: two rules appear under the editor: "no reading files", "no input". Then the title
> card "Can a program print itself?".
[b3] So here are the rules. No <bookmark mark="files"/>reading files, and
<bookmark mark="input"/>no input. The program has to produce its own text from scratch.

## s02 Why it's hard
> visual: the editor shows 'print("hello")' and the terminal prints "hello".
[b1] Let's just try. In Python, print, followed by something in quotes, prints whatever's in
the quotes.

> visual: the editor shows 'print("' then a highlighted gap then '")'. At "again" the gap
> fills with a smaller copy: 'print("print(" ... ")")'.
[b2] So to print the whole program, the quotes have to hold the whole program. That's print,
then a quote, then the whole program <bookmark mark="again"/>again.

> visual: the nesting repeats: each copy gets a smaller copy inside its quotes, five or six
> levels, shrinking toward a point and running off the side.
[b3] But that copy needs its own copy inside its quotes, and so on, forever. Every attempt
is longer than the thing it's trying to print.

> visual: the nested strings fade. Text: "can't contain a copy" crossed out to the left,
> "build one" to the right.
[b4] So a program can't contain a full copy of itself. If it's going to print itself, it has
to build the copy somehow.

## s03 The trick in English
> visual: the sentence in two colors: 'Print two copies of the following, the second one in
> quotes:' (blue) followed by '"Print two copies of the following, the second one in quotes:"'
> (orange, in quotes).
[b1] Here's how to do it in English. Read this instruction, and follow it.

> visual: below, the output builds: first the orange text without quotes (a first copy), then
> the orange text again with its quotes (the second copy). At "whole" the output lines up
> under the original and the two match, letter for letter, with a "=" between them.
[b2] The first copy gives you the instruction. The second copy, in quotes, gives you the
quoted part. Put them together, and you've written out the
<bookmark mark="whole"/>whole thing again.

> visual: labels under the original: "instructions" under the blue half and "data" under the
> orange half. At "twice" two arrows go from the data to the two copies in the output.
[b3] Notice what happened. The quoted part is just data. It doesn't do anything. The
instructions in front of it do the work, and they use the data
<bookmark mark="twice"/>twice: once as itself, and once in quotes.

> visual: the orange data and the blue instructions side by side, with "data = copy of the
> instructions" between them.
[b4] And the data is a copy of the instructions, not of the whole sentence. So nothing has to
contain itself.

## s04 The construction
> visual: a long box labelled SELF, split into two boxes labelled A and B.
[b1] Let's do the same thing with programs. We'll write in pseudocode: plain steps that any
programming language could follow. Our program, call it SELF, comes in two parts, A and then
B.

> visual: a string "w" on the left, an arrow, and on the right a small box labelled "P(w)"
> containing 'write "w"'. Under the arrow: "add write and quotes".
[b2] First, one small tool. For any string w, there's an easy program that writes out w:
write, then w in quotes. Call it P of w. And going from w to P of w is mechanical. You just
add the write and the quotes, so a program can do it too.

> visual: an empty strip of paper appears under the boxes, labelled "written so far". Box B
> expands into three numbered steps: "1. Let w be what's written so far."
> "2. Write P(w) in front of w." "3. Print everything written."
[b3] Part B says: look at what's been written so far, and call it w. Write P of w in front of
it. Then print everything.

> visual: box A expands into one step: "1. Write the text of B." Then "A = P(B)" under it.
[b4] Part A says: write out the text of B. That's all. So A is just P of B, the program that
writes B.

> visual: the strip below the boxes. A lights up and the text of B appears on the strip.
> At "sees" B lights up and the text on the strip is labelled "w = B". At "front" the text of A
> slides in on the left of the strip. At "prints" the strip reads "A B", the whole strip flies
> to an output box, and a "=" points at the SELF box above.
[b5] Now run SELF. A goes first, and writes out the text of B. Then B runs. It
<bookmark mark="sees"/>sees its own text, so w is B. It writes P of B in
<bookmark mark="front"/>front, which is exactly A. Then it <bookmark mark="prints"/>prints
A followed by B, which is SELF.

> visual: an arrow from A to B labelled "copy of". At "never" an arrow from B to A appears
> dashed and is crossed out.
[b6] So where did the infinite regress go? A depends on B. It's a copy of B's text. But B
<bookmark mark="never"/>never mentions A. It doesn't need to, because it rebuilds A from
what A left behind. The arrows only go one way, so there's no loop.

> visual: the English sentence from before appears above the boxes. Its blue half is joined to
> B and its orange half to A by thin lines.
[b7] It's the same as the English sentence. The quoted data is A. The instructions, two
copies with the second one in quotes, are B.

## s05 A real language
> visual: the Python file from the user's notes, five lines, in a code panel:
> def PB():
>     return 'def B(w):\n    return f"def PB():\\n    return {repr(w)}\\n{w}\\nprint(B(PB()))"'
> def B(w):
>     return f"def PB():\n    return {repr(w)}\n{w}\nprint(B(PB()))"
> print(B(PB()))
[b1] This works in any real programming language. Here it is in Python, with one extra line
at the end to start it.

> visual: lines 1 and 2 (PB) highlighted with the label "A".
[b2] The function P B is part A. All it does is hand back the text of B, as a string.

> visual: lines 3 and 4 (B) highlighted with the label "B". Inside the f-string, the part
> "def PB():\n    return {repr(w)}" glows with the label "P(w)", then "repr" glows with the
> label "adds quotes".
[b3] B takes that string and builds a program around it. First it writes the definition of
P B, with the string inside. That's the step from w to <bookmark mark="repr"/>P of w.
Python's repr function does the fiddly part: it adds the quotes, and escapes the special
characters inside.

> visual: "{w}" glows, then "print(B(PB()))" at the end of the f-string glows.
[b4] Then it adds w itself, which is B's own text, and finally the last line, which runs
everything.

> visual: the last line of the file highlighted. Then a terminal: "$ python quine.py" and the
> five lines print below. At "character" the output and the file are shown side by side,
> lines matched, and "diff: identical" appears.
[b5] That last line hands P B's string to B, and prints the result. Run it, and out comes the
program, <bookmark mark="character"/>character for character.

> visual: the word "quine" appears over the code.
[b6] A program like this is called a quine. Douglas Hofstadter named them after the
philosopher Willard Van Orman Quine, who studied sentences that talk about themselves.

## s06 Running an interpreter backwards
> visual: a box labelled "interpreter". An expression "(list 'a 'b)" goes in the left side, and
> the value "(a b)" comes out the right.
[b1] There's a completely different way to find a quine: run an interpreter backwards. An
interpreter is a program that runs other programs. Usually it's a function. You hand it an
expression, and it hands you back the value.

> visual: the box relabels to "evalo", and its arrows turn into a two-way link between
> "expression" and "value". At "either" a "?" appears on the left side, then on the right.
[b2] In a language called miniKanren, you can write it as a relation instead. It just states
when an expression and a value go together. So you can fill in
<bookmark mark="either"/>either side, and ask for the other.

> visual: the query appears: "(run 1 (q) (evalo q '() q))". At "itself" both occurrences of q
> glow the same color.
[b3] So ask it for an expression whose value is <bookmark mark="itself"/>itself. The same
unknown, q, on both sides.

> visual: the answer appears below (miniKanren names the variable "_.0"; show it as x, with a
> small note "variable renamed"):
> ((lambda (x) (list x (list 'quote x)))
>  '(lambda (x) (list x (list 'quote x))))
[b4] It searches through programs, and comes back with this.

> visual: the quoted second line highlighted orange and labelled "data"; the lambda on the
> first line highlighted blue and labelled "instructions". At "quotes" the output is shown: the
> lambda, then the lambda with a quote mark, matching the original.
[b5] Look at its shape. On the second line, a quoted copy of a function. That's the data. On
the first line, the function itself. It takes x, and makes a list of x, and x in
<bookmark mark="quotes"/>quotes. Two copies, the second one in quotes. The search found the
same trick on its own.

## s07 The recursion theorem
> visual: the A and B boxes again, with B's step 3 "Print everything written." highlighted.
> At "anything" the word "Print" is crossed out.
[b1] Go back to B for a moment. Once B has rebuilt the text of SELF, it prints it. But it
doesn't have to print it. It could do <bookmark mark="anything"/>anything with it.

> visual: a new box T with two input slots labelled "source code" and "y".
[b2] Take any program T that expects two inputs: the source code of some program, and an
ordinary input, y.

> visual: the boxes A, B, T in a row, under the label R. A writes the text of B and T on the
> strip. At "hands" the strip, now reading "A B T", flies into T's "source code" slot, and the
> input y into its other slot.
[b3] Put A and B in front of it, and call the whole thing R. R takes an input y. A writes out
B and T. B rebuilds the whole text, A, B and T together, and
<bookmark mark="hands"/>hands it to T, along with y. So T gets the source code of the very
program it's part of.

> visual: "Recursion theorem" as a heading, then: "for every T there is R with R(y) = T(<R>, y)",
> with "<R> = the source code of R" under it. Then: "any program can use its own source code".
[b4] That's the recursion theorem. Any program can be written as if it could read its own
source code. No files needed. It can always build its own text first.

## s08 You can't list the shortest programs
> visual: two programs that do the same thing, one long and one short. The short one gets a
> star labelled "shortest".
[b1] Here's what that buys you. Call a program shortest if no shorter program does exactly the
same thing, on every input.

> visual: "No program can list all the shortest programs."
[b2] Claim: no program can print a list of all the shortest programs, even if it runs forever.

> visual: a box E printing a scrolling list of programs, drawn as bars of uneven lengths. At
> "longer" a vertical line marks a length, and further down the list a bar crosses it.
[b3] Suppose some program E did. Every behavior has at least one shortest program, and there
are infinitely many behaviors: print one, print two, and so on. So E's list never ends. And
there are only finitely many programs of each length, so sooner or later it has to list
programs <bookmark mark="longer"/>longer than any length you pick.

> visual: a program C with three numbered steps appearing one at a time: "1. Get your own
> source code." "2. Run E until it lists a program D longer than C." "3. Do what D does."
> Next to step 1, a small tag "recursion theorem".
[b4] Now write a program C. <bookmark mark="one"/>First, get your own source code, so you
know how long you are. The recursion theorem says that's allowed. <bookmark mark="two"/>Second, run E, and wait for a
program on its list that's longer than C. Call it D. <bookmark mark="three"/>Third, do
exactly what D does.

> visual: C and D side by side as bars, C shorter. "same behavior" between them. At "isn't" the
> star on D cracks. At "exist" E is crossed out.
[b5] So C does exactly what D does, and C is shorter. That means D
<bookmark mark="isnt"/>isn't a shortest program. But E listed it as one. So E can't
<bookmark mark="exist"/>exist.

> visual: the three steps of C stay on screen, with step 1 glowing.
[b6] The whole proof rests on step one. A program that can look at itself can always make
itself the counterexample.

## s09 Ending
> visual: the A/B boxes morph into a line of logic symbols, and the caption "a sentence that
> says: I have no proof".
[b1] And this isn't only about programs. Godel's famous sentence, the statement in arithmetic
that says it has no proof, is built with the same trick. Some data, and instructions that use
it twice. That's enough for anything to talk about itself.

## short1 Can a program print itself
> visual: portrait. "Can a program print itself?" at the top. The Python quine in a code panel,
> with long lines wrapped and each wrapped piece marked as a continuation, and a terminal below.
[b1] Can a program print its own source code, without reading its own file? Here's one in
Python. Run it, and out comes the program, <bookmark mark="run"/>character for character.

> visual: the English sentence, blue instructions and orange quoted data. Below it the output
> builds: the data, then the data in quotes.
[b2] It works like this sentence: print two copies of the following, the second one in
quotes, followed by that same phrase in quotes. Follow it, and you get the sentence back.

> visual: labels "instructions" and "data" under the two halves.
[b3] The quoted part is just data. The instructions in front use it twice: once as itself, and
once in quotes.

> visual: back to the code. P B highlighted as "data", then B highlighted as "instructions",
> with repr glowing.
[b4] The Python program works the same way. The function P B is the data. It holds the text of
B. B is the instructions. It takes that text, wraps it in quotes to rebuild P B, and adds its
own text after it. The last line prints the result.

> visual: an arrow from P B to B labelled "copy of", and none back.
[b5] Neither half contains a copy of the whole program. P B holds a copy of B, but B never
needs a copy of P B. It rebuilds it.

## short2 Running a program backwards
> visual: portrait. "Run a program backwards?" An interpreter box with an expression going in
> and a value coming out.
[b1] What if you could run a program backwards? An interpreter is a program that runs other
programs. Give it an expression, and it gives you back the value.

> visual: the box becomes "evalo", a two-way link, with "?" on either side.
[b2] In a language called miniKanren, you write the interpreter as a relation instead: a rule
saying which expressions and values go together. Then you can leave either side blank, and
ask the computer to fill it in.

> visual: "(run 1 (q) (evalo q '() q))", both q's glowing.
[b3] So ask it for an expression whose value is the expression itself.

> visual: the answer, on two lines.
[b4] It searches, and comes back with this.

> visual: the lambda highlighted, then the quoted copy, then the output: lambda, then lambda in
> quotes, matching the input.
[b5] The function on the first line takes x, and makes a list of x, and x in quotes. On the
second line, it's given a quoted copy of itself. So the value is the function, then the
function in quotes, which is the expression you started with. An expression whose value is
itself, found by running an interpreter backwards.

## short3 You can't list the shortest programs
> visual: portrait. "No program can list every shortest program."
[b1] No program can list every shortest program. Call a program shortest if no shorter program
does exactly the same thing.

> visual: a box E printing a list of bars of uneven lengths; a vertical line marks a length,
> and a bar further down crosses it.
[b2] Suppose some program E prints all of them, forever. There are infinitely many behaviors,
like print one, print two, and so on, and each has a shortest program. So the list never ends.
And there are only so many programs of each length, so sooner or later it lists programs
longer than any length you pick.

> visual: program C with three steps appearing one at a time, a tag "recursion theorem" next
> to step 1.
[b3] Now write a program C that does three things. <bookmark mark="one"/>Get its own source
code, so it knows its own length. Programs can always do this, by a result called the
recursion theorem.
<bookmark mark="two"/>Then run E until it lists a program longer than C. Call it D.
<bookmark mark="three"/>Then do exactly what D does.

> visual: C and D as bars, C shorter, "same behavior". D's star cracks, then E is crossed out.
[b4] Now C does the same thing as D, and C is shorter. So D isn't a shortest program, but E
listed it as one. Contradiction. So no such E can exist.
