from fastapi import APIRouter, UploadFile, HTTPException, File, Body
from app.services.ocr_service import PDFService
from app.services.structure_data_service import StructureDataService
from typing import Dict, Any, List

router = APIRouter()
pdf_service = PDFService()
structure_service = StructureDataService()

@router.post("/extract-tables")
async def extract_tables(files: List[UploadFile] = File(...)) -> Dict[str, Any]:
    """
    Estrae le tabelle da uno o più file (PDF o immagini).
    
    Args:
        files: Lista di file da processare (PDF o immagini)
        
    Returns:
        Dict contenente le tabelle estratte da tutti i file
        
    Raises:
        HTTPException: Se i file non sono nei formati supportati
    """
    allowed_extensions = ('.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp')
    for file in files:
        if not file.filename.lower().endswith(allowed_extensions):
            raise HTTPException(
                status_code=400, 
                detail=f"Tutti i file devono essere PDF o immagini ({', '.join(allowed_extensions)})"
            )
    return await pdf_service.extract_tables_data(files)

@router.post("/extract-medical-data", response_model=List[Dict[str, Any]])
async def extract_tables(files: List[UploadFile] = File(...)) -> List[Dict[str, Any]]:
    """
    Extract and structure data from medical files (PDF or images).
    
    Args:
        files: List of files to process (PDF or images)
        
    Returns:
        List of dictionaries containing structured medical data
        
    Raises:
        HTTPException: If files are not in supported formats
    """
    allowed_extensions = ('.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp')
    for file in files:
        if not file.filename.lower().endswith(allowed_extensions):
            raise HTTPException(
                status_code=400, 
                detail=f"All files must be PDF or images ({', '.join(allowed_extensions)})"
            )
    return await structure_service.process_medical_files(files)

@router.post("/structure-clinical-data")
async def structure_clinical_data(data: Dict[str, Any] = Body(...)) -> List[Dict[str, Any]]:
    """
    Struttura i dati clinici estratti dalle tabelle in un formato JSON standardizzato.
    
    Args:
        data: Dizionario contenente i dati delle tabelle estratte nel formato:
            {
                "tables": [
                    {
                        "page": int,
                        "headers": List[str],
                        "data": List[List[str]]
                    }
                ]
            }
        
    Returns:
        Lista di dizionari con i dati strutturati nel formato:
        [
            {
                "field name": str,
                "field value": str,
                "field unit of measure": str,
                "LOINC_value": str,
                "belonging_panel_LOINC_value": str,
                "reference_range_low": str,
                "reference_range_high": str
            }
        ]
        
    Raises:
        HTTPException: Se i dati di input non sono nel formato corretto
    """
    try:
        return await structure_service.clean_table_data_json(data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Errore durante la strutturazione dei dati: {str(e)}"
        )

