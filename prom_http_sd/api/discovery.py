#! /usr/bin/env python3

""" Module provides endpoint with discovered entities """

import logging
from fastapi import FastAPI, HTTPException
from prom_http_sd.models.targets import TargetsList
from prom_http_sd.models.discovery import RESULT_CACHE


app = FastAPI()


@app.get("/discovery")
async def get_discovery() -> TargetsList:
    """ Get discovered entities """
    try:
        return RESULT_CACHE.get_value()
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=f"Failed to get discovery cache - {exc}")
