## Aerial Wildlife Survey Log Station: Comprehensive User Manual
System Version: 2.0
Operating Environment: Portable / Airborne Standalone Hardware & Desktop Post-Processing
------------------------------
## 1. System Overview
The Aerial Wildlife Survey Log Station is a two-part ecosystem designed to record, geo-reference, transcribe, and manage wildlife observations taken during aerial transect surveys.

   1. The Hardware Logger: A standalone, physical cockpit device that tracks your flight path (breadcrumb trail) and captures high-fidelity audio observations via your aviation headset when a button is pressed.
   2. The Desktop Application: A local, privacy-compliant Python application that uses AI to parse voice entries, automatically match recordings to your flight track, and format data for direct export into regulatory agency templates.

------------------------------
## 2. Hardware Specification & Assembly## Hardware Blueprint

       +-------------------------------------------------------+

       |                  Teensy 4.1 Board                     |
       |                                                       |
       |  [USB]    (3.3V)  (GND)   (Pin 0) (Pin 1)    (Pin 10) |
       +----+--------+-------+--------+-------+---------+------+

            |        |       |        |       |         |
            |        |       |        |       |         |
+-----------+--+     |       |        |       |         |

| USB-C Power  |     |       |        |       |         |
| (Battery)    |     |       |        |       |         |
+--------------+     |       |        |       |         |

                     |       |        |       |         |
   +-----------------+       |        |       |         |

   |                         |        |       |         |
   |      +------------------+        |       |         |
   |      |                           |       |         |
+--+------++                         ++-------++        |

|  (VIN)   |                         |  (TX)   |        |
|  (GND)   |                         |  (RX)   |        |
|          |                         |         |        |
| Push     |                         | GPS     |        |
| Button   |                         | Module  |        |
+----------+                         +---------+        |
                                                        |
                                                        |
+-------------------------------------------------------+--+

|               Teensy Audio Adaptor Board                 |
|                                                          |
|   [ 3.5mm Audio Jack ] <--- (Plugs directly on top)      |
|   [ MicroSD Card Slot ]                                  |
+----------------------------------------------------------+

## Bill of Materials & Cost Breakdown

| Component | Purpose | Approx. Cost |
|---|---|---|
| Teensy 4.1 Microcontroller | System brains, fast processing, built-in MicroSD card slot. | $35.00 |
| Teensy Audio Adaptor Board (Rev D) | Adds 3.5mm stereo microphone/headphone input lines. | $15.00 |
| Adafruit Ultimate GPS Breakout V3 | Streams live positional metrics and timing arrays. | $30.00 |
| CR1220 Coin Cell Battery | Holds internal atomic GPS time for instant hot satellite locks. | $2.00 |
| Waterproof Momentary Push Button | Physical tactile cockpit trigger to initiate recording events. | $5.00 |
| SPDT Toggle Switch | Selects between Plane Power and Backup Battery modes. | $3.00 |
| 4xAA Battery Holder with switch | Standalone power supply (lasts over 8 hours). | $5.00 |
| 5V Buck Converter Module | Regulates fluctuating aircraft voltage safely down to 5V. | $5.00 |
| 2.1mm Panel Mount DC Jack | Rugged power port bolted directly through the case. | $3.00 |
| 12V Cigarette Lighter to 2.1mm Cable | Plugs directly into an aircraft or car cigarette outlet. | $7.00 |
| Flanged ABS Plastic Enclosure Box | Hard shell box to securely house and mount components. | $8.00 |
| Total Estimated Hardware Cost | | ~$118.00 |

## Step-by-Step Hardware Assembly

   1. Stack the Boards: Solder header pins onto the Teensy 4.1. Push the Teensy Audio Adaptor Board directly onto the top pins of the Teensy. They line up perfectly.
   2. Wire the GPS Module: Connect 4 wires from the GPS breakout board to the Teensy board pins:
   * VIN on GPS to 3.3V on Teensy.
      * GND on GPS to GND on Teensy.
      * RX on GPS to Pin 1 (TX1) on Teensy.
      * TX on GPS to Pin 0 (RX1) on Teensy.
   3. Install the Clock Battery: Slide the CR1220 coin cell into the GPS board slot.
   4. Power Subsystem Setup: Wire the 12V DC Jack to the IN+ / IN- pins of the Buck Converter. Wire your 4xAA Battery holder to the outer terminal of your SPDT toggle switch, and wire the Buck Converter OUT+ to the opposite terminal. Wire the center toggle selector pin to VIN on the Teensy. Connect all ground references together.
   5. Button & Visual Feedback Hookup: Connect your physical push button to Pin 10 and GND. Drill out holes on the case to insert a Green LED (wired to Pin 2 through a 220-ohm resistor) to confirm GPS satellite lock, and a Red LED (wired to Pin 3 through a 220-ohm resistor) to confirm active recording status.

------------------------------
## 3. In-Flight Field Operation
When operating the standalone device inside the aircraft, follow this operational sequence:

[Power On Device] ---> Wait for Solid Green Light (GPS Sat Lock)
                             |
                             v
[Sight Wildlife]  ---> Tap Physical Push Button (Red Light Turns On)
                             |
                             v
[Speak Into Mic]  ---> State "Colony X, Count Species Description"
                             |
                             v
[Finish Sight]   ---> Tap Button Second Time (Red Light Shuts Off)


* Storage Mechanics: The device streams your background path continuously to track.csv using total seconds past midnight. Pressing the button stops path writing momentarily to output an audio block file named using an HHMMSSxx.WAV format structure matching your precise coordinate metrics (Hour, Minute, Second, Sub-second fraction).

------------------------------
## 4. Post-Flight Post-Processing Software
The processing workstation is a modularized desktop application written in Python. It performs automated file reading, transcription, and layout generation using four inter-linked text files.
## Post-Processing Layout Block

+--------------------------- Project Workspace Folder -------------------------+

|                                                                              |
|  [survey_app.py]        <--- Launches visual dashboard window GUI panels     |
|  [survey_ui.py]         <--- Renders the 12-column scrolling spreadsheet     |
|  [survey_logic.py]      <--- Extracts timestamps, bird counts, splits text   |
|  [survey_controller.py] <--- Runs the background AI model matching loop       |
|  [ffmpeg.exe]           <--- Local decoder tool handling audio decoding      |
|                                                                              |
+------------------------------------------------------------------------------+

## Installation & Prerequisites

   1. Download and install [Python 3.11+](https://www.python.org/downloads/) ensuring you check the box for "Add Python to PATH" during setup.
   2. Install the necessary processing libraries by opening your command prompt terminal and executing:
   
   pip install openai-whisper pandas customtkinter geopandas shapely pygame scipy openpyxl
   
   
## FFmpeg Audio Decoder Configuration
Because Whisper AI cannot read raw airplane voice recordings natively, it relies on an open-source background decoder named FFmpeg to stream and parse the audio files [1.2]. To drop this tool inside your survey workspace without altering complex Windows system variables, follow these steps:

   1. Download the official, free Windows builder zip file from [Gyan.dev FFmpeg Git Builds](https://www.gyan.dev/ffmpeg/builds/) (Select the ffmpeg-git-essentials.zip link).
   2. Right-click the downloaded file in your Windows Downloads folder, choose Extract All..., and extract the contents.
   3. Open your newly extracted folder and navigate inside until you find a subfolder explicitly named bin.
   4. Inside the bin folder, locate the file named ffmpeg.exe. Right-click it and select Copy.
   5. Navigate to your primary flight project folder (e.g., C:\Users\...\Flight_Survey_App). Right-click inside an empty space right next to your script files and select Paste.

The final directory directory structure must look exactly like this:

 📂 Flight_Survey_App
   ├── 📄 survey_app.py
   ├── 📄 survey_ui.py
   ├── 📄 survey_controller.py
   ├── 📄 survey_logic.py
   └── ⚙️ ffmpeg.exe       <--- Placed here, the code sees it instantly!

------------------------------
## 5. Software Code Architecture
Save these four scripts side-by-side using the precise file names specified below:
## File 1: survey_logic.py

import osimport reimport datetimeimport whisper
WORD_TO_NUM = {
    'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
    'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
    'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15
}
def parse_count_from_text(text):
    clean_text = text.lower()
    clean_text = re.sub(r'col[o|i]n[y|i|e](.*?)\s*\d+', '', clean_text)
    for word in WORD_TO_NUM.keys():
        clean_text = re.sub(r'col[o|i]n[y|i|e](.*?)\s*' + word, '', clean_text)
    matches = re.findall(r'\b(\d+)\b', clean_text)
    if len(matches) > 1:
        bird_match = re.search(r'\b(\d+)\s*(?:birds?|nests?|gulls?|corm|moos|carb|bear|wolf|wolves)?', clean_text)
        if bird_match and not re.search(r'col[o|i]n[y|i|e](?:\s+number)?\s*' + bird_match.group(1), clean_text):
            return bird_match.group(1)
    digit_match = re.search(r'\b(\d+)\b', clean_text)
    if digit_match: return digit_match.group(1)
    for word, num in WORD_TO_NUM.items():
        if re.search(r'\b' + word + r'\b', clean_text): return str(num)
    return "1"
def parse_colony_from_text(text):
    clean_text = text.lower()
    digit_match = re.search(r'col[o|i]n[y|i|e](?:\s+number)?\s*(\d+)', clean_text)
    if digit_match: return digit_match.group(1)
    for word, num in WORD_TO_NUM.items():
        if re.search(r'col[o|i]n[y|i|e](?:\s+number)?\s*' + word, clean_text): return str(num)
    return None
def get_raw_seconds_string(filename):
    digits = "".join(filter(str.isdigit, filename))
    if len(digits) >= 6:
        try:
            h, m, s = int(digits[0:2]), int(digits[2:4]), int(digits[4:6])
            if 0 <= h < 24 and 0 <= m < 60 and 0 <= s < 60:
                return str((h * 3600) + (m * 60) + s)
        except Exception: pass
    return "0"
def split_transcript_by_species(text, species_dict):
    lower_text = text.lower()
    clauses = re.split(r'\band\b|,|\bplus\b', lower_text)
    clauses = [c.strip() for c in clauses if c.strip()]
    matching_codes = []
    for code, description in species_dict.items():
        if description in lower_text or code.lower() in lower_text:
            matching_codes.append((code, description))
    if len(matching_codes) <= 1 or len(clauses) <= 1: return [text]
    detected_phrases = []
    colony_prefix_match = re.search(r'^(col[o|i]n[y|i|e](?:\s+number)?\s*\w+\s*)', lower_text)
    colony_prefix = colony_prefix_match.group(1) if colony_prefix_match else ""
    for clause in clauses:
        for code, description in matching_codes:
            if description in clause or code.lower() in clause:
                final_clause = clause if "col" in clause or not colony_prefix else f"{colony_prefix}{clause}"
                detected_phrases.append(final_clause)
                break
    return detected_phrases if detected_phrases else [text]
class SurveyEngine:
    def __init__(self):
        print("Loading Whisper AI 'Base' Model...")
        self.model = whisper.load_model("base")
        print("AI Model Ready!")
        self.species_dict = {}
        self.valid_codes = ["SELECT..."]
        self.ai_vocabulary_prompt = ""

    def load_species_list(self, folder_path):
        species_path = os.path.join(folder_path, "species.csv")
        if not os.path.exists(species_path):
            self.valid_codes = ["NEST", "POOP", "MOOS"]
            return
        try:
            import pandas as pd
            df = pd.read_csv(species_path)
            self.valid_codes = df['Code'].astype(str).tolist()
            self.species_dict = {}
            prompt_words = []
            for _, row in df.iterrows():
                code = str(row['Code'])
                eng = str(row['English_Name']).lower()
                self.species_dict[code] = eng
                prompt_words.extend([row['English_Name'], code])
            self.ai_vocabulary_prompt = "Wildlife survey words: " + ", ".join(prompt_words)
        except Exception as e: print(f"Error parsing species file: {str(e)}")

## File 2: survey_ui.py

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
        self.table_frame.grid_columnconfigure((0,1,2,3,4,5,6,7,8,9,10,11), weight=1)
        
        headers = ["File Target", "Audio", "Seconds", "Latitude", "Longitude", "Colony ID", "Live AI Transcript", "Species Code", "Count", "Verify Data", "Clone Row", "Purge Line"]
        for col_idx, text in enumerate(headers):
            ctk.CTkLabel(self.table_frame, text=text, font=ctk.CTkFont(weight="bold")).grid(row=0, column=col_idx, padx=5, pady=5, sticky="w")

    def update_status(self, msg, val):
        self.after(0, lambda: self.status_lbl.configure(text=msg))
        self.after(0, lambda: self.progress_bar.set(val))

## File 3: survey_controller.py

import osimport datetimeimport pandas as pdfrom survey_logic import get_raw_seconds_string, parse_count_from_text, split_transcript_by_species, parse_colony_from_text
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
            if len(digits) >= 6:
                h, m, s = digits[0:2], digits[2:4], digits[4:6]
                f = digits[6:8] if len(digits) >= 8 else "00"
                return f"{year}-{month}-{day}T{h}:{m}:{s}.{f}0{tz_offset}"
        except Exception: pass
        selected_tz_text = self.c.tz_dropdown.get()
        tz_offset = selected_tz_text.split('(')[1].split(')')[0].strip() if '(' in selected_tz_text else "-08:00"
        return f"{self.c.entry_year.get()}-{self.c.entry_month.get().zfill(2)}-{self.c.entry_day.get().zfill(2)}T12:00:00.000{tz_offset}"

    def run_worker(self, folder_path):
        self.c.engine.load_species_list(folder_path)
        self.c.verified_data_store.clear()
        self.c.ui_row_counter = 1
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
                    if 'Colony' in valid_gps.columns: colony_val = str(valid_gps.loc[closest_idx, 'Colony'])
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
                self.c.app.after(0, self.c.add_ui_row, self.c.ui_row_counter, filename, raw_seconds, lat_val, lon_val, phrase, detected_code, auto_count, active_colony)
                self.c.ui_row_counter += 1
        self.c.app.update_status("Processing Complete!", 1.0)
        self.c.app.import_btn.configure(state="normal")
        self.c.app.export_btn.configure(state="normal")

## File 4: survey_app.py

import osimport pandas as pdimport threadingimport customtkinter as ctkimport datetimefrom tkinter import filedialogfrom pygame import mixerfrom survey_ui import MainSurveyWindowfrom survey_logic import SurveyEnginefrom survey_controller import SurveyProcessor
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
        self.tz_dropdown = ctk.CTkOptionMenu(self.meta_frame, values=["AKDT (-08:00)", "AKST (-09:00)", "PDT (-07:00)", "PST (-08:00)", "MDT (-06:00)", "MST (-07:00)", "CDT (-05:00)", "CST (-06:00)", "EDT (-04:00)", "EST (-05:00)"], width=120)
        self.tz_dropdown.set("AKDT (-08:00)")
        self.tz_dropdown.pack(side="left", padx=5)

    def play_audio_file(self, filename):
        try:
            full_path = os.path.join(self.current_folder, filename)
            if os.path.exists(full_path):
                mixer.music.stop()
                mixer.music.load(full_path)
                mixer.music.play()
        except Exception: pass

    def start_folder_thread(self):
        working_dir = os.path.dirname(os.path.abspath(__file__))
        folder_path = filedialog.askdirectory(initialdir=working_dir, title="Select your Survey Folder")
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
        col_entry.insert(0, str(colony_val)); col_entry.grid(row=row, column=5, padx=5, pady=5)
        txt_entry = ctk.CTkEntry(self.app.table_frame, width=240)
        txt_entry.insert(0, phrase_text); txt_entry.grid(row=row, column=6, padx=5, pady=5)
        code_dropdown = ctk.CTkOptionMenu(self.app.table_frame, values=self.engine.valid_codes, width=100)
        code_dropdown.set(detected_code); code_dropdown.grid(row=row, column=7, padx=5, pady=5)
        count_spin = ctk.CTkEntry(self.app.table_frame, width=50)
        count_spin.insert(0, auto_count); count_spin.grid(row=row, column=8, padx=5, pady=5)
        save_btn = ctk.CTkButton(self.app.table_frame, text="Verify Row", width=80, command=lambda r=row, f=filename, la=lat_val, lo=lon_val, tx=txt_entry, cd=code_dropdown, cn=count_spin, ce=col_entry: self.verify_and_save(r, f, la, lo, tx, cd, cn, ce))
        save_btn.grid(row=row, column=9, padx=5, pady=5)
        clone_btn = ctk.CTkButton(self.app.table_frame, text="📋 Clone", width=55, fg_color="#4682B4", hover_color="#5F9EA0", command=lambda r=row, f=filename, s=raw_seconds, la=lat_val, lo=lon_val, tx=txt_entry, cd=code_dropdown, cn=count_spin, ce=col_entry: self.clone_ui_row(r, f, s, la, lo, tx.get(), "SELECT...", "1", ce.get()))
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
                if isinstance(w, ctk.CTkButton) and w.cget("text") == "❌ Delete":
                    w.configure(command=lambda r=current_w_row + 1: self.purge_ui_row(r))
        updated_store = {}
        for k, v in self.verified_data_store.items():
            if k >= target_row_idx: v["Line"] = k + 1; updated_store[k + 1] = v
            else: updated_store[k] = v
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
if __name__ == "__main__":
    controller = SurveyAppController()
    controller.app.mainloop()

------------------------------
## 6. Data Verification Workflow Guide## Step 1: Initialize Workspace Directories
Create a flight session folder inside your script directory (e.g., Flight_01). Place the following items into that directory:

   1. track.csv: Your raw hardware coordinate log (must contain Timestamp, Latitude, and Longitude column headers).
   2. Your raw captured .wav audio files.
   3. species.csv: Your lookup dictionary taxonomy containing Code,English_Name. Wrap descriptions containing commas in double quotes (e.g., NEST,"nest seen"). Do not use the word "colony" as a standalone keyword description [1.2].

## Step 2: Open and Run the Desktop Interface
Open your command prompt, navigate to your script directory, and execute:

python survey_app.py

The window interface will instantly display. Enter your global flight context metadata parameters (Year, Month, Day, Observer, Seat, and Timezone Region Offset) into the top toolbar panel entries.
## Step 3: Load Data and Human Quality Review
Click Load Data Folder and choose your flight folder. The app will open the browser path directly inside your current workspace directory.
Once loaded, perform quality verification checks using the workspace row buttons:

* Audio Check: Click ▶ Play to listen to any uncertain or garbled observation clip directly through your headset.
* Direct Edits: Click inside any Transcript, Colony ID, or Count text block to correct typos or misheard numbers.
* Missed Data Cloning: If an entry contains multiple species that the AI missed, click 📋 Clone. A duplicate line will insert directly underneath the current source row, copying the time and coordinates while letting you input the secondary observations.
* Error Purging: Click ❌ Delete to instantly drop pilot test-triggers or cockpit errors from your active layout matrix grid.

## Step 4: Final Validation and Compliance Export
When a data entry line reflects exact mission numbers, click Verify Row. The action button will snap to a Saved! ✅ confirmation state.
Once your rows are verified, click the dark green Export CSV Data button. The station will re-index your sequential data lines, map full compliant ISO-8601 UTC timezone strings, and write out a clean, compliant database ready for direct agency review!
------------------------------
## Support & Troubleshooting

* Lat/Lon fields showing "Not Found": Ensure the Timestamp column header inside your track.csv file matches case spelling exactly and contains no hidden trailing characters or blank lines.
* AI Hallucinations / Faint Audio: For flights with extreme engine roar, keep your taxonomy text strings inside species.csv descriptive (e.g., "common eider flying duck") to force Whisper to bias its vocabulary matrix toward your required reporting words [1.2].

