---
name: moonsighting
description: Use this skill when the user asks about moon sighting, hilal visibility, start or end of Ramadan, start of Shawwal or any Islamic month, crescent visibility, whether the moon can be seen tonight, Eid al-Fitr date, Islamic calendar month determination, or anything about the Islamic lunar calendar in Italy or Torino specifically.
argument-hint: [YYYY-MM-DD] [--scan]
allowed-tools: Bash
---

# Moonsighting — Islamic Hilal Visibility Calculator

This skill calculates whether the new crescent moon (hilal) is visible for a given date and
location, using the Shaukat Q-factor criterion. Defaults to **Torino, Italy**.

For full formula details, zone definitions, key URLs, and the Torino case study, see
[knowledge.md](knowledge.md).

## When invoked

1. **Parse arguments** from `$ARGUMENTS`:
   - Date in `YYYY-MM-DD` format (required — ask user if not provided)
   - `--scan` flag (optional) to also show the afternoon altitude table
   - Location args if user specifies a different city (use defaults otherwise)

2. **Ensure `ephem` is available:**
   ```bash
   python3 -c "import ephem" 2>/dev/null || (
     python3 -m venv /tmp/moonvenv &&
     /tmp/moonvenv/bin/pip install ephem --quiet
   )
   ```
   Use `/tmp/moonvenv/bin/python3` if system python lacks ephem.

3. **Run the calculation script:**
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/moonsighting_calc.py --date YYYY-MM-DD [--scan]
   # or if using venv:
   /tmp/moonvenv/bin/python3 ${CLAUDE_SKILL_DIR}/scripts/moonsighting_calc.py --date YYYY-MM-DD [--scan]
   ```
   Override defaults with `--lat`, `--lon`, `--elev`, `--tz`, `--location` if needed.

4. **Present results** in a clear table. Include:
   - Sunset and moonset times (local)
   - Window duration
   - Moon altitude at sunset and at Yallop best-sighting time
   - Q factor and Zone (A/B/C/D/E) with plain-language meaning
   - Practical verdict: which day does the Islamic month start?

5. **Contextualise for Torino** (when relevant):
   - Mention Po Valley haze as an aggravating factor for near-horizon sightings
   - If elongation < 15°, warn that pre-sunset binocular searching is dangerous
   - Note that the practical sweet spot is around sunset, not the Yallop time, since
     the moon drops ~1°/5 min and altitude at sunset is higher than at the Yallop time

6. **Optional: cross-check moonsighting.com** by fetching the relevant month page.
   URL pattern: `https://www.moonsighting.com/{YEAR_AH}{MONTH_CODE}.html`
   See [knowledge.md](knowledge.md) for month codes and other URL patterns.

## Script arguments reference

| Arg | Default | Description |
|-----|---------|-------------|
| `--date` | (required) | Date to check: `YYYY-MM-DD` |
| `--lat` | 45.0703 | Latitude (°N) |
| `--lon` | 7.6869 | Longitude (°E) |
| `--elev` | 239 | Elevation (metres) |
| `--tz` | 1.0 | UTC offset (hours); CET=1, CEST=2 |
| `--location` | "Torino, Italy" | Display name |
| `--scan` | off | Print 5-min altitude table (3h before sunset → moonset) |
