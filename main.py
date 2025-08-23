import requests
import json
import os
from dotenv import load_dotenv
from typing import TypedDict, List, Dict, Any, Union
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool

# Import preprocessing utilities from module
from preprocessing import preprocessing_data, safe_convert_to_number

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Configuration
N8N_URL = 'https://aizen.auto.123host.asia/webhook/9057a9e7-1f29-4474-a501-730a2f2bfb68'

class AnalysisState(TypedDict, total=False):
    question: str
    payload: Any
    rows: List[Dict[str, Any]]
    context: str
    analysis: str
    calculations: Dict[str, Any]

@tool
def calculate_total_revenue(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate total revenue from order data"""
    total_revenue = 0
    unique_orders = set()
    
    for row in rows:
        order_id = row.get('orderId')
        calc_total = safe_convert_to_number(row.get('calcTotalMoney'))
        
        # Only count each order once for total revenue
        if order_id and order_id not in unique_orders:
            unique_orders.add(order_id)
            total_revenue += calc_total
    
    return {
        "total_revenue": total_revenue,
        "total_orders": len(unique_orders),
        "average_order_value": total_revenue / len(unique_orders) if unique_orders else 0
    }

@tool
def calculate_product_stats(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate product statistics including top products by quantity and revenue"""
    product_stats = {}
    
    for row in rows:
        product_name = row.get('productName', 'Unknown')
        quantity = safe_convert_to_number(row.get('quantity'))
        price = safe_convert_to_number(row.get('price'))
        
        if product_name not in product_stats:
            product_stats[product_name] = {
                'total_quantity': 0,
                'total_revenue': 0,
                'order_count': 0
            }
        
        product_stats[product_name]['total_quantity'] += quantity
        product_stats[product_name]['total_revenue'] += quantity * price
        product_stats[product_name]['order_count'] += 1
    
    # Sort by quantity and revenue
    top_by_quantity = sorted(
        product_stats.items(), 
        key=lambda x: x[1]['total_quantity'], 
        reverse=True
    )[:5]
    
    top_by_revenue = sorted(
        product_stats.items(), 
        key=lambda x: x[1]['total_revenue'], 
        reverse=True
    )[:5]
    
    return {
        "top_products_by_quantity": [
            {
                "product_name": name,
                "total_quantity": stats['total_quantity'],
                "total_revenue": stats['total_revenue'],
                "order_count": stats['order_count']
            }
            for name, stats in top_by_quantity
        ],
        "top_products_by_revenue": [
            {
                "product_name": name,
                "total_quantity": stats['total_quantity'],
                "total_revenue": stats['total_revenue'],
                "order_count": stats['order_count']
            }
            for name, stats in top_by_revenue
        ]
    }

@tool
def calculate_daily_stats(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate daily statistics from order data"""
    daily_stats = {}
    
    for row in rows:
        created_dt = row.get('createdDateTime', '')
        if not created_dt:
            continue
            
        # Extract date (assuming format includes date)
        date = created_dt.split('T')[0] if 'T' in created_dt else created_dt.split(' ')[0]
        
        quantity = safe_convert_to_number(row.get('quantity'))
        price = safe_convert_to_number(row.get('price'))
        revenue = quantity * price
        
        if date not in daily_stats:
            daily_stats[date] = {
                'total_quantity': 0,
                'total_revenue': 0,
                'unique_orders': set(),
                'unique_products': set()
            }
        
        daily_stats[date]['total_quantity'] += quantity
        daily_stats[date]['total_revenue'] += revenue
        daily_stats[date]['unique_orders'].add(row.get('orderId'))
        daily_stats[date]['unique_products'].add(row.get('productName'))
    
    # Convert sets to counts
    for date_stats in daily_stats.values():
        date_stats['order_count'] = len(date_stats['unique_orders'])
        date_stats['product_count'] = len(date_stats['unique_products'])
        del date_stats['unique_orders']
        del date_stats['unique_products']
    
    return daily_stats


def calculate_comprehensive_stats(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate all statistics using the calculator tools"""
    revenue_stats = calculate_total_revenue.invoke({"rows": rows})
    product_stats = calculate_product_stats.invoke({"rows": rows})
    daily_stats = calculate_daily_stats.invoke({"rows": rows})
    
    return {
        "revenue_summary": revenue_stats,
        "product_analysis": product_stats,
        "daily_breakdown": daily_stats,
        "data_quality": {
            "total_rows": len(rows),
            "rows_with_valid_price": sum(1 for row in rows if safe_convert_to_number(row.get('price')) > 0),
            "rows_with_valid_quantity": sum(1 for row in rows if safe_convert_to_number(row.get('quantity')) > 0),
        }
    }


def fetch_data(from_date: str, to_date: str) -> Dict[str, Any]:
    """Fetch data from n8n webhook"""
    data = {
        "fromDate": from_date,
        "toDate": to_date
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(N8N_URL, data=json.dumps(data), headers=headers)
    response.raise_for_status()
    return response.json()


def preprocess_node(state: AnalysisState) -> Dict[str, Any]:
    """Preprocess node for LangGraph with calculations"""
    payload = state.get("payload")
    if payload is None:
        return {"rows": [], "context": "[]", "calculations": {}}
    
    rows = preprocessing_data(payload)
    
    # Calculate comprehensive statistics
    calculations = calculate_comprehensive_stats(rows)
    
    # Create context with both raw data and calculations
    context_data = {
        "raw_data_sample": rows[:10] if len(rows) > 10 else rows,  # Show sample for context
        "total_rows": len(rows),
        "calculations": calculations
    }
    context_json = json.dumps(context_data, ensure_ascii=False, default=str)
    
    # Limit context length to avoid token limits
    if len(context_json) > 100000:
        # If too long, use only calculations and summary
        context_data = {
            "total_rows": len(rows),
            "calculations": calculations
        }
        context_json = json.dumps(context_data, ensure_ascii=False, default=str)
    
    return {"rows": rows, "context": context_json, "calculations": calculations}


def llm_node(state: AnalysisState) -> Dict[str, Any]:
    """LLM analysis node for LangGraph with calculator tools"""
    question = state.get("question", "Phân tích dữ liệu và tóm tắt ngắn gọn.")
    context = state.get("context", "")
    calculations = state.get("calculations", {})
    
    # Get LLM from environment or state
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is required")
    
    # Bind calculator tools to LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        temperature=0.3, 
        api_key=google_api_key
    )
    
    # Add pre-calculated stats to the prompt
    calc_summary = json.dumps(calculations, ensure_ascii=False, indent=2, default=str)
    
    messages = [
        SystemMessage(content=(
            "Bạn là chuyên gia phân tích dữ liệu ngành F&B. "
            "Dữ liệu đã được tiền xử lý và tính toán chính xác với các công cụ tính toán chuyên dụng. "
            "Sử dụng các số liệu đã tính sẵn để tạo báo cáo chính xác. "
            "Trả lời bằng tiếng Việt nếu câu hỏi là tiếng Việt. "
            "Tập trung vào việc giải thích và đưa ra insight từ các số liệu đã tính toán."
        )),
        HumanMessage(content=(
            f"Dữ liệu và kết quả tính toán:\n{context}\n\n"
            f"Các số liệu đã được tính toán chính xác:\n{calc_summary}\n\n"
            f"Câu hỏi: {question}\n\n"
            "Yêu cầu: Dựa trên các số liệu đã tính toán, hãy tạo báo cáo tóm tắt bao gồm:\n"
            "1. Tổng quan (số đơn hàng, tổng doanh thu, giá trị đơn hàng trung bình)\n"
            "2. Top 5 sản phẩm theo số lượng bán\n"
            "3. Top 5 sản phẩm theo doanh thu\n"
            "4. Phân tích theo ngày (nếu có)\n"
            "5. Khung giờ nào đông khách nhất\n"
            "6. Đánh giá chất lượng dữ liệu\n"
            "7. Insight và khuyến nghị\n\n"
            "Sử dụng định dạng markdown để trình bày báo cáo một cách rõ ràng và chuyên nghiệp."
        )),
    ]
    
    response = llm.invoke(messages)
    return {"analysis": response.content}


def build_analysis_graph() -> Any:
    """Build LangGraph pipeline: preprocess -> llm -> END"""
    graph = StateGraph(AnalysisState)
    graph.add_node("preprocess", preprocess_node)
    graph.add_node("llm", llm_node)
    graph.set_entry_point("preprocess")
    graph.add_edge("preprocess", "llm")
    graph.add_edge("llm", END)
    return graph.compile()


def analyze_with_agent(payload: Any, question: str) -> str:
    """Run agent to analyze payload. Returns analysis content (string)."""
    app = build_analysis_graph()
    result = app.invoke({"payload": payload, "question": question})
    return result.get("analysis", "")


def main():
    """Main execution function"""
    # Check for required environment variable
    if not os.getenv("GOOGLE_API_KEY"):
        raise ValueError("Please set GOOGLE_API_KEY environment variable")
    
    try:
        # Fetch data
        payload = fetch_data("2025-08-17", "2025-08-22")
        
        # Analyze data
        question = "Phân tích dữ liệu và tóm tắt ngắn gọn."
        result = analyze_with_agent(payload, question)
        print(result)
        
    except requests.RequestException as e:
        print(f"Error fetching data: {str(e)}")
    except Exception as e:
        print(f"Error during analysis: {str(e)}")

if __name__ == "__main__":
    main()