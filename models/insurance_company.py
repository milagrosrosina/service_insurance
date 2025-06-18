from typing import List, Optional
from pydantic import BaseModel
from src.models import PyObjectId
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime, date
from pydantic import TypeAdapter

class Status(Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    PENDING = "Pending"
    SUSPENDED = "Suspended"
    DELETED = "Deleted"

class InsuranceCompany(BaseModel):
    __table_name__ = 'insurance_company'

    id: PyObjectId = Field(validation_alias="_id")
    insurer_custom_name: str
    name: str
    email: str
    phones: str
    fax: str
    direction: str
    status: Optional[Status] = Status.PENDING
    business_line: List[str]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": "5f0a0a5f1c4ae6f149404935",
                    "insurer_custom_name": "132",
                    "name": "John",
                    "email": "Doe",
                    "phones": "2341213123",
                    "fax": "2341213123",
                    "direction": "2341213123",
                    "status": "Active",
                    "business_line": ["2341213123"],
                    "created_at": "2020-07-10T00:00:00",
                    "updated_at": "2020-07-10T00:00:00"
                }
            ]
        }
    }

InsuranceCompanyAdapter = TypeAdapter(InsuranceCompany)

class InsuranceCompanyRequest(BaseModel):
    insurer_custom_name: str
    name: str
    email: str
    phones: str
    fax: str
    direction: str
    status: Optional[Status] = Status.PENDING
    business_line: List[str]
    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "examples": [
                {
                    "insurer_custom_name": "132",
                    "name": "John",
                    "email": "Doe",
                    "phones": "2341213123",
                    "fax": "2341213123",
                    "direction": "2341213123",
                    "status": "Active",
                    "business_line": ["2341213123"]
                }
            ]
        }
    }

class InsuranceCompanyFilterQuery(BaseModel):
    insurer_custom_name: str
    name: str
    email: str
    phones: str
    fax: str
    direction: str
    status: Optional[Status] = Status.PENDING
    business_line: List[str] = []