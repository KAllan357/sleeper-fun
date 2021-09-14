import csv
import itertools
from sleeper_wrapper import League

# inefficient / assumes there's only ever one roster for a roster_id
def get_roster_owner_by_roster_id(rosters, roster_id):
    roster = [r for r in rosters if r.get('roster_id') == roster_id][0]
    return roster['owner_id']

# inefficient / assumes there's only ever one user for a user_id (or owner_id)
def get_user_by_owner_id(users, owner_id):
    owner = [u for u in users if u.get('user_id') == owner_id][0]
    return owner

# Our League ID
league = League("726470301583495168")

# Need both Users and Rosters
users = league.get_users()
rosters = league.get_rosters()

# Assumptions / Notes:
#   Get Matchups returns 16 matchups - one per team.
#   An actual matchup is between two teams which share a matchup_id.
#   Individual matchups have a roster_id which can be used in the Get Rosters API.
#   owner_id and user_id are interchangeable / the same.
#   matchup -> roster_id -> owner_id -> team name


# The other script should pipe weekly matchup:  GAME_ID (or MATCHUP_ID) YEAR, WEEK, HOME_OWNER, HOME_TEAM,
# AWAY_OWNER, AWAY_TEAM, HOME_TEAM_SCORE, AWAY_TEAM_SCORE

year = 2021

# Open a CSV, iterate the grouped matchup pairs, and write dicts
with open('matchups.csv', 'w', newline='') as csvfile:
    fieldnames = ['matchup_id', 'year', 'week', 'home_owner', 'home_team', 'away_owner', 'away_team', 'home_team_score', 'away_team_score']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    # Need the header row
    writer.writeheader()

    for n in range(1,19):
        # Get Matchups by the WEEK_NUM
        week_n_matchups = sorted(league.get_matchups(n), key=lambda x: x.get('matchup_id'))
        # Group the matchups into their pairs based on their matchup_id
        grouped_matchups = itertools.groupby(week_n_matchups, lambda x: x.get('matchup_id'))

        # Iterate the generator of grouped matchup pairs
        for key, matchup in grouped_matchups:
            # Materialize the generator into a list and make a bold assumption:
            # Home team is the first entry, Away team is in the second.
            mu = list(matchup)
            home_team_owner_id = get_roster_owner_by_roster_id(rosters, mu[0].get('roster_id'))
            away_team_owner_id = get_roster_owner_by_roster_id(rosters, mu[1].get('roster_id'))

            home_team_user = get_user_by_owner_id(users, home_team_owner_id)
            away_team_user = get_user_by_owner_id(users, away_team_owner_id)

            ho = home_team_user.get('display_name')
            home_team = home_team_user.get('metadata', {}).get('team_name') or f'Team {home_team_user.get("display_name")}'

            ao = away_team_user.get('display_name')
            away_team = away_team_user.get('metadata', {}).get('team_name') or f'Team {away_team_user.get("display_name")}'

            ht_score = mu[0].get('points')
            at_score = mu[1].get('points')

            # Write each row to the CSV
            writer.writerow({'matchup_id': mu[0].get('matchup_id'), 'year': year, 'week': n, 'home_owner': ho, 'home_team': home_team, \
                'away_owner': ao, 'away_team': away_team, 'home_team_score': ht_score, 'away_team_score': at_score})
