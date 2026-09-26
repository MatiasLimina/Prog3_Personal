from fastapi import APIRouter, status

from .schemas import ProveedorCreate, ProveedorRead

router = APIRouter(prefix="/proveedores", tags=["Proveedores"])


@router.post(
    "/",
    response_model=ProveedorRead,
    status_code=status.HTTP_201_CREATED,
)
def crear_proveedor(proveedor: ProveedorCreate) -> ProveedorRead:
    """Ejemplo de endpoint tipado para crear un proveedor."""

    # En una aplicación real, el ID sería generado por la base de datos.
    return ProveedorRead(id=1, **proveedor.model_dump())
