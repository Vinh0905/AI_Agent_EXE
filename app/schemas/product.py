from pydantic import BaseModel, Field

class ProductUpdatePayload(BaseModel):
    product_id: str = Field(..., description="ID của kho lạnh")
    name: str
    price: float 
    stored_items: int 