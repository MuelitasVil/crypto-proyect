from typing import Optional
from sqlmodel import Session
from fastapi import HTTPException
from sqlalchemy import text

from app.domain.models.user_unal import UserUnal
from app.domain.dtos.user_unal.user_info import UserInfoAssociation

from app.service.crud.user_unal_service import UserUnalService
from app.utils.app_logger import AppLogger

logger = AppLogger(__file__)


def get_info_user(
    email_unal: str,
    session: Session
) -> Optional[UserInfoAssociation]:
    """
    Llama al SP GetUserAcademicData y procesa los resultados en un DTO
    agrupado por periodos.
    """

    user: UserUnal = UserUnalService.get_by_email(email_unal, session)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )

    stmt = (
        text("CALL GetUserAcademicData(:email)")
        .bindparams(email=email_unal)
    )

    result = session.exec(stmt).mappings().all()
    user_info = UserInfoAssociation(
        email_unal=email_unal,
        document=user.document,
        name=user.name,
        lastname=user.lastname,
        full_name=user.full_name,
        gender=user.gender,
        headquarters=user.headquarters,
        period_associations={}
    )

    temp_dict = {}
    for row in result:
        period = row['cod_period']
        if period not in temp_dict:
            temp_dict[period] = {}

        headquarters_name = row['headquarters_name']
        if headquarters_name not in temp_dict[period]:
            cod_headquarters = row['cod_headquarters']
            temp_dict[period][headquarters_name] = {
                "code": cod_headquarters,
                "schools": {}
            }

        headquarter = temp_dict[period][headquarters_name]
        school_name = row['school_name']
        if school_name not in headquarter["schools"]:
            school_code = row['cod_school']
            headquarter["schools"][school_name] = {
                "code": school_code,
                "units": {}
            }

        school = headquarter["schools"][school_name]
        units_of_school = school["units"]
        unit_name = row['unit_name']
        if unit_name not in units_of_school:
            unit_code = row['cod_unit']
            units_of_school[unit_name] = {
                "code": unit_code
            }

    user_info.period_associations = temp_dict
    return user_info
