import logging
import azure.functions as func
import io,json
import pandas

def main(userRequest: func.HttpRequest,cfrsFile : func.InputStream) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    cbrs_predictions = pandas.read_csv(io.BytesIO(cfrsFile.read()),index_col='user_id')
    #
    #
    #
    req_body = userRequest.get_json()
    logging.info(f"the body {req_body} -- {type(req_body)}")
    user_id = req_body.get('user_id')
    result = cbrs_predictions.loc[user_id][0]
    #
    #
    #
    theFiveRecommendedArticles = {}
    theFiveRecommendedArticles['description'] = "recommended articles by cfrs"
    theFiveRecommendedArticles['result'] = str(result) #"rien pour le moment"
    theFiveRecommendedArticles = json.dumps(theFiveRecommendedArticles)
    return func.HttpResponse(theFiveRecommendedArticles,mimetype='text/json')
