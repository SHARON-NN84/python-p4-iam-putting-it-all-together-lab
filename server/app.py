#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        data = request.get_json() or {}

        username = data.get('username')
        password = data.get('password')
        image_url = data.get('image_url')
        bio = data.get('bio')

        # Basic required fields validation
        if not username or not password:
            return {'error': 'Username and password are required.'}, 422

        try:
            user = User(
                username=username,
                image_url=image_url,
                bio=bio,
            )
            # triggers bcrypt hashing via hybrid_property setter
            user.password_hash = password

            db.session.add(user)
            db.session.commit()

            # store user id in session
            session['user_id'] = user.id

            return {
                'id': user.id,
                'username': user.username,
                'image_url': user.image_url,
                'bio': user.bio,
            }, 201

        except IntegrityError:
            db.session.rollback()
            return {'error': 'Username already exists.'}, 422
        except ValueError as e:
            db.session.rollback()
            return {'error': str(e)}, 422

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Unauthorized'}, 401

        user = User.query.filter_by(id=user_id).first()
        if not user:
            return {'error': 'Unauthorized'}, 401

        return {
            'id': user.id,
            'username': user.username,
            'image_url': user.image_url,
            'bio': user.bio,
        }, 200

class Login(Resource):
    def post(self):
        data = request.get_json() or {}
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return {'error': 'Username and password are required.'}, 422

        user = User.query.filter_by(username=username).first()
        if not user or not user.authenticate(password):
            return {'error': 'Unauthorized'}, 401

        session['user_id'] = user.id
        return {
            'id': user.id,
            'username': user.username,
            'image_url': user.image_url,
            'bio': user.bio,
        }, 200

class Logout(Resource):
    def delete(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Unauthorized'}, 401

        session.pop('user_id', None)
        return '', 204

class RecipeIndex(Resource):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Unauthorized'}, 401

        recipes = Recipe.query.all()
        data = []
        for r in recipes:
            data.append({
                'id': r.id,
                'title': r.title,
                'instructions': r.instructions,
                'minutes_to_complete': r.minutes_to_complete,
                'user': {
                    'id': r.user.id if r.user else None,
                    'username': r.user.username if r.user else None,
                    'image_url': r.user.image_url if r.user else None,
                    'bio': r.user.bio if r.user else None,
                }
            })

        return data, 200

    def post(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Unauthorized'}, 401

        data = request.get_json() or {}
        title = data.get('title')
        instructions = data.get('instructions')
        minutes_to_complete = data.get('minutes_to_complete')

        try:
            recipe = Recipe(
                title=title,
                instructions=instructions,
                minutes_to_complete=minutes_to_complete,
                user_id=user_id,
            )

            db.session.add(recipe)
            db.session.commit()

            return {
                'id': recipe.id,
                'title': recipe.title,
                'instructions': recipe.instructions,
                'minutes_to_complete': recipe.minutes_to_complete,
                'user': {
                    'id': recipe.user.id if recipe.user else None,
                    'username': recipe.user.username if recipe.user else None,
                    'image_url': recipe.user.image_url if recipe.user else None,
                    'bio': recipe.user.bio if recipe.user else None,
                }
            }, 201
        except ValueError as e:
            db.session.rollback()
            return {'error': str(e)}, 422

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)