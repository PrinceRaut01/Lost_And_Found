import os
from tkinter import *
from tkinter import ttk, messagebox
from db_connection import get_db_connection, get_resource_path


def _center(win, w, h):
    win.update_idletasks()
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    win.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")


class UserPage(Frame):
    """User dashboard – originally user_page.py.
    Converted to a Frame so it can live inside App.container without its own Tk root.
    Visual design is pixel-faithful to the original: same header height, fonts,
    button sizes, search bar, table padding, and modal layouts.
    Only addition: a Logout button in the header.
    """

    def __init__(self, parent, app, username=None):
        super().__init__(parent)
        self.app = app
        self.current_user = username
        self._report_lost_win   = None
        self._report_found_win  = None
        self._adv_search_win    = None
        self._build()

    def _root(self):
        return self.app.root

    # Main layout

    def _build(self):
        # Header
        self._header_frame = Frame(self, bg="#4A9EFF", height=80)
        self._header_frame.pack(fill=X)
        self._header_frame.pack_propagate(False)

        Label(self._header_frame,
              text=f"Welcome, {self.current_user or 'User'}!",
              font=("Arial", 20, "bold"), bg="#4A9EFF", fg="white"
              ).pack(side=LEFT, pady=20, padx=20)

        # Logout button
        Button(self._header_frame, text="Logout",
               font=("Arial", 10, "bold"), bg="#ef5350", fg="white",
               relief="flat", command=self.app.logout
               ).pack(side=RIGHT, pady=20, padx=10)

        # Button frame
        self._btn_frame = Frame(self, bg="white", height=80)
        self._btn_frame.pack(fill=X, padx=20, pady=5)
        self._btn_frame.pack_propagate(False)

        # Original buttons: Arial 12 bold, width=18, height=2
        Button(self._btn_frame, text="Report Lost Item",
               font=("Arial", 12, "bold"), bg="#FF3300", fg="white",
               width=18, height=2,
               command=self._report_lost_item
               ).pack(side=LEFT, padx=10, pady=10)
        Button(self._btn_frame, text="Report Found Item",
               font=("Arial", 12, "bold"), bg="#4CAF50", fg="white",
               width=18, height=2,
               command=self._report_found_item
               ).pack(side=LEFT, padx=10, pady=10)
        Button(self._btn_frame, text="Refresh",
               font=("Arial", 12, "bold"), bg="#2196F3", fg="white",
               width=18, height=2,
               command=self._refresh_table
               ).pack(side=LEFT, padx=10, pady=10)

        # Search frame
        self._search_frame = Frame(self, bg="white", height=60)
        self._search_frame.pack(fill=X, pady=5)
        self._search_frame.pack_propagate(False)

        # Original: padx=(50,10)
        Label(self._search_frame, text="Search:",
              font=("Arial", 12, "bold"), bg="white"
              ).pack(side=LEFT, padx=(50, 10), pady=10)

        self._search_var = StringVar()
        self._search_entry = Entry(self._search_frame, textvariable=self._search_var,
                                    width=40, font=("Arial", 11),
                                    bd=1, relief="solid")
        self._search_entry.pack(side=LEFT, padx=(0, 10), pady=10)

        Button(self._search_frame, text="Search",
               font=("Arial", 11, "bold"), bg="#2196F3", fg="white",
               command=self._search_items
               ).pack(side=LEFT, padx=(0, 10), pady=10)
        Button(self._search_frame, text="Advanced Search",
               font=("Arial", 11, "bold"), bg="#9C27B0", fg="white",
               command=self._advanced_search
               ).pack(side=LEFT, padx=(0, 10), pady=10)

        # Table frame
        self._table_frame = Frame(self, bg="white")
        self._table_frame.pack(fill=BOTH, expand=True, padx=50, pady=(0, 50))

        columns = ("ID", "Item Name", "Category", "Type", "Date", "Status")
        self._tree = ttk.Treeview(self._table_frame, columns=columns,
                                   show="headings", height=15)
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

    # Data loading

    def _load_items(self, search_term="", filters=None):
        for item in self._tree.get_children():
            self._tree.delete(item)
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            if filters:
                item_type = filters.get("type", "All")
                category  = filters.get("category", "")
                date_from = filters.get("date_from", "")
                date_to   = filters.get("date_to", "")

                if item_type in ("All", "Lost"):
                    q = ("SELECT id,item_name,category,'Lost',"
                         "date_lost,'active' FROM lost_items WHERE 1=1")
                    params = []
                    if search_term:
                        q += " AND (item_name LIKE ? OR description LIKE ?)"
                        params += [f"%{search_term}%", f"%{search_term}%"]
                    if category:
                        q += " AND category LIKE ?"; params.append(f"%{category}%")
                    if date_from:
                        q += " AND date_lost >= ?"; params.append(date_from)
                    if date_to:
                        q += " AND date_lost <= ?"; params.append(date_to)
                    cursor.execute(q, params)
                    lost_items = cursor.fetchall()
                else:
                    lost_items = []

                if item_type in ("All", "Found"):
                    q = ("SELECT id,item_name,category,'Found',"
                         "date_found,'active' FROM found_items WHERE 1=1")
                    params = []
                    if search_term:
                        q += " AND (item_name LIKE ? OR description LIKE ?)"
                        params += [f"%{search_term}%", f"%{search_term}%"]
                    if category:
                        q += " AND category LIKE ?"; params.append(f"%{category}%")
                    if date_from:
                        q += " AND date_found >= ?"; params.append(date_from)
                    if date_to:
                        q += " AND date_found <= ?"; params.append(date_to)
                    cursor.execute(q, params)
                    found_items = cursor.fetchall()
                else:
                    found_items = []

                all_items = lost_items + found_items
            elif search_term:
                cursor.execute(
                    "SELECT id,item_name,category,'Lost',date_lost,'active'"
                    " FROM lost_items"
                    " WHERE item_name LIKE ? OR description LIKE ?",
                    (f"%{search_term}%", f"%{search_term}%"))
                lost_items = cursor.fetchall()
                cursor.execute(
                    "SELECT id,item_name,category,'Found',date_found,'active'"
                    " FROM found_items"
                    " WHERE item_name LIKE ? OR description LIKE ?",
                    (f"%{search_term}%", f"%{search_term}%"))
                found_items = cursor.fetchall()
                all_items = lost_items + found_items
            else:
                cursor.execute(
                    "SELECT id,item_name,category,'Lost',date_lost,'active'"
                    " FROM lost_items")
                lost_items = cursor.fetchall()
                cursor.execute(
                    "SELECT id,item_name,category,'Found',date_found,'active'"
                    " FROM found_items")
                found_items = cursor.fetchall()
                all_items = lost_items + found_items

            conn.close()
            for display_id, row in enumerate(all_items, 1):
                self._tree.insert('', 'end', values=(display_id,) + row[1:])
        except Exception as e:
            messagebox.showerror("Database Error", str(e), parent=self._root())

    def _search_items(self):
        self._load_items(search_term=self._search_var.get().strip())

    def _refresh_table(self):
        self._search_var.set("")
        self._load_items()
        messagebox.showinfo("Refresh", "Table refreshed successfully!",
                             parent=self._root())

    # Report Lost Item modal

    def _report_lost_item(self):
        if self._report_lost_win is not None and self._report_lost_win.winfo_exists():
            self._report_lost_win.lift()
            return

        win = Toplevel(self._root())
        win.title("Report Lost Item")
        _center(win, 1100, 600)
        win.minsize(1100, 600)
        win.resizable(True, True)
        win.configure(bg="black")
        win.grab_set()
        win.transient(self._root())
        self._report_lost_win = win

        def on_closing():
            self._report_lost_win = None
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", on_closing)

        hdr = Frame(win, bg="#FF3300", height=60)
        hdr.pack(fill=X)
        hdr.pack_propagate(False)
        Label(hdr, text="Report Lost Item",
              font=("Arial", 18, "bold"), bg="#FF3300", fg="white"
              ).pack(pady=15)

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
                messagebox.showinfo("Success", "Lost item reported successfully!",
                                     parent=win)
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

    # Report Found Item modal

    def _report_found_item(self):
        if self._report_found_win is not None and self._report_found_win.winfo_exists():
            self._report_found_win.lift()
            return

        win = Toplevel(self._root())
        win.title("Report Found Item")
        _center(win, 1100, 600)
        win.minsize(1100, 600)
        win.resizable(True, True)
        win.configure(bg="black")
        win.grab_set()
        win.transient(self._root())
        self._report_found_win = win

        def on_closing():
            self._report_found_win = None
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", on_closing)

        hdr = Frame(win, bg="#4CAF50", height=60)
        hdr.pack(fill=X)
        hdr.pack_propagate(False)
        Label(hdr, text="Report Found Item",
              font=("Arial", 18, "bold"), bg="#4CAF50", fg="white"
              ).pack(pady=15)

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
                messagebox.showinfo("Success", "Found item reported successfully!",
                                     parent=win)
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

    # Advanced Search modal

    def _advanced_search(self):
        if self._adv_search_win is not None and self._adv_search_win.winfo_exists():
            self._adv_search_win.lift()
            return

        win = Toplevel(self._root())
        win.title("Advanced Search")
        _center(win, 1100, 600)
        win.minsize(1100, 600)
        win.resizable(True, True)
        win.configure(bg="black")
        win.grab_set()
        win.transient(self._root())
        self._adv_search_win = win

        def on_closing():
            self._adv_search_win = None
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", on_closing)

        hdr = Frame(win, bg="#9C27B0", height=60)
        hdr.pack(fill=X)
        hdr.pack_propagate(False)
        Label(hdr, text="Advanced Search",
              font=("Arial", 18, "bold"), bg="#9C27B0", fg="white"
              ).pack(pady=15)

        form_frame = Frame(win, bg="black")
        form_frame.pack(fill=BOTH, expand=True, padx=40, pady=30)

        y_pos = 50
        Label(form_frame, text="Search Term:",
              font=("Arial", 12), bg="black", fg="white").place(x=50, y=y_pos)
        search_term = Entry(form_frame, width=30, font=("Arial", 11),
                            bd=1, relief="solid")
        search_term.place(x=200, y=y_pos)

        y_pos += 40
        Label(form_frame, text="Item Type:",
              font=("Arial", 12), bg="black", fg="white").place(x=50, y=y_pos)
        item_type = ttk.Combobox(form_frame, width=28, font=("Arial", 11),
                                  state="readonly")
        item_type['values'] = ("All", "Lost", "Found")
        item_type.set("All")
        item_type.place(x=200, y=y_pos)

        y_pos += 40
        Label(form_frame, text="Category:",
              font=("Arial", 12), bg="black", fg="white").place(x=50, y=y_pos)
        category = Entry(form_frame, width=30, font=("Arial", 11),
                         bd=1, relief="solid")
        category.place(x=200, y=y_pos)

        y_pos += 40
        Label(form_frame, text="Date From:",
              font=("Arial", 12), bg="black", fg="white").place(x=50, y=y_pos)
        date_from = Entry(form_frame, width=30, font=("Arial", 11),
                          bd=1, relief="solid")
        date_from.place(x=200, y=y_pos)

        y_pos += 40
        Label(form_frame, text="Date To:",
              font=("Arial", 12), bg="black", fg="white").place(x=50, y=y_pos)
        date_to = Entry(form_frame, width=30, font=("Arial", 11),
                        bd=1, relief="solid")
        date_to.place(x=200, y=y_pos)

        def do_search():
            filters = {
                "type":      item_type.get(),
                "category":  category.get().strip(),
                "date_from": date_from.get().strip(),
                "date_to":   date_to.get().strip(),
            }
            self._load_items(
                search_term=search_term.get().strip(), filters=filters)
            on_closing()

        y_pos += 50
        Button(form_frame, text="Search", font=("Arial", 12, "bold"),
               bg="#9C27B0", fg="white", width=12,
               command=do_search).place(x=200, y=y_pos)
        Button(form_frame, text="Cancel", font=("Arial", 12, "bold"),
               bg="#dc3545", fg="white", width=12,
               command=on_closing).place(x=350, y=y_pos)
