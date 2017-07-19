from datetime import datetime, timedelta, timezone


import sheets
from database import db



class Person(object):
	def __init__(self, name, number):
		self.name   = name
		self.number = number
		self.shifts = 1

	def addShift(self):
		self.shifts += 1

class Shift(object):

	#gets values from Firebase based on ID given
	#date is stored as datetime object so time methods are easier
	def __init__(self, id):
		self.id       = id
		self.path     = "shifts/" + id
		values        = db.child("shifts").child(id).get().val()
		self.date     = self.utc_to_local(datetime.strptime(values['date'], '%Y-%m-%dT%H:%M:00.000Z'))
		self.name     = values['name']
		self.number   = self.clean_number(values['number'])
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

	#gets rid of weird symbols people enter as part of their number
	def clean_number(self, number):
		clean = ""
		for i in number:
			if i.isdigit():
				clean += i
		if clean[0] == "1":
			clean = clean[1:]
		return clean

	#firebase automatically stores things in UTC time, so this changes it to local
	def utc_to_local(self, utc_dt):
		return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

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

def delete_shift(path):
	db.child(path).remove()

def update_shift(path, shift):
	db.child(shift.id).update({"lockedIn":response})
	sheets.delete(shift.sheet, shift.row, shift.column)

#queries database for all shifts tomorrow
#need UTC time for tomorrow and next day to get all shifts within that range in Firebase
def shifts_tomorrow():
	shifts = []

	tomorrow = datetime.utcnow() + timedelta(days=1)
	nextDay  = tomorrow + timedelta(days=1)
	tomorrow = tomorrow.strftime("%Y-%m-%dT06:00:00.000Z")
	nextDay  = nextDay.strftime("%Y-%m-%dT06:00:00.000Z")

	for child in db.child("shifts").order_by_child("date").start_at(tomorrow).end_at(nextDay).get().each():
		shifts.append(Shift(child.val()['id']))

	print(status(shifts))

#queries database for all shifts that match the number given
#returns list of Shift objects
def shifts_from_number(number):
	shifts = []
	for child in db.child("shifts").order_by_child("number").equal_to(str(number)).get().each():
		id_ = child.val()['id']
		shifts.append(Shift(id_))
	return shifts
