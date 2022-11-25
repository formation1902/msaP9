#!/usr/bin/python
from flask import Flask,render_template,request
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
    # connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    connect_str = os.getenv('STORAGE_CONNSTR')
    # connect_str = "DefaultEndpointsProtocol=https;EndpointSuffix=core.windows.net;AccountName=p9azurefunctionapp;AccountKey=nT3CNIBuBcl9K2U96LSWiNLQjKwLzbZq13g3aCAWNaYZACAhgcHVygb1Vzb2yYmSzS+fUKpG5MqL+AStQLRHoA==;BlobEndpoint=https://p9azurefunctionapp.blob.core.windows.net/;FileEndpoint=https://p9azurefunctionapp.file.core.windows.net/;QueueEndpoint=https://p9azurefunctionapp.queue.core.windows.net/;TableEndpoint=https://p9azurefunctionapp.table.core.windows.net/"
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
# - the_reader_blacklist : les lecteurs specialisées
# - elected_categories   : les categoris promues (par default all)
# - nouveaux_articles_non_publies : selection de quelques articles retirees pour etre republier
# - known_users : les lecteurs references
# - consuted_articles : les articles publiees consultees
#
the_reader_blacklist, elected_categories,nouveaux_articles_non_publies,known_users,consulted_articles = get_data()
print(the_reader_blacklist[:5])

###########################################
###########################################
#
# Parametres pour l'application FLASK
#
###########################################
User.init(known_users)
current_users = {}
already_added = []
user_new_terminated_sessions = {}
closed_sessions = []


class userArticle():
    def __init__(self,article_id,article_has_never_been_consulted):
        self.article_id     = article_id
        self.article_has_never_been_consulted = article_has_never_been_consulted


    
app = Flask(__name__,template_folder='templates')    
cache_manager_url = 'http://0.0.0.0:8878'  # local
# cache_manager_url = 'http://0.0.0.0:20100' # docker local
# cache_manager_url = 'https://msap9-cm001.azurewebsites.net' # docker webapp service on azure 


def get_cache_manager_status():
    res = requests.get(cache_manager_url + '/pingFromBibliothque')
    print(res)
    print(res.content)
    return json.loads(res.content)

sorry_about_it = {'msg':'waiting for the cache manager to come up. This can take a while','published_articles':-1}
cache_manager_status = sorry_about_it

#
###################################
#
msaLockFileName = "lock_ana.lock"
with open(msaLockFileName,"w") as f:
    f.write('operation en cours')

def set_add_articles_lock():
    global container_client,msaLockFileName
    print("-------------------> set called : ",end=" == ")
    try:
        with open(msaLockFileName,'rb') as smth:
            container_client.upload_blob(data=smth,overwrite=False,name=msaLockFileName)
        print('OK')
        return True
    
    except:
        print('KO')
        return False

def release_add_articles_lock():
    global container_client,msaLockFileName
    print("-------------------> release called : ",end=" == ")
    try:
        container_client.delete_blob(msaLockFileName)
        print("OK")
        return True
    except:
        print('NOK')
        return False

def check_add_articles_lock():
    global container_client,msaLockFileName
    print("-------------------> check called : ",end=" == ")
    try:
        smth = container_client.download_blob(msaLockFileName)
        print("A lock is here")
        return True
    except:
        print(" No lock")
        return False
    
#
###################################
#    

msaCFRS_LockFileName = "lock_update_cfrs.lock"
with open(msaCFRS_LockFileName,"w") as f:
    f.write('update_cfr_operation en cours')

def set_update_cfrs_lock():
    global container_client,msaCFRS_LockFileName
    print("-------------------> set called : ",end=" == ")
    try:
        with open(msaCFRS_LockFileName,'rb') as smth:
            container_client.upload_blob(data=smth,overwrite=False,name=msaCFRS_LockFileName)
        print('OK')
        return True
    
    except:
        print('KO')
        return False

def release_update_cfrs_lock():
    global container_client,msaCFRS_LockFileName
    print("-------------------> release called : ",end=" == ")
    try:
        container_client.delete_blob(msaCFRS_LockFileName)
        print("OK")
        return True
    except:
        print('NOK')
        return False

def check_update_cfrs_lock():
    global container_client,msaCFRS_LockFileName
    print("-------------------> check called : ",end=" == ")
    try:
        smth = container_client.download_blob(msaCFRS_LockFileName)
        print("A lock is here")
        return True
    except:
        print(" No lock")
        return False

update_cfrs_activated =    check_update_cfrs_lock() 
###############################################################
###############################################################
###############################################################

@app.route('/')
def home():
    #
    # ping vers le cache manager et recuperation du nombre d'articles publiées 
    # ---> on l'utiliser pour de la marketing 
    # ---> mais nous permettra aussi de verifier l'ajour de nouveaux articles 
    #
    global cache_manager_status
    try:
        cache_manager_status=get_cache_manager_status()
    except:
        cache_manager_url = sorry_about_it
        
    lockana = check_add_articles_lock()
    update_cfrs_activated =    check_update_cfrs_lock() 
    return render_template('welcome.html',elected_categories=elected_categories,nouveaux_articles=list(nouveaux_articles_non_publies.index),lockana=lockana,cfrs_update=update_cfrs_activated,cache_manager_status=cache_manager_status)

def record_new_visiteur(current_user):
    global current_users
    current_users[str(current_user.user_id)] = current_user


###################################################################################
###################################################################################
#
#  Ajout d'un lots de nouveaux articles à publier - avec maj cbrs
#
###################################################################################
class RetourAddArticles():
    def __init__(self,candidat_article_ids=None,actual_added_articles_ids=None,msg=None,valid=True):
        self.candidat_article_ids     = candidat_article_ids
        self.actual_added_articles_ids= actual_added_articles_ids
        self.msg                      = msg
        self.valid                    = valid
    def __str__(self) -> str:
        if self.valid :
            return json.dumps({
                'candidat_article_ids' : self.candidat_article_ids,
                'actual_added_articles_ids' : self.actual_added_articles_ids,
                'msg' : self.msg,
            })
        
@app.route('/PublishNewArticles',methods=['POST'])
def fx_publish_brand_new_article():
    global cache_manager_status
    print("\n before --------------> check : ",check_add_articles_lock())
    if not check_add_articles_lock() and set_add_articles_lock():
        print(" -------------> and now check_add_articles_lock : ",check_add_articles_lock())
        articles_ids = [int(article_id) for article_id in request.form.getlist('article_name')]    
        print("Les articles : ",articles_ids)
        
        nouveaux_articles_non_publies.drop(articles_ids,inplace=True)
        
        cm_url = cache_manager_url + '/publier_des_nouveaux_articles'
        
        toto = json.loads(requests.post(cm_url,json={'articles_ids':articles_ids}).json())
        toto = RetourAddArticles(articles_ids,toto['article_ids'],toto['msg'],True)
        release_add_articles_lock()

    else:
        toto = RetourAddArticles(valid=False)
        print(" else check_add_articles_lock : ",check_add_articles_lock())
        print(" else set_add_articles_lock : ",set_add_articles_lock())
    cache_manager_status=get_cache_manager_status()
    lockana = check_add_articles_lock()
    update_cfrs_activated =    check_update_cfrs_lock() 
    print("Finally lockana : ",lockana)
    print("Finally : toto = ",toto)
    return render_template('welcome.html',elected_categories=elected_categories,nouveaux_articles=list(nouveaux_articles_non_publies.index),toto=toto,lockana=lockana,cfrs_update=update_cfrs_activated,cache_manager_status=cache_manager_status)



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
            print("1.............")
            userRequestBody = json.dumps({
                "user_id" : current_user.user_id
            })
            print("2.............")
            toto_cbrs = requests.post(azure_function_API,userRequestBody).content.decode('utf-8')
            print("3.............")
            print("toto_cbrs = ",toto_cbrs)
            res = json.loads(toto_cbrs)
            print("4.............")
            print("\n res = ",res)
            print("5.............")
            user_cbrs_objects = []
            print("\n eevaal ",res['result'])
            for e in eval(res['result']):
                article_id = int(e)
                article_has_never_been_consulted = not article_id in consulted_articles
                user_cbrs_objects.append(userArticle(article_id,article_has_never_been_consulted))
        
        
            
            # current_user.setUser_cbrs(eval(res['result']))
            current_user.setUser_cbrs(user_cbrs_objects)
            current_user.setUserGreeting(res['description'])
    
    
    record_new_visiteur(current_user)
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

    return render_template('getThemIn.html',current_user=current_users[request.form['user_id']])



@app.route('/seeYousoonWewillCookSomeRecommendationForYouAndOnlyYou',methods=['POST'])
def fx_seeYouSoon():
    global current_users,closed_sessions,cache_manager_status
    #
    # On integre les interactions enregistrees dans la session ainsi terminee recue
    # 
    print("L'utlisateur a cloturee sa session :  ", request.form['user_id'])
    # print("Here is the recorded incomes : ", current_users[request.form['user_id']].getUserSessionInteractions())
    closed_sessions.append({'user_id' : request.form['user_id'], 'incomes' : current_users[request.form['user_id']].getUserSessionInteractions()})
    current_users.pop(request.form['user_id'])
    lockana = check_add_articles_lock()
    update_cfrs_activated =    check_update_cfrs_lock() 
    
    cache_manager_status=get_cache_manager_status()
    print("\n\nclosed sessions : ",closed_sessions,"\n\n")
    
    return render_template('welcome.html',elected_categories=elected_categories,nouveaux_articles=list(nouveaux_articles_non_publies.index),lockana=lockana,cfrs_update=update_cfrs_activated,cache_manager_status=cache_manager_status)


def convert_closed_sessions_to_pandasDF(closed_sessions):
    df = pd.DataFrame(columns=['user_id','session_id','session_size','article_id','clicks_n'])
    vars = ['user_id', 'session_id', 'session_size', 'article_id']
    session_counter = dict()
    for session_income in closed_sessions:
        user_id = session_income['user_id']
        if user_id in session_counter.keys():
            session_counter[user_id]+=1
        else:
            session_counter[user_id]=1
        res=pd.DataFrame(columns=['user_id','session_id','article_id','clicks_n'])
        session_size = 0
        for a in session_income['incomes']:
            article_id  = a
            clicks_n =     session_income['incomes'][a]
            session_size+=clicks_n
            for i in range(clicks_n):
                res = pd.concat([res,pd.DataFrame({'user_id':user_id,'session_id':str(user_id) + '_' +str(session_counter[user_id]),'article_id':article_id,'clicks_n':clicks_n},index=[0])]) 
        res['session_size'] = session_size
        df = pd.concat([df,res[['user_id','session_id','session_size','article_id','clicks_n']]])
    # df.to_csv("myDF.csv")
    print("The df")
    print(df)
    
    return df[vars]

import time
@app.route('/cfrs_watcher',methods=['POST'])
def moulinette_to_update_cfrs():
    #
    # Integration des nouvelles interactions utilisateurs uniquement pour le cfrs
    # - Les populars et knowldeges sont des condamnées à attendre un lendemain
    global container_client,msaCFRS_LockFileName,closed_sessions
    if not check_update_cfrs_lock() and set_update_cfrs_lock():
        #
        # On envois les dictionnaires au cache-manager pour integration par le CRFS agent!
        #
        print("La liste des sessions closes  : ")
        for sc in closed_sessions:
            print("\t - ",sc)
            
        print("\n\n1...............")
        
        # df = pd.DataFrame(columns=['user_id','article_id','clicks_n'])        
        # for session_income in closed_sessions:
        #     for article_id,clicks_n in session_income['incomes'].items():
        #         df = pd.concat(
        #             [
        #                 df,
        #                 pd.DataFrame(
        #                     {
        #                         'user_id':session_income['user_id'],
        #                         'article_id':article_id,
        #                         'clicks_n':clicks_n
        #                     },
        #                     index=[0]
        #                 )
        #             ]
        #         )
        df = convert_closed_sessions_to_pandasDF(closed_sessions)
        msaFileName = "new_consultations.csv"
        df.to_csv(msaFileName,index=False)
        with open(msaFileName,'rb') as smth:
            container_client.upload_blob(data=smth,overwrite=True,name=msaCFRS_LockFileName)
        
        cm_url = cache_manager_url + '/closed_sessions_incomes'

        
        toto = requests.get(cm_url)
        print("toto = ",type(toto))
        closed_sessions = []
        msaCondition = False
        if msaCondition:
            release_update_cfrs_lock()

    else:
        print(" else check_update_cfrs_lock : ",check_update_cfrs_lock())
        
    cache_manager_status=get_cache_manager_status()
    lockana = check_add_articles_lock()
    update_cfrs_activated =    check_update_cfrs_lock() 

    return render_template('welcome.html',elected_categories=elected_categories,nouveaux_articles=list(nouveaux_articles_non_publies.index),lockana=lockana,cfrs_update=update_cfrs_activated,cache_manager_status=cache_manager_status)



# def convert_closed_sessions_to_pandasDF(closed_sessions):
#     df = pd.DataFrame(columns=['user_id','session_id','article_id','clicks_n'])
#     session_counter = dict()
#     for session_income in closed_sessions():
#         user_id = session_income['user_id']
#         if user_id in session_counter.keys():
#             session_counter[user_id]+=1
#         else:
#             session_counter[user_id]=1
#         for a in session_income['incomes']:
#             article_id  = a
#             clicks_n =     session_income['incomes'][a]
#             pd.concat(df,pd.DataFrame({'user_id':user_id,'session_id':session_counter[user_id],'article_id':article_id,'clicks_n':clicks_n}))
#     return df
            
if __name__ == '__main__':
    app.run(debug=True,port=10100)
