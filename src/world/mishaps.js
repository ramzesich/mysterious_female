// How she takes a hit (docs/plan-three-uses.md §1.6): which of an obstacle's scenarios a hit is, by
// the two facts read at every hit, which side of her it is on and who was moving. The scenarios
// themselves (her word, her reaction with a tangerine on her, what stands in for her gag without
// one) are `MISHAP_SCENES` in src/config.js; the obstacles are `MISHAPS` there.

// `f`: { front: the hit is on the side she faces; she: she was moving toward it; it: it was moving
// toward her; faces: it faces her (a person: the porter, the jogger); lying: a thing at rest on the
// floor (a paper); crowded: someone stands just past it (the trolley's stewardess) }. Returns the scenario's number, as in the plan's tables.
const PICK = {
    chips: () => '1',
    popcorn: () => '1',
    lead: () => '2',
    trays: () => '3',
    // A paper (the user, 2026-11-16): at her front, sliding at her or lying where she steps, her
    // leg goes up behind her and she falls on her belly; at her heel, from behind, her leg goes up
    // in front and she falls on her bottom. Standing still she slips too.
    papers: f => f.front ? '4a' : '4b',
    // (With none on her she rides it off either way, the user, 2026-11-16; with one, the side.)
    vacuum: f => f.front || f.she ? '5a' : '5b',
    // The suitcase: run into; rolled into her back; rolled into her front. With none on her she
    // rides it off in all three (the user, 2026-11-16); the side picks her reaction with one on her.
    suitcase: f => f.she ? '6a' : f.front ? '6c' : '6b',
    deckchair: f => f.front ? '7a' : '7b',
    // The porter: into his cart (he faces her) or into his back; standing, the cart pushes into her
    // front or reaches her back.
    cart: f => f.she ? (f.faces ? '8a' : '8d') : f.front ? '8b' : '8c',
    jogger: f => f.she && f.front ? (f.faces ? '9a' : '9d') : f.front ? '9b' : '9c',
    breakfast: f => f.front ? '10a' : '10b',
    // Her trolley: at her front, over it if no one stands just past it, else back off it; at her
    // back. The stewardess herself, her hands empty: bounced off.
    trolley: f => f.front ? (f.crowded ? '10d' : '10c') : '10e',
    stewardess: () => '10f',
    // (The lady in her bathrobe, standing: she bounces off her as off the stewardess, 10f.)
    robe: () => '10f',
    // (The Seven Seas' waiter, either way: she bounces off him as off her, the user, 2026-11-28.)
    waiter: () => '10f',
    jet: f => f.front ? '11a' : '11b',
    light: f => f.front ? '12a' : '12b',
    // A door: opening in her face (she faces it), or catching her just past it.
    door: f => f.front ? '13a' : '13b',
    ball: f => f.front ? '14a' : '14b',
    boat: () => '15',
    sprinkler: () => '16',
    steam: () => '17',
    towels: () => '18',
    flare: () => '19',
    railgull: () => '20',
    funnelgull: () => '21',
    crossgull: () => '22',
    dnd: () => '23',
    balcony: () => '24',
    // A gym ball: at her front she trips over it, forward; at her back it bumps her onto her bottom (the user).
    gymball: f => f.front ? '25a' : '25b',
    pillow: () => '26',
    kid: () => '27',
    painting: () => '28',
};

export function scenario(what, f) {
    return (PICK[what] ?? (() => null))(f);
}
