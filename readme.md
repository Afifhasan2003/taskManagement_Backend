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



# testing

curl -X PATCH http://localhost:5001/projects/1/members/2/role \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc4NDMxOTY0NSwianRpIjoiMDQ5ODZiMDAtYTIzOC00NTdmLTliOWUtMzlhYjI5NjQwZWFjIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjEiLCJuYmYiOjE3ODQzMTk2NDUsImNzcmYiOiJjMWI2ZWI1ZC00NTkyLTQ5MmMtYjQyMy04NTEwMTcyNmExYTAiLCJleHAiOjE3ODQzMjA1NDV9.UJoY179r2vJrvO-59W1h52c1HDOhsT9ngPeyRdyuGD4" \
-H "Content-Type: application/json" \
-d '{"role":"admnn"}'



curl -X PUT http://localhost:5001/users/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc4NDI4Mzc1NSwianRpIjoiMGQ2ODFmNzUtYWE3NC00YmQ3LTk1NzQtMjk2NzdiMWU0NjNmIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjEiLCJuYmYiOjE3ODQyODM3NTUsImNzcmYiOiI5MDBiZDNlMi05ZjNkLTQzOWQtYjg1ZS03Yzg0ZTZmMjVmYTUiLCJleHAiOjE3ODQyODQ2NTV9.XZpQicZUux-LwvkB84KM5yh1bn54stnMhdZ8kp33nE8" \
  -H "Content-Type: application/json" \
  -d '{"email": "afifffff@test.com"}'


 curl -X POST http://localhost:5001/projects \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc4NDI4ODEyNCwianRpIjoiMzFiNjQyZDAtZWZmMC00M2ViLTk2NTMtN2M5MDM5MjNiZDgxIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjEiLCJuYmYiOjE3ODQyODgxMjQsImNzcmYiOiI3Mzk4NmM3NC1jNjIzLTQ1YTktYTJiNS1iNmRkNTllYWZjNTEiLCJleHAiOjE3ODQyODkwMjR9.tv9rn-3EuQAg0OgZ-6T-bekXWQ_A-M-ogrlbpoYM5CA" \
  -H "Content-Type: application/json" \
  -d '{"name": "sellervaiiii","description":"this is sellervai"}'

   curl -X POST http://localhost:5001/auth/refresh \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc4NDI4Mzc1NSwianRpIjoiYjE4OTVlYzAtNzRlMy00NDg3LWJjNjktZTdkNzZkYmQzYzEwIiwidHlwZSI6InJlZnJlc2giLCJzdWIiOiIxIiwibmJmIjoxNzg0MjgzNzU1LCJjc3JmIjoiNTMwMmVhNWMtMDQ4Yi00NjU2LTlkMzYtZTQwZWUxMzU4YWM5IiwiZXhwIjoxNzg2ODc1NzU1fQ.PmyMq4IbouxE_TviET-O-ly5fOVoKCDN67EMYx3PP6k"

  curl -X GET http://localhost:5001/projects \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc4NDI4OTI0MCwianRpIjoiMzM1YTczN2ItN2RjZi00ZGI0LTlkNTctZjIzZTBlZmQxZGI1IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjEiLCJuYmYiOjE3ODQyODkyNDAsImNzcmYiOiJiMzQxOGJjNC1kMzQ2LTQwY2UtODdiYy1jMmU5Yzk0NTcxNWIiLCJleHAiOjE3ODQyOTAxNDB9.QO2qhkWsQejbjsfRd1ZfCaRgZfjyP9qELtw0GNJR0TI" \
  -H "Content-Type: application/json"

    curl -X GET http://localhost:5001/projects/1 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc4NDI4OTI0MCwianRpIjoiMzM1YTczN2ItN2RjZi00ZGI0LTlkNTctZjIzZTBlZmQxZGI1IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjEiLCJuYmYiOjE3ODQyODkyNDAsImNzcmYiOiJiMzQxOGJjNC1kMzQ2LTQwY2UtODdiYy1jMmU5Yzk0NTcxNWIiLCJleHAiOjE3ODQyOTAxNDB9.QO2qhkWsQejbjsfRd1ZfCaRgZfjyP9qELtw0GNJR0TI" \
  -H "Content-Type: application/json"


  curl -X POST http://localhost:5001/projects/join \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc4NDMxNTc2MiwianRpIjoiM2Y3ZmIzZGUtNjcxZS00NTFlLTk1ZWItMThkMjdiNzFhNTNjIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjIiLCJuYmYiOjE3ODQzMTU3NjIsImNzcmYiOiJkY2E5ZWMwMy1kZTEwLTQxMDQtOGQ0ZS00MWVmNTQ2NjljZmMiLCJleHAiOjE3ODQzMTY2NjJ9.33h4wa5x8316BxuJs3lQtwHOopPOlgeJ3CKVsd6yXsM" \
-H "Content-TYpe: application/json" \
-d '{"join_code":"048818c8bcab"}'