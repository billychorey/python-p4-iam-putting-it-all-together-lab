from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin

from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)
    recipes = db.relationship('Recipe', backref='user')

    # Exclude _password_hash from the serialization
    serialize_rules = ('-recipes', '-_password_hash')

    @hybrid_property
    def password_hash(self):
        raise AttributeError("Password hash is not accessible directly.")

    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self._password_hash:
            # Set a default password if none is provided
            self.password_hash = 'defaultpassword'

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password)

class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    @validates('title')
    def validate_title(self, key, title):
        if not title:
            raise ValueError("Title cannot be empty.")
        return title

    @validates('instructions')
    def validate_instructions(self, key, instructions):
        if len(instructions) < 50:
            raise ValueError("Instructions must be at least 50 characters long.")
        return instructions
