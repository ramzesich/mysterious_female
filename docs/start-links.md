# Start links

Every place the game can be started at on this computer, for testing. Run `python tools/serve.py`
first. Each link skips the welcome screen and the intro (`?play`), opens every lock and gives her every verb (`cards=all`), and makes
the dash free (`tangerines=infinite`).

Useful additions to any link:

- `&reset` clears the saved progress first.
- `&lang=uk` shows the game in Ukrainian for that session (`&lang=en` for English).
- `&sound=off` silences it.
- `&did=<flags>` starts with parts of the story already done (the list is in `README.md`).

The places are the map's `place` objects, made in `tools/build_ship_map.py` (`build_objects()`); a
new one added there should be added here too.

## The game's own start

| Place | Link |
|---|---|
| Where the game starts: deck 3, her crew cabin's door (with a fresh save) | <http://localhost:8000/?play&reset&cards=all&tangerines=infinite> |
| The welcome screen, then the whole intro (a new game: the save is cleared) | <http://localhost:8000/?reset&tangerines=infinite> |
| The welcome screen with the save kept (a game under way gets the short way in) | <http://localhost:8000/?tangerines=infinite> |
| The intro from the whole ship in view | <http://localhost:8000/?reset&intro=ship&tangerines=infinite> |
| The intro from the corridor, just before her door | <http://localhost:8000/?reset&intro=corridor&tangerines=infinite> |
| The intro from the close-up on her (the badge) | <http://localhost:8000/?reset&intro=badge&tangerines=infinite> |

## Deck 3

| Place | Link |
|---|---|
| `crew`: the crew corridor, at her cabin's door | <http://localhost:8000/?play&at=crew&cards=all&tangerines=infinite> |

## Deck 4

| Place | Link |
|---|---|
| `gangway`: the gangway lobby | <http://localhost:8000/?play&at=gangway&cards=all&tangerines=infinite> |

## Deck 5

| Place | Link |
|---|---|
| `atrium-floor`: the atrium's floor, by the café | <http://localhost:8000/?play&at=atrium-floor&cards=all&tangerines=infinite> |

## Deck 6

| Place | Link |
|---|---|
| `bar`: Bliss Ultra Lounge | <http://localhost:8000/?play&at=bar&cards=all&tangerines=infinite> |
| `library`: inside the Library | <http://localhost:8000/?play&at=library&cards=all&tangerines=infinite> |
| `theatre`: the Stardust Lounge | <http://localhost:8000/?play&at=theatre&cards=all&tangerines=infinite> |
| `promenade`: outside, on the promenade | <http://localhost:8000/?play&at=promenade&cards=all&tangerines=infinite> |

## Deck 7

| Place | Link |
|---|---|
| `bow`: the mooring deck | <http://localhost:8000/?play&at=bow&cards=all&tangerines=infinite> |
| `kids`: Splash Academy | <http://localhost:8000/?play&at=kids&cards=all&tangerines=infinite> |
| `atrium`: the atrium's walk | <http://localhost:8000/?play&at=atrium&cards=all&tangerines=infinite> |
| `walkway`: outside, the boat walkway over the promenade, at the station locker | <http://localhost:8000/?play&at=walkway&cards=all&tangerines=infinite> |

## Deck 8

| Place | Link |
|---|---|
| `cabin`: inside cabin 8206 | <http://localhost:8000/?play&at=cabin&cards=all&tangerines=infinite> |
| `home`: the corridor, a few doors from cabin 8206 | <http://localhost:8000/?play&at=home&cards=all&tangerines=infinite> |

## Deck 9

| Place | Link |
|---|---|
| `captain`: the captain's door | <http://localhost:8000/?play&at=captain&cards=all&tangerines=infinite> |
| `linen`: inside the linen room | <http://localhost:8000/?play&at=linen&cards=all&tangerines=infinite> |
| `housekeeping`: the corridor where the red trunk comes up | <http://localhost:8000/?play&at=housekeeping&cards=all&tangerines=infinite> |
| `balcony`: outside, on the balcony of the balcony cabin | <http://localhost:8000/?play&at=balcony&cards=all&tangerines=infinite> |
| `stern`: the aft terrace | <http://localhost:8000/?play&at=stern&cards=all&tangerines=infinite> |

## Deck 10

| Place | Link |
|---|---|
| `bridge`: the bridge | <http://localhost:8000/?play&at=bridge&cards=all&tangerines=infinite> |

## Deck 11

| Place | Link |
|---|---|
| `sunset`: the balcony forward of the spa, where the last glide starts | <http://localhost:8000/?play&at=sunset&cards=all&tangerines=infinite> |
| `spa`: the spa's reception | <http://localhost:8000/?play&at=spa&cards=all&tangerines=infinite> |
| `gym`: the fitness centre | <http://localhost:8000/?play&at=gym&cards=all&tangerines=infinite> |
| `pool`: the pool deck | <http://localhost:8000/?play&at=pool&cards=all&tangerines=infinite> |
| `buffet`: the Garden Café | <http://localhost:8000/?play&at=buffet&cards=all&tangerines=infinite> |
| `diner`: the Great Outdoors | <http://localhost:8000/?play&at=diner&cards=all&tangerines=infinite> |

## Deck 12

| Place | Link |
|---|---|
| `spinnaker`: the Spinnaker Lounge | <http://localhost:8000/?play&at=spinnaker&cards=all&tangerines=infinite> |
| `chapel`: inside the Chapel | <http://localhost:8000/?play&at=chapel&cards=all&tangerines=infinite> |
| `champs`: Champs Bar | <http://localhost:8000/?play&at=champs&cards=all&tangerines=infinite> |
| `deck12`: the sun deck, over the pools | <http://localhost:8000/?play&at=deck12&cards=all&tangerines=infinite> |
| `sundeck`: the sun deck, by the old lady's sunbed | <http://localhost:8000/?play&at=sundeck&cards=all&tangerines=infinite> |
| `court`: the sports court | <http://localhost:8000/?play&at=court&cards=all&tangerines=infinite> |
| `technical`: the technical ladder's foot, at Cagney's | <http://localhost:8000/?play&at=technical&cards=all&tangerines=infinite> |
| `cagneys`: Cagney's, by the wedding cake | <http://localhost:8000/?play&at=cagneys&cards=all&tangerines=infinite> |
| `sushi`: the Sushi Bar | <http://localhost:8000/?play&at=sushi&cards=all&tangerines=infinite> |
| `teppanyaki`: Teppanyaki | <http://localhost:8000/?play&at=teppanyaki&cards=all&tangerines=infinite> |
| `bistro`: Le Bistro | <http://localhost:8000/?play&at=bistro&cards=all&tangerines=infinite> |
| `terrace`: the aft terrace | <http://localhost:8000/?play&at=terrace&cards=all&tangerines=infinite> |

## Above deck 12

| Place | Link |
|---|---|
| `funnel`: the funnel's top | <http://localhost:8000/?play&at=funnel&cards=all&tangerines=infinite> |
