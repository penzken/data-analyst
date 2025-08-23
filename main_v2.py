import requests
import json
import os
from dotenv import load_dotenv
from typing import TypedDict, List, Dict, Any, Union
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
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
        date = row.get('date', '')
        if not date:
            continue
        
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

@tool
def calculate_hourly_stats(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate hourly statistics from order data"""
    hourly_stats = {}
    time_period_stats = {}
    
    for row in rows:
        hour = row.get('hour', '')
        time_period = row.get('time_period', '')
        
        if not hour:
            continue
        
        quantity = safe_convert_to_number(row.get('quantity'))
        price = safe_convert_to_number(row.get('price'))
        revenue = quantity * price
        
        # Hourly stats
        if hour not in hourly_stats:
            hourly_stats[hour] = {
                'total_quantity': 0,
                'total_revenue': 0,
                'unique_orders': set(),
                'unique_products': set()
            }
        
        hourly_stats[hour]['total_quantity'] += quantity
        hourly_stats[hour]['total_revenue'] += revenue
        hourly_stats[hour]['unique_orders'].add(row.get('orderId'))
        hourly_stats[hour]['unique_products'].add(row.get('productName'))
        
        # Time period stats
        if time_period and time_period not in time_period_stats:
            time_period_stats[time_period] = {
                'total_quantity': 0,
                'total_revenue': 0,
                'unique_orders': set(),
                'unique_products': set()
            }
        
        if time_period:
            time_period_stats[time_period]['total_quantity'] += quantity
            time_period_stats[time_period]['total_revenue'] += revenue
            time_period_stats[time_period]['unique_orders'].add(row.get('orderId'))
            time_period_stats[time_period]['unique_products'].add(row.get('productName'))
    
    # Convert sets to counts and sort
    for hour_stats in hourly_stats.values():
        hour_stats['order_count'] = len(hour_stats['unique_orders'])
        hour_stats['product_count'] = len(hour_stats['unique_products'])
        del hour_stats['unique_orders']
        del hour_stats['unique_products']
    
    for period_stats in time_period_stats.values():
        period_stats['order_count'] = len(period_stats['unique_orders'])
        period_stats['product_count'] = len(period_stats['unique_products'])
        del period_stats['unique_orders']
        del period_stats['unique_products']
    
    # Find busiest hours and periods
    busiest_hours = sorted(
        hourly_stats.items(),
        key=lambda x: x[1]['order_count'],
        reverse=True
    )[:5]
    
    busiest_periods = sorted(
        time_period_stats.items(),
        key=lambda x: x[1]['order_count'],
        reverse=True
    )
    
    return {
        "hourly_breakdown": hourly_stats,
        "time_period_breakdown": time_period_stats,
        "busiest_hours": [
            {
                "hour": hour,
                "order_count": stats['order_count'],
                "total_revenue": stats['total_revenue'],
                "total_quantity": stats['total_quantity']
            }
            for hour, stats in busiest_hours
        ],
        "busiest_periods": [
            {
                "period": period,
                "order_count": stats['order_count'],
                "total_revenue": stats['total_revenue'],
                "total_quantity": stats['total_quantity']
            }
            for period, stats in busiest_periods
        ]
    }

def calculate_comprehensive_stats(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate all statistics using the calculator tools"""
    revenue_stats = calculate_total_revenue.invoke({"rows": rows})
    product_stats = calculate_product_stats.invoke({"rows": rows})
    daily_stats = calculate_daily_stats.invoke({"rows": rows})
    hourly_stats = calculate_hourly_stats.invoke({"rows": rows})
    
    return {
        "revenue_summary": revenue_stats,
        "product_analysis": product_stats,
        "daily_breakdown": daily_stats,
        "time_analysis": hourly_stats,
        "data_quality": {
            "total_rows": len(rows),
            "rows_with_valid_price": sum(1 for row in rows if safe_convert_to_number(row.get('price')) > 0),
            "rows_with_valid_quantity": sum(1 for row in rows if safe_convert_to_number(row.get('quantity')) > 0),
            "rows_with_valid_time": sum(1 for row in rows if row.get('hour', '') != ''),
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
            "Bây giờ bạn có thêm dữ liệu thời gian chi tiết (ngày, giờ, khung giờ) để phân tích xu hướng theo thời gian. "
            "Sử dụng các số liệu đã tính sẵn để tạo báo cáo chính xác. "
            "Trả lời bằng tiếng Việt nếu câu hỏi là tiếng Việt. "
            "Tập trung vào việc giải thích và đưa ra insight từ các số liệu đã tính toán, đặc biệt là phân tích theo thời gian."
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
            "5. Phân tích theo giờ - Khung giờ nào đông khách nhất\n"
            "6. Phân tích theo khung thời gian (Sáng, Chiều, Tối, Đêm)\n"
            "7. Top 5 giờ có nhiều đơn hàng nhất\n"
            "8. Đánh giá chất lượng dữ liệu\n"
            "9. Insight và khuyến nghị dựa trên phân tích thời gian\n\n"
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
        
        # Analyze data with time analysis
        question = "Phân tích dữ liệu bao gồm cả phân tích theo thời gian và tóm tắt ngắn gọn."
        result = analyze_with_agent(payload, question)
        print(result)
        
    except requests.RequestException as e:
        print(f"Error fetching data: {str(e)}")
    except Exception as e:
        print(f"Error during analysis: {str(e)}")

if __name__ == "__main__":
    main()