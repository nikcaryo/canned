import pyrebase

config = {
  "apiKey": "AIzaSyAkvtnmwoG7pxTif0RHSqbJxMrFI_LcgFA",
  "authDomain": "ma-canned-food-drive-2017.firebaseapp.com",
  "databaseURL": "https://ma-canned-food-drive-2017.firebaseio.com",
  "storageBucket": "ma-canned-food-drive-2017.appspot.com",
  "serviceAccount": "key_firebase.json"

 }

firebase = pyrebase.initialize_app(config)
db = firebase.database()
