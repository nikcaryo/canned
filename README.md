# canned
Backend system for a highschool canned food drive sign up system. Users sign up for a canning shift on a Google Sheet by entering their name and phone number. A JS script within Google Sheets periodically syncs with a Firebase database, where a python Flask server can send out text reminders and listen for responses. Users have the option to cancel a shift from their phone, and the master Google Sheet will be automatically updated, allowing for others to take their shift. Periodically, the master Google Sheet is synced with Firebase and cleaned up to make sure no one is tampering with it. Heroku was used to host the Flask server.  



