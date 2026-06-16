import json
import os
import logging
from sqlalchemy import create_engine, text

DATA_DIR = "/app/data"
#DB_URL = os.getenv("DATABASE_URL")
DB_URL = "mysql+pymysql://root:123456@mysql_db:3306/coldstorage_db?charset=utf8mb4"
engine = create_engine(DB_URL)
_logger = logging.getLogger(__name__)

def extract_products_data_to_jsonl(output_file: str):
    _logger.info("Starting data extraction")
    try:
        with engine.connect() as connection:
            query =text("""
                            SELECT id_warehouse, name, description, location_province, address, location_address_text, location_commune
                    from Warehouse
                    where status = 'Active'
                    """)
            result = connection.execute(query)
            with open(output_file, "w", encoding = "utf-8") as f:
                for row in result:
                    safe_desc = row.description if getattr(row, "description", None) else "Không"
                    safe_province = row.location_province if getattr(row, "location_province", None) else "Không"
                    warehouse_address = row.location_address_text or row.address or "Không"
                    location_commune = row.location_commune or "Không"

                    context_text = (
                        f"Tên kho: {row.name}\n"
                        f"Mô tả: {safe_desc}\n"
                        f"Tỉnh: {safe_province}\n"
                        f"Địa chỉ: {warehouse_address}\n"
                        f"Phường/Xã: {location_commune}"
                    )
                    doc = {
                        "doc_id": f"warehouse_{row.id_warehouse}",
                        "content": context_text,
                        "name": row.name,
                        "description": safe_desc,
                        "location_province": safe_province,
                        "address": warehouse_address,
                        "location_commune": location_commune
                    }
                    f.write(json.dumps(doc, ensure_ascii=False) + "\n")
            _logger.info(f"Data extraction completed. Output file: {output_file}")
    except Exception as e:
        _logger.error(f"Error during extract: {e}")
        raise

if __name__ == "__main__":
    output_file = "/app/data/products_data_raws.jsonl"
    _logger.info("Starting the data extract")
    try:
        extract_products_data_to_jsonl(output_file)

        _logger.info("\nKiểm Tra KQ")
        if os.path.exists(output_file):
            with open(output_file, "r", encoding="utf-8") as f:
                for i,line in enumerate(f):
                    if i < 2:
                        parsed_json = json.loads(line)
                        print(json.dumps(parsed_json, indent=2, ensure_ascii=False))
        else:
            _logger.info("Lỗi")
    except Exception as e:
        _logger.error(f"Test fail: {e}")