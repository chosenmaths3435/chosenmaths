# Integration by parts is enough

## s01 Hook
> visual: dark screen. The power rule integral of x^n dx = x^(n+1)/(n+1) appears, then a
> few other memorized integrals (sin, e^x, 1/x) around it. At "cross" all of them are
> struck through and fade.
[b1] Forget the power rule. <bookmark mark="cross"/>Forget every integral you ever memorized.

> visual: a single formula remains in the center: integral of p q' dx = pq - integral of q p' dx.
[b2] You get to keep one big thing, <bookmark mark="ibp"/>integration by parts, plus
two small facts we'll get to.

> visual: the integration by parts formula shrinks to the top. Below it, large:
> integral of x^5 dx = ?
[b3] With only that, can you still work out <bookmark mark="q"/>the integral of x to the fifth?

[b4] You can. And integration by parts does almost all of the work.

## s02 The rules
> visual: a box labelled I in the center. A polynomial (3x^2 + 1) slides in from the
> left; a different polynomial slides out the right with a question mark on it.
[b1] Picture a machine. You feed it a polynomial, and it hands back another polynomial.
Call it I.

[b2] We want I to be the integral, but we're not allowed to say so. Instead, it has to
follow three rules.

> visual: a "Rules" panel on the right. Rule 1 appears: I(p + q) = I(p) + I(q),
> I(c p) = c I(p).
[b3] Rule one. <bookmark mark="r1"/>I is linear. Feed it a sum, and you get the sum of
the outputs. Scale the input, and the output scales the same way.

> visual: Rule 2 appears: I(1) = x. The box takes in 1 and outputs x.
[b4] Rule two. <bookmark mark="r2"/>I of one is x. That's the only answer we get for
free.

> visual: the usual formula: integral of p q' dx = pq - integral of q p' dx. The two primes
> are highlighted.
[b5] Rule three is integration by parts. You've probably seen it like this.
<bookmark mark="ibp"/>The integral of p times the derivative of q equals p times q,
minus the integral of q times the derivative of p.

> visual: the box runs backwards: x goes in the output side and 1 comes out the input
> side. Label: I^{-1}.
[b6] But our machine doesn't know about derivatives. All it can do is run itself
backwards. It never turns two different inputs into the same output, so backwards
always makes sense. <bookmark mark="inv"/>Call that I inverse. If I turns one into x,
then I inverse turns x back into one.

> visual: in the usual formula, each primed term morphs into an I^{-1} term, and each
> integral sign into I. Result, boxed as Rule 3:
> I(p I^{-1}(q)) = pq - I(q I^{-1}(p)). Small note under it: "p, q: outputs of I".
[b7] Swap each derivative for I inverse, and each integral for I, and rule three becomes
this. <bookmark mark="rule"/>I of p times I inverse of q equals p q, minus I of q times
I inverse of p. It's integration by parts, with every integral starting at zero.

> visual: a small table appears at the bottom left with one filled row: 1 -> x.
[b8] One catch. We only know I inverse of something after we've seen the machine
produce it. So every new answer has to be built from the ones before it.

## s03 The first step
> visual: Rule 3 at the top. Below, the question I(x) = ?
[b1] Let's start small. What is I of x?

> visual: in Rule 3, p and q are both replaced by x (colored PRIMARY).
[b2] Use rule three, with p equal to x and q equal to x.

> visual: I^{-1}(x) on the left side is highlighted, then replaced by 1, pointing back
> at the table row 1 -> x.
[b3] On the left, we need I inverse of x. Rule two says I turns one into x, so
<bookmark mark="one"/>I inverse of x is one. The left side is just I of x.

> visual: on the right, pq becomes x^2, and I(x I^{-1}(x)) becomes I(x). The line now
> reads I(x) = x^2 - I(x).
[b4] On the right, x times x is x squared. <bookmark mark="rhs"/>Then we subtract I of
x times one, which is I of x.

> visual: both copies of I(x) glow.
[b5] So I of x equals x squared, minus I of x. The thing we're looking for shows up on
both sides.

> visual: the right-hand I(x) slides across the equals sign, giving 2 I(x) = x^2, then
> I(x) = x^2/2. New table row: x -> x^2/2.
[b6] So move it over. <bookmark mark="move"/>Two I of x equals x squared, and I of x is
x squared over two.

[b7] The rule never told us the answer directly. It gave us an equation, and the
answer was the only thing that could solve it.

## s04 Climbing
> visual: Rule 3 again, now with p = x^2 and q = x substituted:
> I(x^2 I^{-1}(x)) = x^3 - I(x I^{-1}(x^2)).
[b1] Now we can climb one step higher. Take p equal to x squared and q equal to x.

> visual: I^{-1}(x) on the left is replaced by 1, pointing at the table row 1 -> x.
[b2] On the left, I inverse of x is one again, so the left side is I of x squared.

> visual: highlight I^{-1}(x^2). Point at the table row x -> x^2/2; scale it by 2 to
> show 2x -> x^2. Replace I^{-1}(x^2) with 2x.
[b3] On the right, we need I inverse of x squared. We just found that I turns x into x
squared over two. Double both, and I turns two x into x squared. <bookmark mark="inv2"/>So I
inverse of x squared is two x.

> visual: x times 2x collapses to 2x^2, and linearity pulls the 2 out:
> I(x^2) = x^3 - 2 I(x^2).
[b4] Then x times two x is two x squared. <bookmark mark="sub"/>The equation becomes: I of
x squared equals x cubed, minus two I of x squared.

> visual: same move as before: 3 I(x^2) = x^3, then I(x^2) = x^3/3. New table row.
[b5] Same trick. Three I of x squared equals x cubed, so I of x squared is x cubed over
three.

> visual: the table grows row by row, each new row drawing an arrow from the row above:
> 1 -> x, x -> x^2/2, x^2 -> x^3/3, x^3 -> x^4/4.
[b6] Each row of the table <bookmark mark="table"/>unlocks the next one.

> visual: the general step. Start from the row x^(n-1) -> x^n/n, so
> I^{-1}(x^n) = n x^(n-1). Rule 3 with p = x^n, q = x gives
> I(x^n) = x^(n+1) - I(x * n x^(n-1)) = x^(n+1) - n I(x^n), then
> (n+1) I(x^n) = x^(n+1), then I(x^n) = x^(n+1)/(n+1).
[b7] In general, <bookmark mark="general"/>the row before tells us I inverse of x to
the n is n times x to the n minus one. Rule three then puts I of x to the n on both
sides, with an n in front on the right. Move it over, and we divide by n plus one.

> visual: the table jumps to the row x^5 -> x^6/6, and the hook's question
> "integral of x^5 dx = ?" is filled in.
[b8] Climb five rows, and we have our answer. <bookmark mark="answer"/>I of x to the
fifth is x to the sixth, over six.

[b9] That's the power rule, rebuilt from linearity, integration by parts, and one free
answer.

## s05 The picture
> visual: I(x^2) = x^3 - 2 I(x^2) at the top of the screen. Below: axes in t and y.
> The curve y = t^2 from 0 to a point a. A dashed rectangle from the origin to
> (a, a^2); its width labelled "q = t, so a" and its height "p = t^2, so a^2".
[b1] There's a picture hiding in this equation. Let's peek at what I really is: the
area under a curve, starting from zero. Draw y equals t squared, from zero out to a.
<bookmark mark="rect"/>Then draw the rectangle around it, a wide and a squared tall.
Its area is a cubed.

> visual: the region under the curve fills with PRIMARY; then the region between the
> curve and the y-axis fills with SECONDARY.
[b2] The curve cuts the rectangle in two. <bookmark mark="under"/>The area under the
curve, and <bookmark mark="left"/>the area to its left.

> visual: the two regions slide apart slightly and back together, with
> "under + left = a^3" written beside them.
[b3] Integration by parts says the two pieces add up to the whole rectangle. That's
the p times q in the formula.

> visual: a thin horizontal strip in the left region, width t and height 2t dt. Label
> the left region "integral of t * 2t dt = 2A" and the under region "A". Then the
> rectangle shows as three equal bars, with the under region matching one: A = a^3/3.
[b4] Now measure the left piece sideways, in thin horizontal strips. A strip at height
t squared is t wide and two t d t thick. Add them up, and the left piece is twice the
bottom piece. That's the two in our equation. So the rectangle splits into three
equal shares, and the area under the curve gets one of them.

> visual: the curve morphs to y = t (a triangle: the two pieces are equal, labels A and
> A, under = 1/2).
[b5] Change the power, and the split changes. <bookmark mark="k1"/>For a straight line,
the two pieces are equal, and the area under is half the rectangle.

> visual: the curve morphs to y = t^3 (labels A and 3A, under = 1/4), then y = t^4
> (A and 4A, under = 1/5).
[b6] <bookmark mark="k3"/>For t cubed, the left piece is three times the bottom one,
and the area under is a quarter.

> visual: general label: y = t^k, pieces A and kA, under = 1/(k+1) of the rectangle.
> The 1/(k+1) is highlighted, and the power rule formula appears with its 1/(n+1)
> highlighted the same way.
[b7] For t to the k, the strips are k times t to the k minus one thick, so the left
piece is k times the bottom one. The rectangle splits into k plus one shares, and the
area under the curve gets one. That's where the
k plus one in the power rule comes from.

## s06 Why the other rules
> visual: the three rules panel again.
[b1] We used three rules. Do we really need all of them?

> visual: a second box labelled 2I. Rule 3 with I replaced by 2I and I^{-1} by
> (1/2) I^{-1}; the 2 and the 1/2 cancel on each side, and the rule holds. A check mark.
[b2] Try doubling the machine. Running two I backwards halves things, so its inverse
is one half of I inverse. <bookmark mark="double"/>Plug that in, and the two and the
one half cancel on both sides. Two I passes the integration by parts test too.

> visual: a row of boxes 2I, 10I, 100I, all with check marks. Then Rule 2 lights up.
[b3] So integration by parts can't tell the integral apart from twice the integral, or
a hundred times it. Rule two, I of one is x, is the one that pins it down.

> visual: the plus C. Rule 2 shown as I(1) = x, with a faded alternative I(1) = x + 5
> crossed out. Then the table outputs x, x^2/2, x^3/3 with their (absent) constant
> terms highlighted as 0. Then the rectangle picture from s05, with its corner at the
> origin highlighted.
[b4] Rule two quietly picks the plus C, too. <bookmark mark="noc"/>It says x, not x
plus five. That's why none of our answers have a constant term, and why the
rectangle starts at the origin.

> visual: back to the s04 step where I(2x) = x^2 was found by doubling, with the
> doubling highlighted. Then 4x^3 - x + 7 splits into its terms, each goes through the
> box, and the outputs recombine.
[b5] And linearity was working the whole time. It let us double rows of the table,
and pull numbers out in front. It also builds any polynomial out of powers of x. Know
I on every power, and you know it on everything.

## s07 Ending
> visual: the three rules, and the full power rule beneath them.
[b1] So linearity, one rule about products, and one free answer pin down the integral
of every polynomial.

> visual: the product rule (pq)' = p'q + pq' appears. Below it:
> "linear + ____ + ____ => derivative", with the blanks pulsing.
[b2] Here's one for you. Integration by parts comes from the product rule.
<bookmark mark="challenge"/>So what's the derivative's version of this? Which rules
force a machine to be the derivative, at least on polynomials?

[b3] Try it. The argument is even shorter than this one.

## short1 Self-solving
> visual: the question "integral from 0 to a of x dx = ?" with a note: "allowed:
> derivatives and integration by parts. No integral formulas."
[b1] Here's an integral that solves itself.

[b2] Say you know derivatives and integration by parts, but you've forgotten every
integral formula. What's the integral of x, from zero to a?

> visual: integral of p q' dx = pq - integral of q p' dx, all from 0 to a. Then p = x, q = x
> substituted: integral of x dx = a^2 - integral of x dx (from 0 to a).
[b3] Use integration by parts, with both pieces equal to x. It says <bookmark mark="eq"/>the
integral of x equals a squared, minus the integral of x.

> visual: both copies glow; one slides across: 2 times the integral = a^2, then a^2/2.
[b4] The unknown is on both sides. Move it over. Twice the integral is a squared, so
the integral is a squared over two.

> visual: same with p = x^2, q = x: integral of x^2 dx = a^3 - integral of x times 2x
> dx = a^3 - 2 times the integral of x^2 dx, then a^3/3.
[b5] Do it again with x squared and x. The derivative of x squared is two x, so the
integral of x squared comes out as a cubed, minus twice itself. That makes it a cubed
over three.

> visual: a column of results stacking up: a^2/2, a^3/3, a^4/4, ..., then the general
> power rule.
[b6] Every answer unlocks the next one. Keep going, and integration by parts rebuilds
the entire power rule.

## short2 Rectangle
> visual: the integration by parts formula, then the curve y = t^2 from 0 to a with its
> rectangle (area a^3).
[b1] Integration by parts has a picture, and it's a rectangle. Draw y equals t
squared from zero to a, and the rectangle around it, with area a cubed.

> visual: under region in PRIMARY, left region in SECONDARY.
[b2] The curve splits the rectangle in two. <bookmark mark="split"/>The area under the
curve, and the area to its left. Integration by parts says the two add up to the whole
rectangle.

> visual: a thin horizontal strip in the left region, width t and height 2t dt. The
> left region labelled "integral of t * 2t dt = 2A".
[b3] Measure the left piece sideways, in thin strips. Each strip is t wide and two t
d t thick, which makes the left piece twice the bottom piece.

> visual: the rectangle as three equal bars, the under region matching one. a^3/3.
[b4] So the rectangle is three equal shares, and the area under the curve is one of
them. A cubed over three.

> visual: the curve morphs through t^3, t^4, with labels kA and the fraction 1/(k+1).
[b5] Swap in t to the k, and the same strips make the left piece k times the bottom.
Now there are k plus one shares.

[b6] That's the one over k plus one in the power rule. It counts the shares.
