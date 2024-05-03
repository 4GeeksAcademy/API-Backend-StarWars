"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User , Planet , Favorite , Character
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():
    user = User.query.all()
    if user == []:
        return jsonify({"msg": "No existen usuarios"}), 400
    response_body = list(map(lambda x : x.serialize(), user))
    return jsonify(response_body), 200

@app.route('/people', methods=['GET'])
def character():
    people = Character.query.all()
    if people == []:
        return jsonify({"msg": "No existen personajes"}), 400
    response_body = list(map(lambda x : x.serialize(), people))
    return jsonify(response_body), 200

@app.route('/planet', methods=['GET'])
def planet_hello():
    planet = Planet.query.all()
    if planet == []:
        return jsonify({"msg": "No existen personajes"}), 400
    response_body = list(map(lambda x : x.serialize(), planet))
    return jsonify(response_body), 200

@app.route('/characters/<int:character_id>', methods=['GET'])
def get_one_character(character_id):
    character = Character.query.get(character_id)
    if character is None:
        return jsonify({"msg": f"character with id {character_id} not found"}), 404
    serialized_character = character.serialize()
    return serialized_character, 200

@app.route('/planets/<int:character_id>', methods=['GET'])
def get_one_planet(character_id):
    planet = Planet.query.get(character_id)
    if planet is None:
        return jsonify({"msg": f"planet with id {character_id} not found"}), 404
    serialized_planet = planet.serialize()
    return serialized_planet, 200


@app.route('/user/<int:user_id>/favorites', methods=['GET'])
def user_id(user_id):
    user_favorite = Favorite.query.filter_by(user_id = user_id).all()
    if len(user_favorite) < 1:
        return jsonify({"msg": "No hay favoritos agregados"}), 400

    response_body = list(map(lambda x : x.serialize(), user_favorite))
    return jsonify(response_body), 200


@app.route('/favorite/planet/<int:character_id>/<int:user_id>', methods=['POST'])
def add_fav_planet(character_id, user_id):
        # try:
            user_id = request.args.get('user_id')
            existing_favorite = Favorite.query.filter_by(user_id=user_id, character_id=character_id).first()

            if existing_favorite:
                return jsonify({"message": "Is already a favorite planet of the user"}), 400

            planet = Planet.query.get(character_id)
            if not planet:
                return jsonify({"message": "Planet does not exist"}), 404

            new_favorite = Favorite(user_id=user_id, character_id=character_id)
            db.session.add(new_favorite)
            db.session.commit()
            return jsonify({"message": "Planet set as favorite"}), 200
            

@app.route('/favorite/character/<int:character_id>/<int:user_id>', methods=['POST'])
def add_fav_character(character_id, user_id):
        # try:
            user_id = request.args.get('user_id')
            existing_favorite = Favorite.query.filter_by(user_id=user_id, character_id=character_id).first()

            if existing_favorite:
                return jsonify({"message": "Is already a character of the user"}), 400

            character = Character.query.get(character_id)
            if not character:
                return jsonify({"message": "Planet does not exist"}), 404

            new_favorite = Favorite(user_id=user_id, character_id=character_id)
            db.session.add(new_favorite)
            db.session.commit()
            return jsonify({"message": "Character set as favorite"}), 200

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_fav_planet(planet_id):
    try:
        user_id = request.args.get('user_id')
        favorite_to_delete = Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()

        if favorite_to_delete:
            db.session.delete(favorite_to_delete)
            db.session.commit()
            return jsonify({"message": "Favorite Planet deleted"}), 200
        else:
            return jsonify({"message": "Favorite Planet not found"}), 404

    except Exception as e:
            print(str(e))
            return jsonify({"message": "Server error"}), 500

@app.route('/favorite/character/<int:character_id>', methods=['DELETE'])
def delete_fav_character(character_id):
    try:
        user_id = request.args.get('user_id')
        favorite_to_delete = Favorite.query.filter_by(user_id=user_id, character_id=character_id).first()

        if favorite_to_delete:
            db.session.delete(favorite_to_delete)
            db.session.commit()
            return jsonify({"message": "Favorite Character deleted"}), 200
        else:
            return jsonify({"message": "Favorite Character not found"}), 404

    except Exception as e:
            print(str(e))
            return jsonify({"message": "Server error"}), 500
            




# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
