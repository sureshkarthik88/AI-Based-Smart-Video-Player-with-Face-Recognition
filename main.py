import os
import datetime
from flask import Flask, render_template, Response, redirect, request, session, url_for, flash
from werkzeug.utils import secure_filename
import cv2
import mysql.connector
import warnings

from camera import VideoCamera
from camera2 import VideoCamera2
from camera3 import VideoCamera3

warnings.filterwarnings("ignore")

app = Flask(__name__)
app.secret_key = "abcdef"

UPLOAD_FOLDER = "static/upload"
ALLOWED_EXTENSIONS = {"csv"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    charset="utf8",
    database="age_wise_video",
)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html", msg="")

@app.route("/login", methods=["GET", "POST"])
def login():
    msg = ""
    if request.method == "POST":
        uname = request.form["uname"]
        pwd = request.form["pass"]
        cursor = mydb.cursor()
        cursor.execute("SELECT * FROM register WHERE uname = %s AND pass = %s", (uname, pwd))
        account = cursor.fetchone()
        if account:
            session["username"] = uname
            open("age.txt", "w").close()
            return redirect(url_for("test_cam"))
        msg = "Incorrect username/password!"
    return render_template("login.html", msg=msg)

@app.route("/login_admin", methods=["GET", "POST"])
def login_admin():
    msg = ""
    if request.method == "POST":
        uname = request.form["uname"]
        pwd = request.form["pass"]
        cursor = mydb.cursor()
        cursor.execute("SELECT * FROM admin WHERE username = %s AND password = %s", (uname, pwd))
        account = cursor.fetchone()
        if account:
            session["username"] = uname
            return redirect(url_for("admin"))
        msg = "Incorrect username/password!"
    return render_template("login_admin.html", msg=msg)

@app.route("/register", methods=["GET", "POST"])
def register():
    msg = ""
    now = datetime.datetime.now()
    rdate = now.strftime("%d-%m-%Y")
    mycursor = mydb.cursor()
    if request.method == "POST":
        name = request.form["name"]
        mobile = request.form["mobile"]
        email = request.form["email"]
        uname = request.form["uname"]
        pass1 = request.form["pass"]
        mycursor.execute("SELECT max(id)+1 FROM register")
        maxid = mycursor.fetchone()[0]
        if maxid is None:
            maxid = 1
        sql = "INSERT INTO register(id,name,mobile,email,uname,pass) VALUES (%s, %s, %s, %s, %s, %s)"
        val = (maxid, name, mobile, email, uname, pass1)
        mycursor.execute(sql, val)
        mydb.commit()
        msg = "success"
    return render_template("register.html", msg=msg, rdate=rdate)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    msg = ""
    act = request.args.get("act")
    mycursor = mydb.cursor()

    if request.method == "POST":
        age = request.form["age"]
        mycursor.execute("SELECT max(id)+1 FROM upload_video")
        maxid = mycursor.fetchone()[0]
        if maxid is None:
            maxid = 1
        file = request.files["file"]
        fname = file.filename
        f1 = "V" + str(maxid) + fname
        filename = secure_filename(f1)
        file.save(os.path.join("static/video/", filename))
        sql = "INSERT INTO upload_video(id,age,filename) VALUES (%s, %s, %s)"
        val = (maxid, age, filename)
        mycursor.execute(sql, val)
        mydb.commit()
        msg = "success"
    return render_template("admin.html", msg=msg)

@app.route("/view_file", methods=["GET", "POST"])
def view_file():
    msg = ""
    act = request.args.get("act")
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM upload_video order by id desc")
    data1 = mycursor.fetchall()
    if act == "del":
        did = request.args.get("did")
        mycursor.execute("delete from upload_video where id=%s", (did,))
        mydb.commit()
        return redirect(url_for("view_file"))
    return render_template("view_file.html", msg=msg, data1=data1)

def highlightFace(net, frame, conf_threshold=0.7):
    frameOpencvDnn = frame.copy()
    frameHeight = frameOpencvDnn.shape[0]
    frameWidth = frameOpencvDnn.shape[1]
    blob = cv2.dnn.blobFromImage(frameOpencvDnn, 1.0, (300, 300), [104, 117, 123], True, False)
    net.setInput(blob)
    detections = net.forward()
    faceBoxes = []
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > conf_threshold:
            x1 = int(detections[0, 0, i, 3] * frameWidth)
            y1 = int(detections[0, 0, i, 4] * frameHeight)
            x2 = int(detections[0, 0, i, 5] * frameWidth)
            y2 = int(detections[0, 0, i, 6] * frameHeight)
            faceBoxes.append([x1, y1, x2, y2])
            cv2.rectangle(frameOpencvDnn, (x1, y1), (x2, y2), (0, 255, 0), int(round(frameHeight / 150)), 8)
    return frameOpencvDnn, faceBoxes

@app.route("/userhome", methods=["GET", "POST"])
def userhome():
    msg = ""
    fn = ""
    st = ""
    act = request.args.get("act")

    if request.method == "POST":
        st = "1"
        file = request.files["file"]
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        fname = file.filename
        filename = secure_filename(fname)
        file.save(os.path.join("static/upload", filename))

        faceProto = "opencv_face_detector.pbtxt"
        faceModel = "opencv_face_detector_uint8.pb"
        ageProto = "age_deploy.prototxt"
        ageModel = "age_net.caffemodel"
        genderProto = "gender_deploy.prototxt"
        genderModel = "gender_net.caffemodel"

        MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
        ageList = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']
        genderList = ['Male', 'Female']

        faceNet = cv2.dnn.readNet(faceModel, faceProto)
        ageNet = cv2.dnn.readNet(ageModel, ageProto)
        genderNet = cv2.dnn.readNet(genderModel, genderProto)

        video = cv2.VideoCapture("static/upload/" + filename)
        padding = 20

        last_age = "25-32"
        while cv2.waitKey(1) < 0:
            hasFrame, frame = video.read()
            if not hasFrame:
                break

            resultImg, faceBoxes = highlightFace(faceNet, frame)
            if not faceBoxes:
                print("No face detected")
            for faceBox in faceBoxes:
                face = frame[max(0, faceBox[1]-padding):min(faceBox[3]+padding, frame.shape[0]-1),
                             max(0, faceBox[0]-padding):min(faceBox[2]+padding, frame.shape[1]-1)]
                blob = cv2.dnn.blobFromImage(face, 1.0, (227, 227), MODEL_MEAN_VALUES, swapRB=False)
                genderNet.setInput(blob)
                genderPreds = genderNet.forward()
                gender = genderList[genderPreds[0].argmax()]
                ageNet.setInput(blob)
                agePreds = ageNet.forward()
                age = ageList[agePreds[0].argmax()]
                last_age = age
                cv2.putText(resultImg, f"{gender}, {age}", (faceBox[0], faceBox[1]-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2, cv2.LINE_AA)

            fn = "D" + filename
            cv2.imwrite("static/upload/" + fn, resultImg)
            break

        with open("age.txt", "w") as ff:
            ff.write(last_age)

    return render_template("userhome.html", msg=msg, fn=fn, st=st)

@app.route("/test_cam", methods=["GET", "POST"])
def test_cam():
    msg = ""
    fn = ""
    st = ""
    vid = ""
    act = request.args.get("act")
    mycursor = mydb.cursor()
    with open("age.txt", "r") as ff:
        val = ff.read()
    return render_template("test_cam.html", msg=msg, st=st)

@app.route("/show_video", methods=["GET", "POST"])
def show_video():
    msg = ""
    fn = ""
    st = ""
    act = request.args.get("act")
    vid = request.args.get("vid")
    mycursor = mydb.cursor()

    with open("age.txt", "r") as ff:
        val = ff.read()

    mycursor.execute("SELECT * FROM upload_video where age=%s", (val,))
    data1 = mycursor.fetchall()
    mycursor.execute("SELECT * FROM upload_video where id=%s", (vid,))
    data2 = mycursor.fetchone()
    vfile = data2[2]
    with open("video.txt", "w") as f1:
        f1.write(vfile)
    with open("getframe.txt", "w") as ff:
        ff.write("1")
    with open("check.txt", "w") as ff:
        ff.write("1")
    return render_template("show_video.html", msg=msg, st=st, val=val, data1=data1, fn=fn, data2=data2)

@app.route("/test_pro3", methods=["GET", "POST"])
def test_pro3():
    msg = ""
    fn = ""
    st = ""
    vid = ""
    act = request.args.get("act")
    mycursor = mydb.cursor()
    try:
        if act == "1":
            with open("age.txt", "r") as ff:
                val = ff.read()
            mycursor.execute("SELECT * FROM upload_video where age=%s limit 0,1", (val,))
            data1 = mycursor.fetchone()
            vid = data1[0]
            vfile = data1[2]
            with open("video.txt", "w") as f1:
                f1.write(vfile)
            st = "1"
    except Exception:
        st = "2"
    return render_template("test_pro3.html", msg=msg, act=act, st=st, vid=vid)

@app.route("/test_pro4", methods=["GET", "POST"])
def test_pro4():
    msg = ""
    fn = ""
    st = ""
    vid = request.args.get("vid")
    with open("age.txt", "r") as ff:
        val = ff.read()
    with open("check.txt", "r") as ff:
        cc = ff.read()
    st = "1" if cc == "1" else "2"
    return render_template("test_pro4.html", msg=msg, st=st, vid=vid)

@app.route("/test_pro41", methods=["GET", "POST"])
def test_pro41():
    msg = ""
    fn = ""
    st = ""
    vid = request.args.get("vid")
    with open("age.txt", "r") as ff:
        val = ff.read()
    with open("check.txt", "r") as ff:
        cc = ff.read()
    st = "1" if cc == "1" else "2"
    return render_template("test_pro41.html", msg=msg, st=st, vid=vid)

@app.route("/page", methods=["GET", "POST"])
def page():
    msg = ""
    fn = ""
    st = ""
    vid = request.args.get("vid")
    with open("age.txt", "r") as ff:
        val = ff.read()
    with open("check.txt", "r") as ff:
        cc = ff.read()
    st = "1" if cc == "1" else "2"
    return render_template("page.html", msg=msg, st=st, vid=vid)

@app.route("/page2", methods=["GET", "POST"])
def page2():
    msg = ""
    fn = ""
    st = ""
    vid = request.args.get("vid")
    with open("age.txt", "r") as ff:
        val = ff.read()
    with open("check.txt", "r") as ff:
        cc = ff.read()
    st = "1" if cc == "1" else "2"
    return render_template("page2.html", msg=msg, st=st, vid=vid)

@app.route("/test_pro5", methods=["GET", "POST"])
def test_pro5():
    msg = ""
    fn = ""
    st = ""
    mess = ""
    vid = request.args.get("vid")
    with open("age.txt", "r") as ff:
        val = ff.read()
    with open("check.txt", "r") as ff:
        cc = ff.read()
    if cc == "1":
        st = "1"
    else:
        if cc == "2":
            mess = "Face Not Detected"
        elif cc == "3":
            mess = "Eye Closed"
        st = "2"
    return render_template("test_pro5.html", msg=msg, st=st, vid=vid, mess=mess)

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n")

@app.route("/video_feed")
def video_feed():
    return Response(gen(VideoCamera()), mimetype="multipart/x-mixed-replace; boundary=frame")

def gen2(camera2):
    while True:
        frame2 = camera2.get_frame()
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame2 + b"\r\n\r\n")

@app.route("/video_feed2")
def video_feed2():
    return Response(gen2(VideoCamera2()), mimetype="multipart/x-mixed-replace; boundary=frame")

def gen3(camera3):
    while True:
        frame3 = camera3.get_frame()
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame3 + b"\r\n\r\n")

@app.route("/video_feed3")
def video_feed3():
    return Response(gen3(VideoCamera3()), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
