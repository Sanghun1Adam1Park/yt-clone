import os 
from .exceptions import * 
from google.cloud import storage 
import ffmpeg 

RAW_DIR = "./raw_vids"
PROCESSED_DIR = "./processed_vids"
RAW_BUCKET_NAME = "yt-clone-raw-06280527"
PROCESSED_BUCKET_NAME = "yt-clone-processed-06280527"

# ---------- Setting up local enivornment ---------- #
def __ensure_dir_eixist(dir_name: str):
  """Ensures directory with given name exists. 

  Args:
      dir_name (str): name of directory.

  Raises:
      DirCreationError: If failed to create directory.
  """
  try:
    os.makedirs(dir_name, exist_ok=True)
  except Exception as e:
    raise DirCreationError(f"Failed to create directory. Reason: {e}")

def ensure_local_env(): #IO-bound
  __ensure_dir_eixist(RAW_DIR)
  __ensure_dir_eixist(PROCESSED_DIR)
# ---------- Setting up local enivornment ---------- #

# ---------- Cloud things ---------- #
client = storage.Client() # bucket client object

def download_video(video_name: str): #IO-bound
  """Download blob (vidoe) from google storage bucket. 

  Args:
      filename (str): name of the blob (video)
  """
  try:
    bucket = client.bucket(RAW_BUCKET_NAME)
    blob = bucket.blob(video_name)
    blob.download_to_filename(os.path.join(RAW_DIR, video_name))
  except Exception as e:
    raise DownloadVidError(f"Failed to download video. Reason: {e}")

def upload_video(video_name: str): #IO-bound
  """Upload video to bucket as blob (file),
  and make the blob (file) visible to public.

  Args:
      filename (str): name of video to be uploaded
  """
  try: 
    bucket = client.bucket(PROCESSED_BUCKET_NAME)
    blob = bucket.blob(video_name)
    blob.upload_from_filename(os.path.join(PROCESSED_DIR, video_name))
    blob.make_public()
  except Exception as e:
    raise UploadVidError(f"Failed to upload video. Reason: {e}")
# ---------- Cloud things ---------- #

# ---------- Processing video ---------- #
def process_video(video_name: str): #CPU-bound 
  """Process video

  Args:
      video_name (str): name of unprocessed video to be processed.

  Raises:
      ProcessVidError: If failed to process the video.
  """
  try: 
    processed_name = "processed-" + video_name
    ffmpeg.input(os.path.join(RAW_DIR, video_name)).output(os.path.join(PROCESSED_DIR, processed_name), vf="scale=-2:360")
  except Exception as e:
    raise ProcessVidError(f"Failed to process video. Reason: {e}")
# ---------- Processing video ---------- #

# ---------- Cleaning up ---------- # 
def clean_up(video_name: str): #IO-bound
  """Clean up (delete no more neede video) from local enviornment. 

  Args:
      video_name (str): name of video to be deleted.

  Raises:
      DeleteVidError: if fail to delete video.
  """
  try: 
    processed_name = "processed-" + video_name
    os.remove(os.path.join(RAW_DIR, video_name))
    os.remove(os.path.join(PROCESSED_DIR, processed_name))
  except Exception as e:
    raise DeleteVidError(f"Failed to delete video. Reason: {e}")
# ---------- Cleaning up ---------- # 