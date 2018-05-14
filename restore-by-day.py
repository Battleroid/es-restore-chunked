from datetime import datetime
from elasticsearch import Elasticsearch
from pathlib import Path
import re
import json
import argparse

def do(args):
    """
    Look through indices in snapshot, chunk by day, dumping snapshot
    payloads in the process. Uses a file from the snapshot status page.

    """
    # TODO: this should also be able to reach out to the snapshot page
    # itself, if we need it that is

    data = json.load(open(args.file))['snapshots'][0]
    prefix = args.prefix
    snapshot_name = data['snapshot']
    indices = data['indices']
    partial = data['state'] != 'SUCCESS'
    renaming = args.renaming

    if prefix:
        indices = list(filter(lambda i: i.startswith(prefix), indices))

    # Get days chunked
    days = {}
    for index in indices:

        # Extract date, use this to build list
        match = re.search(r'\d{4}\.\d{2}\.\d{2}', index)
        day = datetime.strptime(match.group(), '%Y.%m.%d')
        days.setdefault(day, set())
        days[day].add(index)

    # Build payloads with the indices chunked by day
    for day, indices in days.items():
        day_str = day.strftime('%Y.%m.%d')
        name = f'{snapshot_name}-{prefix or ""}'
        file = Path(f'{name}-{day_str}.json')
        payload = {}

        # payload['indices'] = ','.join(indices)
        payload['indices'] = f'{prefix}-{day_str}*'
        payload['ignore_unavailable'] = True
        payload['include_global_state'] = False
        payload['partial'] = partial
        payload['index_settings'] = {
            'index.number_of_replicas': 0,
        }

        if renaming:
            payload['rename_pattern'] = '(.+)'
            payload['rename_replacement'] = '$1_restored'

        file.write_text(json.dumps(payload, indent=2, sort_keys=True))
        print(f'{day_str} : {len(indices):4d} => {file}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file')
    parser.add_argument('prefix', nargs='?', type=str)
    parser.add_argument('-r', '--renaming', default=True, action='store_false', help='turn off rename replacement')
    args = parser.parse_args()
    do(args)


if __name__ == '__main__':
    main()
