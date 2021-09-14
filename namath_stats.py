import csv
import itertools
from sleeper_wrapper import League

# inefficient / assumes there's only ever one user for a user_id (or owner_id)
def get_user_by_owner_id(users, owner_id):
    owner = [u for u in users if u.get('user_id') == owner_id][0]
    return owner

# Our League ID
league = League('726470301583495168')

# Need both Users and Rosters
users = league.get_users()
rosters = league.get_rosters()

# ROSTER_ID, TEAM_NAME, OWNER_NAME, PF, PA
# That just does a running total of PF and PA for the current season.
with open('namath_stats.csv', 'w', newline='') as csvfile:
    fieldnames = ['roster_id', 'team_name', 'owner_name', 'pf', 'pa', 'wins', 'losses', 'ties']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    # Need the header row
    writer.writeheader()

    for r in rosters:
        roster_id = r['roster_id']

        owner_id = r['owner_id']
        user = get_user_by_owner_id(users, owner_id)
        team_name = user.get('metadata', {}).get('team_name') or f'Team {user.get("display_name")}'
        owner_name = user.get('display_name')

        # Just some format strings since they store the whole number and decimal part in separate fields.
        pf = f'{r["settings"]["fpts"]}' + '.' + f'{r["settings"]["fpts_decimal"]:02d}'
        pa = f'{r["settings"]["fpts_against"]}' + '.' + f'{r["settings"]["fpts_against_decimal"]:02d}'

        # Write each row to the CSV
        writer.writerow({'roster_id': roster_id, 'team_name': team_name, 'owner_name': owner_name, \
        'pf': pf, 'pa': pa, 'wins': r['settings']['wins'], 'losses': r['settings']['losses'], 'ties': r['settings']['ties']})
