from datetime import datetime, timedelta, timezone
from database import db
from sheets import sheets


#gets rid of weird symbols people enter as part of their number
def clean_number(number):
	print(number)
	if len(number) == 0:
		return number
	clean  = ""
	for i in number:
		if i.isdigit():
			clean += i
	if clean[0] == "1":
		clean = clean[1:]
	return clean

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
		self.date     = datetime.strptime(values['date'][0:13], '%Y-%m-%d %H')
		self.name     = values['name']
		self.number   = values['number']


	#return a string that looks nice
	def __str__(self):
		string = str(self.date_readable())
		string += ", ID: " + self.id
		return string

	#formats the date
	#Mon Jan 1 at 4:05 PM
	def date_readable(self):
		return self.date.strftime("%a %b %-d at %-I:%M %p")

	#firebase automatically stores things in UTC time, so this changes it to local
	def utc_to_local(self, utc_dt):
		return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

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

def update_scoreboard():
	people = []
	names = []
	then = datetime.now()
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

	print("scoreboard updated. time elapsed: " + str(datetime.now()-then))

def delete_shift(shift):
	db.child(shift.path).remove()
	active = sheets[shift.sheet]
	for i in range(0,2):
		active.update_cell(shift.row, shift.column + i, '')
		print("deleted: {},{},{}".format(shift.sheet,shift.row,shift.column))

"""def update_shift(path, response):
	db.child(shift.path).update({"lockedIn":response})"""

#queries database for all shifts tomorrow
#need UTC time for tomorrow and next day to get all shifts within that range in Firebase
def shifts_tomorrow():
	shifts = []

	tomorrow = datetime.utcnow() + timedelta(days=0)
	nextDay  = tomorrow + timedelta(days=1)
	tomorrow = tomorrow.strftime("%Y-%m-%d 06:00:00.000000")
	nextDay  = nextDay.strftime("%Y-%m-%d 06:00:00.000000")

	for child in db.child("shifts").order_by_child("date").start_at(tomorrow).end_at(nextDay).get().each():
		shifts.append(Shift(child.val()['id']))
	return shifts

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
	sheetNum = get_today_sheet()
	sheetData = sheet_data(sheetNum)
	data = {}
	for col in range(4, 13, 4):
		for row in range(3, 27):
			id = "c{}".format(create_id(sheetNum, row, col))
			hours = int((row-3)//4 *2 +10)
			date = datetime.today().replace(hour = hours) + timedelta(days=1)
			data[str(id)] = {
				"id":       id,
				"location": sheetData[0][col-1],
				"date":     str(date),
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

def get_today_sheet():
	"""find sheet for today"""

	today = datetime.today().strftime('%a %b %-d')

	print("finding today's sheet")

	for i in range(len(sheets)):
		if sheets[i].title == str(today):
			print("{} sheet found!".format(sheets[i].title))
			return i
	print("Sheet not found")

def sheet_data(sheetNum):
    active = sheets[sheetNum]
    rawData = active.range('A1:M26')
    cleanData = [[0 for x in range(13)] for y in range(26)]

    for i, cell in enumerate(rawData):
        print(cell.value)
        cleanData[i//13][int(i - 13*(i//13))] = cell.value

    print(cleanData)
    return(cleanData)


"""

fix every method to new thing
add timing for update methods
build sms sending stuyff
"""
