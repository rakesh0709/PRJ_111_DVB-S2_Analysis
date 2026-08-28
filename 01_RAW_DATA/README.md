# 01_RAW_DATA — Raw Dataset Organization

## Overview
This directory stores the primary raw datasets collected and organized for **Project PRJ_111: Development of a Software Application for Analysis and Processing of DVB-S2 Receiver Output Stream**.

> **Note on Version Control & Local Storage:**  
> In accordance with project repository policies, all large binary streams (`.ts`, `.pcap`, `.zip`, etc.) are retained **locally** and are excluded from GitHub commits via `.gitignore`. This `README.md` documents the verified folder structure, filenames, and roles of the raw data.

---

## Directory Organization & Dataset Inventory

```
01_RAW_DATA/
├── 01_BBFRAME_GSE/
│   └── dvb-s2_bb_example.pcap
├── 02_GSE/
│   └── GSExtract/
│       └── sample.ts
├── 03_TS/
│   ├── Astra_19.2E_France/
│   │   ├── astra192E-ts1080-2018-05-11.ts
│   │   └── astra192E-ts1120-2018-05-11.ts
│   ├── Astra_19.2E_Spain/
│   │   └── astra-10847V-2020-08-24.ts
│   └── DVBS2_toolkit/
│       └── sample.ts
├── 04_RFI_AI/
│   ├── Modulation Recognition.zip
│   └── RFI classification.zip
└── 05_REAL_DVB_S2/
    └── GRCon22_Blockstream/
        ├── blockstream.ts
        └── ip_packets.pcap
```

---

## Folder Descriptions (Confirmed from Existing Files)

### 1. `01_BBFRAME_GSE/`
* **File:** `dvb-s2_bb_example.pcap`
* **Purpose:** DVB-S2 Baseband (BB) Frame and GSE packet capture data for Link/Baseband-layer parser design, protocol inspection, and validation.
* **Source/Details:** Wireshark DVB-S2 BBFrame/GSE protocol dissector example capture. Further technical properties: *Source/details to be documented.*

### 2. `02_GSE/`
* **Subfolder / File:** `GSExtract/sample.ts`
* **Purpose:** Sample stream containing Generic Stream Encapsulation (GSE) packets for validating GSE de-encapsulation and header parsing logic.
* **Source/Details:** `ssloxford/gsextract` parser validation sample. Further technical properties: *Source/details to be documented.*

### 3. `03_TS/`
* **Subfolders & Files:**
  * `Astra_19.2E_France/` (`astra192E-ts1080-2018-05-11.ts`, `astra192E-ts1120-2018-05-11.ts`)
  * `Astra_19.2E_Spain/` (`astra-10847V-2020-08-24.ts`)
  * `DVBS2_toolkit/` (`sample.ts`)
* **Purpose:** Real-world and toolkit-generated MPEG Transport Stream (MPEG-TS) captures across different satellite transponders for stream health metrics, PID distribution analysis, continuity counter checking, and multiplex analysis.
* **Source/Details:** Satellite broadcast captures (Astra 19.2°E) and DVB-S2 toolkit sample data. Further technical properties: *Source/details to be documented.*

### 4. `04_RFI_AI/`
* **Files:**
  * `Modulation Recognition.zip`
  * `RFI classification.zip`
* **Purpose:** Reference dataset archives supporting AI/ML exploration for signal interference (RFI) classification, anomaly detection, and modulation pattern recognition.
* **Source/Details:** *Source/details to be documented.*

### 5. `05_REAL_DVB_S2/`
* **Subfolder & Files:**
  * `GRCon22_Blockstream/` (`blockstream.ts`, `ip_packets.pcap`)
* **Purpose:** Real-world over-the-air DVB-S2 satellite broadcast capture containing simultaneous Transport Stream (`.ts`) data and encapsulated IP traffic (`.pcap`) for end-to-end multi-format stream analysis.
* **Source/Details:** GRCon22 Blockstream Satellite CTF capture (`daniestevez/grcon22-ctf`). Further technical properties: *Source/details to be documented.*

---

## Data Usage Rules
1. **Preservation:** Raw data files must remain unmodified in their respective directories.
2. **Preprocessing:** Cleaned, parsed, or transformed data will be written into `02_PROCESSED_DATA/` and `03_FEATURE_DATA/` during later project phases.
3. **Repository Cleanliness:** Raw data files must remain local and must not be pushed to GitHub.
