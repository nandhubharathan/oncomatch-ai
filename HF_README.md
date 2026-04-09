---
title: OncoMatch-AI Professional
emoji: 🧬
colorFrom: indigo
colorTo: purple
sdk: streamlit
sdk_version: "1.32.0"
app_file: app.py
pinned: true
license: mit
short_description: >
  AI-powered oncology drug intelligence platform — maps any cancer type to
  recommended drugs with 2D/3D structural analysis and pharmacist-grade
  clinical dossiers (PK, BBW, DDI, Lipinski RO5).
tags:
  - medicine
  - chemistry
  - drug-discovery
  - oncology
  - bioinformatics
  - rdkit
  - cheminformatics
  - streamlit
  - pharmacology
---

# 🧬 OncoMatch-AI Professional

> **Precision Oncology Drug Intelligence Platform**  
> An AI system that maps any known cancer type to recommended drugs, providing a
> complete 2D/3D structural and pharmacist-grade clinical pharmacological dossier.

[![Python 3.10](https://img.shields.io/badge/Python-3.10-3776AB?logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![RDKit](https://img.shields.io/badge/RDKit-2022.9+-4CAF50)](https://rdkit.org)
[![License MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![Spaces](https://img.shields.io/badge/HuggingFace-Spaces-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/spaces)

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🎯 **1,500+ Mappings** | 100+ molecularly-defined cancer subtypes mapped to clinical drugs |
| 🔬 **Interactive 3D Viewer** | RDKit ETKDG 3D conformation + py3Dmol WebGL rotation/zoom |
| ⚕️ **Pharmacist's Dossier** | FDA Status, Mechanism of Action, PK/ADME, BBW, DDI |
| 🧪 **Lipinski RO5 Calculator** | Real-time drug-likeness scoring (MW, LogP, HBD, HBA, TPSA) |
| 💊 **24 Drug Mechanism Classes** | TKIs, PARP, CDK4/6, ICI, Platinum, Taxanes, BCL-2, KRAS... |
| ⬛ **Black Box Warnings** | FDA BBW alerts with structured safety profiles |
| ⚡ **Drug–Drug Interactions** | CYP-mediated DDI alerts per drug |
| 📊 **Analytics Dashboard** | Efficacy distributions, drug class breakdown, downloadable DB |

---

## 🚀 How to Use

1. **Select a Cancer Type** from the sidebar dropdown (100+ subtypes available)  
2. View **AI-ranked drug recommendations** with efficacy scores  
3. Expand any drug card to see the full **Clinical Dossier**  
4. Interact with the **3D molecular structure** — rotate, zoom, change style  
5. Switch to **Drug Explorer** tab for individual drug deep-dives  
6. Visit **Analytics Dashboard** for database-wide insights  

---

## 🧬 Under the Hood

### Conformational Search (3D Structure Generation)
The 3D structure is not just a drawing — it uses **RDKit's ETKDG v3 algorithm**
(Experimental Torsion Knowledge Distance Geometry) to generate the most likely
low-energy 3D conformation, followed by **MMFF94 force-field optimization** to
find the global energy minimum. This mimics how the drug physically exists in
solution before binding its target.

### Molecular Fingerprinting
The AI models use **Morgan Fingerprints (ECFP4)** — circular fingerprints with
radius 2 that encode the chemical environment of every atom out to 4 bonds. This
allows the system to compare molecular similarities and generalize drug activity
predictions beyond the training set.

### Bioavailability — ADME Bridge
The **Pharmacist's Dossier** focuses on ADME properties — the bridge between
chemistry and clinical medicine:
- **Absorption**: Route of admin + t½ inform dosing schedules  
- **Distribution**: Plasma Protein Binding (PPB%) predicts free drug levels  
- **Metabolism**: CYP enzyme interactions guide DDI prediction  
- **Excretion**: t½ informs renal/hepatic dose adjustments  

---

## 🛠️ Technical Stack

```
Frontend:    Streamlit 1.32+
Chemistry:   RDKit 2022.9+ (2D/3D, Lipinski, ECFP4)
3D Viewer:   py3Dmol 2.0+ + stmol (WebGL)
ML/Data:     scikit-learn, pandas, numpy
Deployment:  Hugging Face Spaces (Streamlit SDK)
```

---

## ⚕️ Clinical Disclaimer

> **For educational and research purposes only.**  
> All drug recommendations must be verified by a licensed oncologist or clinical pharmacist.  
> Not intended for clinical decision-making or direct patient care.

---

*Built with ❤️ for Oncology Research & Clinical Pharmacy Education*
