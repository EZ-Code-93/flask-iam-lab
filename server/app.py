#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe, UserSchema, RecipeSchema

class Signup(Resource):
    def post(self):
        data = request.get_json()

        username = data.get('username')
        password = data.get('password')
        image_url = data.get('image_url')
        bio = data.get('bio')

        user = User(
            username=username,
            image_url=image_url,
            bio=bio
        )

        user.password_hash = password

        try:
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
            return UserSchema().dump(user), 201
        except IntegrityError:
            return {'error': '422 Unprocessable Entity'}, 422

class CheckSession(Resource):
    def get(self):

        if session.get('user_id'):
            user = User.query.filter(User.id == session['user_id']).first()
            return UserSchema().dump(user), 200
        
        return {}, 401

class Login(Resource):
    def post(self):
        data = request.get_json()

        username = data.get('username')
        password = data.get('password')

        user = User.query.filter(User.username == username).first()

        if user and user.authenticate(password):
            session['user_id'] = user.id
            return UserSchema().dump(user), 200
        
        return {'error': '401 Unauthorized'}, 401

class Logout(Resource):
    def delete(self):
        if session.get('user_id'):
            session['user_id'] = None
            return {}, 204
        return {}, 401

class RecipeIndex(Resource):
    def get(self):
        recipes = [RecipeSchema().dump(recipe) for recipe in Recipe.query.all()]
        if session.get('user_id') is None:
            return {'error': '401 Unauthorized'}, 401
        return recipes, 200

    def post(self):
        if session.get('user_id') is None:
            return {'error': '401 Unauthorized'}, 401

        data = request.get_json()

        recipe = Recipe(
            title=data.get('title'),
            instructions=data.get('instructions'),
            minutes_to_complete=data.get('minutes_to_complete'),
            user_id=session['user_id']
        )

        try:
            db.session.add(recipe)
            db.session.commit()
            return RecipeSchema().dump(recipe), 201
        except IntegrityError:
            return {'error': '422 Unprocessable Entity'}, 422
      

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)