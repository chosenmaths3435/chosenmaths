# Continuous at every irrational, broken at every fraction

## s01 Hook
> visual: the popcorn function plotted on [0, 1] as dots: 1/2 at height 1/2, 1/3 and 2/3
> at height 1/3, and so on, thinning toward the axis. The axis itself glows faintly.
[b1] There's a function that's continuous at every irrational number, and
<bookmark mark="broken"/>broken at every fraction.

> visual: the text "continuous at every fraction, broken at every irrational?", then a red
> cross over it. Title card: "The popcorn function".
[b2] Try to build the opposite. <bookmark mark="cant"/>You can't.

## s02 The definition
> visual: the fraction 3/4 with an arrow to height 1/4. Then 2/6 simplifying to 1/3, with
> an arrow to height 1/3. Then sqrt(2)/2 with an arrow to 0.
[b1] Here's the rule. Take a fraction, p over q, in lowest terms, and send it to
<bookmark mark="q"/>one over q. So three quarters goes to one quarter, and two sixths is
one third, so it goes to one third. Every irrational number goes to
<bookmark mark="zero"/>zero.

> visual: the dots appear row by row: 0 and 1 at height 1, then height 1/2 (one dot), height 1/3 (two dots), 1/4
> (two dots), 1/5 (four dots), and so on, the rows getting denser and lower.
[b2] Plot it, and the fractions <bookmark mark="rows"/>pop up in rows. Zero and one are
zero over one and one over one, so they sit at the top, at height one. Then one dot at one
half. Two at one third. Lower down, the rows fill up, crowding toward the axis.
It looks like popcorn. Carl Thomae wrote it down in eighteen seventy-five.

## s03 What continuous means
> visual: a smooth curve and a point on it. At "band" a horizontal band around the point's
> height. At "window" a vertical window around the point; inside it, the curve stays in
> the band.
[b1] What does continuous mean? Roughly, that nearby inputs give nearby outputs. Here's a
precise version. Pick a point, and draw <bookmark mark="band"/>a band around its value,
however thin. The function is continuous there if you can always find
<bookmark mark="window"/>a window around the point where the graph stays inside the band.

> visual: the band thins; the window shrinks to match, still working.
[b2] Thinner band, smaller window. As long as some window always works, the function is
continuous at that point.

> visual: a step function, 0 to the left of x = 0 and 1 from 0 onward, like a light switch.
> At the jump, a band around the value 1 from 0.5 to 1.5. At "left" every window around 0
> contains points on the left at height 0, lit red, outside the band.
[b3] Here's what broken looks like. This function flips from zero to one at zero, like a
light switch. Put a band around its value there, one, from a half to one and a half. Every
window around zero reaches <bookmark mark="left"/>a little to the left, where the
function is zero, outside the band. No window works, so it's not continuous at zero. Keep
that picture in mind.

## s04 Broken at every fraction
> visual: the popcorn plot zoomed near 1/2. The dot at 1/2 with a band from 1/4 to 3/4.
> At "window" a window around 1/2; at "zero" many points on the axis inside the window light
> up red, outside the band. The window shrinks; red points remain.
[b1] Take one half. Its value is one half. Put a band around it, from a quarter to three
quarters. Now any window around one half, however small,
<bookmark mark="window"/>contains irrational numbers, and those sit at
<bookmark mark="zero"/>zero, outside the band.

[b2] So no window works, and the function is broken at one half. The same goes for every
fraction: it sits above zero, and there are always irrationals right next to it, down at
zero.

## s05 Continuous at every irrational
> visual: the plot zoomed near 1/sqrt(2), about 0.707. Its value is 0. At "band" a thin band
> below 1/10. The dots poking above the band (denominators up to 10) light up.
[b1] Now take an irrational, like one over root two. Its value is zero. Put
<bookmark mark="band"/>a band around zero, say everything below a tenth.

> visual: the dots above the band light up and are counted: "denominators up to 10:
> finitely many". The nearest ones to 0.707 are 7/10 and 5/7, highlighted.
[b2] Which dots poke out of the band? Only fractions with value at least a tenth, so
denominators up to ten. There are only <bookmark mark="few"/>finitely many of those
between zero and one.

> visual: at "dodge" a window around 0.707 shrinks until it fits between the nearest
> lit-up dots (7/10 and 5/7). Inside the window, every dot is below the band.
[b3] One over root two isn't one of them, so the nearest one is some distance away. Make
the window <bookmark mark="dodge"/>smaller than that. Inside it, every fraction has
denominator bigger than ten, so its value is under a tenth. And every irrational is at
zero. The whole window stays in the band.

> visual: the band thins to 1/100; more dots poke out, still finitely many; the window
> shrinks to dodge them.
[b4] A thinner band means more dots poke out. But it's always <bookmark mark="finite"/>finitely
many, so there's always a window that dodges them. The function is continuous at every
irrational.

## s06 The reverse is impossible
> visual: the question "continuous at every fraction, broken at every irrational?"
[b1] So can you flip it? A function continuous at every fraction, and broken at every
irrational?

> visual: the interval from 0 to 1, and a list of the fractions in it: 0, 1, 1/2, 1/3, 2/3,
> 1/4, 3/4, ..., labelled r1, r2, r3, .... A brace: "every fraction from 0 to 1 is on the
> list".
[b2] Suppose you had one. Here's how to catch it. Look between zero and one, and
<bookmark mark="list"/>list every fraction there, one after another. You can do that: go
by denominator, halves, then thirds, then quarters, and so on.

> visual: the current interval. At "skip" it shrinks a little to leave out the next fraction
> on the list, which turns red with a cross. At "pick" a different fraction inside what's
> left lights up. At "tight" a smaller closed interval around it, well inside the old one,
> where the graph stays within a band of the fraction's value.
[b3] Now a countdown. First, shrink the interval a little so it
<bookmark mark="skip"/>leaves out the next fraction on the list. Then
<bookmark mark="pick"/>pick some fraction inside what's left. The function is continuous
there, so there's <bookmark mark="tight"/>a smaller interval around it where the function
barely moves. Make it sit well inside the old one, away from its ends.

> visual: the step repeats, faster: each new interval strictly inside the last, the band of
> allowed wiggle getting thinner (labels "within 1", "within 1/2", "within 1/3", ...), and
> each step crossing out the next fraction on the list.
[b4] Repeat. Each new interval sits strictly inside the last. Each time, the function moves
<bookmark mark="less"/>less inside it: within one, then a half, then a third. And each
time, one more fraction on the list gets left out.

> visual: the intervals close in on a single point, which glows.
[b5] The intervals close in on <bookmark mark="point"/>a point. The real numbers have no
holes, so that point is really there.

> visual: the list with every entry crossed out, and the point labelled "not on the list:
> irrational".
[b6] Which number is it? It's not the first fraction on the list. That one got left out.
It's not the second, or the third, or <bookmark mark="any"/>any of them. So it's
irrational.

> visual: zoom on the point: nested intervals wrapped around it with room on both sides,
> each with its thinning band. Text: "continuous here". A red cross over "broken at every
> irrational".
[b7] And every interval wraps around this point, with room on both sides. Inside them, the
function moves less than a half, less than a third, less than anything you name. So it's
<bookmark mark="cont"/>continuous there, at an irrational. That's the contradiction. No
function is continuous at every fraction and broken at every irrational.

## s07 Ending
> visual: the popcorn plot again, with the irrationals glowing along the axis and the
> fractions as dots.
[b1] This countdown is the heart of something called the Baire category theorem. It says
you can't build the line out of a list of thin pieces, so the irrationals, in a precise
sense, are <bookmark mark="big"/>big.

> visual: the fraction dots spread across the line, then fading like dust.
[b2] Fractions are everywhere on the line, but they're thin. And a set that's everywhere,
yet <bookmark mark="thin"/>this thin, can't be exactly where a function is continuous.

## short1 The popcorn function
> visual: the popcorn plot appearing row by row.
[b1] This function is broken at every fraction, and continuous at every irrational number.
Here's the <bookmark mark="rule"/>rule. A fraction p over q in lowest terms goes to one
over q. Every irrational goes to zero.

> visual: zoom near 1/2: band around 1/2, irrationals at 0 in every window, in red.
[b2] Why broken at fractions? One half sits at one half. But every window around it,
however small, <bookmark mark="zero"/>contains irrationals, down at zero. So it's broken
there.

> visual: zoom near 1/sqrt(2): a band below 1/10, the finitely many dots above it lit up.
[b3] Why continuous at irrationals? Take one over root two, at zero. Ask for every value
nearby to be under a tenth. Only fractions with denominator up to ten
<bookmark mark="poke"/>poke above that, and there are only finitely many.

> visual: the window shrinks to dodge the lit dots; everything inside stays in the band.
[b4] So shrink the window to <bookmark mark="dodge"/>dodge them. Inside, every value is
under a tenth. Ask for a hundredth, and you dodge more dots, but still finitely many.

> visual: the full plot, irrationals glowing along the axis.
[b5] Near any irrational, only fractions with huge denominators survive, and those are
<bookmark mark="tiny"/>tiny. Continuous at every irrational, broken at every fraction.

## short2 No function is continuous only at the fractions
> visual: the question "continuous at every fraction, broken at every irrational?"
[b1] Can a function be continuous at every fraction, but broken at every irrational?
<bookmark mark="no"/>No. Here's the countdown that catches it.

> visual: the interval from 0 to 1, and a list of its fractions r1, r2, r3, ....
[b2] Between zero and one, the fractions can be <bookmark mark="list"/>listed, one after
another. Start with that whole interval.

> visual: the interval shrinks to leave out the next fraction on the list (crossed out);
> a different fraction inside lights up; a smaller interval around it, well inside, where
> the graph barely moves.
[b3] Shrink it a little so it <bookmark mark="skip"/>leaves out the next fraction on the
list. Pick a fraction inside what's left. The function's continuous there, so there's a
smaller interval around it, well inside, where the function barely moves.

> visual: nested intervals repeating, faster, "within 1", "within 1/2", "within 1/3", each
> crossing out one more fraction; they close in on a glowing point.
[b4] Repeat, forever. Each interval sits strictly inside the last, the function moves less
than any amount you name, and one more fraction gets left out each time. The intervals
close in on <bookmark mark="point"/>a point.

> visual: the list fully crossed out; the point labelled "irrational, and continuous here".
[b5] That point missed every fraction on the list, so it's irrational. And every interval
wraps around it, so the function is <bookmark mark="cont"/>continuous there. No function
is broken at every irrational and continuous at every fraction.
