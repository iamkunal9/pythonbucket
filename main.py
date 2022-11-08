
# iamkunal9 Here!

from flask import Flask, request
from flask_mysqldb import MySQL
from yaml import load, FullLoader
from os import urandom
from flask import jsonify
app = Flask(__name__)

mysql = MySQL(app)
db = load(open('/home/2021pietcskunal096/mysite/db.yaml'), Loader=FullLoader)
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
app.config['SECRET_KEY'] = urandom(24)

# @app.after_request
# def add_headers(response):
#     response.headers.add('Access-Control-Allow-Origin', '*')
#     response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization, data')
#     return response
@app.route('/')
def hello_world():
    return 'Hello World'
@app.route('/api/v1/bucket/data', methods=['POST'])
def test():
    bucketid = request.json["bid"]
    mode = request.json["mode"]
    cursor = mysql.connection.cursor()
    # carrier = request.json["carrier"]
    # email = request.json["email"]
    # location = request.json["location"]
    if mode == "create":
        cmd = f"insert into bucket values('{bucketid}','Null');"
    elif mode == "append":
        cursor.execute(f"select * from bucket where bid='{bucketid}'")
        bData = cursor.fetchone()
        
        bData = bData[1]+" "+request.json["data"]
        cmd = f"update bucket set data='{bData}' where bid='{bucketid}'"
    elif mode == "nRappend": #No repeat append
        cursor.execute(f"select * from bucket where bid='{bucketid}'")
        bData = cursor.fetchone()
        if str(request.json["data"]) not in bData[1].split(" "):
            bData = bData[1]+" "+request.json["data"]
            cmd = f"update bucket set data='{bData}' where bid='{bucketid}'"
    elif mode == "update":
        cmd = f"update bucket set data='{bData}' where bid='{bucketid}'"

    elif mode == "purge":
        cmd = f"delete from bucket where bid='{bucketid}'"
    elif mode == "remove":
        indx = request.json["data"]
        cursor.execute(f"select * from bucket where bid='{bucketid}'")
        bData = cursor.fetchone()
        bData = bData[1]
        bData = bData.split(" ")
        bData.remove(indx)
        bData = " ".join(bData)
        cmd = f"update bucket set data='{bData}' where bid='{bucketid}'"
    else:
        return "404"



    try:
        cursor.execute(cmd)
        mysql.connection.commit()
        cursor.close()
        return "ok "+mode
    except:
        return "exist"
@app.route('/api/v1/bucket/getData/<bid>', methods=['GET'])
def getData(bid):
    cursor = mysql.connection.cursor()
    # if oid[:32] != "d842040b1c5dc8c9752e013c75bd48e9":
    #     return "<h1>UNAUTHORISED</h1>"

    cursor.execute(f"select * from bucket where bid='{bid}'")
    bucket_data = cursor.fetchone()
    if bucket_data:
        data = {
            "resp":"200",
            "bucketid":bid,
            "data": bucket_data[1].split(" "),

        }
    else:
        data = {"resp":"404"}


    cursor.close()
    return jsonify(data)