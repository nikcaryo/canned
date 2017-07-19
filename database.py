import pyrebase

config = {
  "apiKey": "AIzaSyDfwUxnBYr-1yn4MjiTnJ2Jyyby1OQgm4Q",
  "authDomain": "canned-test.firebaseapp.com",
  "databaseURL": "https://canned-test.firebaseio.com",
  "storageBucket": "canned-test.appspot.com"
 }

firebase = pyrebase.initialize_app(config)
db = firebase.database()
