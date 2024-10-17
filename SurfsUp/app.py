# Import the dependencies.
import warnings
warnings.filterwarnings('ignore')
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy import func



#################################################
# Database Setup
#################################################


# Python SQL toolkit and Object Relational Mapper
from flask import Flask, jsonify
from sqlalchemy.orm import Session
import datetime as dt


# Create an engine for the chinook.sqlite database
engine = create_engine("sqlite:///C:/Users/weiwei/Bootcamp/sqlalchemy-challenge/SurfsUp/Resources/hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)
print(Base.classes.keys())


# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return ("Welcome to the Hawaii Climate API!<br/>"
            "Available Routes:<br/>"
            "/api/v1.0/precipitation<br/>"
            "/api/v1.0/stations<br/>"
            "/api/v1.0/tobs<br/>"
            "/api/v1.0/<start><br/>"
            "/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def percipitation():
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = dt.datetime.strptime(most_recent_date,'%Y-%m-%d')
    one_year_ago = most_recent_date - dt.timedelta(days=365)

    query = session.query(Measurement.date,Measurement.prcp).\
    filter(Measurement.date >= one_year_ago).\
    order_by(Measurement.date).all()

    precipitation_dict = {date: prcp for date, prcp in query}

    return jsonify(precipitation_dict)


@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()

    stations_list = [station[0] for station in results]
    return jsonify(stations_list)


@app.route("/api/v1.0/tobs")
def tobs():
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = dt.datetime.strptime(most_recent_date,'%Y-%m-%d')
    one_year_ago = most_recent_date - dt.timedelta(days=365)

    most_active_station_id = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.id).desc()).first()[0]
    results = session.query(Measurement.date,Measurement.tobs).filter(Measurement.station == most_active_station_id).filter(Measurement.date >= one_year_ago).all()
    temp_obs_list = [(date,tobs) for date,tobs in results]

    return jsonify(temp_obs_list)

@app.route('/api/v1.0/<start>')
def start_stats(start):
    results = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start).all()

    stats_dict ={
        'TMIN': results[0][0],
        'TAVG': results[0][1],
        'TMAX': results[0][2]
    }

    return jsonify(stats_dict)

@app.route('/api/v1.0/<start>/<end>')
def start_end_stats(start,end):
    results = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    stats_dict =  {
        'TMIN': results[0][0],
        'TAVG': results[0][1],
        'TMAX': results[0][2]
    }

    return jsonify(stats_dict)

if __name__=="__main__":
    app.run(debug=True)