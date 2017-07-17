from flask import Flask, request, redirect, render_template
from twilio.twiml.messaging_response import MessagingResponse
from datetime import datetime, timedelta, timezone
import schedule
import pyrebase
import string
import sheets
import os



config = {
  "apiKey": "AIzaSyDfwUxnBYr-1yn4MjiTnJ2Jyyby1OQgm4Q",
  "authDomain": "canned-test.firebaseapp.com",
  "databaseURL": "https://canned-test.firebaseio.com",
  "storageBucket": "canned-test.appspot.com"
 }

firebase = pyrebase.initialize_app(config)
db = firebase.database()

#holds data for a person and the number of shifts theyve signed up for
class Person(object):
	def __init__(self, name, number):
		self.name   = name
		self.number = number
		self.shifts = 1

	def addShift(self):
		self.shifts += 1

#holds all data for an individual shift (name, number, id, time, place etc)
class Shift(object):

	#gets values from Firebase based on ID given
	#date is stored as datetime object so time methods are easier
	def __init__(self, id):
		self.id       = id
		self.path     = "shifts/" + id
		values        = db.child("shifts").child(id).get().val()
		self.date     = utc_to_local(datetime.strptime(values['date'], '%Y-%m-%dT%H:%M:00.000Z'))
		self.name     = values['name']
		self.number   = clean_number(values['number'])
		self.lockedIn = values['lockedIn']
		self.sheet    = values['sheet']
		self.row      = values['row']
		self.column   = values['column']

	#return a string that looks nice
	def __str__(self):
		string = str(self.date_readable())
		string += ", ID: " + self.id
		string += ", Locked in? " + self.lockedIn
		return string

	#formats the date
	#Mon Jan 1 at 4:05 PM
	def date_readable(self):
		return self.date.strftime("%a %b %-d at %-I:%M %p")

#makes a new shift
def new_shift(id):
	return Shift(id)

def test():
    print("here we go")
	#update_scoreboard()

#firebase automatically stores things in UTC time, so this changes it to local
def utc_to_local(utc_dt):
	return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

#queries database for all shifts tomorrow
#need UTC time for tomorrow and next day to get all shifts within that range in Firebase
def shifts_tomorrow():
	shifts = []

	tomorrow = datetime.utcnow() + timedelta(days=1)
	nextDay  = tomorrow + timedelta(days=1)
	tomorrow = tomorrow.strftime("%Y-%m-%dT06:00:00.000Z")
	nextDay  = nextDay.strftime("%Y-%m-%dT06:00:00.000Z")

	for child in db.child("shifts").order_by_child("date").start_at(tomorrow).end_at(nextDay).get().each():
		shifts.append(new_shift(child.val()['id']))

	print(status(shifts))

#gets rid of weird symbols people enter as part of their number
def clean_number(number):
	clean = ""
	for i in number:
		if i.isdigit():
			clean += i
	if clean[0] == "1":
		clean = clean[1:]
	return clean

#queries database for all shifts that match the number given
#returns list of Shift objects
def shifts_from_number(number):
	shifts = []
	for child in db.child("shifts").order_by_child("number").equal_to(str(number)).get().each():
		id_ = child.val()['id']
		shifts.append(new_shift(id_))
	return shifts

#finds number of shifts associated with each student ID and stores it in Firebase
def update_scoreboard():
	people = []
	names = []
	then = datetime.now()
	for child in db.child("shifts").get().each():
		name = child.val()["name"]
		number = child.val()["number"]
		if name in names:
			people[names.index(name)].addShift()
		else:
			people.append(Person(name, number))
			names.append(name)
	data = {}
	for person in people:
		this = {}
		this["name"] = person.name
		this["shifts"] = person.shifts
		path = "scoreboard/" + str(person.name)
		data[path] = this
	print("scoreboard updated. time elapsed: " + str(datetime.now()-then))
	db.update(data)


#formats list of Shifts by calling their __str__ method
#adds some info afterwards
def status(shifts):
	message = "Current Shifts:"
	for shift in shifts:
		message += "\n" + str(shift)
	message += "\n\nReply confirm/delete followed by the ID to lock in/cancel a shift"
	message += "\nOr, reply \'shifts\' to see the status of your shifts"
	message += "\ni.e. \"confirm #a3\""
	return message

#returns string of stuff user can do
def options():
	message = "reply \'confirm #id\' to lock in your shift"
	message += "\nreply \'delete #id\' to delete your shift"
	message += "\n reply \'shifts\' to see your shifts"
	message += "\n reply \'STOP\' to stop these reminders"
	return message

app = Flask(__name__)


@app.route('/<string:page_name>/')
def render_static(page_name):
    return render_template('%s.html' % page_name)

@app.route("/sms", methods = ('GET', 'POST'))
def sms_reply():
	response = MessagingResponse()
	body     = request.values.get('Body', None)
	number   = int(request.values.get('From')[2:])
	message  = ""
	shifts   = shifts_from_number((number))

	print(number)
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
		thisShift = new_shift(body[body.index("c")+1:])
	except (ValueError):
		response.message("huh? use the right format plz")
	return str(response)

	if (number != thisShift.number):
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
    app.run(host='0.0.0.0', port=port, debug=True)
