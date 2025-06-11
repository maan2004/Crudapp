from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restful import Resource, Api, abort
import bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)

class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    phone = db.Column(db.Integer, unique=True)
    password = db.Column(db.String(80), nullable=False)
    status = db.Column(db.Boolean, default=True)

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UserModel
        load_instance = True

    password = ma.String(load_only=True, required=True)

user_schema = UserSchema()
users_schema = UserSchema(many=True)

def hash_password(plain_password):
    return bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

class Users(Resource):
    def get(self):
        users = UserModel.query.all()
        return users_schema.dump(users), 200

    def post(self):
        json_data = request.get_json()
        if not json_data:
            abort(400, message="No input data provided")

        try:
            user_data = user_schema.load(json_data)
        except Exception as e:
            return {'error': str(e)}, 422

        if UserModel.query.filter_by(email=user_data.email).first():
            abort(409, message="Email already exists")
        if UserModel.query.filter_by(name=user_data.name).first():
            abort(409, message="Name already exists")
        if user_data.phone and UserModel.query.filter_by(phone=user_data.phone).first():
            abort(409, message="Phone already exists")

        user_data.password = hash_password(user_data.password)

        db.session.add(user_data)
        db.session.commit()
        return user_schema.dump(user_data), 201

class User(Resource):
    def get(self, id):
        user = UserModel.query.get(id)
        if not user:
            abort(404, message="User not found")
        return user_schema.dump(user), 200

    def patch(self, id):
        user = UserModel.query.get(id)
        if not user:
            abort(404, message="User not found")

        json_data = request.get_json()
        if not json_data:
            abort(400, message="No input data provided")

        if 'name' in json_data:
            user.name = json_data['name']
        if 'email' in json_data:
            user.email = json_data['email']
        if 'phone' in json_data:
            user.phone = json_data['phone']
        if 'status' in json_data:
            user.status = json_data['status']
        if 'password' in json_data:
            user.password = hash_password(json_data['password'])

        db.session.commit()
        return user_schema.dump(user), 200

    def delete(self, id):
        user = UserModel.query.get(id)
        if not user:
            abort(404, message="User not found")

        db.session.delete(user)
        db.session.commit()
        return {'message': 'User deleted'}, 200

api.add_resource(Users, '/api/users/')
api.add_resource(User, '/api/users/<int:id>')

@app.route('/')
def home():
    return '<h1>Flask RestAPI</h1>'

if __name__ == '__main__':
    app.run(debug=True)
