# Remaking a sequence: the plan

How a sequence of the game is remade from start to finish. Written 2026-11-24 from the two remakes done that way
(the linen room's shaft, `docs/shaft-remake-log.md`, 2026-11-23; the pool's scene, `docs/pool-remake-log.md`,
2026-11-24; **used first for near-catch 1 the same day, `docs/near-catch-1-remake-log.md`, which added three kinds
of correction and three checks to it; then for near-catch 2, `docs/near-catch-2-remake-log.md`, approved on its
first play**), from the user's two prompts and from every correction the user made before each was merged. The user,
2026-11-24: "save this plan. We will start using it right away."

**It is used whenever the user asks for a sequence to be remade or refined as a whole.** Each remake gets its own
log, `docs/<scene>-remake-log.md`, as those two have.

## The plan

**Standing rule: PixelLab is used freely, as needed, at any step** (the user, 2026-11-24: "you're free to use
PixelLab as needed"). No asking before spending generations on a piece, a figure, a clip or a second try. What was
made and what it cost goes into the log and is said at each stop.

1. **Set up.**
   - Start from the latest `main`, on a branch and worktree of its own, with its own port and test folder.
   - Open `docs/<scene>-remake-log.md` with the user's prompt word for word.
2. **Record the scene as it is.**
   - Play it with real keys from every way she can arrive (each side, each pose, from the water, from another
     deck).
   - Go through the frames at the game's pixel size and list every fault, not only the ones named.
   - List what hangs on the scene: its flags, locks, rewards, tests, and what the plan says must be kept.
   - Measure the scene's whole reach against one screen (480 px, 220 of it ahead of her): where it starts, where its
     point is seen (near-catch 2: the door he opened was 460 px past the screen's edge).
   - **For every piece the remake takes out, grep what names it** (near-catch 1: the lunch's pulse was the old
     cabinet's, and went with it unnoticed).
3. **Settle the structure with the user before anything is drawn.**
   - Lay out the constraints: where the route must lead, what cannot move, which way she faces coming in.
   - Ask only the decisions that are the user's (a direction, a room mirrored, a thing dropped), each with a
     picture.
4. **Write the sequence beat by beat**, each beat held to these rules:
   - One continuous space at its true place and length, with no fade or teleport.
   - Her direction of travel is kept from entry to exit.
   - Every effect has a cause she can see, and the cause could do it (a door knocked open swings away from the knock).
   - Going into a thing, she is behind its near side and in front of its far side.
   - Only what really exists is shown, and Bumbot is where the story has him.
   - Whoever is on screen stays visible throughout.
   - What she must find is in view at the moment she needs it.
   - Nothing waits for a key the world can press itself.
5. **Preview stop.**
   - Each new piece is roughed at its size beside her in a real screenshot, then generated with PixelLab (as many
     tries as it takes to read) and checked frame by frame.
   - The user sees one picture per piece and a storyboard strip. Size, colour and readability are settled here.
   - The storyboard is composed over shots of the real room, and put on its clock as a GIF (near-catch 2: the
     clock written for the GIF became the scene's own).
6. **Make the art, generated wherever it can be.**
   - Nothing is drawn in code or put together from other scenes' props to save generations; code drawing stays
     for what is flat by nature and for thin or turning parts, in the picture's tones.
   - Pieces are generated into the game's own picture of the place and cut out by what differs.
   - A thing with states is one picture plus the part that changes.
   - Her clips start from her built sheet's frame, on a green copy of the set.
   - A key beat gets a generated clip of its own, never a stand-in.
7. **Build** it in the data, the config and the scene code, on the game's clock.
8. **Check it against the kinds of correction** (below; twelve now) before the user sees it:
   - Measure feet and things against the floor's strip, pixel by pixel.
   - Check the depth at every beat.
   - Try every wall standing, crawling and jumping.
   - Look at the deck above and below, and at the outside view.
   - Go through a second time, and reload after the scene.
   - Look at the whole screen at the moment the scene takes over: its subject well inside the picture, not at its
     edge (measure the camera's view).
   - Stand where E acts on each thing the scene leaves her: it pulses; and once taken it is gone from its place.
   - Cross every line that starts the scene in a jump as well as on foot.
   - Run the scenarios touched, with a new check for each decision, and the overlap check.
9. **Play stop.** The user gets the link, the strip and a GIF, with a plain note that motion and sound are theirs to
   judge.
10. **Fix rounds.** Each correction becomes a numbered decision with the user's words, a constant or rule instead of
    a one-off nudge, a check in the test, and a look for the rest of its kind. Where a fix is better made by a new
    picture or clip than by a patch, it is generated.
11. **Close on the user's approval.** Update the documents and the lessons (the log's table of generations and their
    job ids among them), commit, take `main` into the branch, merge and push on the user's word, remove the
    worktree.

For scale: the shaft took 92 generations, the pool 60, near-catch 1 31, near-catch 2 15.

## The kinds of correction

Nearly every correction the user made on playing the remakes is one of these. None shows in a still or a test;
all can be looked for before the user plays (step 8). The first nine came of the shaft and the pool, the last three
of near-catch 1.

| Kind | The shaft | The pool |
|---|---|---|
| A fitting too big next to her | the mouth "protruding too much" | the lever "way too big" |
| The floor line as the eye sees it | | the 2 to 5 px shifts, "floating in the air" |
| Depth when she goes into a thing | "inside of it, not behind it" | the hatch's near edge |
| Something shown that is not true | peeks at "nothing", the two yellow dots | |
| A character lost from view | | Bumbot gone in the water |
| A wall tried in one pose only | she fell past the cart standing | |
| A stand-in where the beat needed its own clip | the cover's fall "too plain" | her reach up from the water |
| A pause or a fade in a hand-over | "no delays", no fade going in | no fade into deck 10 |
| Another deck's things leaking in | the dark over the outside view | the laundry line |
| The subject at the screen's edge as the scene takes over | (near-catch 1: "we can barely see Bumbot and what he is actually doing", the scene began 200 px from him) | |
| A thing she can use that does not pulse, or stays where it stood once taken | (near-catch 1: "the tray is a pickable object, it should pulsate"; "when pick up tray, it should stop being on the counter") | |
| Two things at once that the player must tell apart | (near-catch 1: "make her cry, and then dash, with a little pause in between") | |

## What the two prompts had in common

| Part of the prompt | The shaft | The pool | What it did |
|---|---|---|---|
| A whole sequence, start to finish | "the sequence where we enter the opening" | "from start to finish (Bumbot, kid, the lever, the pool drain)" | Every beat was looked at, not only the named faults |
| Autonomy | "do the remake autonomously" | "the same rules as yesterday" | The decisions were the session's to make and log |
| The bar | "placement of things, layering, directions, visuals" | "placement, layering, everything" | Became the checklist |
| One or two things disliked | facing left | the lever, the hatch not found | Showed what "broken" means to the user |
| Generate freely | yes | yes | No stand-ins drawn in code |
| Ask when unsure | "ask me" | "give me context (also, visually)" | The pool got a preview stop; the shaft did not |
| Housekeeping | latest main, a log | latest main, a throwaway worktree | Nothing collided with the other session |

**What a next prompt can add to save rounds:** how she usually arrives (from which side, in which pose: the shaft's
first hour turned on that); what must not change (a route, a reward, a place on another deck); a word that the
preview stop is wanted (it caught the lever before it was built).

## How each went

- **The shaft:** a false start. A turn inside the shaft was proposed and refused, and the idea was dropped for a
  while. It moved once the geography was laid out (why she cannot come out to the right) and the user chose the
  mirrored room. After the build the user played it and sent five corrections that evening and four more the next
  day.
- **The pool:** the scene was recorded as it was first, and eight faults found, six more than the user named. Two
  things were settled on previews before the build (the pistol's colour, the lever's size). After the build,
  thirteen corrections, almost all small (a few pixels, a visibility, a timing); approved the same morning.

The pool went better for three reasons: the record of the old scene, the preview stop, and the shaft's lessons
already applied.

- **Near-catch 1** (the first by this plan): the old scene recorded (eleven faults, an 8.3 s lock among them);
  three structural questions answered by the user in one message; the pieces and a storyboard over the real room
  approved as shown ("Build like it is here, I like it"); then four corrections in three short rounds of play (the
  pause before the dash, the lunch's pulse, the nearer start, the tray off the counter), and "Approved" the same
  afternoon. 31 generations. None of the four was one of the nine kinds: they are the last three rows above.
- **Near-catch 2** (the second): the old scene recorded (nine faults, the chief one structural: its point 460 px
  off the screen); two questions with one picture, answered in two lines (the user's own place for him, not one of
  the three offered); the pieces, a storyboard and its GIF approved ("Go ahead"); built; the self-check found two
  things the storyboard had wrong (the door at the screen's edge, him behind the stand's card); **approved on its
  first play, no correction.** 15 generations.

## The two prompts, word for word

**The shaft (2026-11-23):**

> I want us to redraw the sequence of the game, where we enter the opening in the laundry room after Bumbot's escape.
> Reload everything from the updated main branch.
> I want you to do the remake autonomously, because doing this with me would take much time for me to describe every details.
> I want the entire sequence look good, authentic, make sense in terms of placement of things, layering, directions, visuals, etc.
> Use PixelLab generations as much as needed.
> Analyze the current state of the game, focus on already built parts of the plan-the-rest plan. See what was done and how.
> In the same spirit: generate proper scenes, animations, check yourself.
> What I really dislike about how the sequence starts is that when we enter the opening, we are in 99% cases facing right. The sequence starts with us facing left and the shaft going left.
> If the shaft can be rebuilt going right and us exiting at another place to the right, but still making sense story wise: do it.
> If you unsure about something: ask me. Log everything you decided and done, in a separate document.
> Let's start.

**The pool (2026-11-24):**

> Let's make sure we're on the latest main.
> Then I want you to refine the pool animation from start to finish (Bumbot, kid, the lever, the pool drain).
> Use the same rules as you used yesterday for the linen room refinement.
> I want it make sense visually, in terms of placement, layering, everything. What can be generated with PixelLab—generate it.
> Just for example, the lever looks very poor now. The opening on the pool floor I couldn't find at all.
> If you're unsure about anything—give me context (also, visually if relevant), and ask.
> Make sure we don't interfere with our work of the Implementation branch, so maybe let's work in a separate throwaway worktree
