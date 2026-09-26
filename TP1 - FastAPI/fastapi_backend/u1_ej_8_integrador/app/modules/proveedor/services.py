from typing import List, Optional

from fastapi import HTTPException, status

from .schemas import ProveedorCreate, ProveedorRead


db_proveedores: List[ProveedorRead] = []
id_counter = 1


def _validar_datos(data: ProveedorCreate) -> None:
    if not data.codigo:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El código del proveedor es obligatorio",
        )

    if len(data.razon_social) < 3:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La razón social debe tener al menos 3 caracteres",
        )


def _validar_codigo_unico(codigo: str, id_excluido: Optional[int] = None) -> None:
    if any(
        proveedor.codigo == codigo and proveedor.id != id_excluido
        for proveedor in db_proveedores
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un proveedor con ese código",
        )


def _obtener_existente(id: int) -> ProveedorRead:
    proveedor = next(
        (proveedor for proveedor in db_proveedores if proveedor.id == id),
        None,
    )
    if proveedor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proveedor no encontrado",
        )
    return proveedor


def crear(data: ProveedorCreate) -> ProveedorRead:
    global id_counter

    _validar_datos(data)
    _validar_codigo_unico(data.codigo)

    nuevo = ProveedorRead(id=id_counter, **data.model_dump())
    db_proveedores.append(nuevo)
    id_counter += 1
    return nuevo


def obtener_todos(
    skip: int,
    limit: int,
    activo: Optional[bool] = None,
) -> List[ProveedorRead]:
    proveedores = db_proveedores
    if activo is not None:
        proveedores = [proveedor for proveedor in proveedores if proveedor.activo == activo]

    return proveedores[skip : skip + limit]


def obtener_por_id(id: int) -> ProveedorRead:
    return _obtener_existente(id)


def actualizar_total(
    id: int,
    data: ProveedorCreate,
) -> ProveedorRead:
    _obtener_existente(id)
    _validar_datos(data)
    _validar_codigo_unico(data.codigo, id_excluido=id)

    for index, proveedor in enumerate(db_proveedores):
        if proveedor.id == id:
            actualizado = ProveedorRead(id=id, **data.model_dump())
            db_proveedores[index] = actualizado
            return actualizado

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Proveedor no encontrado",
    )


def desactivar(id: int) -> ProveedorRead:
    proveedor = _obtener_existente(id)
    if not proveedor.activo:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El proveedor ya está desactivado",
        )

    for index, proveedor in enumerate(db_proveedores):
        if proveedor.id == id:
            datos = proveedor.model_dump()
            datos["activo"] = False
            actualizado = ProveedorRead(**datos)
            db_proveedores[index] = actualizado
            return actualizado

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Proveedor no encontrado",
    )
