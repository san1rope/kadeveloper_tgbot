from typing import Optional, Union

from pydantic import BaseModel


class APIUser(BaseModel):
    telegram: Union[str, int]
    name: Optional[str] = None
    email: Optional[str] = None
    balance: int
