# Equality in disguise

## s01 Hook
> visual: the words "listen" and "silent" side by side, with a "~" between them labelled
> "anagrams". At "sort" the letters of each word slide into alphabetical order, and both
> become "eilnst". The "~" turns into "=".
[b1] Two words are anagrams when they use the same letters, like "listen" and "silent".
Now <bookmark mark="sort"/>sort the letters of each word. Both turn into the same string. So
"is an anagram of" becomes plain old equals.

> visual: title card "Equality in disguise".
[b2] That trick works for every kind of "the same". And computing it fast leads to one of
the strangest running times in computer science.

## s02 What "the same" means
> visual: header "equivalence relation". Three rules appear one at a time, each with a small
> picture: "x ~ x" (a dot with a loop arrow), "x ~ y  =>  y ~ x" (a double arrow), and
> "x ~ y and y ~ z  =>  x ~ z" (three dots with arrows closing a triangle).
[b1] What should a rule for "the same" satisfy? Three things. Everything is the same as
<bookmark mark="refl"/>itself. If x is the same as y, then <bookmark mark="sym"/>y is the
same as x. And if x is the same as y, and y is the same as z, then
<bookmark mark="trans"/>x is the same as z. A rule with all three is called an equivalence
relation.

> visual: examples appear under the rules: "listen ~ silent"; a clock face with 7 and 19
> landing on the same spot; "1/2 ~ 2/4".
[b2] Anagrams are one. Clock times are another: <bookmark mark="clock"/>seven o'clock and
nineteen hundred hours are the same spot on the clock. Fractions too:
<bookmark mark="frac"/>one half and two quarters name the same number.

> visual: a number line with 0, 0.8 and 1.6 marked. Green arcs labelled "within 1" from 0 to
> 0.8 and from 0.8 to 1.6. At "fail" a red arc from 0 to 1.6 with a cross.
[b3] Here's one that fails. Call two numbers close if they're
<bookmark mark="close"/>within one of each other. Zero is close to zero point eight, and
zero point eight is close to one point six. But zero and one point six
<bookmark mark="fail"/>aren't close. The third rule breaks, so "close" isn't a kind of
sameness.

## s03 Equality in disguise
> visual: a set X drawn as dots grouped into colored blobs, and a set Y to the right. At "f"
> an arrow from every dot into Y; all the dots of one blob land on the same point.
[b1] Here's the claim. A rule is an equivalence relation exactly when it's equality in
disguise. That is, there's some other set Y, and a <bookmark mark="f"/>function f into it,
so that x and y are the same exactly when f of x equals f of y.

> visual: the statement: "~ is an equivalence relation  <=>  there is f : X -> Y with
> x ~ y  <=>  f(x) = f(y)". Under it, small: "anagrams: f = sort the letters".
[b2] For anagrams, f sorts the letters. The claim is that every equivalence relation has
some f like that.

> visual: the three rules rewritten with f: "f(x) = f(x)", "f(x) = f(y)  =>  f(y) = f(x)",
> "f(x) = f(y) = f(z)  =>  f(x) = f(z)". A tick appears next to each.
[b3] One direction is quick. Equality itself follows all three rules. So any rule of the
form "f of x equals f of y" <bookmark mark="inherit"/>inherits all three.

> visual: back to the blobs. Each blob shrinks to a single point, and those points form Y.
> Label: "f(x) = the class of x".
[b4] For the other direction, group everything into classes: each class is all the things
that are the same as each other. Then let f of x be <bookmark mark="class"/>the class x
belongs to. Checking that this f really works is where all three rules get used.
Each class gets crushed to a single point, which is why f is often called a projection.

## s04 A better f
> visual: the class map labelled "always works". Then a row of examples with arrows:
> "listen -> eilnst", "19 -> 7" with "remainder mod 12", "2/4 -> 0.5".
[b1] That choice of f always works, but it doesn't tell you much. "The class of x" just
means "everything that's the same as x". Usually there's a much better f. For anagrams,
<bookmark mark="sort"/>sort the letters. For clock times, take the
<bookmark mark="rem"/>remainder after dividing by twelve. For fractions, take
<bookmark mark="num"/>the number they stand for: both are zero point five.

> visual: a plane through the origin in 3D space, and the expression "a + bx" (all
> polynomials of degree at most 1), with "isomorphic" between them. At "dim" both map to the
> number 2. Then more spaces drop in: a line -> 1, all of 3D space -> 3. Label:
> "f = dimension".
[b2] Here's my favorite. Two vector spaces are isomorphic when there's a
<bookmark mark="iso"/>linear map from one to the other that can be undone. A plane through
the origin, and the polynomials a plus b x, look nothing alike, but they're isomorphic. It
turns out two finite-dimensional spaces are isomorphic exactly when they have
<bookmark mark="dim"/>the same dimension. So f is the dimension. The whole question of when
two spaces are "the same" comes down to <bookmark mark="one"/>one number.

## s05 Computing f
> visual: ten dots labelled 0 to 9. Facts appear on the left one at a time: "1 ~ 4",
> "4 ~ 7", "2 ~ 9", and an edge draws between each pair. At "ask" the question "1 ~ 7 ?"
> appears and the path 1-4-7 glows.
[b1] Now flip it around. Say you have a pile of items, and facts keep arriving:
<bookmark mark="facts"/>this one is the same as that one. Pixels in the same region of an
image. Computers on the same network. In between, questions arrive:
<bookmark mark="ask"/>are these two the same? Two items count as the same when a chain of
facts connects them.

> visual: each dot gets a small label above it: its group's representative (1, 4 and 7 are
> labelled "4"; 2 and 9 are labelled "9"; the rest are labelled with themselves). At "eq" the
> question "1 ~ 7 ?" turns into "f(1) = f(7) ?" and then "4 = 4".
[b2] By the theorem, it's enough to compute some f. Here's an easy one. Each group
<bookmark mark="rep"/>picks a representative, and f of x is x's representative. Then "are
these the same?" becomes "do they have <bookmark mark="eq"/>the same representative?"

[b3] The hard part is that groups keep merging, so f keeps changing. How do you store it
so that both merging and looking up are fast?

## s06 Write f down
> visual: a row of ten boxes, indexed 0 to 9, each holding its item's representative. At
> "lookup" one box lights up. At "merge" the groups {1, 4, 7} and {2, 9} merge, and the
> boxes of one group get rewritten one at a time, with a counter.
[b1] First idea: just write f down. Keep a table of every item's representative. Looking
one up takes <bookmark mark="lookup"/>one step. But when two groups merge, every item in one
of them needs a new label. <bookmark mark="merge"/>A single merge can mean rewriting almost
the whole table.

## s07 A forest of pointers
> visual: the items as dots with arrows. Each item points to a parent; each root has a small
> loop arrow and is highlighted as the representative.
[b1] Second idea: instead of storing the representative, store
<bookmark mark="ptr"/>a pointer one step closer to it. Each item points to a parent, and the
representative points to itself. Each group is a tree, so the whole thing is called a
disjoint set forest, or union-find.

> visual: at "find" a highlight walks from a node up to its root. At "union" two finds run,
> then one root's arrow swings over to the other root.
[b2] To compute f of x, <bookmark mark="find"/>follow the pointers up to the root. That's
called find. To merge two groups, find both roots, and <bookmark mark="union"/>point one at
the other. The merge itself is a single pointer, however big the groups are.

> visual: a bad sequence of merges builds a chain of nine nodes. A find from the bottom
> walks all eight steps, with a counter.
[b3] The catch: unlucky merges can build <bookmark mark="chain"/>a long chain. Then a find
from the bottom takes about as many steps as there are items. We've moved the slowness from
merging to finding.

## s08 Union by rank
> visual: two trees, one tall and one short, each root showing a small number (its rank).
> At "short" the short tree's root points to the tall tree's root, and the height stays the
> same. At "tie" two trees of rank 2 merge and the new root's rank becomes 3.
[b1] The fix is to choose which root points to which. Give each root a number called its
rank. For now, it's just the height of its tree. When you merge,
<bookmark mark="short"/>put the shorter tree under the taller one, and the height doesn't
change. Only when two trees of <bookmark mark="tie"/>equal rank merge does the rank go up by
one.

> visual: trees of rank 0, 1, 2, 3 side by side, each built from two copies of the one
> before, with "at least 1, 2, 4, 8 nodes" under them.
[b2] Now the key fact. A tree of rank r has <bookmark mark="nodes"/>at least two to the r
nodes. Why? The only way to reach rank r plus one is to join two trees of rank r. Each has
at least two to the r nodes, so together they have at least <bookmark mark="double"/>two to
the r plus one.

> visual: "n items  ->  height at most log2(n)". Then "n = 1,000,000  ->  at most 20 steps".
[b3] So with n items, no tree is taller than <bookmark mark="log"/>log base two of n. Every
find takes at most that many steps, and a merge is just two finds plus one pointer. For a million items,
<bookmark mark="million"/>that's at most twenty steps.

## s09 Path compression
> visual: a tree of height 5. A find from the deepest node walks up, highlighting each node
> on its path. At "knows" each highlighted node gets a small tag naming the root.
[b1] Twenty steps is good. But look at what a find actually does. It walks up a path, and
when it reaches the top, it <bookmark mark="knows"/>knows the root of every node it passed.
Then it throws that away.

> visual: the same path. At "flat" every node on it swings its pointer straight to the
> root. The tree becomes short and bushy.
[b2] So don't. On the way back, <bookmark mark="flat"/>point every node on the path straight
at the root. That's called path compression. The next find from any of those nodes takes
one step.

> visual: a slider. Left end: the table from before, every item pointing straight at its
> root, labelled "fast finds, slow merges". Right end: a long chain, labelled "fast merges,
> slow finds". The forest sits in the middle; the parts that get searched flatten, and the
> marker drifts left.
[b3] Here's a way to see it. If every item pointed straight at its root, that would be
<bookmark mark="table"/>the table from before: instant lookups, slow merges. Long chains are
<bookmark mark="chainend"/>the opposite. Path compression pulls the forest toward the table,
but lazily. It only flattens the parts you actually look at, and a merge is still one
pointer.

> visual: the trees flatten while the rank numbers on the roots stay put. Text: "rank is at
> least the height".
[b4] One detail. Compression makes trees shorter, but we <bookmark mark="rank"/>leave the
ranks alone. So a rank is no longer the height, just a number that's at least the height.
And a single find can still be slow. What gets faster is the total cost of many operations.

## s10 Alpha of n
> visual: the statement "m operations on n items: time at most proportional to m * alpha(n)". Under
> it: "alpha = inverse Ackermann function".
[b1] So how fast is it, with both tricks? Any sequence of m operations on n items takes time at
most proportional to <bookmark mark="bound"/>m times alpha of n. So averaged over many
operations, each one costs at most a few times alpha of n steps. Alpha is the inverse of the Ackermann function.

> visual: the three Ackermann rules in small type, then the diagonal values appear one by
> one: "A(0, 0) = 1", "A(1, 1) = 3", "A(2, 2) = 7", "A(3, 3) = 61", and
> "A(4, 4) = 2^2^2^65536 - 3".
[b2] We met Ackermann's function in an earlier video. Walk down its diagonal: A of zero and
zero is one, then three, then seven, then <bookmark mark="a33"/>sixty-one. The next one, A of
four and four, is <bookmark mark="a44"/>a tower of twos: two to the two to the two to the
sixty-five thousand five hundred thirty-six, minus three.

> visual: "alpha(n) = the smallest k with A(k, k) >= n". A stretched number line with the
> diagonal values marked: alpha is 0, 1, 2, 3 on tiny stretches, then one enormous stretch
> labelled 4 running off toward the tower.
[b3] Alpha of n asks how far down that diagonal you have to go to
<bookmark mark="reach"/>reach n. Up to sixty-one, it's at most three. After that it's four,
all the way up to that tower, which is far more than the number of atoms in the universe. So
for any input you could ever store, alpha of n is <bookmark mark="four"/>at most four.

> visual: the number line keeps going: 5, 6, ... far off. Text: "alpha(n) -> infinity".
[b4] But it isn't a constant. It does grow without bound, just
<bookmark mark="slow"/>absurdly slowly. At most four for anything real, and still not
constant. That's a strange thing for a running time to be.

## s11 Why it's so fast
> visual: a tree with a rank on every node; along a path going up, the ranks read
> "0 < 1 < 3 < 4", with arrows.
[b1] The proof of the alpha bound is hard. But there's a slightly weaker bound, found by
Hopcroft and Ullman in nineteen seventy-three, whose proof you can follow, and it has the
same flavor. It uses two facts about ranks. First, ranks
<bookmark mark="up"/>go up as you climb any path.

> visual: several disjoint subtrees, each under a node of rank r, each with "at least 2^r
> nodes". Text: "at most n / 2^r nodes ever have rank r".
[b2] Second, high ranks are rare. Each node of rank r had at least two to the r nodes under
it when it got that rank. And no two of them share those nodes: if they did, one would be
below the other, and the one above would have a bigger rank. So at most
<bookmark mark="rare"/>n over two to the r nodes ever have rank r.

> visual: ranks 0 to 20 and beyond on a line, cut into groups: {0, 1}, {2}, {3, 4},
> {5 ... 16}, {17 ... 65536}. Label: "number of groups: about log* n".
[b3] Now sort the ranks into groups, whose ends grow like a tower of twos: zero and one,
then two, then three and four, then five to sixteen, then seventeen to sixty-five thousand
five hundred thirty-six. Ranks never pass log of n, so any realistic n needs at most five
groups. The number of groups is about <bookmark mark="logstar"/>log star of n: how many times
you can take log base two before you get down to one.

> visual: a find path with each step colored: steps that land in a new rank group, or on the
> root, in one color ("billed to the find"); steps that stay inside a group in another
> ("billed to the node").
[b4] Split the steps of each find into two kinds. Some steps <bookmark mark="cross"/>jump
into a new group, or reach the root. There are only a few of those per find: one per group,
plus one. Bill them to the find. The other steps stay inside a group. Bill each of those to
<bookmark mark="node"/>the node it starts from.

> visual: one node of rank 7 (in the group 5 to 16) and its parent. Each time it's billed,
> its pointer moves to a higher-ranked node: the parent's rank ticks 8, 11, 14, 17, and
> leaves the group. A counter: "at most 16 bills".
[b5] Once a node stops being a root, its rank is frozen, and its parent's rank only ever
goes up. When a node gets billed, path compression gives it <bookmark mark="newparent"/>a new
parent, the root, with a higher rank than the old one. So for a node in the group up to
sixteen, after at most sixteen bills, its parent's rank has <bookmark mark="leaves"/>left
the group. From then on, every step from that node crosses into a new group, so it's never
billed again.

> visual: the group 5 to 16: "n/32 + n/64 + ... + n/2^16 < n/16 nodes", then "at most
> 16 bills each: at most n bills".
[b6] And how many nodes are in that group? High ranks are rare: add up n over
thirty-two, n over sixty-four, and so on, and you stay under
<bookmark mark="few"/>n over sixteen. That's n over sixteen nodes, with at most sixteen
bills each: at most <bookmark mark="n"/>n bills for the whole group. The same balance
happens in every group.

> visual: the total: "finds: m * (log* n + 1)" plus "groups: n * log* n". Since n <= m:
> "time proportional to m * log* n".
[b7] Add it up. Each find pays about one step per group, and each group pays at most n in
total. Adding an item counts as an operation, so n is at most m, and the whole thing takes
time proportional to <bookmark mark="total"/>m times log star of n.

## s12 The true answer
> visual: the tower-of-twos group boundaries morph into boundaries labelled with Ackermann
> rows. Text: "Tarjan, 1975: m * alpha(n)".
[b1] Robert Tarjan proved the alpha bound in nineteen seventy-five. The simpler proofs found
since play the same counting game, with <bookmark mark="levels"/>the Ackermann function in
place of the towers of twos.

> visual: "Tarjan: some inputs really take this long", then "Fredman and Saks, 1989: no
> union-find structure can beat it by more than a constant factor". A green tick next to "alpha(n) is the true answer".
[b2] And alpha isn't a weak spot in the proof. Tarjan also showed that, for this algorithm,
some sequences of operations <bookmark mark="slow"/>really do take that long. Then in
nineteen eighty-nine, Fredman and Saks showed that <bookmark mark="any"/>no data structure for this problem
can do better by more than a constant factor, even on an idealized computer that only pays
for reading and writing memory. The inverse Ackermann
function is the true answer.

## s13 Ending
> visual: the projection picture again: blobs collapsing to points. On the left, the forest
> with "f = representative". On the right, the vector spaces with "f = dimension".
[b1] Union-find uses the most boring f there is: pick a representative. All the cleverness
goes into computing it fast. The interesting f's, like dimension, are what math goes looking
for.

> visual: two drawings of the same graph, laid out differently, with "same graph?" and
> "f = ?" between them.
[b2] And sometimes nobody has found one. Two networks are the same graph if you can rename
the points of one to get the other. Is there an f for that, something you can compute
quickly and compare? <bookmark mark="open"/>Nobody knows one that runs in polynomial time, and nobody has
proved there isn't one.

## short1 Equality in disguise
> visual: "listen" and "silent"; at "sort" the letters slide into order and both become
> "eilnst"; "~" turns into "=".
[b1] "Listen" and "silent" are anagrams. <bookmark mark="sort"/>Sort the letters of each,
and they become the same string. "Is an anagram of" turns into plain equals.

> visual: the three rules: "x ~ x", "x ~ y => y ~ x", "x ~ y and y ~ z => x ~ z".
[b2] That works for every kind of "the same". A rule counts as sameness if everything is
the same as itself, sameness goes <bookmark mark="rules"/>both ways, and chains of sameness
hold up.

> visual: blobs in X with arrows into Y. The statement: "x ~ y  <=>  f(x) = f(y)".
[b3] And every rule like that is equality in disguise: there's a function f with x and y the
same exactly when <bookmark mark="f"/>f of x equals f of y. One choice always works: send x
to its whole class of look-alikes.

> visual: "19 -> 7" (remainder mod 12). Then a plane and the polynomials a + bx, both
> mapping to 2, with "f = dimension".
[b4] But usually there's a better one. Clock times are the same when they have
<bookmark mark="rem"/>the same remainder after dividing by twelve. And two finite-dimensional vector
spaces can be matched up by a reversible linear map exactly when they have
<bookmark mark="dim"/>the same dimension.

[b5] Every kind of sameness is equality, once you look at the right thing.

## short2 Why union-find trees stay short
> visual: dots with parent pointers forming trees; roots highlighted. A find walks up; a
> merge points one root at another.
[b1] Here's a data structure whose trees can't get tall, and the reason fits in one line.
Items are split into groups. Each item <bookmark mark="ptr"/>points to a parent, and the root
of each tree represents its group. To check a group, walk up to the root. To merge two
groups, point one root at the other.

> visual: a chain of nine nodes and a find walking all eight steps.
[b2] The danger is <bookmark mark="chain"/>a long chain, where walking up takes forever.

> visual: a short tree joining a tall one; then two equal trees joining and the rank going up.
[b3] So give each root a rank, its tree's height, and always
<bookmark mark="short"/>put the shorter tree under the taller one. The rank only goes up
when two trees of <bookmark mark="tie"/>equal rank merge.

> visual: trees of rank 0, 1, 2, 3 with "at least 1, 2, 4, 8 nodes".
[b4] Now, a tree of rank r has at least <bookmark mark="nodes"/>two to the r nodes, because
the only way to reach rank r plus one is to join two trees of rank r.

> visual: "n items -> height at most log2(n)", "1,000,000 -> 20".
[b5] So with n items, no tree is taller than log base two of n. A million items, and every
walk to the root takes at most <bookmark mark="twenty"/>twenty steps.

## short3 The strangest running time
> visual: a tree; a find walks up a long path, then every node on the path swings its
> pointer straight to the root.
[b1] This data structure has one of the strangest running times in computer science.
Items are grouped into trees, and you find an item's group by walking up to the root. The
trick: after each walk, <bookmark mark="flat"/>point every node you passed straight at the
root.

> visual: "m operations: time proportional to m * alpha(n)", "alpha = inverse Ackermann".
[b2] With one more trick for merging, m operations on n items take time proportional to
<bookmark mark="bound"/>m times alpha of n, the inverse Ackermann function.

> visual: the diagonal: "A(0, 0) = 1", "A(1, 1) = 3", "A(2, 2) = 7", "A(3, 3) = 61",
> "A(4, 4) = 2^2^2^65536 - 3".
[b3] Ackermann's function grows absurdly fast. Along its diagonal, it goes one, three,
seven, sixty-one, and then <bookmark mark="tower"/>a tower of twos with sixty-five thousand
five hundred thirty-six at the top.

> visual: "alpha(n) = the smallest k with A(k, k) >= n" and the stretched number line, with
> the huge stretch labelled 4.
[b4] Alpha of n asks how far down that diagonal you go to reach n. Past sixty-one, it's
<bookmark mark="four"/>four, all the way up to that tower, far more than the atoms in the
universe.

> visual: the number line continuing to 5, 6, ...; then "Fredman and Saks, 1989: optimal".
[b5] So it's at most four for anything real. But it isn't constant: it
<bookmark mark="grows"/>grows forever, just absurdly slowly. And it's not a weak proof. No
data structure for this problem can do better, beyond a constant factor.
