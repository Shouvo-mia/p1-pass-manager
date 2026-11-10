import customtkinter as ctk
from tkinter import messagebox
import keyboard
import database

# ডার্ক মোড এবং মডার্ন ডার্ক-ব্লু থিম সেটআপ
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class PasswordManagerGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SecureKey Vault")
        self.geometry("900x600") # স্ট্যান্ডার্ড প্রিমিয়াম সাইজ
        self.minsize(850, 550)
        self.resizable(True, True)
        self.master_key = ""
        self.selected_site = None # Track currently selected site for updates
        self.is_password_visible = False  # পাসওয়ার্ড টগল ভিজিবিলিটি ট্র্যাক করার জন্য
        
        # শুরুতে লগইন স্ক্রিন লোড করা
        self.show_login_screen()
        self.init_global_hotkey()

    def toggle_password_visibility(self):
        """পাসওয়ার্ড দৃশ্যমান বা অদৃশ্য করার টগল ফাংশন"""
        if self.is_password_visible:
            self.entry_pass.configure(show="*")
            self.btn_toggle_pass.configure(text="👁️")
            self.is_password_visible = False
        else:
            self.entry_pass.configure(show="")
            self.btn_toggle_pass.configure(text="🔒")
            self.is_password_visible = True
            
    def init_global_hotkey(self):
        try:
            keyboard.add_hotkey('ctrl+shift+v', self.bring_to_front)
        except Exception as e:
            print(f"Hotkey error: {e}")

    def bring_to_front(self):
        try:
            self.deiconify()
            self.lift()
            self.attributes('-topmost', True)
            self.attributes('-topmost', False)
        except Exception as e:
            print(e)

    # ==========================================
    # ১. মডার্ন লগইন স্ক্রিন (Modern Login UI)
    # ==========================================
    def show_login_screen(self):
        """স্ক্রিনের একদম মাঝে একটি প্রিমিয়াম লকড ভল্ট কার্ড তৈরি করে"""
        self.login_frame = ctk.CTkFrame(self, width=400, height=380, corner_radius=20, fg_color="#1E1E24")
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # ব্র্যান্ডিং
        lbl_logo = ctk.CTkLabel(self.login_frame, text="🛡️", font=("Helvetica", 50))
        lbl_logo.pack(pady=(35, 10))
        
        lbl_title = ctk.CTkLabel(self.login_frame, text="SECUREKEY VAULT", font=("Helvetica", 20, "bold"), text_color="#3B8ED0")
        lbl_title.pack(pady=5)
        
        lbl_sub = ctk.CTkLabel(self.login_frame, text="Enter Master Key to unlock your credentials", font=("Helvetica", 11), text_color="#A0A0A0")
        lbl_sub.pack(pady=(0, 25))
        
        # master key ইনপুট
        self.txt_master = ctk.CTkEntry(self.login_frame, width=280, height=45, show="*", placeholder_text="Enter Master Password", justify="center", font=("Helvetica", 14), corner_radius=10, fg_color="#2B2B36", border_color="#3B8ED0")
        self.txt_master.pack(pady=10)
        self.txt_master.focus()
        self.txt_master.bind("<Return>", lambda e: self.verify_master()) # Press Enter to unlock
        
        # বাটন
        btn_unlock = ctk.CTkButton(self.login_frame, text="Unlock Secure Vault", width=280, height=45, font=("Helvetica", 13, "bold"), corner_radius=10, command=self.verify_master)
        btn_unlock.pack(pady=(20, 35))

    def verify_master(self):
        """মাস্টার কি সঠিক কিনা তা ডাটাবেজের প্রথম রেকর্ড দিয়ে যাচাই করে"""
        key = self.txt_master.get()
        if not key:
            messagebox.showerror("Error", "Master Key cannot be empty!")
            return
        
        try:
            accounts = database.get_all_accounts()
            if accounts:
                first_site = accounts[0][0] # tuple থেকে প্রথম সাইটের নাম সঠিকভাবে নেওয়া হয়েছে
                test_decrypt = database.get_password(first_site, key)
                
                if test_decrypt is None:
                    messagebox.showerror("Access Denied", "Wrong Master Key! Access Blocked.")
                    self.txt_master.delete(0, 'end')
                    return
        except Exception as e:
            # If database table is empty or uninitialized, allow setting master key
            pass

        self.master_key = key
        self.login_frame.place_forget()
        self.show_dashboard()

    # ==========================================
    # ২. অ্যাডভান্সড ৩-কলাম ড্যাশবোর্ড (3-Column Layout)
    # ==========================================
    def show_dashboard(self):
        """সাইডবার, সার্চসহ লিস্ট এবং ডিটেইলস ভিউ কলাম তৈরি করে"""
        self.grid_columnconfigure(0, weight=0) # সাইডবার ফিক্সড থাকবে
        self.grid_columnconfigure(1, weight=1) # লিস্ট কলাম বড় হবে
        self.grid_columnconfigure(2, weight=1) # ডিটেইলস কলাম বড় হবে
        self.grid_rowconfigure(0, weight=1)

        # --- ১. বাম পাশের সাইডবার (Sidebar Section) ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color="#1E1E24")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.build_sidebar_widgets()

        # --- ২. মাঝখানের ভল্ট লিস্ট (Vault Items List Section) ---
        self.list_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.list_frame.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)
        self.build_list_widgets()

        # --- ৩. ডান পাশের ডিটেইলস কার্ড (Credential Details Section) ---
        self.details_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="#1E1E24")
        self.details_frame.grid(row=0, column=2, sticky="nsew", padx=(0, 20), pady=20)
        self.build_details_widgets()

    # ==========================================
    # ৩. সাইডবার উইজেটস (Sidebar Section)
    # ==========================================
    def build_sidebar_widgets(self):
        lbl_app_name = ctk.CTkLabel(self.sidebar_frame, text="🛡️ SecureKey", font=("Helvetica", 18, "bold"), text_color="#3B8ED0")
        lbl_app_name.pack(pady=(30, 40), padx=20, anchor="w")

        # সাইডবার নেভিগেশন বাটনসমূহ
        self.btn_vault = ctk.CTkButton(self.sidebar_frame, text="🔒 My Vault", font=("Helvetica", 13), height=40, corner_radius=8, fg_color="#2B2B36", anchor="w")
        self.btn_vault.pack(fill="x", padx=15, pady=5)

        self.btn_add_new = ctk.CTkButton(self.sidebar_frame, text="➕ Add Account", font=("Helvetica", 13), height=40, corner_radius=8, fg_color="transparent", anchor="w", command=self.trigger_add_form)
        self.btn_add_new.pack(fill="x", padx=15, pady=5)

        # নিচের দিকে লক বোতাম
        btn_lock = ctk.CTkButton(self.sidebar_frame, text="🚪 Lock Vault", font=("Helvetica", 12), height=35, corner_radius=8, fg_color="#A83232", hover_color="#822525", command=self.lock_vault)
        btn_lock.pack(side="bottom", fill="x", padx=15, pady=20)

    def lock_vault(self):
        """লক করে আবার লগইন স্ক্রিনে ফিরিয়ে নেয়"""
        self.master_key = ""
        self.selected_site = None
        # Destroy dashboard widgets
        for widget in self.winfo_children():
            widget.destroy()
        self.show_login_screen()

    # ==========================================
    # ৪. মাঝখানের লিস্ট উইজেটস ও সার্চ (List & Search)
    # ==========================================
    def build_list_widgets(self):
        search_container = ctk.CTkFrame(self.list_frame, fg_color="transparent")
        search_container.pack(fill="x", pady=(10, 15))

        self.txt_search = ctk.CTkEntry(search_container, placeholder_text="🔍 Search accounts...", height=38, corner_radius=8)
        self.txt_search.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.txt_search.bind("<KeyRelease>", lambda e: self.refresh_list())

        self.scroll_bucket = ctk.CTkScrollableFrame(self.list_frame, fg_color="transparent")
        self.scroll_bucket.pack(fill="both", expand=True)
        
        self.refresh_list()

    def refresh_list(self):
        """ডাটাবেজ থেকে ডাটা এনে সার্চ ফিল্টার অনুযায়ী সুন্দর কার্ড বাটন তৈরি করে"""
        for widget in self.scroll_bucket.winfo_children():
            widget.destroy()
            
        search_query = self.txt_search.get().lower().strip()
        accounts = database.get_all_accounts()
        
        filtered_accounts = [acc for acc in accounts if search_query in acc[0].lower()] if search_query else accounts

        if not filtered_accounts:
            lbl_empty = ctk.CTkLabel(self.scroll_bucket, text="No matches found.", font=("Helvetica", 12, "italic"), text_color="gray")
            lbl_empty.pack(pady=40)
            return

        for acc in filtered_accounts:
            site_name = acc[0]
            username = acc[1]
            
            item_btn = ctk.CTkButton(
                self.scroll_bucket, 
                text=f"🔑  {site_name.upper()}\n    {username}", 
                font=("Helvetica", 12),
                height=55,
                anchor="w",
                hover_color="#2B2B36",
                fg_color="#1E1E24",
                text_color="#E0E0E0",
                corner_radius=10,
                command=lambda s=site_name, u=username: self.load_account_details(s, u)
            )
            item_btn.pack(fill="x", pady=6, padx=2)

    # ==========================================
    # ৫. ডান পাশের ডিটেইলস কার্ড (Details Panel UI)
    # ==========================================
    def build_details_widgets(self):
        """পাসওয়ার্ড ডিটেইলস দেখার ও আপডেট করার প্রিমিয়াম ইন্টারফেস তৈরি করে"""
        self.details_title = ctk.CTkLabel(self.details_frame, text="Credential Details", font=("Helvetica", 16, "bold"), text_color="#3B8ED0")
        self.details_title.pack(pady=(25, 20))

        self.details_content = ctk.CTkFrame(self.details_frame, fg_color="transparent")
        self.details_content.pack(fill="both", expand=True, padx=25)

        # প্লাটফর্ম ইনপুট
        ctk.CTkLabel(self.details_content, text="Platform / Website:", font=("Helvetica", 11), text_color="gray", anchor="w").pack(fill="x", pady=(5, 2))
        self.entry_site = ctk.CTkEntry(self.details_content, height=35, corner_radius=8, fg_color="#2B2B36")
        self.entry_site.pack(fill="x", pady=(0, 10))

        # ইউজারনেম ইনপুট
        ctk.CTkLabel(self.details_content, text="Username / Email:", font=("Helvetica", 11), text_color="gray", anchor="w").pack(fill="x", pady=(5, 2))
        self.entry_user = ctk.CTkEntry(self.details_content, height=35, corner_radius=8, fg_color="#2B2B36")
        self.entry_user.pack(fill="x", pady=(0, 10))

        # পাসওয়ার্ড ইনপুট
        ctk.CTkLabel(self.details_content, text="Password:", font=("Helvetica", 11), text_color="gray", anchor="w").pack(fill="x", pady=(5, 2))
        
        # পাসওয়ার্ড ইনপুট এবং শো/হাইড টগল বাটনের জন্য ফ্রেম
        pass_frame = ctk.CTkFrame(self.details_content, fg_color="transparent")
        pass_frame.pack(fill="x", pady=(0, 20))
        
        self.entry_pass = ctk.CTkEntry(pass_frame, show="*", height=35, corner_radius=8, fg_color="#2B2B36")
        self.entry_pass.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        # পাসওয়ার্ড দেখার/লুকানোর জন্য টগল বাটন (👁️)
        self.btn_toggle_pass = ctk.CTkButton(
            pass_frame, 
            text="👁️", 
            width=40, 
            height=35, 
            corner_radius=8, 
            fg_color="#2B2B36", 
            hover_color="#3B3B4A", 
            command=self.toggle_password_visibility
        )
        self.btn_toggle_pass.pack(side="right")
        
        self.btn_action = ctk.CTkButton(self.details_content, text="💾 Save / Update Securely", height=42, font=("Helvetica", 13, "bold"), corner_radius=8, command=self.save_or_update_details)
        self.btn_action.pack(fill="x", pady=10)
        
        # ডিলিট বাটন
        self.btn_delete = ctk.CTkButton(self.details_content, text="🗑️ Delete Account", fg_color="#A83232", hover_color="#822525", height=38, font=("Helvetica", 12), corner_radius=8, command=self.delete_account)
        self.btn_delete.pack(fill="x", pady=5)

    def trigger_add_form(self):
        """নতুন একাউন্ট যোগ করার জন্য ডিটেইলস প্যানেল পরিষ্কার করে"""
        self.selected_site = None
        self.details_title.configure(text="Add New Credential")
        self.entry_site.delete(0, 'end')
        self.entry_user.delete(0, 'end')
        self.entry_pass.delete(0, 'end')
        self.entry_site.focus()

    def load_account_details(self, site, username):
        """নির্দিষ্ট একাউন্টে ক্লিক করলে তার ডিক্রিপ্ট করা তথ্য ডান পাশের প্যানেলে লোড করবে"""
        self.selected_site = site
        self.details_title.configure(text=f"Edit: {site.upper()}")
        
        # ডাটাবেজ থেকে ডিক্রিপ্ট করা পাসওয়ার্ড আনা
        decrypted_password = database.get_password(site, self.master_key)
        
        # ফিল্ডগুলো খালি করে সঠিক ডাটা বসানো
        self.entry_site.delete(0, 'end')
        self.entry_site.insert(0, site)
        
        self.entry_user.delete(0, 'end')
        self.entry_user.insert(0, username)
        
        self.entry_pass.delete(0, 'end')
        if decrypted_password:
            self.entry_pass.insert(0, decrypted_password)

    def save_or_update_details(self):
        """নতুন একাউন্ট সেভ বা বিদ্যমান একাউন্ট আপডেট করে মাস্টার কি সহ"""
        site = self.entry_site.get().strip()
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()

        if not site or not username or not password:
            messagebox.showerror("Validation Error", "All fields are required!")
            return

        try:
            # যদি আগে থেকে সিলেক্ট করা সাইট থাকে এবং সাইটের নাম পরিবর্তন করা হয়
            if self.selected_site and self.selected_site != site:
                database.delete_account(self.selected_site) # পুরানোটা মুছে ফেলা 
                # (উল্লেখ্য: database.py তে delete_account ফাংশন না থাকলে নিচের মতো সরাসরি সেভ করতে পারেন)
            
            # এখানে database.add_password এর পরিবর্তে database.save_or_update_account ব্যবহার করা হলো
            database.save_or_update_account(site, username, password, self.master_key)
            
            messagebox.showinfo("Success", f"Credential for '{site}' saved successfully using Master Key!")
            self.selected_site = site
            self.refresh_list()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to save credential:\n{str(e)}")
    def delete_account(self):
        """সিলেক্ট করা একাউন্টটি ডাটাবেজ থেকে মুছে ফেলে"""
        if not self.selected_site:
            messagebox.showwarning("Warning", "No account selected to delete!")
            return
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete credentials for '{self.selected_site}'?"):
            try:
                database.delete_account(self.selected_site)
                messagebox.showinfo("Deleted", "Account deleted successfully.")
                self.trigger_add_form()
                self.refresh_list()
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete: {str(e)}")