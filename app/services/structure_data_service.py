from typing import List, Dict, Any
import logging
# from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
import json
from app.core.config import settings
from fastapi import UploadFile
from app.services.ocr_service import PDFService
from fastapi import HTTPException

class MedicalFieldInfo(BaseModel):
    field_name: str = Field(description="Medical test name")
    field_value: str = Field(description="Test result value, converted to use dot as decimal separator")
    field_unit_of_measure: str = Field(description="Unit of measurement for the test value")
    reference_range_low: str = Field(description="Lower bound of the reference range")
    reference_range_high: str = Field(description="Upper bound of the reference range")

class MedicalDataResponse(BaseModel):
    medical_fields: List[MedicalFieldInfo] = Field(description="List of analyzed medical fields")

class StructureDataService:
    def __init__(self):
        # self.llm = HuggingFaceEndpoint(
        #     repo_id="deepseek-ai/DeepSeek-R1",
        #     task="text-generation",
        #     max_new_tokens=512,
        #     temperature=0.1,
        #     top_p=0.95,
        #     repetition_penalty=1.15,
        #     huggingfacehub_api_token=settings.HUGGING_FACE_HUB_TOKEN
        # )
        self.chat_llm = ChatOpenAI(
            model="gpt-4",
            temperature=0,
            api_key=settings.OPENAI_API_KEY
        )
        self.ocr_service = PDFService()

    async def process_medical_files(self, files: List[UploadFile]) -> List[Dict[str, str]]:
        """
        Process medical files through three steps:
        1. Extract tables from images/PDFs
        2. Clean and structure table data
        3. Transform data into final standardized format
        """
        try:
            logging.info("Starting medical files processing...")
            
            try:
                tables_data = await self.ocr_service.extract_tables_data(files)
                if not tables_data or not isinstance(tables_data, dict) or "tables" not in tables_data:
                    raise ValueError("Invalid or empty tables data received")
                logging.info(f"Tables extracted successfully")
            except Exception as e:
                logging.error(f"Error during table extraction: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Error during table extraction: {str(e)}"
                )
            
            try:
                structured_data = await self.clean_table_data_json(tables_data)
                if not structured_data:
                    raise ValueError("No data after cleaning and structuring")
                logging.info(f"Data structured successfully")
            except Exception as e:
                logging.error(f"Error during data structuring: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Error during data structuring: {str(e)}"
                )

            try:
                final_data = await self.transform_medical_data(structured_data)
                if not final_data:
                    raise ValueError("No data after final transformation")
                logging.info(f"Data transformed successfully")
                return final_data
            except Exception as e:
                logging.error(f"Error during final data transformation: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Error during final data transformation: {str(e)}"
                )
            
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"Unexpected error during file processing: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error during processing: {str(e)}"
            )

    async def transform_medical_data(self, data: List[Dict[str, str]]) -> List[Dict[str, str]]:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Healthcare specialist capable of extracting information from Italian "Referti di laboratorio".
                Answer solely on the "Referti di laboratorio" provided and do not give any information that does not appear on the "Referti di laboratorio".
                Answers should be formulated in the language of the "Referti di laboratorio" Be very thorough and complete in every answer.
                All information may not be present in the "Referti di laboratorio". If the answer is not in the provided "Referti di laboratorio" say "N/A".

                Do not provide any additional comment using "#" beyond the information to be extracted.
                Output decimal numbers using the dot notation.

                You are a specialized medical data analyst. Your task is to analyze medical test results and structure them in a standardized format.

                For each medical test entry, you need to:
                1. Extract the test name as it appears in the input
                2. Convert numerical values to use dots as decimal separators (e.g., "3,15" → "3.15")
                3. Keep the original unit of measurement
                4. Parse the reference range into separate low and high values

                Important rules:
                - Preserve original test names exactly as provided
                - Convert all decimal numbers from comma format to dot format
                - Extract numeric bounds from reference ranges (e.g., "3,1 - 20,5" → low: "3.1", high: "20.5")
                - Keep original units of measurement
                - Handle both integer and decimal values correctly

                Example Input:
                {{
                    "descrizioneEsame": "FOLATI",
                    "esiti": "3,15",
                    "unitaDiMisura": "ng/mL",
                    "valoriNormali": "3,1 - 20,5"
                }}

                Example Output:
                {{
                    "field_name": "FOLATI",
                    "field_value": "3.15",
                    "field_unit_of_measure": "ng/mL",
                    "reference_range_low": "3.1",
                    "reference_range_high": "20.5"
                }}"""),
            ("human", "Please analyze and structure these medical test results according to the specified format: {input_data}")
        ])

        chain = prompt | self.chat_llm.with_structured_output(MedicalDataResponse)
        
        result = await chain.ainvoke({
            "input_data": json.dumps(data, ensure_ascii=False)
        })
        
        return [field.model_dump() for field in result.medical_fields]

    async def clean_table_data_json(self, tables_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        result = []
        
        for table in tables_data.get("tables", []):
            headers = table.get("headers", [])
            data = table.get("data", [])
            
            formatted_headers = []
            for header in headers:
                words = header.lower().split()
                formatted_header = words[0]
                for word in words[1:]:
                    formatted_header += word.capitalize()
                formatted_headers.append(formatted_header)
            
            for row in data:
                row_dict = {}
                for header, value in zip(formatted_headers, row):
                    row_dict[header] = value
                result.append(row_dict)
        
        return result

    def _extract_json(self, text: str) -> str:
        """Estrae il JSON valido dalla risposta del modello."""
        import re
        
        text = text.replace('```json', '').replace('```', '').strip()
        
        json_pattern = r'\{[^{}]*\}'
        matches = re.finditer(json_pattern, text)
        
        for match in matches:
            try:
                json_str = match.group()
                json.loads(json_str)
                return json_str
            except:
                continue
        
        return None
