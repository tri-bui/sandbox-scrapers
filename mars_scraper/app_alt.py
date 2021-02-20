from flask import Flask, render_template
from flask_pymongo import PyMongo
import mars_scraper


# Flask app
app = Flask(__name__)

# App's connection to MongoDB
db_name = 'mars'
mongo_uri = 'mongodb://localhost:27017/' + db_name
app.config['MONGO_URI'] = mongo_uri
mongo = PyMongo(app)


""" App Routes """


@app.route('/')
def index():

    """ Home page displaying all data """

    # Extract Mars data and render home page
    last_doc = mongo.db.mars.find().sort([('last_modified', -1)]).limit(1) # last added document
    return render_template('index.html', mars=last_doc) # pass data to and render home page


@app.route('/scrape')
def scrape():

    """ Scrape new data, update database with new data, and refresh page """

    mars_data = mars_scraper.scrape_all() # scrape new data
    mongo.db.mars.insert(mars_data) # add new data to collection
    return redirect('/', code=302) # redirect to home page with updated data


if __name__ == '__main__':
    app.run()