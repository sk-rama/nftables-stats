from functools import lru_cache
import json
import logging
from logging import config
from fastapi import FastAPI, Depends, Header, HTTPException, Request
from fastapi.exceptions import RequestValidationError, ValidationError, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
import string
import sys
import time
import uvicorn

import app_config
import app_chain.routes_items
import app_ruleset.routes_items
import helpers



sys.dont_write_bytecode = True

cfg = app_config.get_settings()


app = FastAPI(
    title = 'Nftables API for ICINGA2',
    license_info={
        'name': 'Apache 2.0',
        'url' : 'https://www.apache.org/licenses/LICENSE-2.0.html',
    },
    description = cfg.description,
    version = '0.8.2',
)

app.include_router(app_chain.routes_items.router, prefix="/chain", tags=['CHAIN'])
app.include_router(app_ruleset.routes_items.router, prefix="/ruleset", tags=['RULESET'])

@app.on_event("startup")
async def update_ruleset():
    helpers.update_nft_ruleset() 
    


@app.exception_handler(RequestValidationError)
@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    print(f"OMG! The client sent invalid data!: {exc}")
    exc_json = json.loads(exc.json())
    response = {"message": [], "data": None}

    for error in exc_json:
        response['message'].append(error['loc'][-1]+f": {error['msg']}")

    return JSONResponse(response, status_code=422)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response




if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
