import datetime

from flask import Flask, request, jsonify, Response
from bson.son import SON
from flask_pymongo import PyMongo
from pprint import pprint
from bson import json_util

app = Flask(__name__)
app.config['MONGO_URI'] = "mongodb://localhost:27017/magic_base"
mongo = PyMongo(app)


@app.route('/get_user/', methods=['POST'])
def get_user():
    # поиск пользователя
    # проверка на существования данного пользователя
    user_id = request.json['user_id']
    user = mongo.db.employee.find_one({"tg_chat_id": int(user_id)})
    response = json_util.dumps(user)
    return Response(response, mimetype='application/json')


@app.route('/get_roles/', methods=['GET'])
def get_roles():
    # все роли для регистрации
    user = mongo.db.role.find()
    response = json_util.dumps(user)
    return Response(response, mimetype='application/json')


@app.route('/create_employee/', methods=['POST'])
def create_employee():
    # регистрация пользователя
    tg_chat_id = request.json['tg_chat_id'],
    name = request.json['name'],
    last_name = request.json['last_name'],
    department = request.json['department'],
    role = request.json["role"],
    employee = {"tg_chat_id": tg_chat_id,
                "name": name,
                "last_name": last_name,
                "department": [department[0]],
                "role": [role[0]]
                }
    employee = mongo.db.employee.update({'tg_chat_id': employee['tg_chat_id']}, {"$set": employee}, upsert=True)
    employee['role'] = role[0]['name']
    response = json_util.dumps(employee)

    return Response(response, mimetype='application/json')


@app.route('/get_departments/', methods=['GET'])
def get_departments():
    # все департаменты для регистрации
    user = mongo.db.department.find()
    response = json_util.dumps(user)
    return Response(response, mimetype='application/json')


@app.route('/get_staff_by_manager/', methods=['POST'])
def get_staff_by_manager():
    # все сотрудники отдела исключая менеджера
    department = request.json['department'],
    tg_chat_id = request.json['tg_chat_id'],
    staff = mongo.db.employee.find(
        {"department": SON([("name", department[0])]),
         "tg_chat_id": {"$ne": tg_chat_id[0]}})
    response = json_util.dumps(staff)
    return Response(response, mimetype='application/json')


def serialize_tag(manager_id, employee_id, title, comment, deadline):
    return {
        'author': {"tg_chat_id": manager_id[0]},
        'maker': {"tg_chat_id": employee_id[0]},
        'title': title[0],
        'comment': comment[0],
        'deadline': deadline
    }


def get_deadline(deadline):
    time = {'завтра': 1, 'послезавтра': 2, 'неделя': 7}
    return datetime.datetime.today() + datetime.timedelta(days=time[deadline])


@app.route('/create_task/', methods=['POST'])
def create_task():
    manager_id = request.json.get('manager_id').get('tg_chat_id'),
    employee_id = request.json.get('employee_id').get('tg_chat_id'),
    title = request.json.get('title'),
    comment = request.json.get('comment'),
    deadline = request.json.get('deadline')

    deadline_time = get_deadline(deadline)
    print(deadline_time)
    print(type(deadline_time))
    print('-------')
    serialized_task = serialize_tag(manager_id, employee_id, title, comment, deadline_time)

    print(serialized_task)
    print('serialized_task---------')

    task = mongo.db.task.update({}, {"$set": serialized_task}, upsert=True)
    print(task)

    response = json_util.dumps(task)
    Response(response, mimetype='application/json')


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)
