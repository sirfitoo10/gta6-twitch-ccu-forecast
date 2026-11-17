# gta6-twitch-ccu-forecast-01 entry: empirical launch-day curve forecaster.
#
# Idea: hour-1's print anchors the day. For each hour h = 2..24 we take the
# pooled distribution, across past big game launches (the case's comparables,
# restricted to points on their release day), of ln(viewers(h) / viewers(1)),
# and read the contest's quantiles straight off that empirical distribution:
#
#   q_tau(h) = p1 * exp( emp_quantile_tau( ln(v_h / v_1) ) )
#
# The empirical curve already encodes what launch days really do: a dip in the
# small hours, then a long ramp as the Americas unlock and prime time arrives.
# If a launch day's own points are missing for an hour, that hour's ratios are
# just absent from the pool (more data lands as the final's comparables list
# the practice launches too). No randomness: same input, same bytes out.

import json
import math
import os
import re

INPUT_DIR = os.environ.get('MAKEFUN_INPUT_DIR', '/input')
OUTPUT_DIR = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')

LEVELS = [0.05, 0.25, 0.5, 0.75, 0.95]
Z = [-1.645, -0.674, 0.0, 0.674, 1.645]
SIGMA = 0.15  # fallback walk spread when the pool is thin

MAX_Q = 1e9
MIN_Q = 1e-9


def empirical_quantile(values, tau):
    """Linear interpolation on the sorted sample (type 7)."""
    v = sorted(values)
    if not v:
        return None
    idx = tau * (len(v) - 1)
    lo = int(math.floor(idx))
    frac = idx - lo
    if lo >= len(v) - 1:
        return v[-1]
    return v[lo] + frac * (v[lo + 1] - v[lo])


def launch_day_curve(comp):
    """{hour -> viewers} for one comparable's release day (UTC day of day_start)."""
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


def pooled_log_ratios(comparables):
    """{h -> [ln(v_h / v_1) across launches]} for h = 2..24."""
    logs = {h: [] for h in range(2, 25)}
    for comp in comparables:
        hm = launch_day_curve(comp)
        p1 = hm.get(1, 0)
        if p1 <= 0:
            continue
        l1 = math.log(p1)
        for h in range(2, 25):
            vh = hm.get(h, 0)
            if vh > 0:
                logs[h].append(math.log(vh) - l1)
    return logs


def clamp(x):
    return min(MAX_Q, max(1.0, x))


def forecast_case(case):
    known = {}
    for k in case.get('known', []):
        if k.get('hour') == 1:
            known = k
    p1 = max(1, known.get('viewers') or 1)
    logs = pooled_log_ratios(case.get('comparables', []))
    hours = []
    for row in case.get('forecast', []):
        h = row['hour']
        qs = []
        for tau, z in zip(LEVELS, Z):
            e = empirical_quantile(logs.get(h, []), tau)
            if e is None:
                e = z * SIGMA * math.sqrt(h - 1)
            qs.append(clamp(round(p1 * math.exp(e), 2)))
        # enforce monotone non-decreasing
        for i in range(1, len(qs)):
            if qs[i] < qs[i - 1]:
                qs[i] = qs[i - 1]
        hours.append({'hour': h, 'q': qs})
    return {'hours': hours}


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    files = sorted(f for f in os.listdir(INPUT_DIR) if f.endswith('.in'))
    for fname in files:
        case_id = fname[:-3]
        with open(os.path.join(INPUT_DIR, fname), 'r', encoding='utf-8') as fh:
            case = json.load(fh)
        out = forecast_case(case)
        with open(os.path.join(OUTPUT_DIR, case_id + '.out'), 'w', encoding='utf-8') as fh:
            json.dump(out, fh)
            fh.write('\n')


main()
