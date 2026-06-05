import random
from atm import Atm


def generate_atms(count: int = 10, seed: int = 42) -> list[Atm]:
    if seed is not None:
        random.seed(seed)

    atms = []
    LAT_MIN, LAT_MAX = 55.55, 55.95
    LON_MIN, LON_MAX = 37.30, 37.95

    for i in range(1, count + 1):
        lat = round(random.uniform(LAT_MIN, LAT_MAX), 6)
        lon = round(random.uniform(LON_MIN, LON_MAX), 6)
        cap_in = random.randint(8000, 30000)
        cap_out = random.randint(10000, 25000)

        atm = Atm(
            atm_id=i,
            lat=lat,
            lon=lon,
            capacity_in=cap_in,
            capacity_out=cap_out,
            mean_in=round(random.uniform(50, 200), 1),
            std_in=round(random.uniform(5, 30), 1),
            mean_out=round(random.uniform(50, 200), 1),
            std_out=round(random.uniform(5, 30), 1)
        )

        atms.append(atm)

    return atms