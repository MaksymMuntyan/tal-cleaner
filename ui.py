# ui.py
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import processor
import threading

# Colors & styles
BG_COLOR = "#f0f4f8"
BTN_COLOR = "#4a90e2"
BTN_HOVER = "#357ABD"
BTN_BORDER = "#2C5AA0"
FONT_BTN = ("Helvetica", 14, "bold")
FONT_LABEL = ("Helvetica", 12)
FONT_INTRO = ("Helvetica", 14, "bold")
FONT_INSTRUCTIONS = ("Helvetica", 11)

# Track last mode clicked: 'single' or 'bulk'
last_mode = None

def run_in_thread(func, *args):
    """Run a function in a separate thread to avoid freezing the UI."""
    threading.Thread(target=func, args=args, daemon=True).start()

def single_clean():
    global last_mode
    last_mode = 'single'
    select_file_or_folder(mode="single", generate_report=report_var.get())

def bulk_clean():
    global last_mode
    last_mode = 'bulk'
    select_file_or_folder(mode="bulk", generate_report=report_var.get())

def select_file_or_folder(mode, generate_report):
    """Prompt the user to select a file or folder, then start processing."""
    if mode == "single":
        path = filedialog.askopenfilename(
            title="Select a CSV or Excel file",
            filetypes=[("Excel files", "*.xls *.xlsx"), ("CSV files", "*.csv")]
        )
    else:
        path = filedialog.askdirectory(title="Select a folder with TAL files")

    if path:
        # Show progress bar
        show_progress_bar()
        run_in_thread(process_file_wrapper, path, mode, generate_report)

def show_progress_bar():
    """Add progress bar to the main window if it doesn't exist yet."""
    global progress
    if not hasattr(root, 'progress'):
        root.progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="indeterminate")
        root.progress.pack(pady=(10, 20))
    root.progress.start()

def hide_progress_bar():
    """Stop and hide progress bar safely."""
    if hasattr(root, 'progress') and root.progress.winfo_exists():
        root.progress.stop()
        root.progress.pack_forget()
        root.progress.destroy()
        delattr(root, 'progress')

def process_file_wrapper(path, mode, generate_report):
    """Wrapper to process files/folders and update the UI when done."""
    try:
        if mode == "single":
            processor.process_single_file(path, generate_report)
        else:
            processor.process_folder(path, generate_report)
        root.after(0, post_process_ui)
    except Exception as e:
        root.after(0, lambda: messagebox.showerror("Error", f"An error occurred:\n{e}"))
    finally:
        root.after(0, hide_progress_bar)

def post_process_ui():
    """Update the main window to show 'Process complete' and options."""
    # Clear previous widgets
    for widget in root.winfo_children():
        widget.destroy()

    # Intro label
    intro_label = tk.Label(
        root,
        text="Process complete! ✅",
        font=FONT_INTRO, bg=BG_COLOR, fg="#333333", wraplength=450, justify="center"
    )
    intro_label.pack(pady=(30, 10))

    # Instruction label
    instructions_label = tk.Label(
        root,
        text="What would you like to do next?",
        font=FONT_INSTRUCTIONS, bg=BG_COLOR, fg="#555555", wraplength=450, justify="center"
    )
    instructions_label.pack(pady=(0, 20))

    # Buttons frame (stacked vertically)
    btn_frame = tk.Frame(root, bg=BG_COLOR)
    btn_frame.pack(pady=10)

    button_width = 20

    btn_again = tk.Button(
        btn_frame, text="Run Another TAL", font=FONT_BTN, bg=BTN_COLOR, fg="white",
        activebackground=BTN_HOVER, activeforeground="white", width=button_width, height=2,
        command=lambda: reset_ui(), bd=3, relief="raised", highlightbackground=BTN_BORDER
    )
    btn_again.pack(pady=5)
    btn_again.bind("<Enter>", lambda e: btn_again.config(bg=BTN_HOVER))
    btn_again.bind("<Leave>", lambda e: btn_again.config(bg=BTN_COLOR))

    btn_exit = tk.Button(
        btn_frame, text="Goodbye 👋", font=FONT_BTN, bg=BTN_COLOR, fg="white",
        activebackground=BTN_HOVER, activeforeground="white", width=button_width, height=2,
        command=root.destroy, bd=3, relief="raised", highlightbackground=BTN_BORDER
    )
    btn_exit.pack(pady=5)
    btn_exit.bind("<Enter>", lambda e: btn_exit.config(bg=BTN_HOVER))
    btn_exit.bind("<Leave>", lambda e: btn_exit.config(bg=BTN_COLOR))

def reset_ui():
    """Reset the main UI to the initial state."""
    for widget in root.winfo_children():
        widget.destroy()
    build_main_ui()

def build_main_ui():
    """Construct the initial UI."""
    # Introductory label
    intro_label = tk.Label(
        root,
        text="Greetings, I am the TAL Cleaner *BEEEEEEP* 🤖",
        font=FONT_INTRO, bg=BG_COLOR, fg="#333333", wraplength=450, justify="center"
    )
    intro_label.pack(pady=(20, 10))

    # Instructions label
    instructions_label = tk.Label(
        root,
        text="Choose 'Single Clean' to clean one file, or 'Bulk Clean' to clean a folder full of TAL files.",
        font=FONT_INSTRUCTIONS, bg=BG_COLOR, fg="#555555", wraplength=450, justify="center"
    )
    instructions_label.pack(pady=(0, 20))

    # **NEW:** Checkbox for generating the report
    report_checkbox = tk.Checkbutton(
        root,
        text="Generate report on cleaned files",
        variable=report_var,
        onvalue=True,
        offvalue=False,
        font=FONT_INSTRUCTIONS,
        bg=BG_COLOR,
        activebackground=BG_COLOR
    )
    report_checkbox.pack(pady=(10, 5))

    # Single Clean Button
    btn_single = tk.Button(
        root, text="Single Clean", font=FONT_BTN, bg=BTN_COLOR, fg="white",
        activebackground=BTN_HOVER, activeforeground="white", width=20, height=2,
        command=single_clean, bd=3, relief="raised", highlightbackground=BTN_BORDER
    )
    btn_single.pack(pady=5)
    btn_single.bind("<Enter>", lambda e: btn_single.config(bg=BTN_HOVER))
    btn_single.bind("<Leave>", lambda e: btn_single.config(bg=BTN_COLOR))

    # Bulk Clean Button
    btn_bulk = tk.Button(
        root, text="Bulk Clean", font=FONT_BTN, bg=BTN_COLOR, fg="white",
        activebackground=BTN_HOVER, activeforeground="white", width=20, height=2,
        command=bulk_clean, bd=3, relief="raised", highlightbackground=BTN_BORDER
    )
    btn_bulk.pack(pady=5)
    btn_bulk.bind("<Enter>", lambda e: btn_bulk.config(bg=BTN_HOVER))
    btn_bulk.bind("<Leave>", lambda e: btn_bulk.config(bg=BTN_COLOR))

def main():
    global root, report_var
    root = tk.Tk()
    root.title("TAL Cleaner 🤖")
    root.geometry("500x380") # Increased height for the checkbox
    root.configure(bg=BG_COLOR)
    root.resizable(False, False)
    
    # **NEW:** Variable to hold the checkbox state
    report_var = tk.BooleanVar(value=False) # Default is unchecked

    # Center the window
    root.eval('tk::PlaceWindow . center')

    build_main_ui()
    root.mainloop()

if __name__ == "__main__":
    main()