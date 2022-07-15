#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from audioop import add
from email.policy import default
import imp
import json
import re
from tracemalloc import start
from typing import final
from unicodedata import name
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy import delete, desc, false
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app=app, db=db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    genres = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(250))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    artist_id = db.relationship('Artist', backref='venue', lazy=True)

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'))

class Show(db.Model):
  __tablename__ = 'show'
  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))
  venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'))
  start_time = db.Column(db.DateTime, default=datetime.utcnow)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  unique_state = Venue.query.with_entities(Venue.city).distinct().all()
  data = []
  records = {}
  city_names = []

  for city in unique_state:
    for j in city:
      city_names.append(j)
      
  for name in city_names:
    all_venues = Venue.query.with_entities(Venue.id, Venue.name).filter_by(city=name).all()
    all_states = Venue.query.with_entities(Venue.state).filter_by(city=name).first()
    records = {'city': name, 'state': all_states,'venues': all_venues}
    data.append(records) 
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_text = request.form.get('search_term')
  search_result = Venue.query.with_entities(Venue.name, Venue.id).filter(Venue.name.ilike(f'%{search_text}%')).all()
  result = []
  search_dict = {}
  for k,v in search_result:
    search_dict = {'name':k, 'id':v}
    result.append(search_dict)
  
  count=len(result)
  return render_template('pages/search_venues.html', results=result, search_term=search_text, count=count)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  data = Venue.query.filter_by(id=venue_id).first()
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  isAdded = False

  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    
    address = request.form['address']
    phone = request.form['phone']
    img_link = request.form['image_link']
    
    genres = request.form['genres']
    facebook_link = request.form['facebook_link']
    web_link = request.form['website_link']
    seeking_talent = request.form['seeking_talent']

    if seeking_talent == 'y':
      seeking_talent = True
    else:
      seeking_talent = False

    # print(seeking_talent)
    seeking_description = request.form['seeking_description']

    if request.method == 'POST':
      new_venue = Venue(
        name=name, 
        city=city, 
        state=state, 
        address=address, 
        phone=phone, 
        image_link=img_link, 
        genres=genres, 
        facebook_link=facebook_link, 
        website_link=web_link, 
        seeking_talent=seeking_talent, 
        seeking_description=seeking_description
      )
      db.session.add(new_venue)
      db.session.commit()
      isAdded = True
    if isAdded:
      flash('Venue ' + name + ' was successfully listed!')
    else:
      flash('An error occurred. Venue ' + name + ' could not be listed.')
  except:
    isAdded = False
    db.session.rollback()
  finally:
    db.session.close()

  
  
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  delete_status = False
  if request.method == 'DELETE':
    try:
      Venue.query.filter_by(id=venue_id).delete()
      db.session.commit()
      delete_status = True 
    except:
      delete_status = False
      db.session.rollback()
    finally:
      db.session.close()
  
  if delete_status:
    flash('Venue was successfully listed!')
  else:
    flash('Error: Deletion was not successfull')
  return redirect(url_for('index'))


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  try:
    search_term = request.form.get('search_term')
    search_result = Artist.query.with_entities(Artist.name, Artist.id).filter(Artist.name.ilike(f'%{search_term}%')).all()
    output = []
    searched_artist = {}
    for k,v in search_result:
      searched_artist = {'name':k, 'id':v}
      output.append(searched_artist)
    total = len(output)
  except:
    print('Error Searching Artist')
  finally:
    print('Done')
  return render_template('pages/search_artists.html', results=output, search_term=search_term, count=total)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  data = Artist.query.join(Venue).filter(Artist.id == artist_id).first()
  
  return render_template('pages/show_artist.html', artist = data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  data = Artist.query.filter_by(id=artist_id).first()
  return render_template('forms/edit_artist.html', form=form, artist=data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist_edit_status = False 
  try:
    if request.method == 'POST':
      artist_update = Artist.query.filter_by(id=artist_id).update({
        'name' : request.form['name'],
        'city' : request.form['city'],
        'state' : request.form['state'],
        'phone' : request.form['phone'],
        'genres' : request.form['genres'],
        'image_link' : request.form['image_link'],
        'facebook_link' : request.form['facebook_link'],
        'website_link' : request.form['website_link'],
        'seeking_venue' : request.form['seeking_venue'],
        'seeking_description' : request.form['seeking_description']
      })
      db.session.commit()
      artist_edit_status = True
  except:
    db.session.rollback()
  finally:
    db.session.close()

  if artist_edit_status:
    flash('Artist Successfully Edited')
  else:
    flash('Error in Editing Artist')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.filter_by(id=venue_id).first()
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  edit_status = False
  try:
    Venue.query.filter_by(id=venue_id).update({
      'name' : request.form['name'],
      'city' : request.form['city'],
      'state': request.form['state'],
      'address': request.form['address'],
      'phone': request.form['phone'],
      'image_link': request.form['image_link'],
      'genres': request.form['genres'],
      'facebook_link': request.form['facebook_link'],
      'website_link': request.form['website_link'],
      'seeking_talent': request.form['seeking_talent'],
      'seeking_description': request.form['seeking_description']
    })
    db.session.commit()
    edit_status = True
  except:
    edit_status = False
    db.session.rollback()
  finally:
    db.session.close()
  
  if edit_status:
    flash('Venue was successfully edited')
  else:
    flash('Error editing venue')

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  if request.method =='POST':
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    img_link = request.form['image_link']
    genres = request.form['genres']
    facebook = request.form['facebook_link']
    website =request.form['website_link']

    if request.form['seeking_venue'] == 'y':
      seeking = True
    else:
      seeking = False
    description = request.form['seeking_description']
    new_artist = Artist(
      name=name, 
      city=city, 
      state=state, 
      phone=phone, 
      image_link=img_link, 
      genres=genres, 
      facebook_link=facebook, 
      website_link=website, 
      seeking_venue=seeking, 
      seeking_description=description
    )
    db.session.add (new_artist)
    db.session.commit()

    if new_artist:
      flash('Artist ' + name + ' was successfully listed!')
    else:
      flash('An error occurred. Artist ' + name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows_record = []
  shows_dict = {}
  show_data = Show.query.all()
  for show in show_data:
    venue_data = Venue.query.with_entities(Venue.id, Venue.name).filter_by(id=show.venue_id).all()
    artist_data = Artist.query.with_entities(Artist.id, Artist.name, Artist.image_link).filter_by(id=show.artist_id).all()
    shows_dict = {
      'venue_id':venue_data[0][0], 
      'venue_name':venue_data[0][1],
      'artist_id': artist_data[0][0],
      'artist_name':artist_data[0][1],
      'artist_image_link':artist_data[0][2],
      'start_time':show.start_time
    }
    shows_record.append(shows_dict)
  return render_template('pages/shows.html', shows=shows_record)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  isSuccesful = False
  try:
    if request.method == 'POST':
      artistId = request.form['artist_id']
      venueId = request.form['venue_id']
      starttime = request.form['start_time']
      new_show = Show(
        artist_id=artistId, 
        venue_id=venueId, 
        start_time=starttime
      )

    db.session.add(new_show)
    db.session.commit()
    isSuccesful = True

    if isSuccesful:
      flash('Show was successfully listed!')
  except:
    isSuccesful = False
    db.session.rollback()
  finally:
    db.session.close
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
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
