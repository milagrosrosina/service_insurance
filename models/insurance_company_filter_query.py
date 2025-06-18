from typing import Optional
from pydantic import BaseModel


class InsuranceCompanyFilterQuery(BaseModel):
    name: Optional[str] = None
    page_number: int = 0
    docs_per_page: int = 10
    deleted: bool = False
    search : Optional[str] = None
    email : Optional[str] = None
    phone : Optional[str] = None
    deleted: bool = False