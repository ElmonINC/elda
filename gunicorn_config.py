import multiprocessing

# One worker per CPU core, but keep it at least 2 for low-core machines
workers = 2
threads = 2
timeout = 120 # Increase timeout to 120 seconds