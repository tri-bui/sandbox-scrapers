from flask import Flask, render_template
from flask_pymongo import PyMongo
import mars_scraper


# Flask app
app = Flask(__name__)

# App's connection to MongoDB
db_name = 'mars_db'
mongo_uri = 'mongodb://localhost:27017/' + db_name
app.config['MONGO_URI'] = mongo_uri
mongo = PyMongo(app)


""" App Routes """


@app.route('/')
def index():

    """ Home page displaying all data """

    # Extract Mars data and render home page
    mars_doc = mongo.db.mars.find_one() # 1st document in mars collection contains all data
    return render_template('index.html', mars=mars_doc) # pass data to and render home page


@app.route('/scrape')
def scrape():

    """ Scrape new data, update database with new data, and refresh page """

    mars = mongo.db.mars # Mars collection
    mars_data = mars_scraper.scrape_all() # scrape new data
    mars.update({}, mars_data, upsert=True) # create or update mars collection with new data
    # return index() # render home page
    return redirect('/', code=302) # redirect to home page with updated data


if __name__ == '__main__':
    app.run()