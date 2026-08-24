# Cockpit Data Logger — Prototype Hardware Module

**Firmware:** prototype (see `hardware.cpp`) | **Target:** Teensy 4.1 + Audio Adaptor (Rev D)

> ## ⚠️ NOT AIRWORTHY — BENCH PROTOTYPE ONLY
>
> **This device and firmware have NOT been reviewed or tested by any qualified
> avionics or aviation professional. Everything here is an unverified prototype
> intended for bench development only.**
>
> Before any use in or near an aircraft, this design MUST be reviewed and
> approved by appropriate experts. In particular:
>
> - **Do NOT connect this device to aircraft electrical systems** (no cigarette/
>   ship-bus power in flight). Run it on its own internal battery, electrically
>   isolated from the airframe.
> - **Do NOT connect this device to a shared aircraft intercom/audio panel.**
>   The intended topology is **one device per person, in-line with that one
>   person's own headset**, with **galvanic isolation** on the audio path. The
>   isolation scheme shown below is a *placeholder concept* and must be
>   specified and verified by a qualified reviewer.
> - **Do NOT permanently install this in an aircraft.** It is a temporary,
>   removable unit used only during survey missions (velcro / clamp mount).
> - Tapping the aircraft's existing PTT or wiring into certified equipment is a
>   regulated modification and is explicitly out of scope. Use a **separate,
>   added momentary button**.
>
> An earlier version of this document was produced entirely by an AI agent with
> no expert review. This corrected version is still AI-assisted and still
> requires expert sign-off.

---

## 1. What this device does

A self-contained, single-person voice + position logger for aerial wildlife
surveys. Each pilot or observer uses **their own device**, keeping their WAV
files and GPS track separate.

- Records mono voice clips from the user's headset mic to microSD as `.wav`.
- Filenames encode local time of day: `HHMMSSCC.WAV` (CC = hundredths of a
  second), so files sort chronologically and rarely collide.
- Logs a GPS track (`track.csv`) with UTC datetime, fractional seconds, and
  local seconds-past-midnight.
- **Single click** (either button) = start/stop recording.
- **Double click** = play back the most recent clip to the headset.
- Location of each clip is resolved later in post-processing by matching the
  clip's timestamp to the nearest-in-time GPS track point.

---

## 2. System block diagram (conceptual)

```text
   ┌──────────────────────────────────────────────────────────────┐
   │                    ISOLATED FROM AIRFRAME                      │
   │  (device runs on its own battery; no shared ground with ship)  │
   │                                                                │
   │   ┌───────────────┐        ┌──────────────────────────────┐   │
   │   │  AA Battery    │  5V    │        Teensy 4.1            │   │
   │   │  Pack (NiMH)   ├───────►│  + Audio Adaptor (SGTL5000)  │   │
   │   │  + protection  │  VIN   │  + built-in microSD slot     │   │
   │   └───────────────┘        │                              │   │
   │                            │  Serial1 (RX0/TX1) ──────────┼───┐
   │   ┌───────────────┐  5V    │  Pin 10  ◄── Yoke button     │   │
   │   │  microSD card  │◄──────►│  Pin  9  ◄── Observer button │   │
   │   └───────────────┘        │  Pin  2  ──► Green LED (lock) │   │
   │                            │  Pin  3  ──► Red LED (rec/err)│   │
   │                            └───────────┬──────────────────┘   │
   │                                        │ I2S audio            │
   │                            ┌───────────▼──────────────────┐   │
   │                            │  Audio Adaptor MIC/HP jack    │   │
   │                            │                              │   │
   │        ┌───────────────────┤  ◄── mic in / hp out ──►     │   │
   │        │  AUDIO ISOLATION   │                              │   │
   │        │  (transformers /   │  *** PLACEHOLDER — must be   │   │
   │        │   isolated codec)  │      specified by reviewer ***│  │
   │        └─────────┬─────────┘└──────────────────────────────┘  │
   │                  │                                             │
   └──────────────────┼─────────────────────────────────────────┬─┘
                      │                                          │
              ┌───────▼────────┐                        ┌────────▼───────┐
              │ User's headset │                        │  GPS module    │
              │ (mic + phones) │                        │  (patch ant.)  │
              │  — bench test  │                        │   5V powered   │
              │    only —      │                        └────────────────┘
              └────────────────┘

  Charging (GROUND ONLY, device OFF, NOT in flight):
     Wall/USB charger ──► barrel jack ──► battery charger circuit
     (No connection to aircraft power at any time.)
```

**Key differences from the original design:**
- Powered **only** from an internal battery in flight; no cigarette/ship-bus
  connection, no shared airframe ground.
- Audio path shown **isolated** and **per-person** (one headset, one device) —
  not tapped into a shared intercom. The isolation block is a placeholder.
- GPS powered from **5V**, not the Teensy 3.3V regulator.
- **Two** trigger buttons (yoke + observer), both added by us, neither tapping
  aircraft PTT.
- Removable mounting; no permanent installation.

---

## 3. Bill of Materials (prototype)

| Component | Purpose | Notes | Approx. Cost |
| :--- | :--- | :--- | :--- |
| Teensy 4.1 | Main processor + built-in microSD | | \$35 |
| Teensy Audio Adaptor (Rev D) | SGTL5000 codec, mic in / headphone out | Stacks on Teensy | \$15 |
| GPS module (u-blox NEO-M8 **or** Adafruit Ultimate GPS) | Position + time | u-blox preferred for reliable 5–10 Hz; MTK3339 works at 1–5 Hz | \$30–40 |
| CR1220 coin cell | GPS almanac backup (faster fix) | Not the Teensy RTC | \$2 |
| microSD card (good quality, e.g. A1/A2) | Storage | Cheap cards drop audio; buy a known-good brand | \$10 |
| 2 × momentary push buttons | Yoke + observer triggers | Wire to GND, use INPUT_PULLUP | \$10 |
| NiMH AA battery pack (e.g. 4×AA) + holder | Isolated flight power | With inline fuse | \$8 |
| Low-dropout 5V regulator/boost as needed | Clean 5V from pack | Match to pack voltage | \$5 |
| Battery protection / fuse | Safety | | \$3 |
| USB or barrel-jack charger circuit | **Ground charging only** | Never connected in flight | \$8 |
| 2 × status LEDs + 220 Ω resistors | Green=lock, Red=rec/err | | \$2 |
| **Audio isolation transformers (600:600 Ω) or isolated interface** | **Galvanic isolation of headset audio** | ***Placeholder — reviewer must specify correct GA headset interface, mic bias, levels, and isolation*** | TBD |
| GA headset connectors (PJ-055 / PJ-068) **or** in-line adapter | Interface to aviation headset | ***Reviewer to confirm; consumer 3.5 mm is NOT the GA standard*** | TBD |
| ABS enclosure (removable mount) | Housing | No permanent airframe anchoring | \$8 |
| **Est. subtotal (excl. TBD audio-interface items)** | | | **~\$135** |

> The **audio interface and isolation** line items are intentionally left as
> "TBD / reviewer-specified." This is the highest-risk part of the build and the
> part most likely to be wrong if guessed. Do not finalize it without expert input.

---

## 4. Wiring guide (prototype)

1. **Stack the Audio Adaptor** onto the Teensy 4.1 with headers. Use the Audio
   Adaptor's own microSD slot **or** the Teensy's built-in slot — the firmware
   uses `BUILTIN_SDCARD` (the Teensy 4.1 onboard slot).
2. **GPS module:**
   - GPS `VIN` → **5V** (not 3.3V)
   - GPS `GND` → Teensy `GND`
   - GPS `TX`  → Teensy **Pin 0 (RX1)**
   - GPS `RX`  → Teensy **Pin 1 (TX1)**
   *(Cross-over: the module's TX goes to the Teensy's RX. Verify against the
   Teensy 4.1 pinout card — Serial1 is RX1=pin 0, TX1=pin 1.)*
3. **Buttons:**
   - Yoke button: one leg → **Pin 10**, other leg → `GND`
   - Observer button: one leg → **Pin 9**, other leg → `GND`
   *(Both use internal pull-ups; pressed = LOW. Only one is needed for a
   single-user device, but both inputs are supported.)*
4. **LEDs:**
   - Green LED anode → **Pin 2** via 220 Ω; cathode → `GND` (GPS lock)
   - Red LED anode → **Pin 3** via 220 Ω; cathode → `GND` (recording / error)
5. **Power:** Battery pack → 5V regulator → Teensy `VIN`. Common ground within
   the device only. **No wire leaves the enclosure to aircraft power in flight.**
6. **Audio:** *Left to the reviewer.* Do not connect to an aircraft headset/
   intercom until the isolated interface is specified and approved.

---

## 5. Firmware — usage

The firmware is in `hardware.cpp`. It is a **prototype** — expect to fix a
minor library/version detail on first compile.

1. Install the **Arduino IDE** + **Teensyduino**.
2. Install libraries via Library Manager:
   - **TinyGPS++** (Mikal Hart) — parses NMEA sentences.
   - **Teensy Audio Library** (included with Teensyduino).
3. Open `hardware.cpp`.
4. Set your timezone: edit `UTC_OFFSET_HOURS` near the top
   (e.g. `-5` CDT, `-6` CST, `-8` AKDT, `-9` AKST). Note: this is a fixed
   offset; it does not auto-handle daylight saving.
5. Optionally set sample rate / mic gain / playback volume constants; **mic gain
   and volume must be tuned by ear on the bench.**
6. Connect via USB, click **Upload**. The firmware is reflashable — it is not
   "burned permanently."

### LED status
- **Green solid:** valid GPS fix (recent).
- **Green off:** no fix / stale fix.
- **Red solid:** recording in progress.
- **Red fast blink (won't stop):** fatal SD-card error at startup.

---

## 6. Bench test checklist (before anyone talks to avionics)

- [ ] Compiles under Teensyduino.
- [ ] SD card mounts; `track.csv` created with header row.
- [ ] Green LED lights when GPS gets a fix (near a window / outside).
- [ ] Single click starts recording (red on); single click stops (red off).
- [ ] Recorded file plays in a normal audio player (valid WAV, not raw).
- [ ] Filename matches local time at moment of press.
- [ ] Double click plays back the last clip to headphones.
- [ ] No audio dropouts on a long (several-minute) recording.
- [ ] Track logs at expected rate with plausible lat/lon/alt.
- [ ] Runs for the target endurance on a battery charge.

---

## 7. Known limitations / open questions for the expert review

- **Audio isolation & GA headset interface are unspecified** (highest risk).
- Sub-second timing is estimated from `TinyGPS++` age, not PPS-disciplined.
  Adequate for nearest-time matching, not for precise sync.
- Fixed UTC offset (no automatic DST).
- MTK3339 baud/rate settings are volatile across power cycles (firmware re-sends
  them each boot); a u-blox module is more robust for a production unit.
- No low-battery warning yet.
- No file-system-full handling beyond the red error LED.
