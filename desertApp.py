#from flask import Flask, render_template, redirect, jsonify
from flask_pymongo import PyMongo
from flask import Flask, render_template, redirect, jsonify, json, request
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#################################################
# Database Setup
#################################################
from passwords import paulgres
engine = create_engine('postgres://postgres:' + paulgres + '@localhost:5432/deserts')

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to each table
Contacts = Base.classes.contacts

# Create an instance of Flask
app = Flask(__name__)
#Prevent Jsonify from reoganizing dictionary
app.config['JSON_SORT_KEYS'] = False

# Route to render index.html template using data from Mongo
@app.route("/")
def home():
	return redirect("/index.html")

@app.route("/index.html")
def indexpage():
    return render_template("index.html")

@app.route("/viz.html")
def visualization():
    # Return template and data
    return render_template("viz.html")

@app.route("/api.html", methods=['GET', 'POST'])
def api():
    # Return template and data
    return render_template("api.html")

@app.route('/zipinputs', methods=['GET', 'POST'])
def zipinputs():
	return redirect('/api/v1.0/zip/'+str(request.form['zipcode']))

@app.route('/stateinputs', methods=['GET', 'POST'])
def stateinputs():
	return redirect('/api/v1.0/state/'+str(request.form['state']))

@app.route('/tractinputs', methods=['GET', 'POST'])
def tractinputs():
	return redirect('/api/v1.0/tract/'+str(request.form['tract']))

@app.route("/resources.html", methods=['GET', 'POST'])
def resources():
    # Return template and data
    errors= []
    if request.method == "POST":
        # get zipcode that the person has entered
        try:
        	zipcode = request.form['zipcode']
        	session = Session(engine)
        	results = session.query(Contacts.name, Contacts.phone).\
        		filter(Contacts.zip == zipcode).first()
        	session.close()
        	last, first = results[0].split(",")
        	final = [first, last, results[1]]
        	return render_template("resources.html", results=final)
        except:
            errors.append(
                "Unable to get Zipcode. Please make sure it's valid and try again."
            )
            return render_template('resources.html', errors=errors)
    return render_template("resources.html")

@app.route('/api/v1.0/zip/<zip_code>')
def loc_zip(zip_code):
	session = Session(engine)
	results = session.query(Contacts.zip, Contacts.tract, Contacts.distname, Contacts.name, Contacts.phone, Contacts.population, Contacts.desert, Contacts.url).\
    	filter(Contacts.zip == zip_code).all()
	session.close()
	return render_template("json.html", jsons =  dictionize(results), datatype = "Zip Code", datavalue = zip_code)

@app.route('/api/v1.0/state/<state>')
def loc_state(state):
	session = Session(engine)
	results = session.query(Contacts.zip, Contacts.tract, Contacts.distname, Contacts.name, Contacts.phone, Contacts.population, Contacts.desert, Contacts.url).\
    	filter(Contacts.state == state.upper()).all()
	session.close()
	return render_template("json.html", jsons =  dictionize(results), datatype = "State", datavalue = state.upper())

@app.route('/api/v1.0/tract/<census_tract>')
def loc_tract(census_tract):
	session = Session(engine)
	results = session.query(Contacts.zip, Contacts.tract, Contacts.distname, Contacts.name, Contacts.phone, Contacts.population, Contacts.desert, Contacts.url).\
    	filter(Contacts.tract == census_tract).all()
	session.close()
	return render_template("json.html", jsons = dictionize(results), datatype = "Census Tract", datavalue = census_tract)

@app.route('/api/v1.0/zipapi/<zip_code>')
def api_zip(zip_code):
	session = Session(engine)
	results = session.query(Contacts.zip, Contacts.tract, Contacts.distname, Contacts.name, Contacts.phone, Contacts.population, Contacts.desert, Contacts.url).\
    	filter(Contacts.zip == zip_code).all()
	session.close()
	return jsonify(dictionize(results))

@app.route('/api/v1.0/stateapi/<state>')
def api_state(state):
	session = Session(engine)
	results = session.query(Contacts.zip, Contacts.tract, Contacts.distname, Contacts.name, Contacts.phone, Contacts.population, Contacts.desert, Contacts.url).\
    	filter(Contacts.state == state.upper()).all()
	session.close()
	return jsonify(dictionize(results))

@app.route('/api/v1.0/tractapi/<census_tract>')
def api_tract(census_tract):
	session = Session(engine)
	results = session.query(Contacts.zip, Contacts.tract, Contacts.distname, Contacts.name, Contacts.phone, Contacts.population, Contacts.desert, Contacts.url).\
    	filter(Contacts.tract == census_tract).all()
	session.close()
	return jsonify(dictionize(results))


def dictionize(query_results):
	zipcode_results = []
	for zip_c, tract, district, rep, phone, population, desert, url in query_results:
		zips = {}
		zips["census_tract"] = tract
		zips["zipcode"] = str(zip_c).zfill(5)
		if desert == True:
			zips["food desert status"] = 'Yes'
		else:
			zips["food desert status"] = 'No'
		zips["district"] = district
		zips['contact_info'] = {}
		zips['contact_info']["representative"] = rep
		zips['contact_info']["phone"] = phone
		zips["population"] = population
		zips["tract_map"] = url
		zipcode_results.append(zips)
	return zipcode_results


if __name__ == "__main__":
    app.run(debug=True)
