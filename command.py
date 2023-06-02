import click
from flask.cli import with_appcontext
from raw_data import venues, artists, shows


def make_venue_or_artist(type):
    types = {
        'venue': ['Apapa', 'Oshodi', 'Agege'],
        'artist': ['Guns N Petals', 'Matt Quevedo', 'The Wild Sax Band']
    }
    seek = {'artist': 'seeking_venue', 'venue': 'seeking_talent'}
    entities = [
        {
            "id": 2,
            "name": types[type][0],
            "city": "Lagos",
            "state": "Lagos",
            "phone": "08108013285",
            "genres": "[Hip]",
            "image_link": "https://via.placeholder.com/350x150",
            "website": "https://via.placeholder.com",
            "facebook_link": "https://facebook.com",
            seek[type]: True
        },
        {
            "id": 3,
            "name": types[type][1],
            "city": "Lagos",
            "state": "Lagos",
            "phone": "08108013285",
            "genres": "[Hip]",
            "image_link": "https://via.placeholder.com/350x150",
            "website": "https://via.placeholder.com",
            "facebook_link": "https://facebook.com",
            seek[type]: True
        },
        {
            "id": 4,
            "name": types[type][2],
            "city": "Lagos",
            "state": "Lagos",
            "phone": "08108013285",
            "genres": "[Hip]",
            "image_link": "https://via.placeholder.com/350x150",
            "website": "https://via.placeholder.com",
            "facebook_link": "https://facebook.com",
            seek[type]: True
        }
    ]

    def add_address(entity):
        return {
            **entity, 'address': '12 Ijero road ebute meta'
            # **entity, 'seeking_talent': 'talent', 'seeking_description': 'description'
        }

    if type == 'venue':
        entities = [add_address(entity) for entity in entities]
    return entities


def clear_db(db):
    db.session.execute('''TRUNCATE TABLE shows, venues, artists''')
    db.session.commit()


def seed_venues_and_artist(model_types, db):
    for model_type in model_types:
        for venue in make_venue_or_artist(model_type[0]):
            db.session.add(model_type[1](**venue))
            db.session.commit()


def make_venue_or_artist_from_raw(type):
    entity = {'venue': venues, 'artist': artists, 'show': shows}
    return entity[type]


def seed_venues_and_artist_from_raw(model_types, db):
    for model_type in model_types:
        for venue in make_venue_or_artist_from_raw(model_type[0]):
            db.session.add(model_type[1](**venue))
            db.session.commit()


@click.command("seed_db")
@with_appcontext
def seed():
    from model import Venue, Artist, Show, db
    # db.init_app(app)
    """Seed the database."""
    clear_db(db)
    seed_venues_and_artist_from_raw(
        [['venue', Venue], ['artist', Artist], ['show', Show]], db
    )
    # seed_venues_and_artist(
    #     [['venue', Venue], ['artist', Artist]], db
    # )
