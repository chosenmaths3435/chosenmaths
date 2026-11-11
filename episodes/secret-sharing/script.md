# Split a secret so any three can open it

## s01 Hook
> visual: a vault door with a dial. Five manager icons in a row below it. At "three" three
> of them light up and the vault swings open. At "two" the vault closes; two light up and
> a "?" appears over them.
[b1] A vault code, split among five managers. <bookmark mark="three"/>Any three of them can
open it. <bookmark mark="two"/>But any two together know nothing at all. Not a little.
Nothing.

> visual: guesses float over the two managers, "first digit?", "even?", each crossed out.
> A stranger icon appears beside them with the same "?".
[b2] Not the first digit, not whether it's even. Two managers working together are no
better off than a stranger guessing.

> visual: two points, then a line through them. Title card: "Secret sharing".
[b3] And the trick is something you learned in school. <bookmark mark="line"/>Two points
make a line.

## s02 When everyone is needed
> visual: a dial with the digits 0 to 9. A lock icon with the secret digit 7 inside.
[b1] Start with an easier version: two people, and both are needed. Say the secret is a
single digit, <bookmark mark="seven"/>seven.

> visual: at "nine" a random digit 9 goes to person A. At "eight" person B gets 8. At
> "dial" the dial turns 9 steps, then 8 more, wrapping past 0, and lands on 7.
[b2] Give the first person a random digit, say <bookmark mark="nine"/>nine. The second
person gets <bookmark mark="eight"/>eight, because nine plus eight is seventeen, and we
only keep the last digit. It's like <bookmark mark="dial"/>turning a dial: nine clicks,
then eight more, and you land on seven.

> visual: B alone with an 8. Ten dials, one for each possible secret 0 to 9, each with the
> first digit that would make it work (0 -> 2, 1 -> 3, ..., 7 -> 9, ...). Each gets the
> label "1/10".
[b3] Together, they turn the dial and get seven. But the second person alone, holding an
eight? Every secret is possible. <bookmark mark="any"/>For each one, there's a first digit
that makes it work. And the first digit was random, so every secret fits equally well.
The eight tells them nothing.

> visual: four people; three get random digits, the last gets the digit that fixes the
> sum. A longer secret "7 3 0 5" handled one digit at a time.
[b4] It works for any number of people. Give everyone but the last a random digit, and
the last gets whatever fixes the sum. For a longer secret, do it one digit at a time.

> visual: the five managers. At "groups" the ten groups of three appear as small brackets,
> each with its own split. Each manager collects a stack of six pieces.
[b5] Now, any three of five. You could do a separate split for
<bookmark mark="groups"/>every group of three. There are ten groups, and each manager
ends up holding six pieces.

> visual: "any 51 of 100" with a counter running up to "about 10^29 splits".
[b6] That gets out of hand fast. For any fifty-one out of a hundred people, you'd need
about <bookmark mark="big"/>ten to the twenty-nine separate splits. We need a better idea.

## s03 Two points make a line
> visual: axes. At "secret" a point on the vertical axis at height 5, labelled "secret".
> At "random" a line through it with a random slope.
[b1] Let's start with any two managers out of five. Put the secret on the vertical axis.
It's <bookmark mark="secret"/>the height where a line crosses it. Then draw
<bookmark mark="random"/>a random line through that point.

> visual: at "points" five dots on the line at x = 1 to 5, each handed to one manager.
[b2] Each manager gets one point on the line: <bookmark mark="points"/>the first at one,
the second at two, and so on up to five.

> visual: the line disappears. Two managers' points remain. At "draw" a line is drawn
> through them, and its crossing with the axis lights up: the secret.
[b3] Any two managers put their points together, <bookmark mark="draw"/>draw the one line
through them, and read off where it crosses the axis. That's the secret.

> visual: only one manager's point remains. At "fan" a fan of lines through it, each
> hitting the axis at a different height, sweeping through the whole axis.
[b4] Now give one manager their point alone. How many lines go through it? There's
<bookmark mark="fan"/>one for every possible secret. Pick any height on the axis, and
exactly one line joins it to this point. Their point fits every secret.

[b5] So one point seems to tell you nothing. We'll come back to that. Two points tell you
everything.

## s04 Three points make a parabola
> visual: at "para" a random parabola through the secret on the axis, with five dots at x
> = 1 to 5.
[b1] For any three of five, use a curve that needs three points: a parabola. Pick
<bookmark mark="para"/>a random parabola that crosses the axis at the secret, and hand
out its heights at one through five.

> visual: three managers' points remain; at "fit" the parabola through them is redrawn and
> its crossing lights up.
[b2] Any three managers have three points, and three points pin down exactly one
parabola. <bookmark mark="fit"/>Draw it, and read off the secret.

> visual: two managers' points remain. At "fan" a fan of parabolas through them, one per
> height on the axis.
[b3] Two managers? Pick any height on the axis. That's a third point, and it pins down
exactly one parabola. So there's <bookmark mark="fan"/>a parabola for every possible
secret. Their two points fit every secret.

> visual: a table: "2 people: line", "3: parabola", "4: cubic", "k: degree k - 1". At
> "one" a hundred managers, each holding a single number.
[b4] It keeps going. Need four people? Use a cubic, which takes four points. For any k
people, use a polynomial of degree k minus one. A hundred managers, any fifty-one of them:
one polynomial, and each person holds <bookmark mark="one"/>one number.

## s05 The catch
> visual: the fan of lines through one manager's point at x = 1, height 50. At "ten" the
> fan narrows to the slopes between -10 and 10, and the axis lights up only from 40 to 60.
[b1] Now, I said one point tells you nothing. With ordinary numbers, that's not quite
true. "Pick a random line" means pick a random slope, and there's no way to pick from all
the real numbers so that every one is equally likely.

[b2] Say the slope is picked between <bookmark mark="ten"/>minus ten and ten. A manager at
one, holding a height of fifty, now knows the secret is between forty and sixty. That's a
leak.

> visual: the dial from before, now with 11 positions, 0 to 10.
[b3] The fix is the dial. Do all the arithmetic like the dial from before, keeping only
what's left after wrapping around, but with a prime number of positions. Say
<bookmark mark="eleven"/>eleven.

> visual: an 11 by 11 grid of dots. At "wrap" the line "height = 4x + 3" is drawn as dots,
> climbing by 4 each step and wrapping back to the bottom when it passes 10.
[b4] Now the plane is an eleven by eleven grid of dots. A line is still height equals
slope times x, plus the secret. But it <bookmark mark="wrap"/>wraps around when it goes off
the top.

> visual: one manager's dot at x = 1. At "each" eleven lines through it, one per slope,
> each landing on a different dot of the axis column. Each axis dot gets "1/11".
[b5] And now there are only eleven slopes, so we can pick one with every slope exactly
equally likely. Through one manager's point, there are eleven lines, and
<bookmark mark="each"/>each one hits the axis at a different secret. Every secret fits
with exactly one slope, and every slope is equally likely. Now one point really does tell
you nothing.

> visual: two points on the grid at x = 1 and x = 3, and the line through them. At
> "divide" the step "slope = (difference in height) / 2" lights up. Below: "on a 10-dial:
> 2 x 5 = 0".
[b6] Why a prime? Two points still have to pin down one line, and finding the slope means
dividing. With a prime number of positions, <bookmark mark="divide"/>you can always divide
by anything but zero. On a ten-position dial, you can't. Doubling zero and doubling five
both give zero, so there's no undoing a doubling.

> visual: on a ten-position dial, the manager at x = 2 holds "secret + 2 x slope". At
> "even" every value of 2 x slope lights up as even (0, 2, 4, 6, 8), and the secret's
> evenness matches the height's. A callback to the hook's crossed-out "even?".
[b7] And it leaks. A manager at two holds the secret plus two times the slope, and on a
ten-position dial, two times anything is <bookmark mark="even"/>even. So they learn
whether the secret is even. That's exactly what we promised couldn't happen.

> visual: a huge prime written out, dozens of digits long, over the grid.
[b8] In practice, the prime is often <bookmark mark="huge"/>enormous, dozens of digits long, and
the secret is a number below it. But the picture is the same.

## s06 What goes wrong
> visual: the point at x = 0 lights up, labelled "seat 0 = the secret". A manager icon
> walks up to it.
[b1] There are a couple of ways to get this wrong. First, nobody sits at
<bookmark mark="zero"/>zero. The point at zero is the secret itself. That sounds obvious,
but if you number the managers from zero, the first one walks off with the vault code.

> visual: a fan of only two lines through the point (1, 9), with slopes 1 and 2, hitting
> the axis at 8 and 7. At "two" those two axis points light up.
[b2] Second, the line has to be <bookmark mark="random"/>truly random. Say your slope only
ever comes out as one or two. A manager at one with a height of nine knows the secret is
<bookmark mark="two"/>eight or seven. That's not nothing.

> visual: the even fan of eleven lines from before, then the lopsided two-line fan.
[b3] The reason one point told you nothing was that every slope was equally likely. Take
that away, and the fan isn't even anymore.

## s07 Ending
> visual: text "Adi Shamir, 1979". Small: "the S in RSA".
[b1] This is Shamir's secret sharing, from Adi Shamir in nineteen seventy-nine. He's also the S
in RSA.

> visual: the parabola with all five managers' points. At "liar" one point jumps off the
> curve and turns red.
[b2] Here's one more thing polynomials can do. Say all five managers show up, but
<bookmark mark="liar"/>one of them lies about their point. Three points pin down the
parabola, so there are two extra. Can you find the liar, and still open the vault?

> visual: the four honest points glow on the true parabola. A few other parabolas are tried
> through the liar's point, each passing through at most three of the five. At "qr" a QR
> code with a smudge in one corner scans with a tick.
[b3] You can. The four honest points all sit on one parabola, and no other parabola gets
through more than three of the five. Extra points on a polynomial are also how
<bookmark mark="qr"/>a QR code still scans with a smudge on it.

> visual: seven manager icons and a parabola. A "?" next to "liars".
[b4] So here's a question for you. With seven managers and a parabola, how many of them
can lie, and you still find the true code?

## short1 Two points make a line
> visual: a vault with a dial, five manager icons below. Then two points and a line.
[b1] Split a secret among five people, so that any two can open it, but one alone learns
nothing. All you need is this: <bookmark mark="line"/>two points make a line.

> visual: axes, the secret as a point on the vertical axis, a random line through it, and
> five dots on the line at x = 1 to 5.
[b2] Put the secret on the vertical axis. Draw <bookmark mark="random"/>a random line
through it. Give each person one point on the line, at one, two, three, four and five.

> visual: two points remain; the line is redrawn through them and its crossing lights up.
[b3] Any two people <bookmark mark="draw"/>draw the line through their points, and read
off where it crosses the axis. That's the secret.

> visual: one point remains. A fan of lines through it, sweeping the whole axis.
[b4] One person alone? Through their point, there's <bookmark mark="fan"/>a line for every
possible secret. Pick any height on the axis, and exactly one line joins it to their
point.

> visual: the 11 by 11 grid of dots, eleven wrapping lines through one point, each axis
> dot labelled "1/11".
[b5] But fitting isn't enough. Every secret also has to fit equally well, and you can't
pick a slope fairly from all the real numbers. So do the math on a clock that wraps around
at a prime, like eleven. Now there are only eleven slopes, you can
<bookmark mark="equal"/>pick one fairly, and every secret fits exactly one of them.

> visual: back to the vault. A parabola appears with three points. Text: "Shamir's secret
> sharing".
[b6] Need three people instead of two? <bookmark mark="para"/>Use a parabola. That's
Shamir's secret sharing.

## short2 Why two people learn nothing
> visual: a vault with a dial, five managers. Three light up and it opens; two light up and
> a "?" appears.
[b1] Five managers, one vault code. <bookmark mark="three"/>Any three can open it.
<bookmark mark="two"/>Any two together learn nothing. Not a little. Nothing.

> visual: a parabola crossing the vertical axis at the code, with five points at x = 1 to
> 5 handed to the managers.
[b2] Hide the code where a random parabola <bookmark mark="para"/>crosses the vertical
axis. Each manager gets one point on it.

> visual: three points remain; the parabola is redrawn through them and its crossing
> lights up.
[b3] Three points pin down one parabola. So any three managers
<bookmark mark="fit"/>draw it, and read off the code.

> visual: two points remain. A height on the axis lights up, and the one parabola through
> all three draws in. Then the height slides, and the parabola follows, sweeping out a
> fan.
[b4] Two managers have two points. Pick any possible code on the axis. That's a third
point, and there's <bookmark mark="one"/>exactly one parabola through all three. So every
code fits their two points, each with its own parabola.

> visual: the grid of dots with wrapping parabolas, each axis dot labelled with an equal
> chance.
[b5] One catch: you can't pick fairly from all the real numbers. So do the math on a clock
that wraps around at a prime, like eleven. Then there are only so many parabolas, you can
<bookmark mark="equal"/>pick one fairly, and every code fits exactly as well as every
other, even for two managers working together. They know nothing.
