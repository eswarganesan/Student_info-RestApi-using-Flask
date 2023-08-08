from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os


app=Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(basedir,'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] =False

db = SQLAlchemy(app)
ma = Marshmallow(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    contact = db.Column(db.String(40), unique=True)

    def __init__(self, name, contact):
        self.name = name
        self.contact = contact

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User

user_schema = UserSchema()
users_schema = UserSchema(many=True)

def credentials(uname, passw):
    if uname == 'Esh' and passw == 'ESWAR':
        return True
    return False

@app.route('/userd', methods=['POST'])
def add_user():
    auth = request.authorization

    # if not auth or not credentials(auth.uname, auth.passw):
    #     return jsonify("Authentication Required !!!")   

    data = request.get_json()
    name = data.get('name')
    contact = data.get('contact')

    if not name:
        return jsonify({'message': 'Missing required "name" field.'})

    if not contact:
        return jsonify({'message': 'Missing required "contact" field.'})

    existing_user = User.query.filter_by(contact=contact).first()
    if existing_user:
        return jsonify({'message': 'User with the given contact already exists.'})

    new_user = User(name=name, contact=contact)

    try:
        db.session.add(new_user)
        db.session.commit()
        return user_schema.jsonify(new_user)
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to add user to the database.'})

#FETCH ALL USER
@app.route('/userd', methods=['GET'])
def get_all():
    all_users = User.query.all()
    result = users_schema.dump(all_users)
    return jsonify(result)

#GET USER BY ID 
@app.route('/userd/<id>', methods=['GET'])
def getBy_id(id):
    user_id = User.query.get(id)
    return user_schema.jsonify(user_id)

#UPDATE USER BY ID
@app.route('/userd/<id>', methods=['PUT'])
def UpdateBy_id(id):
    user_id = User.query.get(id)
    data = request.get_json()
    name = data.get('name')
    contact = data.get('contact')
    user_id.name =name 
    user_id.contact = contact
    db.session.commit()
    return user_schema.jsonify(user_id)

#DELETE USER BY ID
@app.route('/userd/<id>', methods=['DELETE'])
def Delete_id(id):
    user_id = User.query.get(id)
    db.session.delete(user_id)
    db.session.commit()
    return user_schema.jsonify(user_id)

'''
@app.route('/userd', methods=['POST'])
def add_user():
    name= request.json['user']
    contact =request.json['contact']
    new_user=User(name,contact)
    db.session.add(new_user)
    db.session.commit()
    return user_schema.jsonify(new_user)
'''


if __name__ == '__main__':
    app.run(debug=True)

