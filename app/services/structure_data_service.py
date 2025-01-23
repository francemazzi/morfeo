from typing import List, Dict, Any
import logging
from langchain_huggingface import HuggingFaceEndpoint
from langchain.prompts import PromptTemplate
import json
from app.core.config import settings

class StructureDataService:
    def __init__(self):
        self.llm = HuggingFaceEndpoint(
            repo_id="deepseek-ai/DeepSeek-R1",
            task="text-generation",
            max_new_tokens=512,
            temperature=0.1,
            top_p=0.95,
            repetition_penalty=1.15,
            huggingfacehub_api_token=settings.HUGGING_FACE_HUB_TOKEN
        )

    async def clinical_report(self, tables_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Struttura i dati del referto clinico in un formato JSON standardizzato.
        
        Args:
            tables_data: Dizionario contenente i dati delle tabelle estratte
            
        Returns:
            Lista di dizionari con i dati strutturati secondo il formato richiesto
        """
        try:
            structured_data = []
            
            for table in tables_data.get("tables", []):
                headers = table.get("headers", [])
                data = table.get("data", [])
                
                for row in data:
                    if not any(row):  # Salta righe vuote
                        continue
                        
                    row_data = dict(zip(headers, row))
                    
                    prompt = f"""<s>[INST] You are a medical data structuring expert. Analyze this laboratory test data and extract information in a structured format.

                                Input data:
                                {json.dumps(row_data, indent=2, ensure_ascii=False)}

                                Task: Create a structured representation of this laboratory test result.
                                You need to identify and extract:
                                1. The name of the medical test/examination
                                2. The numerical or qualitative result value
                                3. The unit of measurement (if present)
                                4. The reference ranges (if present)

                                Example Input:
                                {{
                                    "Descrizione esame": "FOLATI",
                                    "Esiti": "3,15",
                                    "Unità di misura": "ng/mL",
                                    "Valori Normali": "3,1 - 20,5"
                                }}

                                Example Output:
                                {{
                                    "testName": "FOLATI",
                                    "resultValue": "3,15",
                                    "unitOfMeasure": "ng/mL",
                                    "loincValue": "",
                                    "belongingPanelLoincValue": "",
                                    "referenceRangeLow": "3,1",
                                    "referenceRangeHigh": "20,5"
                                }}

                                Return a valid JSON object with this exact structure:
                                {{
                                    "testName": "The name of the test/examination",
                                    "resultValue": "The result value",
                                    "unitOfMeasure": "The unit of measurement (empty string if not present)",
                                    "loincValue": "",
                                    "belongingPanelLoincValue": "",
                                    "referenceRangeLow": "The lower bound of the reference range (empty string if not applicable)",
                                    "referenceRangeHigh": "The upper bound of the reference range (empty string if not applicable)"
                                }}

                                Rules for reference ranges:
                                - For ranges like "X - Y", extract X as low and Y as high
                                - For ranges like "< X", leave low empty and use X as high
                                - For ranges like "> X", use X as low and leave high empty
                                - For ranges like "X", use X as both low and high
                                - If no range is found, leave both empty
                                - Keep the decimal separator as found in the input (comma or dot)
                                - Keep the exact format of numbers as in the input (do not convert commas to dots or vice versa)

                                Return ONLY the JSON object, no other text or explanation.[/INST]</s>"""
                    
                    try:
                        response = await self.llm.agenerate([prompt])
                        response_text = response.generations[0][0].text.strip()
                            
                    except Exception as e:
                        logging.error(f"Errore nell'elaborazione della riga: {row_data}")
                        logging.error(f"Errore: {str(e)}")
                        continue
            
            return response_text
            
        except Exception as e:
            logging.error(f"Errore nella strutturazione dei dati: {str(e)}")
            raise

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
