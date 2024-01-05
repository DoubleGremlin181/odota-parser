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
        matches.match_id
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

    # Query OpenDota to convert get a replay url info
    print(f'Querying OpenDota for replay urls for {len(match_ids)} matches')
    odota_replays_url = 'https://api.opendota.com/api/replays'
    aggregated_response = []
    for match_id_chunk in [match_ids[i:i + 5] for i in range(0, len(match_ids), 5)]:
        params = {'match_id': match_id_chunk}
        chunked_response = requests.get(odota_replays_url, params=params)
        aggregated_response.extend(chunked_response.json())

    # Generate urls
    print(f'Generating {len(match_ids)} urls')
    match_url_dict = {match["match_id"]: f'http://replay{match["cluster"]}.{"valve.net" if match["cluster"] != 236 else "wmsj.cn/570"}/570/{match["match_id"]}_{match["replay_salt"]}.dem.bz2' for match in aggregated_response}

    # Download demos
    print(f'Downloading {len(match_url_dict)} demos')
    if not os.path.exists('raw'):
        os.mkdir('raw')

    for match_id, match_url in match_url_dict.items():
        if not os.path.exists(f'raw/{match_id}.dem'):
            print(f'Downloading {match_url}')
            subprocess.call(f'curl {match_url} | bunzip2 > raw/{match_id}.dem', shell=True)
        else:
            print(f'Skipping {match_url}')

    # Parse demos
    print(f'Parsing {len(match_url_dict)} demos')
    if not os.path.exists('parsed'):
        os.mkdir('parsed')

    for match_id in match_url_dict.keys():
        if not os.path.exists(f'parsed/{match_id}.txt'):
            print(f'Parsing {match_id}')
            subprocess.call(f'curl localhost:5600 --data-binary "@raw/{match_id}.dem" > parsed/{match_id}.txt', shell=True)
        else:
            print(f'Skipping {match_id}')

    print('Completed tournament demo parser')


if __name__ == '__main__':
    # Example usage: python parse_tournament.py --league-id 15739 --min-start-time 2023-09-22T07:00:00.000Z
    parser = argparse.ArgumentParser(description='Download and parse tournament demos')
    parser.add_argument('--league-id', help='OpenDota League ID to query for matches', required=True)
    parser.add_argument('--min-start-time', help='Minimum start time for matches', required=True)
    args = parser.parse_args()
    main(args.league_id, args.min_start_time)
