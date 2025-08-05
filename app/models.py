from . import db
from flask_login import UserMixin

# Corrected favorites association table
favorites = db.Table('favorites', 
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('listing_id', db.Integer, db.ForeignKey('listing.id'), primary_key=True)
)

class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    rent = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    tags = db.Column(db.String(200))  # comma-separated string for tags
    image = db.Column(db.String(200))  # filename of uploaded image

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='listings')

    def __repr__(self):
        return f"<Listing {self.title}>"
    
    def get_tag_list(self):
        return self.tags.split(",") if self.tags else []

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)

    favorites = db.relationship('Listing',
                                secondary=favorites,
                                backref=db.backref('favorited_by', lazy='dynamic'),
                                lazy='dynamic')