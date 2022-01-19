from fastapi import APIRouter, Header, Depends, HTTPException, Response, status
from typing import Optional


import app_config
import nftables

router = APIRouter()

@router.get("/ruleset")
async def get_ruleset():
    ruleset = app_config.get_ruleset()
    return ruleset


@router.get("/{chain}")
async def get_chain(chain: str, stats: Optional[bool] = False):
    ruleset = app_config.get_ruleset()
    if not stats:
        return nftables.get_rules_from_ruleset(ruleset, chain)
    else:
        return nftables.get_stats_from_chain(ruleset, chain)




