from datetime import datetime
import re

from fastapi import HTTPException
from src.database import DatabaseConnection
from pymongo.collection import Collection
from bson import ObjectId

from src.helper.models.api_response import ApiResponse
from src.helper.models.pagination import Pagination

import json

from src.insurance_company.models.insurance_company import InsuranceCompany, InsuranceCompanyAdapter
from src.insurance_company.models.insurance_company_filter_query import InsuranceCompanyFilterQuery
from src.helper.models.pagination import Pagination, PaginationRequest

class InsuranceCompanyService:
    def __init__(self, db: DatabaseConnection):
        self.db_connection = db.get_collection('insurance_company')

    def get_adapter(self, insurance_company):
        if insurance_company is not None:
            insurance_company = InsuranceCompanyAdapter.validate_python(insurance_company)
        return insurance_company
    def get_collection(self, collection_name: str) -> Collection:
        return self.db_connection.get_collection(collection_name)

    def get_collection_filtered(self, collection_name: str, filter: InsuranceCompanyFilterQuery) -> Collection:
        try:
            filter_query = {}

            print(filter)

            if filter.name is not None:
                filter_query["name"] = {"$regex": re.compile("^.*" + filter.name + ".*$", re.IGNORECASE)}
            
            if filter.deleted is False:
                filter_query["delete_at"] = {"$ne": False}
            else:
                filter_query["delete_at"] = {"$eq": None}

            print(filter_query)

            documents = self.db_connection.get_collection(collection_name).find(filter_query).skip(((filter.page_number) - 1) * filter.docs_per_page).limit(filter.docs_per_page)
            response_document = []

            for result in documents:
                result['id'] = str(result['_id'])
                del result['_id']
                response_document.append(result)        

            document_count = self.db_connection.get_collection(collection_name).count_documents(filter_query)

            paginationFormat = Pagination()
            paginationFormat.setPagination(filter.page_number, filter.docs_per_page, document_count, response_document)

            response = ApiResponse()
            response.setResponse(True, "Data retrieved successfully.", "SUCCESS", paginationFormat)
            response.__setattr__('data', json.loads(paginationFormat.model_dump_json()))
            return response
        except Exception as e:
            response = ApiResponse(False, str(e), "ERROR", {})
            return response

    def create_form(self, form_data: InsuranceCompany) -> dict:
        result = self.db_connection.insert_one(form_data.dict())
        created_form = self.db_connection.find_one({"_id": result.inserted_id})
        created_form = InsuranceCompanyAdapter.validate_python(created_form)
        return created_form
    def get_insurance_company_by_search(self, pagination: PaginationRequest, filter: InsuranceCompanyFilterQuery) -> Collection:
            filter_query = {}
            matches = []

            if filter.search is not None:
                filter_query["$or"] = [
                        {"first_name": {"$regex": f".*{filter.search}.*", "$options": "i"}},
                        {"last_name": {"$regex": f".*{filter.search}.*", "$options": "i"}},
                        {"email": {"$regex": f".*{filter.search}.*", "$options": "i"}},
                        {"phone": {"$regex": f".*{filter.search}.*", "$options": "i"}}
                    ]

            else:    
                if filter.name is not None:
                    filter_query["name"] = {"$regex": filter.name, "$options": "i"}
                if filter.email is not None:
                    filter_query["email"] = {"$regex": filter.email, "$options": "i"}
                if filter.phone is not None:
                    filter_query["phone"] = {"$regex": filter.phone, "$options": "i"}

            documents = self.db_connection.find(filter_query).skip(
                ((pagination.page_number) - 1) * pagination.docs_per_page).limit(pagination.docs_per_page)
            
            document_count = self.db_connection.count_documents(filter_query)

            for document in documents:
                matches.append(self.get_adapter(document))

            paginationFormat = Pagination()
            paginationFormat.setPagination(
                pagination.page_number, pagination.docs_per_page, document_count, matches)
            return json.loads(
                paginationFormat.model_dump_json())
                
    def get_all_forms(self, collection: Collection) -> list:
        return list(collection.find())

    def get_insurance_company_by_id(self, insurance_company_id: str) -> Collection:
        quotes_documents = self.db_connection.find({"_id": insurance_company_id})
        response_documents = []
        for result in quotes_documents:
            response_documents.append(self.get_adapter(result))
        return response_documents
    
    def update_insurance_company_status(self, insurance_company_id: str, status: str) -> dict:
        result = self.db_connection.find_one_and_update(
            {"_id": ObjectId(insurance_company_id)},
            {"$set": {
                "status": status
            }},
            return_document=True  # Ensure the updated document is returned
        )
        if result:
            return {"_id": str(result["_id"]), "status": result["status"]}
        else:
            return {"error": "Insurance Company not found"}

    def update_form(self, collection: Collection, form_id: str, form_data: dict) -> dict:
        updated_form = collection.find_one_and_update(
            {"_id": ObjectId(form_id)}, {"$set": form_data}, return_document=True
        )
        if updated_form:
            return updated_form
        raise HTTPException(status_code=404, detail="Form not found")
    
    def delete_logic_form(self, collection: Collection, form_id: str, status: bool) -> dict:
        if status == True:
            delete_value = datetime.now()
        else:
            delete_value = False
        form = collection.find_one_and_update({"_id": ObjectId(form_id)}, {'$set': {'delete_at': delete_value}}, return_document=True)
        if form:
            form['id'] = str(form['_id'])
            del form['_id']

            response = ApiResponse()
            response.setResponse(True, "Data retrieved successfully.", "SUCCESS", form)
            response.__setattr__('data', form)
            return response
        raise HTTPException(status_code=404, detail="Form not found")

    def delete_form(self, collection: Collection, form_id: str) -> dict:
        deletion_result = collection.delete_one({"_id": ObjectId(form_id)})
        if deletion_result.deleted_count:
            return {"message": "Form deleted successfully"}
        raise HTTPException(status_code=404, detail="Form not found")
