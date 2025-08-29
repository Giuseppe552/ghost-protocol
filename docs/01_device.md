# 📱 Device Tracking — How Your Phone Leaks Identity

---

## 🧸 5-Year-Old Mode (Simple Explanation)

Imagine your phone is like a **really loud parrot**.  
Everywhere it goes, it **shouts your name, your home address, and your favorite snack**.  
Even if you don’t want it to, it keeps talking:

- 📡 It yells at cell towers: “I’m here! I’m here!”  
- 🌍 It whispers your GPS location in every photo you take.  
- 🛒 It tells apps when you open them, what you click, and even how fast you’re walking.  
- 🐦 It remembers everything, and those memories never really go away.

That’s why companies, governments, or even strangers can **follow your parrot’s voice** and know exactly where you’ve been.

---

## 🧑‍💻 Engineer Mode (Technical Deep Dive)

### 🔑 Unique Identifiers
Every phone has baked-in **unique IDs**:
- **IMEI** (International Mobile Equipment Identity): hardware fingerprint of your device.  
- **IMSI** (International Mobile Subscriber Identity): tied to your SIM card + carrier.  
- **Baseband IDs**: even deeper hardware-level signals, difficult to mask.  

These identifiers are **broadcasted to nearby towers** whenever your device connects, allowing carriers (and anyone with IMSI catchers / Stingrays) to triangulate your location.

---

### 📡 Location Tracking
Phones reveal location through multiple layers:
1. **Cell tower triangulation** (works even if GPS is off).  
2. **Wi-Fi probes** — your device constantly shouts nearby network names (“Is Starbucks Wi-Fi here?”), which can be logged.  
3. **Bluetooth beacons** — used in malls, stadiums, even public transport for micro-tracking.  
4. **GPS metadata in EXIF** — photos and videos silently embed coordinates.

---

### 🛠️ Telemetry & Apps
- Every app includes **analytics SDKs** (Google Firebase, Meta App Events, etc).  
- These leak:  
  - Device model  
  - OS version  
  - Installed apps  
  - In some cases, accelerometer/gyroscope readings (to fingerprint motion).  

This data is monetized via **advertising IDs** (GAID on Android, IDFA on iOS). Even if “reset,” fingerprinting correlates users across resets.

---

### 🎯 Threat Models
- **Governments**: can triangulate positions via carrier logs + compel providers.  
- **Hackers**: can deploy IMSI catchers to spoof towers and grab metadata.  
- **Advertisers**: build cross-app profiles by correlating telemetry and IDs.  
- **OS Vendors (Google/Apple)**: retain master visibility over device activity.

---

## ✅ Countermeasures
1. **Airplane Mode ≠ Invisible** — some radios still ping (esp. baseband).  
2. **Use secondary devices** with no SIM for sensitive work.  
3. **Turn off Wi-Fi/Bluetooth scanning** in settings.  
4. **Strip photo metadata** using tools like `exiftool` or this repo’s `metadata_cleaner.py`.  
5. **Custom ROMs (GrapheneOS)** to minimize Google telemetry.  

---

## 🧭 Key Insight
A phone is never truly “silent.”  
The best you can do is **minimize signals**, use burner hardware, and understand exactly **which layers leak what data**.

