#!/root/mon2/monitoring/venv/bin/python

from multiprocessing import cpu_count

bind = "127.0.0.1:8000"

# Worker Options
workers = cpu_count() * 2 + 1
worker_class = 'uvicorn.workers.UvicornWorker'

# Logging Options
loglevel = 'debug'
accesslog = '/root/mon2/monitoring/access_log'
errorlog = '/root/mon2/monitoring/error_log'




