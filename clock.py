from redis import Redis
from worker import conn
from utils import *
from main import q, send_sms
from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()



@sched.scheduled_job('cron', day_of_week='mon-sun', hour=17)
def send_sms():
	q.enqueue(send_sms)

@sched.scheduled_job('interval', minutes=15)
def update_clean():
	print("15 min elapsed. updating database")
	q.enqueue(clean_sheets)
	q.enqueue(update_shifts)
	q.enqueue(update_scoreboard)

sched.start()
