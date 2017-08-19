import gspread
from datetime import datetime, timedelta
from oauth2client.service_account import ServiceAccountCredentials

SHEET_NAMES = ['Tue Aug 15', 'Wed Aug 16', 'Thu Aug 17', 'Fri Aug 18', 'Sat Aug 19', 'Sun Aug 20', 'Mon Aug 21', 'Tue Aug 22', 'Wed Aug 23', 'Thu Aug 24', 'Fri Aug 25', 'Sat Aug 26', 'Sun Aug 27', 'Mon Aug 28', 'Tue Aug 29', 'Wed Aug 30', 'Thu Aug 31', 'Fri Sep 1', 'Sat Sep 2', 'Sun Sep 3', 'Mon Sep 4', 'Tue Sep 5', 'Wed Sep 6', 'Thu Sep 7', 'Fri Sep 8', 'Sat Sep 9', 'Sun Sep 10', 'Mon Sep 11', 'Tue Sep 12', 'Wed Sep 13']
BAD_WORDS = ['shit', 'fuck']

scope = ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name('key.json', scope)
gc = gspread.authorize(credentials)


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
		print(cell.value)
		cleanData[i//13][int(i - 13*(i//13))] = cell.value

	print(cleanData)
	active.update_cell(1,1,"last synced at: {}".format(datetime.now()))
	return(cleanData)
