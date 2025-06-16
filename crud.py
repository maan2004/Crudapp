from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restful import Resource, Api, abort
from marshmallow import fields, validate, validates_schema, ValidationError
import bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/db_usermodel'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)

class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    phone = db.Column(db.String(15), unique=True)
    password = db.Column(db.String(60), nullable=False)
    status = db.Column(db.Boolean, default=True)

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UserModel
        load_instance = True

    name = fields.String(required=True,validate=validate.Length(min=2))
    email = fields.Email(required=True, validate=validate.Email(error="Invalid email format."))
    phone = fields.String(validate=validate.Regexp(r"^\+?[1-9]\d{1,13}$", error="Invalid phone number."))
    password = fields.String(required=True, load_only=True)

    @validates_schema
    def validate_unique_fields(self, data, **kwargs):
        if 'email' in data and UserModel.query.filter_by(email=data['email']).first():
            raise ValidationError("Email already exists.", field_name="email")
        if 'phone' in data and UserModel.query.filter_by(phone=data['phone']).first():
            raise ValidationError("Phone already exists.", field_name="phone")

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
        except ValidationError as err:
            return {"errors": err.messages}, 422

        user_data.password = hash_password(user_data.password)
        db.session.add(user_data)
        db.session.commit()
        return user_schema.dump(user_data), 201

class UserSearch(Resource):
    def get(self):
        keyword = request.args.get('keyword')
        if not keyword:
            abort(400, message="Keyword is required")

        users = UserModel.query.filter(
            (UserModel.name.ilike(f"%{keyword}%")) |
            (UserModel.email.ilike(f"%{keyword}%")) |
            (UserModel.phone.ilike(f"%{keyword}%"))
        ).all()

        return users_schema.dump(users), 200

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

        if 'email' in json_data and json_data['email'] != user.email:
            if UserModel.query.filter_by(email=json_data['email']).first():
                abort(400, message="Email already exists")
            user.email = json_data['email']

        if 'phone' in json_data and json_data['phone'] != user.phone:
            if UserModel.query.filter_by(phone=json_data['phone']).first():
                abort(400, message="Phone already exists")
            user.phone = json_data['phone']

        if 'name' in json_data:
            user.name = json_data['name']
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
api.add_resource(UserSearch, '/api/usersearch/')
api.add_resource(User, '/api/users/<int:id>')

@app.route('/')
def home():
    return '<h1>Flask RestAPI</h1>'

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
