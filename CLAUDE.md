# Power System HMI — Claude Instructions

## Workflow

Edit source files in `/Users/natnaeltsegai/Downloads/power-hmi/`, then sync live:

```bash
rsync -a --exclude='.git' \
  /Users/natnaeltsegai/Downloads/power-hmi/ \
  /usr/local/ignition/data/projects/power-hmi/

find /usr/local/ignition/data/projects/power-hmi -name "*.json" -exec touch {} \;
```

User hard-refreshes browser (`Cmd+Shift+R`). No zip import needed.

Then commit and push:
```bash
cd /Users/natnaeltsegai/Downloads/power-hmi && git add -A && git commit -m "..." && git push
```

## Project structure

```
com.inductiveautomation.perspective/
  page-config/config.json        ← routes: / /events /monitor /reports
  views/
    Dashboard/                   ← home: nav + generator column + SLD + stats
    Events/                      ← priority-colored alert list
    Monitor/                     ← 6-panel timeseries chart grid (24h stochastic data)
    Reports/                     ← search + type filters + downloadable report list
    Components/Nav/              ← shared navbar with onClick navigation
    Components/Generator Card/   ← reusable card, params-driven
    Components/SLD/              ← single line diagram, coord container 760×490
```

## Navigation

```json
"events": {
  "dom": {
    "onClick": {
      "config": { "script": "\tsystem.perspective.navigate('/events')" },
      "scope": "G",
      "type": "script"
    }
  }
}
```

Active tab: expression binding on `{page.props.path}`.

## Colors

| Token | Hex |
|---|---|
| Background | `#060B18` |
| Surface | `#0D1526` |
| Border | `#1B2B4B` |
| Blue | `#4F8EF7` |
| Green | `#22C55E` |
| Yellow | `#EAB308` |
| Red | `#EF4444` |
| Violet | `#A78BFA` |
| Cyan | `#06B6D4` |

## Known pending issues

- Generator card left-column text disappeared — needs fix
- Switchgear enclosure on SLD was flagged as inaccurate by user

## User rules

- Execute all bash commands without asking permission
- Write directly to Ignition project folder and touch files
- No zip imports
- Electrical engineering accuracy matters (ANSI 52, CT ratios, PR/PM, ground symbols)
