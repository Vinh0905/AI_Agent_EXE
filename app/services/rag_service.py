from asyncio.log import logger
import json
import os
from openai import OpenAI
import openai
from qdrant_client import QdrantClient
from qdrant_client import models
from app.pipeline.load import setup_qdrant, embed_and_load_chunk
from app.pipeline.transform import transform_json_to_chunk

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = "cold_storage"
DATA_DIR = os.getenv("DATA_DIR", "/app/data")
DATA_FILE = os.path.join(DATA_DIR, "products_data_chunks.jsonl")
RAW_DATA_FILE = os.path.join(DATA_DIR, "products_data_raws.jsonl")
ai_client = OpenAI(api_key=OPENAI_API_KEY)
qdrant = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
)


def get_qdrant_point_count() -> int:
    try:
        count_result = qdrant.count(collection_name=COLLECTION_NAME)
        return getattr(count_result, "count", 0)
    except Exception as e:
        logger.error(f"Không thể đếm điểm Qdrant: {e}")
        return 0


def ensure_chunk_data_ready() -> bool:
    if os.path.exists(DATA_FILE):
        logger.info(f"Tìm thấy file chunk dữ liệu: {DATA_FILE}")
        return True

    if os.path.exists(RAW_DATA_FILE):
        logger.info(f"Không tìm thấy file chunk, chuyển đổi raw sang chunk: {RAW_DATA_FILE} -> {DATA_FILE}")
        try:
            transform_json_to_chunk(RAW_DATA_FILE, DATA_FILE)
            return os.path.exists(DATA_FILE)
        except Exception as e:
            logger.error(f"Không thể chuyển đổi raw sang chunk: {e}")
            return False

    logger.warning(f"Không tìm thấy cả file chunk và raw: {DATA_FILE}, {RAW_DATA_FILE}")
    return False


def ensure_qdrant_ready() -> None:
    try:
        if not QDRANT_URL:
            logger.error("Biến môi trường QDRANT_URL chưa được thiết lập.")
            return

        setup_qdrant()

        if not ensure_chunk_data_ready():
            logger.warning("Dữ liệu chunk Qdrant không sẵn sàng, bỏ qua quá trình nạp dữ liệu.")
            return

        current_count = get_qdrant_point_count()
        logger.info(f"Qdrant collection '{COLLECTION_NAME}' hiện có {current_count} điểm.")
        if current_count == 0:
            logger.info(f"Qdrant trống, nạp data từ {DATA_FILE}...")
            embed_and_load_chunk(DATA_FILE)
    except Exception as e:
        logger.error(f"Lỗi khi khởi tạo Qdrant: {e}")

def analyze_query(query: str, stored_items: str = None, max_price: float = None, top_k = 4):
    analyzer_prompt = """Bạn là chuyên gia trích xuất dữ liệu. Hãy đọc câu hỏi và trả về ĐÚNG 1 ĐỊNH DẠNG JSON.
        1. "stored_items": "lạnh", "mát", "nhiệt độ phòng"(bình thường)  hoặc null nếu không rõ.
        2. "max_price": CHÚ Ý - Phải dịch các từ chỉ tiền tệ sang số nguyên VNĐ.
        - Ví dụ: "10 triệu", "10 củ" -> 10000000
        - Ví dụ: "500k", "500 cành" -> 500000
        - Ví dụ: "dưới 2 triệu" -> 2000000
        - Nếu câu hỏi KHÔNG nhắc đến giới hạn giá tối đa -> null

        Trả về duy nhất JSON, không thêm bất kỳ text nào khác.
        """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": analyzer_prompt},
                {"role": "user", "content": query}
            ],
            response_format={"type": "json_object"},
            temperature=0,
            max_tokens=100
        )

        extracted_data = response.choices[0].message.content
        # Ensure we return a dict. The LLM may return a JSON string.
        if isinstance(extracted_data, str):
            try:
                parsed = json.loads(extracted_data)
                return parsed
            except Exception:
                logger.warning("analyze_query: failed to parse JSON from LLM response")
                return {"stored_items": None, "max_price": None}
        elif isinstance(extracted_data, dict):
            return extracted_data
        else:
            return {"stored_items": None, "max_price": None}
    except Exception as e:
        logger.error(f"Error analyzing query: {e}")
        return {"stored_items": None, "max_price": None}

def retrieve_context(query: str, stored_items: str = None, max_price: float = None, top_k= 4):
    """
    Tìm kiếm vector trong Qdrant kết hợp với bộ lọc Metadata (stored_items và Giá).
    """
    try:
        # 1. Nhúng câu hỏi của người dùng thành Vector
        embed_res = ai_client.embeddings.create(
            input=query, 
            model="text-embedding-3-small"
        )
        query_vector = embed_res.data[0].embedding

        # 2. Xây dựng bộ lọc Metadata (Pre-filtering)
        must_conditions = []
        
        # Lọc theo stored_items (Match chính xác)
        if stored_items:
            stored_norm = stored_items.strip().lower()
            if stored_norm.startswith("kho "):
                stored_norm = stored_norm[len("kho "):].strip()
            must_conditions.append(
                models.FieldCondition(
                    key="stored_items",
                    match=models.MatchValue(value=stored_norm)
                )
            )
            
        # Lọc theo khoảng giá (Nhỏ hơn hoặc bằng max_price)
        if max_price:
            must_conditions.append(
                models.FieldCondition(
                    key="price",
                    range=models.Range(lte=max_price) # lte: less than or equal
                )
            )
            
        # Đóng gói filter
        search_filter = models.Filter(must=must_conditions) if must_conditions else None

        # 3. Tìm kiếm Vector trên Qdrant (Chỉ quét các document thỏa mãn filter)
        search_results = qdrant.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            query_filter=search_filter,
            limit=top_k
        )
        
        # 4. Trích xuất nội dung text từ các chunk tìm được
        if not search_results.points:
            return ""
            
        context_chunks = [
            {
                "content": point.payload.get("content", ""),
                "price": point.payload.get("price", 0),
                "type": point.payload.get("type", "product_info"), # Lấy type để phân biệt
                "score": point.score,
                "metadata": point.payload
            }
            for point in search_results.points
        ]
        
        logger.info("Context chunks: %s", context_chunks)
        
        formatted_contexts = []
        for chunk in context_chunks:
            # KIỂM TRA TYPE: Nếu là chính sách thì không hiện giá
            if chunk['type'] == 'policy':
                combined_text = f"[CHÍNH SÁCH WEB]\n{chunk['content']}"
            else:
                # Nếu là sản phẩm thì lấy thêm thông tin name, description, location_province
                product_name = chunk['metadata'].get('name', '')
                description = chunk['metadata'].get('description', '')
                location_province = chunk['metadata'].get('location_province', '')
                formatted_price = f"{chunk['price']:,.0f}".replace(",", ".")
                combined_text = (
                    f"[SẢN PHẨM]\n"
                    f"Tên: {product_name}\n"
                    f"Mô tả: {description}\n"
                    f"Tỉnh: {location_province}\n"
                    f"{chunk['content']}\n"
                    f"Giá bán: {formatted_price} VNĐ"
                )
            
            formatted_contexts.append(combined_text)

        # Nối các khối lại, dùng phân cách rõ ràng để LLM không bị lẫn lộn các đoạn
        context_text = "\n\n" + "="*30 + "\n\n".join(formatted_contexts) + "\n\n" + "="*30
        
        logger.info(f"Context Text gửi cho LLM:\n{context_text}")
        
        return context_text
        
    except Exception as e:
        logger.error(f"❌ Lỗi khi truy xuất Qdrant: {e}")
        return ""
    
def generate_answer_stream(query: str, stored_items: str = None, max_price: float = None):
    """
    Generator function: Gọi retrieve_context lấy dữ liệu, sau đó stream kết quả từ LLM về.
    """
    # Bước 1: Rút trích ngữ cảnh từ Database
    context = retrieve_context(query, stored_items, max_price)
    
    # Xử lý trường hợp database trống hoặc không tìm thấy sản phẩm phù hợp
    if not context:
        yield "Xin lỗi, hiện tại chúng tôi không tìm thấy kho lạnh hoặc thông tin nào phù hợp với yêu cầu của bạn."
        return

    # Bước 2: Xây dựng System Prompt cực kỳ chặt chẽ (Prompt Engineering)
    system_prompt = """Bạn là trợ lý ảo AI xuất sắc của hệ thống E-commerce.
        QUY TẮC BẮT BUỘC:
        1. Thông tin trong [NGỮ CẢNH SẢN PHẨM] là các kho lạnh ĐÃ ĐƯỢC HỆ THỐNG LỌC CHUẨN XÁC theo mức giá và danh mục khách yêu cầu. 
        2. Hãy TỰ TIN giới thiệu các kho lạnh này. TUYỆT ĐỐI KHÔNG được nói là "không có kho lạnh nào phù hợp" nếu trong ngữ cảnh có chứa kho lạnh.
        3. KHÔNG tự ý so sánh toán học (lớn hơn, nhỏ hơn). Chỉ trình bày lại tên, mô tả và giá tiền của kho lạnh trong ngữ cảnh một cách thân thiện, hấp dẫn để chốt sale.
        4. Nếu [NGỮ CẢNH SẢN PHẨM] hoàn toàn trống, lúc đó mới lịch sự xin lỗi khách hàng.

        [NGỮ CẢNH SẢN PHẨM]:
        {context_data}
        """
    # Bước 3: Gọi API OpenAI với chế độ Streaming
    try:
        response = ai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt.format(context_data=context)},
                {"role": "user", "content": query}
            ],
            stream=True,
            temperature=0.1,
            max_tokens=100  # Để siêu thấp (0.1) để AI bám sát dữ liệu, không sáng tạo lung tung
        )

        # Trả về từng chữ ngay khi OpenAI phản hồi
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
                
    except Exception as e:
        logger.error(f"❌ Lỗi khi gọi OpenAI API: {e}")
        yield "Hệ thống AI đang quá tải, vui lòng thử lại sau giây lát."