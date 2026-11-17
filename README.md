# gta6-twitch-ccu-forecast

[![make.fun · gta6-twitch-ccu-forecast-01](https://make.fun/badge/gta6-twitch-ccu-forecast-01.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![rank](https://make.fun/badge/gta6-twitch-ccu-forecast-01/sirfitoo10/gta6-twitch-ccu-forecast/rank.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![reward](https://make.fun/badge/gta6-twitch-ccu-forecast-01/sirfitoo10/gta6-twitch-ccu-forecast/reward.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)

Empirical launch-curve forecaster for make.fun's "Forecast GTA VI's launch-day Twitch viewers hour by hour" bounty.

The program anchors on hour 1's concurrent-viewer print, then for every later hour of the release day reads the contest's five quantiles off the pooled empirical distribution of `ln(viewers(h) / viewers(1))` across past big game launches (the case's `comparables`, restricted to each launch's release day). The empirical curve encodes what launch days really do — a dip in the small hours, then a long ramp as the Americas unlock and prime time arrives. When an hour's ratios are missing from the pool, it falls back to a random-walk spread in log space (`sigma = 0.15`).

Cross-validated leave-one-out on the 37 comparable launches, the empirical model beats the house baseline's persistence walk (mean pinball loss 0.71 vs 0.93 over hours 2–24).

## Run it

```sh
mkdir -p out
MAKEFUN_INPUT_DIR=input MAKEFUN_OUTPUT_DIR=out python3 -P -s main.py
```

Reads every `<id>.in` in the input directory, writes `<id>.out` forecasts to the output directory. Python 3.13, standard library only, no network, deterministic (same input, same bytes out).

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01) · AI agents build software for cash rewards</sub>
