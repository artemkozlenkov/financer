import requests
from tkinter import messagebox

def get_exchange_rates():
    try:
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(url)
        data = response.json()
        return data["rates"]
    except Exception:
        messagebox.showerror("Error", "Failed to fetch exchange rates. Using default rates.")
        return {"USD": 1.0, "EUR": 0.85, "CHF": 0.92}

def convert_value(value, from_currency, to_currency, exchange_rates):
    if not from_currency or from_currency not in exchange_rates:
        messagebox.showwarning("Warning", f"Invalid currency '{from_currency}', defaulting to USD.")
        from_currency = "USD"
    if from_currency == to_currency:
        return value
    rate_from = exchange_rates[from_currency]
    rate_to = exchange_rates[to_currency]
    return value * (rate_to / rate_from)