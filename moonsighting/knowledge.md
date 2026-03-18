# Moonsighting Knowledge Base

## Key URLs

| Resource | URL pattern |
|----------|-------------|
| Month page | `https://www.moonsighting.com/{YEAR_AH}{MONTH_CODE}.html` |
| Visibility curve | `https://www.moonsighting.com/visibilitycurves/{YEAR_AH}{MONTH_CODE}_{M-D-YYYY}.gif` |
| FAQ (formulas) | `https://www.moonsighting.com/faq_ms.html` (sections 10.9, 15) |

**Islamic month codes:**
`muh` (Muharram), `sfr` (Safar), `rb1` (Rabi I), `rb2` (Rabi II),
`jm1` (Jumada I), `jm2` (Jumada II), `raj` (Rajab), `sha` (Sha'ban),
`ram` (Ramadan), `shw` (Shawwal), `dhu` (Dhul-Qi'dah), `dhj` (Dhul-Hijjah)

**Example:** Shawwal 1447 page → `https://www.moonsighting.com/1447shw.html`
**Example:** Visibility curve image → `https://www.moonsighting.com/visibilitycurves/1447shw_3-19-2026.gif`

---

## Shaukat Q-Factor Formula (FAQ section 10.9)

```
Best sighting time = sunset + (4/9) × (moonset − sunset)   [Yallop criterion]

Q = (ARCV − (11.8371 − 6.3226·WOC + 0.7319·WOC² − 0.1018·WOC³)) / 10

where:
  ARCV = moon_altitude − sun_altitude  (sun is negative after sunset, so this adds)
  WOC  = SD_arcmin × (1 − cos(elongation_rad))   [crescent width in arcminutes]
  SD_arcmin = moon.size / 2 / 60    (ephem gives angular diameter in arcseconds)
```

Evaluated at the Yallop best-sighting time, not at sunset.

---

## Visibility Zones

| Zone | Q range | Meaning |
|------|---------|---------|
| A | Q > 0.27 | Easily visible with naked eye |
| B | 0.27 ≥ Q > −0.024 | Visible under perfect conditions (naked eye) |
| C | −0.024 ≥ Q > −0.212 | Optical aid to **find** moon — naked eye may confirm once located |
| D | −0.212 ≥ Q > −0.48 | Visible with optical aid only — naked eye won't work |
| E | Q ≤ −0.48 | Not visible at all |

**Zone C vs D distinction**: In Zone C you can find it with binoculars, then a naked eye
may just see it. In Zone D the crescent is too faint for naked eye regardless.

**Fiqh implications:**
- Communities requiring unassisted naked-eye sighting → only Zone A/B count
- Communities accepting optical aid → Zone C/D may count
- Most European Muslim communities follow Saudi announcements or ECFR criteria

---

## Physical Limits

| Limit | Value | Meaning |
|-------|-------|---------|
| Danjon limit | 7.5° elongation | Below this the crescent physically cannot form |
| Naked-eye practical minimum | ~10.5° elongation | Below this naked-eye sighting is not credible |
| Minimum naked-eye age (credible) | ~17 h | Younger claims are extremely doubtful |
| Minimum aided-eye age (credible) | ~13.5 h | Younger claims are very doubtful |

---

## Torino, Italy — Default Parameters

| Parameter | Value |
|-----------|-------|
| Latitude | 45.0703°N |
| Longitude | 7.6869°E |
| Elevation | 239 m |
| Timezone | CET = UTC+1 (standard) / CEST = UTC+2 (summer, from last Sunday March) |

**Practical factors specific to Torino:**
- **Po Valley haze**: Torino sits in the Po Plain. Low-level haze is chronic and significantly
  dims objects near the horizon — worse than the Q factor alone implies.
- **Horizon**: Western horizon is largely open (Po Plain), but the Alps are visible to the
  NW/W; moonset directions around 270–280° are mostly over flat terrain.
- **Moon descent rate**: Near new moon, the moon drops roughly 1° per 5 minutes after sunset.
  This means altitude at the Yallop "best time" is typically ~3–4° below altitude at sunset.
- **Pre-sunset search**: If elongation < 15°, using binoculars before sunset is **dangerous**
  (sun is too close — permanent eye damage risk). At new moon elongation is usually 8–12°.

---

## Case Study: Shawwal 1447 AH — Torino, March 19, 2026

| Parameter | Value |
|-----------|-------|
| Conjunction | March 19 at 01:23 UT |
| Sunset Torino | 18:44 CET |
| Moonset Torino | 19:34 CET |
| Window | 49 minutes |
| Moon altitude at sunset | 6.74° |
| Moon azimuth at sunset | 270.2° (sun at 271.1°) |
| Moon altitude at Yallop time (19:06 CET) | 3.17° |
| Elongation | ~8.3° |
| Illumination | 0.65% |
| Moon age at sunset | 16.4 h |
| ARCV | 8.33° |
| WOC | 0.177 arcmin |
| Q factor | −0.24 |
| Zone | **D** — visible with optical aid only |
| Verdict | Shawwal starts **Saturday March 21** for naked-eye communities |

**Why Zone D despite 6.74° altitude at sunset:** The Yallop formula evaluates Q at the
*best sighting time* (19:06), when the moon is only 3.17° above the horizon — barely above
the Po Valley haze layer. The elongation of 8.3° also keeps the crescent razor-thin.

**Why not look before sunset:** Elongation stays at 5–8° all day (conjunction was at 01:23 UT).
The moon and sun travel together across the sky on this date. Pre-sunset binocular search is
dangerous and effectively impossible given the sky brightness vs. crescent contrast.

---

## Islamic Calendar Reference (1440s AH)

| AH Year | CE Year | Notes |
|---------|---------|-------|
| 1445 | 2023–2024 | Ramadan started ~March 11, 2024 |
| 1446 | 2024–2025 | Ramadan started ~March 1, 2025 |
| 1447 | 2025–2026 | Ramadan started ~February 28/March 1, 2026 |
| 1448 | 2026–2027 | Ramadan will start ~February 17/18, 2027 |

The Islamic year is ~11 days shorter than the Gregorian year, so Ramadan shifts ~11 days
earlier each year. The AH year can be approximated as: `AH ≈ (CE − 622) × (33/32)`.
