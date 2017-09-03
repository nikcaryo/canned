import gspread
from datetime import datetime, timedelta
from oauth2client.service_account import ServiceAccountCredentials


SHEET_NAMES = ['Sat Sep 2', 'Sun Sep 3', 'Mon Sep 4', 'Tue Sep 5', 'Wed Sep 6', 'Thu Sep 7', 'Fri Sep 8', 'Sat Sep 9', 'Sun Sep 10', 'Mon Sep 11', 'Tue Sep 12', 'Wed Sep 13', 'Thu Sep 14', 'Fri Sep 15', 'Sat Sep 16', 'Sun Sep 17', 'Mon Sep 18', 'Tue Sep 19', 'Wed Sep 20', 'Thu Sep 21', 'Fri Sep 22', 'Sat Sep 23', 'Sun Sep 24', 'Mon Sep 25', 'Tue Sep 26', 'Wed Sep 27', 'Thu Sep 28', 'Fri Sep 29', 'Sat Sep 30', 'Sun Oct 1']

scope = ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name('key.json', scope)
gc = gspread.authorize(credentials)

def sheet_names():
	SHEET_NAMES = []
	for i in range(0,30):
		SHEET_NAMES.append((datetime.now()+timedelta(days=i)).strftime('%a %b %-d'))
	print(SHEET_NAMES)



sheet_names()

def get_sheets():
	spread = gc.open('canned test')
	sheets = spread.worksheets()
	return sheets

def clean_sheets():
	spread = gc.open('canned test')
	sheets = spread.worksheets()
	for sheet in sheets:
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



def sheet_data(sheetNum):
	active = get_sheets()[sheetNum]
	rawData = active.range('A1:M26')
	cleanData = [[0 for x in range(13)] for y in range(26)]

	for i, cell in enumerate(rawData):
		cleanData[i//13][int(i - 13*(i//13))] = cell.value
		if len(cell.value)!= 0 and not(cell.value.isspace()):
			print(cell.value)
	active.update_cell(1,1,"last synced at: {}".format(datetime.now().strftime('%c')))
	return(cleanData)
