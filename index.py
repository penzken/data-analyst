from flask import Flask, jsonify, json, render_template
from flask_cors import CORS
import pandas as pd
import os
from analyse import analyze_data

app = Flask(__name__, template_folder='templates')
CORS(app)

# --- Helper Functions ---
def find_invoice_path():
    # *** CHANGE: Prioritize loading the new data files first ***
    if os.path.exists('invoices_realistic.json'):
        return 'invoices_realistic.json'
    if os.path.exists('invoices_updated.json'):
        return 'invoices_updated.json'
    if os.path.exists('invoices.json'):
        return 'invoices.json'
    elif os.path.exists('reports/invoices.json'):
        return 'reports/invoices.json'
    else:
        return None

def get_sidebar_html(active_page=''):
    try:
        with open('templates/_sidebar.html', 'r', encoding='utf-8') as f:
            content = f.read()
        placeholders = {'sales': '{{ sales_active }}', 'products': '{{ products_active }}', 'reports': '{{ reports_active }}'}
        for page, placeholder in placeholders.items():
            content = content.replace(placeholder, 'active' if page == active_page else '')
        return content
    except FileNotFoundError:
        return "<p>Error: Sidebar template not found.</p>"

# --- Tải và chuẩn bị dữ liệu ---
def load_and_prepare_data():
    invoice_path = find_invoice_path()
    if not invoice_path:
        print("Lỗi: không tìm thấy tệp hóa đơn JSON!")
        return pd.DataFrame(), {}
    try:
        print(f"Đang tải dữ liệu từ: {invoice_path}")
        df = pd.read_json(invoice_path)
        if 'datetime' not in df.columns:
             print("Lỗi: Cột 'datetime' không có trong file JSON.")
             return pd.DataFrame(), {}
        df['datetime'] = pd.to_datetime(df['datetime'])
        all_analyzed_data = analyze_data(df)
        return df, all_analyzed_data
    except Exception as e:
        print(f"Lỗi khi tải dữ liệu từ {invoice_path}: {e}")
        return pd.DataFrame(), {}

invoices_df, analyzed_data = load_and_prepare_data()

# --- Các Route cho trang HTML ---
@app.route('/', methods=['GET'])
def sales_page():
    sidebar_content = get_sidebar_html(active_page='sales')
    return render_template('index.html', sidebar=sidebar_content)

@app.route('/products', methods=['GET'])
def products_page():
    sidebar_content = get_sidebar_html(active_page='products')
    return render_template('products.html', sidebar=sidebar_content)

@app.route('/reports', methods=['GET'])
def reports_page():
    sidebar_content = get_sidebar_html(active_page='reports')
    return render_template('reports.html', sidebar=sidebar_content)

# --- API Endpoints ---
@app.route('/api/dashboard-data', methods=['GET'])
def get_dashboard_data():
    if not analyzed_data:
        return jsonify({"error": "Không có dữ liệu"}), 500
    response_data = {
        "overall_metrics": analyzed_data.get("overall_metrics", {}),
        "dashboard_data": analyzed_data.get("dashboard_data", {})
    }
    return jsonify(response_data)

@app.route('/api/product-analysis', methods=['GET'])
def product_analysis():
    if not analyzed_data:
        return jsonify({"error": "Không có dữ liệu"}), 500
    return jsonify(analyzed_data.get("product_analysis", []))

@app.route('/api/reports-analysis', methods=['GET'])
def reports_analysis():
    if not analyzed_data:
        return jsonify({"error": "Không có dữ liệu"}), 500
    return jsonify(analyzed_data.get("reports_analysis", {}))

@app.route('/api/product-hierarchy', methods=['GET'])
def product_hierarchy():
    if not analyzed_data:
        return jsonify({"error": "Không có dữ liệu"}), 500
    return jsonify(analyzed_data.get("product_hierarchy", {}))

if __name__ == '__main__':
    app.run(debug=True, port=5000)