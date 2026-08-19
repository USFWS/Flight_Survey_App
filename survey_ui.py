import customtkinter as ctk

class MainSurveyWindow(ctk.CTk):
    def __init__(self, start_callback, export_callback):
        super().__init__()
        self.title("Aerial Wildlife Survey Post-Processor")
        self.geometry("1550x750")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        top_frame = ctk.CTkFrame(self, height=70)
        top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(top_frame, text="Survey Workstation", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left", padx=15)
        
        self.status_lbl = ctk.CTkLabel(top_frame, text="Ready", font=ctk.CTkFont(size=12))
        self.status_lbl.pack(side="left", padx=20)
        
        self.progress_bar = ctk.CTkProgressBar(top_frame, width=180)
        self.progress_bar.set(0)
        self.progress_bar.pack(side="left", padx=10)
        
        self.export_btn = ctk.CTkButton(top_frame, text="Export CSV Data", fg_color="darkgreen", state="disabled", command=export_callback)
        self.export_btn.pack(side="right", padx=15, pady=10)
        
        self.import_btn = ctk.CTkButton(top_frame, text="Load Data Folder", command=start_callback)
        self.import_btn.pack(side="right", padx=5, pady=10)
        
        self.table_frame = ctk.CTkScrollableFrame(self, label_text="Observer Verification Workspace")
        self.table_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # --- FIXED: Configured layout matrix for 11 sequential columns ---
        self.table_frame.grid_columnconfigure((0,1,2,3,4,5,6,7,8,9,10,11), weight=1)
        
        headers = ["File Target", "Audio", "Seconds", "Latitude", "Longitude", "Colony ID", "Live AI Transcript", "Species Code", "Count", "Verify Data", "Clone Row", "Purge Line"]
        for col_idx, text in enumerate(headers):
            ctk.CTkLabel(self.table_frame, text=text, font=ctk.CTkFont(weight="bold")).grid(row=0, column=col_idx, padx=5, pady=5, sticky="w")

    def update_status(self, msg, val):
        self.after(0, lambda: self.status_lbl.configure(text=msg))
        self.after(0, lambda: self.progress_bar.set(val))
