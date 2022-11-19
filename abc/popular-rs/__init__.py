import logging
import azure.functions as func
import json,io,pandas


# def main(userRequest: func.HttpRequest,popular_rs:func.InputStream) -> func.HttpResponse:
def main(userRequest: func.HttpRequest,popularRSfile: func.InputStream) -> func.HttpResponse:
    theFiveRecommendedArticles = {}
    theFiveRecommendedArticles['description'] = "recommended articles by popular_rs"
    result = str(pandas.read_csv(io.BytesIO(popularRSfile.read())).article_id.values.tolist())
    theFiveRecommendedArticles['result'] = result
    theFiveRecommendedArticles = json.dumps(theFiveRecommendedArticles)
    return func.HttpResponse(theFiveRecommendedArticles,mimetype='text/json')
    # return func.HttpResponse(result)