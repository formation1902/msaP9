#
# Hihihihihi, fot gitting activitiez
#
#!/usr/bin/python
from flask import Flask,render_template,url_for,request
from pydantic import BaseModel,Field
import requests
import os,io,json,pickle
import pandas as pd
import numpy as np
from azure.storage.blob import BlobServiceClient
from user import User
#
# On recupere les donnes de stockage azure :
#
try:
    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    container_client = blob_service_client.get_container_client(container="an-existing-container") 
except:
    print("Pb d'acces au stockage azure")
    
    
def get_data(fakeString=""):
        print('1.............')
        download_file_path_1 = "./" +str(fakeString) +"cbrs_users_referentiel.pck" 
        with open(file=download_file_path_1, mode="wb") as download_file:
            download_file.write(container_client.download_blob('cbrs_users_referentiel.pck').readall())
        
        print('2.............')    
        download_file_path_2 = "./"+str(fakeString) +"elected_categories.pck" 
        with open(file=download_file_path_2, mode="wb") as download_file:
            download_file.write(container_client.download_blob('elected_categories.pck').readall())
        
        print('3.............')
        blob_name = "Quelques_articles_publiees_non_consultees_a_considerer_comme_des_articles_nouveaux.csv"
        nouveaux_articles_non_publies = pd.read_csv(io.BytesIO(container_client.download_blob(blob_name).readall()),index_col='index')
        
        print('4.............')
        blob_name = "known_user_ids.pck"
        known_users = pickle.load(io.BytesIO(container_client.download_blob(blob_name).readall())) 
        
        print('5.............')
        blob_name = "consulted_articles_ids.pck"
        consulted_articles = pickle.load(io.BytesIO(container_client.download_blob(blob_name).readall())) 
        
        
        return pickle.load(open(download_file_path_1,"rb")),pickle.load(open(download_file_path_2,"rb")),nouveaux_articles_non_publies,known_users,consulted_articles

#
#
#
the_reader_blacklist, elected_categories,nouveaux_articles_non_publies,known_users,consulted_articles = get_data()
User.init(known_users)
already_added = []
print(the_reader_blacklist[:5])
app = Flask(__name__,template_folder='templates')
user_new_terminated_sessions = {}
update_cfrs_activated = True
current_users = {}
lock_operation_ajout_en_cours = True


class userArticle():
    def __init__(self,article_id,article_has_never_been_consulted):
        self.article_id     = article_id
        self.article_has_never_been_consulted = article_has_never_been_consulted

class Article(BaseModel):
    article_id: int
    class Config:
        arbitrary_types_allowed = True
    article_vector: np.ndarray = Field(default_factory=lambda: np.zeros(shape=75).reshape(-1,75))
    
    
@app.route('/')
def home():
    return render_template('welcome.html',elected_categories=elected_categories,nouveaux_articles=list(nouveaux_articles_non_publies.index),lockana=lock_operation_ajout_en_cours,cfrs_update=update_cfrs_activated)


###################################################################################
###################################################################################
#
#  Ajout d'un lots de nouveaux articles à publier - maj cbrs
#
###################################################################################


@app.route('/unlock_add_new_article',methods=['POST'])
def fx_unlock_add_new_articles():
    global lock_operation_ajout_en_cours
    assert lock_operation_ajout_en_cours,"Une incoherence de la gestion du verrou ajout new articles"

@app.route('/PublishNewArticles',methods=['POST'])
def fx_publish_brand_new_article():
    global lock_operation_ajout_en_cours
    if not lock_operation_ajout_en_cours:
        lock_operation_ajout_en_cours = True
    articles_ids = [int(article_id) for article_id in request.form.getlist('article_name')]    
    print("Les articles : ",articles_ids)
    
    cache_manager_url = 'http://0.0.0.0:8879/publier_un_nouveau_article:'+str(article_ids)
    toto = requests.post(cache_manager_url)
    print("5...............")
    nouveaux_articles_non_publies.drop(article_id,inplace=True)
    print(type(toto))
    print(type(toto.content))
    print(toto.content.decode('utf-8'))
    
    lock_operation_ajout_en_cours = False
    return render_template('welcome.html',elected_categories=elected_categories,nouveaux_articles=list(nouveaux_articles_non_publies.index),toto=toto.content.decode('utf-8'),lockana=lock_operation_ajout_en_cours,cfrs_update=update_cfrs_activated)



@app.route('/byebye',methods=['POST'])
def fx_byebye():
    #
    # on envois la session ainsi terminée au service cache-manager
    # 
    print("On envois les infos de la session au cache-manager : ")
    return render_template('welcome.html',elected_categories=elected_categories,nouveaux_articles=list(nouveaux_articles_non_publies.index),lockana=lock_operation_ajout_en_cours,cfrs_update=update_cfrs_activated)

def handle_new_visiteur(current_user):
    global current_users
    current_users[str(current_user.user_id)] = current_user


@app.route('/sendUserInformation',methods=['POST'])
def fx_any_user():
    global current_users_n
    try:
        print("\n\n########### ",request.form)
        print("\n\n########### ",request.form['user_id'])
        current_user = User(int(request.form['user_id']))
    except:
        current_user = User(-1)
        user_pcs = []
        try:
            user_region = int(request.form['user_region'])
            current_user.setUserRegion(user_region)
        except:
            pass
        for i in range(3):
            element = 'user_pc'+str(i+1)
            try:
                tmp = request.form[element]
                if int(tmp) > -1:
                    user_pcs.append(int(tmp))
            except:
                pass
        current_user.setUserPreferredCategories(user_pcs)
        current_user.set_as_new_user()
    #
    #   
    #
    if current_user.is_new_user():
        if len(current_user.user_pcs)==0 and current_user.user_region==-1:
            print("------------------------ Popular ------------------------")
            azure_function_API = 'https://p9-azurefunctionapp.azurewebsites.net/api/popular-rs'
            toto = requests.post(azure_function_API).content.decode('utf-8')
        else:
            print("------------------------ knowledge ------------------------")
            azure_function_API = 'https://p9-azurefunctionapp.azurewebsites.net/api/knowledge-rs'
            userRequestBody = {
                "region"  : "" if current_user.user_region==-1 else current_user.user_region,
                "user_pc" : current_user.user_pcs
            }
            print(userRequestBody)
            toto = requests.post(azure_function_API,json=userRequestBody).content.decode('utf-8')  
        #
        # 
        #
        res = json.loads(toto)
        print("\n res = ",res)
        user_ra_objects = []
        print("\n eevaal ",res['result'])
        for e in eval(res['result']):
            print("eeeeeeeeeeeeeeee = ",e)
            article_id = int(e)
            article_has_never_been_consulted = not article_id in consulted_articles
            user_ra_objects.append(userArticle(article_id,article_has_never_been_consulted))
        # current_user.setUserRA(eval(res['result']))
        print("A....................")
        current_user.setUserRA(user_ra_objects)
        print("B....................")
        current_user.setUserGreeting(res['description'])
        print("C....................")
        current_user.setNewUserId()
        print("D....................")
    else:
        print("------------------------ CFRS ------------------------")
        azure_function_API = 'https://p9-azurefunctionapp.azurewebsites.net/api/cfrs'
        userRequestBody = {
            "user_id" : current_user.user_id
        }
        toto_cfrs = requests.post(azure_function_API,json=userRequestBody).content.decode('utf-8')
        res = json.loads(toto_cfrs)
        
        print("\n res = ",res)
        user_cfrs_objects = []
        print("\n eevaal ",res['result'])
        for e in eval(res['result']):
            print("eeeeeeeeeeeeeeee = ",e)
            article_id = int(e)
            article_has_never_been_consulted = not article_id in consulted_articles
            user_cfrs_objects.append(userArticle(article_id,article_has_never_been_consulted))
        
        
        # current_user.setUser_cfrs(eval(res['result']))
        current_user.setUser_cfrs(user_cfrs_objects)
        current_user.setUserGreeting(res['description'])
        if current_user.user_id in the_reader_blacklist:
            current_user.set_as_specialist()
            print("------------------------ CBRS ------------------------")
            azure_function_API = 'https://p9-azurefunctionapp.azurewebsites.net/api/cbrs'
            userRequestBody = json.dumps({
                "user_id" : current_user.user_id
            })
            toto_cbrs = requests.post(azure_function_API,userRequestBody).content.decode('utf-8')
            res = json.loads(toto_cbrs)
            
            print("\n res = ",res)
            user_cbrs_objects = []
            print("\n eevaal ",res['result'])
            for e in eval(res['result']):
                print("eeeeeeeeeeeeeeee = ",e)
                article_id = int(e)
                article_has_never_been_consulted = not article_id in consulted_articles
                user_cbrs_objects.append(userArticle(article_id,article_has_never_been_consulted))
        
        
            
            # current_user.setUser_cbrs(eval(res['result']))
            current_user.setUser_cbrs(user_cbrs_objects)
            
            current_user.setUserGreeting(res['description'])
    
    handle_new_visiteur(current_user)
    return render_template('getThemIn.html',current_user=current_user)

###################################################################################
###################################################################################
#
#  Une moulinette pour l'integration des nouvelles sessions utilisateur terminées
#
###################################################################################

@app.route('/add_user_article_click',methods=['POST','GET'])
def fx_add_user_article_click():
    print(" request == ",request.form)
    print("current users == ",current_users.keys())
    print("user_id : ",request.form['user_id'])
    print("article_id : ",request.form['article_id'])
    print("current_users : ",current_users)
    print('Current_user  : ',current_users[request.form['user_id']])
    print("\n\n")
    current_users[request.form['user_id']].recordNewConsultation(request.form['article_id'])
    print("current user == ",current_users[request.form['user_id']].toJson())
    print("\n\n")
    return render_template('getThemIn.html',current_user=current_users[request.form['user_id']])



import time
@app.route('/cfrs_watcher',methods=['POST','GET'])
def moulinette_to_update_cfrs():
    print("La moulinette est lancée - ")
    update_cfrs_activated = True
    while True:
        if len(user_new_terminated_sessions)>0:
            #
            # Envoyer les informations de sessions au cache manager
            #
            time.sleep(3600)
            pass
        else:
            #
            # diminuer l interval de mise a jour
            #
            time.sleep(3600)
            pass

if __name__ == '__main__':
    app.run(debug=True,port=10100)
