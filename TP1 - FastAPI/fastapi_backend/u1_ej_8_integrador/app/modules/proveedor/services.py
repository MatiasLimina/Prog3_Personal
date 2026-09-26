from typing import List, Optional

from .schemas import ProveedorCreate, ProveedorRead


db_proveedores: List[ProveedorRead] = []
id_counter = 1


def crear(data: ProveedorCreate) -> ProveedorRead:
    global id_counter

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


def obtener_por_id(id: int) -> Optional[ProveedorRead]:
    return next((proveedor for proveedor in db_proveedores if proveedor.id == id), None)


def actualizar_total(
    id: int,
    data: ProveedorCreate,
) -> Optional[ProveedorRead]:
    for index, proveedor in enumerate(db_proveedores):
        if proveedor.id == id:
            actualizado = ProveedorRead(id=id, **data.model_dump())
            db_proveedores[index] = actualizado
            return actualizado
    return None


def desactivar(id: int) -> Optional[ProveedorRead]:
    for index, proveedor in enumerate(db_proveedores):
        if proveedor.id == id:
            datos = proveedor.model_dump()
            datos["activo"] = False
            actualizado = ProveedorRead(**datos)
            db_proveedores[index] = actualizado
            return actualizado
    return None
