# There's only one random graph

## s01 Hook
> visual: seven dots in a loose cluster on the left half. A coin flips in the corner. At
> "heads" it lands heads and a line draws between two dots; at "tails" it lands tails and
> a dashed line between two other dots flashes and vanishes. Then pairs fill in quickly,
> one coin flip each.
[b1] I'll flip a coin for every pair of dots. <bookmark mark="heads"/>Heads, I connect
them. <bookmark mark="tails"/>Tails, I don't.

> visual: at "you" a second cluster appears on the right half with its own coin, filling
> in its own lines. The two graphs look clearly different.
[b2] You do the same, <bookmark mark="you"/>with your own coin. Our coins will disagree
about half the time.

> visual: both clusters keep growing, new dots fading in at the edges faster and faster,
> trailing off with "...". At "same" a large "=" appears between them. Title card:
> "The random graph".
[b3] But if we keep going forever, with infinitely many dots, we'll build
<bookmark mark="same"/>the exact same network.

## s02 What "same" means
> visual: left, a pentagon on five dots labelled 0 to 4. Right, a pentagram on five dots.
[b1] First, what does "the same" mean? A network of dots and lines is called a graph.
These two graphs look different.

> visual: at "slide" the dots of the pentagram slide around the circle (dot i moves to
> where the pentagon has dot 2i mod 5) until the picture is a pentagon. Each line of the
> left graph flashes with its partner on the right.
[b2] But <bookmark mark="slide"/>slide the dots on the right around, and every one of its
lines lands on a line of the left picture. They're the same graph, drawn two ways. That's
what "same" means here: the same once you rename the dots.

> visual: two new random graphs on five dots each. At "tri" a triangle in the left one
> lights up; the right one has none, and a small "no triangle" tag appears under it.
[b3] Now flip coins for five dots, twice. You'll usually get two different graphs.
<bookmark mark="tri"/>This one has a triangle. This one doesn't. No renaming fixes that.

> visual: a counter: "10 dots, 45 pairs, 2^45 = about 35 trillion ways". At "rare" two
> random ten-dot graphs side by side with a "!=" between them.
[b4] And more dots make it worse. Ten dots have forty-five pairs, so there are
<bookmark mark="count"/>about thirty-five trillion ways the coins can land. Two random
graphs on ten dots <bookmark mark="rare"/>almost never match.

> visual: a row of dots 0, 1, 2, 3, ... running off the right edge, lines filling in by
> coin flips. Text: "chance they match: 1".
[b5] So it's strange that with infinitely many dots, the chance goes
<bookmark mark="one"/>all the way up to one.

## s03 Every wish is granted
> visual: a big random graph, dots fading in at the edges to suggest it goes on. At
> "green" two dots turn green; at "red" one dot turns red. A thought bubble: "a new dot,
> joined to every green, to no red".
[b1] Here's the property that makes it work. Pick a few dots, and color some of them
<bookmark mark="green"/>green and the rest <bookmark mark="red"/>red. Now make a wish: a
new dot that's connected to every green dot, and to no red dot.

> visual: one other dot is pulled out beside the three colored dots. Three coins flip for
> its three connections: it needs heads, heads, tails. A label: "chance 1/8".
[b2] Take any other dot. Its three connections are three coin flips, so it grants the
wish with chance <bookmark mark="eighth"/>one in eight.

> visual: candidate dots are tested one after another, most getting a red cross. A tally
> in the corner: "chance all fail" = 7/8, (7/8)^2, ..., (7/8)^10, shrinking toward 0. At
> "zero" the tally reads "0", and a candidate gets a tick.
[b3] It'll probably fail. But there are infinitely many other dots, each with its own
coins. The chance the first two both fail is seven eighths squared.
<bookmark mark="shrink"/>The first ten, seven eighths to the tenth. So the chance that
every single one fails is <bookmark mark="zero"/>zero.

> visual: a scrolling list of wishes, each a small pattern of green and red dots, with
> "fails: 0" beside each. At "list" a brace around the scroll: "a list of zeros adds up to
> 0".
[b4] That's one wish. But there's only <bookmark mark="list"/>a list's worth of wishes,
since each one is a few dots chosen from a list. The chance that any of them fails is at
most the chances added up. Each one is zero, and a list of zeros adds up to zero. So with
probability one, every wish is granted.

> visual: a coin landing tails, tails, tails, ..., with "possible, chance 0" under it.
[b5] Probability one isn't quite the same as certain. You could flip tails forever. It's
possible, but its chance is zero, and that's the kind of bad luck we're setting aside.

## s04 Matching your graph to mine
> visual: two random graphs, left labelled "mine", right "yours". Each graph's dots are
> also shown as a numbered list along its outer edge, so "first unmatched dot" is visible.
> Threads will be drawn as curves from a dot on the left to a dot on the right.
[b1] Now let's match my graph to yours, one dot at a time. Each match is a thread from a
dot on my side to a dot on yours. The rule is that threads keep the lines: if two of my
dots are connected, their partners have to be connected too, and if they're not, neither
are the partners.

> visual: at "t1" a thread from my dot 0 to your dot 0.
[b2] I go first. My first dot has no thread yet, and there are no threads to respect, so
any partner works. <bookmark mark="t1"/>Take your first dot.

> visual: at "pick" your next unthreaded dot lights up. It is joined to your threaded dot,
> which turns green. At "carry" the green slides across the thread to my threaded dot. At
> "t2" a dot on my side that is joined to my green dot lights up, and a thread draws to it.
[b3] Your turn. Your first dot without a thread is <bookmark mark="pick"/>this one. It's
connected to the matched dot on your side, so color that dot green.
<bookmark mark="carry"/>Carry the color across the thread. Now I need a new dot connected
to my green dot. That's a wish, and my graph grants it. <bookmark mark="t2"/>Thread.

> visual: my next unthreaded dot lights up. It is joined to one threaded dot (green) and
> not the other (red). The colors carry across both threads. At "t3" your graph's witness
> lights up and a thread draws.
[b4] My turn. My next dot is connected to one matched dot and not the other. So that's
one green, one red. Carry them across, and <bookmark mark="t3"/>your graph grants the
wish.

> visual: a summary card: "pick your first dot without a thread; color the matched dots;
> the other side grants the wish". At "stuck" a tick.
[b5] That's the whole game. Whoever's turn it is picks their first dot without a thread,
colors the matched dots by how it connects to them, and asks the other side for a dot
that connects the same way. That's always a wish, so <bookmark mark="stuck"/>we never
get stuck. And the dot that grants it never already has a thread, since every threaded
dot got a color, and a wish asks for a new dot.

> visual: the game runs fast, threads alternating sides. At "skip" a version where only my
> side picks: one of your dots stays dark while threads pile up around it. Then back to
> taking turns, and that dot gets its thread.
[b6] Why take turns? If only I picked, every one of my dots would get a partner, but
<bookmark mark="skip"/>some of your dots might get skipped forever. Taking turns means
every dot, on both sides, eventually gets its turn.

> visual: threads fill everything. Every line on the left flashes with its partner on the
> right. The "=" from the hook returns between the two graphs.
[b7] Keep going forever. <bookmark mark="all"/>Every dot gets a thread, and every line
matches a line. Our graphs are the same.

> visual: a small inset of the two number lines and threads from the rational numbers
> episode, labelled "same game".
[b8] If you saw our video on the rational numbers, this is the same thread game. There,
what kept us from getting stuck was that there's always another dot between any two, and
beyond either end. Here, it's the wishes.

## s05 The random graph
> visual: one large graph, titled "the random graph (the Rado graph)".
[b1] So any two infinite random graphs are the same, with probability one. There's really
only one, and it gets a name: the random graph, or the Rado graph.

> visual: the summary card from s04, with "random" crossed out and replaced by "grants
> every wish". Text: "dots in a list + every wish granted = the random graph".
[b2] Notice that the matching never used the coins. It only used the wishes. So
<bookmark mark="any"/>any graph whose dots you can list, and that grants every wish, is
this same graph.

> visual: at "flip" every line becomes a gap and every gap a line (the picture
> visibly changes). A wish with green and red swaps colors. Then the dots slide back into
> the original picture.
[b3] It's strange in a few ways. <bookmark mark="flip"/>Flip every connection, so lines
become gaps and gaps become lines. You get the same graph back, because every wish still
gets granted, with green and red swapped.

> visual: a small target graph (a house shape: a square with a roof) in the corner. At
> "build" its dots are found one at a time inside the big graph, each new one lighting up
> with green and red marks on the dots already placed.
[b4] And every finite graph is hiding inside it. Want this one?
<bookmark mark="build"/>Build it one dot at a time. Each new dot has to connect to some
of the dots you've placed, and not the others. That's a wish. The same trick finds every
infinite graph whose dots you can list.

## s06 A recipe with no coins
> visual: the number 13 and below it its binary digits 1101, with positions 3, 2, 1, 0
> written under the digits. At "ones" the positions 0, 2 and 3 light up. Then dots 0 to
> 13 in a row, with lines from 13 to 0, 2 and 3.
[b1] You don't even need coins. Here's a recipe. Number the dots zero, one, two, and so
on. A smaller number k connects to a bigger one when the bigger one, written in binary,
has a one in position k. Thirteen is <bookmark mark="bin"/>one one zero one. Count
positions from the right, starting at zero. There are ones in positions
<bookmark mark="ones"/>zero, two and three. So thirteen connects to zero, two and three,
and not to one.

> visual: the graph on dots 0 to 15 drawn with this rule, in a circle.
[b2] Do that for every pair, and you get <bookmark mark="graph"/>this. It doesn't look
random. But check the wishes. Say we want a dot connected to zero, and not to one, two or
three.

> visual: dots 0 to 3, with 0 green and 1, 2, 3 red. Above them, empty digit slots for
> positions 3, 2, 1, 0. At "fill" the slots fill in: 0001. At "own" the result "= 1"
> points at dot 1, which is red, with a cross. At "lead" a 1 is added in position 4:
> 10001 = 17. At "check" dot 17 appears, with a line to 0 (and to 4), none to 1, 2 or 3.
[b3] Write <bookmark mark="fill"/>a one in every green position, and a zero in every red
one. That's zero zero zero one, which is just <bookmark mark="own"/>one, a dot in the wish
itself. So put another one out front, <bookmark mark="lead"/>to make the new number bigger
than every dot in the wish. That's one zero zero zero one, seventeen.
<bookmark mark="check"/>Seventeen connects to zero, and not to one, two or three. Wish
granted.

> visual: text "every wish, granted on demand". Small credits: "Erdos and Renyi, 1963" and
> "Rado, 1964".
[b4] That works for every wish, so this is the random graph too. Paul Erdos and Alfred
Renyi showed in nineteen sixty-three that the coins give one graph, with probability one.
A year later, Richard Rado wrote down this recipe, which is where the name comes from.

## s07 Ending
> visual: a sentence in symbols, "for all x, y there is z with z ~ x and z ~ y", with a
> key: "~" = "connected". Under it the words "any two dots have a common neighbor".
[b1] Here's why logicians care. Take a statement about graphs, built from "and", "or",
"not", "for every dot" and "there's a dot". Like this one: <bookmark mark="common"/>any
two dots have a common neighbor.

> visual: random graphs labelled "100 dots", "1,000 dots", "1,000,000 dots" (drawn as
> denser and denser clouds), with a bar for "chance it's true" climbing toward 1.
[b2] Flip coins on a hundred dots, then a thousand, then a million. The chance that this
statement is true <bookmark mark="up"/>climbs toward one.

> visual: a second statement, "some dot is connected to every other dot". Its bar falls
> toward 0.
[b3] Try a different one: <bookmark mark="hub"/>some dot is connected to every other dot.
Its chance drops toward zero.

> visual: both bars side by side, one at 1, one at 0. Between them, the random graph
> appears, with a tick next to the first statement and a cross next to the second.
[b4] It turns out every statement like this goes one way or the other. Its chance heads to
one, or it heads to zero, never anything in between. And to find out which,
<bookmark mark="ask"/>you just ask the random graph. If the statement is true there, it's
almost always true in big random graphs. If it's false there, it's almost always false.
This is called the zero-one law.

> visual: the statement, then a short stack of rules under it, "every wish with up to 3
> colored dots is granted", "... up to 4 ...", with a bracket "finitely many wish rules".
> A small "compactness" label linking to the previous episode.
[b5] The reason uses this whole video, plus compactness from our last one. If a statement
is true in the random graph, it has to follow from the wishes. Otherwise, some other
graph would grant every wish and break the statement, but we just saw that graph would be
the random graph. Compactness then says the statement follows from
<bookmark mark="few"/>a few wish rules, like "every wish with up to five colored dots is
granted". And in a big random graph, a rule like that is almost always true.

> visual: one statement on screen; a large finite random graph next to the infinite one,
> with "=" in a soft color and the caption "on any one statement".
[b6] So pick any one statement, and a big enough random network almost always agrees with
the one random graph you'd get by flipping forever.

## short1 There's only one random graph
> visual: two clusters of dots, each with its own coin, lines filling in by coin flips.
[b1] I'll flip a coin for every pair of dots. Heads, I connect them. Tails, I don't. You do
the same with your own coin.

> visual: both keep growing off the edges. An "=" between them, and "(with probability 1)"
> under it.
[b2] With infinitely many dots, we'll build <bookmark mark="same"/>the exact same network,
once you rename the dots.

> visual: in one graph, two dots turn green and one red. A thought bubble: "joined to every
> green, to no red".
[b3] Here's why. Color a few dots <bookmark mark="colors"/>green and red, and wish for a
new dot connected to every green and to no red.

> visual: candidates tested one by one, each with three coin flips, a tally "1/8 each";
> most fail, then one gets a tick.
[b4] Any one dot grants this wish with chance one in eight. But there are infinitely many
dots, so the chance they <bookmark mark="fail"/>all fail is zero. And there's only a
list's worth of wishes, so every wish gets granted.

> visual: the two graphs side by side, threads drawing between them, alternating sides.
> Each new dot colors the matched dots green and red, and the colors carry across.
[b5] Now match my graph to yours, one dot at a time, keeping every line lined up. Each new
dot, on either side, connects to the matched dots in some pattern. The
<bookmark mark="match"/>other graph grants that wish with a new dot. Take turns, and
every dot gets a partner.

> visual: the threads fill in; the two graphs merge into one. Label: "the Rado graph".
[b6] So there aren't many infinite random graphs. <bookmark mark="one"/>There's one. It's
called the Rado graph.

## short2 A random graph with no coins
> visual: the graph on dots 0 to 15 from the binary recipe, drawn in a spiral that trails
> off with "..." to suggest it goes on forever.
[b1] This network is built by a simple rule. With probability one, it's the same network
you'd get by flipping a coin for every pair of dots.

> visual: 13 = 1101 with positions 3, 2, 1, 0 below. Positions 0, 2, 3 light up, and lines
> draw from 13 to those dots.
[b2] The rule: a smaller number k connects to a bigger one when the bigger one, in binary,
has a one in position k. Thirteen is <bookmark mark="bin"/>one one zero one, so it connects to
zero, two and three.

> visual: in a coin-flip graph, two dots green and two red; a thought bubble "joined to
> every green, to no red"; candidates tested until one works.
[b3] A random graph grants every wish. Color a few dots green and red, and
<bookmark mark="wish"/>some other dot connects to every green and to no red. Coin flips
give you that, with probability one.

> visual: back to the recipe. Dot 0 green, 1, 2, 3 red. Digit slots fill: 0001, then a
> leading 1: 10001 = 17. Dot 17 appears with the right lines.
[b4] With the recipe, you can just build the answer. Want zero, but not one, two or three?
<bookmark mark="fill"/>A one in the green position, zeros in the red, and a one out front
to make it bigger than all of them: one zero zero zero one. That's seventeen.

> visual: text "every wish, granted" and then "=" next to a coin-flip graph.
[b5] Every wish is granted on demand. And any two graphs on a list of dots that grant
every wish are the same graph. So this <bookmark mark="same"/>orderly rule built the
random graph.
