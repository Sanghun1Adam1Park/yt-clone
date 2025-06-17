# 2. trigger post request
from .storage import (
    convert_vid,
    download_raw_vid,
    upload_vid,
    delete_raw_vid,
    delete_processed_vid
)
from .firestore import (
    is_new,
    set_video,
    delete_video, 
    Video
)

import time
import asyncio
import logging
import subprocess
import base64
import json

async def process_video(message) -> dict:
    # 1. Isolate message parsing. If this fails, we can't do anything.
    try:
        data: bytes = message.data
        if data is None:
            raise ValueError("Missing 'data' field in Pub/Sub message")

        decoded_json = data.decode("utf-8")
        payload = json.loads(decoded_json)
        raw_vid = payload.get("name")
        if not raw_vid:
            raise ValueError(f"Missing 'name' in payload: {decoded_json}")
        
        vid_id: str = raw_vid.split('.')[0]

    except (ValueError, json.JSONDecodeError, UnicodeDecodeError) as e:
        logging.error(f"Invalid message payload: {e}")
        return {"status_code": 400, "detail": "Invalid message payload received."}

    # 2. Check for idempotency and set the initial "processing" state.
    try:
        is_new_vid: bool = await is_new(vid_id)
        if is_new_vid:
            await set_video(vid_id, 
                Video(id=vid_id, uid=vid_id.split('-')[0], status="processing")) 
        else: 
            logging.warning(f"Video {vid_id} is already processing or processed. Acknowledging message.")
            # Return success to prevent Pub/Sub from retrying a job that's already done/in-progress.
            return {"status_code": 200, "detail": "Video already processed."}
    except Exception as e:
        logging.error(f"Firestore pre-check failed for {vid_id}: {e}")
        # We can't proceed and can't clean up because the record may not exist.
        return {"status_code": 500, "detail": "Failed to check or set initial video state."}

    # 3. Main processing block with robust success/failure handling
    try:
        # Download video from raw bucket
        await download_raw_vid(raw_vid)
        logging.info(f"{raw_vid} has been successfully downloaded")

        # Process the video
        process: subprocess.Popen = convert_vid(raw_vid)
        loop = asyncio.get_running_loop()
        _, stderr = await loop.run_in_executor(None, process.communicate)
        if process.returncode != 0:
            # Raise a specific error to be caught below
            raise RuntimeError(f"FFmpeg failed with exit code {process.returncode}: {stderr.decode('utf-8')}")
        logging.info(f"{raw_vid} has been successfully converted.")

        # Upload video to processed bucket
        processed_name: str = await upload_vid(raw_vid)
        logging.info(f"{processed_name} has been successfully uploaded")

    except Exception as e:
        # SINGLE FAILURE POINT: Catches *any* error from the try block above.
        logging.error(f"Processing failed for {vid_id}: {e}")
        logging.info(f"Cleaning up Firestore record for failed video {vid_id}...")
        await delete_video(vid_id)  # <-- Use await!
        return {"status_code": 500, "detail": "Video processing failed."}
    
    else:
        # SUCCESS PATH: This runs only if the try block had NO errors.
        logging.info(f"Processing for {vid_id} successful. Finalizing...")
        await set_video(vid_id, Video(status="processed", filename=processed_name))

        # Delete local videos since they are no longer needed
        try:
            delete_raw_vid(raw_vid)
            delete_processed_vid(raw_vid)
        except OSError as e:
            # This is not a critical failure, but should be logged.
            logging.warning(f"Failed to delete local files for {vid_id}: {e}")

        return {"status_code": 200, "content": {"status": "ok", "message": f"{raw_vid} processed successfully."}}