from robocorp.tasks import task

@task
def minimal_task():
    message = "Hello"
    message = message + " World!"
    print(message)  # or return message if you want to use it elsewhere
