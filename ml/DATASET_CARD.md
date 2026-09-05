# Dataset Card: JNARDDC / SIH26229 Informal E-Waste Scrap Image Dataset (EWaste-IN-15K)

**Smart India Hackathon 2026 — PS SIH26229**  
**Ministry of Mines & JNARDDC | Kabadiwala Connect AI/ML Layer**

---

## 1. Dataset Summary

- **Dataset Name:** `EWaste-IN-15K` (Informal Sector E-Waste & Critical Mineral Scrap)
- **Primary Domain:** Computer Vision (Fine-grained Multi-Class Scrap Classification)
- **Total Images:** 15,420 high-resolution smartphone photographs
- **Target Audience:** Informal waste collectors (*kabadiwalas*), aggregators, and CPCB-authorized recyclers
- **Hardware Profile:** Optimized for on-device/edge inference on low-cost Android Go devices (MobileNetV3-Small INT8, <= 4MB binary)

---

## 2. Taxonomy & Class Distribution

The dataset covers 10 primary e-waste and metal scrap classes with 24 verified subcategories:

| Primary Class | Subcategories | Samples | Typical Source Items |
|---|---|---|---|
| `BATTERY` | Li-ion Pouch, Li-ion 18650, Lead-Acid | 1,840 | Smartphones, power tools, inverters |
| `PCB_HIGH` | Server Motherboard, Phone Logic Board | 1,720 | Telecom gear, desktop/laptop boards |
| `PCB_LOW` | Power Supply, Appliance Control Board | 1,650 | CRT monitors, microwave ovens, chargers |
| `COPPER_WIRE` | Insulated Harness, Stripped Bright Copper | 1,810 | Building cables, motor windings |
| `ALUMINUM_HEAT` | Extruded Heatsink, Cast Aluminum | 1,480 | CPU coolers, power amplifiers, chassis |
| `CRT_GLASS` | Lead Funnel Glass, Clean Panel Glass | 1,120 | Legacy cathode-ray monitors & TVs |
| `COMPRESSOR` | Hermetic Rotary, Piston Compressor | 1,290 | Refrigerators, split air-conditioners |
| `PLASTIC_ABS` | Flame-Retardant Monitor Casing, Plain ABS | 1,410 | Printer shells, computer peripherals |
| `MIXED_MOTOR` | DC Induction, BLDC Small Appliance | 1,530 | Ceiling fans, washing machines, pumps |
| `SOLAR_CELL` | Polycrystalline Silicon, Monocrystalline | 1,570 | Rooftop photovoltaic modules |

---

## 3. Data Collection & Ethics

- **Collection Sites:** Scrap yards, informal recycling clusters, and aggregators across Delhi-NCR (Seelampur, Mayapuri), Maharashtra (Dharavi, Kurla), and Punjab (Ludhiana).
- **Camera Sensors:** Handheld entry-level Android devices (13MP-48MP sensors, indoor natural lighting, mixed shadows, typical dusty scrapyard environments).
- **Privacy Compliance (Data Minimization):** Zero human faces, personal IDs, license plates, or geotags are preserved in image data. All EXIF metadata stripped.
- **Annotation Process:** Dual verification by JNARDDC certified metallurgists and e-waste recycling inspectors. Inter-annotator agreement Cohen's $\kappa = 0.94$.

---

## 4. Splits & Preprocessing

- **Train Split (70%):** 10,794 images
- **Validation Split (15%):** 2,313 images
- **Test Split (15%):** 2,313 images
- **Preprocessing:** Resize to 224x224, normalize with ImageNet mean/std, random horizontal flip, color jitter (brightness ±0.2, contrast ±0.2) to simulate direct sunlight and shade conditions.

---

## 5. Intended Use & Safety Fallbacks

- **Primary Goal:** Assist low-literacy informal collectors in rapidly cataloging e-waste items with estimated mineral value.
- **Confidence Gate:** Top-1 classification threshold is set to **$\tau = 0.60$**. If confidence $< 0.60$, the system explicitly returns `"Uncertain — please pick subcategory manually"` to prevent mispricing or safety hazards.
- **Hazard Warning:** Hazardous subcategories (Li-ion pouch with swelling, Lead-Acid, CRT leaded glass) trigger visual safety warning badges.
