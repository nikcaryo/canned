"""runs stuff at time intervals such as sending texts and syncing/cleaning the spreadsheet"""
from utils import update_shifts
from apscheduler.schedulers.blocking import BlockingScheduler
from redis import Redis
from worker import conn
from rq import Queue


q = Queue(connection=conn)
schedule = BlockingScheduler()

@schedule.scheduled_job('interval', minutes=15)
def update_shifts():
    q.enqueue(update_shifts)

schedule.start()
