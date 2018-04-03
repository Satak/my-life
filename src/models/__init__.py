'''Models'''

from datetime import datetime
from core_app import db, bcrypt

friends = db.Table(
    'friends',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('friend_id', db.Integer, db.ForeignKey('user.id')),
    db.UniqueConstraint(
        'user_id',
        'friend_id',
        name='friends_unique_constraint'
    )
)

class Happiness(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    happiness = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(1000))
    date_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, user_id, happiness, description=None):
        self.user_id = user_id
        self.happiness = happiness
        self.description = description

    def as_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "happiness": self.happiness,
            "description": self.description,
            "date_time": self.date_time
        }

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000), nullable=False, unique=True)
    email = db.Column(db.String(1000), nullable=False, unique=True)
    description = db.Column(db.String(1000))
    happiness = db.relationship('Happiness', backref='user')
    login = db.relationship('Login', backref='user', uselist=False)

    friends = db.relation(
        'User',
        secondary=friends,
        primaryjoin=friends.c.user_id == id,
        secondaryjoin=friends.c.friend_id == id,
        backref="users"
    )

    def __init__(self, name, email, description=None):
        self.name = name
        self.email = email
        self.description = description

    def check_pw(self, password):
        return bcrypt.check_password_hash(self.login.password, password)

    def get_happiness(self):
        if not self.happiness:
            return []
        return [item.as_dict().get('happiness') for item in self.happiness]

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "description": self.description,
            "happiness": self.get_happiness()
        }

class Login(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    password = db.Column(db.String(1000), nullable=False, unique=True)

    def __init__(self, user_id, password):
        self.user_id = user_id
        self.password = bcrypt.generate_password_hash(password)

    def as_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "password": self.password
        }
