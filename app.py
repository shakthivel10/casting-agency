import os
import sys
import json
import datetime
from flask import Flask, request, Response, abort, jsonify
from werkzeug.datastructures import MultiDict
from models import setup_db, db_drop_and_create_all, Actor, Movie, CastedIn
from flask_cors import CORS, cross_origin
from auth import AuthError, requires_auth


def create_app(test_config=None):

    app = Flask(__name__)
    setup_db(app)
    cors = CORS(app)

    # uncomment to delete all data in the database
    # db_drop_and_create_all()

    @app.route('/')
    def index():
        return jsonify({"API": "Casting Agency API",
                        "API Documentation": "https://github.com/shakthivel10/casting-agency/master/README.md"})

    '''
    Fetches a list of all actors in the database
    Request Arguments: None
    Returns: A list of actor objects, where each object has the following properties: id, name, age, gender and list of movie titles the actor acted in.
    '''

    @app.route('/actors', methods=["GET"])
    @requires_auth("get:actor")
    def get_actors(jwt):

        query_result = Actor.query.all()
        response = []

        for obj in query_result:
            actor = obj.format()
            movies = []
            for casted_in in obj.casted_in:
                movies.append(casted_in.movie.title)
            actor["movies"] = movies
            response.append(actor)

        return jsonify(response)

    '''
    Fetches a list of all movies in the database
    Request Arguments: None
    Returns: A list of movie objects, where each object has the following properties: id, title, release_date and list of names of actors who acted in in the movie.
    '''
    @app.route('/movies', methods=["GET"])
    @requires_auth("get:movie")
    def get_movies(jwt):
        query_result = Movie.query.all()
        response = []

        for obj in query_result:
            movie = obj.format()
            actors = []
            for casted in obj.casted:
                actors.append(casted.actor.name)
            movie["actors"] = actors
            response.append(movie)

        return jsonify(response)

    '''
    Deletes the actor with given id from the database
    Returns: the id of the actor succefully deleted 
    '''
    @app.route('/actors/<int:id>', methods=["DELETE"])
    @requires_auth("delete:actor")
    def delete_actor(jwt, id=id):

        actor = Actor.query.filter(Actor.id == id).first()

        if not actor:
            abort(404)

        try:
            actor.delete()
            return (jsonify({"success": True,
                             "delete": id}), 200)
        except:
            print(sys.exc_info())
            abort(422)
    '''
    Deletes the movie with given id from the database
    Returns: the id of the movie succefully deleted
    '''
    @app.route('/movies/<int:id>', methods=["DELETE"])
    @requires_auth("delete:movie")
    def delete_movie(jwt, id=id):

        movie = Movie.query.filter(Movie.id == id).first()

        if not movie:
            abort(404)

        try:
            movie.delete()
            return (jsonify({"success": True,
                             "delete": id}), 200)
        except:
            print(sys.exc_info())
            abort(422)

    '''
    Creates and inserts a new actor record into the database
    Request Body: actor information { "name": <actor_name>, "age": <actor_age>, "gender": <actor_gender>}
    Returns: A JSON containing the actor inserted
    '''
    @app.route("/actors", methods=["POST"])
    @requires_auth("post:actor")
    def post_actor(jwt):

        if not request.json:
            abort(400)
        try:
            if "name" in request.json:
                name = request.json["name"]
            if "age" in request.json:
                age = request.json["age"]
            if "gender" in request.json:
                gender = request.json["gender"]

            new_actor = Actor(name=name, age=age, gender=gender)

            new_actor.insert()

            return (jsonify({"success": True,
                             "actor": new_actor.format()}), 200)

        except:
            print(sys.exc_info())
            abort(422)
    '''
    Creates and inserts a new movie record into the database
    Request Body: movie information { "title": <movie_title>, "release_date": <<movie_release_date>}
    The release date has to a string in the following format: "YYYY-MM-DD", example: “2021-12-31”
    Returns: A JSON containing the movie inserted
    '''
    @app.route("/movies", methods=["POST"])
    @requires_auth("post:movie")
    def post_movie(jwt):
        if not request.json:
            abort(400)
        try:
            new_movie = Movie()
            if "title" in request.json:
                title = request.json["title"]
                new_movie.title = title
            if "release_date" in request.json:
                date_arr = [int(val)
                            for val in request.json["release_date"].split("-")]
                release_date = datetime.datetime(*date_arr)
                new_movie.release_date = release_date

            new_movie.insert()

            return (jsonify({"success": True,
                             "movie": new_movie.format()}), 200)

        except:
            print(sys.exc_info())
            abort(422)
    '''
    Updates an existing actor record in the database.
    Request Body: new actor information conatining one or more of the following keys { "name": <actor_name>, "age": <actor_age>, "gender": <actor_gender>}
    Returns: A JSON containing the actor updated
    '''
    @app.route("/actors/<int:id>", methods=["PATCH"])
    @requires_auth("patch:actor")
    def patch_actor(jwt, id=id):

        if not request.json:
            abort(400)

        actor = Actor.query.filter(Actor.id == id).first()
        if not actor:
            abort(404)

        try:
            if "name" in request.json:
                name = request.json["name"]
                actor.name = name
            if "age" in request.json:
                age = request.json["age"]
                actor.age = age
            if "gender" in request.json:
                gender = request.json["gender"]
                actor.gender = gender

            actor.update()

            return (jsonify({"success": True,
                             "actor": actor.format()}), 200)

        except:
            print(sys.exc_info())
            abort(422)
    '''
    Updates an existing movie record in the database.
    Request Body: new movie information conatining one or more of the following keys { "title": <movie_title>, "release_date": <<movie_release_date>}
    The release date has to a string in the following format: "YYYY-MM-DD", example: “2021-12-31”
    Returns: A JSON containing the movie updated
    '''
    @app.route("/movies/<int:id>", methods=["PATCH"])
    @requires_auth("patch:movie")
    def patch_movie(jwt, id=id):

        if not request.json:
            abort(400)

        movie = Movie.query.filter(Movie.id == id).first()

        if not movie:
            abort(404)

        try:
            if "title" in request.json:
                title = request.json["title"]
                movie.title = title
            if "release_date" in request.json:
                date_arr = [int(val)
                            for val in request.json["release_date"].split("-")]
                release_date = datetime.datetime(*date_arr)
                movie.release_date = release_date

            movie.update()

            return (jsonify({"success": True,
                             "movie": movie.format()}), 200)

        except:
            print(sys.exc_info())
            abort(422)

    # Error Handling

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "not found"
        }), 404

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(AuthError)
    def auth_error(error):
        return (jsonify({
                        "success": False,
                        "error": error.status_code,
                        "message": error.error,
                        }), error.status_code)

    return app


app = create_app()

if __name__ == '__main__':
    app.run()
