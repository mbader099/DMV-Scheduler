import json
import requests

from flask import Flask, render_template, request, redirect
from datetime import datetime, timedelta

import maps
from scheduler import Scheduler

app = Flask(__name__)


@app.route("/")
def home():
    for svctype in maps.svc_types:
        svctype.fetchLocationsJson()
    min_date = datetime.today().strftime('%Y-%m-%d')
    max_date = (datetime.today() + timedelta(days=90)).strftime('%Y-%m-%d')
    return render_template("home.html", svc_types=[s.__dict__ for s in maps.svc_types], min_date=min_date, max_date=max_date)


@app.route("/appointmentSearch", methods=['POST'])
def apptSearch():
    data = request.form
    locations = request.form.getlist('locations')
    startdate = datetime.strptime(request.form.get('startdate'), "%Y-%m-%d").date()
    enddate = datetime.strptime(request.form.get('enddate'), "%Y-%m-%d").date()
    svcType = request.form.get('svcType')

    # Server Side Validation
    if (enddate < startdate):
        return "End Date cannot be before start date!", 400

    # Get location names
    locDict = {}
    for svc in maps.svc_types:
        if svc.svcId == svcType:
            svc.fetchLocationsJson()
            for loc in svc.locationsJson:
                locDict[loc["locationID"]] = loc["location"]
            break

    # Start Selenium Script to pull appointments
    sched = Scheduler()
    appts = sched.searchForAppointments(locations, startdate, enddate)

    # Return Appointments
    return render_template("appt_search_results.html", locations=locDict, appts=[s.toJSON() for s in appts])


def scheduleAppointment():
    print("test")


app.run('127.0.0.1', 8080, debug=True)
