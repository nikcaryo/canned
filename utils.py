from datetime import datetime, timedelta, timezone
from database import db
from sheets import get_sheets, clean_sheets, get_today_sheet, get_sheet_data
from sms import client

class Person(object):
	def __init__(self, name, number):
		self.name   = name
		self.number = number
		self.shifts = 1

	def addShift(self):
		self.shifts += 1

	def __str__(self):
		return self.name

class Shift(object):

	#gets values from Firebase based on ID given
	#date is stored as datetime object so time methods are easier
	def __init__(self, id):
		self.id       = id
		self.path     = "shifts/" + id
		values        = db.child("shifts").child(id).get().val()
		self.sheet    = values['sheet']
		self.row      = values['row']
		self.column   = values['column']
		tempDate	  = values['date'] + " " + values['time']
		self.date     = datetime.strptime(tempDate, '%a %b %d %I:%M %p').replace(year=2017)
		self.name     = values['name']
		self.number   = values['number']
		self.location = values['location']


	#return a string that looks nice
	def __str__(self):
		string = str(self.date_readable())
		string += ", ID: " + self.id
		return string

	#formats the date
	#Mon Jan 1 at 4:05 PM
	def date_readable(self):
		return self.date.strftime("%a %b %d at %-I:%M %p")

	def time_readable(self):
		return self.date.strftime("%-I:%M %p")

	#firebase automatically stores things in UTC time, so this changes it to local
	def utc_to_local(self, utc_dt):
		return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

#gets rid of weird symbols people enter as part of their number
def clean_number(number):
	#if it's blank or contains letters, just store the whole thing. let twilio figure out it's not a number
	if len(number) == 0 or (number.isupper() or number.islower()):
		return number
	else:
		clean  = ""
		for i in number:
			if i.isdigit():
				clean += i
		if clean[0] == "1":
			clean = clean[1:]
		return clean

def status(shifts):
	message = "Current Shifts:"
	for shift in shifts:
		message += "\n" + str(shift)
	message += "\n\nReply confirm/delete followed by the ID to lock in/cancel a shift"
	message += "\nOr, reply \'shifts\' to see the status of your shifts"
	message += "\ni.e. \"confirm #a3\""
	return message

def options():
	message = "reply \'confirm (id)\' to lock in your shift"
	message += "\nreply \'delete (id)\' to delete your shift"
	message += "\n reply \'shifts\' to see your shifts"
	message += "\n reply \'STOP\' to stop these reminders"
	return message

def update_scoreboard():
	people = []
	names = []
	for child in db.child("shifts").get().each():
		name = child.val()["name"]
		number = child.val()["number"]
		if name in names :
			people[names.index(name)].addShift()
		elif name != "":
			people.append(Person(name, number))
			names.append(name)
	print(people)
	for person in people:
		data = {
				"name": person.name,
				"shifts" : person.shifts
				}
		db.child("scoreboard").child(str(person.name)).set(data)

	print("scoreboard updated")

def delete_shift(shift):
	active = get_sheets()[shift.sheet]
	for i in range(0,2):
		active.update_cell(shift.row, shift.column + i, '')
		print("deleted: {},{},{}".format(shift.sheet,shift.row,shift.column))
	db.child(shift.path).remove()

"""def update_shift(path, response):
	db.child(shift.path).update({"lockedIn":response})"""

#queries database for all shifts tomorrow
#need UTC time for tomorrow and next day to get all shifts within that range in Firebase
def shifts_tomorrow():
	shifts = []
	tomorrow = (datetime.now() + timedelta(days=1)).strftime('%a %b %-d')

	print("checking {}".format(tomorrow))
	for child in db.child("shifts").order_by_child("date").equal_to(tomorrow).get().each():
		print(child)
		if child.val()['name'] != '':
			shifts.append(Shift(child.val()['id']))
	print(shifts)
	return shifts

def send_sms():
	for shift in shifts_tomorrow():
		try:
			message = client.messages.create(
				to     = "+1{}".format(shift.number),
				from_  = "+14158533663",
				body   = "Hey {}! Looks like you're signed up for a shift tomorrow at {} at {}!\nThis shift's id is: {} \n\n {}".format(shift.name, shift.time_readable(), shift.location, shift.id, options())
				)
		except:
			pass


#queries database for all shifts that match the number given
#returns list of Shift objects
def shifts_from_number(number):
	shifts = []
	for child in db.child("shifts").order_by_child("number").equal_to(str(number)).get().each():
		id_ = child.val()['id']
		shifts.append(Shift(id_))
	print(shifts)
	return shifts

def update_shifts():
	db.child("shifts").set({})
	ALLsheetData = get_sheet_data()
	for sheetNum, sheet in enumerate(get_sheets()):
		print('{} being updated'.format(sheet.name))
		sheetData = ALLsheetData[sheetNum]
		data = {}
		for col in range(4, 13, 4):
			for row in range(3, 27):
				print('{}{} being updated'.format(col, row))
				if len(sheetData[row-1][col-1])!=0 and not(sheetData[row-1][col-1].isspace()):
					id = "c{}".format(create_id(sheetNum, row, col))
					hours = int((row-3)//4 *2 +10)
					time = ''
					if hours > 12:
						hours -= 12
						time = "{}:00 PM".format(hours)
					elif hours == 12:
						time = "12:00 PM"
					else:
						time = "{}:00 AM".format(hours)
					data[str(id)] = {
						"id":       id,
						"location": sheetData[0][col-1],
						"date":     sheet.title,
						"time":		time,
						"name":     sheetData[row-1][col-1],
						"number":   clean_number(sheetData[row-1][col]),
						"sheet":    sheetNum,
						"row":      row,
						"column":   col
					  }
					print("shift {} updated".format(data[str(id)]))

			db.child("shifts").update(data)
	update_scoreboard()

def create_id(x, y, z):
	"""
		using this little formula to generate the shift IDs
		its a pairing function, but for 3 integers
		so it'll give you a unique number for any (x,y,z) with order mattering
		so it'll make the shift ids shorter and easier to type
		http://dmauro.com/post/77011214305/a-hashing-function-for-x-y-z-coordinates
	"""

	big = max(x, y, z)
	hash = big^3 + (2 * big * z) + z
	if (big == z):
		hash += max(x, y)^2
	if (y >= x):
		hash += x + y
	else:
		hash += y
	return hash

def check(name):
	message = client.messages.create(
		to    = "6502797134",
		from_ = "+14158533663",
		body  = name
		)
