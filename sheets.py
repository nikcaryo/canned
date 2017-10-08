import gspread
from datetime import datetime, timedelta
from oauth2client.service_account import ServiceAccountCredentials


SHEET_NAMES = ['Sat Oct 7', 'Sun Oct 8', 'Mon Oct 9', 'Tue Oct 10', 'Wed Oct 11', 'Thu Oct 12', 'Fri Oct 13', 'Sat Oct 14', 'Sun Oct 15', 'Mon Oct 16', 'Tue Oct 17', 'Wed Oct 18', 'Thu Oct 19', 'Fri Oct 20', 'Sat Oct 21', 'Sun Oct 22', 'Mon Oct 23', 'Tue Oct 24', 'Wed Oct 25', 'Thu Oct 26', 'Fri Oct 27', 'Sat Oct 28', 'Sun Oct 29', 'Mon Oct 30', 'Tue Oct 31', 'Wed Nov 1', 'Thu Nov 2', 'Fri Nov 3', 'Sat Nov 4', 'Sun Nov 5']
BAD_WORDS = ["fuck", "shit"]

scope = ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name('key_sheets.json', scope)
gc = gspread.authorize(credentials)


def sheet_names():
	SHEET_NAMES = []
	for i in range(0,30):
		SHEET_NAMES.append((datetime.now()+timedelta(days=i)).strftime('%a %b %-d'))
	print(SHEET_NAMES)

def get_sheets():
	spread = gc.open('MA Canned Food Drive Signups')
	sheets = spread.worksheets()
	return sheets

def clean_sheets():
	spread = gc.open('MA Canned Food Drive Signups')
	sheets = spread.worksheets()
	for sheet in sheets:
		print(sheet.title)
		if sheet.title not in SHEET_NAMES:
			spread.del_worksheet(sheet)
		else:
			rawData = sheet.range('A1:M26')
			for cell in rawData:
				if cell.value in BAD_WORDS:
					sheet.update_cell(cell.row, cell.col, "")
					sheet.update_cell(cell.row, cell.col+1, "")

def get_today_sheet():
	"""find sheet for today"""

	today = datetime.now().strftime('%a %b %-d')

	print("finding today's sheet")
	print(today)
	sheets = get_sheets()
	for i in range(len(sheets)):
		print(sheets[i].title)
		if sheets[i].title == str(today):
			print("{} sheet found!".format(sheets[i].title))
			return i
	print("Sheet not found")

def get_sheet_data():
	sheets = get_sheets()
	sheetData = [x for x in range(len(sheets))]
	print(sheetData)
	for i, sheet in enumerate(sheets):
		sheetData[i] = sheet.get_all_values()
	return sheetData

def old():
	rawData = sheet.range('A1:M26')
	cleanData = [[0 for x in range(13)] for y in range(26)]
	for i, cell in enumerate(rawData):
		cleanData[i//13][int(i - 13*(i//13))] = cell.value
		if len(cell.value)!= 0 and not(cell.value.isspace()):
			print(cell.value)
	sheet.update_cell(1,1,"last synced at: {}".format(datetime.now().strftime('%c')))
	return(cleanData)
