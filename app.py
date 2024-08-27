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

@app.route("/upload", methods = ["POST"])    #사진 업로드
def upload():
    f = request.files.get('file')

    
    print("checkupload")   #테스팅
    print(f)

    photoid = str(uuid.uuid4())[:12]                   #서버에는 임의의 이름으로 받은 사진 저장
    f.save("static/img/{}.jpeg".format(photoid))   
    return jsonify({"photo_id" : photoid})            #저장한 사진의 url을 프론트에 전달

#OCR 모델
@app.route("/model", methods = ["POST"])
def model():
    id = request.get_json()                      #저장한 사진의 url을 프론트에서 다시 받기
    photoid = id['photo_id']

    uid = session.get("uid")       #일단

    #Dtext = text_model.detect_text("static/img/{}.jpeg".format(photoid))
    Dtext = "for test"
    if Dtext == None:                         #인식이 안된 경우 
        print("no text")
        return jsonify({"imgsrc" : "static/img/{}.jpeg".format(photoid) , "detect" : False, "text" : Dtext})
    else: 
        print("yes text")
        DB.write_post(photoid, uid, Dtext)  
        return jsonify({"imgsrc" : "static/img/{}.jpeg".format(photoid), "detect" : True, "text": Dtext})
    

@app.route("/category", methods = ["POST"])
def category():
    info = request.get_json()                      #저장한 사진의 url을 프론트에서 다시 받기
    photoid = info['photo_id']
    category_name = info['category']

    uid = session.get("uid")       #일단
    DB.update_category(photoid, category_name)

@app.route("/text_list", methods = ["POST"])       #사용자의 해당 카테고리를 가지는 사진 목록을 보여줌.
def text_list():
    if "uid" in session:
        info = request.get_json()       #카테고리 정보를 받을 것
        category_name = info['category']

        uid = session.get("uid")
        print(uid)
        
        c_post = DB.get_category(uid, category_name)       #해당 카테고리의 이미지 소스들

        return jsonify({"post_list" :c_post, "category" : category_name})     #none이면 아직 목록이 없는 상태, category를 통해 어떤 카테고리의 리스트인지표기
    else :
        return jsonify(False)  #로그인 안된 상태로 mypage로 가면 다시 로그인 상태로 바꾼다.

@app.route("/detail",methods = ["POST"])
def detail():
    if "uid" in session:
        info = request.get_json()
        photoid = info['photoid']

        detail_info = DB.get_detail(photoid)
        print(detail_info)

        return jsonify({"photo": detail_info["photo"] , "text" : detail_info["Dtext"]})
    else: 
        return jsonify(False)


if __name__ == "__main__":
    app.run(host = "0.0.0.0")