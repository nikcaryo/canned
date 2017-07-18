from flask import Flask, request, redirect, render_template
from twilio.twiml.messaging_response import MessagingResponse
from datetime import datetime, timedelta, timezone
from rq_scheduler import Scheduler
from redis import Redis

import pyrebase
import string
from sheets import delete
from lib import *

import os

from rq import Queue
from worker import conn

q = Queue(connection=conn)

config = {
  "apiKey": "AIzaSyDfwUxnBYr-1yn4MjiTnJ2Jyyby1OQgm4Q",
  "authDomain": "canned-test.firebaseapp.com",
  "databaseURL": "https://canned-test.firebaseio.com",
  "storageBucket": "canned-test.appspot.com"
 }

firebase = pyrebase.initialize_app(config)
db = firebase.database()

def test():
	print("here we go")
	print(new_shift("c001"))
	#q.enqueue(shifts_from_number, 6502797134)
	#q.enqueue(update_scoreboard)
	#q.enqueue(delete, 1, 1, 1)



app = Flask(__name__)


@app.route('/<string:page_name>/')
def render_static(page_name):
	if page_name == "update":
		q.enqueue(update_scoreboard)
	return render_template('%s.html' % page_name)

@app.route("/sms", methods = ('GET', 'POST'))
def sms_reply():
	response = MessagingResponse()
	body     = request.values.get('Body', None)
	number   = int(request.values.get('From')[2:])
	message  = ""
	shifts   = shifts_from_number((number))

	print("phone " + str(number))

	print(body)
	print(shifts)
	print(len(shifts))


	if len(shifts) == 0:
	   response.message("Hmm, you havent signed up for any shifts yet")
	   return str(response)
	elif "shifts" in body:
		response.message(status(shifts))
		return str(response)
	elif "options" in body:
		response.message(options())
		return str(response)

	try:
		thisShift = new_shift(body[body.index("c"):])
	except (ValueError):
		response.message("huh? use the right format plz")
		return str(response)

	print("shift number " + str(thisShift.number))
	if (int(number) != int(thisShift.number)):
		message = "thats not your shift"
		response.message(message)
		return str(response)
	elif ("confirm" in body):
		db.child(thisShift.path).update({"lockedIn":"yes"})
		message = "shift #" + str(thisShift.id) + " locked in"
	elif "no" in body:
		db.child(thisShift.path).update({"lockedIn": "no"})
		message = "shift #" + str(thisShift.id) + " unlocked"
	elif "delete" in body:
		db.child(thisShift.path).remove()
		message = "shift #" + str(thisShift.id) + " deleted"

	#refresh shift data, cause we changed it up
	shifts = shifts_from_number((number))
	message += "\n\n" + status(shifts)
	print(message)
	response.message(message)
	return str(response)






if __name__ == "__main__":
	# Bind to PORT if defined, otherwise default to 5000.
	port = int(os.environ.get('PORT', 5000))
	test()
	app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
