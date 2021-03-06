import os
from flask import Flask, request, redirect, render_template
from twilio.twiml.messaging_response import MessagingResponse
from rq import Queue
from redis import Redis
from worker import conn
from utils import *

import time
import atexit

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

q = Queue(connection=conn)
app = Flask(__name__)



def update():
	q.enqueue(clean_sheets)
	q.enqueue(update_shifts)

@app.route('/<string:page_name>/')
def render_static(page_name):
	if page_name == "update":
		update()
	if page_name == "sms":
		q.enqueue(send_sms)


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
		thisShift = Shift(body[body.index("c"):])
	except (ValueError):
		response.message("huh? use the right format plz")
		return str(response)

	print("shift number " + str(thisShift.number))
	if (int(number) != int(thisShift.number)):
		message = "thats not your shift"
		response.message(message)
		return str(response)
	elif ("confirm" in body):
		q.enqueue(update_shift, thisShift.path, "no")
		message = "shift #" + str(thisShift.id) + " locked in"
	elif "no" in body:
		q.enqueue(update_shift, thisShift.path, "yes")
		message = "shift #" + str(thisShift.id) + " unlocked"
	elif "delete" in body:
		q.enqueue(delete_shift, thisShift)
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
	update()

	app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)


#TODO reminder if multiple shifts on same days
#number but no name?
#area code shit
#add more locations
#better replying conversation flow
#pay for heroku
