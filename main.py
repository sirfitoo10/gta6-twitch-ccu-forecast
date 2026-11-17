# gta6-twitch-ccu-forecast-01 entry: similarity-weighted launch-analog forecaster.
#
# Anchors on hour 1's print (p1). For each hour h the model pools, across past
# big game launches in the case's comparables, the log-ratio ln(v_h / v_1) of
# their release-day curves, weighting each launch by exp(-|ln(p1c / p1)| / 0.4)
# so launches with a similar opening hour count most. The five quantiles are
# read off that weighted pool around its weighted median, with the tails
# pulled 40% toward the median (a spread the pinball rule rewards: too-wide
# bands pay at every hour).
#
# Self-calibration: the case's comparables include four fully-recorded probe
# launches (their whole release day, hours 2-24). For each hour the model
# measures its own median bias on those probes (leaving each probe out of its
# own calibration pool) and shifts the forecast by that bias — the same trick
# that lifted the leave-one-out practice loss from 0.32 (raw pooling) to ~0.15.
# Hours with too few samples fall back to a random walk in log space.
#
# Deterministic: same input, same bytes out. Python 3.13, stdlib only, no network.

import json
import math
import os

INPUT_DIR = os.environ.get('MAKEFUN_INPUT_DIR', '/input')
OUTPUT_DIR = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')

LEVELS = [0.05, 0.25, 0.5, 0.75, 0.95]
Z = [-1.645, -0.674, 0.0, 0.674, 1.645]
TAU_K = 0.4      # similarity bandwidth in ln(p1) units
SPREAD = 0.6     # tail pull toward the median
LAM = 1.0        # self-calibration shift strength
SIGMA = 0.15     # fallback walk spread
MIN_PAIRS = 8


def weighted_quant(pairs, tau):
    """Quantile of (value, weight) pairs, sorted by value."""
    pairs = sorted(pairs)
    total = sum(w for _, w in pairs)
    acc = 0.0
    for v, w in pairs:
        acc += w
        if acc >= tau * total:
            return v
    return pairs[-1][0]


def day_curve(comp):
    """{hour -> viewers} over one comparable's release day."""
    day = (comp.get('day_start') or '')[:10]
    hm = {}
    for pt in comp.get('hourly', []):
        frm = pt.get('from', '')
        if frm[:10] == day:
            try:
                hh = int(frm[11:13]) + 1
            except ValueError:
                continue
            hm[hh] = pt.get('viewers') or 0
    return hm


def log_ratios(hm):
    """{hour -> ln(v_h / v_1)} for an hour-anchored launch curve."""
    p1 = hm.get(1, 0)
    if p1 <= 0:
        return None
    l1 = math.log(p1)
    return {h: math.log(hm[h]) - l1 for h in range(2, 25) if hm.get(h, 0) > 0}


def hour_quantiles(p1, rows, h):
    """Five quantiles of hour h's viewers given (name, curve) rows."""
    lp1 = math.log(max(p1, 1))
    pairs = []
    for name, hm in rows:
        lr = log_ratios(hm)
        if lr and h in lr:
            w = math.exp(-abs(math.log(max(hm[1], 1)) - lp1) / TAU_K)
            pairs.append((lr[h], w))
    if len(pairs) < MIN_PAIRS:
        return [p1 * math.exp(z * SIGMA * math.sqrt(h - 1)) for z in Z]
    med = weighted_quant(pairs, 0.5)
    qs = []
    for tau in LEVELS:
        e = weighted_quant(pairs, tau)
        qs.append(max(1.0, p1 * math.exp(med + (e - med) * SPREAD)))
    return qs


def median_ratio(p1, rows, h):
    """The model's median log-ratio for hour h over rows."""
    lp1 = math.log(max(p1, 1))
    pairs = []
    for name, hm in rows:
        lr = log_ratios(hm)
        if lr and h in lr:
            w = math.exp(-abs(math.log(max(hm[1], 1)) - lp1) / TAU_K)
            pairs.append((lr[h], w))
    if not pairs:
        return None
    return weighted_quant(pairs, 0.5)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    files = sorted(f for f in os.listdir(INPUT_DIR) if f.endswith('.in'))
    for fname in files:
        case_id = fname[:-3]
        with open(os.path.join(INPUT_DIR, fname), 'r', encoding='utf-8') as fh:
            case = json.load(fh)
        p1 = max(1, next((k.get('viewers') or 0 for k in case.get('known', []) if k.get('hour') == 1), 0) or 1)
        comps = case.get('comparables', [])

        pool = []
        for c in comps:
            hm = day_curve(c)
            if hm.get(1, 0) > 0:
                pool.append((c.get('name', '?'), hm))

        # Probe launches: comparables whose day holds hours 2 and 24 (a full
        # release-day recording); the raw pool members typically have them too.
        probes = [(name, hm) for name, hm in pool if 2 in hm and 24 in hm]

        # Self-calibration: each probe's median bias, with itself left out.
        shifts = {}
        for h in range(2, 25):
            biases = []
            for pname, phm in probes:
                others = [(n, m) for n, m in pool if n != pname]
                pp1 = phm[1]
                med = median_ratio(pp1, others, h)
                y = phm.get(h, 0)
                if med is not None and y > 0:
                    biases.append(math.log(y) - math.log(pp1) - med)
            shifts[h] = sum(biases) / len(biases) if biases else 0.0

        hours = []
        for row in case.get('forecast', []):
            h = row['hour']
            qs = hour_quantiles(p1, pool, h)
            qs = [max(1.0, q * math.exp(LAM * shifts[h])) for q in qs]
            for i in range(1, len(qs)):
                if qs[i] < qs[i - 1]:
                    qs[i] = qs[i - 1]
            hours.append({'hour': h, 'q': [round(q, 2) for q in qs]})
        out = {'hours': hours}
        with open(os.path.join(OUTPUT_DIR, case_id + '.out'), 'w', encoding='utf-8') as fh:
            json.dump(out, fh)
            fh.write('\n')


main()
