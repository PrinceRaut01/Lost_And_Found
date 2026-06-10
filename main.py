# Utility function to center a window on the screen
def center_window(win, width, height):
    win.update_idletasks()
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")
from tkinter import *
from tkinter import messagebox
import os
import subprocess
import sys
import sqlite3
from db_connection import get_db_connection, get_resource_path


if '--admin' in sys.argv:
    import admin_page  # noqa: F401
    raise SystemExit(0)

if '--user' in sys.argv:
    import user_page  # noqa: F401
    raise SystemExit(0)

# Database initialization 
def initialize_db():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Add phone column if not exists (for existing DBs)
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN phone TEXT")
            except sqlite3.OperationalError:
                pass  # Column already exists
            # Add user_type column if not exists (for existing DBs)
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN user_type TEXT DEFAULT 'user'")
            except sqlite3.OperationalError:
                pass  # Column already exists
            conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")

initialize_db()


def set_window_icon(win):
    icon_path = get_resource_path(os.path.join('assets', 'icon.ico'))
    if os.path.exists(icon_path):
        try:
            win.iconbitmap(default=icon_path)
        except Exception:
            pass

# User registration logic
def register_user_to_db(username, password, full_name, email, phone):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password, full_name, email, phone, user_type) VALUES (?, ?, ?, ?, ?, ?)",
                       (username, password, full_name, email, phone, 'user'))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


root = Tk()
root.title("Lost & Found Desktop - Login")
center_window(root, 1100, 600)
root.minsize(1100, 600)
root.resizable(True, True)
root.state("zoomed")
set_window_icon(root)

# Setting the background color
canvas = Canvas(root, width=900, height=600, highlightthickness=0)
canvas.place(x=0, y=0, relwidth=1, relheight=1)

# Drawing a gradient from darkblue to skyblue/lightblue
def get_gradient_color(i):
    # Gradient from dark blue (#001848) to light blue (#87ceeb)
    start_rgb = (0, 24, 72)      # dark blue
    end_rgb = (135, 206, 235)    # light blue (skyblue)
    ratio = i / 599
    r = 30 + int(i * 0.2)
    g = 30 + int(i * 0.1)
    b = 100 + int(i * 0.2)
    r, g, b = min(r, 255), min(g, 255), min(b, 255)
    return f'#{r:02x}{g:02x}{b:02x}'

root.update_idletasks()  # Ensure geometry is updated
window_width = root.winfo_width()
for i in range(600):  # window height
    color = get_gradient_color(i)
    canvas.create_line(0, i, window_width, i, fill=color)
    canvas.create_line(0, i+1, window_width, i+1, fill=color)  # fill the gap for smoother gradient

for i in range(600):  # window height
    color = get_gradient_color(i)
    canvas.create_line(0, i, 1000, i, fill=color)
    canvas.create_line(0, i+1, 1000, i+1, fill=color)  # fill the gap for smoother gradient

# Global variable for register window
register_window = None

# Function to open admin control panel
def open_admin_panel():
    try:
        # Clear login fields for security
        username_entry.delete(0, END)
        password_entry.delete(0, END)
        root.destroy()
        if getattr(sys, 'frozen', False):
            command = [sys.executable, '--admin']
        else:
            command = [sys.executable, os.path.abspath(__file__), '--admin']
        subprocess.run(command, check=False)
    except Exception as e:
        messagebox.showerror("Error", f"Could not open admin page: {str(e)}")
        root.deiconify()
        
def open_user_page():
    try:
        username_entry.delete(0, END)
        password_entry.delete(0, END)
        root.destroy()
        if getattr(sys, 'frozen', False):
            command = [sys.executable, '--user']
        else:
            command = [sys.executable, os.path.abspath(__file__), '--user']
        subprocess.run(command, check=False)
    except Exception as e:
        messagebox.showerror("Error", f"Could not open user page: {str(e)}")
        root.deiconify() 

# Function to handle login
def authenticate_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_type FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()
    if user:
        return user[0]  # user_type
    return None
def handle_login():
    username = username_entry.get().strip()
    password = password_entry.get()
    
    # Basic validation
    if not username or not password:
        messagebox.showerror("Error", "Please enter both username and password!")
        return
    
    user_type = authenticate_user(username, password)
    if user_type:
        messagebox.showinfo("Success", f"Welcome back, {username}!")
        if user_type == 'admin':
            open_admin_panel()
        else:
            open_user_page()
    else:
        messagebox.showerror("Error", "Invalid username or password!")
        password_entry.delete(0, END)  

# function for registering a new user
def register_user():
    global register_window
    if register_window is not None and register_window.winfo_exists():
        register_window.lift()
        return

    register_window = Toplevel()
    register_window.title("User Registration")
    center_window(register_window, 1100, 600)
    register_window.minsize(1100, 600)
    register_window.resizable(True, True)
    register_window.grab_set()  # Make window modal
    register_window.transient(root)  # Keep on top of parent

    # Create canvas for gradient background
    reg_canvas = Canvas(register_window, width=1100, height=600, highlightthickness=0,)
    reg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
    def get_gradient_color_1(i):
        # Gradient from dark blue (#001848) to light blue (#87ceeb)
        start_rgb = (0, 24, 72)      # dark blue
        end_rgb = (135, 206, 235)    # light blue (skyblue)
        ratio = i / 599
        r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * ratio)
        g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * ratio)
        b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * ratio)
        return f'#{r:02x}{g:02x}{b:02x}'
    get_gradient_color_1
    for i in range(600):  # window height
        color = get_gradient_color_1(i)
        reg_canvas.create_line(0, i, 1100, i, fill=color)
        reg_canvas.create_line(0, i+1, 1100, i+1, fill=color)  # fill the gap for smoother gradient

    def on_closing():
        global register_window
        register_window.destroy()
        register_window = None

    register_window.protocol("WM_DELETE_WINDOW", on_closing)

    lbl_registration = Label(register_window, text="User Registration", font=("Impact", 30), fg="white", bg=get_gradient_color_1(70))
    reg_canvas.create_window(550, 70, window=lbl_registration, anchor="center")

    # Username
    lbl_username = Label(register_window, text="Username:", font=("Arial", 12, "bold"), fg="white", bg=get_gradient_color_1(120))
    reg_canvas.create_window(400, 120, window=lbl_username, anchor="center")
    username_entry_reg = Entry(register_window, width=25, font=("Arial", 11), bd=2, highlightthickness=0)
    reg_canvas.create_window(700, 120, window=username_entry_reg, anchor="center")

    # Full Name
    lbl_full_name = Label(register_window, text="Full Name:", font=("Arial", 12, "bold"), fg="white", bg=get_gradient_color_1(180))
    reg_canvas.create_window(400, 160, window=lbl_full_name, anchor="center")
    full_name_entry = Entry(register_window, width=25, font=("Arial", 11), bd=2, highlightthickness=0)
    reg_canvas.create_window(700, 160, window=full_name_entry, anchor="center")

    # Email
    lbl_email = Label(register_window, text="Email:", font=("Arial", 12, "bold"), fg="white", bg=get_gradient_color_1(230))
    reg_canvas.create_window(400, 210, window=lbl_email, anchor="center")
    email_entry = Entry(register_window, width=25, font=("Arial", 11), bd=2, highlightthickness=0)
    reg_canvas.create_window(700, 210, window=email_entry, anchor="center")

    # Phone
    lbl_phone = Label(register_window, text="Phone:", font=("Arial", 12, "bold"), fg="white", bg=get_gradient_color_1(280))
    reg_canvas.create_window(400, 260, window=lbl_phone, anchor="center")
    phone_entry = Entry(register_window, width=25, font=("Arial", 11), bd=2, highlightthickness=0)
    reg_canvas.create_window(700, 260, window=phone_entry, anchor="center")

    # Password
    lbl_password = Label(register_window, text="Password:", font=("Arial", 12, "bold"), fg="white", bg=get_gradient_color_1(330))
    reg_canvas.create_window(400, 310, window=lbl_password, anchor="center")
    password_entry_reg = Entry(register_window, show="*", width=25, font=("Arial", 11), bd=2, highlightthickness=0)
    reg_canvas.create_window(700, 310, window=password_entry_reg, anchor="center")

    # Confirm Password
    lbl_confirm_password = Label(register_window, text="Confirm Password:", font=("Arial", 12, "bold"), fg="white", bg=get_gradient_color_1(380))
    reg_canvas.create_window(400, 360, window=lbl_confirm_password, anchor="center")
    confirm_password_entry = Entry(register_window, show="*", width=25, font=("Arial", 11), bd=2, highlightthickness=0)
    reg_canvas.create_window(700, 360, window=confirm_password_entry, anchor="center")

    def handle_registration():
        username = username_entry_reg.get().strip()
        full_name = full_name_entry.get().strip()
        email = email_entry.get().strip()
        phone = phone_entry.get().strip()
        password = password_entry_reg.get()
        confirm_password = confirm_password_entry.get()
        if not all([username, full_name, email, phone, password, confirm_password]):
            messagebox.showerror("Error", "Please fill all fields!")
            return
        if "@" not in email or "." not in email:
            messagebox.showerror("Error", "Please enter a valid email address!")
            return
        if not phone.isdigit() or len(phone) < 10:
            messagebox.showerror("Error", "Please enter a valid phone number (at least 10 digits)!")
            return
        result = None
        if password != confirm_password:
            result = "Passwords do not match!"
        elif len(password) < 6:
            result = "Password must be at least 6 characters!"
        elif register_user_to_db(username, password, full_name, email, phone):
            result = f"Registration successful! Welcome, {full_name}!"
        else:
            result = "Username or email already exists!"

        if result.startswith("Registration successful!"):
            messagebox.showinfo("Success", result)
            # Clear the registration fields
            username_entry_reg.delete(0, END)
            full_name_entry.delete(0, END)
            email_entry.delete(0, END)
            phone_entry.delete(0, END)
            password_entry_reg.delete(0, END)
            confirm_password_entry.delete(0, END)
            register_window.destroy()
            # After registration, just close the registration window and show the login page again
            # (root window remains open)
        else:
            messagebox.showerror("Error", result)

    # Center the buttons with original styling to match login page
    submit_button = Button(register_window, text="Register", width=12, font=("Arial", 12), bg="lightgreen", fg="black", command=handle_registration)
    reg_canvas.create_window(475, 450, window=submit_button, anchor="center")
    cancel_button = Button(register_window, text="Cancel", width=10, font=("Arial", 12), bg="lightcoral", fg="black", command=on_closing)
    reg_canvas.create_window(625, 450, window=cancel_button, anchor="center")

    # Add footer similar to login page (centered for 1100px width)
    footer_reg = Label(register_window, text="Join the Lost & Found community!", font=("Arial", 12, "bold"), fg="#111111", bg=get_gradient_color_1(550))
    reg_canvas.create_window(550, 550, window=footer_reg, anchor="center")

# --- Login fields directly on canvas ---
# Username field - properly centered
username_label = Label(root, text="Username", font=("Calibri", 14), bg=get_gradient_color(250), fg="white")
canvas.create_window(450, 265, window=username_label, anchor="center")

username_entry = Entry(root, width=27, font=("Calibri", 14) )
canvas.create_window(550, 290, window=username_entry, anchor="center")

# Password field - properly centered
password_label = Label(root, text="Password", font=("Calibri", 15), bg=get_gradient_color(300), fg="white")
canvas.create_window(450, 325, window=password_label, anchor="center")

password_entry = Entry(root, show="*", width=27, font=("Calibri", 14) )
canvas.create_window(550, 350, window=password_entry, anchor="center")

# Buttons - centered horizontally with original styling
login_btn = Button(root, text="Login", width=10, fg="black", font=("Arial", 13), bg="skyblue", command=handle_login)
canvas.create_window(550, 430, window=login_btn, anchor="center")

register_btn = Button(root, text="Register", width=12, fg="black", font=("Arial", 13), bg="lightgreen", command=register_user)
canvas.create_window(550, 480, window=register_btn, anchor="center")

# --- App name typewriter effect ---
def blink_text_effect(current_text, next_text, canvas, item_id, delay=3000, fade_steps=10, on_complete=None):
    # Set the canvas item's text to the current text
    canvas.itemconfig(item_id, text=current_text)
    # Fade colors from white to transparent and back
    def fade_out(step):
        # Fade from white to background color (#3f2e85)
        def blend_color(c1, c2, t):
            return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
        white_rgb = (255, 255, 255)
        # Convert #3f2e85 to RGB
        bg_rgb = (63, 46, 133)  # #3f2e85 in RGB
        t = step / fade_steps
        r, g, b = blend_color(white_rgb, bg_rgb, t)
        color = f'#{r:02x}{g:02x}{b:02x}'
        canvas.itemconfig(item_id, fill=color)
        if step < fade_steps:
            root.after(delay // (fade_steps * 2), fade_out, step + 1)
        else:
            # Text is now fully faded out, change to next text and fade in
            canvas.itemconfig(item_id, text=next_text)
            fade_in(0)

    def fade_in(step):
        # Fade from background color (#3f2e85) to white
        def blend_color(c1, c2, t):
            return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
        # Convert #3f2e85 to RGB
        bg_rgb = (63, 46, 133)  # #3f2e85 in RGB
        white_rgb = (255, 255, 255)
        t = step / fade_steps
        r, g, b = blend_color(bg_rgb, white_rgb, t)
        color = f'#{r:02x}{g:02x}{b:02x}'
        canvas.itemconfig(item_id, fill=color)
        if step < fade_steps:
            root.after(delay // (fade_steps * 2), fade_in, step + 1)
        else:
            # Text is now fully white, wait 2.5 seconds before completing the cycle
            root.after(2550, lambda: on_complete() if on_complete else None)
    
    # Start the fade out effect
    fade_out(0)

def typewriter_effect(text, canvas, item_id, delay=100, on_complete=None):
    """
    Displays the given text on a Tkinter canvas item with a typewriter animation effect.

    Args:
        text (str): The text to display.
        canvas (tkinter.Canvas): The canvas where the text will be shown.
        item_id (int): The canvas text item ID to update.
        delay (int, optional): Delay in milliseconds between each character. Defaults to 100.
        on_complete (callable, optional): Function to call when animation completes. Defaults to None.
    """
    displayed_text = ""
    def update_text(i=0):
        nonlocal displayed_text
        if i < len(text):
            displayed_text += text[i]
            canvas.itemconfig(item_id, text=displayed_text)
            root.after(delay, update_text, i+1)
        else:
            if on_complete:
                on_complete()
    update_text()

# Center the text horizontally (550 is center of 1100px window)
app_name_text = canvas.create_text(550, 90, text="", font=("Impact", 35, "bold"), fill="white", anchor="center")
app_name_text2 = canvas.create_text(550, 135, text="", font=("Rockwell", 20), fill="white", anchor="center")
app_name_text3 = canvas.create_text(550, 170, text="", font=("Rockwell", 20), fill="white", anchor="center")
# Sequence for typewriter and blink effects
def run_blink_sequence(index=0, is_first=False):
    blink_texts = [
        "Every item has a story. Find yours!",
        "Don't just wish it back, find it here.",
        "Lost, but not forgotten. Found, and reunited.",
        "Dedicated to reuniting you with what's yours.",
        "Find what you've lost. Return what you've found.",
        "Building bridges between the lost and the found.",
        "Helping forgotten items remember their way home.",
    ]
    current_text = blink_texts[index]
    next_index = (index + 1) % len(blink_texts)
    next_text = blink_texts[next_index]
    
    if is_first:
        # For the first text, start with blank text and fade in, wait 3 seconds, then start normal cycle
        canvas.itemconfig(app_name_text3, text=current_text, fill="#3f2e85")  # Start invisible
        fade_in_first(0, current_text, next_text)
    else:
        # Normal fade cycle for subsequent texts
        blink_text_effect(
            current_text, next_text, canvas, app_name_text3, delay=2000, fade_steps=20,
            on_complete=lambda: run_blink_sequence(next_index)
        )

def fade_in_first(step, current_text, next_text, fade_steps=20):
    # Fade from background color (#3f2e85) to white for the first text
    def blend_color(c1, c2, t):
        return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
    # Convert #3f2e85 to RGB
    bg_rgb = (63, 46, 133)  # #3f2e85 in RGB
    white_rgb = (255, 255, 255)
    t = step / fade_steps
    r, g, b = blend_color(bg_rgb, white_rgb, t)
    color = f'#{r:02x}{g:02x}{b:02x}'
    canvas.itemconfig(app_name_text3, fill=color)
    if step < fade_steps:
        root.after(50, fade_in_first, step + 1, current_text, next_text, fade_steps)
    else:
        # Text is now fully white, wait 3 seconds, then start normal cycle
        root.after(3000, lambda: blink_text_effect(
            current_text, next_text, canvas, app_name_text3, delay=2000, fade_steps=20,
            on_complete=lambda: run_blink_sequence(1)  # Start with index 1 for next text
        ))

typewriter_effect(
    "Lost & Found Desktop App", canvas, app_name_text,  
    delay=100,
    on_complete=lambda: typewriter_effect(
        "Connecting what's lost with those who are looking!", canvas, app_name_text2, delay=100,
        on_complete=lambda: run_blink_sequence(0, is_first=True)
    )
)
footer_text1 = canvas.create_text(
    550, 553,  # x, y position (centered at bottom)
    text="Turning 'lost' into 'found' together.", 
    font=("Open Sans", 12, "bold"),
    fill="#000000",
    anchor="center"
)

footer_text2 = canvas.create_text(
    550, 570,  # x, y position (centered at bottom; 550 is center for 1100px width)
    text="Powered by TEAM DOBERMAN",
    font=("Open Sans", 11),
    fill="#000000",
    anchor="center"
)
footer_text3 = canvas.create_text(
    550, 585,  # x, y position (centered at very bottom)
    text="© 2025 All rights reserved",
    font=("Open Sans", 11),
    fill="#000000",
    anchor="center"
)



root.mainloop()