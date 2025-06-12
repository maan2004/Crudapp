3) steps to replace sqlite database to mysql database:
   i) delete the existing database stored in instance
   ii) install pymysql by "pip install pymysql" int the bash terminal
   iii) replace the line >> app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:\\\database.db' to
                         >> app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/db_usermodel'
   iv) go to mysql, and with the help of query "create database usermodel_db" create a database having name usermodel_db.
   v) now run the existing code and create new data with the help of postman.

4) HTTP codes: Informational (1xx), Success (2xx), Redirection (3xx), Client Error (4xx), and Server Error (5xx):
   i) (200, 201, 301, 302, 401-404, 500)
   i) 200 : The request was successful, and the server has sent the requested data. Used for: GET, PUT, PATCH, or DELETE requests that completed successfully. 
   ii) 201 : The request was successful, and a new resource has been created. Used for: POST requests where a new resource is added.
   iii) 301 : The requested resource has been permanently moved to a new location.
   iv) 302 : The requested resource has been temporarily moved to a new location.
   v) 401 : request unauthorized or Authentication is required or failed.
   vi) 402 : intended for digital payment systems. payment is needed before a client can access a resource or service.
   vii) 403 : forbidden, Authenticated but not allowed to access the resource.
   viii) 404 : Not Found, Meaning that Resource doesn’t exist.
   ix) 409 : Conflict, The request could not be completed due to a conflict with the current state of the target resource.
   x) 500 : Internal Server Error, Generic server error — something went wrong on the backend.
