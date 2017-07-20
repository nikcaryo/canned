import os
from flask import Flask, request, redirect, render_template
from twilio.twiml.messaging_response import MessagingResponse
from rq import Queue
from rq_scheduler import Scheduler
from redis import Redis
from worker import conn
from utils import *


q = Queue(connection=conn)


def test():
	print("here we go")
	print(Shift("c045"))
	q.enqueue(shifts_from_number, 6502797134)
	q.enqueue(update_scoreboard)
	q.enqueue(sheets.delete, 1, 1, 1)

def status(shifts):
	message = "Current Shifts:"
	for shift in shifts:
		message += "\n" + str(shift)
	message += "\n\nReply confirm/delete followed by the ID to lock in/cancel a shift"
	message += "\nOr, reply \'shifts\' to see the status of your shifts"
	message += "\ni.e. \"confirm #a3\""
	return message

def options():
	message = "reply \'confirm #id\' to lock in your shift"
	message += "\nreply \'delete #id\' to delete your shift"
	message += "\n reply \'shifts\' to see your shifts"
	message += "\n reply \'STOP\' to stop these reminders"
	return message


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
	test()
	app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
