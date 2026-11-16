// How she takes a hit (docs/plan-three-uses.md §1.6): which of an obstacle's scenarios a hit is, by
// the two facts read at every hit, which side of her it is on and who was moving. The scenarios
// themselves (her word, her reaction with a tangerine on her, what stands in for her gag without
// one) are `MISHAP_SCENES` in src/config.js; the obstacles are `MISHAPS` there.

// `f`: { front: the hit is on the side she faces; she: she was moving toward it; it: it was moving
// toward her; faces: it faces her (a person: the porter, the jogger); lying: a thing at rest on the
// floor (a paper) }. Returns the scenario's number, as in the plan's tables.
const PICK = {
    chips: () => '1',
    lead: () => '2',
    trays: () => '3',
    // A paper: run onto, or sliding her way as she goes, her foot goes on ahead (back on her bottom);
    // slid against her from behind, her foot is taken back (on her front); one sliding at her as she
    // stands looking at it stops against her shoe (the user's: "nothing").
    papers: f => f.lying ? '4a' : !f.front ? '4b' : f.she ? '4a' : '4c',
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
};

export function scenario(what, f) {
    return (PICK[what] ?? (() => null))(f);
}
