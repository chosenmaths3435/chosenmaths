# Godel and Turing proved the same theorem

## s01 Hook
> visual: a dark title strip: "Konigsberg, September 1930" (with the umlaut on screen).
> Below it, a quote in large text at "six": "Wir mussen wissen. Wir werden wissen."
> (umlaut on screen), and under it in smaller text, "We must know. We will know.",
> attributed to David Hilbert.
[b1] In September nineteen thirty, David Hilbert, one of the most famous mathematicians
alive, gave a speech in Konigsberg. He ended it with <bookmark mark="six"/>six words.
"We must know. We will know."

> visual: the quote shrinks to the top. A row of question marks appears, each one
> turning into a tick. At "before" a calendar flips back one day, and a small label
> appears: "Kurt Godel, 24". The ticks stop; the last question mark stays.
[b2] He meant that every question in math has an answer, and that we'll find it.
<bookmark mark="before"/>The day before, in the same city, a twenty-four-year-old
named Kurt Godel had quietly announced a theorem that says no fixed set of rules can
get you there.

> visual: at "machines" a strip of tape with a small head over it slides in on the
> right, labelled "Turing, 1936". On the left a column of proof lines, labelled
> "Godel, 1930". The two sit apart.
[b3] Six years later, Alan Turing proved something that sounds just as bad, about
<bookmark mark="machines"/>machines. Godel's theorem is about proofs. Turing's is
about computers.

> visual: the two halves slide together and overlap. Title card at "same": "The same
> theorem, twice".
[b4] They come from different fields and they look nothing alike. But I'd argue
they're <bookmark mark="same"/>the same theorem.

## s02 The question
> visual: two labels side by side: "logic: proofs" and "computer science: programs".
> At "reason" they slide together under one heading: "reasoning about reasoning".
[b1] Logic studies proofs. Computer science studies programs. But both fields started
from the same place. They're about <bookmark mark="reason"/>reasoning about our own
ability to reason.

> visual: the heading fades and a question takes its place: "What problems can we
> solve?" At "two" the words "problems" and "solve" turn gold.
[b2] And they ask the same question. What problems can we solve? As it stands, that's
too vague to answer. To make it math, you have to say what you mean by
<bookmark mark="two"/>two words. Problem, and solve.

> visual: the question becomes the root of a fork with two branches. At "machine" the
> left branch fills in: "problem = string", "solve = machine", ending in "the halting
> problem". At "proof" the right branch fills in: "problem = sentence", "solve =
> proof", ending in "incompleteness".
[b3] There's more than one reasonable way to do it. Say a problem is a string of
symbols, and solving it means running a <bookmark mark="machine"/>machine, and you get
Turing's halting problem. Say a problem is a sentence, and solving it means writing
a <bookmark mark="proof"/>proof, and you get Godel's incompleteness theorem.

> visual: the fork stays; the left branch glows.
[b4] Let's take them one at a time.

## s03 Problems as strings
> visual: the fork shrinks to a small icon in the corner with the left branch lit.
> Centre: the question "is n prime?". Then the number 7 and, at "binary", its binary
> string 1 1 1 in boxes.
[b1] Start with problem. Take a yes-or-no question, like "is this number prime?". Its
inputs are strings of symbols. Seven, written in <bookmark mark="binary"/>binary, is
the string one one one.

> visual: a bin labelled "yes" fills with the binary strings for 2, 3, 5, 7, 11, 13,
> then "...". Strings for 4, 6, 9 bounce off. Tag: "a problem = a set of strings".
[b2] So the problem is a set of strings: the ones where the answer is
<bookmark mark="yes"/>yes. Two, three, five, seven, and so on, all written in binary.

> visual: a Turing machine: a long tape of cells, a head with a state label "q0" above
> one cell, and a small rule table on the side with three rows like "q0, 1 -> write
> 0, right, q1". At "rule" one row lights up and the head carries it out: it writes,
> moves one cell, and its state label changes.
[b3] Now, solve. Turing's model of a computer is a machine with a long tape, a head
that reads one cell at a time, and a short table of rules. Each
<bookmark mark="rule"/>rule says: if you're in this state and you see this symbol,
write a symbol, move left or right, and switch state.

> visual: the machine runs a few quick steps on its own. A faint laptop outline appears
> beside it with an equals sign between them. At "method" a wider tag appears around
> both: "any step-by-step method", with a small "?".
[b4] That's the whole thing, and it's enough. Given enough tape and time, a machine
like this can do anything a laptop can. As far as anyone knows, it can carry out any
step-by-step <bookmark mark="method"/>method at all.

> visual: inputs go into the machine one at a time. Each time the head stops and a
> light shows "yes" (green) or "no" (red), matching the bin from b2. Tag at "every":
> "solve = always stop, always right".
[b5] A machine solves a problem if, on <bookmark mark="every"/>every input, it
eventually stops and gives the right answer: yes for the strings in the set, and no
for the rest. It can't run forever on any of them.

> visual: the rule table slides off the machine and flattens into one long string of
> symbols. At "input" that string feeds onto the tape of a second machine.
[b6] One more thing, and it's the important one. The rule table is finite, so you can
write it out as one string. That means a machine can be the
<bookmark mark="input"/>input to another machine. A compiler does this all day.

## s04 The halting problem
> visual: a machine M and an input string w, with an arrow into a box with a question:
> "does M halt on w?" Two outcomes below it: "halts" and "runs forever".
[b1] So here's a problem about machines. Given a machine M and an input w, does M
eventually stop on w? Or does it <bookmark mark="forever"/>run forever? That's the
halting problem.

> visual: M runs on w, with a step counter ticking: 10, 1000, 1000000. At "nothing" the
> counter freezes and a question mark appears beside it. Then the counter shows
> 1000001 in faint gold.
[b2] The obvious approach is to run it. If it stops, you'll see it stop, and you can
say yes. But if it's still going after a million steps, you've learned
<bookmark mark="nothing"/>nothing. Maybe it stops at step one million and one.

> visual: a box labelled H. M and w go in; a single word comes out: "halts" or
> "loops". A tick next to it.
[b3] So running it isn't enough. Could a cleverer machine always tell? Suppose one
exists. Call it <bookmark mark="h"/>H. Give H any machine and any input, and it
always stops with "halts" or "loops", and it's always right.

> visual: a bigger box labelled D, with H drawn inside it. A machine M goes into D. At
> "own" D copies M's description and feeds both copies into H: "M, run on M".
[b4] Now use H to build a new machine. Call it D. D takes a machine M, and asks H one
question: what does M do when you feed it its <bookmark mark="own"/>own description?

> visual: inside D, H's answer goes to a switch. At "opposite": "halts" leads to a loop
> arrow spinning forever; "loops" leads to a stop sign.
[b5] Then D does the <bookmark mark="opposite"/>opposite. If H says M halts, D loops
forever. If H says M loops, D halts.

> visual: D's own description goes into D. The two branches play out in turn: at
> "loops" the "halts" branch spins; at "halts" the "loops" branch stops. Both get a red
> cross. At "wrong" H gets a red cross.
[b6] Now feed D its own description. Does D halt? If H says D halts, then D
<bookmark mark="loops"/>loops. If H says D loops, then D
<bookmark mark="halts"/>halts. Either way, H is <bookmark mark="wrong"/>wrong.

> visual: the red cross on H stays; text "no machine solves the halting problem".
[b7] So H can't exist. No machine solves the halting problem.

> visual: a grid. Rows are labelled M1, M2, M3, ... and columns are labelled by the
> same machines' descriptions, in the same order. Each cell shows a green tick (halts)
> or a loop arrow (loops). At "diagonal" the diagonal cells light up gold and each one
> flips.
[b8] Here's another way to see it. Every machine is a finite string, so you can list
them all. Put the list down the side, and the same list across the top. Each cell says
whether that machine halts on that description. D goes down the
<bookmark mark="diagonal"/>diagonal and flips every entry.

> visual: the flipped diagonal forms a new row, labelled D. It is compared with each
> row in turn; the differing cell flashes red. At "not" D's row gets a red cross. At
> "built" an arrow from D's row back to H, and H gets the red cross. Small tag:
> "Cantor's diagonal".
[b9] So D's row differs from every row somewhere. D is <bookmark mark="not"/>not on
the list, but the list has every machine on it. The only way out is that D doesn't
exist, and D was <bookmark mark="built"/>built from H. If you've seen Cantor's
diagonal argument, this is the same move.

> visual: the grid fades. D's box remains, with the arrow from D's description back
> into D glowing.
[b10] Notice where the trouble came from. Nothing about tapes or heads. It came from
the fact that machines can <bookmark mark="read"/>read descriptions of machines.

## s05 Problems as sentences
> visual: the corner fork icon switches to the right branch. Centre: the sentence
> "Every even number bigger than 2 is the sum of two primes."
[b1] Now the other road. This time a problem is a statement about numbers, like
<bookmark mark="goldbach"/>"every even number bigger than two is the sum of two
primes".

> visual: an alphabet strip of symbols: for all, there exists, not, and, =, +, times
> (as a cross), 0, S, (, ), x, y. At "grammar" a short formal sentence assembles from
> them: "for all x, not (S(x) = 0)", with a plain gloss under it: "0 is not the next
> number after anything".
[b2] To make that precise, logicians use a formal language. There's a small alphabet:
for all, there exists, not, equals, plus, times, zero, and a symbol for "the next
number". And there are <bookmark mark="grammar"/>grammar rules for which strings
count as sentences.

> visual: the formal sentence gets a "true" tag. Below it, a second line: "true" and
> "proved" as two separate boxes, with a gap between them at "another".
[b3] Every sentence is either true or false about the natural numbers. But being true
is one thing. Knowing it is <bookmark mark="another"/>another.

> visual: a numbered proof, five lines. Each line has a small tag on the right:
> "axiom", "axiom", "rule from 1, 2", "axiom", "rule from 3, 4". At "rules" the tags
> light up one at a time.
[b4] So, solve. Solving a sentence means proving it, or proving its opposite. A proof
system has axioms, which are sentences you start from, and
<bookmark mark="rules"/>rules for getting new sentences from old ones. A proof is a
list of sentences, where each line is an axiom or follows from earlier lines by a rule.

> visual: a small machine like the one from before scans down the proof, ticking each
> line. Tag at "machine": "checking a proof is mechanical".
[b5] As long as you can tell which sentences are axioms, checking a proof is
mechanical. You don't need to understand it. You check each line against the rules. A
<bookmark mark="machine"/>machine could do it. Hold on to that.

> visual: a sentence goes into a box labelled "Hilbert's dream". Out comes either a
> proof of it or a proof of its opposite. Tags under the box appear one by one:
> "settles every sentence", "never proves anything false", and at "check" "a machine
> can check the proofs". At "cheat" a list "axioms: every true sentence" appears and
> gets a red cross. The quote "We will know." returns faintly at the top at "know".
[b6] Hilbert hoped for a proof system for arithmetic that settles everything. For
every sentence, a proof of it or a proof of its opposite. It would never prove anything
false, and a machine could <bookmark mark="check"/>check its proofs. That last part
matters, or you could <bookmark mark="cheat"/>cheat and call every true sentence an
axiom. That's the <bookmark mark="know"/>"we will know".

## s06 Incompleteness
> visual: the symbols from the alphabet strip each get a small number underneath:
> "for all" -> 1, "not" -> 2, "=" -> 3, and so on. At "sentence" the formal sentence from s05
> collapses into one long number. At "proof" the whole proof from s05 collapses into an
> even longer number.
[b1] Godel's first move was to turn everything into numbers. Give every symbol a code
number. Then a <bookmark mark="sentence"/>sentence, which is a string of symbols, gets
one big code number, and so does a <bookmark mark="proof"/>proof, which is a list of
sentences.

> visual: text "p is the code of a proof of the sentence with code s". At "numbers" it
> gets a tag: "a statement about numbers".
[b2] Now a claim like "this number is the code of a proof of that sentence" is itself
a statement about <bookmark mark="numbers"/>numbers. Writing it out with plus and
times takes real work, but it can be done. So arithmetic can talk about its own
proofs.

> visual: on the left, the rule table flattening into a string (from s03). On the
> right, a proof flattening into a number. An equals sign between them. At "describe"
> both glow.
[b3] Sound familiar? It's the same trick as writing a machine out as a string. The
system can now <bookmark mark="describe"/>describe itself.

> visual: a sentence in a box, labelled G. Its text: "G has no proof in this system."
> An arrow from the text back to the label G. At "feed" a small inset: D's description
> going into D, beside G's code number going into G.
[b4] Then Godel built a sentence, call it G, that says <bookmark mark="g"/>"G has no
proof in this system". The details are technical, but the idea is to
<bookmark mark="feed"/>feed a sentence its own code number, a lot like feeding D its
own description.

> visual: a branch "suppose G has a proof". At "false" it leads to "the system proved
> something false" with a red cross. Then the branch is struck out, and "G has no
> proof" gets a tick.
[b5] Is G provable? Suppose it is. Then the system proves G, but G says it has no
proof, so the system proved something <bookmark mark="false"/>false. If the rules
never prove anything false, that can't happen. So G has no proof.

> visual: "G has no proof" (ticked) moves next to G's own text "G has no proof." They
> match, and G gets a "true" tag at "true".
[b6] But that's exactly what G says. So G is <bookmark mark="true"/>true. A true
sentence, with no proof.

> visual: the opposite sentence "G has a proof" appears, tagged "false", so "no proof
> either". Both G and its opposite sit in a box labelled "not settled". At
> "incomplete" the box gets the label "incomplete".
[b7] And its opposite, "G has a proof", is false, so that has no proof either. The
system can't settle G. It's <bookmark mark="incomplete"/>incomplete.

> visual: G is added to the axiom list. At "new" a new sentence G' appears: "G' has no
> proof in the new system". It repeats once more with G'' and then "...". At "every"
> three tags: "a machine checks the proofs", "never proves anything false", "does
> arithmetic with + and x".
[b8] Adding G as a new axiom doesn't fix it. G is true, so the bigger system still
never proves anything false, and a machine can still check it. So it has a
<bookmark mark="new"/>new sentence of its own, saying "I have no proof in the new
system". The same goes for <bookmark mark="every"/>every proof system that a machine
can check, that never proves anything false, and that can do basic arithmetic with
plus and times.

> visual: a small note card: "assumed: never proves anything false". At "less" it
> changes to "Rosser, 1936: never contradicting itself is enough".
[b9] One caveat. This argument assumed the rules never prove anything false. That can
be weakened a lot. A few years later, Barkley Rosser showed it's enough that the rules
<bookmark mark="less"/>never contradict themselves.

## s07 Side by side
> visual: a two-column table, "Turing" and "Godel". Rows appear at the bookmarks.
> At "problem": "a string" | "a sentence". At "solve": "a machine stops with the
> answer" | "a proof of it or its opposite".
[b1] Let's put them side by side. A <bookmark mark="problem"/>problem is a string, or
a sentence. To <bookmark mark="solve"/>solve it, you need a machine that stops with
the answer, or a proof of it or its opposite.

> visual: new row at "reads": "machines read machines" | "sentences talk about codes
> of sentences".
[b2] The key ingredient on both sides is that the system can describe itself. A
machine <bookmark mark="reads"/>reads the description of a machine. A sentence talks
about the code number of a sentence.

> visual: new row at "d": "D: do the opposite of what H says about me" | "G: I have
> no proof". At "against" both cells glow.
[b3] And then each side builds something that points back at itself.
<bookmark mark="d"/>D says, "do the opposite of whatever H predicts about me". G says,
"I have no proof". Both turn the system's own judgment
<bookmark mark="against"/>against it.

> visual: the table's two columns slide together until they overlap. At "other" an
> arrow from the Turing column into the Godel column.
[b4] Same shape. But this is more than an analogy. You can get one theorem
<bookmark mark="other"/>straight out of the other.

## s08 One from the other
> visual: a machine with a sentence on its tape. A stream of candidate proofs flows
> past, shortest first. Each gets checked and rejected. At "stops" one is accepted
> and the machine stops with a green light.
[b1] Remember, checking a proof is mechanical. So here's a machine. Given a sentence,
it goes through every possible proof, shortest first, and checks each one. If it finds
a proof of the sentence, it <bookmark mark="stops"/>stops.

> visual: text "provable" = "the proof search halts". At "halting" the word "halts"
> glows.
[b2] That machine halts on a sentence exactly when the sentence has a proof. So "is
this provable?" is a <bookmark mark="halting"/>halting question.

> visual: text "M halts on w" turns into "there is a number that codes a finished run
> of M on w", tagged "a sentence of arithmetic". At "run" a short tape run plays
> and collapses into one number.
[b3] It works the other way too. "Machine M halts on input w" can be written as a
sentence of arithmetic. It says there's a number that codes a complete
<bookmark mark="run"/>run of M on w, ending in a stop.

> visual: "Hilbert's dream" box from s05 returns, with its three tags. Then two proof
> searches side by side:
> left looking for "M halts on w", right looking for "M never halts on w". Both start
> at "same".
[b4] Now suppose Hilbert got his wish: a proof system that a machine can check, that
settles every sentence, and that never proves anything false. Here's how to solve the halting problem. Given M and w,
search for a proof of "M halts on w" and a proof of "M never halts on w", at the
<bookmark mark="same"/>same time.

> visual: at "one" one of the searches stops with a proof. A tick at "right". The
> whole setup gets boxed and labelled "a machine that solves the halting problem".
[b5] The system settles everything, so <bookmark mark="one"/>one of them has a proof,
and that search stops. The system never proves anything false, so the answer is
<bookmark mark="right"/>right. That's a machine that solves the halting problem.

> visual: at "impossible" the box from b5 gets the red cross from s04. Then
> "Hilbert's dream" gets a red cross. Tag: "incompleteness".
[b6] Which we know is <bookmark mark="impossible"/>impossible. So no such proof
system exists. That's a version of the incompleteness theorem, out of the halting
problem in a few lines.

> visual: two columns: "halts" (a short tape run, then a proof made of its steps,
> ticked) and "never halts" (a run trailing off to "...", then "sometimes no proof" in
> gold).
[b7] It even tells you where the gaps are. In any system that can do basic arithmetic,
if a machine does halt, there's a proof: write down the run, step by step. So the gaps
are on the <bookmark mark="never"/>other side. Some machines never halt, and the
system has no proof that they don't.

> visual: the Goldbach sentence from s05 returns. A program checks 4, 6, 8, 10, ...,
> each split into two primes (4 = 2 + 2, 6 = 3 + 3, 8 = 3 + 5, ...). Tag: "stops if
> it finds an even number that fails". At "nobody" a question mark over the program.
[b8] And these questions aren't exotic. Go back to the statement about even numbers.
Write a program that checks four, six, eight, and so on, and stops the moment it finds
an even number that isn't the sum of two primes. That statement is true exactly when
the program never halts. And as of today, <bookmark mark="nobody"/>nobody knows if it
does. That doesn't make it unprovable. We just don't know yet.

## s09 Reasoning about reasoning
> visual: the heading "reasoning about reasoning" from s02 returns. Under it: a machine
> reading a machine's string, and arithmetic reading a proof's code number.
[b1] So why do these limits exist? Go back to where we started. Both fields study
reasoning, and their tools are made of the same stuff as the thing they study.
Machines are strings, so machines can read machines. Proofs are numbers, so
<bookmark mark="talk"/>arithmetic can talk about proofs.

> visual: D, G, and the flipped diagonal row from s04's grid appear in a row. A single
> loop arrow is drawn around each.
[b2] Once a system can describe itself, you can build something that says "do the
opposite of whatever you say about me". That's <bookmark mark="dg"/>D, and that's G.
And it's the same move as Cantor's diagonal.

> visual: text "Lawvere's fixed point theorem, 1969" with three arrows out of it to
> "Cantor", "Godel", and, faintly at "later", "Turing".
[b3] In nineteen sixty-nine, William Lawvere wrote down a single theorem with Cantor's
and Godel's arguments as special cases. <bookmark mark="later"/>Later work fit
Turing's in too.

> visual: the fork from s02, both branches lit, now ending in the same wall.
[b4] So the limit isn't a flaw in Turing's machines, or in some particular list of
axioms. Pick any meaning for problem and solve that's strong enough to describe
itself and flip its own answers, and you hit the same <bookmark mark="wall"/>wall.

## s10 Ending
> visual: a machine on the left and a proof on the right, with a two-way arrow between
> them: "a proof checker is a machine", "halting is a sentence". At "program" the
> two pictures slide toward each other.
[b1] Here, machines and proofs ran side by side. A proof checker is a machine, and
halting is a sentence. But there's a deeper match, where they stop being two things at
all. A proof <bookmark mark="program"/>is a program. A statement is a type.

> visual: the arrow fills in solid. Text: "the Curry-Howard correspondence". Fade to
> black.
[b2] That's the <bookmark mark="ch"/>Curry-Howard correspondence, and it's a story for
another video.

## short1 The halting problem
> visual: a program's code scrolling in a box, with a question under it: "does it ever
> stop?"
[b1] Here's a question no program can answer about every program. Does it
<bookmark mark="stop"/>ever stop?

> visual: the program runs with a step counter: 10, 1000, 1000000. The counter freezes
> with a question mark at "nothing".
[b2] You might think you can just run it. If it stops, you'll see it. But if it's
still running after a million steps, you've learned <bookmark mark="nothing"/>nothing.
It might stop at step one million and one.

> visual: a box labelled H. A program and an input go in; "halts" or "loops" comes out.
[b3] So suppose some program H is smarter. Give it any program and input, and it
always answers <bookmark mark="h"/>"halts" or "loops", and it's always right.

> visual: a bigger box D with H inside. A program goes in, gets copied, and both copies
> go into H. H's answer goes to a switch: "halts" leads to a spinning loop, "loops"
> leads to a stop sign.
[b4] Now build a new program, D. D takes a program, asks H what that program does when
it's fed its own code, and then does the <bookmark mark="opposite"/>opposite. If H
says halts, D loops forever. If H says loops, D stops.

> visual: D's code goes into D. The two branches play out and each gets a red cross.
> At "wrong" H gets a red cross.
[b5] Now feed D its own code. If H says D halts, D loops. If H says D loops, D halts.
Either way, H is <bookmark mark="wrong"/>wrong.

> visual: text "the halting problem: no program solves it". Then D's code with an arrow looping
> back into D, glowing.
[b6] So H can't exist. That's Turing's halting problem. And the whole trick is that
<bookmark mark="read"/>programs can read programs.

## short2 A true statement with no proof
> visual: a box labelled "your rules" with a list of axioms. Beside it, a sentence in
> a box labelled G, with the text hidden, a "true" tag, and a "no proof" tag.
[b1] There's a true statement about numbers that your rules can't prove. Whatever your
rules are. Here's how Kurt Godel <bookmark mark="found"/>found it.

> visual: a numbered proof, each line tagged "axiom" or "rule". A small machine ticks
> each line.
[b2] A proof is a list of statements, each one an axiom or following from earlier
lines by a rule. A machine can <bookmark mark="mech"/>check it.

> visual: symbols get code numbers, then a statement collapses into one number, then a
> proof into a longer one. Text: "p codes a proof of s" tagged "a statement about
> numbers".
[b3] Godel turned every symbol into a number. So every statement, and every proof, gets
a <bookmark mark="code"/>code number. Now "this number codes a proof of that
statement" is itself a statement about numbers.

> visual: G's text is revealed: "G has no proof." An arrow loops from the text back to G.
[b4] Then he built a statement, G, that says <bookmark mark="g"/>"G has no proof".

> visual: "suppose G has a proof" leads to "the rules proved something false", red
> cross. Then "G has no proof" is ticked and matched against G's text. G gets "true".
[b5] Suppose G had a proof. But G says it has no proof, so the rules proved something
false. If the rules never
prove anything false, that can't happen. So G has no proof. But that's exactly what G
says. So G is <bookmark mark="true"/>true.

> visual: G is added to the axioms; a new G' appears, then G'', then "...".
[b6] A true statement with no proof. Adding G as an axiom doesn't help. The new
rules have a <bookmark mark="new"/>new G. Any rules for arithmetic that a machine can
check, and that never prove anything false, have this gap.

## short3 The same theorem
> visual: two labels, "Godel: incompleteness" and "Turing: the halting problem". At
> "disguise" the first slides over the second like a mask.
[b1] Godel's incompleteness theorem is hiding inside the halting problem. It's
Turing's theorem in <bookmark mark="disguise"/>disguise.

> visual: a program with "does it ever stop?" and a red cross over a box labelled H.
[b2] The halting problem says no program can tell, for every program, whether it
<bookmark mark="stop"/>eventually stops. Alan Turing proved a version of it in
nineteen thirty-six.

> visual: a machine checking a stream of candidate proofs, shortest first.
[b3] Now take a proof system for arithmetic, with proofs a machine can check. Then a
program can <bookmark mark="search"/>search through every proof, shortest first.

> visual: text "this program halts" turns into a sentence about numbers.
[b4] And "this program halts" can be written as a <bookmark mark="sentence"/>statement
about numbers.

> visual: two searches side by side, for "halts" and for "never halts". One stops with
> a proof; a tick.
[b5] Suppose the proof system settled every statement, and never proved anything
false. Then to tell whether a program halts, search for a proof that it does and a
proof that it doesn't, at the same time. One of them exists, so the search
<bookmark mark="one"/>stops, with the right answer.

> visual: the whole setup gets the red cross from b2. Text: "some statements have no
> proof either way".
[b6] That would solve the halting problem. Which is impossible. So if the rules never
prove anything false, some statements have no proof <bookmark mark="either"/>either
way. That's incompleteness, straight out of Turing.

> visual: "a machine" and "a proof" side by side, merging into one shape.
[b7] One theorem about machines, one about proofs. And it's the
<bookmark mark="same"/>same theorem.
