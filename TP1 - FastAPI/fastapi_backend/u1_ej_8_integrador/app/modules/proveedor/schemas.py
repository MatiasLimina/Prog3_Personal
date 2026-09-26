from typing import Optional

from pydantic import BaseModel, Field


class ProveedorBase(BaseModel):
    """Campos compartidos por los esquemas de proveedores."""

    codigo: str = Field(..., min_length=1)
    razon_social: str = Field(..., min_length=3)
    cuit: str = Field(..., min_length=11, max_length=15)
    email: str = Field(default="")
    telefono: str = Field(default="")
    activo: bool = Field(default=True)


class ProveedorCreate(ProveedorBase):
    """Datos necesarios para crear un proveedor."""

    pass


class ProveedorRead(ProveedorBase):
    """Representación de un proveedor devuelta por el backend."""

    id: int


class ProveedorUpdate(BaseModel):
    """Campos opcionales para una actualización parcial."""

    codigo: Optional[str] = Field(default=None, min_length=1)
    razon_social: Optional[str] = Field(default=None, min_length=3)
    cuit: Optional[str] = Field(default=None, min_length=11, max_length=15)
    email: Optional[str] = Field(default=None)
    telefono: Optional[str] = Field(default=None)
    activo: Optional[bool] = Field(default=None)
