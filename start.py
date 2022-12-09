import flask
from flask import Flask, render_template, request, redirect

from bson import json_util, ObjectId, DBRef
from datetime import datetime, timedelta

from pymongo.collection import Collection, ReturnDocument

from datetime import datetime 

from models import *

from flask import Flask, request, url_for, jsonify

from pymongo.errors import DuplicateKeyError
from pymongo import MongoClient

from objectid import PydanticObjectId

from dotenv import load_dotenv

import os

from utils import *


load_dotenv()


APP_DIR = os.path.abspath(os.path.dirname(__file__))
STATIC_FOLDER = os.path.join(APP_DIR, 'static')
TEMPLATE_FOLDER = os.path.join(APP_DIR, '')

app = Flask(__name__, static_folder=STATIC_FOLDER,
            template_folder=TEMPLATE_FOLDER,
            )

app.config["MONGO_URI"] = os.getenv("MONGO_URI")


#pymongo = PyMongo(app)
client = MongoClient(os.getenv("MONGO_URI"), connect=False)
db = client["Main"]

students: Collection = db["students"]
groups: Collection = db["groups"]


def redirect_url(default='index'):
    return request.args.get('next') or \
           request.referrer or \
           url_for(default)


@app.route('/students/', methods=["GET"])
def index():

    q = get_or_none(request, "qs", "")                
    menu_item = "students"
    
    filtered = students.find()

    if q:
        filtered = students.find({"$or": [
            {"fullname": {"$regex": q, "$options": "i"}},
            {"age": {"$regex": q, "$options": "i"}},            
        ]})

    data = []
    data_groups = []
    fields = ["id", "age", "fullname", "group"]                        
    fields_for_create = ["age", "fullname"]
    

    for item in filtered:        
        #group_name = None if not item["group"] else item["group"]["$id"]  
        print(item)      
        group_id  = item["group"].id        
        group_name = groups.find_one({"_id": ObjectId(group_id)})["name"]
        data.append([item["_id"], item["age"], item["fullname"], group_name])

    for group in groups.find():
        data_groups.append({"name": group["name"], "_id": group["_id"]})
        
    return render_template('templates/index.html',
                            data=data,
                            fields=fields,
                            fields_for_create=fields_for_create,
                            menu_item=menu_item,
                            groups=data_groups,
                            qs=q)


@app.route("/students/", methods=["POST"])
def add_student():
    data = {
        "fullname": request.form['fullname'],        
        "age": request.form['age'],        
        "group": DBRef("groups", ObjectId(request.form['group']), "Main"),
    } 

    #student = Student(**data)
    insert_result = students.insert_one(data)
    #student.id = PydanticObjectId(str(insert_result.inserted_id))        

    return redirect(redirect_url())


@app.route("/students/get", methods=["GET"])
def get_students():
    cursor = students.find()
    data = {
        "students": []
    }
    for item in cursor:
        data["students"].append(Student(**item).to_json())
    print(data)
    return data


@app.route("/students/<string:slug>", methods=["GET"])
def get_student(slug):
    student = students.find_one_or_404({"slug": slug})
    return Student(**student).to_json()


@app.route("/students/update/", methods=["PUT", "POST"])
def update_student():
    _id = request.form['id']    

    data = {
        "fullname": request.form['fullname'],
        "age": request.form['age'],
        "group": DBRef("groups", ObjectId(request.form['group']), "Main")
    }

    
    updated_doc = students.find_one_and_update(
        {"_id": ObjectId(_id)},
        {"$set": data},
        return_document=ReturnDocument.AFTER,
    )    
    return redirect(redirect_url())
    


@app.route("/students/delete", methods=["DELETE", "POST"])
def delete_student():
    _id = request.form['id']

    deleted_student = students.find_one_and_delete(
        {"_id": ObjectId(_id)},
    )
    if deleted_student:
        return redirect(redirect_url())
    else:
        flask.abort(404, "Student not found")




@app.route("/groups/", methods=["POST"])
def add_group():    
    data = {
        "name": request.form['name'],        
    }    

    group = Group(**data)
    insert_result = groups.insert_one(group.to_bson())
    group.id = PydanticObjectId(str(insert_result.inserted_id))    

    return redirect(redirect_url('groups_page'))


@app.route("/groups/", methods=["GET"])
def groups_page():
    q = get_or_none(request, "qs", "")                
    menu_item = "groups"
    
    filtered = groups.find()    

    if q:
        filtered = groups.find({"name": {"$regex": q, "$options": "i"}})

    data = []
    fields = ["id", "name"]                        
    fields_for_create = ["name"]
    

    for item in filtered:                
        data.append([item["_id"], item["name"]])
    
    print(data)
        
    return render_template('templates/index.html',
                            data=data,
                            fields=fields,
                            fields_for_create=fields_for_create,
                            menu_item=menu_item,                            
                            qs=q)

@app.route("/groups/get", methods=["GET"])
def get_groups():
    cursor = groups.find()
    data = {
        "groups": []
    }
    for item in cursor:
        data["groups"].append(Group(**item).to_json())
    print(data)
    return data


@app.route("/groups/<string:slug>", methods=["GET"])
def get_group(slug):
    group = groups.find_one_or_404({"slug": slug})
    return Student(**group).to_json()


@app.route("/groups/update", methods=["PUT", "POST"])
def update_group():
    _id = request.form['id']    

    data = {        
        "name": request.form['name']
    }

    group = Group(**data) 
    updated_doc = groups.find_one_and_update(
        {"_id": ObjectId(_id)},
        {"$set": group.to_bson()},
        return_document=ReturnDocument.AFTER,
    )
    if updated_doc:
        return redirect(redirect_url('groups_page'))
    else:
        flask.abort(404, "Group not found")


@app.route("/groups/delete", methods=["DELETE", "POST"])
def delete_group():
    _id = request.form['id']

    deleted_group = groups.find_one_and_delete(
        {"_id": ObjectId(_id)},
    )
    if deleted_group:
        return redirect(redirect_url('groups_page'))
    else:
        flask.abort(404, "Group not found")


@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404


@app.errorhandler(DuplicateKeyError)
def resource_not_found(e):
    return jsonify(error=f"Duplicate key error."), 400