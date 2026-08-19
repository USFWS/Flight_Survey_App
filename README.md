# Aerial Wildlife Survey Post-Processor

An automated local data workstation designed to ingest, synchronize, and transcribe post-flight aerial transect survey observations. This software connects raw hardware cockpit audio recordings with timestamped flight tracking data via a nearest-neighbor spatial time alignment algorithm.

The matching data logging cockpit hardware ecosystem is fully documented in the [Hardware Documentation Module](./hardware/README.md).

## Key Features
* **AI Post-Flight Transcription:** Uses local OpenAI Whisper execution matrices to transcribe raw cockpit voice recordings.
* **Intelligent Sentence Splitting:** Parses compound multi-species observations (e.g., *"25 gulls and 10 cormorants"*) automatically into individual data lines.
* **Nearest-Neighbor Coordinate Sync:** Correlates unique time-coded sub-second filenames against local tracking metrics to extract decimal degrees.
* **Integrated Workspace Panel:** Provides an interactive 12-column verification grid equipped with audio playback, line cloning, and mistake purging actions.
* **Timezone Offset Drops:** Outputs ISO 8601 compliant data tags (`YYYY-MM-DDTHH:MM:SS.xxx-XX:00`) tailored to regional parameters.

---

## File Architecture & Directory Layout

To process field operations seamlessly, preserve this local working structure:

```text
📂 Flight_Survey_App/
 ├── 📄 survey_app.py        # Master controller launcher 
 ├── 📄 survey_ui.py         # 12-column CustomTkinter visual viewport
 ├── 📄 survey_controller.py # Ingestion processor threads & coordinate lookup loops
 ├── 📄 survey_logic.py      # Species-split rules & voice numerical parsing regex
 ├── ⚙️ ffmpeg.exe           # Local audio streaming decoder executable
 └── 📂 Flight_Session_01/   # Example target field processing asset folder
       ├── 📄 track.csv      # Positional data log output from cockpit hardware
       ├── 📄 species.csv    # Custom agency taxonomy lookup dictionary
       ├── 🎵 17133201.WAV   # Flight observation audio files (HHMMSSxx format)
       └── 🎵 17140510.WAV
```

---

## Installation & Environment Setup

### 1. Core Python Dependencies
Ensure you have Python 3.11+ installed with the system path option flagged. Install the complete application dependency stack via your command terminal prompt:
```bash
pip install openai-whisper pandas customtkinter geopandas shapely pygame scipy openpyxl
```

### 2. FFmpeg Background Codec Configuration
Whisper requires an underlying decoder engine to unpack spatial audio wave files cleanly.
1. Download the Windows binary assets package from the official [Gyan.dev FFmpeg Distribution](https://gyan.dev) (Select the `ffmpeg-git-essentials.zip` release).
2. Extract the file content, open the nested **`bin`** folder, and locate **`ffmpeg.exe`**.
3. **Copy and paste** `ffmpeg.exe` directly inside your `Flight_Survey_App` directory right next to `survey_app.py`.

---

## Workspace Pre-Configuration

Before loading the desktop workstation window, ensure your targeted survey flight asset folder contains these two template structures:

### Target A: `track.csv`
Your cockpit logger’s tracking log requires these exact column text labels:
```csv
Timestamp,Latitude,Longitude,Altitude
17:12:50.20,61.21811,-149.90032,154.2
17:12:50.60,61.21952,-149.90154,154.6
```
*Note: Other column are optional and are not used. Timestamp represents hours, minutes, seconds past midnight local clock time.*

### Target B: `species.csv`
Your agency taxonomy dictionary maps descriptions to database codes. Descriptions containing commas must be wrapped inside double quotes. Do not include the generic term "colony" as a standalone keyword anchor. *Note that the current app and species dictionary is designed for a seabird colony survey.*

**Optimizing for Variations** If you often say different things for the same observation (e.g., sometimes you say "nest seen", sometimes just "nest"), keep the description in your CSV short and distinct. For example, change "nest seen" to just "nest". That way, whether you say "nest seen", "large nest", or "eagle nest", the word "nest" is caught by the script and automatically populates the NEST code.

```csv
Code,English_Name
BLKI,"Black-legged Kittiwake, kittiwakes, kittiwake"
GULL,"gull, gulls, unknown gull"
LGULL,"unknown large gull, glacous-winged gull, large gulls" 
SGULL,"unknown small gull, short-billed gull, small gulls" 
TERN,"tern arctic tern"
MURR,"common murre, thick-billed murre, murre"
PIGU,"pigeon guillemot"
PUFF,"unknown puffin, puffin"
TUPU,"tufted puffin"
HOPU,"horned puffin"
CORM,"unknown commorant, cormorant"
RFCO,"red faced cormorant"
PECO,"pelagic cormorant"
UNAU,"unknown auklet"
OTHER,"any other species, duck, sea duck, eider, scoter"
NEST,"nest seen active nest"
NESTLING,"nestling seen nestlings"
POOP,"large poop whitewash area indicator of likely nesting"
SEOT,"sea otter, otters"
STSL,"Steller's sea lion"
TEST,"testing the mike, test test 123, test"
BEGIN,"survey effort starts here, on effort, begin survey"
END,"End survey off effort"
```

### Target C: `transects.geojson` or `.shp`
GIS Transects (Optional): If a survey uses predefined transects, place a polygon dataset named `transects.geojson` or `transects.shp` directly in your folder. If you don't use them, simply leave it out!

---

## Operational Workflow

### Step 1: Initialize Session Context
Launch your workspace interface from your local command terminal window prompt:
```bash
python survey_app.py
```
Fill out your specific metadata tracking variables in the dashboard header entries (**Year**, **Month**, **Day**, **Observer Initials**, and **Flight Seat assignment**). Choose your matching survey region from the **Timezone Dropdown** to dictate final time calculations.

### Step 2: Ingest Flight Data
Click **Load Data Folder**. The picker dialog automatically targets the root path of your application directory for quick subfolder navigation. Select your target session directory. The progress tracking bar will animate while the multi-threaded processor extracts tracking paths and transcribes audio blocks.

### Step 3: Human Verification Loop
* **Audio Playback:** Click the purple **▶ Play** button on any line item to review and stream the raw recording directly into your flight headset.
* **Direct Overrides:** Clean up mechanical mistakes or voice glitches directly within the editable text boxes on screen. 
* **Row Cloning:** If a nesting colony recording holds secondary species missed by the AI, click blue **📋 Clone**. A row replica will slide **directly underneath that specific parent observation**, duplicating the file markers and GPS points while setting counts to 1 so you can input missed sightings quickly.
* **Purge Entries:** Use the dark red **❌ Delete** action button to drop checklist trials, cockpit radio chatter, or blank file triggers instantly.

### Step 4: Final Database Export
When a row matches true flight observations, select your finalized species code and tap **Verify Row** to secure a green **Saved! ✅** check mark. Click the dark green **Export CSV Data** button at the top to re-index all operational numbers and save a compliance-ready flight database.

# Future enhancements

  - add a moving maps with observations, transcects and trackline,
  - allow visual inspection of data or csv output below validating,
  - allow cancelation of validation,
  - add "waterfowl" mode: add observation type column,
  - others as needed.

# Getting help

Contact the [Erik Osnas](mailto:erik_osnas@fws.gov) for help with this repository.

# Contribute

Contact the project maintainer for information about contributing to this repository. Submit a [GitHub Issue](https://github.com/USFWS/Flight_Survey_App/issues) to report a bug or request a feature or enhancement.

---

![](https://i.creativecommons.org/l/zero/1.0/88x31.png) This work is
licensed under a [Creative Commons Zero Universal v1.0
License](https://creativecommons.org/publicdomain/zero/1.0/).

*Built by FWS Alaska Region · Prototype developed 2026*
*Code: https://github.com/USFWS/Flight_Survey_App · Contact: [Erik Osnas](mailto:erik_osnas@fws.gov)*

