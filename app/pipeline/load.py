import json
import uuid
import os
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PayloadSchemaType, VectorParams, PointStruct

embedding_model = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
)
COLLECTION_NAME = "cold_storage"

def setup_qdrant():
    if not qdrant_client.collection_exists(COLLECTION_NAME):
        qdrant_client.create_collection(
            collection_name = COLLECTION_NAME,
            vectors_config=VectorParams(size=1536, distance= Distance.COSINE),
        )
        print(f"Đã tạo collection: {COLLECTION_NAME}")

        qdrant_client.create_payload_index(COLLECTION_NAME, "price", PayloadSchemaType.FLOAT)
        qdrant_client.create_payload_index(COLLECTION_NAME, "stored_items", PayloadSchemaType.KEYWORD)
        print("Đã tạo index cho trường price và stored_items")

def embed_and_load_chunk(input_file: str, batch_size: int = 100):
    with open(input_file, "r", encoding="utf-8") as f:
        points = []
        for line in f:
            doc = json.loads(line)
            content = doc.get("content", "")
            # stored_items and price are expected at top-level in the doc
            parent_doc_id = doc.get("parent_doc_id", "unknown_parent_id")
            chunk_id = doc.get("chunk_id", str(uuid.uuid4()))

            embedding_response = embedding_model.embeddings.create(
                input=content,
                model="text-embedding-3-small"
            )
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk_id))
            embedding_vector = embedding_response.data[0].embedding
            # Normalize stored_items so filters (exact match) are consistent
            # Fallback to nested metadata if chunks were produced without top-level stored_items
            raw_stored = doc.get("stored_items") or (doc.get("metadata", {}) or {}).get("stored_items", "") or ""
            norm_stored = raw_stored.strip().lower()
            if norm_stored.startswith("kho "):
                norm_stored = norm_stored[len("kho "):].strip()

            # Fallback price from nested metadata if top-level price is missing
            raw_price = doc.get("price")
            if raw_price is None:
                raw_price = (doc.get("metadata", {}) or {}).get("price", 0)
            try:
                price_value = float(raw_price)
            except (TypeError, ValueError):
                price_value = 0.0

            payload = {
                "parent_doc_id": parent_doc_id,
                "chunk_id": chunk_id,
                "content": content,
                "price": price_value,
                "stored_items": norm_stored if norm_stored else "không",
                "name": doc.get("name", ""),
                "description": doc.get("description", ""),
                "location_province": doc.get("location_province", "")
            }

            point = PointStruct(
                id=point_id,
                vector=embedding_vector,
                payload=payload
            )
            points.append(point)

            if len(points) >= batch_size:
                qdrant_client.upsert(
                    collection_name=COLLECTION_NAME,
                    points=points
                )
                points = []

        if points:
            qdrant_client.upsert(
                collection_name=COLLECTION_NAME,
                points=points
            )
    print(f"Đã load dữ liệu vào Qdrant collection: {COLLECTION_NAME}")

if __name__ == "__main__":
    setup_qdrant()
    input_file = "/app/data/products_data_chunks.jsonl"
    print(f"Đang load dữ liệu từ file")
    embed_and_load_chunk(input_file)
    print("Quá trình load dữ liệu hoàn tất")
