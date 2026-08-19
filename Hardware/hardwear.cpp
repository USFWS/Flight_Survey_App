#include <Audio.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>
#include <SerialFlash.h>
#include <TinyGPS++.h>
#include <TimeLib.h> 

const int UTC_OFFSET = -5; // CDT = -5, CST = -6, AKDT = -8, AKST = -9
const int BUTTON_PIN = 10;
const int GREEN_LED  = 2;   
const int RED_LED    = 3;   
#define GPS_SERIAL Serial1  

TinyGPSPlus gps;
AudioInputI2S            audioInput;     
AudioRecordQueue         queue1;         
AudioConnection          patchCord1(audioInput, 0, queue1, 0); 
AudioControlSGTL5000     audioShield;    

bool isRecording = false;
unsigned long lastGpsWrite = 0;
const unsigned long GPS_INTERVAL = 400; 
File audioFile;
File trackFile;

void setup() {
  Serial.begin(9600); GPS_SERIAL.begin(9600);
  pinMode(BUTTON_PIN, INPUT_PULLUP); pinMode(GREEN_LED, OUTPUT); pinMode(RED_LED, OUTPUT);
  digitalWrite(GREEN_LED, HIGH); digitalWrite(RED_LED, HIGH); delay(600);
  digitalWrite(GREEN_LED, LOW);  digitalWrite(RED_LED, LOW);
  AudioMemory(60); audioShield.enable(); audioShield.inputSelect(AUDIO_INPUT_MIC); audioShield.micGain(35);                  
  if (!SD.begin(BUILTIN_SDCARD)) {
    while (1) { digitalWrite(RED_LED, HIGH); delay(100); digitalWrite(RED_LED, LOW); delay(100); }
  }
  trackFile = SD.open("track.csv", FILE_WRITE);
  if (trackFile) {
    if (trackFile.size() == 0) { trackFile.println("Timestamp,Latitude,Longitude,Altitude_M,Status"); }
    trackFile.close();
  }
}

void loop() {
  while (GPS_SERIAL.available() > 0) { gps.encode(GPS_SERIAL.read()); }
  if (gps.location.isValid() && gps.location.age() < 1500) { digitalWrite(GREEN_LED, HIGH); } 
  else { digitalWrite(GREEN_LED, LOW); }
  if (millis() - lastGpsWrite >= GPS_INTERVAL) { lastGpsWrite = millis(); logBreadcrumb(); }
  if (digitalRead(BUTTON_PIN) == LOW) {
    delay(40); 
    if (digitalRead(BUTTON_PIN) == LOW) {
      if (!isRecording) startRecording(); else stopRecording();
      while(digitalRead(BUTTON_PIN) == LOW); delay(40);
    }
  }
  if (isRecording) { continueRecording(); }
}

void logBreadcrumb() {
  if (gps.location.isValid() && gps.time.isValid() && gps.date.isValid()) {
    trackFile = SD.open("track.csv", FILE_WRITE);
    if (trackFile) {
      setTime(gps.time.hour(), gps.time.minute(), gps.time.second(), gps.date.day(), gps.date.month(), gps.date.year());
      adjustTime(UTC_OFFSET * 3600); 
      unsigned long local_seconds = (hour() * 3600) + (minute() * 60) + second();
      trackFile.print(local_seconds); trackFile.print(",");
      trackFile.print(gps.location.lat(), 6); trackFile.print(",");
      trackFile.print(gps.location.lng(), 6); trackFile.print(",");
      trackFile.print(gps.altitude.meters()); trackFile.print(",");
      trackFile.println(isRecording ? "RECORDING" : "TRACKING"); trackFile.close();
    }
  }
}

void startRecording() {
  char filename[] = "00000000.WAV";
  if (gps.time.isValid() && gps.date.isValid()) {
    setTime(gps.time.hour(), gps.time.minute(), gps.time.second(), gps.date.day(), gps.date.month(), gps.date.year());
    adjustTime(UTC_OFFSET * 3600);
    sprintf(filename, "%02d%02d%02d01.WAV", hour(), minute(), second());
  }
  audioFile = SD.open(filename, FILE_WRITE);
  if (audioFile) { queue1.begin(); isRecording = true; digitalWrite(RED_LED, HIGH); }
}

void continueRecording() {
  if (queue1.available() >= 1) {
    byte buffer;
    memcpy(buffer, queue1.readBuffer(), 256); queue1.freeBuffer();
    audioFile.write(buffer, 256);
  }
}

void stopRecording() {
  queue1.end(); 
  while (queue1.available() > 0) { audioFile.write((byte*)queue1.readBuffer(), 256); queue1.freeBuffer(); }
  audioFile.close(); isRecording = false; digitalWrite(RED_LED, LOW); 
}
