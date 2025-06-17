from pydantic import BaseModel, field_validator
import json, base64

class Data(BaseModel):
  id: str
  name: str 

class Message(BaseModel): 
  data: Data 

  @field_validator("data", mode="before")
  @classmethod
  def decode_data_and_validate(cls, data: str) -> str:
    if isinstance(data, str):
      try:
        decoded_bytes = base64.b64decode(data) # byte in string to byte
        decoded_str = decoded_bytes.decode("utf-8") # byte to dict in string 
        parsed_data = json.loads(decoded_str) # string in dict to dict 
        return parsed_data 
      except Exception as e:
        raise ValueError(f"Unable to decode base64 or parse JSON: {e}")
    else:
      return data 

class PubSubMessage(BaseModel):
  message: Message 
  subscription: str