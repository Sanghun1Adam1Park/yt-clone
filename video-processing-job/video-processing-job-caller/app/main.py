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

app = FastAPI()

@app.post("/")
async def root(pubsub_message: PubSubMessage):
    try:
        data: Data = pubsub_message.message.data 
        print(data.name)
        if data is None:
            raise ValueError("Did not recieve any data.")
    except Exception:
        logging.error("Something went wrong!")