from flask import Flask, render_template
from flask_pymongo import PyMongo
import nasa_scraper


# Flask app
app = Flask(__name__)

# Flask app's connection to MongoDB
mongo_uri = 'mongodb://localhost:27017/mars_db'
app.config['MONGO_URI'] = mongo_uri
mongo = PyMongo(app)


""" Routes """


@app.route('/')
def index():
    mars_doc = mongo.db.mars.find_one() # Document containing Mars data
    return render_template('index.html', mars=mars_doc)


@app.route('/scrape')
def scrape():
    mars = mongo.db.mars # Mars collection
    mars_data = nasa_scraper.scrape_all() # Scrape NASA site
    mars.replace_one({}, mars_data, upsert=True) # Update data
    return index()


if __name__ == '__main__':
    app.run()