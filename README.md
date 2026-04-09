---
title: OncoMatch-AI Professional
emoji: 🧬
colorFrom: indigo
colorTo: purple
sdk: docker
pinned: true
license: mit
---

# 🧬 OncoMatch-AI Professional

> **Precision Oncology Drug Intelligence Platform** — AI-powered cancer-to-drug mapping with complete pharmacological dossiers.

[![Python 3.10](https://img.shields.io/badge/Python-3.10-blue)](https://python.org) 
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red)](https://streamlit.io) 
[![RDKit](https://img.shields.io/badge/RDKit-2022.9+-green)](https://rdkit.org) 
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 🚀 Features

| Feature | Description |
|---|---|
| 🎯 **1,500+ Cancer-Drug Mappings** | 100+ molecularly-defined cancer subtypes mapped to clinical drugs |
| 🔬 **3D Molecular Viewer** | RDKit ETKDG 3D conformation + py3Dmol WebGL interactive rotation |
| ⚕️ **Pharmacist's Clinical Dossier** | FDA Status, Mechanism of Action, PK/ADME, BBW, DDI |
| 🧪 **Lipinski RO5 Calculator** | Real-time drug-likeness scoring via RDKit |
| 💊 **50+ Drug Classes** | TKIs, PARP, CDK4/6, ICI, Platinum, Taxanes, BCL-2, KRAS, and more |
| 🏥 **Safety Profile** | Black Box Warnings + CYP-mediated Drug-Drug Interactions |
| 📊 **Analytics Dashboard** | Efficacy distributions, drug class breakdown, downloadable database |

---

## 🗂️ Project Structure

```
PHASE 4/
├── AUTORUN.py              # 🤖 Master autonomous launcher (run this first!)
├── app.py                  # 🌐 Streamlit web application
├── data_generator.py       # 🔬 Synthetic 1500+ dataset generator
├── requirements.txt        # 📦 Python dependencies
├── Dockerfile              # 🐳 Container for Hugging Face / Docker deployment
├── README.md               # 📖 This file
└── .streamlit/
    └── config.toml         # ⚙️ Streamlit dark theme configuration
```

---

## ⚡ Quick Start (Local)

### Option 1: One-Click AUTORUN (Recommended)
```bash
python AUTORUN.py
```
This single command will:
1. ✅ Check Python version
2. 📦 Auto-install all dependencies  
3. 🔬 Generate the 1,500+ cancer-drug dataset
4. 🐳 Create Dockerfile + requirements.txt
5. 🚀 Launch the app at `http://localhost:8501`

### Option 2: Manual Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Generate dataset
python data_generator.py

# Run app
streamlit run app.py
```

---

## 🐳 Docker Deployment

```bash
# Build image
docker build -t oncomatc-ai .

# Run container
docker run -p 7860:7860 oncomatc-ai
```

---

## ☁️ Cloud Deployment

### Streamlit Community Cloud
1. Push this repository to GitHub
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo → select `app.py` → Deploy!

### Hugging Face Spaces
1. Create a new Space (Docker SDK)
2. Push all files to the Space repository
3. The `Dockerfile` handles everything automatically

---

## 🧬 Drug Database Coverage

| Drug Class | Examples | Count |
|---|---|---|
| Tyrosine Kinase Inhibitors (TKI) | Osimertinib, Ibrutinib, Crizotinib | 20+ |
| Immune Checkpoint Inhibitors (ICI) | Pembrolizumab, Nivolumab, Atezolizumab | 6 |
| PARP Inhibitors | Olaparib, Niraparib, Rucaparib | 3 |
| CDK4/6 Inhibitors | Palbociclib, Ribociclib, Abemaciclib | 3 |
| BRAF/MEK Inhibitors | Vemurafenib, Dabrafenib, Trametinib | 3 |
| Platinum Compounds | Cisplatin, Carboplatin, Oxaliplatin | 3 |
| Monoclonal Antibodies | Trastuzumab, Bevacizumab | 2 |
| Novel Targeted (KRAS, BCL-2, RET...) | Sotorasib, Venetoclax, Selpercatinib | 10+ |
| Hormonal Agents | Enzalutamide, Abiraterone, Tamoxifen | 4 |
| Antimetabolites / Cytotoxics | 5-FU, Gemcitabine, Paclitaxel | 10+ |

---

## ⚕️ Clinical Disclaimer

> **This platform is for educational and research purposes only.**  
> All drug recommendations must be verified by a licensed oncologist.  
> Not intended for clinical decision-making or patient care.

---

## 🛠️ Technology Stack

- **Cheminformatics**: [RDKit](https://rdkit.org) — 2D/3D conformation, Lipinski calculations
- **3D Visualization**: [py3Dmol](https://3dmol.org) — WebGL molecular viewer
- **Web Framework**: [Streamlit](https://streamlit.io)
- **ML/Data**: [scikit-learn](https://scikit-learn.org), [pandas](https://pandas.pydata.org)
- **Deployment**: Docker, Streamlit Cloud, Hugging Face Spaces

---

*Built with ❤️ for Oncology Research & Clinical Pharmacy*
