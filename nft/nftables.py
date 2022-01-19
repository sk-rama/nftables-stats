import subprocess
import json
from typing import List, Dict

import app_config


def get_nft_ruleset():
    cmd = f'nft --json list ruleset'
    stdout_byte = subprocess.run(cmd, shell=True, check=True, capture_output=True)
    nft_ruleset = json.loads(stdout_byte.stdout.decode(encoding="utf-8"))
    app_config.set_ruleset(nft_ruleset)
    return nft_ruleset


def get_rules_from_ruleset(ruleset: Dict, chain_name:str) -> List:
    chain_list = []
    ruleset = ruleset['nftables']
    for item in ruleset:
        if str(list(item.keys())[0]) == 'rule':
            if item['rule']['chain'] == chain_name:
                # chain_list.append(str(list(item.keys())[0]))
                chain_list.append(item)
    return chain_list


def get_stats_from_chain(ruleset: Dict, chain_name:str) -> Dict:
    chain_list = get_rules_from_ruleset(ruleset, chain_name)
    expr_list = []
    for rule in chain_list:
        expr = rule['rule']['expr']
        expr_list.append(expr)
    list0 = expr_list[0]
    list1 = expr_list[1]
    packets_in = list0[2]['counter']['packets']
    bytes_in = list0[2]['counter']['bytes']
    packets_out = list1[2]['counter']['packets']
    bytes_out = list1[2]['counter']['bytes']
    return {'packets_in': packets_in, 'bytes_in': bytes_in, 'packets_out': packets_out, 'bytes_out': bytes_out}
        
        
