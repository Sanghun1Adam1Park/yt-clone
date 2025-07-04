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

# TODO: make delete object in fireabase in case it failed to upload
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

def set_video(video_id: str, video: Video) -> Callable:
  """Either add new snapshot (object) to firestore, 
  or update data. 

  Args:
      videoId (str): id of the video
      video (Video): data of the video

  Returns:
      Callable: await-able function that uploads snapshot to firestore
  """
  # set() expects dict, and make sure it doesnt include none fields 
  return db.collection("videos").document(video_id).set(video.dict(exclude_none=True), merge=True)

async def is_new(video_id: str) -> bool:
  """Check if the video is new 

  Args:
      video_id (str): id of the video

  Returns:
      bool: bool - true if video is new else false
  """
  video = await get_video(video_id)
  return video is None or video.status is None

def delete_video(video_id: str):
    """
    Checks if a document exists and deletes it if it does.
    """
    try:
        # 1. Create the reference
        doc_ref = db.collection("videos").document(video_id)

        # 2. Get the document snapshot
        doc = await doc_ref.get()

        # 3. Check the .exists property
        if doc.exist:
          # 4. Delete the doc.
          await doc.delete()


    except Exception as e:
        print(f"An error occurred: {e}")
  