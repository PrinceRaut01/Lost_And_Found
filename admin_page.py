# --- Tkinter imports ---
import os
from tkinter import *
from tkinter import ttk, messagebox

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

# --- MIGRATION: Ensure 'phone' column exists in users table ---
def ensure_phone_column():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Check if 'phone' column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'phone' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN phone TEXT")
            conn.commit()
        conn.close()
    except Exception as e:
        messagebox.showerror("Database Error", f"Migration error: {e}")

ensure_phone_column()
# Main window setup
root = Tk()
center_window(root, 1100, 600)
root.title("Lost & Found - Admin Control Panel")
root.minsize(1100, 600)
root.resizable(True, True)
root.state("zoomed")
root.configure(bg="white")

icon_path = get_resource_path(os.path.join('assets', 'icon.ico'))
if os.path.exists(icon_path):
    try:
        root.iconbitmap(default=icon_path)
    except Exception:
        pass

# Global variables for window management
add_lost_window = None
add_found_window = None
edit_user_window = None
dark_mode = False

# Header Frame
header_frame = Frame(root, bg="#2196F3", height=80)
header_frame.pack(fill=X)
header_frame.pack_propagate(False)

# Header Label
header_label = Label(header_frame, text="Admin Panel - Welcome Administrator", 
                    font=("Arial", 20, "bold"), bg="#2196F3", fg="white")
header_label.pack(side=LEFT, pady=20, padx=20)

# Dark Mode Toggle Function
def toggle_dark_mode():
    global dark_mode
    dark_mode = not dark_mode
    
    if dark_mode:
        # Dark mode colors
        bg_color = "#2b2b2b"
        fg_color = "white"
        header_bg = "#1a1a1a"
        button_text = "☀️ Light Mode"
    else:
        # Light mode colors
        bg_color = "white"
        fg_color = "black"
        header_bg = "#2196F3"
        button_text = "🌙 Dark Mode"
    
    # Update main window
    root.configure(bg=bg_color)
    
    # Update header
    header_frame.configure(bg=header_bg)
    header_label.configure(bg=header_bg)
    
    # Update tabs
    items_frame.configure(bg=bg_color)
    users_frame.configure(bg=bg_color)
    reports_frame.configure(bg=bg_color)
    
    # Update action frames
    action_frame.configure(bg=bg_color)
    users_action_frame.configure(bg=bg_color)
    table_frame.configure(bg=bg_color)
    reports_content.configure(bg=bg_color)
    
    # Update stats label
    stats_label.configure(bg=bg_color, fg=fg_color)
    
    # Update button text
    dark_mode_btn.configure(text=button_text)

# Dark Mode Toggle Button
dark_mode_btn = Button(header_frame, text="🌙 Dark Mode", font=("Arial", 10, "bold"), 
                      bg="white", fg="black", command=toggle_dark_mode)
dark_mode_btn.pack(side=RIGHT, pady=20, padx=20)


# Create Notebook for tabs
notebook = ttk.Notebook(root)
notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)

# Items Management Tab
items_frame = Frame(notebook, bg="white")
notebook.add(items_frame, text="Items Management")

# Users Management Tab
users_frame = Frame(notebook, bg="white")
notebook.add(users_frame, text="Users Management")

# Reports Tab
reports_frame = Frame(notebook, bg="white")
notebook.add(reports_frame, text="Reports")

# Style the notebook tabs
style = ttk.Style()
style.theme_use("clam")
style.configure("TNotebook.Tab", font=("Arial", 12, "bold"), padding=[20, 10])

# Items Management Tab Content
# Functions for adding items
def add_lost_item():
    global add_lost_window
    if add_lost_window is not None and add_lost_window.winfo_exists():
        add_lost_window.lift()
        return
    
    add_lost_window = Toplevel()
    add_lost_window.title("Add Lost Item")
    center_window(add_lost_window, 1100, 600)
    add_lost_window.minsize(1100, 600)
    add_lost_window.resizable(True, True)
    add_lost_window.configure(bg="black")
    add_lost_window.grab_set()
    add_lost_window.transient(root)
    
    def on_closing():
        global add_lost_window
        add_lost_window.destroy()
        add_lost_window = None
    
    add_lost_window.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Header
    header_frame = Frame(add_lost_window, bg="#5DADE2", height=60)
    header_frame.pack(fill=X)
    header_frame.pack_propagate(False)
    
    Label(header_frame, text="Lost Item Details", font=("Arial", 18, "bold"), 
          bg="#5DADE2", fg="white").pack(pady=15)
    
    # Form frame
    form_frame = Frame(add_lost_window, bg="black")
    form_frame.pack(fill=BOTH, expand=True, padx=40, pady=30)
    
    # Basic form fields
    y_pos = 50
    
    #Item Name   
    Label(form_frame, text="Item Name:", font=("Arial", 12), bg="black", fg="white").place(x=50, y=y_pos)
    item_name = Entry(form_frame, width=30, font=("Arial", 11), bd=1, relief="solid")
    item_name.place(x=200, y=y_pos)
    
    #Category 
    y_pos += 40
    Label(form_frame, text="Category:", font=("Arial", 12), bg="black", fg="white").place(x=50, y=y_pos)
    category = Entry(form_frame, width=30, font=("Arial", 11), bd=1, relief="solid")
    category.place(x=200, y=y_pos)
    
    # Date Lost
    y_pos += 40
    Label(form_frame, text="Date Lost:", font=("Arial", 12), bg="black", fg="white").place(x=50, y=y_pos)
    date_lost = Entry(form_frame, width=30, font=("Arial", 11), bd=1, relief="solid")
    date_lost.place(x=200, y=y_pos)
    
    # Location Lost
    y_pos += 40
    Label(form_frame, text="Location Lost:", font=("Arial", 12), bg="black", fg="white").place(x=50, y=y_pos)
    location_lost = Entry(form_frame, width=30, font=("Arial", 11), bd=1, relief="solid")
    location_lost.place(x=200, y=y_pos)
    
    # Description
    y_pos += 40
    Label(form_frame, text="Description:", font=("Arial", 12), bg="black", fg="white").place(x=50, y=y_pos)
    description = Text(form_frame, width=30, height=4, font=("Arial", 11), bd=1, relief="solid")
    description.place(x=200, y=y_pos)
    
    # Contact Info
    y_pos += 120
    Label(form_frame, text="Contact Info:", font=("Arial", 12), bg="black", fg="white").place(x=50, y=y_pos)
    contact_info = Entry(form_frame, width=30, font=("Arial", 11), bd=1, relief="solid")
    contact_info.place(x=200, y=y_pos)
    
    def submit_lost_item():
        # Validate all fields
        if not all([
            item_name.get().strip(),
            category.get().strip(),
            date_lost.get().strip(),
            location_lost.get().strip(),
            description.get("1.0", END).strip(),
            contact_info.get().strip()
        ]):
            messagebox.showerror("Error", "Please fill all fields!")
            return
        # Insert into database
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO lost_items (item_name, category, date_lost, location_lost, description, contact_info) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    item_name.get().strip(),
                    category.get().strip(),
                    date_lost.get().strip(),
                    location_lost.get().strip(),
                    description.get("1.0", END).strip(),
                    contact_info.get().strip()
                ))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Lost item added successfully!")
            on_closing()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
    
    # Buttons
    y_pos += 50
    Button(form_frame, text="Submit", font=("Arial", 12, "bold"), bg="#28a745", fg="white", 
           width=12, command=submit_lost_item).place(x=200, y=y_pos)
    Button(form_frame, text="Cancel", font=("Arial", 12, "bold"), bg="#dc3545", fg="white", 
           width=12, command=on_closing).place(x=350, y=y_pos)
    
def add_found_item():
    global add_found_window
    if add_found_window is not None and add_found_window.winfo_exists():
        add_found_window.lift()
        return
    
    add_found_window = Toplevel()
    add_found_window.title("Add Found Item")
    center_window(add_found_window, 1100, 600)
    add_found_window.minsize(1100, 600)
    add_found_window.resizable(True, True)
    add_found_window.configure(bg="black")
    add_found_window.grab_set()
    add_found_window.transient(root)
    
    def on_closing():
        global add_found_window
        add_found_window.destroy()
        add_found_window = None
    
    add_found_window.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Header
    header_frame = Frame(add_found_window, bg="#5DADE2", height=60)
    header_frame.pack(fill=X)
    header_frame.pack_propagate(False)
    
    Label(header_frame, text="Found Item Details", font=("Arial", 18, "bold"), 
          bg="#5DADE2", fg="white").pack(pady=15)
    
    # Form frame
    form_frame = Frame(add_found_window, bg="black")
    form_frame.pack(fill=BOTH, expand=True, padx=40, pady=30)
    
    # Form fields
    y_pos = 50
    
    # Item Name
    Label(form_frame, text="Item Name:", font=("Arial", 12), bg="black", fg="white").place(x=50, y=y_pos)
    item_name = Entry(form_frame, width=30, font=("Arial", 11), bd=1, relief="solid")
    item_name.place(x=200, y=y_pos)
    
    # Category
    y_pos += 40
    Label(form_frame, text="Category:", font=("Arial", 12), bg="black", fg="white").place(x=50, y=y_pos)
    category = Entry(form_frame, width=30, font=("Arial", 11), bd=1, relief="solid")
    category.place(x=200, y=y_pos)
    
    # Date Found
    y_pos += 40
    Label(form_frame, text="Date Found:", font=("Arial", 12), bg="black", fg="white").place(x=50, y=y_pos)
    date_found = Entry(form_frame, width=30, font=("Arial", 11), bd=1, relief="solid")
    date_found.place(x=200, y=y_pos)
    
    # Location Found
    y_pos += 40
    Label(form_frame, text="Location Found:", font=("Arial", 12), bg="black", fg="white").place(x=50, y=y_pos)
    location_found = Entry(form_frame, width=30, font=("Arial", 11), bd=1, relief="solid")
    location_found.place(x=200, y=y_pos)
    
    # Description
    y_pos += 40
    Label(form_frame, text="Description:", font=("Arial", 12), bg="black", fg="white").place(x=50, y=y_pos)
    description = Text(form_frame, width=30, height=4, font=("Arial", 11), bd=1, relief="solid")
    description.place(x=200, y=y_pos)
    
    # Contact Info
    y_pos += 120
    Label(form_frame, text="Contact Info:", font=("Arial", 12), bg="black", fg="white").place(x=50, y=y_pos)
    contact_info = Entry(form_frame, width=30, font=("Arial", 11), bd=1, relief="solid")
    contact_info.place(x=200, y=y_pos)
    
    def submit_found_item():
        # Validate all fields
        if not all([
            item_name.get().strip(),
            category.get().strip(),
            date_found.get().strip(),
            location_found.get().strip(),
            description.get("1.0", END).strip(),
            contact_info.get().strip()
        ]):
            messagebox.showerror("Error", "Please fill all fields!")
            return
        
       # Insert into database
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO found_items (item_name, category, date_found, location_found, description, contact_info) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    item_name.get().strip(),
                    category.get().strip(),
                    date_found.get().strip(),
                    location_found.get().strip(),
                    description.get("1.0", END).strip(),
                    contact_info.get().strip()
                ))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Found item added successfully!")
            on_closing()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
    # Buttons
    y_pos += 50
    Button(form_frame, text="Submit", font=("Arial", 12, "bold"), bg="#28a745", fg="white", 
           width=12, command=submit_found_item).place(x=200, y=y_pos)
    Button(form_frame, text="Cancel", font=("Arial", 12, "bold"), bg="#dc3545", fg="white", 
           width=12, command=on_closing).place(x=350, y=y_pos)   
    
# Basic refresh function
def refresh_table():
    # Clear existing items
    for item in tree.get_children():
        tree.delete(item)
    # Reload items from the database
    load_items()
    messagebox.showinfo("Refresh", "Table refreshed successfully!")

# Action buttons frame
action_frame = Frame(items_frame, bg="white", height=80)
action_frame.pack(fill=X, padx=20, pady=10)
action_frame.pack_propagate(False)

# Action buttons
Button(action_frame, text="Add Lost Item", font=("Arial", 12, "bold"), bg="#FF3300", 
       fg="white", width=15, height=2,command=add_lost_item).pack(side=LEFT, padx=10, pady=10)

Button(action_frame, text="Add Found Item", font=("Arial", 12, "bold"), bg="#4CAF50", 
       fg="white", width=15, height=2, command=add_found_item).pack(side=LEFT, padx=10, pady=10)

Button(action_frame, text="Refresh", font=("Arial", 12, "bold"), bg="#2196F3", 
       fg="white", width=15, height=2, command=refresh_table).pack(side=LEFT, padx=10, pady=10)

# Table frame
table_frame = Frame(items_frame, bg="white")
table_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)

# Create Treeview for items table
columns = ("ID", "Item Name", "Category", "Type", "Date", "Status")
tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)

# Define column headings and widths
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=150, anchor=CENTER if col in ["ID", "Type", "Status"] else W)

# Add scrollbar
scrollbar = ttk.Scrollbar(table_frame, orient=VERTICAL, command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)

# Pack the treeview and scrollbar
tree.pack(side=LEFT, fill=BOTH, expand=True)
scrollbar.pack(side=RIGHT, fill=Y)

# Function to load all items from the database into the items table
def load_items():
    # Clear existing items
    for item in tree.get_children():
        tree.delete(item)
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Fetch lost items
        cursor.execute("SELECT id, item_name, category, 'Lost' as type, date_lost as date, 'active' as status FROM lost_items")
        lost_items = cursor.fetchall()
        # Fetch found items
        cursor.execute("SELECT id, item_name, category, 'Found' as type, date_found as date, 'active' as status FROM found_items")
        found_items = cursor.fetchall()



        # Fetch claimed items directly from claimed_items table
        cursor.execute("SELECT id, item_name, category, 'Claimed' as type, date_claimed as date, 'claimed' as status FROM claimed_items")
        claimed_items = cursor.fetchall()

        conn.close()

        # Combine all items
        all_items = lost_items + found_items + claimed_items
        # Assign unique sequential IDs for display
        display_id = 1
        for row in all_items:
            # Replace the database id with display_id
            new_row = (display_id,) + row[1:]
            tree.insert('', 'end', values=new_row)
            display_id += 1
    except Exception as e:
        messagebox.showerror("Database Error", str(e))

# Load items on startup
load_items()

# Users Management Tab Content
def edit_user():
    global edit_user_window
    
    # Get selected item
    selected = users_tree.selection()
    if not selected:
        messagebox.showerror("Error", "Please select a user to edit!")
        return
    
    if edit_user_window is not None and edit_user_window.winfo_exists():
        edit_user_window.lift()
        return
    
    # Get selected user ID
    item = users_tree.item(selected[0])
    user_id_val = item['values'][0]
    
    # Fetch user data from database
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, full_name, email, phone, user_type FROM users WHERE id=?", (user_id_val,))
        user_data = cursor.fetchone()
        conn.close()
        if not user_data:
            messagebox.showerror("Error", "User not found in database!")
            return
    except Exception as e:
        messagebox.showerror("Database Error", str(e))
        return
    
    edit_user_window = Toplevel()
    edit_user_window.title("Edit User")
    center_window(edit_user_window, 1100, 600)
    edit_user_window.minsize(1100, 600)
    edit_user_window.resizable(True, True)
    edit_user_window.configure(bg="black")
    edit_user_window.grab_set()
    edit_user_window.transient(root)
    
    def on_closing():
        global edit_user_window
        edit_user_window.destroy()
        edit_user_window = None
    
    edit_user_window.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Show the edit user form with details from the database
    # Header
    header_frame = Frame(edit_user_window, bg="#5DADE2", height=60)
    header_frame.pack(fill=X)
    header_frame.pack_propagate(False)
    
    Label(header_frame, text="Edit User Details", font=("Arial", 18, "bold"), 
          bg="#5DADE2", fg="white").pack(pady=15)

    # Form frame with black background
    form_frame = Frame(edit_user_window, bg="black")
    form_frame.pack(fill=BOTH, expand=True, padx=40, pady=30)
    
    # Form fields
    y_pos = 50
    
    # User ID (read-only)
    Label(form_frame, text="User ID:", font=("Arial", 12), bg="black", fg="white").place(x=50, y=y_pos)
    user_id = Entry(form_frame, width=30, font=("Arial", 11), bd=1, relief="solid", state="readonly")
    user_id.place(x=200, y=y_pos)
    user_id.config(state="normal")
    user_id.insert(0, user_data[0] if user_data else "")
    user_id.config(state="readonly")
    
    # Full Name
    y_pos += 40
    Label(form_frame, text="Full Name:", font=("Arial", 12), bg="black", fg="white").place(x=50, y=y_pos)
    full_name = Entry(form_frame, width=30, font=("Arial", 11), bd=1, relief="solid")
    full_name.place(x=200, y=y_pos)
    full_name.insert(0, user_data[1] if len(user_data) > 1 else "")
    
    # Email
    y_pos += 40
    Label(form_frame, text="Email:", font=("Arial", 12), bg="black", fg="white").place(x=50, y=y_pos)
    email = Entry(form_frame, width=30, font=("Arial", 11), bd=1, relief="solid")
    email.place(x=200, y=y_pos)
    email.insert(0, user_data[2] if len(user_data) > 2 else "")

    # Phone
    y_pos += 40
    Label(form_frame, text="Phone:", font=("Arial", 12), bg="black", fg="white").place(x=50, y=y_pos)
    phone = Entry(form_frame, width=30, font=("Arial", 11), bd=1, relief="solid")
    phone.place(x=200, y=y_pos)
    phone.insert(0, str(user_data[3]) if user_data[3] is not None else "")
    
    # User Type
    y_pos += 40
    Label(form_frame, text="User Type:", font=("Arial", 12), bg="black", fg="white").place(x=50, y=y_pos)
    user_type = ttk.Combobox(form_frame, width=28, font=("Arial", 11), state="readonly")
    user_type['values'] = ('admin', 'user')
    user_type.place(x=200, y=y_pos)
    user_type.set(str(user_data[4]) if len(user_data) > 4 and user_data[4] is not None else "user")

    def update_user():
        # Validate fields
        if not all([full_name.get().strip(), email.get().strip(), phone.get().strip()]):
            messagebox.showerror("Error", "Please fill all fields!")
            return
        
        if "@" not in email.get() or "." not in email.get():
            messagebox.showerror("Error", "Please enter a valid email address!")
            return
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET full_name=?, email=?, phone=?, user_type=? WHERE id=?",
                (
                    full_name.get().strip(),
                    email.get().strip(),
                    phone.get().strip(),
                    user_type.get(),
                    user_id.get()
                ))
            conn.commit()
            conn.close()
            load_users()
            messagebox.showinfo("Success", "User updated successfully!")
            on_closing()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
    
    # Buttons
    y_pos += 50
    Button(form_frame, text="Update", font=("Arial", 12, "bold"), bg="#28a745", fg="white", 
           width=12, command=update_user).place(x=200, y=y_pos)
    Button(form_frame, text="Cancel", font=("Arial", 12, "bold"), bg="#dc3545", fg="white",
           width=12, command=on_closing).place(x=350, y=y_pos)




def load_users():
    # Clear existing users
    for item in users_tree.get_children():
        users_tree.delete(item)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, full_name, email, phone, user_type FROM users")
        users = cursor.fetchall()
        conn.close()
        for row in users:
            users_tree.insert('', 'end', values=row)
    except Exception as e:
        messagebox.showerror("Database Error", str(e))

# Users action buttons frame
users_action_frame = Frame(users_frame, bg="white", height=80)
users_action_frame.pack(fill=X, padx=20, pady=10)
users_action_frame.pack_propagate(False)


# Edit User button
Button(users_action_frame, text="Edit User", font=("Arial", 12, "bold"), bg="#FF9800", 
       fg="white", width=15, height=2, command=edit_user).pack(side=LEFT, padx=10, pady=10)

# Delete User function and button
def delete_user():
    selected = users_tree.selection()
    if not selected:
        messagebox.showerror("Error", "Please select a user to delete!", parent=root)
        return
    item = users_tree.item(selected[0])
    user_id_val = item['values'][0]
    user_name = item['values'][1]
    if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete user '{user_name}' (ID: {user_id_val})?", parent=root):
        return
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id=?", (user_id_val,))
        conn.commit()
        conn.close()
        load_users()
        messagebox.showinfo("Success", f"User '{user_name}' deleted successfully!", parent=root)
    except Exception as e:
        messagebox.showerror("Database Error", str(e), parent=root)

Button(users_action_frame, text="Delete User", font=("Arial", 12, "bold"), bg="#e53935", 
       fg="white", width=15, height=2, command=delete_user).pack(side=LEFT, padx=10, pady=10)

# Refresh Users button
Button(users_action_frame, text="Refresh", font=("Arial", 12, "bold"), bg="#2196F3", 
       fg="white", width=15, height=2, command=load_users).pack(side=LEFT, padx=10, pady=10)

# Users table
users_columns = ("ID", "Full Name", "Email", "Phone", "Type")
users_tree = ttk.Treeview(users_frame, columns=users_columns, show="headings", height=20)

for col in users_columns:
    users_tree.heading(col, text=col)
    users_tree.column(col, width=200, anchor=W)

users_tree.pack(fill=BOTH, expand=True, padx=20, pady=20)
# Load users from database on startup
load_users()

# Reports Tab Content
# Create simple stats display
reports_content = Frame(reports_frame, bg="white")
reports_content.pack(fill=BOTH, expand=True, padx=50, pady=50)

# Stats display
# Function to update stats from the database
def update_stats():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM lost_items")
        lost_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM found_items")
        found_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM claimed_items")
        claimed_count = cursor.fetchone()[0]
        total_count = lost_count + found_count
        active_count = total_count - claimed_count
        stats_text = f"""
Total Items: {total_count}
Lost Items: {lost_count}
Found Items: {found_count}
Active Items: {active_count}
Claimed Items: {claimed_count}
"""
        stats_label.config(text=stats_text)
        conn.close()
    except Exception as e:
        stats_label.config(text="Error loading stats: " + str(e))

stats_label = Label(reports_content, text="Loading stats...", font=("Arial", 14), 
                   bg="white", fg="black", justify=LEFT)
stats_label.pack(pady=50)


# Load initial data
load_users()
update_stats()

root.mainloop()