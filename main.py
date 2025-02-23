import tkinter as tk
from tkinter import ttk, messagebox
import requests

class AssetTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Asset Tracker")
        self.root.geometry("900x700")

        # Initial data
        self.assets = [
            {"Asset Name": "Laptop", "Type": "Electronics", "Value": 1200, "Location": "Home Office", "Notes": "Dell XPS 13"},
            {"Asset Name": "Savings Account", "Type": "Financial", "Value": 15000, "Location": "Bank of America", "Notes": "Emergency Fund"},
            {"Asset Name": "Car", "Type": "Vehicle", "Value": 25000, "Location": "Garage", "Notes": "Toyota Camry"},
            {"Asset Name": "Gold Necklace", "Type": "Jewelry", "Value": 800, "Location": "Safe", "Notes": "Gift from Mom"}
        ]

        # Currency settings
        self.base_currency = "USD"
        self.exchange_rates = self.get_exchange_rates()

        # Create Treeview (table)
        self.tree = ttk.Treeview(root, columns=("Asset Name", "Type", "Value", "Location", "Notes"), show="headings")
        self.tree.pack(pady=10, fill="both", expand=True)

        # Set column headings
        for col in ("Asset Name", "Type", "Value", "Location", "Notes"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=180)

        # Currency selection
        currency_frame = tk.Frame(root)
        currency_frame.pack(pady=5)
        tk.Label(currency_frame, text="Display Currency:").pack(side="left")
        self.currency_var = tk.StringVar(value="USD")
        currency_menu = ttk.Combobox(currency_frame, textvariable=self.currency_var, values=["USD", "EUR", "CHF"], state="readonly")
        currency_menu.pack(side="left", padx=5)
        currency_menu.bind("<<ComboboxSelected>>", lambda e: self.update_table())

        # Total Net Value Label
        self.total_label = tk.Label(root, text="Total Net Value: $0.00")
        self.total_label.pack(pady=5)

        # Populate initial data
        self.update_table()

        # Buttons
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Add Asset", command=self.add_asset).pack(side="left", padx=5)
        tk.Button(button_frame, text="Remove Selected", command=self.remove_asset).pack(side="left", padx=5)
        tk.Button(button_frame, text="Quit", command=root.quit).pack(side="left", padx=5)

    def get_exchange_rates(self):
        try:
            # Using exchangerate-api.com (free tier available, requires API key for production)
            url = "https://api.exchangerate-api.com/v4/latest/USD"
            response = requests.get(url)
            data = response.json()
            return data["rates"]
        except Exception as e:
            messagebox.showerror("Error", "Failed to fetch exchange rates. Using default rates.")
            return {"USD": 1.0, "EUR": 0.85, "CHF": 0.92}  # Fallback rates

    def convert_value(self, value, from_currency="USD", to_currency="USD"):
        if from_currency == to_currency:
            return value
        rate_from = self.exchange_rates[from_currency]
        rate_to = self.exchange_rates[to_currency]
        return value / rate_from * rate_to

    def update_table(self):
        # Clear existing entries
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Insert all assets with converted values
        total_value = 0
        selected_currency = self.currency_var.get()
        for asset in self.assets:
            converted_value = self.convert_value(asset["Value"], "USD", selected_currency)
            total_value += converted_value
            self.tree.insert("", "end", values=(
                asset["Asset Name"], asset["Type"], f"{converted_value:.2f}", asset["Location"], asset["Notes"]
            ))

        # Update total net value
        currency_symbol = {"USD": "$", "EUR": "€", "CHF": "CHF"}[selected_currency]
        self.total_label.config(text=f"Total Net Value: {currency_symbol}{total_value:.2f}")

    def add_asset(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("Add New Asset")
        add_window.geometry("300x300")

        labels = ["Asset Name", "Type", "Value", "Location", "Notes"]
        entries = {}

        for i, label in enumerate(labels):
            tk.Label(add_window, text=label).grid(row=i, column=0, padx=5, pady=5)
            entry = tk.Entry(add_window)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries[label] = entry

        def save_asset():
            new_asset = {label: entries[label].get() for label in labels}
            if new_asset["Asset Name"]:
                try:
                    new_asset["Value"] = float(new_asset["Value"])
                    self.assets.append(new_asset)
                    self.update_table()
                    add_window.destroy()
                except ValueError:
                    messagebox.showerror("Error", "Value must be a number!")
            else:
                messagebox.showerror("Error", "Asset Name cannot be empty!")

        tk.Button(add_window, text="Save", command=save_asset).grid(row=len(labels), column=0, columnspan=2, pady=10)

    def remove_asset(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an asset to remove!")
            return

        confirm = messagebox.askyesno("Confirm", "Are you sure you want to remove the selected asset?")
        if confirm:
            selected_index = self.tree.index(selected[0])
            self.assets.pop(selected_index)
            self.update_table()

if __name__ == "__main__":
    root = tk.Tk()
    app = AssetTrackerApp(root)
    root.mainloop()