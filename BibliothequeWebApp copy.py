#
# Hihihihihi, fot gitting activitiez
#
#!/usr/bin/python
from flask import Flask,render_template,url_for,request
import requests
import os,io,json
from user import User
import pickle

the_reader_blacklist = pickle.load(open("cbrs_users_referentiel.pck","rb"))

elected_categories = pickle.load(open("elected_categories.pck","rb"))

app = Flask(__name__,template_folder='templates')


@app.route('/')
def home():
    return render_template('welcome.html',elected_categories=elected_categories)



@app.route('/sendUserInformation',methods=['POST'])
def fx_any_user():
    try:
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
    #
    #   
    #
    if current_user.user_id==-1:
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
    elif current_user.user_id in the_reader_blacklist:
        print("------------------------ CBRS ------------------------")
        azure_function_API = 'https://p9-azurefunctionapp.azurewebsites.net/api/cbrs'
        userRequestBody = json.dumps({
            "user_id" : current_user.user_id
        })
        toto = requests.post(azure_function_API,userRequestBody).content.decode('utf-8')
    else:
        print("------------------------ CFRS ------------------------")
        azure_function_API = 'https://p9-azurefunctionapp.azurewebsites.net/api/cfrs'
        userRequestBody = {
            "user_id" : current_user.user_id
        }
        toto = requests.post(azure_function_API,json=userRequestBody).content.decode('utf-8')
    
    
    res = json.loads(toto)
    
    current_user.setUserRA(eval(res['result']))
    current_user.setUserGreeting(res['description'])
    
    return render_template('getThemIn.html',current_user=current_user)
    


if __name__ == '__main__':
    app.run(debug=True,port=10100)
