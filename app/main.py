from fastapi import FastAPI
import logging
from app.api.chat_router import router as chat_router 
from fastapi.middleware.cors import CORSMiddleware 

logging.basicConfig(
    level=logging.INFO,
    format= "%(asctime)s [%(levelname)s] %(message)s",
) 

logger = logging.getLogger(__name__)

app = FastAPI(
    title= "Rag Chatbot",
    description="Chat bot hỗ trợ tìm kiếm sản phẩm",
    version= "1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(chat_router, prefix="/api")

@app.get("/")
def test():
    return{
        "status":"online",
        "message": "Chào mừng đến với chatbot "
    }

logger.info("Run server FastAPI")