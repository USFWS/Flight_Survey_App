import os
import datetime
import pandas as pd
from survey_logic import get_raw_seconds_string, parse_count_from_text, split_transcript_by_species, parse_colony_from_text

class SurveyProcessor:
    def __init__(self, controller):
        self.c = controller

    def track_time_to_seconds(self, time_str):
        try:
            val = str(time_str).strip()
            if '.' in val: val = val.split('.')[0].strip()
            h, m, s = map(int, val.split(':'))
            return (h * 3600) + (m * 60) + s
        except Exception: return None

    def generate_iso_timestamp(self, filename):
        try:
            digits = "".join(filter(str.isdigit, filename))
            year = self.c.entry_year.get().strip()
            month = self.c.entry_month.get().strip().zfill(2)
            day = self.c.entry_day.get().strip().zfill(2)
            
            selected_tz_text = self.c.tz_dropdown.get()
            tz_offset = selected_tz_text.split('(')[1].split(')')[0].strip()
            
            if len(digits) >= 8:
                h, m, s, f = digits[0:2], digits[2:4], digits[4:6], digits[6:8]
                return f"{year}-{month}-{day}T{h}:{m}:{s}.{f}0{tz_offset}"
        except Exception: pass
        
        selected_tz_text = self.c.tz_dropdown.get()
        tz_offset = selected_tz_text.split('(')[1].split(')')[0].strip() if '(' in selected_tz_text else "-08:00"
        return f"{self.c.entry_year.get()}-{self.c.entry_month.get().zfill(2)}-{self.c.entry_day.get().zfill(2)}T12:00:00.000{tz_offset}"

    def run_worker(self, folder_path):
        self.c.engine.load_species_list(folder_path)
        self.c.verified_data_store.clear()
        self.c.ui_row_counter = 1  # Reset row counter on main app controller
        
        track_file_path = os.path.join(folder_path, "track.csv")
        try:
            gps_df = pd.read_csv(track_file_path)
            gps_df['Seconds_Num'] = gps_df['Timestamp'].apply(self.track_time_to_seconds)
            valid_gps = gps_df.dropna(subset=['Seconds_Num'])
        except Exception:
            self.c.app.update_status("Error loading tracks", 0)
            self.c.app.import_btn.configure(state="normal")
            return

        audio_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.wav')]
        total_files = len(audio_files)
        
        for idx, filename in enumerate(audio_files):
            self.c.app.update_status(f"Processing {idx+1}/{total_files}", (idx / total_files))
            full_audio_path = os.path.join(folder_path, filename)
            raw_seconds = get_raw_seconds_string(filename)
            lat_val, lon_val, colony_val = "Not Found", "Not Found", "0"
            
            try:
                file_seconds_num = int(raw_seconds)
                if not valid_gps.empty and file_seconds_num > 0:
                    time_diffs = (valid_gps['Seconds_Num'] - file_seconds_num).abs()
                    closest_idx = time_diffs.idxmin()
                    lat_val = round(float(valid_gps.loc[closest_idx, 'Latitude']), 5)
                    lon_val = round(float(valid_gps.loc[closest_idx, 'Longitude']), 5)
                    if 'Colony' in valid_gps.columns:
                        colony_val = str(valid_gps.loc[closest_idx, 'Colony'])
            except Exception: pass
            
            try:
                result = self.c.engine.model.transcribe(full_audio_path, initial_prompt=self.c.engine.ai_vocabulary_prompt, language="en", fp16=False)
                full_transcript = result["text"].strip()
            except Exception: full_transcript = "[Error]"
            
            sub_phrases = split_transcript_by_species(full_transcript, self.c.engine.species_dict)
            for phrase in sub_phrases:
                detected_code = "SELECT..."
                lower_phrase = phrase.lower()
                for code, description in self.c.engine.species_dict.items():
                    if description in lower_phrase or code.lower() in lower_phrase:
                        detected_code = code
                        break
                
                spoken_colony = parse_colony_from_text(phrase)
                active_colony = spoken_colony if spoken_colony is not None else colony_val
                auto_count = parse_count_from_text(phrase)
                
                # --- FIXED: Corrected mapping target pointers to self.c.ui_row_counter ---
                self.c.app.after(0, self.c.add_ui_row, self.c.ui_row_counter, filename, raw_seconds, lat_val, lon_val, phrase, detected_code, auto_count, active_colony)
                self.c.ui_row_counter += 1
            
        self.c.app.update_status("Processing Complete!", 1.0)
        self.c.app.import_btn.configure(state="normal")
        self.c.app.export_btn.configure(state="normal")
