import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from currency import get_exchange_rates, convert_value

class AssetTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Asset Tracker")
        self.root.geometry("1000x700")

        self.db = Database()
        self.assets = self.db.load_assets()
        self.exchange_rates = get_exchange_rates()
        self.sort_column = None  # Track current sort column
        self.sort_reverse = False  # Track sort direction

        self.setup_ui()

    def setup_ui(self):
        # Treeview with sortable columns
        self.tree = ttk.Treeview(self.root, columns=("Asset Name", "Type", "Value", "Currency", "Location", "Notes"), show="headings")
        for col in ("Asset Name", "Type", "Value", "Currency", "Location", "Notes"):
            self.tree.heading(col, text=col if col != "Value" else f"Value (USD)", command=lambda c=col: self.sort_by_column(c))
            self.tree.column(col, width=150)
        self.tree.pack(pady=10, fill="both", expand=True)
        self.tree.bind("<Double-1>", self.on_double_click)

        # Currency selection
        currency_frame = tk.Frame(self.root)
        currency_frame.pack(pady=5)
        tk.Label(currency_frame, text="Display Currency:").pack(side="left")
        self.currency_var = tk.StringVar(value="USD")
        ttk.Combobox(currency_frame, textvariable=self.currency_var, values=["USD", "EUR", "CHF"], state="readonly").pack(side="left", padx=5)
        self.currency_var.trace("w", lambda *args: self.update_table())

        # Total label
        self.total_label = tk.Label(self.root, text="Total Net Value: $0.00")
        self.total_label.pack(pady=5)

        # Buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Add Asset", command=self.add_asset).pack(side="left", padx=5)
        tk.Button(button_frame, text="Edit Selected", command=self.edit_asset).pack(side="left", padx=5)
        tk.Button(button_frame, text="Remove Selected", command=self.remove_asset).pack(side="left", padx=5)
        tk.Button(button_frame, text="↑", command=self.move_up).pack(side="left", padx=5)  # Up arrow
        tk.Button(button_frame, text="↓", command=self.move_down).pack(side="left", padx=5)  # Down arrow
        tk.Button(button_frame, text="Quit", command=self.quit).pack(side="left", padx=5)

        self.update_table()

    def update_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        selected_currency = self.currency_var.get()
        self.tree.heading("Value", text=f"Value ({selected_currency})")
        total_value = 0
        for asset in self.assets:
            converted_value = convert_value(asset["Value"], asset["Currency"], selected_currency, self.exchange_rates)
            total_value += converted_value
            self.tree.insert("", "end", values=(asset["Asset Name"], asset["Type"], f"{converted_value:.2f}", asset["Currency"], asset["Location"], asset["Notes"]))
        
        currency_symbol = {"USD": "$", "EUR": "€", "CHF": "CHF"}[selected_currency]
        self.total_label.config(text=f"Total Net Value: {currency_symbol}{total_value:.2f}")

    def sort_by_column(self, col):
        # Toggle sort direction if clicking the same column, otherwise reset to ascending
        if self.sort_column == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_reverse = False
            self.sort_column = col

        # Sort assets
        if col == "Value":
            self.assets.sort(key=lambda x: convert_value(x["Value"], x["Currency"], self.currency_var.get(), self.exchange_rates), reverse=self.sort_reverse)
        else:
            self.assets.sort(key=lambda x: x[col], reverse=self.sort_reverse)
        
        self.update_table()

    def on_double_click(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            index = self.tree.index(item)
            self.edit_asset(index=index)

    def add_asset(self):
        self.create_asset_window("Add New Asset", self.save_new_asset)

    def edit_asset(self, index=None):
        if index is None:
            selected = self.tree.selection()
            if not selected:
                messagebox.showwarning("Warning", "Please select an asset to edit!")
                return
            index = self.tree.index(selected[0])
        self.create_asset_window("Edit Asset", self.save_edited_asset, self.assets[index], index)

    def create_asset_window(self, title, save_callback, asset=None, index=None):
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry("350x350")

        labels = ["Asset Name", "Type", "Value", "Currency", "Location", "Notes"]
        entries = {}
        type_options = ["Digital", "Cash", "Metal", "Crypto"]
        currency_options = ["USD", "EUR", "CHF"]

        for i, label in enumerate(labels):
            tk.Label(window, text=label).grid(row=i, column=0, padx=5, pady=5)
            if label == "Type":
                var = tk.StringVar(value=asset["Type"] if asset else "Digital")
                entry = ttk.Combobox(window, textvariable=var, values=type_options, state="readonly")
            elif label == "Currency":
                var = tk.StringVar(value=asset["Currency"] if asset else "CHF")
                entry = ttk.Combobox(window, textvariable=var, values=currency_options, state="readonly")
            else:
                entry = tk.Entry(window)
                if asset:
                    entry.insert(0, asset[label])
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries[label] = entry

        tk.Button(window, text="Save", command=lambda: save_callback(entries, window, index)).grid(row=len(labels), column=0, columnspan=2, pady=10)

    def save_new_asset(self, entries, window):
        new_asset = {label: entries[label].get() for label in entries}
        if not new_asset["Asset Name"] or not new_asset["Currency"]:
            messagebox.showerror("Error", "Asset Name and Currency cannot be empty!")
            return
        try:
            new_asset["Value"] = float(new_asset["Value"])
            self.assets.append(new_asset)
            self.db.save_asset(new_asset)
            self.update_table()
            window.destroy()
        except ValueError:
            messagebox.showerror("Error", "Value must be a number!")

    def save_edited_asset(self, entries, window, index):
        new_asset = {label: entries[label].get() for label in entries}
        if not new_asset["Asset Name"] or not new_asset["Currency"]:
            messagebox.showerror("Error", "Asset Name and Currency cannot be empty!")
            return
        try:
            new_asset["Value"] = float(new_asset["Value"])
            old_asset = self.assets[index]
            self.assets[index] = new_asset
            self.db.update_asset(old_asset, new_asset)
            self.update_table()
            window.destroy()
        except ValueError:
            messagebox.showerror("Error", "Value must be a number!")

    def remove_asset(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an asset to remove!")
            return
        if messagebox.askyesno("Confirm", "Are you sure you want to remove the selected asset?"):
            index = self.tree.index(selected[0])
            asset = self.assets.pop(index)
            self.db.delete_asset(asset)
            self.update_table()

    def move_up(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an asset to move!")
            return
        index = self.tree.index(selected[0])
        if index > 0:
            self.assets[index], self.assets[index - 1] = self.assets[index - 1], self.assets[index]
            self.update_table()
            self.tree.selection_set(self.tree.get_children()[index - 1])

    def move_down(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an asset to move!")
            return
        index = self.tree.index(selected[0])
        if index < len(self.assets) - 1:
            self.assets[index], self.assets[index + 1] = self.assets[index + 1], self.assets[index]
            self.update_table()
            self.tree.selection_set(self.tree.get_children()[index + 1])

    def quit(self):
        self.db.close()
        self.root.quit()