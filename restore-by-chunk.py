from datetime import datetime
from elasticsearch import Elasticsearch
from pathlib import Path
import json
import argparse

def do(args):
    """
    Look through indices in snapshot, chunk by so many indices, dumping
    snapshot payloads in the process. Uses a file from the snapshot status
    page.
    """

    data = json.load(open(args.file))['snapshots'][0]
    prefix = args.prefix
    snapshot_name = data['snapshot']
    indices = data['indices']
    partial = data['state'] != 'SUCCESS'
    chunk_limit = args.chunk
    renaming = args.renaming

    if prefix:
        indices = list(filter(lambda i: i.startswith(prefix), indices))

    # Get chunked indices
    chunks = [
        indices[x:x + chunk_limit]
        for x in range(0, len(indices), chunk_limit)
    ]

    # Build payload for chunk
    for i, chunk in enumerate(chunks, 1):
        name = f'{snapshot_name}-{prefix or ""}'
        file = Path(f'{name}-chunk-{i}.json')
        payload = {}

        payload['indices'] = ','.join(chunk)
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
        print(f'Chunk {i:4d} : {len(chunk):4d} => {file}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file')
    parser.add_argument('prefix', nargs='?', type=str)
    parser.add_argument('-c', '--chunk', default=50, type=int, help='indices per chunk')
    parser.add_argument('-r', '--renaming', default=True, action='store_false', help='turn off rename replacement')
    args = parser.parse_args()
    do(args)


if __name__ == '__main__':
    main()
