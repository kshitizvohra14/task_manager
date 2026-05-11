from flask import Blueprint, request, jsonify
from models import db, Task

task_bp = Blueprint('tasks', __name__)

# Add Task
@task_bp.route('/tasks', methods=['POST'])
def add_task():

    data = request.json

    task = Task(
        title=data['title'],
        description=data['description'],
        priority=data['priority'],
        status=data['status']
    )

    db.session.add(task)
    db.session.commit()

    return jsonify({"message": "Task Added"})
@task_bp.route('/tasks', methods=['GET'])
def get_tasks():

    tasks = Task.query.all()

    result = []

    for task in tasks:
        result.append({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "status": task.status
        })

    return jsonify(result)
@task_bp.route('/tasks/<int:id>', methods=['PUT'])
def update_task(id):

    task = Task.query.get(id)

    data = request.json

    task.status = data['status']

    db.session.commit()

    return jsonify({"message": "Task Updated"})
@task_bp.route('/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):

    task = Task.query.get(id)

    db.session.delete(task)
    db.session.commit()

    return jsonify({"message": "Task Deleted"})
from extensions import socketio
socketio.emit('task_update', {
    'message': 'Task Updated'
})