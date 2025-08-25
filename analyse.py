import json
import pandas as pd
from datetime import datetime
import numpy as np
from collections import defaultdict

def load_invoices(file_path='invoices.json'):
    """Load invoices data from JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"File {file_path} not found!")
        return []
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {file_path}")
        return []

def analyze_invoices(invoices):
    """Analyze invoices and calculate key metrics"""
    if not invoices:
        print("No invoices data to analyze")
        return
    
    print("=== PHÂN TÍCH DỮ LIỆU INVOICES ===\n")
    
    # 1. Thống kê cơ bản
    total_invoices = len(invoices)
    print(f"1. TỔNG QUAN:")
    print(f"   - Tổng số hóa đơn: {total_invoices:,}")
    
    # 2. Phân tích theo thời gian
    dates = []
    total_amounts = []
    daily_sales = defaultdict(float)
    
    for invoice in invoices:
        date_str = invoice['date_time'].split(' ')[0]  # Lấy ngày
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        dates.append(date_obj)
        total_amounts.append(invoice['total_amount'])
        daily_sales[date_str] += invoice['total_amount']
    
    # Chuyển đổi sang pandas để dễ xử lý
    df = pd.DataFrame({
        'date': dates,
        'total_amount': total_amounts
    })
    
    print(f"   - Tổng doanh thu: {sum(total_amounts):,} VND")
    print(f"   - Doanh thu trung bình/hóa đơn: {np.mean(total_amounts):,.0f} VND")
    print(f"   - Doanh thu trung bình/ngày: {np.mean(list(daily_sales.values())):,.0f} VND")
    print(f"   - Thời gian: từ {min(dates).strftime('%Y-%m-%d')} đến {max(dates).strftime('%Y-%m-%d')}")
    
    # 3. Phân tích theo ngày trong tuần
    df['weekday'] = df['date'].dt.day_name()
    weekday_sales = df.groupby('weekday')['total_amount'].agg(['sum', 'count', 'mean']).round(0)
    weekday_sales = weekday_sales.reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    
    print(f"\n2. PHÂN TÍCH THEO NGÀY TRONG TUẦN:")
    for day, row in weekday_sales.iterrows():
        if pd.notna(row['sum']):
            print(f"   {day}: {row['sum']:>10,.0f} VND ({row['count']:>2} hóa đơn, TB: {row['mean']:>8,.0f} VND)")
    
    # 4. Phân tích theo tháng
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year
    monthly_sales = df.groupby(['year', 'month'])['total_amount'].agg(['sum', 'count', 'mean']).round(0)
    
    print(f"\n3. PHÂN TÍCH THEO THÁNG:")
    for (year, month), row in monthly_sales.iterrows():
        month_name = datetime(year, month, 1).strftime('%B %Y')
        print(f"   {month_name}: {row['sum']:>10,.0f} VND ({row['count']:>2} hóa đơn, TB: {row['mean']:>8,.0f} VND)")
    
    # 5. Phân tích sản phẩm
item_stats = defaultdict(lambda: {'quantity': 0, 'revenue': 0, 'count': 0})
    
    for invoice in invoices:
        for item in invoice['items']:
            item_name = item['item_name']
            item_stats[item_name]['quantity'] += item['quantity']
            item_stats[item_name]['revenue'] += item['amount']
            item_stats[item_name]['count'] += 1
    
    print(f"\n4. PHÂN TÍCH SẢN PHẨM:")
    sorted_items = sorted(item_stats.items(), key=lambda x: x[1]['revenue'], reverse=True)
    
    for item_name, stats in sorted_items:
        avg_price = stats['revenue'] / stats['quantity'] if stats['quantity'] > 0 else 0
        print(f"   {item_name}:")
        print(f"     - Số lượng bán: {stats['quantity']:,}")
        print(f"     - Doanh thu: {stats['revenue']:,} VND")
        print(f"     - Số lần xuất hiện: {stats['count']:,}")
        print(f"     - Giá trung bình: {avg_price:,.0f} VND")
    
    # 6. Phân tích giá trị hóa đơn
    print(f"\n5. PHÂN TÍCH GIÁ TRỊ HÓA ĐƠN:")
    print(f"   - Hóa đơn cao nhất: {max(total_amounts):,} VND")
    print(f"   - Hóa đơn thấp nhất: {min(total_amounts):,} VND")
    print(f"   - Độ lệch chuẩn: {np.std(total_amounts):,.0f} VND")
    
    # Phân loại hóa đơn theo giá trị
    small_invoices = len([x for x in total_amounts if x < 30000])
    medium_invoices = len([x for x in total_amounts if 30000 <= x < 60000])
    large_invoices = len([x for x in total_amounts if x >= 60000])
    
    print(f"   - Hóa đơn nhỏ (<30k): {small_invoices:,} ({small_invoices/total_invoices*100:.1f}%)")
    print(f"   - Hóa đơn trung bình (30k-60k): {medium_invoices:,} ({medium_invoices/total_invoices*100:.1f}%)")
    print(f"   - Hóa đơn lớn (>=60k): {large_invoices:,} ({large_invoices/total_invoices*100:.1f}%)")
    
    # 7. Phân tích xu hướng
    print(f"\n6. PHÂN TÍCH XU HƯỚNG:")
    df_sorted = df.sort_values('date')
    df_sorted['cumulative'] = df_sorted['total_amount'].cumsum()
    
    # Tính tốc độ tăng trưởng
    if len(df_sorted) > 1:
        first_week = df_sorted.head(7)['total_amount'].sum()
        last_week = df_sorted.tail(7)['total_amount'].sum()
        if first_week > 0:
            growth_rate = ((last_week - first_week) / first_week) * 100
            print(f"   - Tốc độ tăng trưởng (tuần đầu vs tuần cuối): {growth_rate:+.1f}%")
    
    # 8. Tạo DataFrame để export
    print(f"\n7. TẠO DATAFRAME ĐỂ PHÂN TÍCH:")
    
    # DataFrame cho hóa đơn
    invoices_df = pd.DataFrame(invoices)
    invoices_df['date'] = pd.to_datetime(invoices_df['date_time'])
    invoices_df['date_only'] = invoices_df['date'].dt.date
    invoices_df['weekday'] = invoices_df['date'].dt.day_name()
    invoices_df['month'] = invoices_df['date'].dt.month
    invoices_df['year'] = invoices_df['date'].dt.year
    
    # DataFrame cho items
    all_items = []
    for invoice in invoices:
for item in invoice['items']:
            all_items.append({
                'invoice_id': invoice['invoice_id'],
                'date': invoice['date_time'].split(' ')[0],
                'item_name': item['item_name'],
                'quantity': item['quantity'],
                'price': item['price'],
                'amount': item['amount']
            })
    
    items_df = pd.DataFrame(all_items)
    
    print(f"   - Invoices DataFrame: {invoices_df.shape}")
    print(f"   - Items DataFrame: {items_df.shape}")
    
    return invoices_df, items_df

def export_to_csv(invoices_df, items_df):
    """Export data to CSV files for further analysis"""
    try:
        invoices_df.to_csv('invoices_analysis.csv', index=False, encoding='utf-8-sig')
        items_df.to_csv('items_analysis.csv', index=False, encoding='utf-8-sig')
        print(f"\n8. XUẤT DỮ LIỆU:")
        print(f"   - Đã xuất invoices_analysis.csv")
        print(f"   - Đã xuất items_analysis.csv")
    except Exception as e:
        print(f"Lỗi khi xuất file: {e}")

def main():
    """Main function to run the analysis"""
    print("Bắt đầu phân tích dữ liệu invoices...")
    
    # Load dữ liệu
    invoices = load_invoices()
    
    if invoices:
        # Phân tích dữ liệu
        invoices_df, items_df = analyze_invoices(invoices)
        
        # Xuất ra CSV để phân tích thêm
        export_to_csv(invoices_df, items_df)
        
        print(f"\n=== HOÀN THÀNH PHÂN TÍCH ===")
        print(f"Bạn có thể sử dụng các file CSV để phân tích sâu hơn với pandas, matplotlib, hoặc các công cụ khác.")
    else:
        print("Không thể load dữ liệu invoices!")

if __name__ == "__main__":
    main()