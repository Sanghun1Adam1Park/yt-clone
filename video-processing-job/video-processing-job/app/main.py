# Configure logging for Cloud Run. Logs will appear in Cloud Logging.
import sys, logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout) # Direct logs to stdout for Cloud Run to capture
    ]
)

from bucket import *
from firestore import *
from exceptions import *

if __name__ == "__main__":
  
  try:
    ensure_local_env()
  except DirCreationError as e:
    logging.error(e.get_e())
    sys.exit(1)

  try:
    video_id = sys.argv[1]
    status = get_video_status(video_id)
    if status != "fresh":
      logging.info("Video is already in process") 
      sys.exit(0)
    else: 
      set_video(video_id, Video(id=video_id, status="processing"))
      logging.info("Video process started.")
  except (FSGetError, FSSetError) as e:
    delete_video(video_id)
    delete_video_bucket(video_id)
    logging.error(e.get_e())
    sys.exit(1)
  
  try:
    download_video(video_id)
  except DownloadVidError as e:
    delete_video(video_id)
    delete_video_bucket(video_id)
    logging.error(e.get_e())
    sys.exit(1)
  
  try:
    process_video(video_id)
  except ProcessVidError as e:
    delete_video(video_id)
    delete_video_bucket(video_id)
    logging.error(e.get_e())
    sys.exit(1)
  
  try:
    upload_video(f"processed-{video_id}")
  except UploadVidError as e:
    delete_video(video_id)
    delete_video_bucket(video_id)
    logging.error(e.get_e())
    sys.exit(1)
  
  try:
    set_video(video_id, Video(id=video_id, status="processed"))
  except FSSetError as e:
    delete_video(video_id)
    delete_video_bucket(video_id)
    logging.error(e.get_e())
    sys.exit(1)
  
  try:
    clean_up(video_id)
    delete_video_bucket(video_id)
  except DeleteVidError as e:
    delete_video(video_id)
    logging.error(e.get_e())
    sys.exit(1)