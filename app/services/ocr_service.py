import base64
from typing import List, Dict, Any
from fastapi import UploadFile
from bs4 import BeautifulSoup
from pdf2image import convert_from_bytes
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
import os
import asyncio
from io import BytesIO
import json
import fitz
import logging
from app.core.config import settings
from fastapi import HTTPException

class PDFService:
    async def extract_tables_data(self, files: List[UploadFile]) -> Dict[str, Any]:
        try:
            data_urls = []
            
            for file in files:
                contents = await file.read()
                if file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp')):
                    img_buffer = BytesIO(contents)
                    data_urls.append(self._images_to_data_urls([img_buffer])[0])
                    logging.info(f"Immagine processata: {file.filename}")
                else:
                    image_buffers = self._pdf_to_images(contents)
                    data_urls.extend(self._images_to_data_urls(image_buffers))
                    logging.info(f"PDF processato: {file.filename}")
            
            logging.info(f"Totale immagini da processare: {len(data_urls)}")
            result = await self._parse_tables_from_images(data_urls)
            return result
        except Exception as e:
            logging.error(f"Errore durante l'estrazione delle tabelle: {str(e)}")
            raise

    def _pdf_to_images(self, file_content: bytes, dpi: int = 800) -> List[BytesIO]:
        try:
            images = convert_from_bytes(file_content, dpi=dpi)
            
            image_buffers = []
            for image in images:
                img_buffer = BytesIO()
                image.save(img_buffer, format='PNG', quality=100)
                img_buffer.seek(0)
                image_buffers.append(img_buffer)
            
            return image_buffers
        except Exception as e:
            logging.error(f"Error converting PDF to images: {e}")
            raise

    def _images_to_data_urls(self, image_buffers: List[BytesIO]) -> List[str]:
        return [
            f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode('utf-8')}"
            for buf in image_buffers
        ]

    def _process_llm_response(self, content: str) -> dict:
        try:
            logging.debug(f"Contenuto ricevuto dal modello: {content}")
            
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            
            try:
                return json.loads(content)
            except json.JSONDecodeError as e:
                logging.warning(f"Primo tentativo di parsing JSON fallito: {str(e)}")
            
            import re
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                try:
                    result = json.loads(json_match.group())
                    return self._normalize_tables_response(result)
                except json.JSONDecodeError as e:
                    logging.error(f"Errore nel parsing del JSON estratto: {str(e)}")
                    logging.error(f"JSON problematico: {json_match.group()}")
                    raise
            
            logging.warning("Nessun JSON valido trovato nella risposta")
            return {"tables": []}
            
        except Exception as e:
            logging.error(f"Errore nel processing della risposta: {str(e)}")
            raise

    def _normalize_tables_response(self, result: dict) -> dict:
        """Normalizza la risposta per assicurare una struttura consistente"""
        if not isinstance(result, dict):
            result = {"tables": []}
        elif "tables" not in result:
            result = {"tables": [result] if result else []}
        
        for table in result["tables"]:
            if "headers" not in table:
                table["headers"] = []
            if "data" not in table:
                table["data"] = []
            
            table["headers"] = [str(h).strip() for h in table["headers"] if h]
            table["data"] = [
                [str(cell).strip() for cell in row]
                for row in table["data"]
                if any(str(cell).strip() for cell in row)
            ]
        
        return result

    async def _parse_tables_from_images(self, data_urls: List[str]) -> Dict[str, Any]:
        try:
            messages = [
                {
                    "role": "system",
                    "content": """You are a medical laboratory report analysis expert. Your task is to:
                    1. Identify and extract ALL tables from the medical report
                    2. Preserve the exact structure and content of each table
                    3. Pay special attention to reference ranges and units of measurement
                    4. Ensure ALL cells are captured, even if they appear empty or unclear
                    5. Double-check all numeric ranges columns

                    Return the data in this format:
                    {
                        "tables": [
                            {
                                "page": page_number,
                                "headers": ["exact header 1", "exact header 2", ...],
                                "data": [
                                    ["row1 cell1", "row1 cell2", ...],
                                    ["row2 cell1", "row2 cell2", ...]
                                ]
                            }
                        ]
                    }

                    Important rules:
                    - Extract ALL text exactly as it appears
                    - Preserve ALL reference ranges, especially numeric ranges
                    - Include ALL units of measurement
                    - If a cell appears empty but might contain data, try to enhance and recheck
                    - Pay special attention to faint or low-contrast text
                    - Verify that numeric ranges are complete and accurate"""
                }
            ]

            user_content = [
                {
                    "type": "text",
                    "text": "Extract all tables from these medical laboratory report images. Pay special attention to reference ranges and ensure all cells are captured accurately."
                }
            ]

            for data_url in data_urls:
                user_content.append({"type": "image_url", "image_url": {"url": data_url}})

            messages.append({"role": "user", "content": user_content})

            llm = ChatOpenAI(
                model="gpt-4o",  
                api_key=settings.OPENAI_API_KEY,
                max_tokens=4096,
                temperature=0,
                timeout=120,
                request_timeout=120.0
            )
            
            try:
                response = await asyncio.wait_for(
                    llm.ainvoke(messages),
                    timeout=180.0
                )
                logging.info("Response received from model")
                return self._process_llm_response(response.content)
            except asyncio.TimeoutError:
                logging.error("Timeout during model call")
                raise HTTPException(
                    status_code=504,
                    detail="Request timeout while processing images"
                )
        
        except Exception as e:
            logging.error(f"Errore durante il parsing delle tabelle: {str(e)}")
            if hasattr(e, 'response'):
                logging.error(f"Dettagli errore API: {e.response}")
            raise 