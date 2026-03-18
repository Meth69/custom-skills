#!/usr/bin/env python3
"""
moonsighting_calc.py — Islamic hilal (crescent moon) visibility calculator.

Uses the Shaukat Q-factor criterion (based on Yallop 1997).
Defaults to Torino, Italy.

Usage:
  python moonsighting_calc.py --date 2026-03-19
  python moonsighting_calc.py --date 2026-03-19 --scan
  python moonsighting_calc.py --date 2026-03-19 --lat 41.9 --lon 12.5 --tz 1 --location "Rome, Italy"

Self-installs 'ephem' into /tmp/moonvenv if not available.
"""

import sys
import os

# --- Dependency bootstrap ---
try:
    import ephem
except ImportError:
    import subprocess
    venv = "/tmp/moonvenv"
    if not os.path.isdir(venv):
        subprocess.run([sys.executable, "-m", "venv", venv], check=True)
    subprocess.run([f"{venv}/bin/pip", "install", "ephem", "--quiet"], check=True)
    os.execv(f"{venv}/bin/python3", [f"{venv}/bin/python3"] + sys.argv)

import ephem
import math
import argparse
from datetime import timedelta


def fmt_time(ephem_date, tz_hours):
    """Convert ephem UTC date to local time string."""
    dt = ephem.Date(ephem_date).datetime() + timedelta(hours=tz_hours)
    return dt.strftime("%H:%M")


def zone_label(q):
    if q > 0.27:
        return "A", "Easily visible with naked eye"
    elif q > -0.024:
        return "B", "Visible under perfect conditions (naked eye)"
    elif q > -0.212:
        return "C", "Optical aid to find moon — naked eye may confirm once located"
    elif q > -0.48:
        return "D", "Visible with optical aid only — naked eye won't work"
    else:
        return "E", "Not visible at all"


def run(date_str, lat, lon, elev, tz, location, scan):
    obs = ephem.Observer()
    obs.lat = str(lat)
    obs.lon = str(lon)
    obs.elevation = elev
    obs.pressure = 1013

    sun  = ephem.Sun()
    moon = ephem.Moon()

    # --- Sunset ---
    obs.date = f"{date_str.replace('-', '/')} 12:00:00"
    obs.horizon = "-0:34"
    sunset_utc = obs.next_setting(sun)

    # --- Moonset ---
    moonset_utc = obs.next_setting(moon)

    window_min = int((moonset_utc - sunset_utc) * 24 * 60)

    # --- Conjunction (previous new moon) ---
    obs.horizon = "0"
    obs.date = sunset_utc
    conj_utc = ephem.previous_new_moon(sunset_utc)
    conj_local = fmt_time(conj_utc, tz)
    conj_date = ephem.Date(conj_utc).datetime()

    # --- Moon at sunset ---
    obs.date = sunset_utc
    moon.compute(obs)
    sun.compute(obs)

    moon_alt_s  = math.degrees(moon.alt)
    moon_az_s   = math.degrees(moon.az)
    sun_az_s    = math.degrees(sun.az)
    elong_s     = math.degrees(ephem.separation(moon, sun))
    illum_s     = moon.phase
    age_h       = (sunset_utc - conj_utc) * 24

    # --- Yallop best sighting time ---
    best_utc = sunset_utc + (moonset_utc - sunset_utc) * 4 / 9
    obs.date = best_utc
    moon.compute(obs)
    sun.compute(obs)

    moon_alt_b = math.degrees(moon.alt)
    sun_alt_b  = math.degrees(sun.alt)
    elong_b    = math.degrees(ephem.separation(moon, sun))

    ARCV = moon_alt_b - sun_alt_b
    SD_arcmin = moon.size / 2 / 60.0
    WOC = SD_arcmin * (1 - math.cos(math.radians(elong_b)))
    Q = (ARCV - (11.8371 - 6.3226 * WOC + 0.7319 * WOC**2 - 0.1018 * WOC**3)) / 10

    zone_letter, zone_desc = zone_label(Q)

    # --- Print report ---
    print(f"\n{'='*60}")
    print(f"  Hilal Visibility Report")
    print(f"  {location}  |  {date_str}")
    print(f"{'='*60}")

    conj_date_str = ephem.Date(conj_utc).datetime().strftime("%b %d at %H:%M UT")
    print(f"\n  Conjunction (new moon):  {conj_date_str}")
    print(f"\n  {'Sunset:':<28} {fmt_time(sunset_utc, tz)}")
    print(f"  {'Moonset:':<28} {fmt_time(moonset_utc, tz)}")
    print(f"  {'Window after sunset:':<28} {window_min} min")

    print(f"\n  --- Moon at sunset ({fmt_time(sunset_utc, tz)}) ---")
    print(f"  {'Altitude:':<28} {moon_alt_s:.2f}°")
    print(f"  {'Azimuth:':<28} {moon_az_s:.1f}°  (sun at {sun_az_s:.1f}°)")
    print(f"  {'Elongation:':<28} {elong_s:.2f}°")
    print(f"  {'Illumination:':<28} {illum_s:.2f}%")
    print(f"  {'Moon age:':<28} {age_h:.1f} h")

    if elong_s < 15:
        print(f"\n  ⚠  Elongation only {elong_s:.1f}° — pre-sunset binocular search")
        print(f"     is DANGEROUS (sun too close). Do not scan before sunset.")

    print(f"\n  --- Yallop best sighting time ({fmt_time(best_utc, tz)}) ---")
    print(f"  {'Moon altitude:':<28} {moon_alt_b:.2f}°")
    print(f"  {'Sun altitude:':<28} {sun_alt_b:.2f}° (below horizon)")
    print(f"  {'ARCV:':<28} {ARCV:.2f}°")
    print(f"  {'WOC:':<28} {WOC:.4f} arcmin")
    print(f"  {'Q factor:':<28} {Q:.4f}")
    print(f"  {'Zone:':<28} {zone_letter} — {zone_desc}")

    # Verdict
    print(f"\n  --- Verdict ---")
    if zone_letter in ("A", "B"):
        print(f"  Moon SHOULD be visible with the naked eye.")
        print(f"  The new Islamic month begins TOMORROW (next day after {date_str}).")
    elif zone_letter == "C":
        print(f"  Moon requires binoculars to locate, but naked eye may confirm.")
        print(f"  For communities requiring naked-eye sighting: month starts in 2 days.")
        print(f"  For communities accepting optical aid: month may start tomorrow.")
    elif zone_letter == "D":
        print(f"  Moon is only visible with optical aid. Naked-eye sighting not possible.")
        print(f"  The new Islamic month begins the DAY AFTER TOMORROW.")
    else:
        print(f"  Moon is not visible at all tonight.")
        print(f"  The new Islamic month begins the DAY AFTER TOMORROW.")
    print()

    # --- Optional afternoon scan ---
    if scan:
        print(f"  --- Afternoon altitude scan (5-min intervals) ---")
        print(f"  {'Time':<10} {'Moon Alt':>9} {'Sun Alt':>9} {'Elongation':>11}  Sky")
        print(f"  {'-'*60}")

        start_utc = sunset_utc - (3.0 / 24.0)
        end_utc   = moonset_utc + (5.0 / (24 * 60))
        t = start_utc
        step = 5.0 / (24 * 60)

        while t <= end_utc:
            obs.date = t
            moon.compute(obs)
            sun.compute(obs)

            m_alt = math.degrees(moon.alt)
            s_alt = math.degrees(sun.alt)
            el    = math.degrees(ephem.separation(moon, sun))

            if s_alt > 6:
                sky = "daytime"
            elif s_alt > 0:
                sky = "civil twilight (sun up)"
            elif s_alt > -6:
                sky = "civil twilight"
            elif s_alt > -12:
                sky = "nautical twilight"
            else:
                sky = "dark"

            marker = ""
            if abs(t - sunset_utc) < step / 2:
                marker = " ◀ sunset"
            elif abs(t - best_utc) < step / 2:
                marker = " ◀ Yallop best"
            elif abs(t - moonset_utc) < step / 2:
                marker = " ◀ moonset"

            print(f"  {fmt_time(t, tz):<10} {m_alt:>8.2f}° {s_alt:>8.2f}° {el:>10.2f}°  {sky}{marker}")
            t += step
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Islamic hilal (crescent moon) visibility calculator."
    )
    parser.add_argument("--date",     required=True, help="Date to check: YYYY-MM-DD")
    parser.add_argument("--lat",      type=float, default=45.0703, help="Latitude (default: Torino)")
    parser.add_argument("--lon",      type=float, default=7.6869,  help="Longitude (default: Torino)")
    parser.add_argument("--elev",     type=int,   default=239,     help="Elevation in metres (default: 239)")
    parser.add_argument("--tz",       type=float, default=1.0,     help="UTC offset in hours (default: 1 = CET)")
    parser.add_argument("--location", type=str,   default="Torino, Italy", help="Display name")
    parser.add_argument("--scan",     action="store_true", help="Print 5-min afternoon altitude table")
    args = parser.parse_args()

    run(args.date, args.lat, args.lon, args.elev, args.tz, args.location, args.scan)


if __name__ == "__main__":
    main()
