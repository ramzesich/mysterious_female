# The funnel's smoke: generated tries (2026-11-27, the hull's top review, 8), none used

The user turned down every generated try ("neither of those look like smoke going out of the pipe, not even close";
then "neither of the generated smoke images fit our pipes") and chose smoke drawn as the DJ's fog machine's
(`drawSmoke` in the ship scene, `FUNNEL_SMOKE` in the config). Kept for the record.

- `puff-a.png`, `puff-b.png`: `create_image_pro_flash`, 64 x 64, style `style-cloud-6.png` (the sky atlas's `cloud-6`),
  seeds 11 and 23; jobs 8322d109-a9f9-4919-96f2-c3b39d217a62, e28706c5-051f-4c6d-937a-418ddb321261. 10 generations.
- `plume-c.png`, `plume-d.png`: `inpaint_image_pro_flash` on the game's own picture of the funnel's top with the sky
  turned green (`inp-src.png`, mask `inp-mask.png`), seeds 5 and 17; jobs 849d324f-5970-40a5-981f-1153d363307a,
  b8c11169-fc71-4b4f-9401-6a910d26cd52. 18 generations. `plume-c-cut.png`: c unmixed from the green.
