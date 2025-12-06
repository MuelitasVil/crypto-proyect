from typing import Dict, Any, List, Tuple, Set
from fastapi import HTTPException
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.cell.cell import Cell
from sqlmodel import Session

from app.domain.dtos.school_headquarters_associate.school_headquarters_associate_input import (  # noqa: E501 ignora error flake8
    SchoolHeadquartersAssociateInput,
)
from app.domain.dtos.unit_school_associate.unit_school_associate_input import (
    UnitSchoolAssociateInput,
)

from app.domain.dtos.user_unit_associate.user_unit_associate_input import (
    UserUnitAssociateInput,
)

from app.service.crud.school_headquarters_associate_service import (
    SchoolHeadquartersAssociateService
)

from app.service.crud.unit_school_associate_service import (
    UnitSchoolAssociateService
)

from app.service.crud.user_unit_associate_service import (
    UserUnitAssociateService,
)

from app.utils.excel_processing import (
    get_value_from_row,
    is_blank,
    )

from app.domain.dtos.user_unal.user_unal_input import UserUnalInput
from app.domain.dtos.unit_unal.unit_unal_input import UnitUnalInput
from app.domain.dtos.school.school_input import SchoolInput
from app.domain.dtos.headquarters.headquarters_input import HeadquartersInput

from app.domain.enums.files.general import General_Values
from app.domain.enums.files.estudiante_activos import (
    EstudianteActivos,
    SedeEnum
)

from app.service.crud.user_unal_service import UserUnalService
from app.service.crud.unit_unal_service import UnitUnalService
from app.service.crud.school_service import SchoolService
from app.service.crud.headquarters_service import HeadquartersService

from app.utils.app_logger import AppLogger

logger = AppLogger(__file__)
logger2 = AppLogger(__file__, "user_unit_association.log")


# --------- validación principal y armado de colecciones ---------
def case_estudiantes_activos(
    ws: Worksheet,
    cod_period: str,
    session: Session
) -> Dict[str, Any]:
    """
    - Valida filas vacías y celdas vacías (según Enum).
    - Construye listas de DTOs (sin duplicados por código).
    - Devuelve resumen: status, errores, conteos y previews.
    """
    errors: List[Dict[str, Any]] = []
    users: List[UserUnalInput] = []
    units: List[UnitUnalInput] = []
    schools: List[SchoolInput] = []
    headquarters: List[HeadquartersInput] = []
    userUnitAssocs: List[UserUnitAssociateInput] = []
    unitSchoolAssocs: List[UnitSchoolAssociateInput] = []
    schoolHeadquartersAssocs: List[SchoolHeadquartersAssociateInput] = []

    seen_units: Set[str] = set()
    seen_schools: Set[str] = set()
    seen_heads: Set[str] = set()
    seen_users: Set[str] = set()
    seen_user_unit_assocs: Set[str] = set()
    seen_unit_school_assocs: Set[str] = set()
    seen_school_head_assocs: Set[str] = set()
    unit_with_school_log: Set[str] = set()

    sorted_rows = organize_rows_by_sede(ws, errors)

    if errors:
        raise HTTPException(status_code=400, detail={
            "status": False,
            "errors": errors[0:10]
        })

    logger.info("Iniciando procesamiento de archivo de estudiantes activos")

    for row_idx, row in sorted_rows:
        isSpecialHeadquarters: bool = False
        logger.debug(f"Procesando fila {row_idx}")
        logger.debug(f"Contenido de la fila: {[cell.value for cell in row]}")

        if row_idx == 1:
            continue

        if is_row_blank(row):
            errors.append({
                "row": row_idx,
                "column": None,
                "message": "Fila completamente vacía"
            })
            continue

        errors.extend(get_blank_cell_errors(row, row_idx))

        row_tuple: Tuple[Cell, ...] = row
        user: UserUnalInput = get_user_from_row(row_tuple)
        if user.email_unal and user.email_unal not in seen_users:
            users.append(user)
            seen_users.add(user.email_unal)
            logger.debug(f"Usuario agregado: {user}")
        else:
            logger.warning(f"Usuario duplicado encontrado: {user.email_unal}")

        unit: UnitUnalInput = get_unit_from_row(row_tuple)
        if unit.cod_unit and unit.cod_unit not in seen_units:
            units.append(unit)
            seen_units.add(unit.cod_unit)
            logger.debug(f"Plan agregada: {unit}")
        else:
            logger.warning(f"Plan duplicada encontrada: {unit.cod_unit}")

        school: SchoolInput
        school, isSpecialHeadquarters = get_school_from_row(row_tuple)
        if school.cod_school and school.cod_school not in seen_schools:
            schools.append(school)
            seen_schools.add(school.cod_school)
            logger.debug(f"Facultad agregada: {school}")
        else:
            logger.warning(
                f"Facultad duplicada encontrada: {school.cod_school}"
            )

        head: HeadquartersInput = get_headquarters_from_row(row_tuple)
        if head.cod_headquarters and head.cod_headquarters not in seen_heads:
            headquarters.append(head)
            seen_heads.add(head.cod_headquarters)
            logger.debug(
                f"Sede administrativa agregada: {head}"
            )
        else:
            logger.warning(
                f"Sede administrativa duplicada encontrada: "
                f"{head.cod_headquarters}"
            )

        userUnitAssoc: UserUnitAssociateInput = UserUnitAssociateInput(
            email_unal=user.email_unal,
            cod_unit=unit.cod_unit,
            cod_period=cod_period
        )
        if (
            f"{user.email_unal}{unit.cod_unit}{cod_period}"
            not in seen_user_unit_assocs
        ):
            seen_user_unit_assocs.add(
                f"{user.email_unal}{unit.cod_unit}{cod_period}"
            )
            userUnitAssocs.append(userUnitAssoc)
            logger.debug(
                f"Asociación de usuario a plan agregada: "
                f"{userUnitAssoc}"
            )
        else:
            logger.warning(
                f"Asociación de usuario a plan duplicada encontrada: "
                f"{user.email_unal}, {unit.cod_unit}, {cod_period}"
            )

        logger2.debug(f"Asociación de usuario a plan: {userUnitAssoc}")

        unitSchoolAssoc = UnitSchoolAssociateInput(
            cod_unit=unit.cod_unit,
            cod_school=school.cod_school,
            cod_period=cod_period
        )
        logger.debug(
            f"Es una sede de presencia nacional: {isSpecialHeadquarters}"
        )
        logger.debug(f"Plan: {unit.cod_unit}, Facultad: {school.cod_school}")
        logger.debug(f"unit with school: {unit_with_school_log}")
        if isSpecialHeadquarters and unit.cod_unit in unit_with_school_log:
            logger.debug(
                f"La plan {unit.cod_unit} pertenece a una facultad especial "
                f"de sede {school.cod_school}"
            )
        elif (
            f"{unit.cod_unit}{school.cod_school}{cod_period}"
            not in seen_unit_school_assocs
        ):
            seen_unit_school_assocs.add(
                f"{unit.cod_unit}{school.cod_school}{cod_period}"
            )
            unitSchoolAssocs.append(unitSchoolAssoc)
            unit_with_school_log.add(unit.cod_unit)

            logger.debug(
                f"Asociación de plan a facultad agregada: "
                f"{unitSchoolAssoc}"
            )
        else:
            logger.warning(
                "Asociación de plan a facultad duplicada encontrada: "
                f"{unitSchoolAssoc.cod_period} "
                f"{unitSchoolAssoc.cod_unit} "
                f"{unitSchoolAssoc.cod_school}"
            )

        schoolHeadAssoc = SchoolHeadquartersAssociateInput(
            cod_school=school.cod_school,
            cod_headquarters=head.cod_headquarters,
            cod_period=cod_period
        )
        if (
            f"{school.cod_school}{head.cod_headquarters}{cod_period}"
            not in seen_school_head_assocs
        ):
            seen_school_head_assocs.add(
                f"{school.cod_school}{head.cod_headquarters}{cod_period}"
            )
            schoolHeadquartersAssocs.append(schoolHeadAssoc)
            logger.debug(
                f"Asociación de facultad a sede agregada: "
                f"{schoolHeadAssoc}"
            )
        else:
            logger.warning(
                f"Asociación de facultad a sede duplicada encontrada: "
                f"{schoolHeadAssoc.cod_school}, "
                f"{schoolHeadAssoc.cod_headquarters}, "
                f"{schoolHeadAssoc.cod_period}"
            )

    if errors:
        raise HTTPException(status_code=400, detail={
            "status": False,
            "errors": errors[0:10]
        })

    try:
        logger.info("Validación completada sin errores.")
        logger.info("Resumiendo resultados e iniciando inserciones...")

        resUsers = UserUnalService.bulk_insert_ignore(users, session)
        resUnits = UnitUnalService.bulk_insert_ignore(units, session)
        resSchools = SchoolService.bulk_insert_ignore(schools, session)
        resHeadquarters = HeadquartersService.bulk_insert_ignore(
            headquarters,
            session
        )
        resUserUnitAssocs = UserUnitAssociateService.bulk_insert_ignore(
            userUnitAssocs,
            session
        )
        resUnitSchoolAssocs = UnitSchoolAssociateService.bulk_insert_ignore(
            unitSchoolAssocs,
            session
        )
        resSchoolHeadquartersAssocs = SchoolHeadquartersAssociateService.bulk_insert_ignore(  # noqa: E501 ignora error flake8
            schoolHeadquartersAssocs,
            session
        )
    except Exception as e:
        logger.error(f"Error durante el proceso de inserción: {str(e)}")
        logger.error(f"Detalles del error: {e}")

    logger.info("Inserciones completadas exitosamente.")

    logger.info(f"Resultados de inserción users: {resUsers}")
    logger.info(f"Resultados de inserción units: {resUnits}")
    logger.info(f"Resultados de inserción schools: {resSchools}")
    logger.info(f"Resultados de inserción headquarters: {resHeadquarters}")
    logger.info(
        f"Resultados de inserción user_unit_assocs: {resUserUnitAssocs}"
    )
    logger.info(
        f"Resultados de inserción unit_school_assocs: {resUnitSchoolAssocs}"
    )
    logger.info(
        f"Resultados de inserción school_headquarters_assocs: "
        f"{resSchoolHeadquartersAssocs}"
    )

    for userUserAssoc in userUnitAssocs:
        logger.info(f"Asociación de usuario a plan: {userUserAssoc}")

    return {
        "status": True,
        "cant_users": len(users),
        "cant_units": len(units),
        "cant_schools": len(schools),
        "cant_headquarters": len(headquarters),
        "cant_user_unit_assocs": len(userUnitAssocs),
        "cant_unit_school_assocs": len(unitSchoolAssocs),
        "cant_school_head_assocs": len(schoolHeadquartersAssocs),
    }


def get_user_from_row(row: Tuple[Cell, ...]) -> UserUnalInput:
    return UserUnalInput(
        email_unal=(
            get_value_from_row(row, EstudianteActivos.EMAIL.value) or None
        ),
        document=None,
        name=None,
        lastname=None,
        full_name=(
            get_value_from_row(
                row, EstudianteActivos.NOMBRES_APELLIDOS.value
            ) or None
        ),
        gender=None,
        birth_date=None,
        headquarters=get_value_from_row(
            row, EstudianteActivos.SEDE.value
        )
    )


def get_unit_from_row(row: Tuple[Cell, ...]) -> UnitUnalInput:
    sede: str = get_value_from_row(row, EstudianteActivos.SEDE.value)
    tipoEstudiante: str = get_value_from_row(
        row, EstudianteActivos.TIPO_NIVEL.value
    )

    if tipoEstudiante == General_Values.PREGRADO.value:
        tipoEstudiante = "pre"
    elif tipoEstudiante == General_Values.POSGRADO.value:
        tipoEstudiante = "pos"

    prefix_sede: str = sede.split(" ")[1][:3].lower()
    if sede == SedeEnum.SEDE_DE_LA_PAZ._name:
        prefix_sede = sede.split(" ")[3][:3].lower()

    cod_unit: str = get_value_from_row(row, EstudianteActivos.COD_PLAN.value)
    plan: str = get_value_from_row(row, EstudianteActivos.PLAN.value)
    tipo_nivel: str = get_value_from_row(
        row, EstudianteActivos.TIPO_NIVEL.value
    )
    cod_unit = f"{cod_unit}_{tipoEstudiante}_{prefix_sede}"
    email: str = f"{cod_unit}@unal.edu.co"
    return UnitUnalInput(
        cod_unit=cod_unit,
        email=email,
        name=plan or None,
        description=None,
        type_unit=tipo_nivel or None,
    )


def get_school_from_row(row: Tuple[Cell, ...]) -> Tuple[SchoolInput, bool]:
    isSpecialHeadquarters: bool = False
    facultad: str = get_value_from_row(row, EstudianteActivos.FACULTAD.value)
    sede: str = get_value_from_row(row, EstudianteActivos.SEDE.value)
    tipoEstudiante: str = get_value_from_row(
        row, EstudianteActivos.TIPO_NIVEL.value
    )
    prefix_sede: str = sede.split(" ")[1][:3].lower()

    logger.debug(f"Facultad: {facultad}, Sede: {sede}, Tipo: {tipoEstudiante}")

    if tipoEstudiante == General_Values.PREGRADO.value:
        logger.debug("Tipo de estudiante es pregrado")
        tipoEstudiante = "pre"
    elif tipoEstudiante == General_Values.POSGRADO.value:
        logger.debug("Tipo de estudiante es posgrado")
        tipoEstudiante = "pos"

    cod_school: str = ""

    if (
        sede == SedeEnum.SEDE_AMAZONIA._name or
        sede == SedeEnum.SEDE_CARIBE._name or
        sede == SedeEnum.SEDE_ORINOQUÍA._name or
        sede == SedeEnum.SEDE_TUMACO._name or
        sede == SedeEnum.SEDE_DE_LA_PAZ._name
    ):
        isSpecialHeadquarters = True
        cod_school = f"estf{tipoEstudiante}{prefix_sede}"
    else:
        acronimo = "".join(
            p[0].lower() for p in facultad.split() if len(p) > 2
        )
        cod_school = f"est{acronimo}{tipoEstudiante}_{prefix_sede}"

    email: str = f"{cod_school}@unal.edu.co"

    return SchoolInput(
        cod_school=cod_school,
        email=email,
        name=facultad or None,
        description=None,
        type_facultad=None,
    ), isSpecialHeadquarters


def get_headquarters_from_row(row: Tuple[Cell, ...]) -> HeadquartersInput:
    sede: str = get_value_from_row(row, EstudianteActivos.SEDE.value)
    tipoEstudiante: str = get_value_from_row(
        row, EstudianteActivos.TIPO_NIVEL.value
    )

    if tipoEstudiante == General_Values.PREGRADO.value:
        tipoEstudiante = "pre"
    elif tipoEstudiante == General_Values.POSGRADO.value:
        tipoEstudiante = "pos"

    prefix_sede: str = sede.split(" ")[1][:3].lower()
    if sede == SedeEnum.SEDE_DE_LA_PAZ._name:
        prefix_sede = sede.split(" ")[3][:3].lower()

    cod_sede: str = f"estudiante{tipoEstudiante}_{prefix_sede}"
    type_facultad: str = f"estudiante_{prefix_sede}"

    email: str = f"{cod_sede}@unal.edu.co"

    return HeadquartersInput(
        cod_headquarters=cod_sede,
        email=email,
        name=sede,
        description=None,
        type_facultad=type_facultad,
    )


def is_row_blank(row: Tuple[Cell, ...]) -> bool:
    """Retorna True si todas las columnas del Enum están vacías."""
    cells = [
        row[EstudianteActivos.NOMBRES_APELLIDOS.value - 1].value,
        row[EstudianteActivos.EMAIL.value - 1].value,
        row[EstudianteActivos.SEDE.value - 1].value,
        row[EstudianteActivos.FACULTAD.value - 1].value,
        row[EstudianteActivos.COD_PLAN.value - 1].value,
        row[EstudianteActivos.PLAN.value - 1].value,
        row[EstudianteActivos.TIPO_NIVEL.value - 1].value,
    ]
    return all(is_blank(v) for v in cells)


def get_blank_cell_errors(
    row: Tuple[Cell, ...], row_idx: int
) -> List[Dict[str, Any]]:
    """Retorna lista de errores por celdas vacías en la fila."""
    col_names = [
        "NOMBRES_APELLIDOS",
        "EMAIL",
        "SEDE",
        "FACULTAD",
        "COD_PLAN",
        "PLAN",
        "TIPO_NIVEL",
    ]
    cells = [
        row[EstudianteActivos.NOMBRES_APELLIDOS.value - 1].value,
        row[EstudianteActivos.EMAIL.value - 1].value,
        row[EstudianteActivos.SEDE.value - 1].value,
        row[EstudianteActivos.FACULTAD.value - 1].value,
        row[EstudianteActivos.COD_PLAN.value - 1].value,
        row[EstudianteActivos.PLAN.value - 1].value,
        row[EstudianteActivos.TIPO_NIVEL.value - 1].value,
    ]

    errors: List[Dict[str, Any]] = []
    for i, v in enumerate(cells):
        if is_blank(v):
            errors.append({
                "row": row_idx,
                "column": col_names[i],
                "message": "Celda vacía"
            })
    return errors


def organize_rows_by_sede(
    ws: Worksheet,
    errors: List[Dict[str, Any]]
) -> List[Tuple[int, Tuple[Cell, ...]]]:
    """
    Organiza las filas del archivo Excel según la sede,
    validando que la sede sea válida.

    {
    1: [
        (2, ('SEDE BOGOTÁ', 'ejemplo@bogota.com', 'Juan Pérez')),
        (4, ('SEDE BOGOTÁ', 'ejemplo2@bogota.com', 'Luis García'))
    ],
    2: [
        (3, ('SEDE MANIZALES', 'ejemplo@manizales.com', 'Ana Gómez'))
    ],
    3: [
        (5, ('SEDE MEDELLÍN', 'ejemplo@medellin.com', 'María López'))
    ]
    }

    :param ws: Worksheet del archivo de Excel.
    :param errors: Lista de errores donde se agregarán los errores encontrados.
    :return: Lista de filas organizadas por sede.
    """
    # Diccionario para organizar las filas según la sede
    sede_dict: Dict[int, List[Tuple[int, Tuple[Cell, ...]]]] = {
        order.number: [] for order in SedeEnum
    }

    logger.info(
        "Iniciando organizacion archivo de "
        "estudiantes activos"
    )

    # Recorrer todas las filas del archivo Excel (incluye encabezados en row 1)
    for row_idx, row in enumerate(ws.iter_rows(), start=1):

        if row_idx == 1:
            continue  # Skip header row

        # Verificar si la fila está vacía
        if is_blank(row):
            errors.append({
                "row": row_idx,
                "column": None,
                "message": "Fila completamente vacía"
            })
            continue

        # Validar celdas vacías en la fila
        errors.extend(get_blank_cell_errors(row, row_idx))

        # Obtener el valor de la sede de la fila
        sede_cell = get_value_from_row(row, EstudianteActivos.SEDE.value)
        sede_value = sede_cell.strip().upper()
        info_sede = SedeEnum.get_by_name(sede_value)

        # Comprobar si la sede es válida y mapearla al SedeOrder
        if info_sede:
            sede_order = info_sede.number
            # Almacenar fila en el diccionario
            sede_dict[sede_order].append((row_idx, row))
        else:
            errors.append({
                "row": row_idx,
                "column": EstudianteActivos.SEDE.value,
                "message": f"Sede no válida: {sede_value}"
            })
            continue

    # Ordenar las filas según el valor de SedeOrder (de menor a mayor)
    sorted_rows = []
    for order in sorted(sede_dict.keys()):
        sorted_rows.extend(sede_dict[order])

    logger.info("Finalizando organizacion de archivo de estudiantes activos")
    logger.debug(f"Errores encontrados: {errors}")

    return sorted_rows
