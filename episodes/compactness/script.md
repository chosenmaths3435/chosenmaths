# Solving infinitely many problems at once

## s01 Hook
> visual: a dark screen. The question appears as large text, then the answer below it.
[b1] How do you solve infinitely many problems at the same time?
<bookmark mark="answer"/>Just solve every finite number of them.

> visual: the text clears. A column of problems drops in one by one: "x > 1", "x > 2",
> "x > 3", "x > 4", ..., continuing off the bottom of the screen. At "batch" a bracket
> grabs the first four and "x = 5" appears next to it with a tick. At "all" a real line
> appears under the column, with a marker sliding right and never stopping. A red cross
> over the whole column.
[b2] That sounds like it can't work. Try these. x is bigger than one, bigger than two,
bigger than three, and so on, forever. <bookmark mark="batch"/>Any finite batch has a
solution: pick x past the biggest one. <bookmark mark="all"/>But no real number solves
them all.

> visual: the real line under the column fades out and the column stays. At "world" a
> new, unfamiliar line slides in under the column, and the red cross turns into a tick.
> Title card: "Compactness".
[b3] Except there's a theorem in logic that says the trick works anyway. You just have to
be willing to <bookmark mark="world"/>change the world you're solving in.

## s02 Worlds and sentences
> visual: five symbols appear in a row: +, x, <, 0, 1. Label: "language".
[b1] To make that precise, we need to say what a problem is, and what a world is. Start
with a few symbols: <bookmark mark="syms"/>plus, times, less than, zero and one. This is
our language.

> visual: two rounded regions side by side. Left: the real line inside, labelled "the real
> numbers". Right: dots at the integers, labelled "the integers". Under each, the five
> symbols with small tags "usual meaning".
[b2] A world, which logicians call a <bookmark mark="model"/>model, is a set of things
with a meaning for each symbol. The <bookmark mark="reals"/>real numbers, with the usual
plus and times, are one model. The <bookmark mark="ints"/>integers are another.

> visual: above the two regions, a sentence in symbols:
> "\forall x \exists y (y + y = x)". At "half", its translation appears under it:
> "every number has a half". A small key in the corner: \forall = "for every",
> \exists = "there exists", plus \land, \lor, \lnot with their words.
[b3] A sentence is a statement built from the symbols, using "and", "or", "not", "for
every" and "there exists". Here's one. For every x, there's a y with y plus y equal to x.
In words, <bookmark mark="half"/>every number has a half.

> visual: at "reals" the left region gets a tick and "3 = 1.5 + 1.5" flashes inside it. At
> "ints" the right region gets a cross; the dot 3 is highlighted, and the halves 1 and 2
> flash with "1 + 1 = 2", "2 + 2 = 4", skipping over 3. A spotlight sweeps over each region and
> stops at its border.
[b4] A model satisfies a sentence when the sentence is true there, with "for every"
meaning every thing in that model. Every real number has a half, so
<bookmark mark="reals"/>the reals satisfy this sentence. <bookmark mark="ints"/>The
integers don't. Three has no half among the integers. Same sentence, different worlds.

> visual: a new symbol "c" joins the language row. In the reals region, c lands on 5; in
> the integers region, c lands on -2. The sentence "c > 1" appears with a tick under the
> reals and a cross under the integers.
[b5] One more piece. We can add a new symbol, <bookmark mark="c"/>c, that names one
thing. Each model gets to choose what c means. Then "c is bigger than one" is a sentence,
and a model where c means <bookmark mark="five"/>five satisfies it.

> visual: a stack of sentences on the left, a single model on the right. Ticks run down
> the stack.
[b6] So a problem is a sentence, and solving a bunch of problems means finding one model
that satisfies <bookmark mark="all"/>all of them at once.

## s03 The theorem
> visual: a box with the theorem: "If every finite subset of a set of sentences has a
> model, then the whole set has a model." Under it: "the compactness theorem (Godel, 1930,
> countably many sentences; Malcev, 1936, any number)".
[b1] Here's the compactness theorem. Take any set of sentences, even infinitely many.
<bookmark mark="thm"/>If every finite part of it has a model, then the whole set has a
model.

> visual: the column from the hook returns, rewritten as "c > 1", "c > 2", "c > 3", ...
> with a footnote "2 means 1 + 1, and so on". A bracket grabs a finite batch; the real
> line appears beside it with c landing past the batch's largest number. At "some" the
> unfamiliar line from the hook slides in, with c far off to the right, past a run of
> dots labelled 1, 2, 3, ...
[b2] Back to our problems. c is bigger than one, bigger than two, bigger than three, and
so on. <bookmark mark="batch"/>Any finite batch holds in the real numbers, as long as c
is big enough. So compactness says there's <bookmark mark="some"/>some model where c is
bigger than all of them.

> visual: the unfamiliar line wobbles and turns into a loose, irregular scatter of dots,
> with c still marked. A "?" over it.
[b3] Now, by itself that's not so impressive. With no other rules, that model could be a
<bookmark mark="weird"/>strange thing that looks nothing like the numbers we know. What
makes compactness useful is everything else you can keep true at the same time.

## s04 Infinitesimals
> visual: a long scroll titled "every sentence true in the real numbers". Visible lines:
> "every number has a half", "x times y = y times x", "every positive number has a square
> root", "...". The scroll keeps going.
[b1] So let's keep everything. Take <bookmark mark="all"/>every sentence that's true in
the real numbers. Every number has a half. Times doesn't care about order. Every positive
number has a square root. Every single one.

> visual: under the scroll, a second column: "c > 0", "c < 1", "c < 1/2", "c < 1/3", ...
> Footnote: "c < 1/n means c + c + ... + c (n times) < 1".
[b2] Then add <bookmark mark="new"/>new problems. c is bigger than zero, but smaller than
one, smaller than one half, smaller than one third, and so on.

> visual: a bracket grabs a finite batch from both columns. The last fraction in it,
> 1/7, is highlighted. The real line appears with c landing at 1/8, and every line in
> the batch gets a tick.
[b3] Check any finite batch. It only mentions finitely many of these fractions, so it
<bookmark mark="stops"/>stops somewhere. Let c be <bookmark mark="smaller"/>a smaller
fraction, and the real numbers satisfy the whole batch.

> visual: a new line, labelled "a model of everything true in R", looking just like the
> real line, with c marked just to the right of 0. Tags: "c > 0", "c < 1/n for every n".
[b4] So by compactness, there's a model that satisfies every sentence true of the real
numbers, and has <bookmark mark="c"/>a c that's bigger than zero but smaller than one over
n, for every n. An infinitely small number. <bookmark mark="inf"/>An infinitesimal.

> visual: a portrait-free text card: "Leibniz, 1680s: infinitesimals" and below it, in
> muted text, "Berkeley, 1734, attacking calculus: 'ghosts of departed quantities'". Then "Robinson, 1960s:
> they're consistent".
[b5] Leibniz built calculus out of numbers like this, and one critic called them
<bookmark mark="ghosts"/>ghosts. In the nineteen sixties, Abraham Robinson used logic to
bring them back for good.

> visual: the camera zooms into 0 on the new line. A cloud of points appears around it:
> c, 2c, c/2, c^2. At "still" a small note: "c < 1/(2n), so 2c < 1/n". Then the camera zooms out past the whole numbers to a far point
> labelled 1/c, past 1, 2, 3, ...
[b6] And since the new world agrees with the reals on every sentence, everything still
works. Zoom in on zero, and there's <bookmark mark="cloud"/>a whole cloud: two c, half
of c, c squared. Two c is <bookmark mark="still"/>still infinitesimal, since c is
smaller than one over two n. And c has a reciprocal, one over c, which is
<bookmark mark="big"/>bigger than every whole number.

> visual: two facts about R as cards. At "below": "every number is below some whole
> number", next to 1/c far past 1, 2, 3, ..., with a red "?". At "lub": "every set
> that's bounded above has a least upper bound". The cloud around 0 is boxed, with 1
> marked as an upper bound. At "half" a point s above the cloud and s/2 below it, both
> still above the cloud; footnote "s isn't infinitesimal, so s/2 isn't either". At "set"
> the words "whole number" and "set" glow in the two cards, and both cards slide off the
> scroll with a red strike.
[b7] But wait. Two facts about the reals seem to break. Every real number is
<bookmark mark="below"/>below some whole number, and one over c isn't. And
<bookmark mark="lub"/>every set that's bounded above has a least upper bound. The
infinitesimals are all below one, but no number above them is the least: if s is above
all of them, <bookmark mark="half"/>so is half of s. So is this a contradiction? No. Both
facts talk about a <bookmark mark="set"/>set of numbers: the whole numbers, or a bounded
set. Our sentences can only say "for every number", and they have no way to pick out the
whole numbers. So neither fact was one of the sentences we kept.

## s05 Coloring the plane
> visual: a plane with a few points. A unit segment pops between two of them, and they
> get different colors. More points and unit segments appear, each pair colored
> differently.
[b1] Here's a problem about pictures. Color every point of the plane, so that any two
points <bookmark mark="one"/>exactly one unit apart get different colors. How few colors
can you get away with?

> visual: the plane fills with a hexagon tiling in a seven-color pattern. One hexagon is
> highlighted with a segment across it labelled "< 1". Two same-colored hexagons are
> highlighted with a segment between their nearest points labelled "> 1". Footnote: "each border point goes to just one of its hexagons".
[b2] Seven is enough. Tile the plane with <bookmark mark="hex"/>hexagons a little less
than one unit across, and color them in this pattern. Two points in
<bookmark mark="same"/>the same hexagon are less than one apart, and
<bookmark mark="far"/>hexagons of the same color are more than one apart.

> visual: the tiling fades. An equilateral triangle with unit sides; its corners get three
> different colors.
[b3] For the other direction, look for small pictures. <bookmark mark="tri"/>Three points
at the corners of a triangle with unit sides already need three colors.

> visual: two unit triangles glued along an edge into a diamond. Corners: A at the bottom,
> B and C in the middle, D at the top. With three colors: A red, B blue, C gold, and at
> "match" D turns red.
[b4] Glue two triangles into a <bookmark mark="diamond"/>diamond. With only three colors,
the bottom and top corners <bookmark mark="match"/>have to match: each one differs from
both middle corners, and that leaves only one color.

> visual: a second diamond grows from A and rotates until its top corner D' is exactly
> one unit from D. A unit segment appears between D and D'. Both turn red, and the
> segment flashes. Label: "Moser spindle, 1961: 7 points, 4 colors".
[b5] Now build <bookmark mark="second"/>a second diamond from the same bottom corner, and
turn it until the two tops are <bookmark mark="apart"/>exactly one apart. With three
colors, both tops match the bottom, so they <bookmark mark="clash"/>match each other. So
these seven points need four colors, and so does the plane.

> visual: a number line from 1 to 8 with "4" and "7" marked as the bounds. The gap
> between them is shaded, with "?" above it and "1950 to 2018".
[b6] For almost seventy years, that's where it stood. Somewhere between
<bookmark mark="range"/>four and seven.

> visual: the plane again, with points named p, q, r, ... Three kinds of sentences
> appear: "p is red or blue or gold or green", "p is only one color", and, next to a unit
> segment from p to q, "p and q have different colors". At "finite" a bracket grabs a
> handful of sentences, and only the few points they mention stay lit.
[b7] Here's where compactness comes in. Write the problem as sentences, in a new
language: a name for every point, and a word for each color. Say each point gets one of four colors, and points one apart get different
colors. A <bookmark mark="finite"/>finite batch of these only mentions finitely many
points.

> visual: text: "every finite set of points 4-colorable => the plane is 4-colorable".
> Then it flips: "the plane needs 5 => some finite set of points needs 5". The second
> line glows.
[b8] So if every finite set of points can be colored with four colors, then
<bookmark mark="whole"/>the whole plane can. Turn that around. If the plane needs five
colors, then <bookmark mark="some"/>some finite set of points already needs five.

> visual: a dense unit-distance graph appears, drawn small, labelled "de Grey, 2018: 1581
> points". It shrinks to a smaller one labelled "2020: 509 points". The bounds line
> updates: 5 to 7.
[b9] In twenty eighteen, Aubrey de Grey found one: <bookmark mark="grey"/>fifteen hundred
eighty-one points that can't be colored with four colors, so neither can the plane. Computer searches have since cut
that to <bookmark mark="parts"/>five hundred and nine. So the answer is five, six or
seven.

## s06 Why it's true
> visual: a row of copies of the real line stacked vertically, labelled 1, 2, 3, 4, ...,
> each with c marked at 1, 1/2, 1/3, 1/4. Next to copy n: "c < 1/k for every k < n".
[b1] So why is compactness true? Here's a sketch of one proof, done first for the
infinitesimals. Line up <bookmark mark="copies"/>a copy of the real numbers for each n.
In copy n, c means one over n, so it satisfies every problem up to "c is less than one
over k", for each k below n.

> visual: a vertical slice through the stack picks one number from each copy. The slice
> becomes a sequence in brackets. Then c's slice: (1, 1/2, 1/3, 1/4, ...). Two sequences
> are added entry by entry.
[b2] Now glue them together. A new number is <bookmark mark="seq"/>a sequence, one real
number from each copy. c is the sequence <bookmark mark="cseq"/>one, one half, one
third, and so on. Add and multiply them position by position.

> visual: two sequences a and b, one above the other. Each position gets a small vote:
> "<", "=" or ">". A ballot box collects the votes.
[b3] To compare two sequences, <bookmark mark="vote"/>the positions vote. a is less than b
if it's less in most positions, and they're the same number if they agree in most
positions. But what does "most" mean?

> visual: c's sequence compared with the constant sequence (1/5, 1/5, 1/5, ...). The
> first four positions vote ">", the fifth votes "=", and every later one votes "<". The
> first five are bracketed "finitely many". Then a new sequence (1, -1, 1, -1, ...) compared with 0: votes
> alternate ">" and "<" forever, and the ballot box shows a tie with a "?".
[b4] A natural guess is "all but finitely many". That already makes
<bookmark mark="cless"/>c smaller than one over k for every k. But it isn't enough. Take
<bookmark mark="alt"/>one, minus one, one, minus one, and so on. Is it positive or
negative? Neither side wins. And in the real numbers, every number is positive, negative
or zero, so our new world has to agree.

> visual: a card titled "ultrafilter: which sets of positions count as 'most'". Three
> rules tick on one at a time: "a set or the rest counts, never both", "if two sets
> count, so does their overlap", "finite sets never count".
[b5] So we need a voting rule that always picks a winner. It's called an
<bookmark mark="uf"/>ultrafilter. It decides which sets of positions count as "most".
For any set of positions, <bookmark mark="r1"/>either it counts or the rest does, never
both. If two sets count, <bookmark mark="r2"/>so does their overlap. And
<bookmark mark="r3"/>finite sets never count.

> visual: a few sets of positions drawn as shaded strips that all overlap somewhere. At
> "grow" they expand into a full ultrafilter card. Text: "any sets that always overlap
> grow into an ultrafilter". Footnote: "uses the axiom of choice". Then the alternating
> sequence again: the odd and even positions light up as two teams, and a curtain hides
> which team wins.
[b6] Do rules like this exist? Yes, and more. Any collection of sets where every few of
them overlap can be <bookmark mark="grow"/>grown into a full voting rule. There's a
technical detail here we'll skip: the proof uses the axiom of choice, and nobody can
write such a rule down. It does decide between the odd and the even positions. It just
<bookmark mark="hidden"/>won't tell you which.

> visual: a card: "Los's theorem (Jerzy Los, 1955): a sentence is true in the glued world exactly when the
> positions where it's true count as most." Under it, two small arrows: "and -> overlap
> rule", "not -> either-or rule".
[b7] With this rule, there's a theorem that makes everything work. A sentence is true in the glued
world <bookmark mark="los"/>exactly when it's true in most copies. You check it one symbol
at a time. "And" uses the overlap rule. "Not" uses the either-or rule.

> visual: the scroll of true sentences about the reals; every copy gets a tick next to
> it, then the glued world does. Then "c < 1/5": copies 6, 7, 8, ... tick, copies 1 to 5
> are bracketed "finite, so the rest counts". The glued line appears with the cloud at 0.
> Label: "the hyperreal numbers".
[b8] Every sentence that's true of the reals is true in every copy, so it's true in the
glued world. And "c is less than one over k" fails in <bookmark mark="few"/>only
finitely many copies, so the rest count as most. So c is an infinitesimal. These glued
sequences are called <bookmark mark="hyper"/>the hyperreal numbers.

> visual: the stack of copies is relabelled. Each layer is now a different model, labelled
> by a finite batch of sentences: "{phi1}", "{phi1, phi2}", "{phi2, phi7}", .... Then a
> sentence phi is picked; every layer whose batch contains phi lights up. A few of these
> lit sets overlap, and one layer containing all of their sentences glows in the overlap.
[b9] The general proof is the same. Take a set of sentences where every finite batch has a
model, and line up <bookmark mark="layers"/>one model for each finite batch. Pick the
voting rule so that, for each sentence, <bookmark mark="contain"/>the batches that contain
it count as most. You can, because any few of those sets <bookmark mark="overlap"/>always
overlap: there's a batch with all of their sentences in it. So they grow into a voting
rule.

> visual: phi's lit layers each show a tick next to phi. The ballot box fills, and the
> glued model at the bottom gets a tick next to phi. Then ticks run down the whole set of
> sentences.
[b10] Each sentence holds in every model whose batch contains it, and those count as most.
So by that theorem, it holds in the <bookmark mark="glued"/>glued model. Every sentence,
all at once.

## s07 Compact spaces
> visual: the interval [0,1] as a thick segment with solid endpoints. Several closed
> intervals inside it appear as colored bars. Text: "closed set: includes its edge
> points".
[b1] So why is it called compactness? The word comes from topology, the study of shape,
and it's the same idea. Take a bunch of <bookmark mark="closed"/>closed sets, sets that
include their edge points. The problem is to find one point that's
<bookmark mark="inall"/>in all of them.

> visual: text: "compact: if every finite bunch of closed sets has a common point, then
> all of them do". The words "every finite bunch" and "all of them" glow.
[b2] A space is compact when the hook works. If every
<bookmark mark="finite"/>finite bunch of closed sets has a point in common, then
<bookmark mark="all"/>all of them do.

> visual: bars [0,1], [0,1/2], [0,1/3], ... nested inside [0,1], shrinking toward 0. At
> "zero" the point 0 glows.
[b3] The interval from zero to one is compact. For example, take the closed sets from zero to one over
n. Any finite bunch shares points, and all of them together still
<bookmark mark="zero"/>share zero.

> visual: the full real line with rays [1, oo), [2, oo), [3, oo), ... stacked as bars,
> each starting further right. The hook's column "x > 1, x > 2, ..." appears beside them
> in a corner. At "nothing" the rays slide right and off the screen, and a red cross
> appears.
[b4] The real line isn't. Take everything from one up, from two up, from three up. Any
finite bunch overlaps, but there's <bookmark mark="nothing"/>no point in all of them.
It's the same trouble as the hook.

> visual: back to coloring. A point p with four small switches beside it, one per color;
> one is on. A unit segment to q, with q's switches. At "space" the picture zooms out to
> a huge grid of switches, labelled "every way to set the switches".
[b5] Now, topology can prove things in logic. Back to coloring the plane. Give every point
<bookmark mark="sw"/>four switches, one per color. A coloring attempt is a way to set
every switch. Put all the ways together, and you get <bookmark mark="space"/>a space.

> visual: one rule, "p and q have different colors", highlights only p's and q's switches.
> At "breaks" one setting that breaks the rule is shown, then a blur of other settings
> that agree with it on those switches, all with red crosses. The settings that obey it
> form a shaded region labelled "closed". Footnote: "close = agree on a given finite set
> of switches". Several such regions
> overlap. Text: "Tychonoff: this space is compact".
[b6] Call two settings close when they agree on lots of switches. Each rule only looks at
<bookmark mark="few"/>a few switches. If a setting <bookmark mark="breaks"/>breaks the
rule, so does every setting that agrees with it on those few. That makes the settings
that obey it a closed set. And a theorem of Andrey Tychonoff says this space of settings
is <bookmark mark="tych"/>compact, however many switches there are.

> visual: the shaded regions shrink, each finite bunch with a shared dot. Then all of them
> share one dot, which expands into a fully colored plane.
[b7] If every finite set of points can be colored, every finite bunch of rules has a
setting in common. So by compactness of the space, there's <bookmark mark="one"/>one
setting that obeys every rule. A coloring of the whole plane, and no logic needed.

> visual: a new space: a cloud of points, each labelled by a little true/false list:
> "phi1: T, phi2: F, phi3: T, ...". Title: "complete descriptions". One sentence phi is
> picked, and the points that say "phi: T" are shaded as a closed set.
[b8] It goes the other way too. Make a space whose points are
<bookmark mark="desc"/>complete descriptions of a world. Each one says, for every
sentence, true or false, the way some model would. Each sentence
<bookmark mark="carve"/>carves out a closed set: the descriptions that say it's true.

> visual: two lines side by side, matched with "=" signs: "a set of sentences has a model"
> = "their closed sets share a point"; "every finite batch has a model" = "every finite
> bunch shares a point". Then the theorem box from s03 appears, and at "compact" it turns
> into "this space is compact".
[b9] A set of sentences has a model exactly when their closed sets
<bookmark mark="share"/>share a point. And every closed set in this space is an
overlap of carved ones. So the compactness theorem says exactly this:
the space of descriptions is <bookmark mark="compact"/>compact. Logic proves a fact about a
space, and that space is a basic tool in model theory.

> visual: three cards in a row: "compactness theorem", "Tychonoff's theorem", "overlapping
> sets grow into ultrafilters". Small footnote under the middle card: "for compact
> Hausdorff spaces". Arrows connect each pair in both directions.
> Footnote: "equivalent over ZF, set theory without choice".
[b10] In fact, the voting rules from the proof also prove Tychonoff's theorem. Over the
basic axioms of set theory, the compactness theorem, Tychonoff's theorem for spaces like
these, and the fact that overlapping sets grow into voting rules all
<bookmark mark="equiv"/>prove each other. It's one idea, showing up in three places.

## s08 Ending
> visual: the bounds line from s05, "5 to 7", with 6 highlighted. A faint, unfinished
> graph of points flickers on and off.
[b1] Back to the plane. Five, six or seven colors. If the plane really needs six,
compactness promises <bookmark mark="promise"/>a finite set of points that proves it.
So far, nobody has found one.

## short1 Infinitesimals
> visual: the question appears as large text, then the answer below it.
[b1] How do you solve infinitely many problems at the same time?
<bookmark mark="answer"/>Just solve every finite number of them.

> visual: a column drops in: "c > 0", "c < 1", "c < 1/2", "c < 1/3", ... At "never" a
> real line appears and c slides toward 0 but every position gets a red cross.
[b2] Here's a hard one. c is bigger than zero, but smaller than one, one half, one third,
and so on, forever. <bookmark mark="never"/>No real number does that.

> visual: a bracket grabs a finite batch ending at 1/7; c lands at 1/8 with a tick.
[b3] But any finite batch has a solution. <bookmark mark="batch"/>Just make c small
enough.

> visual: the theorem in a box: "every finite batch has a model => all of them do".
> Label: "the compactness theorem".
[b4] A theorem in logic, the compactness theorem, says that's enough. If every finite
batch of statements can be satisfied, <bookmark mark="all"/>some world satisfies all of
them at once.

> visual: a scroll "every statement true in R" slides in next to the column.
[b5] Even better, throw in <bookmark mark="every"/>every true statement about the real
numbers, as long as it talks about numbers and not sets of them. Every finite batch still
works.

> visual: a new line that looks just like the real line. Zoom into 0: c appears just
> right of it, with a cloud of 2c, c/2, c^2 around it. Label: "infinitesimal".
[b6] So there's a number system that agrees with the real numbers on every one of those
statements, plus one extra: <bookmark mark="c"/>a positive number smaller than every
positive fraction. An infinitesimal.

> visual: text card "Leibniz, 1680s" with "ghosts" in muted text below it, then "logic,
> 1960s".
[b7] Leibniz built calculus out of numbers like this, and one critic called them
<bookmark mark="ghosts"/>ghosts. Logic brings them back.

## short2 Coloring the plane
> visual: a plane; two points one unit apart get different colors.
[b1] Color every point of the plane so that points <bookmark mark="one"/>exactly one apart
never match. How many colors do you need?

> visual: the seven-color hexagon tiling fills the screen.
[b2] Seven is enough, using <bookmark mark="hex"/>hexagons a little less than one across.

> visual: a unit triangle with three colored corners. Then two unit triangles form a
> diamond; bottom red, middle blue and gold, top turns red. A second diamond rotates until its top is one unit from the first top; both tops
> red, the segment between them flashes.
[b3] Three is too few. Three points in a unit triangle already use up three colors. Glue
two triangles into <bookmark mark="diamond"/>this diamond, and with three colors the top
has to match the bottom. Build two diamonds from the same bottom, with
<bookmark mark="tops"/>tops one apart, and the tops would have to match each other. So
you need at least four.

> visual: text: "the plane needs 5 => some finite set of points needs 5". Label: "the
> compactness theorem".
[b4] Five? A theorem in logic says where to look. If the plane needs five colors,
<bookmark mark="finite"/>some finite set of points already does. That's compactness.

> visual: the de Grey graph appears, "1581 points, 2018", then shrinks to "509 points".
[b5] In twenty eighteen, Aubrey de Grey found one, with <bookmark mark="grey"/>fifteen
hundred eighty-one points, so the plane needs five. It's down to <bookmark mark="parts"/>five hundred and nine
now.

> visual: a bounds line with 5, 6, 7 marked and "?" above it.
[b6] So the answer is five, six or seven. Nobody knows which.
