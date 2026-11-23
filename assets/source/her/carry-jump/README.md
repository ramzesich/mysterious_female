# Her hop with a load in her hands (the user, 2026-11-23)

"The ice cream is just hanging in the air before her during the jump": with a tray or a cone she hopped in her free-armed
jump frames (`rise`, `apex`, `fall`), the load floating where her hands are when she walks with it. Her sheet's
`carry-rise`, `carry-apex`, `carry-fall` (the game's `pose()` takes them by name while she carries); the load placed by her
fists in each (`HOP_HOLDS` in `src/world/carry.js`). The hop's height and timing unchanged ("it has to stay as low").

| Folder | What | PixelLab | Generations |
|---|---|---|---|
| `raw/` | The library's jump with her hands held in front; "holding something" in its description drew a grey thing in her hands. Not used | skeleton-v3, group `3985f3bd-80d2-47a8-9e90-ecb3950aa453` | 3 |
| `raw2/` | The same, "hands together in front": no thing, but straight legs ("that doesn't look like a jump at all"). Not used | skeleton-v3, group `2149292f-f8e0-4466-aa2c-b3088faee7bf` | 3 |
| `raw3/` | **Used**: her own jump's three poses (`../jump/3`, `4`, `5`, skeletons estimated on a 96 px canvas, the top's and the fall's left and right swapped back) with her carry-stand's arms (`../carry-walk/2`), moved with her neck; her carry-stand picture animated through them | `animate_with_skeleton_v3`, job `cfb28e98-0d8e-4dc3-b68a-35de8fce9bd5` | 2 (+0.4 estimates) |
