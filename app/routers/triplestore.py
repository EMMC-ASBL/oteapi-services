"""Helper service for fetching triples."""
from typing import Dict, List
from fastapi import APIRouter
from oteapi.models import TripleStoreConfig
from oteapi.triplestore import TripleStore

ROUTER = APIRouter(prefix="/triples")


@ROUTER.post("/fetch")
async def fetch_query_result(
    triplestore_config: TripleStoreConfig,
    sparql_query: str,
) -> Dict[str, List[str]]:
    """Connect to a triplestore and fetch mappings using sparql_query 
    """
    triplestore_instance = TripleStore(triplestore_config)
    result = triplestore_instance.get(sparql_query)
    return result
