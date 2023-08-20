#!/usr/bin/env python3

from flask import request, session, make_response, abort
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import NotFound

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self): 
        try:
            form_json = request.get_json()
            new_user = User(
                username = form_json['username'],
                bio = form_json['bio'],
                image_url = form_json['image_url']
            )

            new_user._password_hash = form_json['password']
            db.session.add(new_user)
            db.session.commit()

            session['user_id'] = new_user.id
            # response = make_response(
            #     new_user.__dict__, 
            #     201
            # )
            # import pdb; pdb.set_trace()
            return new_user.to_dict(), 201

        except ValueError as e:
            abort(422,e.args[0])

class CheckSession(Resource):
    def get(self):
        try:
            user = User.query.filter_by(id=session['user_id']).first()
            response = user.to_dict(), 200
            # import pdb; pdb.set_trace()
            return response
        except:
            abort(401, 'Unauthorized')

class Login(Resource):
    def post(self):
        form_json = request.get_json()

        user = User.query.filter_by(username=form_json['username']).first()
            # import pdb; pdb.set_trace()
        if user and user.authenticate(form_json['password']):
            session['user_id'] = user.id
            response = user.to_dict(), 200
            return response
        else:
                abort(401, 'Incorrect Username or Password')

        

class Logout(Resource):
    def delete(self):
        if 'user_id' in session:
            session['user_id'] = None
            return {}, 204
        return {'error': 'Unauthorized'}, 401

class RecipeIndex(Resource):
    def get(self):
        recipe_list = Recipe.query.filter_by(user_id = session['user_id'])
        response = recipe_list,200

        return response

    def post(self):
        form_json = request.get_json()
        try:
            new_recipe = Recipe(
                title=form_json['title'],
                instructions=form_json['instructions'],
                minutes_to_complete=int(form_json['minutes_to_complete']),
                user_id=session['user_id'],
            )
        except ValueError as e:
            abort(422,e.args[0])

        db.session.add(new_recipe)
        db.session.commit()

        response_dict = new_recipe.to_dict()

        response = make_response(
            response_dict,
            201,
        )
        return response

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')

@app.errorhandler(NotFound)
def handle_not_found(e):
    response = make_response(
        "Not Found: Sorry the resource you are looking for does not exist",
        404
    )
    return response
if __name__ == '__main__':
    app.run(port=5555, debug=True)
