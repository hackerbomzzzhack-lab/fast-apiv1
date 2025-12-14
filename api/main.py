from fastapi import FastAPI

# The FastAPI app instance must be named 'app' for Vercel's Python Runtime to find it
app = FastAPI()

@app.get("/")
def read_root():
    # You can return any JSON serializable content
    return {"message": "Hello from FastAPI on Vercel!"}

# For any CPU-bound tasks, use def instead of async def (FastAPI handles threading)
# OR use libraries designed for serverless environments (e.g., background queues)
@app.get("/cpu-task")
def run_cpu_task():
    # Simulate a CPU-bound operation that FastAPI will run in a thread
    import time
    time.sleep(0.5) 
    return {"result": "CPU task finished"}