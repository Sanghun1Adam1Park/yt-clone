from google.cloud import storage
from google.api_core.exceptions import NotFound, Forbidden, GoogleAPIError
from typing import Final
from dotenv import load_dotenv
import os 
import ffmpeg
import subprocess
import asyncio
import logging 
import time 
import threading

load_dotenv()
client: Final = storage.Client()

RAW_BUCKET_NAME: Final = os.getenv("RAW_BUCKET_NAME")
PROCESSED_BUCKET_NAME: Final = os.getenv("PROCESSED_BUCKET_NAME")

RAW_LOCAL_NAME: Final = os.getenv("RAW_LOCAL_NAME")
PROCESSED_LOCAL_NAME: Final = os.getenv("PROCESSED_LOCAL_NAME")

def _ensure_dir_exists(dir_path: str):
    """Ensures that given dir exists at given path

    Param:
        - dir_path: (relative) directory path. 
    """
    os.makedirs(dir_path, exist_ok=True)

def set_up_dirs():
    """Creates the local directories for raw and processed videos.
    """
    _ensure_dir_exists(RAW_LOCAL_NAME)
    _ensure_dir_exists(PROCESSED_LOCAL_NAME)

def _file_extension_converter(input_filename: str) -> str:
    """Makes sure that output file is consistent wiht .mp4 extension. 

    Args:
        input_filename - input filename
    Returns:
        filename with .mp4 extension
    """
    base, _ = os.path.splitext(input_filename)
    return "processed-" + base + ".mp4"

def convert_vid(raw_vid_name: str) -> subprocess.Popen:
    """Converst the video on child process. 

    Args:
        raw_vid_name (str): file name for raw video (to be converted)

    Returns:
        subprocess.Popen: sub(child) process that will run ffmpeg converting process 
    """
    processed_name: str = _file_extension_converter(raw_vid_name)

    process = (
        ffmpeg
        .input(os.path.join(RAW_LOCAL_NAME, raw_vid_name))
        .output(os.path.join(PROCESSED_LOCAL_NAME, processed_name), 
                vf="scale=-2:360")
        .run_async(pipe_stdout=True, pipe_stderr=True)
    )

    return process

def _download_blob(filename: str):
    """Download blob (file) from google storage bucket. 

    Args:
        filename (str): name of the blob (file)
    """
    bucket = client.bucket(RAW_BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.download_to_filename(os.path.join(RAW_LOCAL_NAME, filename))

async def download_raw_vid(filename: str):
    """Downloads blob (file, raw video) from the gcloud bucket.
    It starts a thread that downloads which runs in background. 

    Args:
        filename (str): name of the blob (file)
    """
    start = time.time()
    await asyncio.get_running_loop().run_in_executor(
        None, _download_blob, filename
    )
    elapsed = time.time() - start
    logging.info(f"Downloaded {filename} from {RAW_BUCKET_NAME} to {RAW_LOCAL_NAME} in {elapsed:.2f} seconds.")

def _upload_blob(filename:str):
    """Upload video to bucket as blob (file),
    and make the blob (file) visible to public.

    Args:
        filename (str): name of video to be uploaded
    """
    bucket = client.bucket(PROCESSED_BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_filename(os.path.join(PROCESSED_LOCAL_NAME, filename))
    blob.make_public()

async def upload_vid(filename: str):    
    """Uploads processed video to the gcloud bucket.
    It starts a thread that downloads which runs in background. 

    Args:
        filename (str): name of the processed video
    """
    start = time.time()
    processed_name: str = _file_extension_converter(filename)

    await asyncio.get_running_loop().run_in_executor(
        None, _upload_blob, processed_name
    )
    elapsed = time.time() - start
    logging.info(f"Uploaded {processed_name} to {PROCESSED_BUCKET_NAME} from {PROCESSED_LOCAL_NAME} in {elapsed:.2f} seconds.")

def _delete_file(filename: str):
    """Deletes file at given path.

    Args:
        filename (str): path + filename 
    """
    os.remove(filename)
    logging.info(f"Deleted: {filename}")


def _delete_file_thread(filename: str) -> threading.Thread:
    """Returns a (back ground running) thread that deletes file.

    Args:
        filename (str): path + filename of file to be deleted.

    Returns:
        threading.Thread: thread that will run "delete file"
    """
    return threading.Thread(target=_delete_file, args=(filename,))

def delete_raw_vid(filename: str) -> threading.Thread:
    return _delete_file_thread(os.path.join(RAW_LOCAL_NAME, filename))

def delete_processed_vid(filename: str) -> threading.Thread:
    processed_name: str = _file_extension_converter(filename)
    return _delete_file_thread(os.path.join(PROCESSED_LOCAL_NAME, processed_name))


