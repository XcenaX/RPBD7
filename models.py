from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder

from pydantic import BaseModel, Field
from typing import List, Optional, Union
from datetime import datetime

from objectid import PydanticObjectId


class Group(BaseModel):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    name: Optional[str]

    def to_json(self):
        return jsonable_encoder(self, exclude_none=True)

    def to_bson(self):
        data = self.dict(by_alias=True, exclude_none=True)
        try:
            data.pop("_id")
        except:
            pass
        return data
        

class Student(BaseModel):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    fullname: str
    age: int
    group: Optional[Group]

    def to_json(self):
        return jsonable_encoder(self, exclude_none=True)

    def to_bson(self):
        data = self.dict(by_alias=True, exclude_none=True)
        try:
            data.pop("_id")
        except:
            pass
        return data