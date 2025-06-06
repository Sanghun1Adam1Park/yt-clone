from pydantic import BaseModel
from typing import Optional, Literal, Callable

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore_async

# Use the application default credentials.
cred = credentials.ApplicationDefault()

firebase_admin.initialize_app(cred)
db = firestore_async.client()

class Video(BaseModel):
  id: Optional[str] = None
  uid: Optional[str] = None
  filename: Optional[str] = None
  status: Optional[Literal["processing", "processed"]] = None
  title: Optional[str] = None
  description: Optional[str] = None

async def get_video(video_id: str) -> Optional[Video]:
  """Gets video snapshot (object) from firestore. 

  Args:
      video_id (str): id of video snapshot
  """
  doc_ref = db.collection("videos").document(video_id)
  snapshot = await doc_ref.get()

  if snapshot.exists:
    data = snapshot.to_dict()
    return Video(**data)
  else:
    return None

def set_video(videoId: str, video: Video) -> Callable:
  """Either add new snapshot (object) to firestore, 
  or update data. 

  Args:
      videoId (str): id of the video
      video (Video): data of the video

  Returns:
      Callable: await-able function that uploads snapshot to firestore
  """
  # set() expects dict, and make sure it doesnt include none fields 
  return db.collection("videos").document(videoId).set(video.dict(exclude_none=True), merge=True)

async def is_new(video_id: str) -> bool:
  """Check if the video is new 

  Args:
      video_id (str): id of the video

  Returns:
      bool: bool - true if video is new else false
  """
  video = await get_video(video_id)
  return video is None or video.status is None