from typing import Optional, Union

from pydantic import BaseModel


class APIUser(BaseModel):
    telegram: Union[str, int]
    name: Optional[str] = None
    email: Optional[str] = None
    balance: Optional[int] = None


class APIOrder(BaseModel):
    telegram: Union[str, int]
    link: str
    title: str
    category: Optional[str] = None
    location: Optional[str] = None
    spend: int
    limit: int
