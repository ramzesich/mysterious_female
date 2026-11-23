"""Builds the game's character sprite sheets from the raw PixelLab frames in assets/source/.

For each character: every frame is converted to Resurrect 64 (tools/palettize.py, plus that
character's colour swaps), placed in a fixed-size cell with the feet on the cell's bottom row, and
packed into one sheet (rows of 48 cells), assets/sprites/<name>.png, with assets/sprites/<name>.json naming the frames
and animations. Re-run after replacing any source frame.

    python tools/build_sprites.py
"""

import json
from pathlib import Path

from PIL import Image

from palettize import palettize, paper_greys, hex_rgb, blouse_grey, water_blue

ROOT = Path(__file__).resolve().parent.parent
COLS = 48           # cells in a row of a sheet

# Bumbusik. Sources face east (the game mirrors her for west); the climb faces north.
HER = {
    # (Her blouse's sky blue grey-blue: `blouse_grey`, the user, 2026-11-23.)
    "blouse": True,
    "name": "her",
    "cell": 84,
    # Palette swaps after the nearest-colour match: warmer brown hair highlights, and pink-peach
    # shading on her fair skin instead of a dusky mauve.
    "remap": {"3e3546": "45293f", "966c6c": "f68181"},
    # name -> list of (source file, anchor). "keep" preserves the frame's own vertical motion (a
    # breathing bob, a running bounce) relative to the standing baseline; "feet" puts the frame's
    # lowest pixel on the bottom row, for airborne poses whose source includes the jump's height.
    "frames": {
        # Standing still: her plain side pose. Every so often one of her idles plays once
        # (GAME_DESIGN.md §3); both are skeleton-v3, starting and ending near "stand". A foot
        # stays planted throughout, so each frame's lowest pixel goes on the floor ("keep" lifted
        # the tap a pixel: its last frame reaches one row lower than the rest).
        "stand": [("rotations/east.png", "keep")],
        "idle-tap": [(f"idle-tap-2/{i}.png", "feet") for i in range(8)],
        "idle-look": [(f"idle-look/{i}.png", "feet") for i in range(8)],
        # skeleton-v3 run: moves her standing sprite instead of redrawing it, so her hair keeps its
        # standing length (the first, template run let it grow and puff up).
        "run": [(f"run-steady/{i}.png", "keep") for i in range(8)],
        "rise": [("jump/3.png", "feet")],
        "apex": [("jump/4.png", "feet")],
        "fall": [("jump/5.png", "feet")],
        # skeleton-v3 climb (PixelLab's built-in climb move): hands reach up in turn. The first,
        # text-described climb moved both hands together.
        "climb": [(f"climb-alternating/{i}.png", "keep") for i in range(8)],
        "front": [("rotations/south.png", "keep")],
        # Waving to us from the life ring, overboard (GAME_DESIGN.md §5.6): skeleton-v3's wave
        # move, facing the camera. Frames 1-5 have the hand up; the game loops those.
        "wave": [(f"wave/{i}.png", "feet") for i in range(8)],
        # At the tip of the bow, facing the sea ahead (drawn facing west, so she shows her left side;
        # not mirrored), she spreads her arms back into the wind and holds it, her hair blowing (the
        # bow view, GAME_DESIGN.md §5.3): skeleton-v3 custom poses; frame 0 is her rest pose. A
        # first try facing the camera is kept in arms-wide-front/.
        "arms-wide": [(f"arms-wide-side/{i}.png", "feet") for i in range(6)],
        # Bouncing on cabin 8206's bed for joy, facing us (GAME_DESIGN.md §5.3): in place, from one
        # foot to the other, her arms waving up and down; skeleton-v3 custom poses. (A first try,
        # skeleton-v3's cheer move with the game hopping her side to side, is kept in bed-cheer/.)
        "bed-joy": [(f"bed-bounce/{i}.png", "feet") for i in range(8)],
        # Onto the spa's massage table and lying face down on it (the massage scene, the user, 2026-11-22): PixMiniMax
        # from her standing frame in front of the game's table to her lying on it (the 14b gag's lying, 2 px into the
        # pad), the table taken out (tools/untable.py); its floor is row 92 of the clip's canvas, the table's middle
        # its canvas's. Played backwards she gets up.
        "massage-lie": [(f"massage-lie/clean/{i}.png", 92) for i in range(17)],
        # Swimming in a pool (GAME_DESIGN.md §5.3): a side-on breaststroke, her head above the water,
        # skeleton-v3 custom poses. Each frame keeps its place on the canvas: lining them up by their
        # lowest pixel made her jump as her legs kicked. Frame 7, a tilted odd one, is left out. (A
        # front crawl was made first and is kept in swim-crawl/.)
        "swim": [(f"swim-breaststroke/{i}.png", "keep") for i in range(7)],
        "back": [("rotations/north.png", "keep")],
        # Bending down with her arms out to pick Bumbot up (a near-catch, GAME_DESIGN.md §4). Her
        # back foot stays planted, so each frame's lowest pixel goes on the floor.
        "reach": [(f"reach/{i}.png", "feet") for i in range(5)],
        # Climbing out of a hatch, from behind: hands on the rim at head, shoulder, then waist
        # height, a knee coming up. The game picks the frame by how far she has risen.
        "climb-out": [(f"climb-out/{i}.png", "keep") for i in range(3)],
        # In cabin 8206's shower, seen softened through its frosted door (GAME_DESIGN.md §5.3):
        # facing us, washing her hair, lather on it; skeleton-v3 custom poses.
        "shower": [(f"shower/{i}.png", "feet") for i in range(6)],
        # With a tray in her hands (§6.1.2): her walk with both forearms held out in front, empty (the
        # game puts the tray and its load there); skeleton-v3's walk with her hands posed on top.
        # Standing with it: the frame with her feet together.
        "carry-run": [(f"carry-walk/{i}.png", "feet") for i in range(8)],
        "carry-stand": [("carry-walk/2.png", "feet")],
        # Her hop with a tray or a cone in her hands (the user, 2026-11-23: "the ice cream is just hanging in the air before
        # her during the jump"): her own jump's three poses with her carry-stand's arms (`carry-jump/`, its README).
        "carry-rise": [("carry-jump/raw3/0.png", "feet")],
        "carry-apex": [("carry-jump/raw3/1.png", "feet")],
        "carry-fall": [("carry-jump/raw3/2.png", "feet")],
        # A start: she recoils from what bumped her (skeleton-v3's hit move), before she runs off.
        "hit": [(f"hit/{i}.png", "feet") for i in range(6)],
        # Her falls (the user, 2026-11-16; skeleton-v3 poses): a slip onto her bottom and a trip flat on
        # her belly, each ending dazed; the slip caught backwards, the trip stumbled on from.
        "slipfall": [(f"slipfall/{i}.png", "feet") for i in range(8)],
        "tripfall": [(f"tripfall/{i}.png", "feet") for i in range(8)],
        "slipback": [(f"slipback/{i}.png", "feet") for i in range(6)],
        "stumble": [(f"stumble/{i}.png", "feet") for i in range(6)],
        # Her reactions to a hit with a tangerine on her (docs/plan-three-uses.md §1.6; skeleton-v3
        # poses, 2026-11-16): thrown back a step, rubbing her nose (a door), spluttering (water in her
        # face), arching (water down her back), yelping and patting her sleeve (a flare), ducking (from
        # above); and the apology, a tangerine held out in both hands (the game's own tangerine is put
        # in them: `HAND_OVER` in src/config.js).
        **{c: [(f"{c}/{i}.png", "feet") for i in range(6)] for c in ("reel", "rubnose", "splutter", "arch", "yelp", "duck", "apology")},
        # Dazed where she fell, butterflies circling over her head, drawn with her (the user's rule).
        "dazed-sit": [(f"dazed-sit/{i}.png", "feet") for i in range(6)],
        "dazed-lie": [(f"dazed-lie/{i}.png", "feet") for i in range(6)],
        # Her quirks (§6.1.11). The Four Seasons' ice swan: she shivers, hugging herself.
        "shiver": [(f"shiver/{i}.png", "feet") for i in range(8)],
        # Bliss's dance floor: standing still on it, she dances (skeleton-v3's dance move).
        "dance": [(f"dance/{i}.png", "feet") for i in range(8)],
        # The Photo Studio's flash catches her: a pose to the camera, facing us (skeleton-v3's
        # thumbs-up move).
        "pose": [(f"pose/{i}.png", "feet") for i in range(4)],
        # Reading in the Library's red chair: she sits down and holds her hands up for the book (the
        # game puts it there); skeleton-v3's sit_seat move with her hands posed on top.
        "read": [(f"read/{i}.png", "feet") for i in range(6)],
        # Centre stage, in the theatre: a deep bow to the house (skeleton-v3, custom poses).
        "bow": [(f"bow/{i}.png", "feet") for i in range(8)],
        # On hands and knees (the duct, under a laundry line); pushing a cart, her walk with both
        # hands out; a camera raised to her eye, held (the game draws the camera): skeleton-v3.
        "crawl": [(f"crawl/{i}.png", "feet") for i in range(8)],
        # (The push remade 2026-11-18, the user: "her legs do not move properly": PixMiniMax from her
        # push frame against the steward's trolley, the trolley taken out, two even steps whose planted
        # foot slides back about 3.6 px a frame (`push2/`, its README); her first, `push/`, kept.)
        "push": [(f"push2/{i}.png", 83) for i in range(8)],
        "camera": [(f"camera/{i}.png", "feet") for i in range(8)],
        # Region 6 (skeleton-v3, custom poses): clinging to a wall in the grip socks, sliding down
        # it; slipping on wet tiles; licking a cone held to her mouth (the game draws the cone);
        # both hands up with the canister (the game draws it; the later frames grew a ghost of one,
        # so only the first is used); sitting down and eating, at the table with her husband
        # (sit_seat with a hand to her mouth: PixelLab drew a chair under her, taken out by
        # tools/unchair.py; frame 2 kept a piece of its seat and is left out).
        "wallslide": [(f"wallslide/{i}.png", "feet") for i in range(4)],
        "slip": [(f"slip/{i}.png", "feet") for i in range(4)],
        # Holding on to the funnel stairway's rail in a gust, facing up the flight and facing down it
        # (assets/source/her/stair-cling/README.md); her stair point at row 79 of a 96 px canvas.
        "cling-up": [(f"stair-cling/up/{i}.png", 79) for i in range(9)],
        "cling-down": [(f"stair-cling/down/{i}.png", 79) for i in range(9)],
        "lick": [(f"lick/{i}.png", "feet") for i in range(4)],
        "pour": [("pour/0.png", "feet")],
        # Region 9. At the Spinnaker's piano: both hands tapping in front of her, skeleton-v3 custom
        # poses. (A first clip, asked to "play piano keys", came with a piano drawn into every
        # frame: kept in piano/.) At the captain's door: a knock, her back to us (north).
        "keys": [(f"keys/{i}.png", "feet") for i in range(8)],
        "knock": [(f"knock/{i}.png", "feet") for i in range(8)],
        # The intro's end and her crew cabin (the user, 2026-11-14; skeleton-v3, custom poses): come
        # out of her door, she straightens her name badge with both hands, facing us (south); at
        # her cabin's mirror she runs a hand over her hair.
        "badge": [(f"badge/{i}.png", "feet") for i in range(8)],
        "hair": [(f"hair/{i}.png", "feet") for i in range(8)],
        # At her husband's table (the user, 2026-11-23; `sit-cone/`, its README): she sits down in the patio chair with
        # the cone she carried (the game's own `load-cone` in her fist, `bake.py`), licks it, and gets up after the book.
        "sit-cone": [(f"sit-cone/cone/sit3/{i}.png", "feet") for i in range(10)],
        "lick-cone": [(f"sit-cone/cone/sit3/{i}.png", "feet") for i in range(9, 15)],
        "sat": [("sit-cone/faced/9.png", "feet")],
        # Her arms up round his neck as they kiss at his table, her back to us (the user, 2026-11-23): her back view
        # (`rotations/north.png`) moved into the embrace by skeleton-v3 (`embrace/`, its README).
        "embrace": [(f"embrace/clean/{i}.png", "feet") for i in range(3)],
        "sit-up": [(f"sit-cone/faced/{i}.png", "feet") for i in range(9, -1, -1)],
        # Region 8 (skeleton-v3, custom poses): both hands up to the horn's cord and down with her
        # weight; a two-handed shot at the court's hoop; under the open parasol she hangs from its
        # handle by both hands (the pull's first frames: a "hover" clip kept her hands down).
        "pull": [(f"pull/{i}.png", "feet") for i in range(8)],
        "throw": [(f"throw/{i}.png", "feet") for i in range(8)],
        "glide": [(f"pull/{i}.png", "feet") for i in (0, 1)],
        # The throw (docs/plan-three-uses.md §1.2; skeleton-v3, custom poses, 2026-11-15): an
        # underarm toss, the arm back low, a step, the swing forward past the hip, the follow-through;
        # the tangerine put in her fist by tools/hold_tangerine.py.
        "toss": [(f"toss-held/{i}.png", "feet") for i in range(8)],
        # Her throw in the air (the user, 2026-11-20): skeleton-v3 from her jump's top (`apex`), only her near arm
        # swung, back, down, forward at her chest and back; the tangerine in her fist in frames 0 to 2
        # (tools/hold_tangerine.py; the tries kept in `air-throw/tries/`, its README).
        "airtoss": [(f"air-throw/held/{i}.png", "feet") for i in range(8)],
        # Her walk (the user, 2026-11-20: out of her door at the intro's end, "walk, not run"):
        # skeleton-v3's walking-8-frames with a shorter stride and less arm swing (0.85, 0.6), the
        # calmer of two tries (walk-a: the template's own, its head dipping once a cycle). Its
        # planted foot rolls back about 4.4 px a frame; a foot comes down on frames 3 and 7.
        "walk": [(f"walk-b-calm/{i}.png", "feet") for i in range(8)],
    },
    # The standing baseline: this frame's lowest pixel row is where the feet are in "keep" frames
    # of the same canvas size. Frames on another canvas use their own animation's lowest row.
    "baseline": "idle/0.png",
}


# Bumbusik after her shower in cabin 8206 (GAME_DESIGN.md §5.3): a towel wrapped round her head
# like a turban, until she leaves the cabin. Only what she does there: PixelLab's "Towel turban"
# state of her character, its profile's face mended by hand to match hers (rotations/east.png;
# PixelLab's is east-raw.png). The run and the jump are the same skeleton-v3 templates as hers; the
# idles and the bed bounce are skeleton-v3 with her own clips' poses, read off their frames.
HER_TOWEL = {
    # (Her blouse's sky blue grey-blue: `blouse_grey`, the user, 2026-11-23.)
    "blouse": True,
    "name": "her-towel",
    "cell": 84,
    "remap": HER["remap"],
    "frames": {
        "stand": [("rotations/east.png", "keep")],
        "idle-tap": [(f"idle-tap/{i}.png", "feet") for i in range(8)],
        "idle-look": [(f"idle-look/{i}.png", "feet") for i in range(8)],
        "run": [(f"run/{i}.png", "keep") for i in range(8)],
        "rise": [("jump/3.png", "feet")],
        "apex": [("jump/4.png", "feet")],
        "fall": [("jump/5.png", "feet")],
        # (PixelLab's front still has the turban touching its canvas's top, its outline over the towel cut off: the
        # user saw it as she stepped out of the shower, 2026-11-23. `south-topped.png` is it a row taller, that row
        # of outline put back in the outline's own colour; stood by its lowest row, as `keep` stood the other.)
        "front": [("rotations/south-topped.png", "feet")],
        "bed-joy": [(f"bed-bounce/{i}.png", "feet") for i in range(8)],
        "back": [("rotations/north.png", "keep")],
    },
    "baseline": "idle-tap/0.png",
    # (The turban's light blues grey, in every frame: `grey_top`.)
    "grey_top": 18,
}


# Bumbusik with Bumbot in her arms (GAME_DESIGN.md §6.1.9: the way home): PixelLab's "Holding the
# cat" state of her character, 6905f308-15b1-4a44-ad97-a38a7ad17dff. Her walk is skeleton-v3's
# "walking" with the arms held still; standing, she bends her head to him now and then (a v3
# clip: its first frames; in the last three the cat is gone). In the air: two strides of the walk
# (a skeleton-v3 jump, kept in jump/, drew him as a dark blob).
HER_CAT = {
    # (Her blouse's sky blue grey-blue: `blouse_grey`, the user, 2026-11-23.)
    "blouse": True,
    "name": "her-cat",
    "cell": 84,
    "remap": HER["remap"],
    "frames": {
        "stand": [("rotations/east.png", "keep")],
        "run": [(f"walk/{i}.png", "feet") for i in range(6)],
        "stroke": [(f"stroke/{i}.png", "feet") for i in range(1, 6)],
        "rise": [("walk/1.png", "feet")],
        "apex": [("walk/1.png", "feet")],
        "fall": [("walk/4.png", "feet")],
        "front": [("rotations/south.png", "keep")],
        "back": [("rotations/north.png", "keep")],
    },
    "baseline": "rotations/east.png",
}


# Her mishap gags (docs/plan-three-uses.md §1.6), each one picture of her with the thing: states of
# her character with the thing drawn in, animated v3 (assets/source/her-mishaps/README.md). A sheet
# of their own so that hers stays within a texture's size; a bigger cell, the thing beside her.
# Each clip is placed by its thing (`props`: the clip's name's start -> the thing's own picture in
# assets/source/things/, cut from the same art): the thing's middle on the cell's middle in the
# clip's first frame, the rest of the clip as drawn round it, so that from sitting down to the
# ride the thing does not jump. Frame 0 of a v3 clip is its start frame (for a sit-down, our
# composition of her standing and the thing: left out).
HER_MISHAPS = {
    # (Her blouse's sky blue grey-blue: `blouse_grey`, the user, 2026-11-23.)
    "blouse": True,
    "name": "her-mishaps",
    "cell": 112,
    "remap": HER["remap"],
    "frames": {
        "vacuum-sit": [(f"vacuum-sit/{i}.png", "feet") for i in range(1, 7)],
        "vacuum-ride": [(f"vacuum-ride/{i}.png", "feet") for i in range(1, 9)],
        "suitcase-sit": [(f"suitcase-sit/{i}.png", "feet") for i in range(1, 7)],
        "suitcase-ride": [(f"suitcase-ride/{i}.png", "feet") for i in range(1, 9)],
        "suitcase-tip": [(f"suitcase-tip/{i}.png", "feet") for i in range(0, 9)],
        # Then she sits there dazed, butterflies circling over her head (the user, 2026-11-17): v3 of
        # the riding state from the tip's last frame with them set over her head (`start.png`, from
        # her own dazed clip), to the same; her eyes open throughout (a try had her blink). Its
        # canvas and edges are the tip's last frame's, so it is placed as the tip is (`shift_as`).
        "suitcase-dazed": [(f"suitcase-dazed/{i}.png", "feet") for i in range(1, 9)],
        # The papers (the user's brief, 2026-11-16; picked 2026-11-17), each from her standing on the
        # sliding newspaper (`paper-start/start2-*.png`), its first frame (her still standing) left out
        # so that the push carries straight into the fall. 4b, from behind: her heel taken forward and
        # up, she sits, the paper round over her onto her head. In the air on her start's floor (row
        # 83, her feet; the paper's lower edge a px under it, as in the start picture); sitting, by
        # each frame's lowest row.
        "paper-behind": [(f"paper-behind-sit/frame_{i:03d}.png", 83 if i < 7 else "feet") for i in range(2, 11)],
        # 4a, from the front: her leg up behind her, onto her belly, the paper round onto her back.
        # Standing and in the air on row 87; lying on her elbows, row 85 (the last frame's paper
        # hanging past them cut at the floor).
        "paper-front": [(f"paper-front-belly/frame_{i:03d}.png", 87 if i < 7 else ("cut", 85)) for i in range(2, 11)],
        # The porter's cart (8a to 8d, approved 2026-11-17): v3 of her base character from her own
        # standing sprite beside the game's own cart (`cart-start/`), on its floor (row 115 of the
        # 136 px frames, 117 of the 140 px ones). 8a: she runs into its front and folds over the bags,
        # her first three (standing) frames left out so the run carries into the leap; then her legs
        # kicking, looped. 8c: it reaches her back and she sits into the bags, the top one on her lap
        # (the game's cart pasted back under her in frames 1 to 5, the generator's flying bag taken
        # out: `cart-start/fix8c.py`). 8b and 8d are her alone (the world's cart and porter stay):
        # pushed back and sat down; bounced off his back and sat down; sitting, by each frame's lowest row.
        "cart-drape": [(f"cart-drape/{i}.png", 115) for i in range(3, 9)],
        "cart-kick": [(f"cart-drape/{i}.png", 115) for i in range(5, 9)],
        "cart-sit": [(f"cart-sit/{i}.png", 115) for i in range(1, 9)],
        "cart-push": [(f"cart-push/{i}.png", 117 if i < 8 else "feet") for i in range(1, 9)],
        "cart-bounce": [(f"cart-bounce/{i}.png", 117 if i < 6 else "feet") for i in range(3, 9)],
        # The breakfast stewardess's tray (10a, 10b; 2026-11-17), her alone (the world's stewardess
        # and tray stay): v3 of her base character from her own standing sprite (`cart-start/
        # start-solo.png`). 10a: she runs into the tray, reels and sits, the toast landing on her head
        # and the flower behind her ear (toward `tray-start/end-10a.png`, her sitting with them, an
        # edit of 8d's end); from its third frame (a rose already flying), so that her run carries
        # into the reel; on row 117 of its 140 px frames, sitting by the lowest row. 10b, the tray
        # meeting her back, is the same clip, she turned round to face it (`turn`, the user, 2026-11-17).
        "tray-sit": [(f"tray-sit/{i}.png", 117 if i < 7 else "feet") for i in range(2, 9)],
        # Her trolley (10c to 10e, 2026-11-17): she trips over it head first and lands on her belly
        # past it; v3 of her base character from her own standing sprite before the game's own
        # trolley (`trolley-start/`), the trolley then taken out of the frames (`fix10c.py`: the
        # world's own is drawn over her while it plays); its first (standing) frame left out, on
        # row 118 of its 140 px frames. Its middle, column 96, is 20 px past the trolley's (`at`).
        "trolley-trip": [(f"trolley-trip/{i}.png", 118) for i in range(1, 9)],
        # The dog's lick after a trip on its lead (2026-11-17): her lying dazed with the dog at her
        # face, one picture (PixMiniMax from her dazed-lie frame 1 and the dog's standing picture
        # turned to her: `dog-lick/raw/start.png`); her body as in that frame, so on its row 74
        # (her hand under her chin) as her own clip has it, and drawn 2 px lower as she is (LIE_DROP).
        "dog-lick": [(f"dog-lick/{i}.png", 74) for i in range(8)],
    },
    "props": {"vacuum-": "robot-vacuum", "suitcase-": "suitcase-rolling"},
    # Moved sideways as another clip is, which it carries on from.
    "shift_as": {"suitcase-dazed": "suitcase-tip"},
    # A gag with no thing to place it by: her middle in its frames (her own sprite's, in the start
    # picture) on the cell's middle.
    # The cart's: its middle (8a, 8c), or 18 px behind hers (8b, 8d: her middle is column 86, room
    # kept for her falling back).
    "middle": {"paper-behind": 36, "paper-front": 28, "cart-drape": 70, "cart-kick": 70, "cart-sit": 52,
               "cart-push": 68, "cart-bounce": 68,
               "tray-sit": 108, "trolley-trip": 96,
               # (Her middle is column 48, as in her dazed clip; the dog reaches to 105: the cell's
               # middle 16 px in front of hers, `GAGS` none: the dog's own `LICK` in movers.js.)
               "dog-lick": 64},
    # Clips with white paper in them: its greys put on the palette as paper (`paper_greys`).
    "paper": ("paper-",),
    "baseline": "ride-vacuum/east.png",
}


def prop_middle(img, colours):
    """The x of the middle of a thing in a frame, found by its own colours (within a few steps of
    them: the frames are redrawn), in the lower half of what is drawn."""
    img = img.convert("RGBA")
    bb = img.getbbox()
    xs = []
    for y in range((bb[1] + bb[3]) // 2, bb[3]):
        for x in range(bb[0], bb[2]):
            p = img.getpixel((x, y))
            if p[3] and any(abs(p[0] - c[0]) + abs(p[1] - c[1]) + abs(p[2] - c[2]) < 24 for c in colours):
                xs.append(x)
    xs.sort()
    return xs[len(xs) // 2] if xs else img.width // 2


def seq(char, folder, anchor="keep"):
    """Every frame in assets/source/<char>/<folder>/, in order."""
    n = len(list((ROOT / "assets" / "source" / char / folder).glob("*.png")))
    return [(f"{folder}/{i}.png", anchor) for i in range(n)]


# Bumbot. Sources face east. His rotations are our own 2/3 shrink of PixelLab's 48px design
# (GAME_DESIGN.md §4); the animations are PixelLab's, made from that shrunk sprite.
BUMBOT = {
    "name": "bumbot",
    "cell": 64,
    "remap": {},
    "frames": {
        "stand": [("rotations/east.png", "keep")],
        "run": seq("bumbot", "run"),
        "wash": seq("bumbot", "wash", "feet"),
        "jump": seq("bumbot", "jump"),
        "sit": seq("bumbot", "sit", "feet"),
        "eat": seq("bumbot", "eat", "feet"),
        "bat": seq("bumbot", "bat", "feet"),
        # Out of the pool (near-catch 5): he shakes himself dry, water flying off him (v3).
        "shake": seq("bumbot", "shake", "feet"),
        # Asleep: the last frame of a v3 "lies down and curls up". The pro "curled up" state drew a
        # featureless ball as tall as he stands, so it is kept in assets/source but not used.
        "asleep": [("curl-up/8.png", "feet")],
    },
    "baseline": "rotations/east.png",
}


def lowest_row(img):
    return img.getbbox()[3] - 1


def paste(dst, src, x, y):
    """alpha_composite that clips a source larger than (or hanging off) the destination."""
    left, top = max(0, -x), max(0, -y)
    right, bottom = min(src.width, dst.width - x), min(src.height, dst.height - y)
    if right > left and bottom > top:
        dst.alpha_composite(src.crop((left, top, right, bottom)), (x + left, y + top))



def grey_top(im, rows):
    """The light blues of the figure's top `rows` (her towel turban) turned to neutral grey of the same lightness: the
    palette's sky blue in its shading read as "water?" (the user, 2026-11-23: "remove the added blue pixels from all the
    with turban on frames"). Dark blues (her eyes) stay."""
    im = im.copy()
    bb = im.getbbox()
    if not bb:
        return im
    for y in range(bb[1], min(bb[3], bb[1] + rows)):
        for x in range(bb[0], bb[2]):
            r, g, b, a = im.getpixel((x, y))
            if a and b - r > 25 and b >= g and (r + g + b) / 3 > 130:
                v = round(0.3 * r + 0.59 * g + 0.11 * b)
                im.putpixel((x, y), (v, v, v, a))
    return im

# Her clips with water on her (the user, 2026-11-23: "when she's wet, a lot of water pixels were turned to grey"): the
# water's own blue kept (`water_blue`), told from the blouse's pale blue by its tint.
WET = {"swim", "shower", "shiver", "splutter"}


def build(spec):
    src_dir = ROOT / "assets" / "source" / spec["name"]
    cell = spec["cell"]
    remap = {hex_rgb(a): hex_rgb(b) for a, b in spec["remap"].items()}
    baseline = {}  # per source canvas size, the y of the standing feet

    def standing_feet(size):
        if size not in baseline:
            ref = Image.open(src_dir / spec["baseline"]).convert("RGBA")
            baseline[size] = lowest_row(ref) if ref.size == size else None
        return baseline[size]

    cells, meta = [], {"cell": cell, "frames": {}, "anims": {}}
    shifts = {}
    for anim, sources in spec["frames"].items():
        indices = []
        paper = anim.startswith(spec.get("paper", ())) if spec.get("paper") else False
        images = [(palettize(paper_greys(Image.open(src_dir / path)) if paper else Image.open(src_dir / path), remap), anchor)
                  for path, anchor in sources]
        if spec.get("grey_top"):
            images = [(grey_top(img, spec["grey_top"]), anchor) for img, anchor in images]
        if spec.get("blouse"):
            images = [(blouse_grey(img), anchor) for img, anchor in images]
            if anim in WET:
                images = [(water_blue(Image.open(src_dir / path), img), anchor) for (img, anchor), (path, _) in zip(images, sources)]
        anim_feet = max(lowest_row(img) for img, _ in images)
        # Placed by its thing (HER_MISHAPS): the clip moved sideways by its first frame's thing.
        shift = 0
        for start, thing in spec.get("props", {}).items():
            if anim.startswith(start):
                pic = Image.open(ROOT / "assets" / "source" / "things" / f"{thing}.png").convert("RGBA")
                colours = {c[1][:3] for c in pic.getcolors(4096) if c[1][3] and sum(c[1][:3]) > 60}
                first = Image.open(src_dir / sources[0][0])
                shift = first.width // 2 - prop_middle(first, colours)
        if anim in spec.get("shift_as", {}):
            shift = shifts[spec["shift_as"][anim]]
        if anim in spec.get("middle", {}):
            shift = Image.open(src_dir / sources[0][0]).width // 2 - spec["middle"][anim]
        shifts[anim] = shift
        for img, anchor in images:
            if anchor == "keep":
                feet = standing_feet(img.size)
                if feet is None:
                    feet = anim_feet
            elif isinstance(anchor, int):
                feet = anchor                       # the row of the frame on the floor
            elif isinstance(anchor, tuple):
                feet = anchor[1]                    # ("cut", row): on the floor, whatever is under it cut
                img = img.copy()
                img.paste((0, 0, 0, 0), (0, feet + 1, img.width, img.height))
            else:
                feet = lowest_row(img)
            frame = Image.new("RGBA", (cell, cell), (0, 0, 0, 0))
            paste(frame, img, (cell - img.width) // 2 + shift, cell - 1 - feet)
            indices.append(len(cells))
            cells.append(frame)
        meta["anims"][anim] = indices
        meta["frames"][anim] = indices[0]

    # In rows of COLS cells, numbered row by row as Phaser's spritesheets are: one strip of her 208
    # frames was 17,472 px wide, over the 16,384 a WebGL texture may be, and she drew as a black box.
    rows = (len(cells) + COLS - 1) // COLS
    sheet = Image.new("RGBA", (cell * min(len(cells), COLS), cell * rows), (0, 0, 0, 0))
    meta["cols"] = COLS
    for i, frame in enumerate(cells):
        sheet.alpha_composite(frame, ((i % COLS) * cell, (i // COLS) * cell))
    out = ROOT / "assets" / "sprites"
    out.mkdir(parents=True, exist_ok=True)
    sheet.save(out / f"{spec['name']}.png")
    (out / f"{spec['name']}.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    print(f"wrote assets/sprites/{spec['name']}.png  ({len(cells)} frames of {cell}x{cell})")


if __name__ == "__main__":
    build(HER)
    build(HER_TOWEL)
    build(HER_CAT)
    build(HER_MISHAPS)
    build(BUMBOT)
