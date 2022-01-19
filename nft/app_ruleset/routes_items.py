from fastapi import APIRouter, Header, Depends, HTTPException, Response, status

import nftables

router = APIRouter()

@router.get("/")
async def get_nft_ruleset():
    ruleset = nftables.get_nft_ruleset()
    return ruleset
    

