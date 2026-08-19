import os
import pandas as pd
import threading
import customtkinter as ctk
import datetime
from tkinter import filedialog
from pygame import mixer
from survey_ui import MainSurveyWindow
from survey_logic import SurveyEngine
from survey_controller import SurveyProcessor

class SurveyAppController:
    def __init__(self):
        mixer.init()
        self.engine = SurveyEngine()
        self.verified_data_store = {}
        self.current_folder = ""
        self.ui_row_counter = 1
        
        self.app = MainSurveyWindow(self.start_folder_thread, self.export_final_csv)
        self.proc = SurveyProcessor(self)
        self.add_global_input_fields()

    def add_global_input_fields(self):
        self.meta_frame = ctk.CTkFrame(self.app, height=45)
        self.meta_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        
        ctk.CTkLabel(self.meta_frame, text="Year:").pack(side="left", padx=5)
        self.entry_year = ctk.CTkEntry(self.meta_frame, width=55)
        self.entry_year.insert(0, str(datetime.datetime.now().year))
        self.entry_year.pack(side="left", padx=5)
        
        ctk.CTkLabel(self.meta_frame, text="Month:").pack(side="left", padx=5)
        self.entry_month = ctk.CTkEntry(self.meta_frame, width=35)
        self.entry_month.insert(0, str(datetime.datetime.now().month).zfill(2))
        self.entry_month.pack(side="left", padx=5)
        
        ctk.CTkLabel(self.meta_frame, text="Day:").pack(side="left", padx=5)
        self.entry_day = ctk.CTkEntry(self.meta_frame, width=35)
        self.entry_day.insert(0, str(datetime.datetime.now().day).zfill(2))
        self.entry_day.pack(side="left", padx=5)
        
        ctk.CTkLabel(self.meta_frame, text="Observer:").pack(side="left", padx=5)
        self.entry_obs = ctk.CTkEntry(self.meta_frame, width=50)
        self.entry_obs.insert(0, "TKZ")
        self.entry_obs.pack(side="left", padx=5)
        
        ctk.CTkLabel(self.meta_frame, text="Seat:").pack(side="left", padx=5)
        self.entry_seat = ctk.CTkEntry(self.meta_frame, width=40)
        self.entry_seat.insert(0, "RF")
        self.entry_seat.pack(side="left", padx=5)

        ctk.CTkLabel(self.meta_frame, text="Zone:").pack(side="left", padx=5)
        self.tz_dropdown = ctk.CTkOptionMenu(
            self.meta_frame, 
            values=["AKDT (-08:00)", "AKST (-09:00)", "PDT (-07:00)", "PST (-08:00)", 
                    "MDT (-06:00)", "MST (-07:00)", "CDT (-05:00)", "CST (-06:00)", 
                    "EDT (-04:00)", "EST (-05:00)"], width=120
        )
        self.tz_dropdown.set("AKDT (-08:00)")
        self.tz_dropdown.pack(side="left", padx=5)

    def play_audio_file(self, filename):
        try:
            full_path = os.path.join(self.current_folder, filename)
            if os.path.exists(full_path):
                mixer.music.stop()
                mixer.music.load(full_path)
                mixer.music.play()
        except Exception as e: print(f"Audio error: {str(e)}")

    def start_folder_thread(self):
        # --- FIXED: Dynamically find the absolute path where survey_app.py lives ---
        working_directory = os.path.dirname(os.path.abspath(__file__))
        
        # Force the dialog to open inside the working folder directory branch
        folder_path = filedialog.askdirectory(
            initialdir=working_directory, 
            title="Select your Survey Folder"
        )
        
        if not folder_path: return
        self.current_folder = folder_path
        self.app.import_btn.configure(state="disabled")
        self.app.export_btn.configure(state="disabled")
        threading.Thread(target=self.proc.run_worker, args=(folder_path,), daemon=True).start()

    def add_ui_row(self, row, filename, raw_seconds, lat_val, lon_val, phrase_text, detected_code, auto_count, colony_val):
        ctk.CTkLabel(self.app.table_frame, text=filename).grid(row=row, column=0, padx=5, pady=5)
        
        play_btn = ctk.CTkButton(self.app.table_frame, text="▶ Play", width=55, fg_color="purple", command=lambda f=filename: self.play_audio_file(f))
        play_btn.grid(row=row, column=1, padx=5, pady=5)
        
        ctk.CTkLabel(self.app.table_frame, text=raw_seconds).grid(row=row, column=2, padx=5, pady=5)
        ctk.CTkLabel(self.app.table_frame, text=str(lat_val)).grid(row=row, column=3, padx=5, pady=5)
        ctk.CTkLabel(self.app.table_frame, text=str(lon_val)).grid(row=row, column=4, padx=5, pady=5)
        
        col_entry = ctk.CTkEntry(self.app.table_frame, width=50)
        col_entry.insert(0, str(colony_val))
        col_entry.grid(row=row, column=5, padx=5, pady=5)
        
        txt_entry = ctk.CTkEntry(self.app.table_frame, width=240)
        txt_entry.insert(0, phrase_text)
        txt_entry.grid(row=row, column=6, padx=5, pady=5)
        
        code_dropdown = ctk.CTkOptionMenu(self.app.table_frame, values=self.engine.valid_codes, width=100)
        code_dropdown.set(detected_code)
        code_dropdown.grid(row=row, column=7, padx=5, pady=5)
        
        count_spin = ctk.CTkEntry(self.app.table_frame, width=50)
        count_spin.insert(0, auto_count)
        count_spin.grid(row=row, column=8, padx=5, pady=5)
        
        save_btn = ctk.CTkButton(self.app.table_frame, text="Verify Row", width=80, 
                                 command=lambda r=row, f=filename, la=lat_val, lo=lon_val, tx=txt_entry, cd=code_dropdown, cn=count_spin, ce=col_entry: 
                                 self.verify_and_save(r, f, la, lo, tx, cd, cn, ce))
        save_btn.grid(row=row, column=9, padx=5, pady=5)
        
        clone_btn = ctk.CTkButton(self.app.table_frame, text="📋 Clone", width=55, fg_color="#4682B4", hover_color="#5F9EA0",
                                  command=lambda r=row, f=filename, s=raw_seconds, la=lat_val, lo=lon_val, tx=txt_entry, cd=code_dropdown, cn=count_spin, ce=col_entry:
                                  self.clone_ui_row(r, f, s, la, lo, tx.get(), "SELECT...", "1", ce.get()))
        clone_btn.grid(row=row, column=10, padx=5, pady=5)
        
        del_btn = ctk.CTkButton(self.app.table_frame, text="❌ Delete", width=65, fg_color="#8B0000", hover_color="#FF0000", command=lambda r=row: self.purge_ui_row(r))
        del_btn.grid(row=row, column=11, padx=5, pady=5)

    def clone_ui_row(self, source_row_idx, filename, raw_seconds, lat, lon, notes, target_code, fallback_count, colony_val):
        target_row_idx = source_row_idx + 1
        for w in self.app.table_frame.winfo_children():
            grid_info = w.grid_info()
            current_w_row = int(grid_info.get("row", 0))
            if current_w_row >= target_row_idx:
                w.grid(row=current_w_row + 1)
                if isinstance(w, ctk.CTkButton):
                    btn_txt = w.cget("text")
                    if btn_txt == "❌ Delete":
                        w.configure(command=lambda r=current_w_row + 1: self.purge_ui_row(r))
        
        updated_store = {}
        for k, v in self.verified_data_store.items():
            if k >= target_row_idx:
                v["Line"] = k + 1
                updated_store[k + 1] = v
            else:
                updated_store[k] = v
        self.verified_data_store = updated_store
        
        self.add_ui_row(target_row_idx, filename, raw_seconds, lat, lon, f"Cloned: {notes}", target_code, fallback_count, colony_val)
        self.ui_row_counter += 1

    def purge_ui_row(self, row_idx):
        if row_idx in self.verified_data_store: del self.verified_data_store[row_idx]
        for w in self.app.table_frame.winfo_children():
            if int(w.grid_info()["row"]) == row_idx: w.destroy()

    def verify_and_save(self, row_idx, filename, lat, lon, tx_entry, code_drop, count_entry, col_entry):
        iso_time = self.proc.generate_iso_timestamp(filename)
        self.verified_data_store[row_idx] = {
            "Line": row_idx, "Year": self.entry_year.get(), "Month": self.entry_month.get(), "Day": self.entry_day.get(),
            "Observer": self.entry_obs.get(), "Seat": self.entry_seat.get(), "Colony": col_entry.get(), "Filename": filename,
            "Lat": lat, "Lon": lon, "Time": iso_time, "Species": code_drop.get(), "Num": count_entry.get(), "Notes": tx_entry.get()
        }
        for w in self.app.table_frame.winfo_children():
            grid_info = w.grid_info()
            if int(grid_info["row"]) == row_idx and isinstance(w, ctk.CTkButton) and w.cget("text") == "Verify Row":
                w.configure(text="Saved! ✅", state="disabled", fg_color="green")

    def export_final_csv(self):
        if not self.verified_data_store: return
        save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")], title="Save Final Survey Data")
        if not save_path: return
        sorted_rows = [self.verified_data_store[k] for k in sorted(self.verified_data_store.keys())]
        export_df = pd.DataFrame(sorted_rows)
        export_df['Line'] = range(1, len(export_df) + 1)
        export_df.to_csv(save_path, index=False)
        print(f"Master spreadsheet saved: {save_path}")

if __name__ == "__main__":
    controller = SurveyAppController()
    controller.app.mainloop()
