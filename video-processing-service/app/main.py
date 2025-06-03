from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from .storage import (
    set_up_dirs,
    convert_vid,
    download_raw_vid,
    upload_vid,
    delete_raw_vid,
    delete_processed_vid
)

import time
import asyncio
import logging
import subprocess
import base64
import json

set_up_dirs() 
app = FastAPI()

@app.post("/process-video")
async def process_video(req: Request):
    try:
        body = await req.json()

        start = time.time()
        message = body.get("message", {})
        encoded_data = message.get("data")
        if encoded_data is None:
            raise ValueError("Missing 'data' field in Pub/Sub message")

        try:
            decoded_json = base64.b64decode(encoded_data).decode("utf-8")
            payload = json.loads(decoded_json)
            raw_vid = payload.get("name")
            if not raw_vid:
                raise ValueError(f"Missing 'name' in payload: {decoded_json}")
        except Exception as e:
            raise ValueError(f"Unable to decode base64 or parse JSON: {e}")    

        await download_raw_vid(raw_vid)
                
        process: subprocess.Popen = convert_vid(raw_vid)
        loop = asyncio.get_running_loop()
        convert_start = time.time()
        _, stderr = await loop.run_in_executor(None, process.communicate)
        elapsed = time.time() - convert_start
        logging.info(f"{raw_vid} has been successfully converted, took {elapsed:.2f} seconds.")
        if process.returncode != 0:
            logging.error(f"FFmpeg stderr: {stderr.decode('utf-8')}")
            raise RuntimeError(f"FFmpeg failed: {stderr.decode()}")

        await upload_vid(raw_vid)

        loop = asyncio.get_running_loop()
        results = await asyncio.gather(
            loop.run_in_executor(None, delete_raw_vid, raw_vid),
            loop.run_in_executor(None, delete_processed_vid, raw_vid),
            return_exceptions=True  
        )
        raw_result, processed_result = results
        if isinstance(raw_result, Exception):
            logging.error(f"Raw video deletion failed: {raw_result}")
        if isinstance(processed_result, Exception):
            logging.error(f"Processed video deletion failed: {processed_result}")

        return JSONResponse(
            status_code=200,
            content={"status": "ok", "message": f"{raw_vid} processed successfully."}
        )
    except ValueError as e:
        logging.error(f"Vale error: {e}")
        raise HTTPException(status_code=400, detail="Invalid message payload received.")
    except RuntimeError as e:
        logging.error(f"Conversion error: {e}")
        raise HTTPException(status_code=500, detail="Convertion failed.")
    except Exception as e:
        logging.exception(f"Unexpected error: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": "An unexpected error occurred."}
        )