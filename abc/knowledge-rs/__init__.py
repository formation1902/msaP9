import logging
import azure.functions as func
import pandas
import json
import io
from .sous_marin import RS_knowledge_based

def main(userRequest: func.HttpRequest,regionRS : func.InputStream,categoryRS:func.InputStream) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    category_top_articles = pandas.read_csv(io.BytesIO(categoryRS.read()),index_col='category_id')
    region_top_articles   = pandas.read_csv(io.BytesIO(regionRS.read()),index_col='region')
    #
    #
    #
    req_body = userRequest.get_json()
    try:
        region = int(req_body.get('region'))
    except:
        region = None
    try:
        user_pc = [int(e) for e in req_body.get('user_pc')]
    except:
        user_pc= []
    logging.info(f"\n\n------> region : {region}")
    logging.info(f"\n\n------> user_pc : {user_pc}")
    result = RS_knowledge_based(region_top_articles,category_top_articles,region=region,user_pc=user_pc)
    #
    #
    #
    theFiveRecommendedArticles = {}
    theFiveRecommendedArticles['description'] = "recommended articles by knowledge_rs"
    theFiveRecommendedArticles['result'] = str(result) #"rien pour le moment"
    theFiveRecommendedArticles = json.dumps(theFiveRecommendedArticles)
    return func.HttpResponse(theFiveRecommendedArticles,mimetype='text/json')
