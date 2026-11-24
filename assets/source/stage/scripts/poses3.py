"""Her two new clips as poses for animate_character skeleton-v3 (east): start-back (out of her tiptoe, a recoil,
held) and look-up (from the recoil upright, her head back, held). Prints each as one line of JSON."""
import json
E = {"right_elbow": [0.3, 0, -1], "left_elbow": [-0.3, 0, -1]}
def hands(f, u, s=0.07):
    return {"right_hand": [s, f, u], "left_hand": [-s, f, u], **E}
sb = [
    {"frame": 1, "pelvis": [0, 0, 0.012], "lean": [9, 0], "head": [0, -4], "right_foot": [0, 0.03, 0.012], "left_foot": [0, -0.03, 0.012], **hands(0.115, 0.115, 0.06)},
    {"frame": 2, "pelvis": [0, -0.012, 0.008], "lean": [1, 0], "head": [0, -6], "right_foot": [0, 0.03, 0.006], "left_foot": [0, -0.03, 0.006], **hands(0.12, 0.155)},
    {"frame": 3, "pelvis": [0, -0.03, 0.0], "lean": [-9, 0], "head": [0, -8], "right_foot": [0, -0.04, 0.025], "left_foot": [0, -0.03, 0], **hands(0.11, 0.2, 0.08)},
    {"frame": 4, "pelvis": [0, -0.045, -0.01], "lean": [-13, 0], "head": [0, -8], "right_foot": [0, -0.085, 0], "left_foot": [0, -0.03, 0], **hands(0.1, 0.215, 0.085)},
    {"frame": 5, "pelvis": [0, -0.043, -0.006], "lean": [-11, 0], "head": [0, -6], "right_foot": [0, -0.085, 0], "left_foot": [0, -0.03, 0], **hands(0.1, 0.21, 0.085)},
    {"frame": 6, "pelvis": [0, -0.04, -0.002], "lean": [-8, 0], "head": [0, -4], "right_foot": [0, -0.085, 0], "left_foot": [0, -0.03, 0], **hands(0.1, 0.19, 0.08)},
    {"frame": 7, "pelvis": [0, -0.038, 0], "lean": [-6, 0], "head": [0, -2], "right_foot": [0, -0.085, 0], "left_foot": [0, -0.03, 0], **hands(0.1, 0.17, 0.075)},
    {"frame": 8, "pelvis": [0, -0.036, 0], "lean": [-5, 0], "head": [0, 0], "right_foot": [0, -0.085, 0], "left_foot": [0, -0.03, 0], **hands(0.1, 0.16, 0.07)},
]
print("STARTBACK", json.dumps(sb))
lu = [
    {"frame": 1, "pelvis": [0, -0.036, 0], "lean": [-5, 0], "head": [0, 0], "right_foot": [0, -0.085, 0], "left_foot": [0, -0.03, 0], **hands(0.1, 0.16, 0.07)},
    {"frame": 2, "pelvis": [0, -0.03, 0], "lean": [-4, 0], "head": [0, -10], "right_foot": [0, -0.06, 0.018], "left_foot": [0, -0.03, 0], **hands(0.08, 0.1, 0.085)},
    {"frame": 3, "pelvis": [0, -0.022, 0], "lean": [-4, 0], "head": [0, -20], "right_foot": [0, -0.035, 0], "left_foot": [0, -0.03, 0], **hands(0.05, 0.04, 0.095)},
    {"frame": 4, "pelvis": [0, -0.02, 0], "lean": [-6, 0], "head": [0, -30], "right_foot": [0, -0.03, 0], "left_foot": [0, -0.03, 0]},
    {"frame": 5, "pelvis": [0, -0.02, 0], "lean": [-7, 0], "head": [0, -34], "right_foot": [0, -0.03, 0], "left_foot": [0, -0.03, 0]},
    {"frame": 6, "pelvis": [0, -0.02, 0], "lean": [-7, 0], "head": [0, -34], "right_foot": [0, -0.03, 0], "left_foot": [0, -0.03, 0]},
    {"frame": 7, "pelvis": [0, -0.02, 0], "lean": [-7, 0], "head": [0, -32], "right_foot": [0, -0.03, 0], "left_foot": [0, -0.03, 0]},
    {"frame": 8, "pelvis": [0, -0.02, 0], "lean": [-6, 0], "head": [0, -32], "right_foot": [0, -0.03, 0], "left_foot": [0, -0.03, 0]},
]
print("LOOKUP", json.dumps(lu))
