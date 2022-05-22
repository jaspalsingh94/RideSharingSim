import json
import random
import scipy.stats as st


ARRIVAL_PROB = {
    "zone_probs": {
        "107": {"count": 85913, "prob": 0.26268750726179774},
        "234": {"count": 96073, "prob": 0.29375271361915767},
        "90": {"count": 74018, "prob": 0.22631736655108942},
        "164": {"count": 71050, "prob": 0.21724241256795515},
    },
    "dist_name": "expon",
    "dist_params": [1.0, 18.107468934687073],
    "sample_count": 316752,
}

ZONE_PROBS_CUMM = {'107': 0.26268750726179774, '234': 0.5564402208809553, '90': 0.7827575874320447, '164': 1.0}


def generate_pickup_zone():
    """
    Generates the pick up zone.
    """
    rand = random.random()
    for zone in ZONE_PROBS_CUMM:
        if rand <= ZONE_PROBS_CUMM[zone]:
            return zone


def generate_dropoff_zone():
    """
    Generate the drop off zone.
    """
    rand = random.random()
    if rand <= 0.25:
        return '107'
    elif rand <= 0.5:
        return '234'
    elif rand <= 0.75:
        return '90'
    return '164'


def gen_expon(size: int):
    """ 
    """
    expon_gen = st.expon.rvs(1.0, 18.107468934687073, size=size)
    return expon_gen

    # poisson = st.poisson.rvs(total_time * (1 / 18.1074689))
    # print(f"Poisson: {poisson}")
