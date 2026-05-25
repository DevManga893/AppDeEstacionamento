from abc import ABC
from pydantic import BaseModel

class Model(BaseModel, ABC):
    pass