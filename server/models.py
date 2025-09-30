from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin

from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    _password_hash = db.Column(db.String)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)

    # Relationship: User has many recipes
    recipes = db.relationship('Recipe', backref='user', lazy=True)

    # Serialization rules to exclude password hash from serialization
    serialize_rules = ('-_password_hash', '-recipes.user')

    @hybrid_property
    def password_hash(self):
        raise AttributeError('Password hash is not a readable attribute')

    @password_hash.setter
    def password_hash(self, password):
        password_hash = bcrypt.generate_password_hash(password.encode('utf-8'))
        self._password_hash = password_hash.decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password.encode('utf-8'))

    @validates('username')
    def validate_username(self, key, username):
        if not username:
            raise ValueError('Username must be present')
        return username

    def __repr__(self):
        return f'<User {self.username}>'

class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer)
    
    # Foreign key to establish relationship with User (belongs to user)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Serialization rules to avoid circular references
    serialize_rules = ('-user.recipes',)

    @validates('title')
    def validate_title(self, key, title):
        if not title or not title.strip():
            raise ValueError('Title must be present')
        return title

    @validates('instructions')
    def validate_instructions(self, key, instructions):
        if not instructions or not instructions.strip():
            raise ValueError('Instructions must be present')
        if len(instructions.strip()) < 50:
            raise ValueError('Instructions must be at least 50 characters long')
        return instructions

    def __repr__(self):
        return f'<Recipe {self.title}>'