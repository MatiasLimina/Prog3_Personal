from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProveedorBase(BaseModel):
    """Campos compartidos por los esquemas de proveedores."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "codigo": "PROV-001",
                    "razon_social": "Distribuidora del Sur S.A.",
                    "cuit": "30712345678",
                    "email": "contacto@distribuidora-sur.com",
                    "telefono": "011-4567-8901",
                    "activo": True,
                }
            ]
        }
    )

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

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "email": "ventas@distribuidora-sur.com",
                    "telefono": "011-4567-8902",
                    "activo": True,
                }
            ]
        }
    )

    codigo: Optional[str] = Field(default=None, min_length=1)
    razon_social: Optional[str] = Field(default=None, min_length=3)
    cuit: Optional[str] = Field(default=None, min_length=11, max_length=15)
    email: Optional[str] = Field(default=None)
    telefono: Optional[str] = Field(default=None)
    activo: Optional[bool] = Field(default=None)
