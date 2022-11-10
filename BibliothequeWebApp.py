#
# Hihihihihi, fot gitting activitiez
#
#!/usr/bin/python
from flask import Flask,render_template,url_for,request
import requests
import os
from user import User



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
        current_user = User(request.form['user_id'])
        print("current_user_id : ",current_user.toJson())
    except:
        current_user = User(-1)
        user_pcs = []
        try:
            user_region = request.form['user_region']
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
                    user_pcs.append(tmp)
            except:
                print("that's really bad, youre not cooperative atol ==> no", element)
        print("Collected users_pcs ordered list : ",user_pcs)
        current_user.setUserPreferredCategories(user_pcs)
    azure_function_API = 'https://p9-azurefunctionapp.azurewebsites.net/api/get_customized_recommended_articles'
    try:
        print('\n\n########################sacred message')
        print("\n\n-----------------------")
        print('1..................')
        toto = requests.post(azure_function_API)
        print('2..................')
        print(type(toto))
        print('3..................')
        res = toto.json()
        current_user.setUserRA(res['user_ra'])
        current_user.setUserGreeting(res['greeting'])
        print(type(res))
        print('4..................')
        print("\n\n-----------------------")
    except:
        print("We got a pb")
        pass
    fp(current_user.toJson())
    return render_template('getThemIn.html',current_user=current_user)
    


if __name__ == '__main__':
    app.run(debug=True,port=10100)
