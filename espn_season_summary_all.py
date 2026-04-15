import requests
import csv
import time
from datetime import date, timedelta

LEAGUE_ID = 167689
SEASON = 2026
TOTAL_PERIODS = 187

BASE_DATE = date(2026, 3, 25)
DAY_ABBREVS = ['M', 'T', 'W', 'TH', 'F', 'SA', 'SU']

def period_date(period):
    return BASE_DATE + timedelta(days=period - 1)

def day_name(d):
    return DAY_ABBREVS[d.weekday()]

def fetch_league(period):
    """
    Fetch the full league snapshot for a scoring period.
    This should return all teams, so we can summarize every team
    from one request instead of 12 separate requests.
    """
    url = (
        f'https://lm-api-reads.fantasy.espn.com/apis/v3/games/flb'
        f'/seasons/{SEASON}/segments/0/leagues/{LEAGUE_ID}'
    )
    headers = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'}
    params = [('view', 'mRoster'), ('scoringPeriodId', period)]
    r = requests.get(url, params=params, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()

def team_period_summary(team, period):
    """
    Return (batter_fpts, pitcher_fpts, gs, total) for one team.
    Active batters: slot IDs 0 to 12
    Active pitchers: slot ID 13
    Exclude bench (16) and IL (17, 18, 19)
    """
    entries = team.get('roster', {}).get('entries', [])

    batter_fpts = 0.0
    pitcher_fpts = 0.0
    gs = 0

    for entry in entries:
        slot_id = entry.get('lineupSlotId', 16)

        # Skip inactive slots
        if slot_id in (16, 17, 18, 19):
            continue

        pm = entry.get('playerPoolEntry', {})
        player = pm.get('player', {})

        is_pitcher = slot_id == 13
        is_batter = 0 <= slot_id <= 12

        if not (is_pitcher or is_batter):
            continue

        stat_entry = None
        for s in player.get('stats', []):
            if s.get('scoringPeriodId') == period and s.get('statSplitTypeId') == 5:
                stat_entry = s
                break

        fpts = float(stat_entry['appliedTotal']) if stat_entry else 0.0
        raw = stat_entry.get('stats', {}) if stat_entry else {}

        if is_pitcher:
            pitcher_fpts += fpts
            gs += int(float(raw.get('33', raw.get(33, 0))))
        else:
            batter_fpts += fpts

    return round(batter_fpts, 2), round(pitcher_fpts, 2), gs, round(batter_fpts + pitcher_fpts, 2)

def build_team_map(data):
    """
    Build {team_id: team_object} from the league payload.
    """
    teams = data.get('teams', [])
    return {team.get('id'): team for team in teams if team.get('id') is not None}

def main():
    rows = []

    # CSV columns: first 3 stay the same, then 4 columns per team
    fieldnames = ['Period', 'Date', 'Day']
    for team_id in range(1, 13):
        fieldnames.extend([
            f'Team {team_id} B',
            f'Team {team_id} P',
            f'Team {team_id} Starts',
            f'Team {team_id} T',
        ])

    for period in range(1, TOTAL_PERIODS + 1):
        d = period_date(period)
        date_str = f"{d.month}/{d.day}"
        day_str = day_name(d)

        print(f"Period {period:2d} ({date_str} {day_str})...", end=' ', flush=True)

        try:
            data = fetch_league(period)
            team_map = build_team_map(data)

            row = {
                'Period': period,
                'Date': date_str,
                'Day': day_str,
            }

            for team_id in range(1, 13):
                team = team_map.get(team_id)
                if team is None:
                    b, p, gs, t = 0.0, 0.0, 0, 0.0
                else:
                    b, p, gs, t = team_period_summary(team, period)

                row[f'Team {team_id} B'] = b
                row[f'Team {team_id} P'] = p
                row[f'Team {team_id} Starts'] = gs
                row[f'Team {team_id} T'] = t

            rows.append(row)
            print("done")

        except Exception as e:
            print(f"ERROR: {e}")
            row = {'Period': period, 'Date': date_str, 'Day': day_str}
            for team_id in range(1, 13):
                row[f'Team {team_id} B'] = 0.0
                row[f'Team {team_id} P'] = 0.0
                row[f'Team {team_id} Starts'] = 0
                row[f'Team {team_id} T'] = 0.0
            rows.append(row)

        time.sleep(0.35)

    long_path = '/Users/peeky/Downloads/espn_season_long_by_team.csv'
    with open(long_path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)

    print(f"\nLong CSV → {long_path}")

if __name__ == '__main__':
    main()