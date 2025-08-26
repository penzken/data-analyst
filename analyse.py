# analyse.py

import pandas as pd
from datetime import datetime, timedelta

def analyze_data(invoices_df):
    """
    Thực hiện phân tích toàn diện, đảm bảo tất cả các kiểu dữ liệu số
    được chuyển đổi sang kiểu gốc của Python để tương thích với JSON.
    """
    if invoices_df.empty:
        return {}

    # --- Các chỉ số tổng quan ---
    total_invoices = len(invoices_df)
    overall_total_revenue = invoices_df['tong_tien_hoa_don'].sum()
    
    latest_date = invoices_df['datetime'].max()
    current_month_start = latest_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    current_month_df = invoices_df[invoices_df['datetime'] >= current_month_start]
    current_month_revenue = current_month_df['tong_tien_hoa_don'].sum()


    # --- Phân tích sản phẩm ---
    all_items = []
    for index, row in invoices_df.iterrows():
        for item in row.get('chi_tiet', []):
            all_items.append({
                'ten_hang': item.get('ten_hang'),
                'so_luong': item.get('so_luong', 0),
                'thanh_tien': item.get('thanh_tien', 0),
                'nhom': item.get('nhom', 'Không xác định'), 
                'loai': item.get('loai', 'Chưa phân loại')
            })
    items_df = pd.DataFrame(all_items)
    
    product_summary = items_df.groupby('ten_hang').agg(
        total_quantity=('so_luong', 'sum'),
        total_revenue=('thanh_tien', 'sum')
    ).reset_index().sort_values(by='total_revenue', ascending=False)
    
    product_summary['total_quantity'] = product_summary['total_quantity'].astype(int)
    product_summary['total_revenue'] = product_summary['total_revenue'].astype(int)

    # --- HIERARCHICAL PRODUCT ANALYSIS ---
    product_hierarchy = {}
    if not items_df.empty:
        for nhom_name, nhom_df in items_df.groupby('nhom'):
            product_hierarchy[nhom_name] = {
                'total_revenue': int(nhom_df['thanh_tien'].sum()),
                'categories': {}
            }
            for loai_name, loai_df in nhom_df.groupby('loai'):
                top_products = loai_df.groupby('ten_hang')['thanh_tien'].sum().nlargest(5)
                
                product_hierarchy[nhom_name]['categories'][loai_name] = {
                    'total_revenue': int(loai_df['thanh_tien'].sum()),
                    'top_products': top_products.astype(int).to_dict()
                }

    # --- Phân tích cho trang Reports ---
    df_reports = invoices_df.copy()
    vietnamese_days_map = {
        'Monday': 'Thứ Hai', 'Tuesday': 'Thứ Ba', 'Wednesday': 'Thứ Tư',
        'Thursday': 'Thứ Năm', 'Friday': 'Thứ Sáu', 'Saturday': 'Thứ Bảy', 'Sunday': 'Chủ Nhật'
    }
    day_order_vietnamese = ['Thứ Hai', 'Thứ Ba', 'Thứ Tư', 'Thứ Năm', 'Thứ Sáu', 'Thứ Bảy', 'Chủ Nhật']
    df_reports['weekday_english'] = df_reports['datetime'].dt.day_name()
    df_reports['weekday_vietnamese'] = df_reports['weekday_english'].map(vietnamese_days_map)
    weekday_sales = df_reports.groupby('weekday_vietnamese')['tong_tien_hoa_don'].sum()
    weekday_sales = weekday_sales.reindex(day_order_vietnamese, fill_value=0)
    df_reports['month'] = df_reports['datetime'].dt.strftime('%Y-%m')
    monthly_sales = df_reports.groupby('month')['tong_tien_hoa_don'].sum()
    item_distribution = items_df.groupby('loai')['thanh_tien'].sum()

    # --- Phân tích theo thời gian cho Dashboard chính ---
    latest_date_normalized = latest_date.normalize()
    today_df = invoices_df[invoices_df['datetime'].dt.normalize() == latest_date_normalized]
    yesterday_df = invoices_df[invoices_df['datetime'].dt.normalize() == (latest_date_normalized - timedelta(days=1))]
    last7days_start = latest_date_normalized - timedelta(days=6)
    last7days_df = invoices_df[(invoices_df['datetime'] >= last7days_start) & (invoices_df['datetime'] < latest_date_normalized + timedelta(days=1))]

    def process_period(df, start_date, num_days):
        result = {'total': int(df['tong_tien_hoa_don'].sum()), 'byHour': [0]*24, 'byDay': {}}
        hourly_sum = df.groupby(df['datetime'].dt.hour)['tong_tien_hoa_don'].sum()
        for hour, total in hourly_sum.items():
            result['byHour'][int(hour)] = int(total)
        for i in range(num_days):
            day = start_date + timedelta(days=i)
            result['byDay'][day.strftime('%Y-%m-%d')] = 0
        daily_sum = df.groupby(df['datetime'].dt.date)['tong_tien_hoa_don'].sum()
        for date, total in daily_sum.items():
            result['byDay'][date.strftime('%Y-%m-%d')] = int(total)
        return result

    # --- Tổng hợp tất cả kết quả ---
    return {
        "overall_metrics": {
            "total_invoices": int(total_invoices),
            "total_revenue": int(overall_total_revenue),
            "current_month_revenue": int(current_month_revenue)
        },
        "dashboard_data": {
            "today": process_period(today_df, latest_date_normalized, 1),
            "yesterday": process_period(yesterday_df, latest_date_normalized - timedelta(days=1), 1),
            "last7days": process_period(last7days_df, last7days_start, 7)
        },
        "product_analysis": product_summary.to_dict(orient='records'),
        "reports_analysis": {
            'weekday_sales': weekday_sales.astype(int).to_dict(),
            'monthly_sales': monthly_sales.astype(int).to_dict(),
            'item_distribution': item_distribution.astype(int).to_dict()
        },
        "product_hierarchy": product_hierarchy
    }