import json
import os
import requests
import time
from datetime import date, timedelta
import gspread
from google.oauth2 import service_account

LEAGUE_ID = 167689
SEASON = 2026
TOTAL_PERIODS = 187

BASE_DATE = date(2026, 3, 25)
DAY_ABBREVS = ['M', 'T', 'W', 'TH', 'F', 'SA', 'SU']

SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID", "YOUR_SPREADSHEET_ID_HERE")


def period_date(period):
    return BASE_DATE + timedelta(days=period - 1)


def day_name(d):
    return DAY_ABBREVS[d.weekday()]


def fetch_league(period):
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
    entries = team.get('roster', {}).get('entries', [])

    batter_fpts = 0.0
    pitcher_fpts = 0.0
    gs = 0

    for entry in entries:
        slot_id = entry.get('lineupSlotId', 16)

        if slot_id in (16, 17, 18, 19):
            continue

        pm = entry.get('playerPoolEntry', {})
        player = pm.get('player', {})

        is_pitcher = slot_id == 13
        is_batter = 0 <= slot_id <= 12

        if not (is_pitcher or is_batter):
            continue

        fpts = 0.0
        player_gs = 0
        for s in player.get('stats', []):
            if s.get('scoringPeriodId') == period and s.get('statSplitTypeId') == 5:
                fpts += float(s.get('appliedTotal', 0))
                if is_pitcher:
                    raw = s.get('stats', {})
                    player_gs += int(float(raw.get('33', raw.get(33, 0))))

        if is_pitcher:
            pitcher_fpts += fpts
            gs += player_gs
        else:
            batter_fpts += fpts

    return round(batter_fpts, 2), round(pitcher_fpts, 2), gs, round(batter_fpts + pitcher_fpts, 2)


def build_team_map(data):
    teams = data.get('teams', [])
    return {team.get('id'): team for team in teams if team.get('id') is not None}


def main():
    rows = []

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
        date_str = f"{d.month}/{d.day}/{d.year}"
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

    creds_json = json.loads(os.environ["GOOGLE_CREDENTIALS"])
    creds = service_account.Credentials.from_service_account_info(
        creds_json, scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(SPREADSHEET_ID)
    ws = sh.sheet1
    ws.clear()
    ws.update([fieldnames] + [[row[f] for f in fieldnames] for row in rows],
              value_input_option='USER_ENTERED')

    print(f"\nGoogle Sheet updated → https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}")


if __name__ == '__main__':
    main()
