# connect to db
  psql -U afif -d taskflowdb

# data database in sql file
pg_dump -U afif taskflowdb > backup.sql

# register new user
curl -X POST http://localhost:5001/auth/register \
-H "Content-Type: application/json" \
-d '{"name": "Afif", "username": "afif123", "email": "afif@test.com", "phone": "01700000000", "password": "1234"}'

# log in user
curl -X POST http://localhost:5001/auth/login \
-H "Content-Type: application/json" \
-d '{"email": "afif@test.com", "password": "1234"}'

# get new token
   curl -X POST http://localhost:5001/auth/refresh \
  -H "Authorization: Bearer refreshe_token_here"


# get users 
 get user
 curl -X GET http://localhost:5001/users/me \
  -H "Authorization: Bearer token_here"

# update user

 curl -X PUT http://localhost:5001/users/me \
  -H "Authorization: Bearer token_here" \
  -H "Content-Type: application/json" \
  -d '{"email": "afifffff@test.com"}'


# create project
 curl -X POST http://localhost:5001/projects \
  -H "Authorization: Bearer token_here" \
  -H "Content-Type: application/json" \
  -d '{"name": "sellervai","description":"this is sellervai"}'


# get all project by user_id
 curl -X GET http://localhost:5001/projects \
  -H "Authorization: Bearer token_here" \
  -H "Content-Type: application/json" \
 

# get project by project_id
 curl -X GET http://localhost:5001/projects/give_id_here \
  -H "Authorization: Bearer token_here" \
  -H "Content-Type: application/json" \


# join project by code
curl -X POST http://localhost:5001/projects/join \
-H "Authorization: Bearer token_here" \
-H "Content-TYpe: application/json" \
-d '{"join_code":"048818c8bcab"}'


# update role 
curl -X PATCH http://localhost:5001//projects/Project_id_here/members/users_id_here/role
-H "Authorization: Bearer token_here" \
-H "Content-TYpe: application/json" \
-d '{"role":"add_role_here"}'



# create task
curl -X POST http://localhost:5001/tasks \
-H "Authorization: Bearer your_token_here" \
-H "Content-Type: application/json" \
-d '{"project_id": 1, "title": "My first task", "priority": "high"}'


#  get all tasks
curl -X GET "http://localhost:5001/tasks?project_id=1" \
-H "Authorization: Bearer your_token"

# get specific task
curl -X GET http://localhost:5001/tasks/1 \
-H "Authorization: Bearer your_token"

# update task
curl -X PUT http://localhost:5001/tasks/1 \
-H "Authorization: Bearer your_token" \
-H "Content-Type: application/json" \
-d '{"title": "Updated title", "priority": "low"}'

# change status
curl -X PATCH http://localhost:5001/tasks/1/status \
-H "Authorization: Bearer your_token" \
-H "Content-Type: application/json" \
-d '{"status": "in_progress"}'


# add comment
curl -X POST http://localhost:5001/comments \
-H "Authorization: Bearer your_token" \
-H "Content-Type: application/json" \
-d '{"task_id": 1, "content": "This is a comment"}'


# get comments of a task
curl -X GET "http://localhost:5001/comments?task_id=1" \
-H "Authorization: Bearer your_token"

# delete a comment
curl -X DELETE http://localhost:5001/comments/1 \
-H "Authorization: Bearer your_token"


# testing

   curl -X POST http://localhost:5001/auth/refresh \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc4NTY0Njk5MiwianRpIjoiNTA4NWNkYjktOWE5Yy00MDVhLWI4MGEtYjczZTIyODExMjExIiwidHlwZSI6InJlZnJlc2giLCJzdWIiOiIzIiwibmJmIjoxNzg1NjQ2OTkyLCJjc3JmIjoiMmYyYWY0OTktODhiYS00MTRkLWE0YzEtZjYwMDM2YjVhMjRkIiwiZXhwIjoxNzg4MjM4OTkyfQ._X031wbkj2nPkU7QHXfls7pa7dt-0Zj87CY0xFXTrzI"



curl -X POST http://localhost:5001/comments \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc4NTY2NDQ5OCwianRpIjoiNTkyZGMyODMtY2MxNS00MTUzLTk0OWQtN2ZhYWViOTJjNzhkIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjMiLCJuYmYiOjE3ODU2NjQ0OTgsImNzcmYiOiJiY2M0YjNkOS0zOTE5LTRiY2EtYWZhMy05NjY0YTQwYWU2YWMiLCJleHAiOjE3ODU2NjUzOTh9.BPtLicpQ6bT4bHQD5EzigMA4UatF2kLDfja84ycf-X8" \
-H "Content-Type: application/json" \
-d '{"task_id": 3, "content": "This is first comment in task 3"}'

curl -X GET "http://localhost:5001/comments?task_id=3" \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc4NTY2NDQ5OCwianRpIjoiNTkyZGMyODMtY2MxNS00MTUzLTk0OWQtN2ZhYWViOTJjNzhkIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjMiLCJuYmYiOjE3ODU2NjQ0OTgsImNzcmYiOiJiY2M0YjNkOS0zOTE5LTRiY2EtYWZhMy05NjY0YTQwYWU2YWMiLCJleHAiOjE3ODU2NjUzOTh9.BPtLicpQ6bT4bHQD5EzigMA4UatF2kLDfja84ycf-X8"

curl -X DELETE http://localhost:5001/comments/2 \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc4NTY2NDQ5OCwianRpIjoiNTkyZGMyODMtY2MxNS00MTUzLTk0OWQtN2ZhYWViOTJjNzhkIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjMiLCJuYmYiOjE3ODU2NjQ0OTgsImNzcmYiOiJiY2M0YjNkOS0zOTE5LTRiY2EtYWZhMy05NjY0YTQwYWU2YWMiLCJleHAiOjE3ODU2NjUzOTh9.BPtLicpQ6bT4bHQD5EzigMA4UatF2kLDfja84ycf-X8"