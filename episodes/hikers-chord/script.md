# Same height, half a loop apart

## s01 Hook
> visual: a globe, slowly turning, with the equator drawn as a glowing ring. Temperature
> colors along it, warm to cool. At "two" two opposite points on the equator light up with
> the same reading, "? C" on both.
[b1] Right now, there are <bookmark mark="two"/>two opposite points on the equator with
exactly the same temperature.

> visual: question marks over the globe. Title card: "Same height, half a loop apart".
[b2] I can't tell you where. But they're there, and the reason fits on a hiking trail.

## s02 The loop trail
> visual: a closed loop trail seen from above, with a hiker dot walking around it. Below,
> the height profile: height against distance along the trail, drawn as the hiker walks,
> ending at the same height it started.
[b1] Here's a loop trail. Walk around it, and plot your height as you go. After one lap
you're <bookmark mark="back"/>back where you started, at the same height.

> visual: a second hiker dot on the trail, always exactly opposite the first, half a loop
> ahead. On the profile, a horizontal rod half the profile's width, with its ends on the
> curve. At "level" the rod is level.
[b2] The claim: somewhere on this trail, there are two spots exactly half a loop apart, at
<bookmark mark="level"/>exactly the same height.

## s03 One subtraction
> visual: on the profile, a point at the hiker's position and a point half a loop ahead,
> with a vertical bar between their heights. A counter: "ahead minus here = +50 m".
[b1] Keep track of one number: the height half a loop ahead, minus the height where you
are. Say at the start, the spot ahead is <bookmark mark="plus"/>fifty meters higher.

> visual: the hiker walks half a loop; the two points slide along the profile. At "swap"
> the hiker stands where "ahead" was, and "ahead" is the starting point (the two ends of
> the profile are marked as the same spot on the trail). The counter reads "-50 m".
[b2] Now walk half a loop. You're standing where "ahead" used to be, and half a loop ahead
of you is where you started. The two spots <bookmark mark="swap"/>swapped. So now the
number is minus fifty.

> visual: below, a plot of "ahead minus here" against distance walked: starting at +50,
> ending at -50, crossing the axis. At "zero" the crossing lights up.
[b3] Your height changes smoothly as you walk, with no teleporting, so this number changes
smoothly too. It goes from fifty to minus fifty, so somewhere in between, it
<bookmark mark="zero"/>has to hit zero. That's the intermediate value theorem, and it's
the whole proof.

> visual: at the crossing, the hiker dots freeze on the trail, and the rod on the profile
> snaps level. Text: "same height".
[b4] At that moment, the spot ahead is exactly as high as you are. <bookmark mark="snap"/>Two
spots, half a loop apart, at the same height. If the number started at zero, you were done
before you began.

## s04 The equator
> visual: back to the globe. The equator unrolls into a temperature profile whose two ends
> match, just like the trail.
[b1] Now back to the equator. It's <bookmark mark="loop"/>a loop, opposite points are half
a loop apart, and temperature changes smoothly as you go around. Same number, same flip,
same proof.

> visual: the whole globe colored by temperature, and a second layer of pressure contours.
> Two antipodal points light up with matching temperature and pressure. Label:
> "Borsuk-Ulam".
[b2] There's even a version for the whole globe, with two quantities at once. Somewhere, two opposite
points have the same temperature <bookmark mark="both"/>and the same air pressure. That's
the Borsuk-Ulam theorem, and it needs more than one subtraction.

## s05 Any distance on a loop
> visual: the trail profile drawn over two laps, with a rod one third of a loop long sliding
> along, tilted.
[b1] Is half a loop special? Try a rod <bookmark mark="third"/>a third of a loop long. Or
any length at all.

> visual: the same "ahead minus here" plot, now for the shorter rod, wiggling above and
> below the axis. At "average" a dashed line at 0, labelled "average over a lap = 0".
[b2] Walk a full lap, tracking the height ahead minus the height here. Over a full lap,
the average height ahead is just the average height of the trail. So is the average height
here, because the spot ahead also walks exactly one full lap. So the difference
<bookmark mark="average"/>averages out to zero.

> visual: the plot crosses the axis; the rod snaps level.
[b3] Something that averages to zero can't stay positive the whole way around, or negative.
So it hits zero, and <bookmark mark="snap"/>the rod fits level. On a loop, every distance
works. Half was just the one with the shortest proof.

## s06 A trail that isn't a loop
> visual: a new trail, from one lake to another lake at the same altitude: a profile that
> starts and ends at the same height but doesn't repeat. Labels: "start", "end".
[b1] Now take a trail that <bookmark mark="open"/>isn't a loop. It starts at one lake and
ends at another, at the same height. You don't get to wrap around anymore.

> visual: a rod half the trail long. Two differences shown: from start to middle, and from
> middle to end. They are drawn as arrows and add up to "end minus start = 0".
[b2] Half the trail still works. Put the rod at the start, then at the middle. Its tilt is
the difference in height between its ends: start to middle, then middle to end. Those
two differences <bookmark mark="add"/>add up to the end minus the start, which is zero.
So one is up and one is down, unless one is already zero and the rod is level right
there. Slide the rod from one spot to the other, and somewhere in between, it's level.

> visual: a rod a third of the trail long. Three differences: start to 1/3, 1/3 to 2/3,
> 2/3 to end, adding to zero. Two of them light up with opposite signs; between them the
> rod snaps level.
[b3] A third of the trail? Three differences, start to a third, a third to two thirds, two
thirds to the end. They <bookmark mark="three"/>add up to zero, so unless one is already
zero, two of them point in opposite directions. Slide the rod between those two spots,
and somewhere along the way, it's level.

> visual: "1/2, 1/3, 1/4, 1/5, ..." each with a tick.
[b4] A quarter, a fifth, one over any whole number: <bookmark mark="all"/>the same trick
works every time.

## s07 Two fifths
> visual: a rod two fifths of the trail long, sliding along a new trail. It stays tilted the
> whole way.
[b1] So what about two fifths? Here's a trail where it <bookmark mark="fails"/>fails.

> visual: the curve "height = sin^2(5 pi x / 2) - x" on [0, 1], starting and ending at 0.
> The rod of length 2/5 slides along it; at every position, the right end is exactly 0.4
> lower. A label tracks the drop: "always 0.4 lower". At "crest" the end of the trail
> lights up on top of a wave crest.
[b2] It starts and ends at the same height. It's built from a wave that repeats every two
fifths, tilted downhill. Slide a rod two fifths long along it, and the far end is always
<bookmark mark="lower"/>exactly the same amount lower. It never levels out. And the trail
still ends where it started, because it finishes on <bookmark mark="crest"/>top of a
wave crest, which cancels the downhill drop.

> visual: text "Paul Levy, 1934". A number line of rod lengths with ticks at 1/2, 1/3, 1/4,
> ... in green and everything else in red.
[b3] Paul Levy found this in nineteen thirty-four. And it's not just two fifths. For
<bookmark mark="every"/>every length that isn't one over a whole number, there's a trail
where the rod never fits.

> visual: the loop trail and the open trail side by side. Over the loop: "every length".
> Over the open trail: "only 1/2, 1/3, 1/4, ...".
[b4] On a loop, every length works. Cut the loop open, and almost every length can fail.
All that changed is <bookmark mark="wrap"/>whether you get to wrap around.

## short1 Same height, half a loop apart
> visual: a globe with a glowing equator; two opposite points light up with the same
> temperature.
[b1] Right now, there are two opposite points on the equator with exactly the same
temperature. Here's why, <bookmark mark="trail"/>on a hiking trail.

> visual: a loop trail and its height profile; two hiker dots, always half a loop apart.
[b2] Walk a loop trail. Keep track of one number: the height half a loop ahead, minus the
height where you are. Say it starts at <bookmark mark="plus"/>plus fifty meters.

> visual: the hiker walks half a loop; the two dots swap places; the counter reads -50.
[b3] Walk half a loop. Now you're where "ahead" was, and ahead of you is where you started.
The spots <bookmark mark="swap"/>swapped, so the number is minus fifty.

> visual: the plot of "ahead minus here" going from +50 to -50, crossing zero; the two
> hiker dots freeze at the same height on the profile.
[b4] Your height changes smoothly, so the number does too. Going from fifty to minus fifty,
it <bookmark mark="zero"/>has to hit zero. Right there, two spots half a loop apart are at
the same height.

> visual: back to the globe; the equator lights up as a loop.
[b5] The equator is a loop too, opposite points are half of it apart, and temperature
changes smoothly around it. Same number, same flip. Two opposite points, <bookmark mark="same"/>same temperature.

## short2 Two fifths can fail
> visual: a trail from one lake to another at the same height; a rod half the trail long
> snaps level.
[b1] Hike a trail that starts and ends at the same height. Somewhere, two spots exactly
<bookmark mark="half"/>half the trail apart are at the same height.

> visual: two differences, start to middle and middle to end, adding to zero; one up, one
> down; the rod snaps level.
[b2] Why? Compare the start with the middle, and the middle with the end. Those
differences add up to the end minus the start, which is zero. So <bookmark mark="one"/>one
goes up and one goes down, or one is already zero. Either way, somewhere in between, the
rod is level.

> visual: three differences for a third, then "1/4, 1/5, ..." with ticks.
[b3] The same works for a third of the trail, a quarter, <bookmark mark="any"/>one over any
whole number. The differences always add up to zero.

> visual: the 2/5 counterexample curve with the rod sliding, always tilted, "always 0.4
> lower".
[b4] But two fifths? Here's a trail where it fails. It's a wave that repeats every two
fifths, tilted downhill, so the far end of the rod is <bookmark mark="lower"/>always the
same amount lower.

> visual: a number line of lengths: 1/2, 1/3, 1/4, ... green, the rest red. "Paul Levy,
> 1934".
[b5] In fact, every length that isn't one over a whole number <bookmark mark="fails"/>can
fail. Paul Levy proved it in nineteen thirty-four.
