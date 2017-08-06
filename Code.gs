function writeDataToFirebase() {
  var ss = SpreadsheetApp.openById("1DK18DwJBnEMgJiyhRM_cb__IjFuiDy9XqofqLMS8aoc");
  var firebaseUrl = "https://canned-test.firebaseio.com/";
  var base = FirebaseApp.getDatabaseByUrl("https://canned-test.firebaseio.com/");
  var dataToImport = {};
  var sheets = ss.getSheets()
  var today = new Date()
  Logger.log(today)
  days = ["Sun", "Mon", "Tues", "Wed", "Thurs", "Fri", "Sat"]
  months = ["","","","","","","","Aug","","Oct","Nov", "Dec"]
  var todayString = days[today.getDay()] + " " + months[today.getMonth()] + " " + today.getDate()
  Logger.log(todayString)

  for (i = 0; i < sheets.length; i++){
    if (sheets[i].getName() === todayString){
      todaySheet = i;
      Logger.log(todaySheet)
      break;
      }
  }

  dataToImport = {}
  sheet = sheets[todaySheet]

  CHARS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M']
  LOCATIONS = ["Safeway", "Bianchinnis", "DRAEGERS"]

  for(col = 3; col < 12; col += 4){
    location = LOCATIONS[i/4]
    for(row = 3; row < 27; row++){
      var colRow = CHARS[col] + "" + row
      var nextColRow = CHARS[col+1] + "" + row
      var tempDateTime = new Date()
      tempDateTime.setHours( ((row-3)/4)*2 + 9)
      var id = "c" + todaySheet + paddle(row) + paddle((col+1))
      var name = sheet.getRange(colRow).getValue()
      var number = sheet.getRange(nextColRow).getValue()

      dataToImport[id] = {
        id: id,
        date: tempDateTime,
        name: name,
        number: cleanNumber(number),
        sheet: todaySheet,
        row: row,
        column: col + 1
      };
    }
  }

      var empty = {}
      base.setData("shifts", empty)
      base.setData("shifts", dataToImport)


}
function paddle(num){
  if (num < 10)
    return "0" + num
  else
    return num
}

function watchyoprofanity(){
  badWords = ["shit", "fuck", "bitch", "dumb", "dick"]
  var ss = SpreadsheetApp.openById("1DK18DwJBnEMgJiyhRM_cb__IjFuiDy9XqofqLMS8aoc");
  var sheets = ss.getSheets()
  for (sheet in sheets) {
    var data = sheet.getDataRange().getValues()
    for (i = 0; i < data.length(); i++){
      for (word in badWords){
        if (data[i][4].indexOf(word) != -1)
          data[i][4].setValue("thats a bad word")
          }
       }
    }
}








function cleanNumber(number) {
  number += "";
  clean = number.replace(/\D/g,'');
  if (clean.substring(0,1).equals("1")){
    clean = clean.substring(1,clean.length);
    }
   return clean;
 }



function sendSMS(to, body) {
  var messages_url = "https://api.twilio.com/2010-04-01/Accounts/ACee8ef9cbef1643834353fe2711428162/Messages.json";
  var payload = {
    "To": to,
    "Body" : body,
    "From" : "14158533663"
  };
  var options = {
    "method" : "post",
    "payload" : payload
  };
  options.headers = {
    "Authorization" : "Basic " + Utilities.base64Encode("ACee8ef9cbef1643834353fe2711428162:b863f7fa4942fbc15c1bc304c6cf79d4")
  };
  UrlFetchApp.fetch(messages_url, options);
}
