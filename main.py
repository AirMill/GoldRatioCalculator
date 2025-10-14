# Golden Ratio Calculator (Modern GUI)
# Requires: pip install customtkinter

import customtkinter as ctk
from tkinter import messagebox

# Golden ratio constant
PHI = 1.61803398875

# Function to calculate smaller and larger numbers
def calculate():
    try:
        value = float(entry.get())
        smaller = value / PHI
        larger = value * PHI
        label_smaller.configure(text=f"Smaller number: {smaller:.6f}")
        label_larger.configure(text=f"Larger number: {larger:.6f}")
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid number.")

# Theme toggle
def toggle_theme():
    current = ctk.get_appearance_mode()
    ctk.set_appearance_mode("Dark" if current == "Light" else "Light")

# App setup
ctk.set_appearance_mode("System")  # Can be "Light", "Dark", or "System"
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Golden Ratio Calculator")
app.geometry("400x300")
app.resizable(False, False)

# Title
title = ctk.CTkLabel(app, text="Golden Ratio Calculator", font=("Segoe UI", 20, "bold"))
title.pack(pady=15)

# Entry
entry = ctk.CTkEntry(app, placeholder_text="Enter a number", font=("Segoe UI", 14), justify="center", width=200)
entry.pack(pady=10)

# Calculate button
calc_button = ctk.CTkButton(app, text="Calculate", command=calculate, corner_radius=10)
calc_button.pack(pady=10)

# Result labels
label_smaller = ctk.CTkLabel(app, text="Smaller number: —", font=("Segoe UI", 13))
label_smaller.pack(pady=5)

label_larger = ctk.CTkLabel(app, text="Larger number: —", font=("Segoe UI", 13))
label_larger.pack(pady=5)

# Theme toggle button
theme_button = ctk.CTkButton(app, text="Toggle Theme", command=toggle_theme, corner_radius=10, fg_color="#999999")
theme_button.pack(pady=15)

# Run app
app.mainloop()
