import sys
import babel
import json
import logging
from forms import *
import dateutil.parser
from command import seed
from flask_wtf import Form
from flask_moment import Moment
from distutils.log import error
from flask_migrate import Migrate
from model import db, Show, Artist, Venue
from logging import Formatter, FileHandler
from flask import Flask, render_template, request, Response, flash, redirect, url_for
de  # ----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#


#----------------------------------------------------------------------------#
# custom command.
#----------------------------------------------------------------------------#
# def register_commands(app):
#     """Register CLI commands."""
#     app.cli.add_command(seed)

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#


app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

# connect to a local postgresql database
migrate = Migrate(app, db)

"""Register CLI commands."""
app.cli.add_command(seed)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    # return render_template('pages/home.html')
    recentVenues = Venue.query.order_by(db.desc(Venue.id)).limit(10).all()
    recentArtists = Artist.query.order_by(db.desc(Artist.id)).limit(10).all()
    return render_template('pages/home.html', venues=recentVenues, artists=recentArtists)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    distinct_venues = [
        v.city_and_state for v in Venue.query.distinct(Venue.city, Venue.state).all()
    ]
    venue_loc = []
    for distinct_venue in distinct_venues:
        venues = [{'id': v.id, 'name': v.name, 'num_upcoming_shows': v.shows}
                  for v in Venue.query.filter_by(city=distinct_venue['city']).all()]
        venue_loc.append({**distinct_venue, 'venues': venues})
    return render_template('pages/venues.html', areas=venue_loc)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    try:
        search_term = request.form.get('search_term', '')

        search_ven = Venue.query.filter(
            Venue.name.ilike(f'%{search_term}%')).all()
        response = {
            "count": len(search_ven),
            "data": [{
                "id": v_search.id,
                "name": v_search.name,
                "num_upcoming_shows": len(v_search.shows)
            } for v_search in search_ven]
        }

        return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))
    except:
        flash('An error occurred while searching, please try again')
        print(sys.exc_info())
        return redirect(url_for('venues'))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id

    try:
        data = Venue.query.filter_by(id=venue_id).all()[0]

        return render_template('pages/show_venue.html', venue=data.full_venue_details)
    except:
        flash('Sorry, venue is not available!')
        print(sys.exc_info())
        return redirect(url_for('index'))


#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    try:
        new_venue = Venue(
            name=request.form.get('name'),
            city=request.form.get('city'),
            state=request.form.get('state'),
            address=request.form.get('address'),
            genres=request.form.getlist('genres'),
            phone=request.form.get('phone'),
            facebook_link=request.form.get('facebook_link'),
            image_link=request.form.get('image_link'),
            website=request.form.get('website'),
            seeking_talent=request.form.get('seeking_talent') == 'True',
            seeking_description=request.form.get('seeking_description')
        )
        db.session.add(new_venue)
        db.session.commit()
    except Exception as err:
        print('An error occured while trying to create venue', err)
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if not error:
        flash('Venue ' + request.form['name'] + ' was successfully created!')

    else:
        flash('An error occurred. Venue ' +
              new_venue.name + ' could not be listed.')

    return redirect(url_for('index'))


@app.route('/venues/<venue_id>/delete', methods=['POST'])
def delete_venue(venue_id):
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    venue_name = Venue.query.get(venue_id).name
    try:
        venue_to_be_deleted = db.session.query(
            Venue).filter(Venue.id == venue_id)
        venue_to_be_deleted.delete()
        db.session.commit()
        flash("Venue: " + venue_name + " was successfully deleted.")

    except:
        db.session.rollback()
        print(sys.exc_info())
        return jsonify(
            {
                "errorMessage": "Something went wrong. This venue was not successfully deleted. Please try again."
            }
        )

    finally:
        db.session.close()
        return redirect(url_for("index"))

    # return redirect(url_for('index'))


#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    
    data = [a.artist_basic_details for a in Artist.query.all()]
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    try:
        search_term = request.form.get('search_term', '')

        search_artst = Venue.query.filter(
            Venue.name.ilike(f'%{search_term}%')).all()

        response = {
            "count": len(search_artst),
            "data": [{
                "id": v_search.id,
                "name": v_search.name,
                "num_upcoming_shows": len(v_search.shows)
            } for v_search in search_artst]
        }

        return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

    except:
        flash('An error occurred while searching, please try again')
        print(sys.exc_info)
        return redirect(url_for('artists'))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    
    try:
        data = Artist.query.filter_by(id=artist_id).all()[0]

        return render_template('pages/show_artist.html', artist=data.full_artist_details)
    except:
        flash('Sorry, artist is not available!')
        print(sys.exc_info())
        return redirect(url_for('index'))


#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.filter_by(id=artist_id).all()[0]

    form = ArtistForm(
        name=artist.name,
        city=artist.city,
        state=artist.state,
        genres=artist.genres,
        phone=artist.phone,
        image_link=artist.image_link,
        facebook_link=artist.facebook_link,
        website=artist.website,
        seeking_venue=artist.seeking_venue,
        seeking_description=artist.seeking_description
    )
    print(sys.exc_info())
    
    return render_template('forms/edit_artist.html', form=form, artist=artist)

#


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    
    # artist record with ID <artist_id> using the new attributes
    try:
        artist = Artist.query.filter_by(id=artist_id).all()[0]

        artist.name = request.form.get('name')
        artist.city = request.form.get('city')
        artist.state = request.form.get('state')
        artist.phone = request.form.get('phone')
        artist.genres = request.form.getlist('genres')
        artist.facebook_link = request.form.get('facebook_link')
        artist.website = request.form.get('website')
        artist.image_link = request.form.get('image_link')
        artist.seeking_venue = request.form.get('seeking_venue') == 'True'
        artist.seeking_description = request.form.get('seeking_description')

        db.session.add(artist)
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Artist could not be updated')
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

    venue = Venue.query.filter_by(id=venue_id).all()[0]

    form = VenueForm(
        name=venue.name,
        city=venue.city,
        state=venue.state,
        address=venue.address,
        phone=venue.phone,
        facebook_link=venue.facebook_link,
        website=venue.website,
        image_link=venue.image_link,
        seeking_talent=venue.seeking_talent,
        seeking_description=venue.seeking_description
    )
    # populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    try:
        venue = Venue.query.filter_by(id=venue_id).all()[0]

        venue.name = request.form.get('name')
        venue.city = request.form.get('city')
        venue.state = request.form.get('state')
        venue.address = request.form.get('address')
        venue.phone = request.form.get('phone')
        venue.facebook_link = request.form.get('facebook_link')
        venue.website = request.form.get('website')
        venue.image_link = request.form.get('image_link')
        venue.seeking_talent = request.form.get('seeking_talent') == 'True'
        venue.seeking_description = request.form.get('seeking_description')

        db.session.add(venue)
        db.session.commit()

        db.session.refresh(venue)
        flash("This venue was successfully updated!")

    except:
        db.session.rollback()
        print(sys.exc_info())
        flash(
            "An error occurred. Venue "
            + request.form.get("name")
            + " could not be updated."
        )

    finally:
        db.session.close()

    return redirect(url_for("show_venue", venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

    # called upon submitting the new artist listing form
    # insert form data as a new Venue record in the db, instead
    # modify data to be the data object returned from db insertion
    error = False
    try:
        seeking_venue = request.form['seeking_venue'] if request.form.get(
            'seeking_venue') else False
        seeking_description = request.form['seeking_description'] if request.form.get(
            'seeking_description') else False
        new_artist = Artist(
            name=request.form.get('name'),
            genres=request.form.get('genres'),
            city=request.form.get('city'),
            state=request.form.get('state'),
            phone=request.form.get('phone'),
            website=request.form.get('website'),
            image_link=request.form.get('image_link'),
            facebook_link=request.form.get('facebook_link'),
            seeking_venue=seeking_venue,
            seeking_description=seeking_description,
        )
        db.session.add(new_artist)
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully created!')
    except Exception as err:
        print('**** error *****', err)
        error = True
        db.session.rollback()
        # In an unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
        flash('An error occurred. Artist ' +
              request.form['name'] + 'could not be created. ')
    finally:
        db.session.close()
    if error:
        return redirect(url_for('index'))
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    
    shows_list = Show.query.all()
    data = []
    for show in shows_list:
        data.append({
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": str(show.start_time)
        })
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # create new shows in the db, upon submitting new show listing form
    # insert form data as a new Show record in the db
    error = False

    try:
        new_show = Show(
            venue_id=request.form.get('venue_id'),
            artist_id=request.form.get('artist_id'),
            start_time=request.form.get('start_time'),
        )
        db.session.add(new_show)
        db.session.commit()
    except Exception as err:
        print('An error occured while trying to create show:', err)
        error = True
        db.session.rollback()
    finally:
        db.session.close()

    if not error:
        flash('Show was successfully listed!')
        # unsuccessful db insert, flash an error instead.
    else:
        flash('An error occurred. Show could not be listed.')

        return redirect(url_for('index'))
    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
