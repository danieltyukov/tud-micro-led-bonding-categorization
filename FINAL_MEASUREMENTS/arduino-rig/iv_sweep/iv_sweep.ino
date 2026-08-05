// ===========================================================================
//  iv_sweep.ino  -  micro-LED bond characterisation, I-V sweep rig
//  Arduino UNO R3 (ATmega328P @ 16 MHz).  AVCC is the ADC reference.
//
//  Wiring:  FINAL_MEASUREMENTS/arduino-rig/breadboard.pdf
//    FORCE   six resistors on D2..D7 -> FORCE rail -> die anode, header pin 4n-2
//    RETURN  die cathode -> RETURN node -> R_SENSE -> UNO GND
//    A1 reads FORCE.  A0 and A2 both read RETURN: they are the same node in
//    this build, so v_cath and v_sense are equal by construction. That is
//    intended for round 2 and it is why R_s from this rig is die + wiring.
//    A3 reads the GND rail, in the same five-hole group as the 100 R's lower
//    leg. The current is then a DIFFERENCE, i = (A2 - A3)/R_SENSE, which
//    cancels the ADC's own offset and takes the GND jumper's IR drop out of
//    the measurement. Verified necessary: step 3 on a 100 R dummy showed a
//    common ~10 mV offset on every channel, worth 26 % of the current at the
//    bottom of the sweep. See RESULTS/R2_meter.csv, fault1_adc_offset.
//
//  Capture one file per channel:
//    stty -F /dev/ttyACM0 115200 raw -echo
//    cat /dev/ttyACM0 | tee s1_D1_R_seat1.csv
// ===========================================================================

// --------------------------------------------------------- bench constants
// Both of these come from RESULTS/R2_meter.csv. Re-measure VCC every session.
const float R_SENSE = 98.61f;   // ohm. 99.0 read, x0.99602 transferred from the
                                // board's 0.1 % R_EIS_LOAD. Same physical
                                // resistor every session, do not swap it.
const float VCC_DMM = 5.034f;   // V, measured at the 5V pin with the rig idle.

// Bandgap calibration. Leave at 0 for the first flash: setup() prints the
// number to paste in here. Once set, every sweep point divides by the LIVE
// rail instead of this constant, which removes rail sag from R_s. Sag is
// current-dependent, so it lands on R_s and does not cancel within a sweep.
const float VBG_X1024 = 1112.5f;   // = VCC_DMM x bandgap raw 221, taken idle

// Common-mode ADC offset. Every channel reads LOW by this. Measured three
// independent ways on the 100 R dummy (constant mV deficit vs theory; AVR pin
// HIGH consistency; and the model-free series-divider fit v_anode = K*v_sense
// + c, which needs no assumption beyond "two resistors in series"). It cancels
// in v_die, which is a difference, but NOT in the current. Re-measure it from
// the step 3 verify sweep at the start of every session.
const float ADC_OFFSET = 0.0144f;   // V

const uint16_t OVERSAMPLE = 64;    // step 4 decided this: 5 ms on-time, no measurable heating
const uint16_t SETTLE_MS  = 2;     // after switching current, before reading
const uint16_t COOL_MS    = 250;   // current OFF between points. Fixed duty cycle.

// D2=10k  D3=5.1k  D4=2k  D5=1k  D6=330  D7=220
const uint8_t SRC_PIN[6] = {2, 3, 4, 5, 6, 7};

char label[40] = "";               // whatever you type between channels

// ------------------------------------------------------------------ current
// A pin set OUTPUT+HIGH sources through its resistor. Set INPUT it is high-Z
// and contributes nothing, which is what makes 6 pins give 63 distinct levels.
void setLevel(uint8_t mask) {
  for (uint8_t i = 0; i < 6; i++) {
    if (mask & (1 << i)) { pinMode(SRC_PIN[i], OUTPUT); digitalWrite(SRC_PIN[i], HIGH); }
    else                 { pinMode(SRC_PIN[i], INPUT); }
  }
}

// --------------------------------------------------------------- rail track
// Measures the 1.1 V bandgap against AVCC. The bandgap's absolute value is only
// specified to 1.0-1.2 V, but we do not need absolute: calibrated once against
// the DMM, its ratio between readings tracks AVCC exactly.
uint16_t bandgapRaw() {
  ADMUX = _BV(REFS0) | _BV(MUX3) | _BV(MUX2) | _BV(MUX1);
  delayMicroseconds(500);                       // bandgap source is high-Z
  ADCSRA |= _BV(ADSC);                          // throw the first one away
  while (bit_is_set(ADCSRA, ADSC)) { }
  (void)ADCL; (void)ADCH;
  uint32_t acc = 0;
  for (uint8_t i = 0; i < 16; i++) {
    ADCSRA |= _BV(ADSC);
    while (bit_is_set(ADCSRA, ADSC)) { }
    uint8_t lo = ADCL, hi = ADCH;
    acc += (uint16_t)((hi << 8) | lo);
  }
  return (uint16_t)(acc >> 4);
}

float readVcc() {
  if (VBG_X1024 <= 0.0f) return VCC_DMM;        // uncalibrated: fall back
  return VBG_X1024 / (float)bandgapRaw();
}

// ------------------------------------------------------------------ sensing
// The four channels are interleaved sample by sample, not read in four blocks.
// A block read puts ~7 ms between v_anode and v_cath, during which the die is
// heating and its forward voltage is falling. Interleaving spreads all four
// evenly over the same window, so drift is common to them and cancels in both
// differences we care about, v_die and (v_sense - v_gnd).
//
// No dummy read after a mux change. That is not an assumption: the step 3
// diagnostic swept prescaler /32, /64, /128 against discard on and off, six
// combinations, and every one gave the same answer to within noise. The 68 nF
// cap on each pin is what makes that true.
void sampleQuad(uint32_t &acc1, uint32_t &acc0, uint32_t &acc2, uint32_t &acc3) {
  acc1 = acc0 = acc2 = acc3 = 0;
  analogRead(A1); analogRead(A0); analogRead(A2); analogRead(A3);   // discarded
  for (uint16_t i = 0; i < OVERSAMPLE; i++) {
    acc1 += analogRead(A1);
    acc0 += analogRead(A0);
    acc2 += analogRead(A2);
    acc3 += analogRead(A3);
  }
}

// Straight division by 1024*OVERSAMPLE. The original sketch right-shifted by a
// hardcoded SHIFT=4, which is only correct at OVERSAMPLE=256. Step 4 asks you
// to change OVERSAMPLE to 64 and 1024, which would have silently rescaled every
// voltage by 4x and 1/4x and made the self-heating check meaningless.
float volts(uint32_t acc, float vcc) {
  return (float)acc * vcc / (1024.0f * (float)OVERSAMPLE) + ADC_OFFSET;
}

// A3 sits on the GND rail at about 0 V. A channel reading LOW cannot report a
// negative count, so the offset is clipped there and v_gnd is not recoverable.
// That is why subtracting A3 does not fix the current, and why the offset is
// added explicitly instead. A3 stays as a monitor: if the GND path ever goes
// bad, v_gnd climbs out of the clip and shows up.
float voltsRaw(uint32_t acc, float vcc) {
  return (float)acc * vcc / (1024.0f * (float)OVERSAMPLE);
}

// ------------------------------------------------------------------- serial
void readLabel() {
  uint8_t n = 0;
  unsigned long t0 = millis();
  while (millis() - t0 < 50 || n == 0) {
    if (Serial.available()) {
      char c = Serial.read();
      if (c == '\n' || c == '\r') { if (n) break; else continue; }
      if (n < sizeof(label) - 1) label[n++] = c;
      t0 = millis();
    }
  }
  label[n] = '\0';
}

void printHeader() {
  Serial.print(F("# iv_sweep  R_SENSE=")); Serial.print(R_SENSE, 2);
  Serial.print(F("  VCC_DMM="));           Serial.print(VCC_DMM, 3);
  Serial.print(F("  OVERSAMPLE="));        Serial.print(OVERSAMPLE);
  Serial.print(F("  prescaler=/32  adc_off=")); Serial.print(ADC_OFFSET * 1000.0f, 2);
  Serial.print(F("mV  vbg_cal=")); Serial.println(VBG_X1024, 1);
  Serial.print(F("# rail_tracking="));
  Serial.println(VBG_X1024 > 0 ? F("live") : F("fixed VCC_DMM"));
  if (label[0]) { Serial.print(F("# label=")); Serial.println(label); }
  Serial.println(F("level,i_mA,v_die_V,v_anode_V,v_cath_V,v_sense_V,v_gnd_V,vcc_V"));
}

// --------------------------------------------------------------------- main
void setup() {
  Serial.begin(115200);
  ADCSRA = (ADCSRA & ~0x07) | 0x05;      // prescaler /32 -> 500 kHz, 26 us/conv
  setLevel(0);
  delay(200);
  uint16_t raw = bandgapRaw();
  Serial.println(F("# ---------------------------------------------------------"));
  if (VBG_X1024 <= 0.0f) {
    Serial.print(F("# BANDGAP NOT CALIBRATED. Raw count now: ")); Serial.println(raw);
    Serial.print(F("# Set VBG_X1024 = ")); Serial.print(VCC_DMM * (float)raw, 1);
    Serial.println(F("  and reflash, then the rail is tracked per point."));
    Serial.println(F("# Do that with the rig idle and the DMM agreeing with VCC_DMM."));
  } else {
    Serial.print(F("# bandgap raw ")); Serial.print(raw);
    Serial.print(F("  ->  rail now ")); Serial.print(VBG_X1024 / (float)raw, 4);
    Serial.println(F(" V"));
  }
  Serial.println(F("# ---------------------------------------------------------"));
}

void loop() {
  printHeader();

  float i_max = 0.0f, vdie_at_max = 0.0f, vcc_min = 99.0f, vcc_max = 0.0f, vg_max = 0.0f;

  for (uint8_t m = 1; m < 64; m++) {
    setLevel(m);
    delay(SETTLE_MS);

    uint32_t a1, a0, a2, a3;
    sampleQuad(a1, a0, a2, a3);
    float vcc = readVcc();               // read while still loaded, to catch sag
    setLevel(0);                         // current OFF immediately

    float va = volts(a1, vcc);
    float vk = volts(a0, vcc);
    float vs = volts(a2, vcc);
    float vg = voltsRaw(a3, vcc);       // GND rail, uncorrected: it is clipped
    float i  = vs / R_SENSE;            // vs already has ADC_OFFSET added back

    if (i > i_max) { i_max = i; vdie_at_max = va - vk; }
    if (vg > vg_max) vg_max = vg;
    if (vcc < vcc_min) vcc_min = vcc;
    if (vcc > vcc_max) vcc_max = vcc;

    Serial.print(m);                Serial.print(',');
    Serial.print(i * 1000.0f, 4);   Serial.print(',');
    Serial.print(va - vk, 5);       Serial.print(',');
    Serial.print(va, 5);            Serial.print(',');
    Serial.print(vk, 5);            Serial.print(',');
    Serial.print(vs, 5);            Serial.print(',');
    Serial.print(vg, 5);            Serial.print(',');
    Serial.println(vcc, 4);

    delay(COOL_MS);
  }

  setLevel(0);

  // Bench sanity checks. These catch the two mistakes that actually happen.
  Serial.print(F("# i_max=")); Serial.print(i_max * 1000.0f, 3);
  Serial.print(F(" mA  v_die@i_max=")); Serial.print(vdie_at_max, 4);
  Serial.print(F(" V  rail ")); Serial.print(vcc_min, 4);
  Serial.print(F(" to ")); Serial.print(vcc_max, 4);
  Serial.print(F(" V  sag=")); Serial.print((vcc_max - vcc_min) * 1000.0f, 1);
  Serial.println(F(" mV"));
  if (i_max < 0.0002f)
    Serial.println(F("# WARNING no current. Open loop: check both F/M jumpers, "
                     "the link E4-E8, and that GND reaches the rail."));
  else if (vdie_at_max < 0.4f)
    Serial.println(F("# WARNING v_die near zero at full current. Shorted die, or "
                     "FORCE and RETURN jumpers on the same header pin."));
  if (vg_max > 0.005f)
    Serial.println(F("# WARNING GND rail is more than 5 mV above the UNO's ground. "
                     "Reseat the GND jumper: its IR drop is entering the current."));
  if ((vcc_max - vcc_min) > 0.010f)
    Serial.println(F("# WARNING rail sag over 10 mV. Shorter or thicker USB cable, "
                     "and make sure VBG_X1024 is set so the sag is divided out."));

  Serial.println();
  Serial.println(F("# sweep done. Move the two F/M jumpers, then type the next "
                   "channel label (e.g. s1_D1_R_seat1) and press enter."));
  readLabel();
}
