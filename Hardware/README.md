# Cockpit Data Logger Hardware Module
**Firmware Version:** 2.0 | **Target Platform:** Teensy 4.1 System Architecture

**Note: this hardware has not beed tested or reviewed by an expert. It was fully design by Google's Gemini AI agent. If you have experience with these designs, please contact the project maintainer.**

This sub-module provides the blueprint, Bill of Materials (BOM), and wiring matrix to build the standalone physical logging unit for the cockpit. 

The accompanying Teensy production firmware can be found in the separate source file [`hardware.cpp`](./hardware.cpp) within this directory.

---

## 1. Hardware Assembly Blueprint

```text
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
```
---

## 2. Component Specification & Cost Breakdown

| Component Name | Operational Purpose | Approx. Cost |
| :--- | :--- | :--- |
| **Teensy 4.1 Development Board** | Main processor equipped with an onboard high-speed SD card slot. | \$35.00 |
| **Teensy Audio Adaptor Shield** | Rev D breakout board adding a 3.5mm stereo headset microphone jack. | \$15.00 |
| **Adafruit Ultimate GPS Breakout** | V3 module with patch antenna tracking live NMEA string metrics. | \$30.00 |
| **CR1220 Coin Cell Battery** | Populates GPS clock memory for instant satellite time sync locks. | \$2.00 |
| **Momentary Push Button** | Weatherproof cockpit button switch used as an audio interrupt trigger. | \$5.00 |
| **SPDT Toggle Switch** | Heavy-duty toggle selector mapping Plane Power vs. Internal Battery. | \$3.00 |
| **4xAA Battery Holder enclosure** | Delivers standalone battery operations exceeding 8 continuous hours. | \$5.00 |
| **5V Buck Converter Module** | Steps variable plane cigarette lines down to a clean, filtered 5V supply. | \$5.00 |
| **2.1mm Chassis Barrel Jack** | Threaded component through the box wall for remote plane charging cords. | \$3.00 |
| **12V Cigarette Adapter Cord** | Standard cockpit accessory line connecting plane bus grids to 2.1mm inputs. | \$7.00 |
| **Flanged ABS Project Enclosure** | Drillable protective shell box allowing permanent cockpit anchoring. | \$8.00 |
| **Net Cost Estimate** | | **~\$118.00** |
---


## 3. Pin Connection Matrix & Wiring Guide

1. **Stack Audio Shield Layer**: Solder header pin strips straight down onto your Teensy 4.1. Mount the Teensy Audio Adaptor Shield directly down onto those matching header pins.
2. **GPS Module Wiring**: Connect four jumper leads across the components:
   * VIN on GPS Breakout ---> 3.3V pin on Teensy 4.1
   * GND on GPS Breakout ---> Any available GND pin on Teensy 4.1
   * RX on GPS Breakout ---> Pin 1 (TX1) hardware serial port on Teensy 4.1
   * TX on GPS Breakout ---> Pin 0 (RX1) hardware serial port on Teensy 4.1
3. **Status Indicator Layout Hookup**: Mount feedback LEDs inside drilled outer casing holes:
   * Green LED (Positive leg) ---> Pin 2 through a 220-ohm protective resistor. (GND to short leg).
   * Red LED (Positive leg) ---> Pin 3 through a 220-ohm protective resistor. (GND to short leg).
4. **Trigger Mechanism Wiring**: Mount your tactical toggle switch button through the project case. Wire Terminal 1 directly to Pin 10 on your Teensy, and Terminal 2 straight to an available GND terminal pin block.
5. **Power Safety Configuration**: Wire the outer pins of the SPDT power toggle switch to the positive lines of your Buck Converter output and your AA battery container. Connect the center selector pin to the Teensy VIN port pin. Combine all system ground wires together securely.


## 4. Firmware File Reference

The cockpit data logger requires specialized software to manage real-time satellite updates, time-zone alignment, and high-speed audio writes simultaneously. This code is managed in a separate file within this repository directory named **`hardware.cpp`**.

### Usage & Installation

1. **Setup Environment:** Open the **Arduino IDE** on your computer. Ensure you have installed the **Teensyduino** board extension tools so the compiler can speak to the Teensy 4.1 hardware chip.
2. **Library Requirements:** Open the Arduino Library Manager (`Ctrl + Shift + I` or `Sketch > Include Library > Manage Libraries...`) and download these two dependencies:
   * **`TinyGPS++`** (By Mikal Hart) — Unpacks raw satellite positional text lines.
   * **`TimeLib`** (By Michael Margolis) — Manages the aircraft's internal clock matrix.
3. **Open the Script:** Open the [`hardware.cpp`](./hardware.cpp) file from your local directory inside the Arduino IDE.
4. **Configure Local Timezone:** Navigate to the top of the file and locate the variable `const int UTC_OFFSET = -5;`. Adjust this integer to match your survey flight corridor parameter mapping rules (e.g., set to `-5` for Central Daylight Time or `-8` for Alaska Daylight Time). This forces the physical hardware to write local tracking seconds past midnight, ensuring an identical timeline lock with your desktop computer app.
5. **Burn to Device:** Connect your constructed hardware logger box to your computer using a standard micro-USB or USB-C data cable. Click the **Upload Arrow** in the top left corner of the Arduino window to compile the code and burn the firmware permanently into your logger's flash memory banks. Once done, unplug the box; it is fully ready for flight operations!
