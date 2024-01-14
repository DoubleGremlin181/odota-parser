import argparse
import os
import requests
import subprocess


def main(league_id, min_start_time):
    print('Starting tournament demo parser')

    # Query OpenDota to get a list of match ids
    print(f'Querying OpenDota for match ids for league {league_id} after {min_start_time}')
    ODOTA_QUERY = f"""
        SELECT
        matches.match_id,
        matches.cluster,
        matches.replay_salt
        FROM matches
        JOIN match_patch using(match_id)
        JOIN leagues using(leagueid)
        WHERE TRUE
        AND (matches.leagueid = {league_id})
        AND matches.start_time >= extract(epoch from timestamp '{min_start_time}')
        ORDER BY matches.match_id NULLS LAST
        LIMIT 200
        """

    odota_explorer_url = 'https://api.opendota.com/api/explorer'
    params = {'sql': ODOTA_QUERY}
    response = requests.get(odota_explorer_url, params=params)
    match_ids = [match['match_id'] for match in response.json()['rows']]

    # Generate urls
    print(f'Generating {len(match_ids)} urls')
    match_url_dict = {match["match_id"]: f'http://replay{match["cluster"]}.{"valve.net" if match["cluster"] != 236 else "wmsj.cn/570"}/570/{match["match_id"]}_{match["replay_salt"]}.dem.bz2' for match in response.json()['rows']}

    # Download demos
    print(f'Downloading {len(match_url_dict)} demos')
    if not os.path.exists(f'{league_id}'):
        os.mkdir(f'{league_id}')
    if not os.path.exists(f'{league_id}/raw'):
        os.mkdir(f'{league_id}/raw')

    for match_id, match_url in match_url_dict.items():
        if not os.path.exists(f'{league_id}/raw/{match_id}.dem'):
            print(f'Downloading {match_url}')
            subprocess.call(f'curl -L {match_url} | bunzip2 > {league_id}/raw/{match_id}.dem', shell=True)
        else:
            print(f'Skipping {match_url}')

    # Parse demos
    print(f'Parsing {len(match_url_dict)} demos')
    if not os.path.exists(f'{league_id}/parsed'):
        os.mkdir(f'{league_id}/parsed')

    for match_id in match_url_dict.keys():
        if not os.path.exists(f'{league_id}/parsed/{match_id}.json'):
            print(f'Parsing {match_id}')
            subprocess.call(f'curl localhost:5600 --data-binary "@raw/{match_id}.dem" > {league_id}/parsed/{match_id}.json', shell=True)
        else:
            print(f'Skipping {match_id}')

    print('Completed tournament demo parser')


if __name__ == '__main__':
    # Example usage: python parse_tournament.py --league-id 15728 --min-start-time 2023-01-01T07:00:00.000Z
    parser = argparse.ArgumentParser(description='Download and parse tournament demos')
    parser.add_argument('--league-id', help='OpenDota League ID to query for matches', required=True)
    parser.add_argument('--min-start-time', help='Minimum start time for matches', required=True)
    args = parser.parse_args()
    main(args.league_id, args.min_start_time)
