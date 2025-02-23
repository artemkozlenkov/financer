import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from currency import get_exchange_rates, convert_value


class AssetTrackerApp:
    COLUMNS = ["Asset Name", "Type", "Value", "Currency", "Location", "Notes"]
    CURRENCIES = ["USD", "EUR", "CHF"]
    ASSET_TYPES = ["Digital", "Cash", "Metal", "Crypto"]

    def __init__(self, root):
        self.root = root
        self.root.title("Asset Tracker")
        self.root.geometry("1000x700")

        self.db = Database()
        self.assets = self.db.load_assets()
        self.exchange_rates = get_exchange_rates()

        self.sort_column = None  # Currently sorted column
        self.sort_reverse = False  # Sorting direction

        self.setup_ui()

    def setup_ui(self):
        # Treeview with sortable columns
        self.tree = ttk.Treeview(self.root, columns=self.COLUMNS, show="headings")
        self.init_tree_columns()
        self.tree.pack(pady=10, fill="both", expand=True)
        self.tree.bind("<Double-1>", self.on_double_click)

        # Currency selection
        self.init_currency_selector()

        # Total label
        self.total_label = tk.Label(self.root, text="Total Net Value: $0.00")
        self.total_label.pack(pady=5)

        # Buttons
        self.init_buttons()

        # Populate table
        self.update_table()

    def init_tree_columns(self):
        for col in self.COLUMNS:
            col_text = f"{col} (USD)" if col == "Value" else col
            self.tree.heading(col, text=col_text,
                              command=lambda c=col: self.sort_by_column(c))
            self.tree.column(col, width=150)

    def init_currency_selector(self):
        currency_frame = tk.Frame(self.root)
        currency_frame.pack(pady=5)
        tk.Label(currency_frame, text="Display Currency:").pack(side="left")
        self.currency_var = tk.StringVar(value="USD")
        currency_selector = ttk.Combobox(
            currency_frame, textvariable=self.currency_var, values=self.CURRENCIES, state="readonly"
        )
        currency_selector.pack(side="left", padx=5)
        self.currency_var.trace("w", lambda *args: self.update_table())

    def init_buttons(self):
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        buttons = [
            ("Add Asset", self.add_asset),
            ("Edit Selected", self.edit_asset),
            ("Remove Selected", self.remove_asset),
            ("↑", self.move_up),
            ("↓", self.move_down),
            ("Quit", self.quit),
        ]
        for text, command in buttons:
            tk.Button(button_frame, text=text, command=command).pack(side="left", padx=5)

    def update_table(self):
        self.clear_table()
        selected_currency = self.currency_var.get()
        total_value = 0

        # Change Value column heading based on selected currency
        self.tree.heading("Value", text=f"Value ({selected_currency})")

        for asset in self.assets:
            converted_value = convert_value(asset["Value"], asset["Currency"], selected_currency, self.exchange_rates)
            total_value += converted_value
            row_data = (
                asset["Asset Name"],
                asset["Type"],
                f"{converted_value:.2f}",
                asset["Currency"],
                asset["Location"],
                asset["Notes"],
            )
            self.tree.insert("", "end", values=row_data)

        # Update total label
        currency_symbol = {"USD": "$", "EUR": "€", "CHF": "CHF"}[selected_currency]
        self.total_label.config(text=f"Total Net Value: {currency_symbol}{total_value:.2f}")

    def clear_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def sort_by_column(self, col):
        # Toggle sorting direction
        if self.sort_column == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column, self.sort_reverse = col, False

        if col == "Value":
            # Sort numerically by converted value
            self.assets.sort(key=lambda x: convert_value(x["Value"], x["Currency"], self.currency_var.get(), self.exchange_rates), reverse=self.sort_reverse)
        else:
            # Sort alphabetically
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

        entries = {}
        for i, label in enumerate(self.COLUMNS):
            tk.Label(window, text=label).grid(row=i, column=0, padx=5, pady=5)

            if label == "Type":
                var = tk.StringVar(value=asset.get("Type") if asset else "Digital")
                entry = ttk.Combobox(window, textvariable=var, values=self.ASSET_TYPES, state="readonly")
            elif label == "Currency":
                var = tk.StringVar(value=asset.get("Currency") if asset else "CHF")
                entry = ttk.Combobox(window, textvariable=var, values=self.CURRENCIES, state="readonly")
            else:
                entry = tk.Entry(window)
                if asset:
                    entry.insert(0, asset[label])

            entry.grid(row=i, column=1, padx=5, pady=5)
            entries[label] = entry

        tk.Button(window, text="Save", command=lambda: save_callback(entries, window, index)).grid(row=len(self.COLUMNS), column=0, columnspan=2, pady=10)

    def save_new_asset(self, entries, window, index):
        try:
            new_asset = {label: entries[label].get() for label in self.COLUMNS}
            if not new_asset["Asset Name"] or not new_asset["Currency"]:
                raise ValueError("Asset Name and Currency cannot be empty!")
    
            new_asset["Value"] = float(new_asset["Value"])  # Convert to float
            self.assets.append(new_asset)
            self.db.save_asset(new_asset)
            self.update_table()
            window.destroy()
    
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")

    def save_edited_asset(self, entries, window, index):
        try:
            updated_asset = {label: entries[label].get() for label in self.COLUMNS}
            if not updated_asset["Asset Name"] or not updated_asset["Currency"]:
                raise ValueError("Asset Name and Currency cannot be empty!")
    
            updated_asset["Value"] = float(updated_asset["Value"])  # Convert to float
            old_asset = self.assets[index]
            self.assets[index] = updated_asset
            self.db.update_asset(old_asset, updated_asset)
            self.update_table()
            window.destroy()
    
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
    

    def process_asset(self, entries, window, new, index=None):
        try:
            asset = {label: entries[label].get() for label in self.COLUMNS}
            if not asset["Asset Name"] or not asset["Currency"]:
                raise ValueError("Asset Name and Currency cannot be empty!")

            asset["Value"] = float(asset["Value"])  # Convert Value to float

            if new:
                self.assets.append(asset)
                self.db.save_asset(asset)
            else:
                old_asset = self.assets[index]
                self.assets[index] = asset
                self.db.update_asset(old_asset, asset)

            self.update_table()
            window.destroy()

        except ValueError as e:
            messagebox.showerror("Error", str(e))

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
        self.reorder_assets(-1)

    def move_down(self):
        self.reorder_assets(1)

    def reorder_assets(self, direction):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an asset to move!")
            return

        index = self.tree.index(selected[0])
        target_index = index + direction
        if 0 <= target_index < len(self.assets):
            self.assets[index], self.assets[target_index] = self.assets[target_index], self.assets[index]
            self.update_table()
            self.tree.selection_set(self.tree.get_children()[target_index])

    def quit(self):
        self.db.close()
        self.root.quit()
