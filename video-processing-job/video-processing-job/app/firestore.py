from pydantic import BaseModel
from typing import Optional, Literal
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from exceptions import * 

# -------- Firestore init -------- #
cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred)
db = firestore.client()
# -------- Firestore init -------- #

# -------- Firestore document metadata -------- #
class Video(BaseModel):
  id: Optional[str] = None
  uid: Optional[str] = None
  filename: Optional[str] = None
  status: Optional[Literal["processing", "processed"]] = None
  title: Optional[str] = None
  description: Optional[str] = None
# -------- Firestore document metadata -------- #

# -------- Firestore things -------- #
def set_video(video_id: str, video: Video):
  """Either add new snapshot (object) to firestore, 
  or update data. 

  Args:
      videoId (str): id of the video
      video (Video): data of the video

  Returns:
      Callable: await-able function that uploads snapshot to firestore
  """
  # set() expects dict, and make sure it doesnt include none fields 
  try: 
    db.collection("videos").document(video_id).set(video.dict(exclude_none=True), merge=True)
  except Exception as e:
    raise FSGetError(f"Failed to set video. Reason: {e}")

def delete_video(video_id: str):
  """
  Checks if a document exists and deletes it if it does.
  """
  doc_ref = db.collection("videos").document(video_id)
  doc = doc_ref.get()
  if doc.exists:
    doc_ref.delete()

def get_video_status(video_id: str) -> str:
  doc_ref = db.collection("videos").document(video_id)
  doc = doc_ref.get()
  if not doc.exists:
    return "fresh"
  else: 
    return doc.to_dict()["status"] 
# -------- Firestore things -------- #
