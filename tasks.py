from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import conn
from psycopg2.extras import RealDictCursor

tasks_bp = Blueprint('tasks', __name__)


@tasks_bp.route('/tasks', methods=['POST'])
@jwt_required()
def create_task():
    user_id = get_jwt_identity()
    data = request.get_json()

    project_id = data.get('project_id')
    title = data.get('title')
    if not project_id:
        return jsonify({"message": "project_id not found"}), 400
    if not title:
        return jsonify({"message": "title not found"}), 400

    description = data.get('description')
    priority = data.get('priority')
    tag = data.get('tag')
    deadline = data.get('deadline')
    assigned_to = data.get('assigned_to')

    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM project_members WHERE project_id = %s AND user_id = %s", (project_id, user_id))
    member = cursor.fetchone()

    if member is None:
        cursor.close()
        return jsonify({"message": "user is not in this project"}), 403

    cursor.execute(
        "INSERT INTO tasks (project_id, title, description, priority, tag, deadline, assigned_to, created_by) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING *",
        (project_id, title, description, priority, tag, deadline, assigned_to, user_id)
    )
    task = cursor.fetchone()
    conn.commit()
    cursor.close()
    return jsonify(task), 201


@tasks_bp.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    user_id = get_jwt_identity()
    project_id = request.args.get('project_id')

    if not project_id:
        return jsonify({"message": "project_id is required"}), 400

    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM project_members WHERE project_id = %s AND user_id = %s", (project_id, user_id))
    member = cursor.fetchone()

    if member is None:
        cursor.close()
        return jsonify({"message": "Access denied"}), 403

    cursor.execute("SELECT * FROM tasks WHERE project_id = %s", (project_id,))
    tasks = cursor.fetchall()
    cursor.close()
    return jsonify(tasks), 200


@tasks_bp.route('/tasks/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    user_id = get_jwt_identity()

    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    task = cursor.fetchone()

    if task is None:
        cursor.close()
        return jsonify({"message": "Task not found"}), 404

    cursor.execute("SELECT * FROM project_members WHERE project_id = %s AND user_id = %s", (task['project_id'], user_id))
    member = cursor.fetchone()

    if member is None:
        cursor.close()
        return jsonify({"message": "Access denied"}), 403

    cursor.close()
    return jsonify(task), 200


@tasks_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    user_id = get_jwt_identity()
    data = request.get_json()

    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    task = cursor.fetchone()

    if task is None:
        cursor.close()
        return jsonify({"message": "Task not found"}), 404

    cursor.execute("SELECT * FROM project_members WHERE project_id = %s AND user_id = %s", (task['project_id'], user_id))
    member = cursor.fetchone()

    if member is None:
        cursor.close()
        return jsonify({"message": "Access denied"}), 403

    if str(task['created_by']) != str(user_id) and member['role'] != 'admin':
        cursor.close()
        return jsonify({"message": "Only the task creator or admin can edit this task"}), 403

    allowed_fields = ['title', 'description', 'priority', 'tag', 'deadline', 'assigned_to']
    updates = {k: v for k, v in data.items() if k in allowed_fields}

    if not updates:
        cursor.close()
        return jsonify({"message": "No valid fields to update"}), 400

    updates['updated_at'] = 'NOW()'
    set_clause = ", ".join(f"{k} = %s" for k in updates.keys())
    values = list(updates.values()) + [task_id]

    cursor.execute(f"UPDATE tasks SET {set_clause} WHERE id = %s RETURNING *", values)
    updated_task = cursor.fetchone()
    conn.commit()
    cursor.close()
    return jsonify(updated_task), 200


@tasks_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    user_id = get_jwt_identity()

    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    task = cursor.fetchone()

    if task is None:
        cursor.close()
        return jsonify({"message": "Task not found"}), 404

    cursor.execute("SELECT * FROM project_members WHERE project_id = %s AND user_id = %s", (task['project_id'], user_id))
    member = cursor.fetchone()

    if member is None:
        cursor.close()
        return jsonify({"message": "Access denied"}), 403

    if str(task['created_by']) != str(user_id) and member['role'] != 'admin':
        cursor.close()
        return jsonify({"message": "Only the task creator or admin can delete this task"}), 403

    cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    conn.commit()
    cursor.close()
    return jsonify({"message": "Task deleted successfully"}), 200


@tasks_bp.route('/tasks/<int:task_id>/status', methods=['PATCH'])
@jwt_required()
def update_task_status(task_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    new_status = data.get('status')

    if new_status not in ['todo', 'in_progress', 'done']:
        return jsonify({"message": "Invalid status. Must be todo, in_progress, or done"}), 400

    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    task = cursor.fetchone()

    if task is None:
        cursor.close()
        return jsonify({"message": "Task not found"}), 404

    cursor.execute("SELECT * FROM project_members WHERE project_id = %s AND user_id = %s", (task['project_id'], user_id))
    member = cursor.fetchone()

    if member is None:
        cursor.close()
        return jsonify({"message": "Access denied"}), 403

    if str(task['assigned_to']) != str(user_id) and member['role'] != 'admin':
        cursor.close()
        return jsonify({"message": "Only the assignee or admin can change status"}), 403

    cursor.execute(
        "UPDATE tasks SET status = %s, updated_at = NOW() WHERE id = %s RETURNING *",
        (new_status, task_id)
    )
    updated_task = cursor.fetchone()
    conn.commit()
    cursor.close()
    return jsonify(updated_task), 200