from flask import Flask, render_template, request, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
import datetime


app = Flask(__name__)
app.url_map.slashes = False
app.config['DEBUG'] = True
app.config['ENV'] = 'development'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config["JWT_SECRET_KEY"] =  'dc7d98009d61ac52e4d1b64de55b7165'

db.init_app(app)
Migrate(app, db)
jwt = JWTManager(app)
CORS(app)

@app.route('/')
def root():
    return render_template('index.html')

@app.route('/api/register', methods=['POST'])
def register():


    #traigo los datos
    name=request.json.get('name', "")
    email=request.json.get('email')
    password=request.json.get('password')

    user = User.query.filter_by(email=email).first()
    if user : return jsonify({ "msg": " Existe una cuenta con este email. "}), 400

    #creo el usuario
    user = User()
    user.name = name
    user.email = email
    user.password = generate_password_hash(password)
    user.save()

    return jsonify({ "msg": "Usuario registrado, por favor, inicie sesión" }), 201

@app.route('/api/login', methods=['POST'])
def login():
    
    email=request.json.get('email')
    password=request.json.get('password')

    user = User.query.filter_by(email=email, isActive=True).first()
    if not user : return jsonify({ "msg": "Usuario y/o contraseña incorrectos. "}), 400

    if not check_password_hash(user.password, password): return jsonify({ "msg" : "Usuario y/o contraseña no se encuentra/n"})

    expire= datetime.timedelta(minutes=1)

    print(expire)

    access_token =  create_access_token(identity=user.email, expires_delta=expire)

    data = {
        "access_token" : access_token,
        "user" : user.serialize()
    }

    return jsonify(data), 200

@app.route('/api/users', methods=['GET'])
@jwt_required()
def users():

    users = User.query.all()
    users = list(map(lambda user : user.serialize(), users))

    return jsonify(users), 200

@app.route('/api/profile', methods=['GET'])
@jwt_required()
def profile():
    identity = get_jwt_identity()
    user = User.query.filter_by(email=identity).first()
    return jsonify({ "identity": identity, "user": user.serialize() }), 200

if __name__ == '__main__':
    app.run()