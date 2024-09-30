import g4f
import traceback
from typing import Union

from fastapi import FastAPI, HTTPException, Request
import jsons
from mangum import Mangum

from types_inputs import *
from myNumberFunction.starlette.middleware.cors import CORSMiddleware
from myNumberFunction.starlette.responses import JSONResponse

app = FastAPI(title="My Number Function", description="This is a simple API to perform some math operations")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)




@app.middleware("http")
async def add_process_time_header(request, call_next):
    


@app.get("/")
def read_root()->read_root_response:
    return read_root_response(message="Hello World")

