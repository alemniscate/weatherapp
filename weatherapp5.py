from flask import Flask
from flask import render_template
from flask import request
import sys
import requests
import json
from flask_sqlalchemy import SQLAlchemy
from flask import redirect, url_for
from flask import flash
import time

def dbtolist(dbcities):
    city_list = []
    for dbcity in dbcities:
        dict = {}
        dict["id"] = dbcity.id
        dict["city_name"] = dbcity.name
        dict["temperature"] = dbcity.degree
        dict["state"] = dbcity.state
        if dbcity.sunrise < time.time() < dbcity.sunset:
            dict["night"] = False
        else:
            dict["night"] = True
        city_list.append(dict)
    return city_list

apikey = "80ad4440ce5819c5e011b22c2f160f6a"
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
db = SQLAlchemy(app)

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    degree = db.Column(db.Float)
    state = db.Column(db.String(80))
    sunrise = db.Column(db.Integer)
    sunset = db.Column(db.Integer)

db.create_all()

#@app.route('/')
#def index():
#    return render_template('index.html')

@app.route('/')
def display():
    city_list = dbtolist(City.query.all())
    return render_template('index.html', cities=city_list)

@app.route('/add', methods=['POST'])
def add_city():
    city_name = request.form['city_name']
    city = City.query.filter_by(name=city_name).first()
    if city == None:  
        res = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={apikey}&units=metric")
        if res.status_code == 200:
            dict = json.loads(res.text)
            weather = dict["weather"][0]
            state = weather["main"]
            temperature = dict["main"]["temp"]
            sunrise = dict["sys"]["sunrise"]
            sunset = dict["sys"]["sunset"]
            db.session.add(City(name=city_name, degree=temperature, state=state, sunrise=sunrise, sunset=sunset))
            try:
                db.session.commit()
            except Exception:
                pass
        else:
            flash("The city doesn't exist!")
    else:
        flash("The city has already been added to the list!")
    return redirect('/')

@app.route('/delete/<city_id>', methods=['GET', 'POST'])
def delete(city_id):
    city = City.query.filter_by(id=city_id).first()
    db.session.delete(city)
    db.session.commit()
    return redirect('/')

# don't change the following way to run flask:
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()