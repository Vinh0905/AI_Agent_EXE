from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):
    query: str = Field(..., description="Câu hỏi của khách hàng")
    stored_items: Optional[str] = Field(default=None, description="Lọc theo loại kho lạnh như lạnh, mát, nhiệt độ phòng")
    max_price: Optional[float] = Field(default=None, description="Giá tối đa (VNĐ) để lọc khi cần")