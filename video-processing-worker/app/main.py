from fastapi import FastAPI, HTTPException
from google.cloud import pubsub_v1
from google.api_core import retry
import logging
# Import the actual video processing function
# Note: Ensure 'prcoess.py' is the correct filename, or adjust if it's 'process.py'
from .prcoess import process_video
from .storage import set_up_dirs

import sys
import asyncio

# This ensures logs are formatted nicely in Cloud Run
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)


app = FastAPI()
set_up_dirs()

def delay_awk_deadline(
    subscriber, path, ack_id, interval_seconds, event):
  """Extends awk deadline of given pub/sub messages every n seconds. 

  Args:
      subscriber (_type_): pub/sub client object
      path (_type_): path to pub/sub message
      ack_id (_type_): ack_id of pub/sub message
      interval_seconds (_type_): how often it checks the status
      event (_type_): event that keeps track of status
  """
  while not event.is_set():
    try:
      await asyncio.sleep(interval_seconds) 
      if event.is_set():
        break
      logging.info(f"Extending request with awk id {ack_id} for another {interval_seconds + 10} seconds")
      subscriber.modify_ack_deadline(
        request={"subscription": path, "ack_ids": [ack_id], "ack_deadline_seconds": interval_seconds + 10}
      )
    except Exception as e:
      logging.error(f"Error extending deadline: {e}")

# TODO: make sure the problem is solved, and fix retry 
@app.post("/process")
async def process_pubsub_message():
  logging.info("--- Endpoint /process invoked ---")
  try:
    project_id = "yt-clone-461110"
    subscription_id = "video-processing-worker-sub"  # Make sure this is the subscription name

    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, subscription_id)
    logging.info(f"Attempting to pull message from: {subscription_path}")

    # 1. PULL MESSAGE
    response = subscriber.pull(
      request={"subscription": subscription_path, "max_messages": 1},
      retry=retry.Retry(deadline=60) # Reduced deadline for quicker testing
    )

    # 2. CHECK IF A MESSAGE WAS RECEIVED
    if not response.received_messages:
      logging.warning("No messages found in subscription. Nothing to process.")
      return {"status": "no messages"}

    received_message = response.received_messages[0]
    ack_id = received_message.ack_id
    logging.info(f"Successfully pulled message with ack_id: {ack_id}")

    process_finished = asyncio.Event()
    process_checking_task = asyncio.create_task(
      delay_awk_deadline(subscriber, subscription_path, ack_id, 10, process_finished)
    )

    # Decode the message data for logging
    message_data = received_message.message.data.decode('utf-8')
    logging.info(f"Message data (decoded): {message_data}")

    # 3. CALL THE VIDEO PROCESSING FUNCTION
    logging.info("Calling the process_video function...")
    result: dict = await process_video(received_message.message) # Passing the original message object
    logging.info(f"process_video function returned: {result}")

    process_finished.set()
    await process_checking_task 

    # 4. CHECK THE RESULT AND ACKNOWLEDGE
    status_code = result.get("status_code", 500) # Default to 500 if no status_code
    if status_code == 200:
      logging.info("Processing was successful. Acknowledging message to Pub/Sub.")
      subscriber.acknowledge(
          request={"subscription": subscription_path, "ack_ids": [ack_id]}
      )
      logging.info(f"Message {ack_id} acknowledged.")
    else:
      # This path means your process_video function reported an error
      logging.error(f"process_video reported a failure (status {status_code}). Not acknowledging message.")
      logging.error(f"Failure details: {result.get('detail', 'No details provided')}")

    return result

  except Exception as e:
    # THIS IS CRITICAL: It will catch any unexpected error in your code
    logging.exception("An unexpected error occurred during message processing!")
    # We return an error response, which can be useful for monitoring
    raise HTTPException(status_code=500, detail="Internal Server Error")
    