#!/usr/bin/python3

import aiohttp
import asyncio
import argparse
import json
import pathlib
import signal
import subprocess
import datetime
import sys
import time
from functools import partial


start_time = time.time()

data_dir = '/var/spool/icinga2/nft_api'
url = 'http://192.168.221.195:8000/chain/{chain}?stats=true'

default_json = { 
    'packets_in': 0,
    'bytes_in': 0,
    'packets_out': 0,
    'bytes_out': 0,
}

return_code = { 0: [0, "OK"],
                1: [1, "WARNING"],
                2: [2, "CRITICAL"],
                3: [3, "UNKNOWN"]
              }
                 

def plugin_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--chain", dest="chain", type=str, default="chain-udp-50001", help="chain name") 
    parser.add_argument("-w", action="store", dest="warning", type=int, default=0, help="warning")
    parser.add_argument("-c", action="store", dest="critical", type=int, default=0, help="critical")
    parser.add_argument("-t", "--plugin_timeout", dest="timeout", type=int, default=10, help="Timeout in seconds for http GET")
    return parser.parse_args()


def handle_sigalrm(signum, frame, timeout=None):
    print(f'Plugin timed out after {timeout} seconds')
    sys.exit(3)


async def get_json(url: str):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                my_json = await resp.json()
                return my_json
    except Exception as e:
        print(f'Can not get json from url: {url}, exception: {e}')
        sys.exit(3)

def read_json_file(file):
    try:
        with open(file, "r") as read_file:
            data = json.load(read_file)
            return data
    except FileNotFoundError:
        write_json_to_file(default_json, file)
        read_json_file(file)
        return default_json
    except Exception as e:
        print(e)


def write_json_to_file(data, file):
    try:
        with open(file, "w") as write_file:
            json.dump(data, write_file)
    except FileNotFoundError:
        dirs = pathlib.Path(file).parent
        dirs.mkdir(parents=True, exist_ok=True)
        write_json_to_file(data, file)
    except Exception as e:
        print(e)


def get_return_status(cur_dict, old_dict):
    list_values = list(zip(cur_dict.values(), old_dict.values()))
    for pair in list_values:
        if pair[0] == pair[1]:
            output = f'CRITICAL - The number of packets or bytes does not increase'
            return_status = 2
            break
        if pair[0] > pair[1]:
            output = f'OK - The number of packets or bytes is increased'
            return_status = 0
        if pair[0] < pair[1]:
            output = f'UNKNOWN - The number of packets or bytes in previous check is bigger as actual check (probably reloaded nftables rules)'
            return_status = 3
            break
    return[return_status, output]


def get_performance_data(cur_dict, old_dict):
    # {'packets_in': 1930, 'bytes_in': 115784, 'packets_out': 1930, 'bytes_out': 123520}
    output = (
        f'\'packets_in\'={cur_dict["packets_in"]}c;;;; '
        f'\'bytes_in\'={cur_dict["bytes_in"]}B;;;; '
        f'\'packets_out\'={cur_dict["packets_out"]}c;;;; '
        f'\'bytes_out\'={cur_dict["bytes_out"]}B;;;; '
        f'\'delta_pakets_in\'={cur_dict["packets_in"] - old_dict["packets_in"]};;;; '
        f'\'delta_pakets_out\'={cur_dict["packets_out"] - old_dict["packets_out"]};;;; '
        f'\'delta_bytes_in\'={cur_dict["bytes_in"] - old_dict["bytes_in"]};;;; '
        f'\'delta_bytes_out\'={cur_dict["bytes_out"] - old_dict["bytes_out"]};;;; '
    )
    return output




        
        

if __name__ == "__main__":
    args = plugin_arguments()

    signal.signal(signal.SIGALRM, partial(handle_sigalrm, timeout=args.timeout))
    signal.alarm(args.timeout)

    cur_json = asyncio.run(get_json(url=url.format(chain=args.chain)))
    old_json = read_json_file(pathlib.Path(data_dir).joinpath(args.chain))

    return_status = get_return_status(cur_json, old_json)
   
    if return_status[0] == 3:
        write_json_to_file(cur_json, pathlib.Path(data_dir).joinpath(args.chain))
        print(return_status[1])
        sys.exit(3)

    # at the end always write json from api to file
    write_json_to_file(cur_json, pathlib.Path(data_dir).joinpath(args.chain))

    perf_data = get_performance_data(cur_json, old_json)
    print(f'{return_status[1]}|{perf_data}')
    # print("--- %s seconds ---" % (time.time() - start_time))
    sys.exit(return_status[0])
