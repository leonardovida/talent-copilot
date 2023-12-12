# Use BackgroundTasks to run backgroun processes

## Context and Problem Statements

After uploading the PDFs we need to trigger all the downstream tasks (for now they are "just" API calls and calls to and from the database)

At the same time we want and need to keep the user not waiting for any result on the front end side. To do this we need some kind of background task utility.

## Considered Options

- FastAPI Background Tasks: FastAPI has a simple background task utility that can run functions in the background. It's a good starting point for simple background operations but may not be suitable for more complex or high-load scenarios.
- Celery with FastAPI: For more robust and scalable background task processing, you might want to use Celery with FastAPI. Celery is a distributed task queue system that can handle a large volume of tasks with reliability and flexibility.
- Message brokers like redis that are then used to send messages across different (distributed) systems.

## Decision Outcome

At the moment we go with the Background Tasks from FastAPI (based on Starlette). Keeping in mind that this decision, if the system will be ever expanded, will need to be revisided to something more scalable
