from flask import Flask, request, session, jsonify
from DB_handler import DBmodule
import uuid
import datetime
from flask_cors import CORS

app = Flask(__name__)
app.config["SECRET_KEY"] = "dasggasdgasd"
app.config["SESSION_COOKIE_SAMESITE"] = "None"
app.config["SESSION_COOKIE_SECURE"] = True


CORS(app, supports_credentials=True)



DB=DBmodule()

@app.route("/")                     #홈화면 버튼에 대한 처리(로그인o : 업로드 화면, 로그인x : 로그인 화면으로)
def index():
    if "uid" in session:
        print("Home True")
        return jsonify(True)
    else:
        print("Home False")
        return jsonify(False)

@app.route("/login", methods = ["POST"])      #실제로 보이는 부분x
def login():
    users = request.get_json()
    uid = users['id']
    pwd = users['pw']

    if DB.login(uid,pwd):
        session["uid"] = uid

        print(session["uid"])   #test
        print("True")

        response = jsonify(True)
        return response             #로그인 성공   ->업로드 화면
    else:
        print("False")
        return jsonify(False)            #로그인 실패   ->다시 로그인 화면
    
@app.route("/logout")           #로그아웃
def logout():
    if "uid" in session:
        session.pop("uid")
        return None         #홈 화면으로 이동?

@app.route("/dup" , methods = ["POST"])           
def dup():
    users = request.get_json()
    uid = users['id']
    print(uid)   #for test
    if DB.signin_verification(uid):
        print(False)
        return jsonify(False)
    else :
        print(True)
        return jsonify(True)
    
@app.route("/signin", methods = ["POST"])   #회원가입 처리
def signin():
    users = request.get_json()
    uid = users['id']
    pwd = users['pwd']
    if DB.signin(uid,pwd):
        return jsonify(True)        #회원가입 성공 -> 로그인 화면
    else:
        return jsonify(False)       #회원가입 실패 -> 다시 회원가입 화면(무슨 이유로 실패인지 전달 1. 비밀번호 재입력 오류, 이미 쓰는)



if __name__ == "__main__":
    app.run(host = "0.0.0.0")