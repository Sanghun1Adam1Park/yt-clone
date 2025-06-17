from pydantic import BaseModel
from typing import Optional, Literal, Callable
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore_async

# -------- Firestore init -------- #
cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred)
db = firestore_async.client()
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

