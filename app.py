# Import the dependencies.
from flask import Flask, jsonify

import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/") # beginning route and explanation of API routes
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/station<br/>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/2016-08-23<br>"
        f"&emsp;ex: 2016-08-23 can be replaced with other start date in a format of yyyy-mm-dd<br>"
        f"/api/v1.0/2016-08-23/2017-01-01<br>"
        f"&emsp;ex: 2016-08-23 can be replaced with other start date in a format of yyyy-mm-dd<br>"
        f"&emsp;ex: 2017-01-01 can be replaced with other end date in a format of yyyy-mm-dd<br>"
        f"&emsp;<b>Reminder</b>: please choose your start and end date between 2010-01-01 to 2017-08-23"
    )

@app.route("/api/v1.0/precipitation") #run data for precipitation
def precipitation():
    most_recent = session.query(measurement).order_by(measurement.date.desc()).first()
    end_date = dt.datetime.strptime(most_recent.date, '%Y-%m-%d').date()
    start_date = end_date - dt.timedelta(days = 365)
    query = session.query(measurement.date,measurement.prcp).\
        filter(measurement.date >= start_date).order_by(measurement.date).all()
    dict1 = {date: prcp for date, prcp in query}
    return jsonify(dict1)

@app.route("/api/v1.0/station") #run data for station
def station():
    query2 = session.query(measurement.station).group_by(measurement.station).all()
    station = list(np.ravel(query2))
    return jsonify(station)


@app.route("/api/v1.0/tobs") #run data for temperature
def tobs():
    most_recent = session.query(measurement).order_by(measurement.date.desc()).first()
    end_date = dt.datetime.strptime(most_recent.date, '%Y-%m-%d').date()
    start_date = end_date - dt.timedelta(days = 365)
    query3 = session.query(measurement.date, measurement.tobs).\
        filter(measurement.date >= start_date).filter(measurement.station == 'USC00519281').\
            order_by(measurement.date).all()
    dict2 = {date: temp for date, temp in query3}
    return jsonify(dict2)

@app.route("/api/v1.0/<start>") # run temperature statistic with start day of choice
def start(start):
    query4 = session.query(func.min(measurement.tobs),\
                                  func.max(measurement.tobs),\
                                  func.avg(measurement.tobs)).\
                                    filter(measurement.station == 'USC00519281').\
                                        filter(measurement.date >= start).all()
    #return query4
    if query4: # return minimum, maximum and average temperature with begin date of choice
        min_temp, max_temp, avg_temp = query4[0]
        result_dict = {
            "min_temperature": min_temp,
            "max_temperature": max_temp,
            "avg_temperature": avg_temp
        }
        return jsonify(result_dict)
    else:
        return jsonify({"error": "No data found for the specified date and station"}), 404

@app.route("/api/v1.0/<start>/<end>") # run temperature statistic with start and end day of choice
def start_end(start, end):
    query5 = session.query(func.min(measurement.tobs),\
                                  func.max(measurement.tobs),\
                                  func.avg(measurement.tobs)).\
                                    filter(measurement.station == 'USC00519281').\
                                        filter(measurement.date <= end).\
                                        filter(measurement.date >= start).all()
    if query5: # return minimum, maximum and average temperature with begin and end date of choice
        min_temp, max_temp, avg_temp = query5[0]
        result_dict = {
            "min_temperature": min_temp,
            "max_temperature": max_temp,
            "avg_temperature": avg_temp
        }
        return jsonify(result_dict)
    else:
        return jsonify({"error": "No data found for the specified date and station"}), 404


if __name__ == '__main__':
    app.run(debug=True)