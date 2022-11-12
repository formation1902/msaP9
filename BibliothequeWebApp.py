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

def fp(*smth):
    print('\n','#'*10)
    print(smth)
    print('#'*10,'\n')


app = Flask(__name__,template_folder='templates')


@app.route('/')
def home():
    fp('Je suis at home')
    return render_template('welcome.html')



@app.route('/sendUserInformation',methods=['POST'])
def fx_any_user():
    print("Gestion des données utilisateurs : ")
    try:
        current_user = User(int(request.form['user_id']))
        print("current_user_id : ",current_user.toJson())
    except:
        current_user = User(-1)
        user_pcs = []
        try:
            user_region = int(request.form['user_region'])
            print("received region :", user_region)
            current_user.setUserRegion(user_region)
        except:
            print("that's not good atol :: where do you come from ? !!!!")
        for i in range(3):
            element = 'user_pc'+str(i+1)
            try:
                tmp = request.form[element]
                print("received user preferred category at order " +str(i+1), " : ", tmp)
                if int(tmp) > -1:
                    user_pcs.append(int(tmp))
            except:
                print("that's really bad, youre not cooperative atol ==> no", element)
        print("Collected users_pcs ordered list : ",user_pcs)
        current_user.setUserPreferredCategories(user_pcs)
    if current_user.user_id==-1:
        if len(current_user.user_pcs)==0 and current_user.user_region==-1:
            print("------------------------ Popular ------------------------")
            azure_function_API = 'https://p9-azurefunctionapp.azurewebsites.net/api/popular-rs'
            toto = requests.post(azure_function_API).content.decode('utf-8')
        else:
            print("------------------------ knowledge ------------------------")
            azure_function_API = 'https://p9-azurefunctionapp.azurewebsites.net/api/knowledge-rs'
            userRequestBody = {
                "region"  : None if current_user.user_region==-1 else current_user.user_region,
                "user_pc" : current_user.user_pcs
            }
            print("userRequest - ",userRequestBody,"\n\n")
            toto = requests.post(azure_function_API,json=userRequestBody).content.decode('utf-8')
            print("---------- toto :",type(toto),"---------- ",toto)
    elif current_user.user_id in the_reader_blacklist:
        print("------------------------ CBRS ------------------------")
        azure_function_API = 'https://p9-azurefunctionapp.azurewebsites.net/api/cbrs'
        userRequestBody = json.dumps({
            "user_id" : current_user.user_id
        })
        print("userRequest - ",userRequestBody,"\n\n")
        toto = requests.post(azure_function_API,userRequestBody).content.decode('utf-8')
    else:
        print("------------------------ CFRS ------------------------")
        azure_function_API = 'https://p9-azurefunctionapp.azurewebsites.net/api/cfrs'
        userRequestBody = {
            "user_id" : current_user.user_id
        }
        print("userRequest - ",userRequestBody,"\n\n")
        toto = requests.post(azure_function_API,json=userRequestBody).content.decode('utf-8')
    print('\n\n########################sacred message')
    print(current_user.user_id in the_reader_blacklist)
    print(current_user.toJson())
    print("\n\n-----------------------")
    print('1..................')
    # toto = requests.post(azure_function_API).content.decode('utf-8')
    print('2..................')
    print(type(toto))
    print('----> 3..................',toto)
    res = json.loads(toto)
    print('res------------> ',res)
    print('3.1..................')
    current_user.setUserRA(eval(res['result']))
    current_user.setUserGreeting(res['description'])
    print(type(res))
    print('4..................')
    print("\n\n-----------------------")
    fp(current_user.toJson())
    return render_template('getThemIn.html',current_user=current_user)
    


if __name__ == '__main__':
    app.run(debug=True,port=10100)
