from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import conn
from psycopg2.extras import RealDictCursor

comments_bp = Blueprint('comments', __name__)


@comments_bp.route('/comments', methods=['POST'])
@jwt_required()
def add_comment():
    user_id = get_jwt_identity()
    data = request.get_json()

    task_id = data.get('task_id')
    content = data.get('content')

    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("select project_id from tasks where id = %s",(task_id,))
    task = cursor.fetchone()
    if task is None:
        cursor.close()
        return jsonify({"message":"task not found"}),400
    project_id = task['project_id']

    cursor.execute("select * from project_members where user_id = %s and project_id = %s",(user_id,project_id))
    project_user = cursor.fetchone()

    if project_user is None:
        cursor.close()
        return jsonify({"message":"user not in project"}),400

    cursor.execute("insert into comments (task_id, user_id, content) values (%s, %s, %s) returning *",
                   (task_id, user_id,content))

    comment = cursor.fetchone()
    conn.commit()
    cursor.close()
    return jsonify(comment),201


@comments_bp.route('/comments', methods=['GET'])
@jwt_required()
def get_comments():
    user_id = get_jwt_identity()
    task_id = request.args.get('task_id')

    if not task_id:
        return jsonify({"message": "task_id is required"}), 400

    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT project_id FROM tasks WHERE id = %s", (task_id,))
    task = cursor.fetchone()

    if task is None:
        cursor.close()
        return jsonify({"message": "Task not found"}), 404

    cursor.execute("SELECT * FROM project_members WHERE project_id = %s AND user_id = %s", (task['project_id'], user_id))
    member = cursor.fetchone()

    if member is None:
        cursor.close()
        return jsonify({"message": "Access denied"}), 403

    cursor.execute("SELECT * FROM comments WHERE task_id = %s ORDER BY created_at ASC", (task_id,))
    comments = cursor.fetchall()
    cursor.close()
    return jsonify(comments), 200


@comments_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    user_id = get_jwt_identity()

    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM comments WHERE id = %s", (comment_id,))
    comment = cursor.fetchone()

    if comment is None:
        cursor.close()
        return jsonify({"message": "Comment not found"}), 404

    cursor.execute("SELECT project_id FROM tasks WHERE id = %s", (comment['task_id'],))
    task = cursor.fetchone()

    cursor.execute("SELECT * FROM project_members WHERE project_id = %s AND user_id = %s", (task['project_id'], user_id))
    member = cursor.fetchone()

    if member is None:
        cursor.close()
        return jsonify({"message": "Access denied"}), 403

    if str(comment['user_id']) != str(user_id) and member['role'] != 'admin':
        cursor.close()
        return jsonify({"message": "Only the comment author or admin can delete this comment"}), 403

    cursor.execute("DELETE FROM comments WHERE id = %s", (comment_id,))
    conn.commit()
    cursor.close()
    return jsonify({"message": "Comment deleted successfully"}), 200