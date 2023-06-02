from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


# Helper for the models

def get_venue(venue_id):
    return Venue.query.get(venue_id)


def get_artist(artist_id):
    return Artist.query.get(artist_id)


def venue_past_shows(venue_id):
    return Show.query.filter(Show.start_time < datetime.now(), Show.venue_id == venue_id).all()


def venue_upcoming_shows(venue_id):
    return Show.query.filter(Show.start_time > datetime.now(), Show.venue_id == venue_id).all()


def artist_past_shows(artist_id):
    return Show.query.filter(Show.start_time < datetime.now(), Show.artist_id == artist_id).all()


def artist_upcoming_shows(artist_id):
    return Show.query.filter(Show.start_time > datetime.now(), Show.artist_id == artist_id).all()


# Implement Show and Artist models, and all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime())
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'))

    @property
    def upcoming(self):
        venue = get_venue(self.venue_id)
        artist = get_artist(self.artist_id)

        if self.start_time > datetime.now():
            return {
                "venue_id": self.venue_id,
                "venue_name": venue.name,
                "artist_id": self.artist_id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": self.start_time.strftime("%m/%d/%Y, %H:%M")
            }
        else:
            return None


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String()), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    website = db.Column(db.String(), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)

    seeking_talent = db.Column(db.Boolean, nullable=False, default=True)
    seeking_description = db.Column(db.String(
        200), nullable=False, default='We are looking for an exciting artist to perform here!')
    shows = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
        return f'<Venue Name: {self.name}, City: {self.city}, State: {self.state}>'

    @property
    def city_and_state(self):
        return {'city': self.city, 'state': self.state}

    @property
    def full_venue_details(self):
        past_shows = venue_past_shows(self.id)
        upcoming_shows = venue_upcoming_shows(self.id)

        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'genres': self.genres,
            'website': self.website,
            'facebook_link': self.facebook_link,
            'seeking_talent': self.seeking_talent,
            'seeking_description': self.seeking_description,
            'image_link': self.image_link,
            'past_shows': [{
                'artist_id': previous_show.artist_id,
                'artist_name': previous_show.artist.name,
                'artist_image_link': previous_show.artist.image_link,
                'start_time': previous_show.start_time.strftime("%m/%d/%Y, %H:%M")
            } for previous_show in past_shows],
            'upcoming_shows': [{
                'artist_id': show.artist.id,
                'artist_name': show.artist.name,
                'artist_image_link': show.artist.image_link,
                'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
            } for show in upcoming_shows],
            'past_shows_count': len(past_shows),
            'upcoming_shows_count': len(upcoming_shows)
        }


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String()), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    website = db.Column(db.String(), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)

    seeking_venue = db.Column(db.Boolean, nullable=False, default=True)
    seeking_description = db.Column(db.String(
        120), nullable=False, default='We are looking to perform at an exciting venue!')

    shows = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
        return f'<Artist Name: {self.name}, City: {self.city}, State: {self.state}>'

    @property
    def artist_basic_details(self):
        return {'id': self.id, 'name': self.name}

    @property
    def full_artist_details(self):
        past_shows = artist_past_shows(self.id)
        upcoming_shows = artist_upcoming_shows(self.id)

        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'genres': self.genres,
            'website': self.website,
            'facebook_link': self.facebook_link,
            'seeking_venue': self.seeking_venue,
            'seeking_description': self.seeking_description,
            'image_link': self.image_link,
            'past_shows': [{
                'venue_id': p.venue_id,
                'venue_name': p.venue.name,
                'venue_image_link': p.venue.image_link,
                'start_time': p.start_time.strftime("%m/%d/%Y, %H:%M")
            } for p in past_shows],
            'upcoming_shows': [{
                'venue_id': u.venue.id,
                'venue_name': u.venue.name,
                'venue_image_link': u.venue.image_link,
                'start_time': u.start_time.strftime("%m/%d/%Y, %H:%M")
            } for u in upcoming_shows],
            'past_shows_count': len(past_shows),
            'upcoming_shows_count': len(upcoming_shows)
        }
