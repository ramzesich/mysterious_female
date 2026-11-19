# Start links

Every place the game can be started at on this computer, for testing. Run `python tools/serve.py`
first. Each link skips the welcome screen and the intro (`?play`), opens every lock and gives her every verb (`cards=all`).

Useful additions to any link:

- `&tangerines=infinite`: a tangerine is never used up (the cry, the lunge, the throw; a gull still
  swoops at her, and takes one rather than playing its gag).
- `&reset` clears the saved progress first.
- `&lang=ua` shows the game in Ukrainian for that session (`&lang=en` for English).
- `&sound=off` silences it.
- `&did=<flags>` starts with parts of the story already done (the list is in `README.md`).

The places are the map's `place` objects, made in `tools/build_ship_map.py` (`build_objects()`); a
new one added there should be added here too.

## The game's own start

| Place | Link |
|---|---|
| Where the game starts: deck 3, her crew cabin's door (with a fresh save) | <http://localhost:8000/?play&reset&cards=all> |
| The welcome screen, then the whole intro (a new game: the save is cleared) | <http://localhost:8000/?reset> |
| The welcome screen with the save kept (a game under way gets the short way in) | <http://localhost:8000/?tangerines=infinite> |
| The intro from the whole ship in view | <http://localhost:8000/?reset&intro=ship> |
| The intro from the corridor, just before her door opens | <http://localhost:8000/?reset&intro=corridor> |

## Deck 3

| Place | Link |
|---|---|
| `crew`: the crew corridor, at her cabin's door | <http://localhost:8000/?play&at=crew&cards=all> |

## Deck 4

| Place | Link |
|---|---|
| `gangway`: the gangway lobby | <http://localhost:8000/?play&at=gangway&cards=all> |
| `deck4`: deck 4's corridor between the runaway suitcase and the porter's round | <http://localhost:8000/?play&at=deck4&cards=all> |
| `deck4-aft`: deck 4's corridor aft, just forward of the robot vacuum's round | <http://localhost:8000/?play&at=deck4-aft&cards=all> |

## Deck 5

| Place | Link |
|---|---|
| `deck5`: deck 5's corridor between its two paper rounds (the first forward of her, the second aft) | <http://localhost:8000/?play&at=deck5&cards=all> |
| `atrium-floor`: the atrium's floor, by the café | <http://localhost:8000/?play&at=atrium-floor&cards=all> |

## Deck 6

| Place | Link |
|---|---|
| `bar`: Bliss Ultra Lounge | <http://localhost:8000/?play&at=bar&cards=all> |
| `library`: inside the Library | <http://localhost:8000/?play&at=library&cards=all> |
| `theatre`: the Stardust Lounge | <http://localhost:8000/?play&at=theatre&cards=all> |
| `promenade`: outside, on the promenade | <http://localhost:8000/?play&at=promenade&cards=all> |
| `light6`: deck 6, by the stage door, forward of the stage's swinging light (walk aft under it as it swings: 12a from in front of it, 12b at her back; it swings once near-catch 3 is done, `did=bb3`) | <http://localhost:8000/?play&at=light6&did=bb3> |

## Deck 7

| Place | Link |
|---|---|
| `bow`: the mooring deck | <http://localhost:8000/?play&at=bow&cards=all> |
| `kids`: Splash Academy | <http://localhost:8000/?play&at=kids&cards=all> |
| `atrium`: the atrium's walk | <http://localhost:8000/?play&at=atrium&cards=all> |
| `walkway`: outside, the boat walkway over the promenade, at the station locker | <http://localhost:8000/?play&at=walkway&cards=all> |
| `chips7`: deck 7, at the casino's door, forward of the slot machines (run aft onto a spill of chips: 1) | <http://localhost:8000/?play&at=chips7> |
| `drill7`: outside, on the boat walkway 5.5 m forward of the drill's boat (once it is hoisted again, run aft at it: 15) | <http://localhost:8000/?play&at=drill7&cards=all> |

## Deck 8

| Place | Link |
|---|---|
| `cabin`: inside cabin 8206 | <http://localhost:8000/?play&at=cabin&cards=all> |
| `home`: the corridor, a few doors from cabin 8206 | <http://localhost:8000/?play&at=home&cards=all> |
| `occupied8`: outside, on the balcony aft of the sunbather's (hold ←, jump and jump again beside the partition to vault onto his: 24, no tangerine on her; `cards=all` for the grip socks) | <http://localhost:8000/?play&at=occupied8&cards=all> |

## Deck 9

| Place | Link |
|---|---|
| `captain`: the captain's door | <http://localhost:8000/?play&at=captain&cards=all> |
| `linen`: inside the linen room | <http://localhost:8000/?play&at=linen&cards=all> |
| `housekeeping`: the corridor where the red trunk comes up | <http://localhost:8000/?play&at=housekeeping&cards=all> |
| `deck9-aft`: deck 9's corridor, a few steps short of the darting vacuum | <http://localhost:8000/?play&at=deck9-aft&cards=all> |
| `steward`: deck 9's corridor at its aft end, just forward of the steward's jammed trolley | <http://localhost:8000/?play&at=steward> |
| `door9`: deck 9, aft of its swinging door (walk forward at it: 13a) | <http://localhost:8000/?play&at=door9> |
| `gull9`: deck 9's balconies, by a perched gull (stand by it: 20) | <http://localhost:8000/?play&at=gull9> |
| `sprinkler9`: deck 9's corridor, 4 m forward of its sprinkler (run aft into its rain: 16; tangerines make no difference) | <http://localhost:8000/?play&at=sprinkler9> |
| `dnd9`: deck 9's corridor, 2 m forward of its "Do Not Disturb" door (walk aft to it and press E: 23, no tangerine on her) | <http://localhost:8000/?play&at=dnd9> |
| `towels9`: deck 9's corridor, 3 m aft of the towel stack (run forward past it: 18) | <http://localhost:8000/?play&at=towels9> |
| `balcony`: outside, on the balcony of the balcony cabin | <http://localhost:8000/?play&at=balcony&cards=all> |
| `stern`: the aft terrace | <http://localhost:8000/?play&at=stern&cards=all> |

## Deck 10

| Place | Link |
|---|---|
| `bridge`: the bridge | <http://localhost:8000/?play&at=bridge&cards=all> |
| `trays10`: deck 10, forward of the room-service tray (run aft onto it: 3) | <http://localhost:8000/?play&at=trays10> |

## Deck 11

| Place | Link |
|---|---|
| `sunset`: the balcony forward of the spa, where the last glide starts | <http://localhost:8000/?play&at=sunset&cards=all> |
| `spa`: the spa's reception | <http://localhost:8000/?play&at=spa&cards=all> |
| `gym`: the fitness centre | <http://localhost:8000/?play&at=gym&cards=all> |
| `pool`: the pool deck | <http://localhost:8000/?play&at=pool&cards=all> |
| `buffet`: the Garden Café | <http://localhost:8000/?play&at=buffet&cards=all> |
| `diner`: the Great Outdoors | <http://localhost:8000/?play&at=diner&cards=all> |
| `wet`: deck 11, aft of the wet patch and its deck chair (walk forward past the chair onto the tiles: she slides away from it) | <http://localhost:8000/?play&at=wet> |
| `wet7a`: deck 11, 2.5 m forward of the wet patch (walk aft onto it: she slides into the chair, 7a) | <http://localhost:8000/?play&at=wet7a> |
| `icecream`: deck 11's Great Outdoors, by the soft serve machine (E and hold, let go in the green: a cone; carry it forward to the kid on the aft pool deck, about 65 m, before it melts in 45 s; he is there once Bumbot's near-catch 5 at the hot tub is done, `did=bb5`) | <http://localhost:8000/?play&at=icecream&did=bb5> |
| `steam11`: deck 11's spa, aft of the sauna's door, just short of the steam's reach (walk forward into it as it rolls out, or stand in it: 17) | <http://localhost:8000/?play&at=steam11> |
| `jet11`: deck 11, at the pool attendant's hut on the aft pool's rim (walk aft at the kid: his jet in her face, 11a; past him, in her back, 11b; he is there once near-catch 5 is done, `did=bb5`) | <http://localhost:8000/?play&at=jet11&did=bb5> |

## Deck 12

| Place | Link |
|---|---|
| `spinnaker`: the Spinnaker Lounge | <http://localhost:8000/?play&at=spinnaker&cards=all> |
| `chapel`: inside the Chapel | <http://localhost:8000/?play&at=chapel&cards=all> |
| `champs`: Champs Bar | <http://localhost:8000/?play&at=champs&cards=all> |
| `deck12`: the sun deck, over the pools | <http://localhost:8000/?play&at=deck12&cards=all> |
| `sundeck`: the sun deck, by the old lady's sunbed | <http://localhost:8000/?play&at=sundeck&cards=all> |
| `court`: the sports court | <http://localhost:8000/?play&at=court&cards=all> |
| `technical`: the technical ladder's foot, at Cagney's | <http://localhost:8000/?play&at=technical&cards=all> |
| `cagneys`: Cagney's, by the wedding cake | <http://localhost:8000/?play&at=cagneys&cards=all> |
| `sushi`: the Sushi Bar | <http://localhost:8000/?play&at=sushi&cards=all> |
| `teppanyaki`: Teppanyaki | <http://localhost:8000/?play&at=teppanyaki&cards=all> |
| `bistro`: Le Bistro | <http://localhost:8000/?play&at=bistro&cards=all> |
| `terrace`: the aft terrace | <http://localhost:8000/?play&at=terrace&cards=all> |

## Above deck 12

| Place | Link |
|---|---|
| `funnel`: the funnel's top | <http://localhost:8000/?play&at=funnel&cards=all> |
| `stairway`: the foot of the funnel's stairway | <http://localhost:8000/?play&at=stairway&cards=all> |
