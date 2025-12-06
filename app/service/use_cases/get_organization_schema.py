from typing import List
from sqlmodel import Session

from app.domain.models.headquarters import Headquarters
from app.domain.models.school_headquarters_associate import (
    SchoolHeadquartersAssociate
)
from app.domain.models.unit_school_associate import (
    UnitSchoolAssociate
)

from app.service.crud.headquarters_service import HeadquartersService

from app.service.crud.unit_school_associate_service import (
    UnitSchoolAssociateService
)
from app.service.crud.school_headquarters_associate_service import (
    SchoolHeadquartersAssociateService
)

from app.utils.app_logger import AppLogger


logger = AppLogger(__file__, "get_organization_schema.log")


def get_organization_schema(session: Session, cod_period: str):
    # organization_schema structure:
    # dict[cod_headquarters, dict[cod_school, list[cod_unit]]]
    organization_schema: dict[str, dict[str, list[str]]] = {}

    headquarters: list[Headquarters] = (
        HeadquartersService.get_all(session)
    )

    headquarter: Headquarters
    for headquarter in headquarters:
        _insert_headquarters_in_organization_dict(
            headquarter.cod_headquarters,
            organization_schema
        )

        _fill_headquarters_schools(
            session,
            headquarter.cod_headquarters,
            organization_schema[headquarter.cod_headquarters],
            cod_period
        )

    return organization_schema


def _fill_headquarters_schools(
    session: Session,
    cod_headquarters: str,
    headquarters_schema: dict[str, list[str]],
    cod_period: str
):
    all_sch_hq_asso: List[SchoolHeadquartersAssociate] = []
    all_sch_hq_asso = SchoolHeadquartersAssociateService.get_by_headquarters(
        cod_headquarters, cod_period, session
    )

    sch_hq_asso: SchoolHeadquartersAssociate
    for sch_hq_asso in all_sch_hq_asso:
        _insert_school_in_organization_dict(
            cod_headquarters, sch_hq_asso.cod_school, headquarters_schema
        )

        _fill_school_units(
            session,
            sch_hq_asso.cod_school,
            headquarters_schema[sch_hq_asso.cod_school],
            cod_period
        )


def _fill_school_units(
    session: Session,
    cod_school: str,
    school_schema: list[str],
    cod_period: str
):
    units_sch_ass: list[UnitSchoolAssociate]
    units_sch_ass = UnitSchoolAssociateService.get_by_school(
        cod_school, cod_period, session
    )

    unit: UnitSchoolAssociate
    for unit in units_sch_ass:
        school_schema.append(unit.cod_unit)


def _insert_headquarters_in_organization_dict(
    cod_headquarters: str,
    organization_schema: dict[str, dict[str, list[str]]]
):
    if cod_headquarters not in organization_schema:
        organization_schema[cod_headquarters] = {}


def _insert_school_in_organization_dict(
    cod_headquarters: str,
    cod_school: str,
    headquarters_schema: dict[str, list[str]]
):
    if cod_school not in headquarters_schema:
        headquarters_schema[cod_school] = []
