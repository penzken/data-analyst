import json
import os
from typing import List, Dict

KNOWLEDGE_FILE = 'knowledge.json'

def _load_knowledge() -> List[Dict]:
    """Tải kiến thức từ file JSON."""
    if not os.path.exists(KNOWLEDGE_FILE):
        return []
    try:
        with open(KNOWLEDGE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def add_knowledge(text: str, tags: List[str] = None):
    """Thêm một mẩu kiến thức mới vào cơ sở dữ liệu."""
    knowledge_base = _load_knowledge()
    new_entry = {
        "id": len(knowledge_base) + 1,
        "text": text,
        "tags": tags or []
    }
    knowledge_base.append(new_entry)
    with open(KNOWLEDGE_FILE, 'w', encoding='utf-8') as f:
        json.dump(knowledge_base, f, indent=4, ensure_ascii=False)
    print(f"✅ Đã thêm kiến thức mới: '{text}'")

def retrieve_knowledge(query: str) -> List[str]:
    """
    Truy xuất kiến thức liên quan dựa trên query.
    Đây là một cơ chế tìm kiếm đơn giản dựa trên từ khóa.
    Trong thực tế, có thể nâng cấp bằng vector search.
    """
    knowledge_base = _load_knowledge()
    relevant_knowledge = []
    query_words = set(query.lower().split())

    for entry in knowledge_base:
        entry_words = set(entry['text'].lower().split())
        # Tìm các kiến thức có từ khóa chung với câu hỏi
        if query_words.intersection(entry_words):
            relevant_knowledge.append(entry['text'])
            
    if relevant_knowledge:
        print(f"📚 Đã tìm thấy {len(relevant_knowledge)} mẩu kiến thức liên quan.")
    return relevant_knowledge

def example_usage():
    """Ví dụ về cách thêm và truy xuất kiến thức."""
    print("--- Ví dụ về Cơ sở tri thức ---")
    
    # Xóa file cũ để chạy lại ví dụ
    if os.path.exists(KNOWLEDGE_FILE):
        os.remove(KNOWLEDGE_FILE)

    # Người dùng thêm kiến thức
    add_knowledge(
        "Đối với ngành F&B, khung giờ vàng thường là từ 18:00 đến 20:00. Hãy chú trọng phân tích xem có đúng như vậy không.",
        ["time_analysis", "peak_hours"]
    )
    add_knowledge(
        "Sản phẩm có doanh thu cao nhưng số lượng bán ít có thể là sản phẩm cao cấp. Đề xuất các combo bán kèm để tăng doanh số.",
        ["product_analysis", "strategy"]
    )
    add_knowledge(
        "Nếu giá trị đơn hàng trung bình thấp, hãy gợi ý các chiến lược up-selling hoặc cross-selling.",
        ["revenue_analysis", "strategy"]
    )

    # Hệ thống truy xuất kiến thức khi có câu hỏi
    question = "Phân tích doanh thu và hiệu suất sản phẩm."
    retrieved = retrieve_knowledge(question)
    print(f"\nKiến thức liên quan cho câu hỏi '{question}':")
    for item in retrieved:
        print(f"- {item}")

if __name__ == '__main__':
    example_usage()