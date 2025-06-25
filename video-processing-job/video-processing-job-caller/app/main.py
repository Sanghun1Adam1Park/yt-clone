# This ensures logs are formatted nicely in Cloud Run
import sys, logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

from fastapi import FastAPI
from .data import PubSubMessage, Data
from google.cloud import run_v2 

app = FastAPI()

@app.post("/")
async def root(pubsub_message: PubSubMessage):
  try:
    data: Data = pubsub_message.message.data
    if data is None or not hasattr(data, 'name'):
      raise ValueError("Invalid Pub/Sub message data: 'video_id' is missing or data is None.")
    
    video_id = data.name # Assuming 'Data' Pydantic model has a 'video_id' field0
    logging.info(f"Received request for video_id: {video_id}")

  except Exception as e:
    logging.error(f"Error processing Pub/Sub message: {e}")
    return {"status": "error", "message": f"Error processing Pub/Sub message: {e}"}, 400

  try:
    client = run_v2.JobsClient()

    job_resource_name = f"projects/yt-clone-461110/locations/europe-west3/jobs/job"

    container_overrides_list = [
      run_v2.RunJobRequest.Overrides.ContainerOverride(
        args=["app/main.py", video_id] # Pass the video_id as a command-line argument
      )
    ]
    
    job_overrides = run_v2.RunJobRequest.Overrides(
      container_overrides=container_overrides_list
    )

    request = run_v2.RunJobRequest(
      name=job_resource_name,
      overrides=job_overrides # Apply the overrides to the job request
    )
    
    operation = client.run_job(request=request)
    logging.info(f"Cloud Run job operation started: {operation.operation.name} for video_id: {video_id}")

    return {"status": "success", "message": f"Cloud Run job triggered for video_id: {video_id}"}


  except Exception as e:
    logging.error(f"Failed to trigger Cloud Run job for video_id {video_id}: {e}")
    return {"status": "error", "message": f"Failed to trigger Cloud Run job: {e}"}, 500