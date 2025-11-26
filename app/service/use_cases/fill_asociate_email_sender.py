from sqlmodel import Session

from app.domain.models.email_sender import EmailSender
from app.domain.models.email_sender_headquarters import EmailSenderHeadquarters
from app.domain.models.email_sender_school import EmailSenderSchool
from app.domain.models.email_sender_unit import EmailSenderUnit
from app.domain.models.headquarters import Headquarters
from app.domain.models.school import School
from app.domain.models.unit_unal import UnitUnal

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
from app.service.crud.unit_unal_service import UnitUnalService
from app.utils.app_logger import AppLogger

logger = AppLogger(__file__, "fill_associate_email_sender.log")


# TODO: Por el momento solo se rellena hasta facultades, porque no hay
# emails para unidades academicas en la base de datos.
def fill_associate_email_sender(session: Session):
    email_senders: list[EmailSender] = EmailSenderService.get_all(session)
    headquarters: list[Headquarters] = (
        HeadquartersService.get_all(session)
    )
    schools: list[School] = SchoolService.get_all(session)

    # Todo : this limit should be removed when we have more units
    units: list[UnitUnal] = UnitUnalService.get_all(session, limit=1000)

    logger.info("Email senders encontrados: ")
    for sender in email_senders:
        logger.info(f"Sender: {sender.email}, Org Type: {sender.org_type}")

    senders_global, senders_headquarters, senders_schools = (
        get_email_senders(email_senders)
    )

    logger.info("Senders globales encontrados:")
    for sender in senders_global:
        logger.info(f"Sender: {sender.email}")

    logger.info("Senders de sedes encontrados:")
    for sede, senders in senders_headquarters.items():
        for sender in senders:
            logger.info(f"Sede: {sede}, Sender: {sender.email}")

    logger.info("Senders de escuelas encontrados:")
    for sender in senders_schools:
        logger.info(f"Sender: {sender.email}")

    units_senders: list[EmailSenderUnit] = []
    school_senders: list[EmailSenderSchool] = []
    headquarters_senders: list[EmailSenderHeadquarters] = []

    temp_units_senders, temp_school_senders, temp_headquarters_senders = (
        fill_global_email_senders(
            senders_global,
            units,
            schools,
            headquarters
        )
    )

    units_senders.extend(temp_units_senders)
    school_senders.extend(temp_school_senders)
    headquarters_senders.extend(temp_headquarters_senders)

    temp_headquarters_senders = (
        fill_headquarters_email_senders(
            senders_headquarters,
            headquarters
        )
    )

    headquarters_senders.extend(temp_headquarters_senders)

    temp_school_senders = fill_school_email_senders(
        senders_schools,
        schools
    )

    school_senders.extend(temp_school_senders)

    responseEmailUnitbulk = EmailSenderUnitService.bulk_insert_ignore(
        units_senders, session
    )

    responseEmailSchoolBulk = EmailSenderSchoolService.bulk_insert_ignore(
        school_senders, session
    )

    for hqs in headquarters_senders:
        logger.info(
            f"Headquarters Sender to insert: {hqs.sender_id}, "
            f"Cod Headquarters: {hqs.cod_headquarters}"
        )

    responseEmailHeadquartersBulk = (
        EmailSenderHeadquartersService.bulk_insert_ignore(
            headquarters_senders, session
        )
    )

    logger.info(
        f"EmailSenderUnit bulk insert response: {responseEmailUnitbulk}"
    )

    logger.info(
        f"EmailSenderSchool bulk insert response: {responseEmailSchoolBulk}"
    )

    logger.info(
        f"EmailSenderHeadquarters bulk insert response: "
        f"{responseEmailHeadquartersBulk}"
    )

    return (responseEmailUnitbulk,
            responseEmailSchoolBulk,
            responseEmailHeadquartersBulk)


def get_email_senders(senders: list[EmailSender]):
    senders_global = []
    senders_headquarters = {}
    senders_schools = []
    for sender in senders:
        if sender.org_type == OrgType.GLOBAL.value:
            senders_global.append(sender)

        if sender.org_type == OrgType.HEADQUARTERS.value:
            if sender.sede_code not in senders_headquarters:
                senders_headquarters[sender.sede_code] = []

            list_sender_headquarters: list = senders_headquarters[
                sender.sede_code
            ]

            list_sender_headquarters.append(sender)

        if sender.org_type == OrgType.SCHOOL.value:
            senders_schools.append(sender)

    return senders_global, senders_headquarters, senders_schools


def fill_global_email_senders(
    senders_global: list[EmailSender],
    units: list[UnitUnal],
    schools: list[School],
    headquarters: list[Headquarters]
):
    logger.info("Llenando senders globales")
    unit_senders: list[EmailSenderUnit] = []
    school_senders: list[EmailSenderSchool] = []
    headquarters_senders: list[EmailSenderHeadquarters] = []
    for sender in senders_global:
        logger.info(f"Llenando sender global: {sender.email}")
        for hq in headquarters:
            logger.info(f"Asociando {sender.email} a {hq.name}")
            hq_sender = EmailSenderHeadquarters(
                sender_id=sender.email,
                cod_headquarters=hq.cod_headquarters,
                role=Role.OWNER.value,
            )
            headquarters_senders.append(hq_sender)

        for school in schools:
            school_sender = EmailSenderSchool(
                sender_id=sender.email,
                cod_school=school.cod_school,
                role=Role.OWNER.value,
            )
            school_senders.append(school_sender)

        for unit in units:
            unit_sender = EmailSenderUnit(
                sender_id=sender.email,
                cod_unit=unit.cod_unit,
            )
            unit_senders.append(unit_sender)

    return unit_senders, school_senders, headquarters_senders


def fill_headquarters_email_senders(
    senders_headquarters: dict,
    headquarters: list[Headquarters]
):
    headquarters_senders: list[EmailSenderHeadquarters] = []
    for hq in headquarters:
        if hq.name in senders_headquarters:
            list_senders = senders_headquarters[hq.name]
            for sender in list_senders:
                hq_sender = EmailSenderHeadquarters(
                    sender_id=sender.email,
                    cod_headquarters=hq.cod_headquarters,
                    role=Role.OWNER.value,
                )
                headquarters_senders.append(hq_sender)

    return headquarters_senders


def fill_school_email_senders(
    senders_schools: list,
    schools: list[School]
):
    logger.info("Llenando senders de escuelas")
    school_senders: list[EmailSenderSchool] = []
    for school in schools:
        # TODO: Mejorar esta logica de asociacion
        if not ("bog" in school.cod_school.lower()):
            continue

        for sender in senders_schools:
            if sender.org_code in school.name:
                school_sender = EmailSenderSchool(
                    sender_id=sender.email,
                    cod_school=school.cod_school,
                    role=Role.OWNER.value,
                )
                school_senders.append(school_sender)

    return school_senders
