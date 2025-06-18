# routes.py in Insurance_Company folder
from fastapi import APIRouter, Query
from typing import List, Optional
from src.insurance_company.models.insurance_company import InsuranceCompany, InsuranceCompanyRequest
from src.insurance_company.models.insurance_company_filter_query import InsuranceCompanyFilterQuery
from src.insurance_company.service import InsuranceCompanyService
from src.helper.models.api_response import ApiResponse
from src.database import DatabaseConnection
from src.account.models.account import Status
from fastapi import APIRouter, Query, Depends, HTTPException
from src.auth.deps import insurance_company
from src.helper.models.pagination import PaginationRequest
from bson import ObjectId

router = APIRouter(prefix="/insurance_company", tags=['Insurance_Company'])

instance = DatabaseConnection()
insurance_company_service = InsuranceCompanyService(instance)

# Create a new Insurance_Company
@router.post("", response_model=ApiResponse)
async def create_insurance_company(form_data: InsuranceCompanyRequest):
    try:
        form_data.status = Status.PENDING.value
        created_form = insurance_company_service.create_form(form_data)
        response = ApiResponse()
        response.setResponse(True, "Data saved successfully.", "SUCCESS", created_form)
        return response
    except Exception as e:
        response = ApiResponse(False, str(e), "ERROR", {})
        return response

# Filter for list of Insurance_Company
@router.get('/finder', response_model=ApiResponse, description="Filter for list of Insurance_Company", dependencies=[Depends(insurance_company)])
async def insurance_company_finder(search: Optional[str] = None,
                          page_number: int = Query(
                              1, description="The page number to retrieve."),
                          docs_per_page: int = Query(
                              10, description="The number of documents per page."),
                          name: Optional[str] = None, last_name: Optional[str] = None,
                          email: Optional[str] = None, phone: Optional[str] = None):
    try:
        filter = []
        pagination = PaginationRequest(
        page_number=page_number,
        docs_per_page=docs_per_page
        )
        filter = InsuranceCompanyFilterQuery(search=search, name=name, last_name=last_name, email=email, phone=phone)
        return insurance_company_service.get_insurance_company_by_search(pagination, filter)
    except Exception as e:
        response = ApiResponse(False, str(e), "ERROR", {})
        return response

@router.get('/{id}', response_model=ApiResponse, description="Get Insurance_Company by ID", dependencies=[Depends(insurance_company)])
async def get_insurance_company_by_id(insurance_company_id: str):
    try:
        data_insurance_company_service = insurance_company_service.get_insurance_company_by_id(ObjectId(insurance_company_id))
        response = ApiResponse()
        response.setResponse(True, "Data retrieved successfully.", "SUCCESS", data_insurance_company_service)
        response.__setattr__('data', data_insurance_company_service)
        return response
    except Exception as e:
        response = ApiResponse(False, str(e), "ERROR", {})
        return response

@router.put('/insurance_company/{insurance_company_id}/status', response_model=ApiResponse, description="Update Insurance_Company by ID", dependencies=[Depends(insurance_company)])
async def update_insurance_company_status(insurance_company_id: str, status: str):
    try:
        data_insurance_company_service = insurance_company_service.update_insurance_company_status(ObjectId(insurance_company_id), status)
        response = ApiResponse()
        response.setResponse(True, "Data updated successfully.", "SUCCESS", data_insurance_company_service)
        response.__setattr__('data', data_insurance_company_service)
        return response
    except Exception as e:
        response = ApiResponse(False, str(e), "ERROR", {})
        return response
