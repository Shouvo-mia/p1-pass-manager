import keyboard
import pyautogui
import time
from tkinter import simpledialog, messagebox
import database
from gui import PasswordManagerGUI

def run_autofill():
    # শর্টকাট চাপলে প্রথমে মাস্টার কি চাবে
    master_key = simpledialog.askstring("Security", "Enter Master Key to unlock autofill:", show='*')
    if not master_key:
        return
        
    # কোন অ্যাকাউন্টের পাসওয়ার্ড বসাতে হবে তার নাম চাবে
    site_name = simpledialog.askstring("Autofill", "Enter Site Name (e.g. facebook, gmail):")
    if not site_name:
        return
        
    # ডাটাবেজ থেকে পাসওয়ার্ডটি ডিক্রিপ্ট করে আনা
    password = database.get_password(site_name, master_key)
    
    if password:
        messagebox.showinfo("Autofill Ready", "Click on the password box now. Typing will start in 3 seconds!")
        time.sleep(3) # ইউজারকে বক্সে ক্লিক করার সুযোগ দেওয়ার জন্য ৩ সেকেন্ড থামা
        pyautogui.typewrite(password) # অটোমেটিক কীবোর্ডের মতো টাইপ করে দেবে
    else:
        messagebox.showerror("Error", "Wrong Master Key or Account not found!")

def open_manager_gui():
    # ডেক্সটপ অ্যাপের মূল ইন্টারফেস ওপেন করা
    app = PasswordManagerGUI()
    app.mainloop()

if __name__ == "__main__":
    # ডাটাবেজ ইনিশিয়েট করা
    database.init_db()
    
    # ব্যাকগ্রাউন্ড হট-কী সেট করা
    keyboard.add_hotkey('ctrl+alt+p', run_autofill)
    
    print("=== PASS MANAGER IS RUNNING ===")
    print("-> Press Ctrl+Alt+P anywhere to Autofill a password.")
    print("-> Starting the Manual GUI Window now...\n")
    
    # একই সাথে মূল অ্যাপ উইন্ডোটি চালু করে দেওয়া
    open_manager_gui()
