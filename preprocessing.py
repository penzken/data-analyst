import json
from datetime import datetime
from typing import List, Dict, Any, Union
from decimal import Decimal, InvalidOperation

def safe_convert_to_number(value: Any) -> Union[float, int]:
    """Safely convert string/any value to number"""
    if value is None:
        return 0
    
    if isinstance(value, (int, float)):
        return value
    
    if isinstance(value, str):
        # Remove common formatting characters
        cleaned = value.replace(',', '').replace(' ', '').strip()
        
        # Handle empty strings
        if not cleaned:
            return 0
            
        try:
            # Try decimal first for precision
            decimal_val = Decimal(cleaned)
            # Convert to float if it has decimals, int otherwise
            if decimal_val % 1:
                return float(decimal_val)
            else:
                return int(decimal_val)
        except (InvalidOperation, ValueError):
            try:
                # Fallback to float conversion
                return float(cleaned)
            except (ValueError, TypeError):
                return 0
    
    return 0

def extract_date_time(datetime_str: str) -> Dict[str, str]:
    """Extract date and time components from datetime string"""
    if not datetime_str:
        return {"date": "", "time": "", "hour": "", "time_period": ""}
    
    try:
        # Try different datetime formats
        formats = [
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%d/%m/%Y %H:%M:%S",
            "%d-%m-%Y %H:%M:%S"
        ]
        
        dt = None
        for fmt in formats:
            try:
                dt = datetime.strptime(datetime_str.split('Z')[0], fmt)
                break
            except ValueError:
                continue
        
        if dt is None:
            # If all formats fail, try to extract manually
            if 'T' in datetime_str:
                date_part, time_part = datetime_str.split('T')[0], datetime_str.split('T')[1].split('Z')[0]
            elif ' ' in datetime_str:
                parts = datetime_str.split(' ')
                date_part, time_part = parts[0], parts[1] if len(parts) > 1 else "00:00:00"
            else:
                return {"date": datetime_str, "time": "00:00:00", "hour": "0", "time_period": "Unknown"}
            
            hour = time_part.split(':')[0] if ':' in time_part else "0"
        else:
            date_part = dt.strftime("%Y-%m-%d")
            time_part = dt.strftime("%H:%M:%S")
            hour = str(dt.hour)
        
        # Determine time period
        hour_int = int(hour) if hour.isdigit() else 0
        if 6 <= hour_int < 12:
            time_period = "Morning (6-12)"
        elif 12 <= hour_int < 18:
            time_period = "Afternoon (12-18)"
        elif 18 <= hour_int < 22:
            time_period = "Evening (18-22)"
        else:
            time_period = "Night (22-6)"
        
        return {
            "date": date_part,
            "time": time_part,
            "hour": hour,
            "time_period": time_period
        }
    except Exception:
        return {"date": "", "time": "", "hour": "", "time_period": ""}

def _collect_orders(payload: Any) -> List[Dict[str, Any]]:
    """
    Recursively traverse to collect all order objects (dict with 'products' key).
    Returns list of order dictionaries.
    """
    results = []
    if isinstance(payload, dict):
        # If it's an order itself
        if 'products' in payload and isinstance(payload.get('products'), list):
            results.append(payload)
        # Traverse child values
        for v in payload.values():
            results.extend(_collect_orders(v))
    elif isinstance(payload, list):
        for item in payload:
            results.extend(_collect_orders(item))
    return results

def preprocessing_data(payload: Any) -> List[Dict[str, Any]]:
    """Process payload and return list of rows with required fields including time components"""
    rows = []
    orders = _collect_orders(payload)
    
    for order in orders:
        order_id = order.get('id')
        calc_total = order.get('calcTotalMoney')
        created_dt = order.get('createdDateTime')
        products = order.get('products') or []
        
        # Extract date and time components
        time_components = extract_date_time(created_dt or '')
        
        if not isinstance(products, list):
            products = []
            
        for product in products:
            row_data = {
                'orderId': order_id,
                'calcTotalMoney': calc_total,
                'productName': product.get('productName'),
                'price': product.get('price'),
                'quantity': product.get('quantity'),
                'createdDateTime': created_dt,
                # Add separated time components
                'date': time_components['date'],
                'time': time_components['time'],
                'hour': time_components['hour'],
                'time_period': time_components['time_period']
            }
            rows.append(row_data)
    
    return rows
