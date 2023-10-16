"""Helper service for fetching triples."""
import os
from typing import Dict, List

import requests
from fastapi import APIRouter
from franz.openrdf.connect import ag_connect
from oteapi.models import TripleStoreConfig
from oteapi.triplestore import TripleStore

ROUTER = APIRouter(prefix="/triples")


@ROUTER.post("/fetch")
async def fetch_query_result(
    triplestore_config: TripleStoreConfig,
    sparql_query: str,
) -> Dict[str, List[str]]:
    """Connect to a triplestore and fetch mappings using sparql_query"""
    triplestore_instance = TripleStore(triplestore_config)
    result = triplestore_instance.get(sparql_query)
    return result


# Temporary function until decided on what to upload by default, or move it to oteapi-core
@ROUTER.post("/upload-ontology")
async def upload_ontology(
    triplestore_config: TripleStoreConfig,
    ontology_url: str,
    file_extention: str,
) -> Dict:
    """Connect to a triplestore and upload the ontology via access url"""
    response = requests.get(
        ontology_url, timeout=(3, 27)  # timeout in seconds (connect, read)
    )
    filename = triplestore_config.repositoryName + file_extention
    with open(filename, "wb") as file:
        file.write(response.content)
        file.close()
    with ag_connect(
        triplestore_config.repositoryName,
        host=triplestore_config.agraphHost,
        port=triplestore_config.agraphPort,
        user=triplestore_config.agraphUser,
        password=triplestore_config.agraphPassword.get_secret_value(),
    ) as conn:
        conn.addFile(filename)
        conn.close()
    if os.path.exists(filename):
        os.remove(filename)
    return {"RepositoryName": triplestore_config.repositoryName}
