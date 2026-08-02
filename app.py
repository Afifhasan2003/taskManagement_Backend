from flask import Flask, request, jsonify
import bcrypt
from db import conn
from psycopg2.extras import RealDictCursor
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt, get_jwt_identity
import secrets
from tasks import tasks_bp
from comments import comments_bp

from dotenv import load_dotenv
import os

load_dotenv()



app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.register_blueprint(tasks_bp)
app.register_blueprint(comments_bp)


jwt = JWTManager(app)

@app.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data['name']
    username = data['username']
    email = data['email']
    phone = data['phone']
    password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        "INSERT INTO users (name, username, email, phone, password) VALUES (%s, %s, %s, %s, %s)",
        (name, username, email, phone, password)
    )
    conn.commit()
    cursor.close()
    
    return jsonify({"message": "User registered successfully"}), 201


@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    
    if user is None:
        return jsonify({"message": "User not found"}), 404
    
    if not bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        return jsonify({"message": "Wrong password"}), 401
    
    access_token = create_access_token(identity=str(user['id']))
    refresh_token = create_refresh_token(identity=str(user['id']))
    return jsonify({"message": "Login successful", "access_token": access_token, "refresh_token": refresh_token}), 200



@app.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify({"access_token": access_token}), 200


@app.route('/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    token = get_jwt()['jti']
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("INSERT INTO blacklisted_tokens (token) VALUES (%s)", (token,))
    conn.commit()
    cursor.close()
    
    return jsonify({"message": "Logged out successfully"}), 200



# now starting user endpoints

@app.route('/users/me', methods=['GET'])
@jwt_required()
def get_me():
    user_id = get_jwt_identity()
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT id, name, username, email, phone, created_at FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    
    if user is None:
        return jsonify({"message": "User not found"}), 404
    
    return jsonify(user), 200



@app.route('/users/me', methods=['PUT'])
@jwt_required()
def update_me():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    allowed_fields = ['name', 'username', 'email', 'phone']
    updates = {k: v for k, v in data.items() if k in allowed_fields}
        # map of field that are allowed to be updated and their new values eg, {'name': 'hasan', 'email': 'hasan@example.com'}
    
    if not updates:
        return jsonify({"message": "No valid fields to update"}), 400
    
    set_clause = ", ".join(f"{k} = %s" for k in updates.keys())     # output: "name = %s, email = %s"
    values = list(updates.values()) + [user_id]     #specific values in sql (eg, ['hasan', 'hasan@example.com', 1])
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        f"UPDATE users SET {set_clause} WHERE id = %s RETURNING id, name, username, email, phone, created_at",
        values  
        #here sending the sql, and values separetely to avoid sql injection, the values will be substituted in the sql query safely by the database driver
    )
    updated_user = cursor.fetchone()
    conn.commit()
    cursor.close()
    
    return jsonify(updated_user), 200



# PROJECTS ENDPOINTS


@app.route('/projects', methods=['POST'])
@jwt_required()
def create_project():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    name = data.get('name')
    description = data.get('description', '')
    
    if not name:
        return jsonify({"message": "Project name is required"}), 400
    
    join_code = secrets.token_hex(6)
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute(
        "INSERT INTO projects (name, description, join_code, created_by) VALUES (%s, %s, %s, %s) RETURNING *",
        (name, description, join_code, user_id)
    )
    project = cursor.fetchone()
    
    cursor.execute(
        "INSERT INTO project_members (project_id, user_id, role) VALUES (%s, %s, %s)",
        (project['id'], user_id, 'admin')
    )
    
    conn.commit()
    cursor.close()
    
    return jsonify(project), 201


@app.route('/projects', methods=['GET'])
@jwt_required()
def get_projects():
    user_id = get_jwt_identity()
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("""
        SELECT p.*, pm.role 
        FROM projects p
        JOIN project_members pm ON p.id = pm.project_id
        WHERE pm.user_id = %s
    """, (user_id,))
    projects = cursor.fetchall()
    if not projects:
        return jsonify({"message": "No projects found"}), 404
    cursor.close()
    
    return jsonify(projects), 200


@app.route('/projects/<int:project_id>', methods=['GET'])
@jwt_required()
def get_project(project_id):
    user_id = get_jwt_identity()
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute(
        "SELECT * FROM project_members WHERE project_id = %s AND user_id = %s",
        (project_id, user_id)
    )
    member = cursor.fetchone()
    
    if member is None:
        cursor.close()
        return jsonify({"message": "Access denied"}), 403
    
    cursor.execute("SELECT * FROM projects WHERE id = %s", (project_id,))
    project = cursor.fetchone()
    cursor.close()
    
    if project is None:
        return jsonify({"message": "Project not found"}), 404
    
    return jsonify(project), 200



@app.route('/projects/<int:project_id>', methods=['PUT'])
@jwt_required()
def update_project(project_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute(
        "SELECT * FROM project_members WHERE project_id = %s AND user_id = %s",
        (project_id, user_id)
    )
    member = cursor.fetchone()
    
    if member is None:
        cursor.close()
        return jsonify({"message": "Access denied"}), 403
    
    if member['role'] != 'admin':
        cursor.close()
        return jsonify({"message": "Only admins can update the project"}), 403
    
    allowed_fields = ['name', 'description']
    updates = {k: v for k, v in data.items() if k in allowed_fields}
    
    if not updates:
        cursor.close()
        return jsonify({"message": "No valid fields to update"}), 400
    
    set_clause = ", ".join(f"{k} = %s" for k in updates.keys())
    values = list(updates.values()) + [project_id]
    
    cursor.execute(
        f"UPDATE projects SET {set_clause} WHERE id = %s RETURNING *",
        values
    )
    updated_project = cursor.fetchone()
    conn.commit()
    cursor.close()
    
    return jsonify(updated_project), 200


@app.route('/projects/<int:project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    user_id = get_jwt_identity()
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute(
        "SELECT * FROM project_members WHERE project_id = %s AND user_id = %s",
        (project_id, user_id)
    )
    member = cursor.fetchone()
    
    if member is None:
        cursor.close()
        return jsonify({"message": "Access denied"}), 403
    
    if member['role'] != 'admin':
        cursor.close()
        return jsonify({"message": "Only admins can delete the project"}), 403
    
    cursor.execute("DELETE FROM projects WHERE id = %s", (project_id,))
    conn.commit()
    cursor.close()
    
    return jsonify({"message": "Project deleted successfully"}), 200



@app.route('/projects/<int:project_id>/code', methods=['GET'])
@jwt_required()
def get_join_code(project_id):
    user_id = get_jwt_identity()
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute(
        "SELECT * FROM project_members WHERE project_id = %s AND user_id = %s",
        (project_id, user_id)
    )
    member = cursor.fetchone()
    
    if member is None:
        cursor.close()
        return jsonify({"message": "Access denied"}), 403
    
    if member['role'] != 'admin':
        cursor.close()
        return jsonify({"message": "Only admins can see the join code"}), 403
    
    cursor.execute("SELECT join_code FROM projects WHERE id = %s", (project_id,))
    project = cursor.fetchone()
    cursor.close()
    
    return jsonify({"join_code": project['join_code']}), 200




@app.route('/projects/join', methods=['POST'])
@jwt_required()
def join_by_code():
    user_id = get_jwt_identity()
    data = request.get_json()
    join_code = data.get('join_code')

    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("select id from projects where join_code = %s",(join_code,))
    project = cursor.fetchone()
    if project is None:
        return jsonify({"message": "join code is invalid"}),404

    p_id = project['id']
    cursor.execute("select * from project_members where project_id = %s and user_id = %s",(p_id,user_id))
    member = cursor.fetchone()
    if member:
        return jsonify({"message":"user already in the project"}),400

    cursor.execute("insert into project_members (project_id, user_id, role) values (%s ,%s , %s) ",(p_id,user_id, 'member'))
    conn.commit()
    cursor.close()
    return jsonify({"message":" successfully joined"}),201


@app.route('/projects/<int:project_id>/members/<int:target_user_id>/role', methods =['PATCH'])
@jwt_required()
def update_member_role(project_id,target_user_id):
    my_id = get_jwt_identity()
    data = request.get_json()
    newRole = data.get('role')

    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("select * from project_members where project_id = %s and user_id = %s",(project_id,my_id))
    member = cursor.fetchone()
    if not member:
        return jsonify({"message":"you are not in this project"}),403
    if member['role']!='admin':
        return jsonify({"message":"only admin can update role"}),403


    cursor.execute("select * from project_members where project_id = %s and user_id = %s",(project_id,target_user_id))
    otherMember = cursor.fetchone()
    
    if not otherMember:
        return jsonify({"message":"member does not exist in this project yet"}),404
    if newRole not in ['admin', 'member']:
        return jsonify({"message": "Invalid role"}),400

    if otherMember['role'] == newRole:
        return jsonify({"message":"already of this role"}),400
    
    cursor.execute(
    "UPDATE project_members SET role = %s WHERE project_id = %s AND user_id = %s",
    (newRole, project_id, target_user_id))

    conn.commit()
    cursor.close()
    return jsonify ({"message":"successfully changed role"}),200

    








if __name__ == "__main__":
    app.run(debug=True, port=5001)
