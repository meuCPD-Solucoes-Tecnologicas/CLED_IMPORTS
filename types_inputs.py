from pydantic import BaseModel


class read_root_response(BaseModel):
    message: str

class read_item_response(BaseModel):
    item_id: int

class helloworld_response(BaseModel):
    message: str

class sum_request(BaseModel):
    
    n1: int
    n2: int

class sum_response(BaseModel):
    sum: int

class sum_params_response(BaseModel):
    sum: int

class sum_list_request(BaseModel):
    numList: list[int] | list[float] 

class sum_list_response(BaseModel):
    sum: int | float

class getGpt3Response_request(BaseModel):
    prompt: str

class getGpt3Response_response(BaseModel):
    response: str

class sum_vector_request(BaseModel):
    A: list[int] | list[float]
    B: list[int] | list[float]