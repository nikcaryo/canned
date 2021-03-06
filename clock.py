from redis import Redis
from worker import conn
from utils import *
from main import q, send_sms
from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()
print("clock running")


@sched.scheduled_job('interval', minutes=40)
def refresh_sheets():
	print("clock running")
	print("refreshing token!")
	q.enqueue(refresh_token)
	q.enqueu(check, 'token refreshed')

@sched.scheduled_job('cron', day_of_week='mon-sun', hour=17)
def send_sms():
	print("clock running")
	print("sending sms!")
	q.enqueue(send_sms)
	q.enqueu(check, 'texts sent')

@sched.scheduled_job('interval', minutes=15)
def update_clean():
	print("clock running")
	print("15 min elapsed. updating database")
	q.enqueue(clean_sheets)
	q.enqueu(check, 'db updated')


sched.start()
