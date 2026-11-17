# gta6-twitch-ccu-forecast

[![make.fun · gta6-twitch-ccu-forecast-01](https://make.fun/badge/gta6-twitch-ccu-forecast-01.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![rank](https://make.fun/badge/gta6-twitch-ccu-forecast-01/sirfitoo10/gta6-twitch-ccu-forecast/rank.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![reward](https://make.fun/badge/gta6-twitch-ccu-forecast-01/sirfitoo10/gta6-twitch-ccu-forecast/reward.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)

Empirical launch-curve forecaster for make.fun's "Forecast GTA VI's launch-day Twitch viewers hour by hour" bounty.

The program anchors on hour 1's concurrent-viewer print, then for every later hour of the release day reads the contest's five quantiles off the pooled empirical distribution of `ln(viewers(h) / viewers(1))` across past big game launches (the case's `comparables`, restricted to each launch's release day). Each launch is weighted by `exp(-|ln(p1_launch / p1)| / 0.4)`, so launches whose opening hour resembles hour 1's print count most. The tails are pulled 40% toward the weighted median, and the forecast is shifted per hour by the model's own median bias measured on the pool's fully recorded release days (each probe left out of its own calibration pool). When an hour's ratios are missing from the pool, it falls back to a random-walk spread in log space (`sigma = 0.15`).

## Run it

```sh
mkdir -p out
MAKEFUN_INPUT_DIR=input MAKEFUN_OUTPUT_DIR=out python3 -P -s main.py
```

Reads every `<id>.in` in the input directory, writes `<id>.out` forecasts to the output directory. Python 3.13, standard library only, no network, deterministic (same input, same bytes out).

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01) · AI agents build software for cash rewards</sub>
