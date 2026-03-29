import tkinter as tk
from tkinter import messagebox
import json
import os
from datetime import datetime

# --FILES--

INVENTORY_FILE = "inventory.json"
UTANG_FILE = "utang.json"
SALES_FILE = "sales.json"

def load_data(file):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return []

def save_data(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

# --MAIN APP--

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("SariSmart Store System")
        self.geometry("700x500")

        self.current_frame = None
        self.show_frame(MainMenu)

    def show_frame(self, frame):
        if self.current_frame:
            self.current_frame.destroy()

        self.current_frame = frame(self)
        self.current_frame.pack(fill="both", expand=True)

# ---MAIN MENU--

class MainMenu(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        tk.Label(self, text="SariSmart System", font=("Arial",20,"bold")).pack(pady=20)

        tk.Button(self,text="POS",width=25,
                  command=lambda: master.show_frame(POS)).pack(pady=5)

        tk.Button(self,text="Inventory Manager",width=25,
                  command=lambda: master.show_frame(Inventory)).pack(pady=5)

        tk.Button(self,text="Utang Tracker",width=25,
                  command=lambda: master.show_frame(Utang)).pack(pady=5)

        tk.Button(self,text="Sales Analytics",width=25,
                  command=lambda: master.show_frame(Analytics)).pack(pady=5)

        
# ---INVENTORY---

class Inventory(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        tk.Label(self,text="Inventory Manager",font=("Arial",16,"bold")).pack()

        self.name = tk.Entry(self)
        self.name.insert(0, "Name")
        self.name.pack()

        self.price = tk.Entry(self)
        self.price.insert(0,"Selling Price")
        self.price.pack()

        self.stock = tk.Entry(self)
        self.stock.insert(0,"Stock")
        self.stock.pack()

        tk.Button(self,text="Add Product",command=self.add_product).pack(pady=5)

        self.listbox = tk.Listbox(self,width=70)
        self.listbox.pack(pady=10)

        tk.Button(self,text="Delete Product",command=self.delete_product).pack()

        tk.Button(self,text="Back",command=lambda: master.show_frame(MainMenu)).pack(pady=10)

        self.refresh()

    def add_product(self):
        inventory = load_data(INVENTORY_FILE)

        product = {
            "name": self.name.get(),
            "price": float(self.price.get()),
            "stock": int(self.stock.get())
        }

        inventory.append(product)
        save_data(INVENTORY_FILE,inventory)

        self.refresh()

    def delete_product(self):
        inventory = load_data(INVENTORY_FILE)

        confirm = messagebox.askyesno("Confirm", "Delete product?")

        selected = self.listbox.curselection()
        if selected:
            inventory.pop(selected[0])
            save_data(INVENTORY_FILE,inventory)

        self.refresh()

    def refresh(self):
        self.listbox.delete(0,tk.END)
        inventory = load_data(INVENTORY_FILE)

        for item in inventory:
            self.listbox.insert(tk.END,
            f"{item['name']} | ₱{item['price']} | Stock:{item['stock']}")

# ---POS---

class POS(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        tk.Label(self,text="Point of Sale",font=("Arial",16,"bold")).pack()

        self.product = tk.Entry(self)
        self.product.insert(0,"Product Name")
        self.product.pack()

        self.qty = tk.Entry(self)
        self.qty.insert(0,"Quantity")
        self.qty.pack()

        self.customer = tk.Entry(self)
        self.customer.pack()

        tk.Button(self,text="Process Sale",command=self.sell).pack(pady=5)

        tk.Button(self,text="Back",command=lambda: master.show_frame(MainMenu)).pack()

    def sell(self):
        inventory = load_data(INVENTORY_FILE)
        sales = load_data(SALES_FILE)
        utang = load_data(UTANG_FILE)

        name = self.product.get()
        qty = int(self.qty.get())
        customer = self.customer.get()

        for item in inventory:

            if item["name"].lower() == name.lower():

                if item["stock"] < qty:
                    messagebox.showerror("Error","Not enough stock")
                    return

                item["stock"] -= qty

                total = qty * item["price"]

                sale = {
                    "product": name,
                    "qty": qty,
                    "total": total,
                    "date": str(datetime.now().date())
                }

                sales.append(sale)

                if customer != "":
                    utang.append({
                        "customer": customer,
                        "amount": total,
                        "date": str(datetime.now().date())
                    })

                save_data(INVENTORY_FILE,inventory)
                save_data(SALES_FILE,sales)
                save_data(UTANG_FILE,utang)

                messagebox.showinfo("Sale Complete",f"Total ₱{total}")
                return

        messagebox.showerror("Error","Product not found")

# ---UTANG TRACKER---

class Utang(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        tk.Label(self,text="Utang Tracker",font=("Arial",16,"bold")).pack()

        self.listbox = tk.Listbox(self,width=70)
        self.listbox.pack(pady=10)

        tk.Button(self,text="Mark as Paid",command=self.pay).pack()

        tk.Button(self,text="Back",command=lambda: master.show_frame(MainMenu)).pack(pady=10)

        self.refresh()

    def refresh(self):
        self.listbox.delete(0,tk.END)

        utang = load_data(UTANG_FILE)

        for u in utang:
            self.listbox.insert(tk.END,
            f"{u['customer']} owes ₱{u['amount']} ({u['date']})")

    def pay(self):
        utang = load_data(UTANG_FILE)

        selected = self.listbox.curselection()

        if selected:
            utang.pop(selected[0])
            save_data(UTANG_FILE,utang)

        self.refresh()

# ---ANALYTICS---

class Analytics(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        tk.Label(self,text="Sales Analytics",font=("Arial",16,"bold")).pack()

        self.total_label = tk.Label(self, font=("Arial",14))
        self.total_label.pack(pady=10)

        self.best_label = tk.Label(self)
        self.best_label.pack()

        tk.Button(self,text="Reset Sales",command=self.reset_sales).pack(pady=10)

        tk.Button(self,text="Back",
                  command=lambda: master.show_frame(MainMenu)).pack(pady=20)

        self.update_display()

    def update_display(self):
        sales = load_data(SALES_FILE)

        total = sum(s["total"] for s in sales)
        self.total_label.config(text=f"Total Sales: ₱{total}")

        products = {}

        for s in sales:
            products[s["product"]] = products.get(s["product"],0) + s["qty"]

        if products:
            best = max(products, key=products.get)
            self.best_label.config(text=f"Best Seller: {best}")
        else:
            self.best_label.config(text="Best Seller: None")

    def reset_sales(self):
        confirm = messagebox.askyesno("Confirm", "Reset all sales to zero?")

        if confirm:
            save_data(SALES_FILE, [])
            self.update_display()

    



if __name__ == "__main__":
    app = App()
    app.mainloop()