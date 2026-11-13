"""The ship's people (GAME_DESIGN.md §6.1.6, docs/population.md §7): each one's PixelLab character
and the clips the game uses. `python tools/fetch_people.py` downloads their frames into
assets/source/people/<name>/ (the standing pose `stand.png`, the figure turned to us `front.png` and away `back.png`, each animation's east frames
`<animation>/<i>.png`); `python tools/build_people.py` packs them into assets/sprites/people.png.

All are PixelLab v3 characters at 64 px, side view (two generations each): that came out at her
height and nearest her look (2026-11-13; a "standard" one was 71 px tall and realistic). Clips are
made with animate_character, east only: a template clip, or skeleton-v3 with one of its moves
(walk, eat, talk, sit_seat...) and poses on top.

name: (character id, {clip: frames per second}, options). A clip is an animation of that name on
the character; "stand" is its standing pose. Options: "flip": the sprite was drawn facing west;
"scale": shrunk by that much (a seated figure that came out as tall as the standing ones).
"""

CAST = {
    # Region 1.
    "officer": ("4d3e6422-a934-40e0-a47d-e841378610ae", {}, {}),
    "rival": ("68ef5f08-d2be-4f41-ad76-5831039110c3", {}, {}),
    "porter": ("3ad54560-70f4-4b3c-8ab0-60b0be9ca97e", {}, {}),
    "waiter": ("3423e6b8-f2d5-423f-86ee-b9c77809194c", {}, {}),
    "tourist": ("5d966249-7a4c-42ab-9ba8-d1384fae259a", {}, {}),
    "robe": ("9d68ff5f-80b7-4187-86a9-7cd9eff01bed", {}, {}),
    "stewardess": ("29866bd3-ce11-4319-8e99-7d6de7ffaef8", {}, {}),
    "receptionist": ("b0851098-7398-456a-a950-c1b5367d4d53", {}, {}),
    "photographer": ("89836c72-c724-4013-a128-46519a7a8976", {}, {}),
    "gentleman": ("4a0085ce-78f1-476c-8863-3f3fc461190f", {}, {}),
    "lady": ("45a8f48c-7fd9-4067-9173-7cb7d82c21d7", {}, {}),
    "cleaner": ("47c5aa91-e4f6-471b-bc77-280aeba5feb8", {}, {}),
    "agent": ("4f239177-54ca-4b07-b1e6-7d9475c8d35b", {}, {}),
    "maitre": ("8336eefc-5d4f-452c-b70d-d3ca545505c8", {}, {}),
    "chef": ("6ca50f05-0ef1-4094-af3c-9ec00846cd36", {}, {}),
    "folder": ("fe49270a-7cd3-4f5d-84ee-3e47316bc16f", {}, {}),
    # Diners, drawn seated on their own dining chairs (they stand in a chair's place at a table).
    "diner_red": ("6dc96ff4-58fc-4a8d-b5c7-1bb111a772fc", {}, {}),
    "diner_suit": ("126b575d-bac9-4369-a721-7aa957e0bb5f", {}, {}),
    "diner_teal": ("f2700aec-2d7f-48b8-8025-4313be63f2ce", {}, {}),
    "diner_linen": ("89dfbeac-8d4c-4a89-a578-8dbc95ba16fc", {}, {}),
    # Region 2.
    "librarian": ("10f3bef9-74d9-47f9-af84-f36ec73cb625", {"shelve": 7, "idle": 4, "shush": 6}, {}),
    "jogger": ("26773aee-c797-4c20-950d-47db78465fda", {"run": 12}, {}),
    "fitter": ("e0de11f2-246a-40cc-b9e6-3f374eb03d66", {"work": 6}, {}),
    "dj": ("d1ef2972-5ac8-41fe-9a95-09bc4c9a7bc3", {"bob": 9}, {}),
    "barmaid": ("a0121f2c-c4ee-4b9f-a230-c20e513d118f", {}, {}),
    "studio": ("c8b8807b-8583-4513-9db2-c3066f6d172e", {}, {}),
    # (Drawn leaning back on a rail of her own, a life ring behind her: for an open deck, where the
    # rail is behind the people. Not placed yet.)
    "railwoman": ("123c4f2e-bcb8-4651-a3b7-0c4910048c62", {}, {}),
    # Seated on his own office chair, at one of the Internet Cafe's terminals. (A first one,
    # 2c479d41-d01d-46ea-90c3-36cb855461c8, came out a grey figure with a monitor in the air.)
    "surfer": ("33bd2921-f3b1-4b59-b2ce-1f8892bd9eee", {}, {"scale": 0.8}),
    "atriumwoman": ("7a2ebdab-d174-463f-8636-6f915cfe60e8", {}, {}),
    "railman": ("0c8faf8c-a4f6-4920-8785-658c177af315", {}, {}),
    "maid": ("4677d8f1-5586-41e1-b13e-53d9bdd49ffc", {"make": 6}, {}),
    "modelguest": ("d15bae3f-7372-455a-82fc-f4ce9bab224e", {}, {}),
    # A couple reading the ports' plaques on deck 7, their backs to us.
    "plaquewoman": ("da2e0888-a560-4557-9f72-ad92e4f5e772", {}, {}),
    "plaqueman": ("e41a23e9-edd4-4784-8de8-33b29d2de61e", {}, {}),
}
