from typing import Union
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def read_root():
    return {"Le gestionnaire du cache repond et vous salue !!!"}

@app.get("/handle_new_user/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.get("/handle_new_article/{article_mbdding_vector}")
def read_item(article_mbdding_vector: int, q: Union[str, None] = None):
    return {"item_id": article_mbdding_vector, "q": q}


@app.get("/handle_user_article_interaction/{user_id}:{article_id}")
def read_item(user_id: int,article_id: int, q: Union[str, None] = None):
    return {
        "user_id": user_id,
        "article_id": article_id,
        "q": q
    }
    
if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8879)
    