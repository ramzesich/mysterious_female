# The books' covers (plan-the-rest §2.3)

Each her own copy's cover: the user photographed them (2026-11-22, `reference/books/`, git-ignored, never committed),
each was straightened (its four corners found by GrabCut, warped flat), its words painted out (OpenCV inpaint over the
letters, boxes per cover), then redrawn by PixelLab `image_to_pixelart` at 120 x 180, the default (redrawn) mode,
seed 7, 1 generation each. The user chose redrawn (a) over faithful (b, init strength 150) on books 3, 10 and 14.
Titles and authors are set back in by `tools/build_covers.py` (Pixelzone), never generated.

| Book | Try | Job id |
|---|---|---|
| 2 Harry Potter and the Chamber of Secrets | `tries/02-a.png` (**used**) | b19fbfe9-0891-4096-b81d-6f359245037c |
| 3 Танґо смерті | `tries/03-a.png` (**used**) | 9c4bcfb3-491d-4677-99f1-6d45dae405b6 |
| 3 | `tries/03-b.png` (faithful) | cf3d5058-1686-4cb9-a57c-8f70552f00a3 |
| 4 Unexpected Lessons in Love | `tries/04-a.png` (**used**) | 6f9a896c-de2e-4ecd-b13c-db09166154cb |
| 5 Її війна | `tries/05-a.png` (**used**) | 41ec5df5-835e-4cbf-9d93-676a8613daea |
| 6 Harry Potter and the Philosopher's Stone | `tries/06-a.png` (**used**) | 01813fb5-6a8d-4197-96a0-3477f42c7d0b |
| 7 Понаїхали | `tries/07-a.png` (**used**; the bag put back to grey) | a99ef86c-9c7c-4c69-b302-bff50cd92cf9 |
| 8 Niebieskie nitki | `tries/08-a.png` (**used**; its bands made taller) | 89584eed-021c-4d43-99ac-6c0ec0ffd6f1 |
| 9 Двор | `tries/09-a.png` (**used**; put back to black and white) | 9265dc11-7766-4a15-87ca-c6ff9ea78a59 |
| 10 Боря, выйди с моря | `tries/10-a.png` (**used**) | 0adb53b3-46c6-48a0-af34-b3eb22b12178 |
| 10 | `tries/10-b.png` (faithful) | 0b982dba-c759-4fa1-a857-aaf48ce9e3e9 |
| 11 נערה במעיל כחול | `tries/11-a.png` (**used**) | f1e7be30-57cd-47f6-bbb8-b61413e768b5 |
| 12 Poczwarka | `tries/12-a.png` (**used**) | cd3944af-635d-461f-8974-8ee08cdb6609 |
| 13 Daughters of Warsaw | `tries/13-a.png` (**used**) | 79516333-dbe1-47e7-96d1-5403e03bd1a9 |
| 14 Pachinko | `tries/14-a.png` (**used**) | 0a0734cb-f35f-4a72-a082-d01037267494 |
| 14 | `tries/14-b.png` (faithful) | 43bf574b-bea7-46cd-bd9e-7b307bcd2226 |

Book 1 (Atomic Habits) is lettering on white with gold dust and nothing else: no try, drawn by the build.
Books 2 and 6 are her Slytherin house editions (Bloomsbury), photographed later the same day.
