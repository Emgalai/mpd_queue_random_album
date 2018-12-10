#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import random
from pathlib import Path
import json

import mpd

# Default Server info, change these values to match yours.
HOST = "192.168.88.241"
PORT = "6600"
PASSWORD = None

__version__ = "1.0.0"
__author__ = "IbeeX"
__email__ = "ibrkanac@gmail.com"


def queue_random_album(client):

    cache_file = get_cache_file()
    cache = load_cache(cache_file)
    albums = client.list("album")
    while True:
        album_name = random.choice(albums)
        if not album_name:
            return
        if in_cache(len(albums), cache, album_name):
            print(f'{album_name}, album was queaed recently skipping...')
            continue
        break
    cache.append(album_name)
    save_cache(cache_file, cache)
    album = client.find("album", album_name)[0]
    print(f"{album['albumartist']}: {album['album']}, from {len(albums)} albums.")
    client.findadd("album", album_name)


def in_cache(no_albums, cache, album):
    found = False
    if album in cache:
        found = True
    percent = no_albums / 100 * 10
    if len(cache) > percent:
        cache.pop(0)
    return found


def get_cache_file():
    cache_dir = Path.home() / ".cache" / "mpdrandom"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / "cache.json"


def load_cache(cache_file):
    json_cache = ""
    if not cache_file.is_file():
        return []
    with cache_file.open() as f:
        json_cache = f.read()
    return json.loads(json_cache)


def save_cache(cache_file, cache):
    with cache_file.open(mode="w") as f:
        f.write(json.dumps(cache))


def main():
    # Arguments
    from argparse import ArgumentParser

    arguments = ArgumentParser(
        description="Pick and play a random album from " "the current playlist"
    )
    arguments.add_argument(
        "-n",
        "--no",
        type=int,
        dest="number_off_albums",
        default=1,
        help="number of albums to queue",
    )
    arguments.add_argument(
        "-p",
        "--port",
        dest="port",
        default=PORT,
        help="specify mpd's port (defaults to {})".format(PORT),
        metavar="PORT",
    )
    arguments.add_argument(
        "-u",
        "--host",
        dest="host",
        default=HOST,
        help="specify mpd's host (defaults to {})".format(HOST),
        metavar="HOST",
    )
    arguments.add_argument(
        "--password",
        dest="password",
        default=PASSWORD,
        help="specify mpd's password",
        metavar="PASSWORD",
    )
    args = arguments.parse_args()

    client = mpd.MPDClient()
    client.timeout = 10
    client.idletimeout = None
    client.connect(args.host, args.port)
    if args.password:
        client.password(args.password)
    for n in range(args.number_off_albums):
        queue_random_album(client)
    client.close()
    client.disconnect()
