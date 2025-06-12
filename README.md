3) steps to replace sqlite database to mysql database:
   i) delete the existing database stored in instance
   ii) install pymysql by "pip install pymysql" int the bash terminal
   iii) replace the line >> app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:\\\database.db' to
                         >> app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/db_usermodel'
   iv) go to mysql, and with the help of query "create database usermodel_db" create a database having name usermodel_db.
   v) now run the existing code and create new data with the help of postman.
