
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
    except:
        current_user = User(-1)
    current_user.user_ra = [1,2,3,4,5]
    fp(current_user.toJson())
    return render_template('getThemIn.html',current_user=current_user)
    


if __name__ == '__main__':
    app.run(debug=True,port=33330)
