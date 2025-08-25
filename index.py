from flask import Flask, jsonify, json, render_template
from flask_cors import CORS
import pandas as pd
from collections import defaultdict
import os

app = Flask(__name__, template_folder='templates')
CORS(app)

# --- Helper Functions ---
def find_invoice_path():
    """Checks for invoices.json in common locations and returns the valid path."""
    if os.path.exists('invoices.json'):
        return 'invoices.json'
    elif os.path.exists('reports/invoices.json'):
        return 'reports/invoices.json'
    else:
        return None

def get_sidebar_html(active_page=''):
    """
    Loads the sidebar template and dynamically adds the 'active' class
    to the link corresponding to the current page.
    """
    try:
        with open('templates/_sidebar.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        placeholders = {
            'sales': '{{ sales_active }}',
            'products': '{{ products_active }}',
            'reports': '{{ reports_active }}'
        }

        for page, placeholder in placeholders.items():
            if page == active_page:
                content = content.replace(placeholder, 'active')
            else:
                content = content.replace(placeholder, '')
        
        return content

    except FileNotFoundError:
        return "<p>Error: Sidebar template not found.</p>"


# --- Data Loading ---
def load_and_prepare_data():
    """Loads and prepares the invoice data from JSON."""
    invoice_path = find_invoice_path()
    if not invoice_path:
        print("Error: invoices.json not found in root or /reports directory!")
        return pd.DataFrame()
        
    try:
        df = pd.read_json(invoice_path)
        df['date_time'] = pd.to_datetime(df['date_time'])
        return df
    except Exception as e:
        print(f"Error loading data from {invoice_path}: {e}")
        return pd.DataFrame()

invoices_df = load_and_prepare_data()

# --- HTML Page Routes ---
@app.route('/', methods=['GET'])
def sales_page():
    """Serves the main sales dashboard page with the sidebar."""
    sidebar_content = get_sidebar_html(active_page='sales')
    return render_template('index.html', sidebar=sidebar_content)

@app.route('/products', methods=['GET'])
def products_page():
    """Serves the product analysis page with the sidebar."""
    sidebar_content = get_sidebar_html(active_page='products')
    return render_template('products.html', sidebar=sidebar_content)

@app.route('/reports', methods=['GET'])
def reports_page():
    """Serves the detailed reports page with the sidebar."""
    sidebar_content = get_sidebar_html(active_page='reports')
    return render_template('reports.html', sidebar=sidebar_content)

# --- API Endpoints ---
@app.route('/api/invoices', methods=['GET'])
def get_invoices():
    invoice_path = find_invoice_path()
    if not invoice_path:
        return jsonify({"error": "invoices.json not found"}), 404
    try:
        with open(invoice_path, 'r', encoding='utf-8') as f:
            invoices = json.load(f)
        for invoice in invoices:
            if 'date_time' in invoice:
                date_time_str = str(invoice['date_time'])
                parts = date_time_str.split(' ')
                if len(parts) == 2:
                    invoice['date'] = parts[0]
                    invoice['time'] = parts[1]
                del invoice['date_time'] 
        return jsonify(invoices)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/product-analysis', methods=['GET'])
def product_analysis():
    if invoices_df.empty:
        return jsonify({"error": "No data available or failed to load"}), 500
    items_df = invoices_df.explode('items').reset_index(drop=True)
    items_df['item_name'] = items_df['items'].apply(lambda x: x.get('item_name'))
    items_df['quantity'] = items_df['items'].apply(lambda x: x.get('quantity'))
    items_df['amount'] = items_df['items'].apply(lambda x: x.get('amount'))
    product_summary = items_df.groupby('item_name').agg(
        total_quantity=('quantity', 'sum'),
        total_revenue=('amount', 'sum')
    ).reset_index().sort_values(by='total_revenue', ascending=False)
    return jsonify(product_summary.to_dict(orient='records'))

@app.route('/api/reports-analysis', methods=['GET'])
def reports_analysis():
    """
    Provides aggregated data for the reports page, now including item revenue distribution.
    """
    if invoices_df.empty:
        return jsonify({"error": "No data available or failed to load"}), 500
        
    df = invoices_df.copy()
    
    # 1. Weekday Analysis
    df['weekday'] = df['date_time'].dt.day_name()
    weekday_sales = df.groupby('weekday')['total_amount'].sum().round(0)
    vietnamese_days = {
        'Monday': 'Thứ Hai', 'Tuesday': 'Thứ Ba', 'Wednesday': 'Thứ Tư',
        'Thursday': 'Thứ Năm', 'Friday': 'Thứ Sáu', 'Saturday': 'Thứ Bảy', 'Sunday': 'Chủ Nhật'
    }
    weekday_sales = weekday_sales.reindex(vietnamese_days.keys(), fill_value=0)
    weekday_sales.index = weekday_sales.index.map(vietnamese_days)

    # 2. Monthly Analysis
    df['month'] = df['date_time'].dt.strftime('%Y-%m')
    monthly_sales = df.groupby('month')['total_amount'].sum().round(0)
    
    # 3. Item Revenue Distribution (replaces invoice distribution)
    items_df = df.explode('items').reset_index(drop=True)
    items_df['item_name'] = items_df['items'].apply(lambda x: x.get('item_name'))
    items_df['amount'] = items_df['items'].apply(lambda x: x.get('amount'))
    item_distribution = items_df.groupby('item_name')['amount'].sum()

    response = {
        'weekday_sales': weekday_sales.to_dict(),
        'monthly_sales': monthly_sales.to_dict(),
        'item_distribution': item_distribution.to_dict()
    }
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
