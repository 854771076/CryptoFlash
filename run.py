from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from main import main

if __name__ == '__main__':
    scheduler = BlockingScheduler(
        job_defaults={
            'max_instances': 10,
            'coalesce': True,
            'misfire_grace_time': 600,
        },
    )
    scheduler.add_job(main, 'interval', minutes=30,next_run_time=datetime.now())
    scheduler.start()