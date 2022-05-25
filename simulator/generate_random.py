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

ZONE_PROBS_CUMM = {
    "107": 0.26268750726179774,
    "234": 0.5564402208809553,
    "90": 0.7827575874320447,
    "164": 1.0,
}

TRAVEL_TIMES = {
    "107": {
        "107": {
            "dist_name": "gamma",
            "dist_params": [1.0595605055074295, 115.98073442301566, 399.1107588971165],
            "mean": 538.8627318734982,
            "sample_count": 6141,
        },
        "234": {
            "dist_name": "gamma",
            "dist_params": [4.943208918902067, 124.85447136169067, 68.97324934794729],
            "mean": 465.8036527041199,
            "sample_count": 10975,
        },
        "90": {
            "dist_name": "gamma",
            "dist_params": [4.237996568858217, 234.2670258838313, 80.55790712873352],
            "mean": 575.6711598898029,
            "sample_count": 8542,
        },
        "164": {
            "dist_name": "gamma",
            "dist_params": [3.910027852857953, 199.14283161298493, 94.05667255866535],
            "mean": 566.9070410645068,
            "sample_count": 10176,
        },
    },
    "234": {
        "107": {
            "dist_name": "gamma",
            "dist_params": [3.538148593296823, 139.35050126121234, 89.94319051445595],
            "mean": 457.5828742565628,
            "sample_count": 9115,
        },
        "234": {
            "dist_name": "lognorm",
            "dist_params": [0.9223032648267515, 106.0337785391994, 280.47965166932863],
            "mean": 535.1907854373871,
            "sample_count": 9578,
        },
        "90": {
            "dist_name": "lognorm",
            "dist_params": [0.4074144037095627, 37.97007578678993, 334.78890349700634],
            "mean": 401.72976042428803,
            "sample_count": 7909,
        },
        "164": {
            "dist_name": "gamma",
            "dist_params": [3.3405082930981314, 139.88206690069944, 103.7517807764905],
            "mean": 486.4657510082653,
            "sample_count": 11789,
        },
    },
    "90": {
        "107": {
            "dist_name": "gamma",
            "dist_params": [5.546598986375935, 164.81587650890793, 67.44466673284992],
            "mean": 538.904396645796,
            "sample_count": 9038,
        },
        "234": {
            "dist_name": "gamma",
            "dist_params": [3.2878913290348026, 125.39010492751109, 82.58482028105033],
            "mean": 396.920019439474,
            "sample_count": 10187,
        },
        "90": {
            "dist_name": "lognorm",
            "dist_params": [1.0472052882517313, 101.94129596859332, 268.83598863679595],
            "mean": 567.1196754689264,
            "sample_count": 5208,
        },
        "164": {
            "dist_name": "gamma",
            "dist_params": [4.413413850178148, 141.03213200129, 83.03189678343799],
            "mean": 507.4862552718776,
            "sample_count": 9929,
        },
    },
    "164": {
        "107": {
            "dist_name": "gamma",
            "dist_params": [3.800296883350668, 171.63924789232982, 91.201030606785],
            "mean": 518.2302402656637,
            "sample_count": 8192,
        },
        "234": {
            "dist_name": "gamma",
            "dist_params": [2.8378165080479656, 130.90278735621956, 98.80054102131234],
            "mean": 411.28059367056994,
            "sample_count": 13324,
        },
        "90": {
            "dist_name": "gamma",
            "dist_params": [3.297720550835024, 199.08770673657716, 87.52064055901457],
            "mean": 487.7063217302848,
            "sample_count": 7711,
        },
        "164": {
            "dist_name": "lognorm",
            "dist_params": [0.9895920619964935, 104.62083946009903, 322.20521251293536],
            "mean": 630.3756019840691,
            "sample_count": 5922,
        },
    },
}


def generate_pickup_zone(random_var: float = None):
    """
    Generates the pick up zone.
    """
    rand = random.random() if not random_var else random_var
    for zone in ZONE_PROBS_CUMM:
        if rand <= ZONE_PROBS_CUMM[zone]:
            return zone, rand


def generate_dropoff_zone(random_var: float = None):
    """
    Generate the drop off zone.
    """
    rand = random.random() if not random_var else random_var
    if rand <= 0.25:
        return "107", rand
    elif rand <= 0.5:
        return "234", rand
    elif rand <= 0.75:
        return "90", rand
    return "164", rand


def gen_expon(size: int):
    """ """
    expon_gen = st.expon.rvs(1.0, 18.107468934687073, size=size)
    return expon_gen

    # poisson = st.poisson.rvs(total_time * (1 / 18.1074689))
    # print(f"Poisson: {poisson}")


class TravelTime:
    def __init__(self, size=500):
        self.size = size
        self.travel_times = self._generate_travel_dist()

    def _generate_travel_dist(self):
        """
        Generates travel distributions.
        """
        travel_times = {}
        for zone_1 in TRAVEL_TIMES:
            travel_times[zone_1] = {}
            for zone_2 in TRAVEL_TIMES[zone_1]:
                travel_times[zone_1][zone_2] = {}
                distribution = getattr(st, TRAVEL_TIMES[zone_1][zone_2]["dist_name"])
                travel_times[zone_1][zone_2]["times"] = list(
                    distribution.rvs(
                        TRAVEL_TIMES[zone_1][zone_2]["dist_params"][0],
                        TRAVEL_TIMES[zone_1][zone_2]["dist_params"][1],
                        TRAVEL_TIMES[zone_1][zone_2]["dist_params"][2],
                        size=self.size,
                    )
                )
                travel_times[zone_1][zone_2]["next"] = 0
        return travel_times

    def next_time(self, zone_1, zone_2):
        """
        Returns the next travel time for zone_1 -> zone_2.
        """
        next_idx = self.travel_times[zone_1][zone_2]["next"]
        next_time = self.travel_times[zone_1][zone_2]["times"][next_idx]
        self.travel_times[zone_1][zone_2]["next"] = next_idx + 1
        return next_time


# tt = TravelTime()
# print(f"All times: {tt.travel_times}")
# print(f"{tt.next_time('107', '107')}")
# print(f"{tt.next_time('107', '107')}")
# print(f"{tt.next_time('107', '107')}")
# print(f"{tt.next_time('107', '234')}")
# print(f"{tt.next_time('107', '234')}")
# print(f"{tt.next_time('107', '234')}")
