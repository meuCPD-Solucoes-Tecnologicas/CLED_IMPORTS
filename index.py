import json

import os
import re
import traceback
from typing import Union

from fastapi import FastAPI, HTTPException, Request

from mangum import Mangum


#imports necessarios para a funcao query_appsync
from botocore.auth import SigV4Auth
import requests
from botocore.awsrequest import AWSRequest
import botocore.session
import botocore
import boto3



from botocore.exceptions import ClientError

from types_inputs import *
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

app = FastAPI(title="CledImports", description="Api to imports data to cled APP ", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

variables_enviroment = {
    k: v for k, v in os.environ.items()
}


def get_secret():

    secret_name = "lambdas/IAM/cred"
    region_name = "sa-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    secret = get_secret_value_response['SecretString']
    return secret



secret=get_secret()
AWS_KEY = json.loads(secret)['AWS_KEY_IAM']
AWS_SECRET= json.loads(secret)['AWS_SECRET_IAM']







#necessary functions---------------------------------------------------------
def query_appsync(query: str, variables: dict = {}):
    """
        Esta função realiza uma consulta ao serviço AWS AppSync.

        Args:
            query (str): A consulta GraphQL a ser realizada.
            variables (dict, optional): Um dicionário contendo as variáveis para a consulta GraphQL. 
                                        Defaults to {}.

        Returns:
            Response: A resposta da consulta, incluindo o status da solicitação e os dados retornados.

        A função inicia uma sessão com o AWS, autentica a solicitação usando SigV4Auth e realiza a consulta.
        Se as variáveis forem fornecidas, elas são incluídas na consulta. A função imprime as variáveis, a solicitação e a resposta para fins de depuração.
    """

    session = botocore.session.Session()
    session.set_credentials(AWS_KEY, AWS_SECRET)
    
    
    
    sigv4 = SigV4Auth(session.get_credentials(), 'appsync',
                      variables_enviroment['AWS_REGION'])

    # endpoint = variables_enviroment['API_CLEDAPI_GRAPHQLAPIENDPOINTOUTPUT' ]
    try:
        nome_da_variavel_api = next(
            filter(lambda x: "_GRAPHQLAPIENDPOINTOUTPUT" in x, variables_enviroment.keys()))
        endpoint = variables_enviroment[nome_da_variavel_api]
        print(f"ENDPOINT: {endpoint}")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Erro ao obter endpoint do AppSync: "+str(e))

    if variables == {}:
        data = json.dumps({"query": query})
    else:
        data = json.dumps({"query": query, "variables": variables})
        print(f"VARIABLES: {variables}")

    headers = {
        "Content-Type": "application/json",
    }

    request = AWSRequest(
        method="POST",
        url=endpoint,
        data=data,
        headers=headers
    )

    sigv4.add_auth(request)

    prepared_request = request.prepare()

    print(f"REQUEST: {prepared_request.url}")

    response = requests.post(
        prepared_request.url,
        data=prepared_request.body,
        headers=prepared_request.headers
    )

    print(f"RESPONSE OF QUERY: {response.text}")

    if (response.json().get("data", None) is None and response.json().get("errors", None) is not None):
        raise HTTPException(
            status_code=500, detail="Erro ao executar consulta no AppSync:  "+str(response.json().get("errors", None)))

    return response


def get_schema_js(appId:str,env:str):
    #cliente boto3 s3
    amplify = boto3.client('amplify', region_name='sa-east-1', aws_access_key_id=AWS_KEY, aws_secret_access_key=AWS_SECRET)
    s3 = boto3.client('s3', region_name='sa-east-1', aws_access_key_id=AWS_KEY, aws_secret_access_key=AWS_SECRET)
    try:
        #obtem o schema do amplify
        deploymentBucket = amplify.get_backend_environment(appId=appId, environmentName=env)
        deploymentBucket = deploymentBucket['backendEnvironment']['deploymentArtifacts']
        
        #obtem o schema do s3 s3://$BUCKET_NAME/models/${APP_ID}apigraph/schema.js
        schema = s3.get_object(Bucket=deploymentBucket, Key=f"models/{appId}apigraph/schema.js")
        schema = schema['Body'].read().decode('utf-8')
        
        
        
        
        #retorna o schema
        return schema
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=traceback.format_exc())



    ...

@app.middleware("http")
async def add_process_time_header(request, call_next):

    #printa todas as variaveis de ambiente
    print("ENVIRONMENT VARIABLES:\n\n")
    print(variables_enviroment)
    print("\n\n-----------------------------------------------\n\n")


    # api_key = request.headers.get("x-api-key")
    # api_keys = ["12345"]
    # if api_key not in api_keys:
    #     return JSONResponse(status_code=403, content={"message": "Forbidden"})
    print("middleware")
    print(request.headers)
    dict_request = dict(request)
    # print(dict_request)
    response = await call_next(request)
    return response

@app.get("/")
def read_root():
    return {"Hello": "World"}

openapi_schema = app.openapi()
handler = Mangum(app)
