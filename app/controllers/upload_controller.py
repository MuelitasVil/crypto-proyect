from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlmodel import Session
from openpyxl import Workbook

from app.configuration.database import get_session
from app.utils.type_file_validation import readExcelFile

from app.service.excel_processor.process_file import process_file
from app.service.crud.period_service import PeriodService
from app.utils.auth import get_current_user

router = APIRouter(prefix="/upload_excel", tags=["Excel Upload"])


@router.post("/", status_code=status.HTTP_200_OK)
async def upload_excel_file(
    cod_period: str,
    file: UploadFile = File(...),
    user_email: str = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    period = PeriodService.get_by_id(cod_period, session)
    if not period:
        raise HTTPException(status_code=400, detail={
            "error": f"El periodo con código {cod_period} no existe",
            "message": "Verifique el código del periodo"
        })
    wb: Workbook = await readExcelFile(file)
    # Save the data in the excel in database
    return process_file(wb, cod_period, session)
