from flask import Blueprint, jsonify
from models import Task
import pandas as pd

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics')
def analytics():

    tasks = Task.query.all()

    data = []

    for task in tasks:

        data.append({
            "status": task.status
        })

    df = pd.DataFrame(data)

    total = len(df)

    completed = len(df[df['status'] == 'done'])

    pending = len(df[df['status'] == 'pending'])

    in_progress = len(df[df['status'] == 'in-progress'])

    completion_percentage = (
        completed / total * 100
    ) if total > 0 else 0

    return jsonify({

        "Total Tasks": total,

        "Completed Tasks": completed,

        "Pending Tasks": pending,

        "In Progress Tasks": in_progress,

        "Completion Percentage": round(
            completion_percentage,
            1
        )

    })