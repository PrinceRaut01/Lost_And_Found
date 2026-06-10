import os
from tkinter import *
from tkinter import ttk, messagebox
from db_connection import get_db_connection, get_resource_path


def _center(win, w, h):
    win.update_idletasks()
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    win.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")


class AdminPage(Frame):
    """Admin dashboard – originally admin_page.py.
    Converted to a Frame so it can live inside App.container without its own Tk root.
    Visual design is pixel-faithful to the original: same header height, fonts,
    button sizes, notebook tabs, modal layouts, and dark-mode colours.
    Only addition: a Logout button next to the Dark Mode button.
    """

    def __init__(self, parent, app, current_user=None):
        super().__init__(parent)
        self.app = app
        self.current_user = current_user
        self._dark = False
        self._add_lost_win   = None
        self._add_found_win  = None
        self._edit_user_win  = None
        self._build()

    def _root(self):
        return self.app.root

    # ── Main layout ───────────────────────────────────────────────────────────

    def _build(self):
        # ── Header – exact original: height=80, Arial 20 bold, #2196F3 ────────
        self._header_frame = Frame(self, bg="#2196F3", height=80)
        self._header_frame.pack(fill=X)
        self._header_frame.pack_propagate(False)

        self._header_label = Label(
            self._header_frame,
            text="Admin Panel - Welcome Administrator",
            font=("Arial", 20, "bold"), bg="#2196F3", fg="white")
        self._header_label.pack(side=LEFT, pady=20, padx=20)

        # Logout button (new – required for single-window navigation)
        Button(
            self._header_frame, text="Logout",
            font=("Arial", 10, "bold"), bg="#ef5350", fg="white",
            relief="flat", command=self.app.logout
        ).pack(side=RIGHT, pady=20, padx=10)

        # Dark Mode toggle – original style: white bg, black fg
        self._dark_mode_btn = Button(
            self._header_frame, text="🌙 Dark Mode",
            font=("Arial", 10, "bold"), bg="white", fg="black",
            command=self._toggle_dark_mode)
        self._dark_mode_btn.pack(side=RIGHT, pady=20, padx=20)

        # ── Notebook – original: clam, Arial 12 bold, padding [20,10] ─────────
        self._notebook = ttk.Notebook(self)
        self._notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook.Tab",
                         font=("Arial", 12, "bold"), padding=[20, 10])

        self._items_frame   = Frame(self._notebook, bg="white")
        self._users_frame   = Frame(self._notebook, bg="white")
        self._reports_frame = Frame(self._notebook, bg="white")
        self._notebook.add(self._items_frame,   text="Items Management")
        self._notebook.add(self._users_frame,   text="Users Management")
        self._notebook.add(self._reports_frame, text="Reports")

        self._build_items_tab()
        self._build_users_tab()
        self._build_reports_tab()

    # ── Items tab ─────────────────────────────────────────────────────────────

    def _build_items_tab(self):
        # Original: action_frame height=80
        self._action_frame = Frame(self._items_frame, bg="white", height=80)
        self._action_frame.pack(fill=X, padx=20, pady=10)
        self._action_frame.pack_propagate(False)

        # Original buttons: Arial 12 bold, width=15, height=2
        Button(self._action_frame, text="Add Lost Item",
               font=("Arial", 12, "bold"), bg="#FF3300", fg="white",
               width=15, height=2, command=self._add_lost_item
               ).pack(side=LEFT, padx=10, pady=10)
        Button(self._action_frame, text="Add Found Item",
               font=("Arial", 12, "bold"), bg="#4CAF50", fg="white",
               width=15, height=2, command=self._add_found_item
               ).pack(side=LEFT, padx=10, pady=10)
        Button(self._action_frame, text="Refresh",
               font=("Arial", 12, "bold"), bg="#2196F3", fg="white",
               width=15, height=2, command=self._refresh_table
               ).pack(side=LEFT, padx=10, pady=10)

        self._table_frame = Frame(self._items_frame, bg="white")
        self._table_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)

        # Original treeview
        columns = ("ID", "Item Name", "Category", "Type", "Date", "Status")
        self._tree = ttk.Treeview(self._table_frame, columns=columns,
                                   show="headings", height=20)
        for col in columns:
            self._tree.heading(col, text=col)
            self._tree.column(col, width=150,
                anchor=CENTER if col in ("ID", "Type", "Status") else W)

        scrollbar = ttk.Scrollbar(self._table_frame, orient=VERTICAL,
                                   command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)
        self._tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        self._load_items()

    def _load_items(self):
        for item in self._tree.get_children():
            self._tree.delete(item)
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id,item_name,category,'Lost' as type,"
                "date_lost as date,'active' as status FROM lost_items")
            lost_items = cursor.fetchall()
            cursor.execute(
                "SELECT id,item_name,category,'Found' as type,"
                "date_found as date,'active' as status FROM found_items")
            found_items = cursor.fetchall()
            cursor.execute(
                "SELECT id,item_name,category,'Claimed' as type,"
                "date_claimed as date,'claimed' as status FROM claimed_items")
            claimed_items = cursor.fetchall()
            conn.close()
            all_items = lost_items + found_items + claimed_items
            for display_id, row in enumerate(all_items, 1):
                self._tree.insert('', 'end', values=(display_id,) + row[1:])
        except Exception as e:
            messagebox.showerror("Database Error", str(e), parent=self._root())

    def _refresh_table(self):
        self._load_items()
        messagebox.showinfo("Refresh", "Table refreshed successfully!",
                             parent=self._root())

    # ── Add Lost Item modal (original layout restored) ────────────────────────

    def _add_lost_item(self):
        if self._add_lost_win is not None and self._add_lost_win.winfo_exists():
            self._add_lost_win.lift()
            return

        win = Toplevel(self._root())
        win.title("Add Lost Item")
        _center(win, 1100, 600)
        win.minsize(1100, 600)
        win.resizable(True, True)
        win.configure(bg="black")
        win.grab_set()
        win.transient(self._root())
        self._add_lost_win = win

        def on_closing():
            self._add_lost_win = None
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", on_closing)

        # Header
        hdr = Frame(win, bg="#5DADE2", height=60)
        hdr.pack(fill=X)
        hdr.pack_propagate(False)
        Label(hdr, text="Lost Item Details",
              font=("Arial", 18, "bold"), bg="#5DADE2", fg="white").pack(pady=15)

        form_frame = Frame(win, bg="black")
        form_frame.pack(fill=BOTH, expand=True, padx=40, pady=30)

        y_pos = 50
        Label(form_frame, text="Item Name:",
              font=("Arial", 12), bg="black", fg="white").place(x=50, y=y_pos)
        item_name = Entry(form_frame, width=30, font=("Arial", 11),
                          bd=1, relief="solid")
        item_name.place(x=200, y=y_pos)

        y_pos += 40
        Label(form_frame, text="Category:",
              font=("Arial", 12), bg="black", fg="white").place(x=50, y=y_pos)
        category = Entry(form_frame, width=30, font=("Arial", 11),
                         bd=1, relief="solid")
        category.place(x=200, y=y_pos)

        y_pos += 40
        Label(form_frame, text="Date Lost:",
              font=("Arial", 12), bg="black", fg="white").place(x=50, y=y_pos)
        date_lost = Entry(form_frame, width=30, font=("Arial", 11),
                          bd=1, relief="solid")
        date_lost.place(x=200, y=y_pos)

        y_pos += 40
        Label(form_frame, text="Location Lost:",
              font=("Arial", 12), bg="black", fg="white").place(x=50, y=y_pos)
        location_lost = Entry(form_frame, width=30, font=("Arial", 11),
                               bd=1, relief="solid")
        location_lost.place(x=200, y=y_pos)

        y_pos += 40
        Label(form_frame, text="Description:",
              font=("Arial", 12), bg="black", fg="white").place(x=50, y=y_pos)
        description = Text(form_frame, width=30, height=4,
                           font=("Arial", 11), bd=1, relief="solid")
        description.place(x=200, y=y_pos)

        y_pos += 120
        Label(form_frame, text="Contact Info:",
              font=("Arial", 12), bg="black", fg="white").place(x=50, y=y_pos)
        contact_info = Entry(form_frame, width=30, font=("Arial", 11),
                              bd=1, relief="solid")
        contact_info.place(x=200, y=y_pos)

        def submit():
            if not all([item_name.get().strip(), category.get().strip(),
                        date_lost.get().strip(), location_lost.get().strip(),
                        description.get("1.0", END).strip(),
                        contact_info.get().strip()]):
                messagebox.showerror("Error", "Please fill all fields!", parent=win)
                return
            try:
                conn = get_db_connection()
                conn.cursor().execute(
                    "INSERT INTO lost_items"
                    " (item_name,category,date_lost,location_lost,"
                    "description,contact_info) VALUES (?,?,?,?,?,?)",
                    (item_name.get().strip(), category.get().strip(),
                     date_lost.get().strip(), location_lost.get().strip(),
                     description.get("1.0", END).strip(),
                     contact_info.get().strip()))
                conn.commit(); conn.close()
                messagebox.showinfo("Success", "Lost item added successfully!", parent=win)
                on_closing()
                self._load_items()
            except Exception as e:
                messagebox.showerror("Database Error", str(e), parent=win)

        y_pos += 50
        Button(form_frame, text="Submit", font=("Arial", 12, "bold"),
               bg="#28a745", fg="white", width=12,
               command=submit).place(x=200, y=y_pos)
        Button(form_frame, text="Cancel", font=("Arial", 12, "bold"),
               bg="#dc3545", fg="white", width=12,
               command=on_closing).place(x=350, y=y_pos)

    # ── Add Found Item modal ──────────────────────────────────────────────────

    def _add_found_item(self):
        if self._add_found_win is not None and self._add_found_win.winfo_exists():
            self._add_found_win.lift()
            return

        win = Toplevel(self._root())
        win.title("Add Found Item")
        _center(win, 1100, 600)
        win.minsize(1100, 600)
        win.resizable(True, True)
        win.configure(bg="black")
        win.grab_set()
        win.transient(self._root())
        self._add_found_win = win

        def on_closing():
            self._add_found_win = None
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", on_closing)

        hdr = Frame(win, bg="#5DADE2", height=60)
        hdr.pack(fill=X)
        hdr.pack_propagate(False)
        Label(hdr, text="Found Item Details",
              font=("Arial", 18, "bold"), bg="#5DADE2", fg="white").pack(pady=15)

        form_frame = Frame(win, bg="black")
        form_frame.pack(fill=BOTH, expand=True, padx=40, pady=30)

        y_pos = 50
        Label(form_frame, text="Item Name:",
              font=("Arial", 12), bg="black", fg="white").place(x=50, y=y_pos)
        item_name = Entry(form_frame, width=30, font=("Arial", 11),
                          bd=1, relief="solid")
        item_name.place(x=200, y=y_pos)

        y_pos += 40
        Label(form_frame, text="Category:",
              font=("Arial", 12), bg="black", fg="white").place(x=50, y=y_pos)
        category = Entry(form_frame, width=30, font=("Arial", 11),
                         bd=1, relief="solid")
        category.place(x=200, y=y_pos)

        y_pos += 40
        Label(form_frame, text="Date Found:",
              font=("Arial", 12), bg="black", fg="white").place(x=50, y=y_pos)
        date_found = Entry(form_frame, width=30, font=("Arial", 11),
                           bd=1, relief="solid")
        date_found.place(x=200, y=y_pos)

        y_pos += 40
        Label(form_frame, text="Location Found:",
              font=("Arial", 12), bg="black", fg="white").place(x=50, y=y_pos)
        location_found = Entry(form_frame, width=30, font=("Arial", 11),
                                bd=1, relief="solid")
        location_found.place(x=200, y=y_pos)

        y_pos += 40
        Label(form_frame, text="Description:",
              font=("Arial", 12), bg="black", fg="white").place(x=50, y=y_pos)
        description = Text(form_frame, width=30, height=4,
                           font=("Arial", 11), bd=1, relief="solid")
        description.place(x=200, y=y_pos)

        y_pos += 120
        Label(form_frame, text="Contact Info:",
              font=("Arial", 12), bg="black", fg="white").place(x=50, y=y_pos)
        contact_info = Entry(form_frame, width=30, font=("Arial", 11),
                              bd=1, relief="solid")
        contact_info.place(x=200, y=y_pos)

        def submit():
            if not all([item_name.get().strip(), category.get().strip(),
                        date_found.get().strip(), location_found.get().strip(),
                        description.get("1.0", END).strip(),
                        contact_info.get().strip()]):
                messagebox.showerror("Error", "Please fill all fields!", parent=win)
                return
            try:
                conn = get_db_connection()
                conn.cursor().execute(
                    "INSERT INTO found_items"
                    " (item_name,category,date_found,location_found,"
                    "description,contact_info) VALUES (?,?,?,?,?,?)",
                    (item_name.get().strip(), category.get().strip(),
                     date_found.get().strip(), location_found.get().strip(),
                     description.get("1.0", END).strip(),
                     contact_info.get().strip()))
                conn.commit(); conn.close()
                messagebox.showinfo("Success", "Found item added successfully!", parent=win)
                on_closing()
                self._load_items()
            except Exception as e:
                messagebox.showerror("Database Error", str(e), parent=win)

        y_pos += 50
        Button(form_frame, text="Submit", font=("Arial", 12, "bold"),
               bg="#28a745", fg="white", width=12,
               command=submit).place(x=200, y=y_pos)
        Button(form_frame, text="Cancel", font=("Arial", 12, "bold"),
               bg="#dc3545", fg="white", width=12,
               command=on_closing).place(x=350, y=y_pos)

    # ── Users tab ─────────────────────────────────────────────────────────────

    def _build_users_tab(self):
        # Original: action frame height=80
        self._users_action_frame = Frame(self._users_frame, bg="white", height=80)
        self._users_action_frame.pack(fill=X, padx=20, pady=10)
        self._users_action_frame.pack_propagate(False)

        Button(self._users_action_frame, text="Edit User",
               font=("Arial", 12, "bold"), bg="#FF9800", fg="white",
               width=15, height=2,
               command=self._edit_user).pack(side=LEFT, padx=10, pady=10)
        Button(self._users_action_frame, text="Delete User",
               font=("Arial", 12, "bold"), bg="#e53935", fg="white",
               width=15, height=2,
               command=self._delete_user).pack(side=LEFT, padx=10, pady=10)
        Button(self._users_action_frame, text="Refresh",
               font=("Arial", 12, "bold"), bg="#2196F3", fg="white",
               width=15, height=2,
               command=self._load_users).pack(side=LEFT, padx=10, pady=10)

        # Users treeview – original: column width=200, anchor=W
        users_columns = ("ID", "Full Name", "Email", "Phone", "Type")
        self._users_tree = ttk.Treeview(self._users_frame,
                                         columns=users_columns,
                                         show="headings", height=20)
        for col in users_columns:
            self._users_tree.heading(col, text=col)
            self._users_tree.column(col, width=200, anchor=W)
        self._users_tree.pack(fill=BOTH, expand=True, padx=20, pady=20)

        self._load_users()

    def _load_users(self):
        for item in self._users_tree.get_children():
            self._users_tree.delete(item)
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id,full_name,email,phone,user_type FROM users")
            for row in cursor.fetchall():
                self._users_tree.insert('', 'end', values=row)
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", str(e), parent=self._root())

    def _delete_user(self):
        selected = self._users_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a user to delete!",
                                  parent=self._root())
            return
        item = self._users_tree.item(selected[0])
        user_id_val = item['values'][0]
        user_name   = item['values'][1]
        if not messagebox.askyesno(
                "Confirm Delete",
                f"Are you sure you want to delete user '{user_name}'"
                f" (ID: {user_id_val})?",
                parent=self._root()):
            return
        try:
            conn = get_db_connection()
            conn.cursor().execute("DELETE FROM users WHERE id=?", (user_id_val,))
            conn.commit(); conn.close()
            self._load_users()
            messagebox.showinfo("Success",
                f"User '{user_name}' deleted successfully!",
                parent=self._root())
        except Exception as e:
            messagebox.showerror("Database Error", str(e), parent=self._root())

    # ── Edit User modal (original layout restored) ────────────────────────────

    def _edit_user(self):
        selected = self._users_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a user to edit!",
                                  parent=self._root())
            return
        if self._edit_user_win is not None and self._edit_user_win.winfo_exists():
            self._edit_user_win.lift()
            return

        item = self._users_tree.item(selected[0])
        user_id_val = item['values'][0]

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id,full_name,email,phone,user_type"
                " FROM users WHERE id=?", (user_id_val,))
            user_data = cursor.fetchone()
            conn.close()
            if not user_data:
                messagebox.showerror("Error", "User not found in database!",
                                      parent=self._root())
                return
        except Exception as e:
            messagebox.showerror("Database Error", str(e), parent=self._root())
            return

        win = Toplevel(self._root())
        win.title("Edit User")
        _center(win, 1100, 600)
        win.minsize(1100, 600)
        win.resizable(True, True)
        win.configure(bg="black")
        win.grab_set()
        win.transient(self._root())
        self._edit_user_win = win

        def on_closing():
            self._edit_user_win = None
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", on_closing)

        hdr = Frame(win, bg="#5DADE2", height=60)
        hdr.pack(fill=X)
        hdr.pack_propagate(False)
        Label(hdr, text="Edit User Details",
              font=("Arial", 18, "bold"), bg="#5DADE2", fg="white").pack(pady=15)

        form_frame = Frame(win, bg="black")
        form_frame.pack(fill=BOTH, expand=True, padx=40, pady=30)

        y_pos = 50
        Label(form_frame, text="User ID:",
              font=("Arial", 12), bg="black", fg="white").place(x=50, y=y_pos)
        user_id_entry = Entry(form_frame, width=30, font=("Arial", 11),
                               bd=1, relief="solid", state="readonly")
        user_id_entry.place(x=200, y=y_pos)
        user_id_entry.config(state="normal")
        user_id_entry.insert(0, user_data[0] if user_data else "")
        user_id_entry.config(state="readonly")

        y_pos += 40
        Label(form_frame, text="Full Name:",
              font=("Arial", 12), bg="black", fg="white").place(x=50, y=y_pos)
        full_name = Entry(form_frame, width=30, font=("Arial", 11),
                          bd=1, relief="solid")
        full_name.place(x=200, y=y_pos)
        full_name.insert(0, user_data[1] if len(user_data) > 1 else "")

        y_pos += 40
        Label(form_frame, text="Email:",
              font=("Arial", 12), bg="black", fg="white").place(x=50, y=y_pos)
        email = Entry(form_frame, width=30, font=("Arial", 11),
                      bd=1, relief="solid")
        email.place(x=200, y=y_pos)
        email.insert(0, user_data[2] if len(user_data) > 2 else "")

        y_pos += 40
        Label(form_frame, text="Phone:",
              font=("Arial", 12), bg="black", fg="white").place(x=50, y=y_pos)
        phone = Entry(form_frame, width=30, font=("Arial", 11),
                      bd=1, relief="solid")
        phone.place(x=200, y=y_pos)
        phone.insert(0, str(user_data[3]) if user_data[3] is not None else "")

        y_pos += 40
        Label(form_frame, text="User Type:",
              font=("Arial", 12), bg="black", fg="white").place(x=50, y=y_pos)
        user_type = ttk.Combobox(form_frame, width=28, font=("Arial", 11),
                                  state="readonly")
        user_type['values'] = ('admin', 'user')
        user_type.place(x=200, y=y_pos)
        user_type.set(
            str(user_data[4]) if len(user_data) > 4 and user_data[4] else "user")

        def update_user():
            if not all([full_name.get().strip(),
                        email.get().strip(),
                        phone.get().strip()]):
                messagebox.showerror("Error", "Please fill all fields!", parent=win)
                return
            if "@" not in email.get() or "." not in email.get():
                messagebox.showerror("Error",
                    "Please enter a valid email address!", parent=win)
                return
            try:
                conn = get_db_connection()
                conn.cursor().execute(
                    "UPDATE users SET full_name=?,email=?,phone=?,user_type=?"
                    " WHERE id=?",
                    (full_name.get().strip(), email.get().strip(),
                     phone.get().strip(), user_type.get(),
                     user_id_entry.get()))
                conn.commit(); conn.close()
                self._load_users()
                messagebox.showinfo("Success", "User updated successfully!",
                                     parent=win)
                on_closing()
            except Exception as e:
                messagebox.showerror("Database Error", str(e), parent=win)

        y_pos += 50
        Button(form_frame, text="Update", font=("Arial", 12, "bold"),
               bg="#28a745", fg="white", width=12,
               command=update_user).place(x=200, y=y_pos)
        Button(form_frame, text="Cancel", font=("Arial", 12, "bold"),
               bg="#dc3545", fg="white", width=12,
               command=on_closing).place(x=350, y=y_pos)

    # ── Reports tab ───────────────────────────────────────────────────────────

    def _build_reports_tab(self):
        # Original: reports_content with padx=50, pady=50
        self._reports_content = Frame(self._reports_frame, bg="white")
        self._reports_content.pack(fill=BOTH, expand=True, padx=50, pady=50)

        # Original: stats label font Arial 14, pady=50
        self._stats_label = Label(
            self._reports_content,
            text="Loading stats...",
            font=("Arial", 14), bg="white", fg="black", justify=LEFT)
        self._stats_label.pack(pady=50)

        self._load_users()
        self._update_stats()

    def _update_stats(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM lost_items")
            lost_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM found_items")
            found_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM claimed_items")
            claimed_count = cursor.fetchone()[0]
            conn.close()
            total_count  = lost_count + found_count
            active_count = total_count - claimed_count
            self._stats_label.config(text=(
                f"\nTotal Items: {total_count}\n"
                f"Lost Items: {lost_count}\n"
                f"Found Items: {found_count}\n"
                f"Active Items: {active_count}\n"
                f"Claimed Items: {claimed_count}\n"
            ))
        except Exception as e:
            self._stats_label.config(text="Error loading stats: " + str(e))

    # ── Dark mode toggle (same widgets as original) ───────────────────────────

    def _toggle_dark_mode(self):
        self._dark = not self._dark
        if self._dark:
            bg_color    = "#2b2b2b"
            fg_color    = "white"
            header_bg   = "#1a1a1a"
            button_text = "☀️ Light Mode"
        else:
            bg_color    = "white"
            fg_color    = "black"
            header_bg   = "#2196F3"
            button_text = "🌙 Dark Mode"

        self.configure(bg=bg_color)
        self._header_frame.configure(bg=header_bg)
        self._header_label.configure(bg=header_bg)
        self._items_frame.configure(bg=bg_color)
        self._users_frame.configure(bg=bg_color)
        self._reports_frame.configure(bg=bg_color)
        self._action_frame.configure(bg=bg_color)
        self._users_action_frame.configure(bg=bg_color)
        self._table_frame.configure(bg=bg_color)
        self._reports_content.configure(bg=bg_color)
        self._stats_label.configure(bg=bg_color, fg=fg_color)
        self._dark_mode_btn.configure(text=button_text)
