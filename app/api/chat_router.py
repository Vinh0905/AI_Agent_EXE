from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import logging

# Import hàm sinh câu trả lời từ tầng Service mà ta vừa viết
from app.services.rag_service import analyze_query, generate_answer_stream
from app.schemas.chat import ChatRequest

logger = logging.getLogger(__name__)

# init router
router = APIRouter()

@router.post("/chat", summary="Chat với Trợ lý ảo E-commerce")
async def chat_with_bot(request: ChatRequest):
    """
    Endpoint nhận câu hỏi và trả về câu trả lời dạng Stream (SSE).
    Hỗ trợ lọc trước theo loại kho lạnh (stored_items) và giá tiền để tăng độ chính xác.
    """
    try:
        filters = analyze_query(request.query)
        stored_items = request.stored_items if request.stored_items is not None else filters.get("stored_items")
        max_price = request.max_price if request.max_price is not None else filters.get("max_price")

        answer_generator = generate_answer_stream(
            query=request.query,
            stored_items=stored_items,
            max_price=max_price
        )
        return StreamingResponse(
            answer_generator,
            media_type="text/event-stream"
        )
        
    except Exception as e:
        logger.exception("❌ Lỗi tại endpoint /chat")
        raise HTTPException(status_code=500, detail="Lỗi hệ thống nội bộ. Vui lòng thử lại sau.")