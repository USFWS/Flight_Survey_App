/* =============================================================================
 *  Cockpit Data Logger  —  PROTOTYPE FIRMWARE  (Teensy 4.1 + Audio Shield)
 * =============================================================================
 *
 *  ****  NOT AIRWORTHY  —  BENCH PROTOTYPE ONLY  ****
 *
 *  This firmware and the associated hardware have NOT been reviewed or tested
 *  by a qualified avionics/aviation professional. It MUST NOT be connected to
 *  aircraft electrical systems or to an aircraft intercom/audio panel, and MUST
 *  NOT be installed or flown, until reviewed and approved by appropriate
 *  experts. The audio interface to any aviation headset requires galvanic
 *  isolation that is the reviewer's responsibility to verify. Use on the bench
 *  only, with a test mic/headset and battery power.
 *
 *  Design assumptions (one person per device):
 *    - Single mono channel: mic in, playback to both ears.
 *    - Single click (either button) = start/stop recording.
 *    - Double click            = play back the most recent recording.
 *    - Two momentary buttons (yoke + observer) OR'd in firmware.
 *    - WAV filenames: HHMMSSCC.WAV  (local time; CC = hundredths of a second).
 *    - Track file logs UTC datetime + fractional seconds AND local seconds
 *      past midnight, so post-processing can match WAV timestamps by nearest
 *      time.
 * =============================================================================
 */

#include <Audio.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>
#include <TinyGPS++.h>

// ----------------------------- Configuration --------------------------------
const int  UTC_OFFSET_HOURS = -5;     // CDT=-5, CST=-6, AKDT=-8, AKST=-9
const int  YOKE_BUTTON_PIN     = 10;  // pilot's yoke button (momentary to GND)
const int  OBSERVER_BUTTON_PIN = 9;   // observer button    (momentary to GND)
const int  GREEN_LED = 2;             // GPS lock status
const int  RED_LED   = 3;             // recording / error status

#define GPS_SERIAL Serial1            // RX1=pin0, TX1=pin1 on Teensy 4.1

// --- MTK3339 (Adafruit Ultimate GPS) configuration strings ---------------
// NOTE: these are for the MTK3339. A u-blox module uses entirely different
// (binary UBX) configuration and these will do nothing on it.
// Baud rate must be raised BEFORE 5 Hz output will fit on the wire.
const char PMTK_SET_BAUD_38400[]  = "$PMTK251,38400*27";       // set 38400
const char PMTK_SET_5HZ[]         = "$PMTK220,200*2C";         // 200ms = 5Hz
const char PMTK_SET_1HZ[]         = "$PMTK220,1000*1F";        // 1000ms = 1Hz
// Output RMC + GGA only (position, time, altitude) to keep the wire light:
const char PMTK_OUTPUT_RMC_GGA[]  =
  "$PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*28";

const unsigned int SAMPLE_RATE = 44100;   // 22050 also fine for voice
const unsigned int BITS_PER_SAMPLE = 16;
const unsigned int NUM_CHANNELS = 1;      // mono

const unsigned long GPS_INTERVAL_MS   = 200;  // track log period (5 Hz target)
const unsigned int  DEBOUNCE_MS       = 40;
const unsigned int  DOUBLE_CLICK_MS   = 350;  // window to detect 2nd click
const int           MIC_GAIN          = 20;   // 0-63; TUNE ON BENCH (was 35)

// ----------------------------- Audio graph ----------------------------------
AudioInputI2S        audioInput;
AudioRecordQueue     recQueue;
AudioPlaySdWav       playWav;
AudioOutputI2S       audioOutput;
AudioControlSGTL5000 audioShield;

AudioConnection      pc1(audioInput, 0, recQueue, 0);   // mic -> record queue
AudioConnection      pc2(playWav, 0, audioOutput, 0);   // playback -> L
AudioConnection      pc3(playWav, 1, audioOutput, 1);   // playback -> R

// ----------------------------- Globals --------------------------------------
TinyGPSPlus gps;

bool          isRecording = false;
File          audioFile;
File          trackFile;
uint32_t      recordedDataBytes = 0;
char          lastWavName[16] = "";      // most recent completed recording
unsigned long lastGpsWrite = 0;

// Button state (both buttons OR'd)
bool          lastButtonDown = false;
unsigned long lastEdgeMs = 0;
unsigned long lastClickMs = 0;
bool          pendingSingleClick = false;

// ----------------------------- Helpers --------------------------------------
bool anyButtonDown() {
  return (digitalRead(YOKE_BUTTON_PIN) == LOW) ||
         (digitalRead(OBSERVER_BUTTON_PIN) == LOW);
}

// Compute local time-of-day components + hundredths from GPS + millis fraction.
// Returns false if GPS time not yet valid.
bool localTimeNow(int &hh, int &mm, int &ss, int &cc,
                  unsigned long &localSecondsOfDay) {
  if (!gps.time.isValid() || !gps.date.isValid()) return false;

  // Seconds since midnight UTC from the last GPS fix:
  long utcSec = (long)gps.time.hour() * 3600L +
                (long)gps.time.minute() * 60L +
                (long)gps.time.second();

  // Add elapsed time since that fix using its age (ms), for sub-second detail.
  unsigned long ageMs = gps.time.age();          // ms since time was parsed
  long totalMs = utcSec * 1000L + (long)ageMs;

  // Apply local offset.
  totalMs += (long)UTC_OFFSET_HOURS * 3600L * 1000L;
  // Wrap into [0, 86400000).
  long dayMs = 86400000L;
  totalMs = ((totalMs % dayMs) + dayMs) % dayMs;

  long totalSec = totalMs / 1000L;
  cc = (int)((totalMs % 1000L) / 10L);           // hundredths
  hh = (int)(totalSec / 3600L);
  mm = (int)((totalSec % 3600L) / 60L);
  ss = (int)(totalSec % 60L);
  localSecondsOfDay = (unsigned long)totalSec;
  return true;
}

// --- WAV header (44-byte canonical PCM). Written twice: reserve, then patch.
void writeWavHeader(File &f, uint32_t dataBytes) {
  uint32_t byteRate   = SAMPLE_RATE * NUM_CHANNELS * (BITS_PER_SAMPLE / 8);
  uint16_t blockAlign = NUM_CHANNELS * (BITS_PER_SAMPLE / 8);
  uint32_t chunkSize  = 36 + dataBytes;

  f.seek(0);
  f.write((const uint8_t*)"RIFF", 4);
  f.write((uint8_t*)&chunkSize, 4);
  f.write((const uint8_t*)"WAVE", 4);
  f.write((const uint8_t*)"fmt ", 4);
  uint32_t sub1 = 16;           f.write((uint8_t*)&sub1, 4);
  uint16_t fmt  = 1;            f.write((uint8_t*)&fmt, 2);   // PCM
  uint16_t ch   = NUM_CHANNELS; f.write((uint8_t*)&ch, 2);
  uint32_t sr   = SAMPLE_RATE;  f.write((uint8_t*)&sr, 4);
  f.write((uint8_t*)&byteRate, 4);
  f.write((uint8_t*)&blockAlign, 2);
  uint16_t bps = BITS_PER_SAMPLE; f.write((uint8_t*)&bps, 2);
  f.write((const uint8_t*)"data", 4);
  f.write((uint8_t*)&dataBytes, 4);
}

void errorBlink() {   // call in a tight spot to signal fatal SD error
  while (1) { digitalWrite(RED_LED, HIGH); delay(120);
              digitalWrite(RED_LED, LOW);  delay(120); }
}

void configureGps() {
  // Start at the module default (9600), raise baud, then re-open faster.
  GPS_SERIAL.begin(9600);
  delay(250);
  GPS_SERIAL.println(PMTK_SET_BAUD_38400);
  GPS_SERIAL.flush();
  delay(250);
  GPS_SERIAL.begin(38400);           // Teensy side now matches module
  delay(250);
  GPS_SERIAL.println(PMTK_OUTPUT_RMC_GGA);
  delay(100);
  GPS_SERIAL.println(PMTK_SET_5HZ);  // now 5 Hz fits on the wire
  delay(100);
  // If the module was power-cycled and ignored the baud change, it will still
  // be at 9600 and we'll see no data; the GREEN_LED simply won't light. In
  // that case, comment the baud lines and run at 1 Hz (PMTK_SET_1HZ) to debug.
}

// ----------------------------- Setup ----------------------------------------
void setup() {
  Serial.begin(115200);
  configureGps();

  pinMode(YOKE_BUTTON_PIN, INPUT_PULLUP);
  pinMode(OBSERVER_BUTTON_PIN, INPUT_PULLUP);
  pinMode(GREEN_LED, OUTPUT);
  pinMode(RED_LED, OUTPUT);

  // Lamp test
  digitalWrite(GREEN_LED, HIGH); digitalWrite(RED_LED, HIGH); delay(500);
  digitalWrite(GREEN_LED, LOW);  digitalWrite(RED_LED, LOW);

  AudioMemory(120);
  audioShield.enable();
  audioShield.inputSelect(AUDIO_INPUT_MIC);
  audioShield.micGain(MIC_GAIN);
  audioShield.volume(0.6);            // headphone playback level (tune)

  if (!SD.begin(BUILTIN_SDCARD)) errorBlink();

  // Create track file header once.
  trackFile = SD.open("track.csv", FILE_WRITE);
  if (trackFile) {
    if (trackFile.size() == 0) {
      trackFile.println("utc_date,utc_time,utc_frac_s,local_sec_of_day,"
                        "lat,lon,alt_m,status");
    }
    trackFile.close();
  }
}

// ----------------------------- Recording ------------------------------------
void startRecording() {
  int hh, mm, ss, cc; unsigned long sod;
  char filename[16];
  if (localTimeNow(hh, mm, ss, cc, sod)) {
    snprintf(filename, sizeof(filename), "%02d%02d%02d%02d.WAV", hh, mm, ss, cc);
  } else {
    // No GPS time yet: fall back to a millis-based unique name, flag in track.
    snprintf(filename, sizeof(filename), "NOFIX%03lu.WAV",
             (millis() / 100) % 1000);
  }

  // If a same-second collision somehow occurs, bump hundredths until free.
  while (SD.exists(filename)) {
    cc = (cc + 1) % 100;
    snprintf(filename, sizeof(filename), "%02d%02d%02d%02d.WAV", hh, mm, ss, cc);
  }

  audioFile = SD.open(filename, FILE_WRITE);
  if (!audioFile) { digitalWrite(RED_LED, HIGH); return; }

  writeWavHeader(audioFile, 0);      // reserve 44 bytes; patched on stop
  recordedDataBytes = 0;
  strncpy(lastWavName, filename, sizeof(lastWavName));
  recQueue.begin();
  isRecording = true;
  digitalWrite(RED_LED, HIGH);
}

void serviceRecording() {
  // Drain ALL available blocks each pass to avoid overflow/drops.
  while (recQueue.available() > 0) {
    audioFile.write((const uint8_t*)recQueue.readBuffer(), 256);
    recQueue.freeBuffer();
    recordedDataBytes += 256;
  }
}

void stopRecording() {
  recQueue.end();
  while (recQueue.available() > 0) {           // flush remainder
    audioFile.write((const uint8_t*)recQueue.readBuffer(), 256);
    recQueue.freeBuffer();
    recordedDataBytes += 256;
  }
  writeWavHeader(audioFile, recordedDataBytes); // patch real length
  audioFile.close();
  isRecording = false;
  digitalWrite(RED_LED, LOW);
}

// ----------------------------- Playback -------------------------------------
void playLast() {
  if (strlen(lastWavName) == 0) return;
  if (isRecording) return;                 // ignore during recording
  playWav.play(lastWavName);
  delay(5);
  // Non-blocking: playback continues; loop() keeps running. We simply don't
  // start a new recording while playWav.isPlaying() is true.
}

// ----------------------------- Track logging --------------------------------
void logBreadcrumb() {
  if (!gps.location.isValid() || !gps.time.isValid() || !gps.date.isValid())
    return;

  int hh, mm, ss, cc; unsigned long sod;
  localTimeNow(hh, mm, ss, cc, sod);
  unsigned long ageMs = gps.time.age();
  int fracS = (int)((ageMs % 1000));      // ms into the current UTC second

  trackFile = SD.open("track.csv", FILE_WRITE);
  if (!trackFile) { digitalWrite(RED_LED, HIGH); return; }

  trackFile.printf("%04d-%02d-%02d,", gps.date.year(), gps.date.month(),
                   gps.date.day());
  trackFile.printf("%02d:%02d:%02d,", gps.time.hour(), gps.time.minute(),
                   gps.time.second());
  trackFile.printf("%d,", fracS);
  trackFile.printf("%lu,", sod);
  trackFile.print(gps.location.lat(), 6); trackFile.print(",");
  trackFile.print(gps.location.lng(), 6); trackFile.print(",");
  trackFile.print(gps.altitude.meters(), 1); trackFile.print(",");
  trackFile.println(isRecording ? "RECORDING" : "TRACKING");
  trackFile.close();
}

// ----------------------------- Button logic ---------------------------------
// Non-blocking edge detect + single/double click discrimination.
void serviceButtons() {
  bool down = anyButtonDown();
  unsigned long now = millis();

  // Debounced press edge (transition to down)
  if (down && !lastButtonDown && (now - lastEdgeMs) > DEBOUNCE_MS) {
    lastEdgeMs = now;
    if (pendingSingleClick && (now - lastClickMs) <= DOUBLE_CLICK_MS) {
      // Second click within window -> double click
      pendingSingleClick = false;
      playLast();
    } else {
      // First click; wait to see if a second follows
      pendingSingleClick = true;
      lastClickMs = now;
    }
  }
  if (!down && lastButtonDown && (now - lastEdgeMs) > DEBOUNCE_MS) {
    lastEdgeMs = now;   // release edge
  }
  lastButtonDown = down;

  // If the double-click window expired, commit the single click.
  if (pendingSingleClick && (now - lastClickMs) > DOUBLE_CLICK_MS) {
    pendingSingleClick = false;
    if (!playWav.isPlaying()) {
      if (!isRecording) startRecording(); else stopRecording();
    }
  }
}

// ----------------------------- Main loop ------------------------------------
void loop() {
  // 1) Feed GPS parser continuously.
  while (GPS_SERIAL.available() > 0) gps.encode(GPS_SERIAL.read());

  // 2) GPS lock LED.
  digitalWrite(GREEN_LED,
    (gps.location.isValid() && gps.location.age() < 1500) ? HIGH : LOW);

  // 3) Service audio recording (must run often).
  if (isRecording) serviceRecording();

  // 4) Buttons (non-blocking).
  serviceButtons();

  // 5) Periodic track logging (skip a beat if actively draining audio is busy;
  //    recording still takes priority via ordering above).
  if (millis() - lastGpsWrite >= GPS_INTERVAL_MS) {
    lastGpsWrite = millis();
    logBreadcrumb();
  }
}
