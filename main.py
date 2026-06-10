import os
import sys
import hashlib
import secrets
import sqlite3
from tkinter import *
from tkinter import messagebox
from db_connection import get_db_connection, get_resource_path


# Utilities

def _center(win, w, h):
    win.update_idletasks()
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    win.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")


def _hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 260000)
    return f"pbkdf2:sha256:{salt}:{dk.hex()}"


def _verify_password(stored: str, provided: str) -> bool:
    if stored.startswith("pbkdf2:sha256:"):
        parts = stored.split(":")
        if len(parts) == 4:
            _, _, salt, stored_hash = parts
            dk = hashlib.pbkdf2_hmac('sha256', provided.encode(), salt.encode(), 260000)
            return dk.hex() == stored_hash
    return stored == provided  # plain-text fallback for migrating old accounts


def _authenticate(username: str, password: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT password, user_type FROM users WHERE username=?", (username,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return None
    stored_pw, user_type = row
    if _verify_password(stored_pw, password):
        if not stored_pw.startswith("pbkdf2:"):   # migrate on first login
            cur.execute("UPDATE users SET password=? WHERE username=?",
                        (_hash_password(password), username))
            conn.commit()
        conn.close()
        return user_type
    conn.close()
    return None


def _register_user(username, password, full_name, email, phone) -> bool:
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (username,password,full_name,email,phone,user_type)"
            " VALUES (?,?,?,?,?,?)",
            (username, _hash_password(password), full_name, email, phone, 'user')
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def _initialize_db():
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            # Add missing columns to older databases
            for col_def in ("phone TEXT", "user_type TEXT DEFAULT 'user'"):
                try:
                    cur.execute(f"ALTER TABLE users ADD COLUMN {col_def}")
                except sqlite3.OperationalError:
                    pass
            # Migrate any remaining plain-text admin passwords to pbkdf2
            cur.execute(
                "SELECT id, password FROM users WHERE user_type='admin'"
            )
            for row_id, pw in cur.fetchall():
                if pw and not pw.startswith("pbkdf2:"):
                    cur.execute(
                        "UPDATE users SET password=? WHERE id=?",
                        (_hash_password(pw), row_id),
                    )
            # Seed a default admin account if no admin exists at all
            cur.execute("SELECT COUNT(*) FROM users WHERE user_type='admin'")
            if cur.fetchone()[0] == 0:
                cur.execute(
                    "INSERT INTO users (username,password,full_name,email,phone,user_type)"
                    " VALUES (?,?,?,?,?,?)",
                    ("admin", _hash_password("admin@123"),
                     "Administrator", "", "", "admin"),
                )
            conn.commit()
    except sqlite3.Error as e:
        print(f"Database init error: {e}")


# Original gradient formulas

def _login_grad(i, h):
    """Original get_gradient_color formula, scaled to actual window height."""
    j = i * 600 / max(h, 1)
    r = min(30 + int(j * 0.2), 255)
    g = min(30 + int(j * 0.1), 255)
    b = min(100 + int(j * 0.2), 255)
    return f'#{r:02x}{g:02x}{b:02x}'


def _reg_grad(i, h):
    """Original get_gradient_color_1 formula (true interpolation), scaled to height."""
    j = min(i * 600 / max(h, 1), 599)
    ratio = j / 599
    r = int(0   + 135 * ratio)
    g = int(24  + 182 * ratio)
    b = int(72  + 163 * ratio)
    return f'#{r:02x}{g:02x}{b:02x}'


# App controller

class App:
    def __init__(self):
        _initialize_db()

        self.root = Tk()
        self.root.title("Lost & Found Desktop - Login")
        self.root.minsize(1100, 600)
        _center(self.root, 1100, 600)
        self.root.resizable(True, True)
        self.root.state("zoomed")
        self._set_icon()

        self.container = Frame(self.root)
        self.container.pack(fill=BOTH, expand=True)

        self.current_user = None
        self.current_user_type = None

        self.show_login()
        self.root.mainloop()

    def _set_icon(self):
        path = get_resource_path(os.path.join('assets', 'icon.ico'))
        if os.path.exists(path):
            try:
                self.root.iconbitmap(default=path)
            except Exception:
                pass

    def _clear(self):
        for w in self.container.winfo_children():
            w.destroy()

    def show_login(self):
        self._clear()
        self.root.title("Lost & Found Desktop - Login")
        LoginPage(self.container, self)

    def show_register(self):
        RegisterModal(self.root, self)

    def show_admin(self, username: str):
        self._clear()
        self.root.title("Lost & Found - Admin Control Panel")
        try:
            from admin_page import AdminPage
            page = AdminPage(self.container, self, username)
            page.pack(fill=BOTH, expand=True)
            self.container.update_idletasks()
        except Exception as exc:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error",
                f"Admin Panel failed to load:\n{exc}",
                parent=self.root)
            self.show_login()

    def show_user(self, username: str):
        self._clear()
        self.root.title("Lost & Found - Welcome User")
        try:
            from user_page import UserPage
            page = UserPage(self.container, self, username)
            page.pack(fill=BOTH, expand=True)
            self.container.update_idletasks()
        except Exception as exc:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error",
                f"User Panel failed to load:\n{exc}",
                parent=self.root)
            self.show_login()

    def logout(self):
        self.current_user = None
        self.current_user_type = None
        self.show_login()


# Login page
# Visual design is 100% faithful to the original main.py canvas-based layout.
# Responsiveness is added via <Configure> binding that scales all positions
# proportionally from the original 1100×600 reference design.

class LoginPage(Frame):
    _BLINK_TEXTS = [
        "Every item has a story. Find yours!",
        "Don't just wish it back, find it here.",
        "Lost, but not forgotten. Found, and reunited.",
        "Dedicated to reuniting you with what's yours.",
        "Find what you've lost. Return what you've found.",
        "Building bridges between the lost and the found.",
        "Helping forgotten items remember their way home.",
    ]

    def __init__(self, parent, app: App):
        super().__init__(parent)
        self.app = app
        self.pack(fill=BOTH, expand=True)

        # Canvas fills the whole frame – same as original canvas.place(relwidth=1,relheight=1)
        self._c = Canvas(self, highlightthickness=0)
        self._c.place(x=0, y=0, relwidth=1, relheight=1)

        # ── Canvas text items (same fonts as original) ────────────────────────
        # Original: Impact 35 bold at y=90
        self._title_id = self._c.create_text(0, 0, text="",
            font=("Impact", 35, "bold"), fill="white", anchor="center")
        # Original: Rockwell 20 at y=135
        self._sub_id = self._c.create_text(0, 0, text="",
            font=("Rockwell", 20), fill="white", anchor="center")
        # Original: Rockwell 20 at y=170  (blink/tagline)
        self._blink_id = self._c.create_text(0, 0, text="",
            font=("Rockwell", 20), fill="white", anchor="center")
        # Footer – originals at y=553, 570, 585
        self._foot1_id = self._c.create_text(0, 0,
            text="Turning 'lost' into 'found' together.",
            font=("Open Sans", 12, "bold"), fill="#000000", anchor="center")
        self._foot2_id = self._c.create_text(0, 0,
            text="Powered by TEAM DOBERMAN",
            font=("Open Sans", 11), fill="#000000", anchor="center")
        self._foot3_id = self._c.create_text(0, 0,
            text="© 2025 All rights reserved",
            font=("Open Sans", 11), fill="#000000", anchor="center")

        # ── Form widgets via canvas.create_window (same as original) ─────────
        # Original: Label Calibri 14, white text, bg = gradient colour at that y
        self._ul = Label(self, text="Username",
                         font=("Calibri", 14), fg="white")
        self._ul_id = self._c.create_window(0, 0,
                         window=self._ul, anchor="center")

        # Original: Entry width=27 Calibri 14
        self._username_entry = Entry(self, width=27, font=("Calibri", 14))
        self._ue_id = self._c.create_window(0, 0,
                         window=self._username_entry, anchor="center")

        # Original: Label Calibri 15, white text
        self._pl = Label(self, text="Password",
                         font=("Calibri", 15), fg="white")
        self._pl_id = self._c.create_window(0, 0,
                         window=self._pl, anchor="center")

        # Original: Entry show="*" width=27 Calibri 14
        self._password_entry = Entry(self, show="*", width=27, font=("Calibri", 14))
        self._pe_id = self._c.create_window(0, 0,
                         window=self._password_entry, anchor="center")

        # Original: Login width=10 Arial 13 skyblue
        self._login_btn = Button(self, text="Login", width=10,
            fg="black", font=("Arial", 13), bg="skyblue",
            command=self._handle_login)
        self._lbtn_id = self._c.create_window(0, 0,
                          window=self._login_btn, anchor="center")

        # Original: Register width=12 Arial 13 lightgreen
        self._register_btn = Button(self, text="Register", width=12,
            fg="black", font=("Arial", 13), bg="lightgreen",
            command=self.app.show_register)
        self._rbtn_id = self._c.create_window(0, 0,
                          window=self._register_btn, anchor="center")

        self.bind("<Configure>", self._on_resize)
        self.after(100, self._start_animations)

    # ── Resize handler – repositions everything proportionally ────────────────
    def _on_resize(self, event=None):
        if event and event.widget is not self:
            return
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 10 or h < 10:
            return

        # Avoid redundant redraws while drag-resizing
        new_size = (w, h)
        if getattr(self, '_last_size', None) == new_size:
            return
        self._last_size = new_size

        # Redraw gradient using original formula, scaled to current height
        self._c.delete("grad")
        for i in range(h):
            self._c.create_line(0, i, w, i, fill=_login_grad(i, h), tags="grad")
        self._c.tag_lower("grad")   # keep gradient behind text and widget windows

        cx = w // 2   # horizontal centre  (original used x=550 in 1100px wide)
        # label x: original was 450/1100, entry/button x: original was 550/1100
        lx = int(w * 450 / 1100)
        ex = int(w * 550 / 1100)

        # Canvas text items – y proportional to original positions in 600px
        self._c.coords(self._title_id,  cx, int(h *  90 / 600))
        self._c.coords(self._sub_id,    cx, int(h * 135 / 600))
        self._c.coords(self._blink_id,  cx, int(h * 170 / 600))
        self._c.coords(self._foot1_id,  cx, int(h * 553 / 600))
        self._c.coords(self._foot2_id,  cx, int(h * 570 / 600))
        self._c.coords(self._foot3_id,  cx, int(h * 585 / 600))

        # Form widgets – positions proportional to original 1100×600 design
        ul_y = int(h * 265 / 600)
        self._c.coords(self._ul_id, lx, ul_y)
        self._ul.config(bg=_login_grad(ul_y, h))

        ue_y = int(h * 290 / 600)
        self._c.coords(self._ue_id, ex, ue_y)

        pl_y = int(h * 325 / 600)
        self._c.coords(self._pl_id, lx, pl_y)
        self._pl.config(bg=_login_grad(pl_y, h))

        pe_y = int(h * 350 / 600)
        self._c.coords(self._pe_id, ex, pe_y)

        self._c.coords(self._lbtn_id, ex, int(h * 430 / 600))
        self._c.coords(self._rbtn_id, ex, int(h * 480 / 600))

    # ── Login handler ─────────────────────────────────────────────────────────
    def _handle_login(self):
        username = self._username_entry.get().strip()
        password = self._password_entry.get()
        if not username or not password:
            messagebox.showerror("Error",
                "Please enter both username and password!",
                parent=self.app.root)
            return
        user_type = _authenticate(username, password)
        if user_type:
            self.app.current_user = username
            role = str(user_type).strip().lower()
            self.app.current_user_type = role
            messagebox.showinfo("Success",
                f"Welcome back, {username}!", parent=self.app.root)
            if role == 'admin':
                self.app.show_admin(username)
            else:
                self.app.show_user(username)
        else:
            messagebox.showerror("Error", "Invalid username or password!",
                parent=self.app.root)
            self._password_entry.delete(0, END)

    # ── Animations (ported from original, using self.after / self._c) ─────────
    def _start_animations(self):
        self._typewriter(
            "Lost & Found Desktop App", self._title_id, delay=100,
            on_complete=lambda: self._typewriter(
                "Connecting what's lost with those who are looking!",
                self._sub_id, delay=100,
                on_complete=lambda: self._run_blink_sequence(0, is_first=True)
            )
        )

    def _typewriter(self, text, item_id, delay=100, idx=0, on_complete=None):
        try:
            self._c.itemconfig(item_id, text=text[:idx])
        except TclError:
            return
        if idx < len(text):
            self.after(delay, self._typewriter, text, item_id, delay, idx + 1, on_complete)
        elif on_complete:
            on_complete()

    def _blink_text_effect(self, current_text, next_text, item_id,
                           delay=3000, fade_steps=10, on_complete=None):
        try:
            self._c.itemconfig(item_id, text=current_text)
        except TclError:
            return

        def blend(c1, c2, t):
            return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

        white = (255, 255, 255)
        bg    = (63, 46, 133)      # original #3f2e85 – matches gradient at y≈170

        def fade_out(step):
            t = step / fade_steps
            r, g, b = blend(white, bg, t)
            try:
                self._c.itemconfig(item_id, fill=f'#{r:02x}{g:02x}{b:02x}')
            except TclError:
                return
            if step < fade_steps:
                self.after(delay // (fade_steps * 2), fade_out, step + 1)
            else:
                try:
                    self._c.itemconfig(item_id, text=next_text)
                except TclError:
                    return
                fade_in(0)

        def fade_in(step):
            t = step / fade_steps
            r, g, b = blend(bg, white, t)
            try:
                self._c.itemconfig(item_id, fill=f'#{r:02x}{g:02x}{b:02x}')
            except TclError:
                return
            if step < fade_steps:
                self.after(delay // (fade_steps * 2), fade_in, step + 1)
            else:
                self.after(2550, lambda: on_complete() if on_complete else None)

        fade_out(0)

    def _run_blink_sequence(self, index=0, is_first=False):
        texts = self._BLINK_TEXTS
        cur_text  = texts[index]
        next_idx  = (index + 1) % len(texts)
        next_text = texts[next_idx]
        if is_first:
            try:
                self._c.itemconfig(self._blink_id, text=cur_text, fill="#3f2e85")
            except TclError:
                return
            self._fade_in_first(0, cur_text, next_text)
        else:
            self._blink_text_effect(
                cur_text, next_text, self._blink_id, delay=2000, fade_steps=20,
                on_complete=lambda: self._run_blink_sequence(next_idx)
            )

    def _fade_in_first(self, step, cur_text, next_text, fade_steps=20):
        def blend(c1, c2, t):
            return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
        bg    = (63, 46, 133)
        white = (255, 255, 255)
        t = step / fade_steps
        r, g, b = blend(bg, white, t)
        try:
            self._c.itemconfig(self._blink_id, fill=f'#{r:02x}{g:02x}{b:02x}')
        except TclError:
            return
        if step < fade_steps:
            self.after(50, self._fade_in_first,
                       step + 1, cur_text, next_text, fade_steps)
        else:
            self.after(3000, lambda: self._blink_text_effect(
                cur_text, next_text, self._blink_id, delay=2000, fade_steps=20,
                on_complete=lambda: self._run_blink_sequence(1)
            ))


# Register modal
# Visual design is 100% faithful to the original register_user() Toplevel.
# Same gradient, same fonts, same labels, same button colours.
# Fixed: canvas positions are now proportional so the window can be resized.

class RegisterModal(Toplevel):
    def __init__(self, parent, app: App):
        super().__init__(parent)
        self.app = app
        self.title("User Registration")
        self.minsize(1100, 600)
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()
        _center(self, 1100, 600)
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        # Canvas with gradient – same as original
        self._c = Canvas(self, highlightthickness=0)
        self._c.place(x=0, y=0, relwidth=1, relheight=1)

        # Title – original: Impact 30 at y=70
        self._title_id = self._c.create_text(0, 0,
            text="User Registration",
            font=("Impact", 30), fill="white", anchor="center")

        # ── Build form widgets (same styling as original) ─────────────────────
        def _lbl(text, bg):
            return Label(self, text=text, font=("Arial", 12, "bold"),
                         fg="white", bg=bg)

        def _entry(show=""):
            kw = {"show": show} if show else {}
            return Entry(self, width=25, font=("Arial", 11),
                         bd=2, highlightthickness=0, **kw)

        # We'll set the bg colour properly in _on_resize, use a placeholder now
        p = "#001848"   # start colour placeholder
        self._lbl_un  = _lbl("Username:",         p)
        self._lbl_fn  = _lbl("Full Name:",         p)
        self._lbl_em  = _lbl("Email:",             p)
        self._lbl_ph  = _lbl("Phone:",             p)
        self._lbl_pw  = _lbl("Password:",          p)
        self._lbl_cf  = _lbl("Confirm Password:",  p)

        self._en_un = _entry()
        self._en_fn = _entry()
        self._en_em = _entry()
        self._en_ph = _entry()
        self._en_pw = _entry("*")
        self._en_cf = _entry("*")

        # Buttons – original: lightgreen Register, lightcoral Cancel
        self._btn_reg = Button(self, text="Register", width=12,
            font=("Arial", 12), bg="lightgreen", fg="black",
            command=self._handle_registration)
        self._btn_can = Button(self, text="Cancel", width=10,
            font=("Arial", 12), bg="lightcoral", fg="black",
            command=self._on_closing)

        # Footer – original: Arial 12 bold #111111 at y=550
        self._footer_id = self._c.create_text(0, 0,
            text="Join the Lost & Found community!",
            font=("Arial", 12, "bold"), fill="#111111", anchor="center")

        # Add all widgets to canvas (positions set in _on_resize)
        self._lbl_un_id  = self._c.create_window(0, 0, window=self._lbl_un,  anchor="center")
        self._lbl_fn_id  = self._c.create_window(0, 0, window=self._lbl_fn,  anchor="center")
        self._lbl_em_id  = self._c.create_window(0, 0, window=self._lbl_em,  anchor="center")
        self._lbl_ph_id  = self._c.create_window(0, 0, window=self._lbl_ph,  anchor="center")
        self._lbl_pw_id  = self._c.create_window(0, 0, window=self._lbl_pw,  anchor="center")
        self._lbl_cf_id  = self._c.create_window(0, 0, window=self._lbl_cf,  anchor="center")
        self._en_un_id   = self._c.create_window(0, 0, window=self._en_un,   anchor="center")
        self._en_fn_id   = self._c.create_window(0, 0, window=self._en_fn,   anchor="center")
        self._en_em_id   = self._c.create_window(0, 0, window=self._en_em,   anchor="center")
        self._en_ph_id   = self._c.create_window(0, 0, window=self._en_ph,   anchor="center")
        self._en_pw_id   = self._c.create_window(0, 0, window=self._en_pw,   anchor="center")
        self._en_cf_id   = self._c.create_window(0, 0, window=self._en_cf,   anchor="center")
        self._btn_reg_id = self._c.create_window(0, 0, window=self._btn_reg, anchor="center")
        self._btn_can_id = self._c.create_window(0, 0, window=self._btn_can, anchor="center")

        self.bind("<Configure>", self._on_resize)

    def _on_closing(self):
        self.destroy()

    def _on_resize(self, event=None):
        if event and event.widget is not self:
            return
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 10 or h < 10:
            return
        new_size = (w, h)
        if getattr(self, '_last_size', None) == new_size:
            return
        self._last_size = new_size

        # Redraw gradient
        self._c.delete("grad")
        for i in range(h):
            self._c.create_line(0, i, w, i, fill=_reg_grad(i, h), tags="grad")
        self._c.tag_lower("grad")   # keep gradient behind text and widget windows

        cx = w // 2
        # Original: labels at x=400, entries at x=700 in 1100px
        lx = int(w * 400 / 1100)
        ex = int(w * 700 / 1100)

        # Title at y=70 in 600px
        self._c.coords(self._title_id, cx, int(h * 70 / 600))

        # Fields – original y positions: 120, 160, 210, 260, 310, 360
        orig_ys = [120, 160, 210, 260, 310, 360]
        lbl_ids = [self._lbl_un_id, self._lbl_fn_id, self._lbl_em_id,
                   self._lbl_ph_id, self._lbl_pw_id, self._lbl_cf_id]
        ent_ids = [self._en_un_id, self._en_fn_id, self._en_em_id,
                   self._en_ph_id, self._en_pw_id, self._en_cf_id]
        lbls    = [self._lbl_un, self._lbl_fn, self._lbl_em,
                   self._lbl_ph, self._lbl_pw, self._lbl_cf]

        for oy, lid, eid, lw in zip(orig_ys, lbl_ids, ent_ids, lbls):
            ny = int(h * oy / 600)
            self._c.coords(lid, lx, ny)
            self._c.coords(eid, ex, ny)
            lw.config(bg=_reg_grad(ny, h))   # match gradient at current y

        # Buttons – original: Register at x=475, Cancel at x=625, y=450
        btn_y = int(h * 450 / 600)
        self._c.coords(self._btn_reg_id, int(w * 475 / 1100), btn_y)
        self._c.coords(self._btn_can_id, int(w * 625 / 1100), btn_y)

        # Footer at y=550
        self._c.coords(self._footer_id, cx, int(h * 550 / 600))

    def _handle_registration(self):
        username = self._en_un.get().strip()
        full_name = self._en_fn.get().strip()
        email     = self._en_em.get().strip()
        phone     = self._en_ph.get().strip()
        password  = self._en_pw.get()
        confirm   = self._en_cf.get()

        if not all([username, full_name, email, phone, password, confirm]):
            messagebox.showerror("Error", "Please fill all fields!", parent=self)
            return
        if "@" not in email or "." not in email:
            messagebox.showerror("Error",
                "Please enter a valid email address!", parent=self)
            return
        if not phone.isdigit() or len(phone) < 10:
            messagebox.showerror("Error",
                "Please enter a valid phone number (at least 10 digits)!", parent=self)
            return
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match!", parent=self)
            return
        if len(password) < 6:
            messagebox.showerror("Error",
                "Password must be at least 6 characters!", parent=self)
            return
        if _register_user(username, password, full_name, email, phone):
            messagebox.showinfo("Success",
                f"Registration successful! Welcome, {full_name}!", parent=self)
            for e in (self._en_un, self._en_fn, self._en_em,
                      self._en_ph, self._en_pw, self._en_cf):
                e.delete(0, END)
            self.destroy()
        else:
            messagebox.showerror("Error",
                "Username or email already exists!", parent=self)


if __name__ == "__main__":
    App()
