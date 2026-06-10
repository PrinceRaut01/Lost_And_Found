# --- Tkinter imports ---
import os
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

# --- Utility: Center window on screen ---
def center_window(win, width=1100, height=600):
    win.update_idletasks()
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")
# Database connection
from db_connection import get_db_connection, get_resource_path

root = Tk()
center_window(root, 1100, 600)
root.title("Lost & Found - Welcome User")
root.minsize(1100, 600)
root.resizable(True, True)
root.state("zoomed")
root.configure(bg="white")  # Set initial background to light mode

icon_path = get_resource_path(os.path.join('assets', 'icon.ico'))
if os.path.exists(icon_path):
    try:
        root.iconbitmap(default=icon_path)
    except Exception:
        pass

# Global variables for window management
lost_window = None
found_window = None
search_window = None
dark_mode = False

# Advanced Search Window
def advanced_search():
    global search_window
    if search_window is not None and search_window.winfo_exists():
        search_window.lift()
        return    
    search_window = Toplevel()
    search_window.title("Advanced Search")
    center_window(search_window, 1100, 600)
    search_window.minsize(1100, 600)
    search_window.resizable(True, True)
    
    # Set background based on current mode
    window_bg = "#2b2b2b" if dark_mode else "white"
    text_color = "white" if dark_mode else "black"
    search_window.configure(bg=window_bg)

    def on_closing():
        global search_window
        search_window.destroy()
        search_window = None
    search_window.protocol("WM_DELETE_WINDOW", on_closing)

    # Heading
    lbl_heading = Label(search_window, text="Advanced Search", font=("Arial", 20, "bold"), bg=window_bg, fg=text_color)
    lbl_heading.place(x=60, y=20)

    # Search Term
    lbl_term = Label(search_window, text="Search Term:", font=("Arial", 12), bg=window_bg, fg=text_color)
    lbl_term.place(x=30, y=70)
    entry_term = Entry(search_window, width=22, font=("Arial", 12), bd=1, relief="solid")
    entry_term.place(x=140, y=70)

    # Item Type
    lbl_type = Label(search_window, text="Item Type:", font=("Arial", 12), bg=window_bg, fg=text_color)
    lbl_type.place(x=30, y=110)
    type_var = StringVar(value="All")
    rb_all = Radiobutton(search_window, text="All", variable=type_var, value="All", font=("Arial", 11), bg=window_bg, fg=text_color)
    rb_all.place(x=130, y=110)
    rb_lost = Radiobutton(search_window, text="Lost", variable=type_var, value="Lost", font=("Arial", 11), bg=window_bg, fg=text_color)
    rb_lost.place(x=190, y=110)
    rb_found = Radiobutton(search_window, text="Found", variable=type_var, value="Found", font=("Arial", 11), bg=window_bg, fg=text_color)
    rb_found.place(x=260, y=110)

    # Category
    lbl_category = Label(search_window, text="Category:", font=("Arial", 12), bg=window_bg, fg=text_color)
    lbl_category.place(x=30, y=150)
    category_var = StringVar()
    combo_category = ttk.Combobox(search_window, textvariable=category_var, font=("Arial", 12), state="readonly", width=18)
    combo_category['values'] = ("All", "Electronics", "Bags", "Books", "Personal Items", "Keys", "Clothing", "Jewelry", "Documents", "Sports Equipment", "Stationery", "Accessories", "Mobile Phones", "Laptops", "Wallets", "Shoes", "Umbrellas", "Water Bottles", "Glasses", "Watches", "Headphones", "Chargers", "USB Drives", "Cards", "Other")
    combo_category.current(0)
    combo_category.place(x=140, y=150)

    # Button commands
    def do_search():
        search_term = entry_term.get().strip()
        item_type = type_var.get()
        category = category_var.get()
        
        # Check if search term is empty
        if not search_term:
            messagebox.showerror("Error", "Please enter a search term!")
            return
        
        # Clear main table
        for item in tree.get_children():
            tree.delete(item)
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            results = []
            # Build queries
            if item_type in ("Lost", "All"):
                sql = "SELECT id, item_name, category, 'Lost' as type, date_lost as date, location_lost as location, 'active' as status FROM lost_items WHERE (item_name LIKE ? OR category LIKE ? OR location_lost LIKE ? OR description LIKE ?)"
                params = [f'%{search_term}%'] * 4
                if category != "All":
                    sql += " AND category = ?"
                    params.append(category)
                cursor.execute(sql, params)
                results += cursor.fetchall()
            if item_type in ("Found", "All"):
                sql = "SELECT id, item_name, category, 'Found' as type, date_found as date, location_found as location, 'active' as status FROM found_items WHERE (item_name LIKE ? OR category LIKE ? OR location_found LIKE ? OR description LIKE ?)"
                params = [f'%{search_term}%'] * 4
                if category != "All":
                    sql += " AND category = ?"
                    params.append(category)
                cursor.execute(sql, params)
                results += cursor.fetchall()
            conn.close()
            if not results:
                messagebox.showinfo("Search Results", "No items found matching your search.")
            else:
                display_id = 1
                for row in results:
                    new_row = (display_id,) + row[1:]
                    tree.insert('', 'end', values=new_row)
                    display_id += 1
            on_closing()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    # Buttons
    btn_search = Button(search_window, text="Search", font=("Arial", 12, "bold"), bg="#21759b", fg="white", width=10, command=do_search)
    btn_search.place(x=70, y=220)
    btn_cancel = Button(search_window, text="Cancel", font=("Arial", 12, "bold"), bg="#c0392b", fg="white", width=10, command=on_closing)
    btn_cancel.place(x=210, y=220)


# Function to handle lost item reporting
def report_lost_item():
    global lost_window
    
    # Check if window is already open
    if lost_window is not None and lost_window.winfo_exists():
        lost_window.lift()  # Bring existing window to front
        return
    
    lost_window = Toplevel()  # --> Create new window
    lost_window.title("Report Lost Item")
    center_window(lost_window, 1100, 600)
    
    # Set background based on current mode
    window_bg = "#2b2b2b" if dark_mode else "white"
    text_color = "white" if dark_mode else "black"
    lost_window.configure(bg=window_bg)
    lost_window.minsize(1100, 600)
    lost_window.resizable(True, True)
    
    # Handle window close event to reset the global variable
    def on_closing():
        global lost_window
        lost_window.destroy()
        lost_window = None

    lost_window.protocol("WM_DELETE_WINDOW", on_closing)

    # Main heading
    lbl_registration = Label(lost_window, text="Report Lost Item", font=("Arial", 18, "bold"), bg="#FF5722", fg="white")
    lbl_registration.place(x=200, y=20)

    # Item Name
    lbl_item_name = Label(lost_window, text="Item Name:", bg=window_bg, font=("Arial", 12), fg=text_color)
    lbl_item_name.place(x=50, y=80)
    item_name = Entry(lost_window, width=35, font=("Arial", 11), bd=2, relief="raised")
    item_name.place(x=180, y=80)

    # Item Category
    lbl_item_category = Label(lost_window, text="Item Category:", bg=window_bg, font=("Arial", 12), fg=text_color)
    lbl_item_category.place(x=50, y=120)
    item_category = Entry(lost_window, width=35, font=("Arial", 11), bd=2, relief="raised")
    item_category.place(x=180, y=120)

    # Date Lost
    lbl_date_lost = Label(lost_window, text="Date Lost:", bg=window_bg, font=("Arial", 12), fg=text_color)
    lbl_date_lost.place(x=50, y=160)
    date_lost = Entry(lost_window, width=35, font=("Arial", 11), bd=2, relief="raised")
    date_lost.place(x=180, y=160)

    # Location Lost
    lbl_location_lost = Label(lost_window, text="Location Lost:", bg=window_bg, font=("Arial", 12), fg=text_color)
    lbl_location_lost.place(x=50, y=200)
    location_lost = Entry(lost_window, width=35, font=("Arial", 11), bd=2, relief="raised")
    location_lost.place(x=180, y=200)

    # Description
    lbl_description = Label(lost_window, text="Description:", bg=window_bg, font=("Arial", 12), fg=text_color)
    lbl_description.place(x=50, y=240)
    description = Text(lost_window, width=35, height=8, font=("Arial", 11), bd=2, relief="raised")
    description.place(x=180, y=240)

    # Submit button with functionality
    def submit_lost_item():
        # Get all field values
        name = item_name.get().strip()
        category = item_category.get().strip()
        date = date_lost.get().strip()
        location = location_lost.get().strip()
        desc = description.get("1.0", END).strip()
        
        # Basic validation
        if not all([name, category, date, location, desc]):
            messagebox.showerror("Error", "Please fill all fields!", parent=lost_window)
            return
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO lost_items (item_name, category, date_lost, location_lost, description, contact_info) VALUES (?, ?, ?, ?, ?, ?)",
                (name, category, date, location, desc, ''))
            conn.commit()
            conn.close()
            # Show notification, then clear fields and close window only after user clicks OK
            messagebox.showinfo("Success", "Lost item report submitted successfully!", parent=lost_window)
            item_name.delete(0, END)
            item_category.delete(0, END)
            date_lost.delete(0, END)
            location_lost.delete(0, END)
            description.delete("1.0", END)
            on_closing()
        except Exception as e:
            messagebox.showerror("Database Error", str(e), parent=lost_window)

    submit_button = Button(lost_window, text="Submit Report", width=12, font=("Arial", 12), bg="#4CAF50", fg="white", bd=2, relief="raised", command=submit_lost_item)
    submit_button.place(x=200, y=420)
    
    cancel_button = Button(lost_window, text="Cancel", width=12, font=("Arial", 12), bg="#f44336", fg="white", bd=2, relief="raised", command=on_closing)
    cancel_button.place(x=340, y=420)


def report_found_item():

    global found_window

    # Check if window is already open
    if found_window is not None and found_window.winfo_exists():
        found_window.lift()  # Bring existing window to front
        return

    found_window = Toplevel()  # --> Create new window
    found_window.title("Report Found Item")
    center_window(found_window, 1100, 600)
    # Set background based on current mode
    window_bg = "#2b2b2b" if dark_mode else "white"
    text_color = "white" if dark_mode else "black"
    found_window.configure(bg=window_bg)
    found_window.minsize(1100, 600)
    found_window.resizable(True, True)

    # Handle window close event to reset the global variable
    def on_closing():
        global found_window
        found_window.destroy()
        found_window = None

    found_window.protocol("WM_DELETE_WINDOW", on_closing)

    # Main heading
    lbl_registration = Label(found_window, text="Report Found Item", font=("Arial", 18, "bold"), bg="#4CAF50", fg="white")
    lbl_registration.place(x=200, y=20)

    # Item Name
    lbl_item_name = Label(found_window, text="Item Name:", bg=window_bg, font=("Arial", 12), fg=text_color)
    lbl_item_name.place(x=50, y=80)
    item_name = Entry(found_window, width=35, font=("Arial", 11), bd=2, relief="raised")
    item_name.place(x=180, y=80)

    # Item Category
    lbl_item_category = Label(found_window, text="Item Category:", bg=window_bg, font=("Arial", 12), fg=text_color)
    lbl_item_category.place(x=50, y=120)
    item_category = Entry(found_window, width=35, font=("Arial", 11), bd=2, relief="raised")
    item_category.place(x=180, y=120)

    # Date Found
    lbl_date_found = Label(found_window, text="Date Found:", bg=window_bg, font=("Arial", 12), fg=text_color)
    lbl_date_found.place(x=50, y=160)
    date_found = Entry(found_window, width=35, font=("Arial", 11), bd=2, relief="raised")
    date_found.place(x=180, y=160)

    # Location Found
    lbl_location_found = Label(found_window, text="Location Found:", bg=window_bg, font=("Arial", 12), fg=text_color)
    lbl_location_found.place(x=50, y=200)
    location_found = Entry(found_window, width=35, font=("Arial", 11), bd=2, relief="raised")
    location_found.place(x=180, y=200)

    # Description
    lbl_description = Label(found_window, text="Description:", bg=window_bg, font=("Arial", 12), fg=text_color)
    lbl_description.place(x=50, y=240)
    description = Text(found_window, width=35, height=8, font=("Arial", 11), bd=2, relief="raised")
    description.place(x=180, y=240)

    # Submit button with functionality
    def submit_found_item():
        # Get all field values
        name = item_name.get().strip()
        category = item_category.get().strip()
        date = date_found.get().strip()
        location = location_found.get().strip()
        desc = description.get("1.0", END).strip()
        
        # Basic validation
        if not all([name, category, date, location, desc]):
            messagebox.showerror("Error", "Please fill all fields!", parent=found_window)
            return
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO found_items (item_name, category, date_found, location_found, description, contact_info) VALUES (?, ?, ?, ?, ?, ?)",
                (name, category, date, location, desc, ''))
            conn.commit()
            conn.close()
            # Show notification, then clear fields and close window only after user clicks OK
            messagebox.showinfo("Success", "Found item report submitted successfully!", parent=found_window)
            item_name.delete(0, END)
            item_category.delete(0, END)
            date_found.delete(0, END)
            location_found.delete(0, END)
            description.delete("1.0", END)
            on_closing()
        except Exception as e:
            messagebox.showerror("Database Error", str(e), parent=found_window)

    submit_button = Button(found_window, text="Submit Report", width=12, font=("Arial", 12), 
                          bg="#4CAF50", fg="white", bd=2, relief="raised", command=submit_found_item)
    submit_button.place(x=200, y=420)
    
    cancel_button = Button(found_window, text="Cancel", width=12, font=("Arial", 12), 
                          bg="#f44336", fg="white", bd=2, relief="raised", command=on_closing)
    cancel_button.place(x=340, y=420)


# Function for main search bar
def quick_search():
    search_term = search_entry.get().strip()
   # Clear table
    for item in tree.get_children():
        tree.delete(item) 
    # Check if search term is empty
    if not search_term:
        messagebox.showerror("Error", "Please enter a search term!")
        return
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Search lost items
        cursor.execute("SELECT id, item_name, category, 'Lost' as type, date_lost as date, location_lost as location, 'active' as status FROM lost_items WHERE item_name LIKE ? OR category LIKE ? OR location_lost LIKE ? OR description LIKE ?",
            (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        lost_results = cursor.fetchall()
        cursor.execute("SELECT id, item_name, category, 'Found' as type, date_found as date, location_found as location, 'active' as status FROM found_items WHERE item_name LIKE ? OR category LIKE ? OR location_found LIKE ? OR description LIKE ?",
            (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        found_results = cursor.fetchall()
        conn.close()
        results = lost_results + found_results
        if not results:
            messagebox.showinfo("Search Results", "No items found matching your search.")
        else:
            display_id = 1
            for row in results:
                new_row = (display_id,) + row[1:]
                tree.insert('', 'end', values=new_row)
                display_id += 1
    except Exception as e:
        messagebox.showerror("Database Error", str(e))

# Function for show all items
def show_all_items():
    # Clear table
    for item in tree.get_children():
        tree.delete(item)
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Fetch lost items
        cursor.execute("SELECT id, item_name, category, 'Lost' as type, date_lost as date, location_lost as location, 'active' as status FROM lost_items")
        lost_items = cursor.fetchall()
        # Fetch found items
        cursor.execute("SELECT id, item_name, category, 'Found' as type, date_found as date, location_found as location, 'active' as status FROM found_items")
        found_items = cursor.fetchall()
        conn.close()
        # Insert all items into the table
        all_items = lost_items + found_items
        display_id = 1
        for row in all_items:
            new_row = (display_id,) + row[1:]
            tree.insert('', 'end', values=new_row)
            display_id += 1
    except Exception as e:
        messagebox.showerror("Database Error", str(e))


# Header Frame
header_frame = Frame(root, bg="#4A9EFF", height=80)
header_frame.pack(fill=X)
header_frame.pack_propagate(False)

# Header Label
header_label = Label(header_frame, text="Lost & Found Desk - Welcome User", 
                    font=("Arial", 20, "bold"), bg="#4A9EFF", fg="white")
header_label.pack(side=LEFT, pady=20, padx=20)

# Dark Mode Toggle Function
def toggle_dark_mode():
    global dark_mode
    dark_mode = not dark_mode
    
    if dark_mode:
        # Dark mode colors
        header_bg = "#1a1a1a"
        button_text = "☀️ Light Mode"
        root_bg = "#2b2b2b"
        frame_bg = "#2b2b2b"
        table_bg = "#3b3b3b"
        text_color = "white"
    else:
        # Light mode colors (original design)
        header_bg = "#4A9EFF"
        button_text = "🌙 Dark Mode"
        root_bg = "white"
        frame_bg = "white"
        table_bg = "white"
        text_color = "black"
    
    # Update main window
    root.configure(bg=root_bg)
    
    # Update header
    header_frame.configure(bg=header_bg)
    header_label.configure(bg=header_bg)
    
    # Update button frame
    button_frame.configure(bg=frame_bg)
    
    # Update search frame
    search_frame.configure(bg=frame_bg)
    search_label.configure(bg=frame_bg, fg=text_color)
    
    # Update table frame
    table_frame.configure(bg=table_bg)
    
    # Update button text
    dark_mode_btn.configure(text=button_text)

# Dark Mode Toggle Button
dark_mode_btn = Button(header_frame, text="🌙 Dark Mode", font=("Arial", 10, "bold"), 
                      bg="white", fg="black", command=toggle_dark_mode)
dark_mode_btn.pack(side=RIGHT, pady=20, padx=20)

# Button Frame
button_frame = Frame(root, bg="white", height=80)
button_frame.pack(fill=X, pady=20)
button_frame.pack_propagate(False)

# Action Buttons with connected functions
report_lost_btn = Button(button_frame, text="Report Lost Item", width=18, height=2, font=("Arial", 12, "bold"), bg="#FF3300", fg="black", relief="flat", cursor="hand2",command=report_lost_item)
report_lost_btn.pack(side=LEFT, padx=30, pady=10)

report_found_btn = Button(button_frame, text="Report Found Item", width=18, height=2, font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", relief="flat", cursor="hand2", command=report_found_item)
report_found_btn.pack(side=LEFT, padx=30, pady=10)

search_items_btn = Button(button_frame, text="Search Items", width=18, height=2, font=("Arial", 12, "bold"), bg="#00BCD4", fg="white", relief="flat", cursor="hand2", command=advanced_search)
search_items_btn.pack(side=LEFT, padx=30, pady=10)


# Search Frame
search_frame = Frame(root, bg="white", height=60)
search_frame.pack(fill=X, pady=(0, 20))
search_frame.pack_propagate(False)

# Search Label and Entry
search_label = Label(search_frame, text="Search:", font=("Arial", 12), bg="white", fg="black")
search_label.pack(side=LEFT, padx=(50, 10), pady=15)

search_entry = Entry(search_frame, width=50, font=("Arial", 11), relief="solid", bd=1)
search_entry.pack(side=LEFT, pady=15)

search_btn = Button(search_frame, text="Search", width=10, font=("Arial", 10), bg="#2196F3", fg="white", relief="flat", cursor="hand2", command=quick_search)
search_btn.pack(side=LEFT, padx=10, pady=15)

show_all_btn = Button(search_frame, text="Show All", width=10, font=("Arial", 10), bg="#E91E63", fg="white", relief="flat", cursor="hand2", command=show_all_items)
show_all_btn.pack(side=LEFT, padx=5, pady=15)

# Refresh Button for user page
def refresh_items():
    show_all_items()
    messagebox.showinfo("Refresh", "Table refreshed successfully!")

refresh_btn = Button(search_frame, text="Refresh", width=10, font=("Arial", 10), bg="#4CAF50", fg="white", relief="flat", cursor="hand2", command=refresh_items)
refresh_btn.pack(side=LEFT, padx=5, pady=15)

# Table Frame
table_frame = Frame(root, bg="white")
table_frame.pack(fill=BOTH, expand=True, padx=50, pady=(0, 50))

# Create Treeview for table
columns = ("ID", "Item Name", "Category", "Type", "Date", "Location", "Status")
tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

# Define column headings and widths
tree.heading("ID", text="ID")
tree.heading("Item Name", text="Item Name")
tree.heading("Category", text="Category")
tree.heading("Type", text="Type")
tree.heading("Date", text="Date")
tree.heading("Location", text="Location")
tree.heading("Status", text="Status")

# Set column widths
tree.column("ID", width=50, anchor=CENTER)
tree.column("Item Name", width=150, anchor=W)
tree.column("Category", width=120, anchor=W)
tree.column("Type", width=80, anchor=CENTER)
tree.column("Date", width=100, anchor=CENTER)
tree.column("Location", width=150, anchor=W)
tree.column("Status", width=100, anchor=CENTER)

# Add scrollbar
scrollbar = ttk.Scrollbar(table_frame, orient=VERTICAL)
tree.configure(yscrollcommand=scrollbar.set)

# Pack the treeview and scrollbar
tree.pack(side=LEFT, fill=BOTH, expand=True)
scrollbar.pack(side=RIGHT, fill=Y)

# Style the treeview
style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview.Heading", font=("Arial", 11, "bold"), background="#f0f0f0")
style.configure("Treeview", font=("Arial", 10), rowheight=25)

# Show all items by default
show_all_items()

root.mainloop()