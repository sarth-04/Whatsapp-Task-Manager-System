from apscheduler.schedulers.background import BackgroundScheduler

def remind_tasks():
    print("⏰ Reminder: Implement logic to send task reminders via WhatsApp.")

def init_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(remind_tasks, 'interval', minutes=60)
    scheduler.start()
