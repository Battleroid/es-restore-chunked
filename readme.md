# es-restore-chunked

If you're using this, it's because today is not a good day. Restoring a huge snapshot won't likely be feasible (or it's just plain not working). This takes a status blob from the snapshot and uses it to chunk by day. Giving you payloads for each day which makes restoring doable. Complement this with a repo that has higher recovery timeouts to ensure its success.

## Preparation

You'll need to grab the status JSON blob from one of the snapshot statuses. e.g.:

```
$ curl -u username https://localhost:9200/_snapshot/repo/20180511 > status.json
```

You **do not** want the full `_status`, it is far too detailed. We only need the listing of what's in it, the snapshot name, and whether it's partial or not.

## restore-by-day Usage

```
usage: restore-by-day.py [-h] [-r] file [prefix]

positional arguments:
  file
  prefix

optional arguments:
  -h, --help      show this help message and exit
  -r, --renaming  turn off rename replacement
```

### Example Usage

```
$ python restore-by-day.py status.json "logstash-example-"
2018.04.11 :   21 => 20180511-2018.04.11.json
2018.04.12 :   24 => 20180511-2018.04.12.json
2018.04.13 :   24 => 20180511-2018.04.13.json
2018.04.14 :   24 => 20180511-2018.04.14.json
2018.04.15 :   24 => 20180511-2018.04.15.json
2018.04.16 :   24 => 20180511-2018.04.16.json
2018.04.17 :   24 => 20180511-2018.04.17.json
2018.04.18 :   24 => 20180511-2018.04.18.json
2018.04.19 :   24 => 20180511-2018.04.19.json
2018.04.20 :   24 => 20180511-2018.04.20.json
2018.04.21 :   24 => 20180511-2018.04.21.json
2018.04.22 :   24 => 20180511-2018.04.22.json
2018.04.23 :   24 => 20180511-2018.04.23.json
2018.04.24 :   24 => 20180511-2018.04.24.json
2018.04.25 :   24 => 20180511-2018.04.25.json
2018.04.26 :   24 => 20180511-2018.04.26.json
2018.04.27 :   24 => 20180511-2018.04.27.json
2018.04.28 :   24 => 20180511-2018.04.28.json
2018.04.29 :   24 => 20180511-2018.04.29.json
2018.04.30 :   24 => 20180511-2018.04.30.json
2018.05.01 :   24 => 20180511-2018.05.01.json
2018.05.02 :   24 => 20180511-2018.05.02.json
2018.05.03 :   24 => 20180511-2018.05.03.json
2018.05.04 :   24 => 20180511-2018.05.04.json
2018.05.05 :   24 => 20180511-2018.05.05.json
2018.05.06 :   24 => 20180511-2018.05.06.json
2018.05.07 :   24 => 20180511-2018.05.07.json
2018.05.08 :   24 => 20180511-2018.05.08.json
2018.05.09 :   24 => 20180511-2018.05.09.json
2018.05.10 :    3 => 20180511-2018.05.10.json
```

You can then use each file to do a restore. For example

```
$ curl -d@20180511-2018.05.10.json -XPOST https://localhost:9200/_snapshot/backups/20180511/_restore
{
    "accepted": true
}
```

## restore-by-chunk Usage

```
usage: restore-by-chunk.py [-h] [-c CHUNK] [-r] file [prefix]

positional arguments:
  file
  prefix

optional arguments:
  -h, --help            show this help message and exit
  -c CHUNK, --chunk CHUNK
                        indices per chunk
  -r, --renaming        turn off rename replacement
```

### Example Usage

```
$ python restore-by-chunk.py status.json "logstash-example-"
Chunk    1 :   50 => 20180511-chunk-1.json
Chunk    2 :   50 => 20180511-chunk-2.json
Chunk    3 :   50 => 20180511-chunk-3.json
Chunk    4 :   50 => 20180511-chunk-4.json
Chunk    5 :   50 => 20180511-chunk-5.json
Chunk    6 :   50 => 20180511-chunk-6.json
Chunk    7 :   50 => 20180511-chunk-7.json
Chunk    8 :   50 => 20180511-chunk-8.json
Chunk    9 :   50 => 20180511-chunk-9.json
Chunk   10 :   50 => 20180511-chunk-10.json
Chunk   11 :   50 => 20180511-chunk-11.json
Chunk   12 :   50 => 20180511-chunk-12.json
Chunk   13 :   50 => 20180511-chunk-13.json
Chunk   14 :   46 => 20180511-chunk-14.json
```

The payloads can be used just the same as the `restore-by-day.py`'s output.
