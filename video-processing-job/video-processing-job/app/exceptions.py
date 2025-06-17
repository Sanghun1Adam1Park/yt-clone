class MyException(Exception):
  def __init__(self, e: str) -> None:
    self.e = e

  def get_e(self):
    return self.e

class DirCreationError(MyException):
  def __init__(self, e: str) -> None:
    super().__init__(e)

class DownloadVidError(MyException):
  def __init__(self, e: str) -> None:
    super().__init__(e)
  
class UploadVidError(MyException):
  def __init__(self, e: str) -> None:
    super().__init__(e)

class ProcessVidError(MyException):
  def __init__(self, e: str) -> None:
    super().__init__(e)
  
class DeleteVidError(MyException):
  def __init__(self, e: str) -> None:
    super().__init__(e)