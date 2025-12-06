from sqlmodel import Session

from app.domain.models.email_sender import EmailSender
from app.domain.models.email_sender_headquarters import EmailSenderHeadquarters
from app.domain.models.email_sender_school import EmailSenderSchool
from app.domain.models.email_sender_unit import EmailSenderUnit
from app.domain.models.headquarters import Headquarters
from app.domain.models.school import School

from app.domain.enums.email_sender.email_sender import OrgType, Role

from app.service.crud.email_sender_service import EmailSenderService
from app.service.crud.email_sender_unit_service import EmailSenderUnitService
from app.service.crud.email_sender_school_service import (
    EmailSenderSchoolService
)
from app.service.crud.email_sender_headquarters_service import (
    EmailSenderHeadquartersService
)
from app.service.crud.headquarters_service import HeadquartersService
from app.service.crud.school_service import SchoolService
from app.service.use_cases.get_organization_schema import (
    get_organization_schema
)
from app.utils.app_logger import AppLogger

logger = AppLogger(__file__, "fill_associate_email_sender.log")


# TODO: Por el momento solo se rellena hasta facultades, porque no hay
# emails para unidades academicas en la base de datos.
def fill_associate_email_sender(session: Session, cod_period: str):
    senders_global: list[EmailSender]
    senders_headquarters: dict[str, dict[str, list[EmailSender]]]
    organization_schema: dict[str, dict[str, list[str]]] = {}

    senders_global, senders_headquarters = (
        _get_email_senders(session)
    )
    _log_email_senders(senders_global, senders_headquarters)

    organization_schema = get_organization_schema(session, cod_period)
    _log_organization(organization_schema)

    emailSenderHeadquarters, emailSenderSchool, emailSenderUnit = (
        _associated_email_senders(
            senders_global,
            senders_headquarters,
            organization_schema,
            session
        )
    )

    response_email_headquarters = (
        EmailSenderHeadquartersService.bulk_insert_ignore(
            emailSenderHeadquarters,
            session
        )
    )

    response_email_school = (
        EmailSenderSchoolService.bulk_insert_ignore(
            emailSenderSchool,
            session
        )
    )

    response_email_unit = (
        EmailSenderUnitService.bulk_insert_ignore(
            emailSenderUnit,
            session
        )
    )

    return {
        "response_email_headquarters": response_email_headquarters,
        "response_email_school": response_email_school,
        "response_email_unit": response_email_unit
    }


def _associated_email_senders(
    senders_global: list[EmailSender],
    senders_headquarters: dict[str, dict[str, list[EmailSender]]],
    organization_schema: dict[str, dict[str, list[str]]] = {},
    session: Session = None
):
    emailSenderHeadquarters: list[EmailSenderHeadquarters] = []
    emailSenderSchool: list[EmailSenderSchool] = []
    emailSenderUnit: list[EmailSenderUnit] = []

    for sede, schools in organization_schema.items():
        sede_info: Headquarters = HeadquartersService.get_by_id(sede, session)
        if not sede_info:
            continue

        sede_name = sede_info.name
        email_senders_sede: list[EmailSender] = (
            _get_email_senders_by_sede(
                sede_name,
                senders_headquarters
            )
        )

        temp_email_senders_headquarters: list[EmailSenderHeadquarters] = (
            _get_email_sender_headquarters(
                sede_info.cod_headquarters,
                email_senders_sede,
                senders_global
            )
        )
        emailSenderHeadquarters.extend(temp_email_senders_headquarters)

        for school, units in schools.items():
            school_info: School = SchoolService.get_by_id(school, session)
            if not school_info:
                continue

            school_name = school_info.name
            email_senders_school: list[EmailSender] = (
                _get_email_senders_by_school(
                    sede_name,
                    school_name,
                    senders_headquarters
                )
            )

            temp_email_senders_schools: list[EmailSenderSchool] = []
            temp_email_senders_schools = (
                _get_email_sender_school(
                    school_info.cod_school,
                    email_senders_sede,
                    senders_global,
                    email_senders_school
                )
            )
            emailSenderSchool.extend(temp_email_senders_schools)

            # todo: dont exist email senders for units in db
            temp_unit_senders_school: list[EmailSenderUnit] = []
            temp_unit_senders_school = (
                _get_email_sender_units(
                    units,
                    email_senders_sede,
                    senders_global,
                    email_senders_school
                )
            )
            emailSenderUnit.extend(temp_unit_senders_school)

    return (
        emailSenderHeadquarters,
        emailSenderSchool,
        emailSenderUnit
    )


def _get_email_sender_headquarters(
        cod_headquarters: str,
        senders_headquarters: list[EmailSender],
        senders_global: list[EmailSender]
) -> list[EmailSenderHeadquarters]:
    email_senders_headquarters: list[EmailSenderHeadquarters] = []
    sender: EmailSender
    hq_sender: EmailSenderHeadquarters

    all_headquarters_senders: list[EmailSender] = (
        senders_headquarters + senders_global
    )

    for sender in all_headquarters_senders:
        hq_sender = EmailSenderHeadquarters(
            sender_id=sender.email,
            cod_headquarters=cod_headquarters,
            role=Role.OWNER.value
        )
        email_senders_headquarters.append(hq_sender)

    return email_senders_headquarters


def _get_email_sender_school(
        cod_school: str,
        senders_headquarters: list[EmailSender],
        senders_global: list[EmailSender],
        senders_school: list[EmailSender]
) -> list[EmailSenderSchool]:
    email_senders_schools: list[EmailSenderSchool] = []
    sender: EmailSender
    sc_sender: EmailSenderSchool

    all_school_senders: list[EmailSender] = (
        senders_headquarters + senders_school + senders_global)

    for sender in all_school_senders:
        sc_sender = EmailSenderSchool(
            sender_id=sender.email,
            cod_school=cod_school,
            role=Role.OWNER.value
        )
        email_senders_schools.append(sc_sender)

    return email_senders_schools


def _get_email_sender_units(
        units: list[str],
        senders_headquarters: list[EmailSender],
        senders_global: list[EmailSender],
        sendol_school: str
) -> list[EmailSenderUnit]:
    email_senders_units: list[EmailSenderUnit] = []
    sender: EmailSender
    sc_sender: EmailSenderUnit

    all_school_units: list[EmailSender] = (
        senders_headquarters + sendol_school + senders_global)

    for cod_unit in units:
        for sender in all_school_units:
            sc_sender = EmailSenderUnit(
                sender_id=sender.email,
                cod_school=cod_unit,
                role=Role.OWNER.value
            )
            email_senders_units.append(sc_sender)

    return email_senders_units


def _get_email_senders_by_school(
        sede_name: str,
        school_name: str,
        senders_headquarters: dict[str, dict[str, list[EmailSender]]]
) -> list[EmailSender]:
    if sede_name in senders_headquarters:
        sede = senders_headquarters[sede_name]
        if OrgType.SCHOOL.value in sede:
            schools = sede[OrgType.SCHOOL.value]
            if school_name in schools:
                return schools[school_name]

    return []


def _get_email_senders_by_sede(
        sede_name: str,
        senders_headquarters: dict[str, dict[str, list[EmailSender]]]
) -> list[EmailSender]:

    if sede_name in senders_headquarters:
        return senders_headquarters[sede_name][OrgType.HEADQUARTERS.value]

    return []


def _get_email_senders(
        session: Session
) -> list[EmailSender]:

    email_senders: list[EmailSender] = EmailSenderService.get_all(session)
    senders_global: list[EmailSender] = []

    # sede : {org_type: [EmailSender, ...], ...} sede
    # sede : {org_type: {org_code: [EmailSender, ...], ...}, ...} school
    senders_headquarters: dict[str, dict[str, list[EmailSender]]] = {}

    return _get_organized_email_senders(
        email_senders,
        senders_global,
        senders_headquarters
    )


def _get_organized_email_senders(
        senders: list[EmailSender],
        senders_global: list[EmailSender],
        senders_headquarters: dict[str, dict[str, list[EmailSender]]]
        ):
    senders_global = []
    senders_headquarters = {}

    for sender in senders:
        _obtain_global_email_sender(
            sender,
            senders_global
        )

        _obtain_headquarters_email_sender(
            sender,
            senders_headquarters
        )

    return senders_global, senders_headquarters


def _obtain_global_email_sender(
        sender: EmailSender,
        senders_global: list[EmailSender]
        ):

    if sender.org_type == OrgType.GLOBAL.value:
        senders_global.append(sender)


def _obtain_headquarters_email_sender(
        sender: EmailSender,
        senders_headquarters: dict[str, dict[str, list[EmailSender]]]
        ):

    origin_type = sender.org_type
    if origin_type == OrgType.HEADQUARTERS.value:

        sede_name = sender.sede_code
        if sede_name not in senders_headquarters:
            senders_headquarters[sede_name] = {}

        sede = senders_headquarters[sede_name]

        if origin_type not in sede:
            sede[origin_type] = []

        sede[origin_type].append(sender)

    if origin_type == OrgType.SCHOOL.value:
        sede_name = sender.sede_code
        if sede_name not in senders_headquarters:
            senders_headquarters[sede_name] = {}

        sede = senders_headquarters[sede_name]

        if origin_type not in sede:
            sede[origin_type] = {}

        facultades = sede[origin_type]
        school_code = sender.org_code
        if school_code not in facultades:
            facultades[school_code] = []

        facultad = facultades[school_code]
        facultad.append(sender)


def _log_organization(organization_schema: dict[str, dict[str, list[str]]]):
    for sede, schools in organization_schema.items():
        logger.info(f"Sede: {sede}")
        for school, units in schools.items():
            logger.info(f"  school: {school}")
            for org_code in units:
                logger.info(f"    unit Code: {org_code}")


def _log_email_senders(
        senders_global: list[EmailSender],
        senders_headquarters: dict[str, dict[str, list[EmailSender]]]
        ):
    logger.info("Global Email Senders:")
    for sender in senders_global:
        logger.info(f"  {sender}")

    logger.info("Headquarters Email Senders:")
    for sede, org_types in senders_headquarters.items():
        logger.info(f"Sede: {sede}")

        for org_type, senders in org_types.items():
            logger.info(f"Org Type: {org_type}")
            if org_type == OrgType.SCHOOL.value:
                for org_code, school_senders in senders.items():
                    logger.info(f"  Org Code: {org_code}")
                    for sender in school_senders:
                        logger.info(f"    {sender}")

            if org_type == OrgType.HEADQUARTERS.value:
                for sender in senders:
                    logger.info(f"  Sender: {sender}")
