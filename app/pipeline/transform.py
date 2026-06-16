import json
from langchain_text_splitters import RecursiveCharacterTextSplitter

def transform_json_to_chunk(input_file: str, output_file: str, chunk_size: int = 500, chunk_overlap: int= 50):
    text_splitter = RecursiveCharacterTextSplitter (chunk_size=chunk_size,chunk_overlap=chunk_overlap)

    processed_trunks = set()
    with open(input_file, "r", encoding="utf-8") as infile, open(output_file, "w", encoding="utf-8"):
        for line in infile:
            doc = json.loads(line)
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})
            doc_id = doc.get("doc_id", "unknown_id")

            #Split coontent into chunks
            chunks = text_splitter.split_text(content)

            stored_items = doc.get("stored_items")
            price = doc.get("price")
            name = doc.get("name")
            description = doc.get("description")
            location_province = doc.get("location_province")
            address = doc.get("address")
            location_commune = doc.get("location_commune")

            info_lines = []
            if name:
                info_lines.append(f"Tên kho: {name}")
            if description:
                info_lines.append(f"Mô tả: {description}")
            if location_province:
                info_lines.append(f"Tỉnh: {location_province}")
            if address:
                info_lines.append(f"Địa chỉ: {address}")
            if location_commune:
                info_lines.append(f"Phường/Xã: {location_commune}")
            base_info = "\n".join(info_lines)

            for i, chunk in enumerate(chunks):
                if base_info:
                    enriched_text = f"{base_info}\n\n{chunk}"
                else:
                    enriched_text = chunk

                chunk_doc = {
                    "parent_doc_id": doc_id,
                    "chunk_id": f"{doc_id}_chunk_{i}",
                    "content": enriched_text,
                    "stored_items": stored_items,
                    "price": price,
                    "name": name,
                    "description": description,
                    "location_province": location_province,
                    "address": address,
                    "location_commune": location_commune,
                    "metadata": metadata
                }
                processed_trunks.add(json.dumps(chunk_doc, ensure_ascii=False))
    with open(output_file, "a", encoding = "utf-8") as outfile:
        for chunk in processed_trunks:
            outfile.write(chunk + "\n")
    print(f"Transform completed. Ouput File: {output_file}")

if __name__ == "__main__":
    input_file = "/app/data/products_data_raws.jsonl"
    output_file = "/app/data/products_data_chunks.jsonl"
    transform_json_to_chunk(input_file, output_file)