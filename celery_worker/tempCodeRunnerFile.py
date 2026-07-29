from celery_worker.celery_app import celery_app

@celery_app.task
def send_email(email: str,username: str,password: str):
    print(email)
    print(username)
    print(password)