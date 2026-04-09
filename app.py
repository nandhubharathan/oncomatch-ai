"""
OncoMatch-AI Professional — Streamlit Application
Full-featured cancer-drug recommendation engine with 3D molecular visualization
and pharmacist-grade clinical dossiers.
"""

import streamlit as st
import pandas as pd
import math
import json
import os
import sys
import io
import base64
import time

# ─── Page configuration (must be first Streamlit call) ──────────────────────
st.set_page_config(
    page_title="OncoMatch-AI Professional | Oncology Drug Intelligence",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://www.cancer.gov/",
        "About": "## OncoMatch-AI Professional\nAI-powered oncology drug matching platform.",
    },
)

# ─── Dependency guard ──────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_rdkit():
    try:
        from rdkit import Chem
        from rdkit.Chem import Descriptors, AllChem, Draw
        from rdkit.Chem.rdMolDescriptors import CalcTPSA
        return True
    except ImportError:
        return False

@st.cache_resource(show_spinner=False)
def load_py3dmol():
    try:
        import py3Dmol
        import stmol
        return True
    except ImportError:
        try:
            import py3Dmol
            return "py3dmol_only"
        except ImportError:
            return False

RDKIT_OK = load_rdkit()
PY3DMOL_OK = load_py3dmol()

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

    :root {
        --bg-primary: #0a0e1a;
        --bg-secondary: #111827;
        --bg-card: #1a2035;
        --bg-card-hover: #1f2847;
        --accent-blue: #3b82f6;
        --accent-cyan: #06b6d4;
        --accent-purple: #8b5cf6;
        --accent-green: #10b981;
        --accent-orange: #f59e0b;
        --accent-red: #ef4444;
        --accent-pink: #ec4899;
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;
        --border: #1e293b;
        --border-accent: #334155;
        --gradient-1: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --gradient-2: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    }

    html, body, .stApp {
        background: var(--bg-primary) !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* Header hero */
    .hero-header {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 20px;
        padding: 2.5rem;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    .hero-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle at center, rgba(139, 92, 246, 0.08) 0%, transparent 60%);
        animation: pulse-bg 4s ease-in-out infinite;
    }
    @keyframes pulse-bg {
        0%, 100% { opacity: 0.5; transform: scale(1); }
        50% { opacity: 1; transform: scale(1.05); }
    }
    .hero-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #60a5fa, #a78bfa, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        line-height: 1.1;
    }
    .hero-subtitle {
        color: var(--text-secondary);
        font-size: 1.1rem;
        margin-top: 0.5rem;
        font-weight: 400;
    }
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.4);
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.78rem;
        color: #34d399;
        font-weight: 600;
        margin-right: 8px;
        margin-top: 12px;
    }

    /* Stat cards */
    .stat-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin-bottom: 2rem;
    }
    .stat-card {
        background: var(--bg-card);
        border: 1px solid var(--border-accent);
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    .stat-card:hover {
        border-color: var(--accent-blue);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.15);
    }
    .stat-number {
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .stat-label { color: var(--text-secondary); font-size: 0.82rem; margin-top: 4px; }

    /* Drug result card */
    .drug-result-card {
        background: linear-gradient(135deg, #1a2035, #1e2a45);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 16px;
        padding: 1.8rem;
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    .drug-result-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6, #06b6d4);
    }
    .rank-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 36px;
        height: 36px;
        border-radius: 50%;
        font-weight: 800;
        font-size: 1rem;
        margin-right: 12px;
    }
    .rank-1 { background: linear-gradient(135deg, #f59e0b, #d97706); color: #000; }
    .rank-2 { background: linear-gradient(135deg, #94a3b8, #64748b); color: #000; }
    .rank-3 { background: linear-gradient(135deg, #b45309, #92400e); color: #fff; }
    .rank-other { background: rgba(59, 130, 246, 0.2); color: #60a5fa; border: 1px solid #3b82f6; }

    /* Section headers */
    .section-header {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 1.3rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid var(--border-accent);
    }
    .section-icon {
        width: 32px;
        height: 32px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
    }

    /* Clinical dossier fields */
    .dossier-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.8rem;
    }
    .dossier-field {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid var(--border-accent);
        border-radius: 10px;
        padding: 0.9rem;
    }
    .dossier-label {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--text-muted);
        margin-bottom: 4px;
    }
    .dossier-value {
        font-size: 0.92rem;
        color: var(--text-primary);
        font-weight: 500;
        line-height: 1.4;
    }
    .dossier-full {
        grid-column: 1 / -1;
    }

    /* Warning/BBW box */
    .bbw-box {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.4);
        border-left: 4px solid #ef4444;
        border-radius: 8px;
        padding: 0.9rem;
        margin-top: 0.5rem;
    }
    .bbw-label {
        font-size: 0.72rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #ef4444;
        margin-bottom: 4px;
    }
    .bbw-text { font-size: 0.88rem; color: #fca5a5; }

    /* DDI box */
    .ddi-box {
        background: rgba(245, 158, 11, 0.1);
        border: 1px solid rgba(245, 158, 11, 0.4);
        border-left: 4px solid #f59e0b;
        border-radius: 8px;
        padding: 0.9rem;
        margin-top: 0.5rem;
    }
    .ddi-label {
        font-size: 0.72rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #f59e0b;
        margin-bottom: 4px;
    }
    .ddi-text { font-size: 0.88rem; color: #fde68a; }

    /* PK metrics row */
    .pk-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.8rem;
        margin-top: 0.8rem;
    }
    .pk-metric {
        background: rgba(6, 182, 212, 0.08);
        border: 1px solid rgba(6, 182, 212, 0.25);
        border-radius: 10px;
        padding: 0.9rem;
        text-align: center;
    }
    .pk-value {
        font-size: 1.4rem;
        font-weight: 800;
        color: #06b6d4;
        font-family: 'JetBrains Mono', monospace;
    }
    .pk-unit { font-size: 0.7rem; color: var(--text-muted); font-weight: 600; display: block; }
    .pk-name { font-size: 0.75rem; color: var(--text-secondary); margin-top: 4px; }

    /* Lipinski card */
    .lipinski-pass { color: #10b981; font-weight: 700; }
    .lipinski-fail { color: #ef4444; font-weight: 700; }
    .lipinski-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 6px;
        margin-top: 8px;
    }
    .lipinski-rule {
        background: rgba(15, 23, 42, 0.8);
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 0.8rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* Efficacy bar */
    .efficacy-bar-bg {
        background: rgba(15, 23, 42, 0.8);
        border-radius: 10px;
        height: 10px;
        width: 100%;
        overflow: hidden;
        margin-top: 8px;
    }
    .efficacy-bar-fill {
        height: 100%;
        border-radius: 10px;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6, #06b6d4);
        transition: width 1s ease;
    }

    /* Sidebar */
    .css-1d391kg, [data-testid="stSidebar"] {
        background: #0d1422 !important;
        border-right: 1px solid var(--border-accent) !important;
    }

    /* Molecule viewer frame */
    .mol-viewer-frame {
        background: #050a14;
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 12px;
        overflow: hidden;
        aspect-ratio: 1/1;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* Route badge */
    .route-badge-oral {
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.4);
        color: #34d399;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .route-badge-iv {
        background: rgba(139, 92, 246, 0.15);
        border: 1px solid rgba(139, 92, 246, 0.4);
        color: #a78bfa;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .route-badge-subq {
        background: rgba(245, 158, 11, 0.15);
        border: 1px solid rgba(245, 158, 11, 0.4);
        color: #fbbf24;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
    }

    /* FDA status badges */
    .fda-approved { color: #10b981; font-weight: 700; }
    .fda-withdrawn { color: #ef4444; font-weight: 700; }
    .fda-investigational { color: #f59e0b; font-weight: 700; }

    /* Search bar */
    .stSelectbox > div > div,
    .stTextInput > div > div > input {
        background: var(--bg-card) !important;
        border-color: var(--border-accent) !important;
        color: var(--text-primary) !important;
        border-radius: 10px !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, #3b82f6, #8b5cf6) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        padding: 0.6rem 2rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 8px 25px rgba(139, 92, 246, 0.4) !important;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: var(--text-secondary) !important;
        border-bottom: 2px solid transparent !important;
        font-weight: 600 !important;
    }
    .stTabs [aria-selected="true"] {
        color: #60a5fa !important;
        border-bottom-color: #3b82f6 !important;
    }

    /* Footer */
    .footer {
        margin-top: 3rem;
        padding: 1.5rem;
        border-top: 1px solid var(--border-accent);
        text-align: center;
        color: var(--text-muted);
        font-size: 0.82rem;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg-primary); }
    ::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }

   /* Hide streamlit branding while keeping UI controls functional */
    #MainMenu { visibility: hidden; } 
    footer { visibility: hidden; }    
    
    /* Removed the lines that were hiding the header/toolbar */
    header { background: rgba(0,0,0,0) !important; } 

</style>
""", unsafe_allow_html=True)


# ─── Utility Functions ────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_data():
    """Load the drug database CSV."""
    csv_path = os.path.join(os.path.dirname(__file__), "oncomatc_drug_database.csv")
    if not os.path.exists(csv_path):
        from data_generator import generate_dataset
        return generate_dataset(csv_path)
    return pd.read_csv(csv_path)


def calculate_lipinski(smiles: str):
    """Calculate Lipinski Rule of 5 parameters using RDKit."""
    if not RDKIT_OK:
        return None
    try:
        from rdkit import Chem
        from rdkit.Chem import Descriptors
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None
        mw = Descriptors.ExactMolWt(mol)
        logp = Descriptors.MolLogP(mol)
        hbd = Descriptors.NumHDonors(mol)
        hba = Descriptors.NumHAcceptors(mol)
        tpsa = Descriptors.TPSA(mol)
        rot_bonds = Descriptors.NumRotatableBonds(mol)
        violations = sum([
            mw > 500,
            logp > 5,
            hbd > 5,
            hba > 10,
        ])
        return {
            "MW": round(mw, 1),
            "LogP": round(logp, 2),
            "HBD": hbd,
            "HBA": hba,
            "TPSA": round(tpsa, 1),
            "RotBonds": rot_bonds,
            "Violations": violations,
            "RO5_Pass": violations <= 1,
        }
    except Exception:
        return None


def smiles_to_2d_image(smiles: str, width=400, height=300):
    """Convert SMILES to 2D molecule PNG (base64)."""
    if not RDKIT_OK:
        return None
    try:
        from rdkit import Chem
        from rdkit.Chem import Draw, AllChem
        from rdkit.Chem.Draw import rdMolDraw2D
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None
        AllChem.Compute2DCoords(mol)
        drawer = rdMolDraw2D.MolDraw2DSVG(width, height)
        drawer.drawOptions().addStereoAnnotation = True
        drawer.drawOptions().clearBackground = False
        drawer.DrawMolecule(mol)
        drawer.FinishDrawing()
        svg = drawer.GetDrawingText()
        b64 = base64.b64encode(svg.encode()).decode()
        return f"data:image/svg+xml;base64,{b64}"
    except Exception:
        return None


def generate_3d_mol_block(smiles: str):
    """Generate 3D mol block from SMILES using ETKDG."""
    if not RDKIT_OK:
        return None
    try:
        from rdkit import Chem
        from rdkit.Chem import AllChem
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None
        mol = Chem.AddHs(mol)
        params = AllChem.ETKDGv3()
        params.randomSeed = 42
        if AllChem.EmbedMolecule(mol, params) == -1:
            AllChem.EmbedMolecule(mol, AllChem.ETKDG())
        AllChem.MMFFOptimizeMolecule(mol, maxIters=2000)
        mol = Chem.RemoveHs(mol)
        return Chem.MolToMolBlock(mol)
    except Exception:
        return None


def render_3d_viewer(mol_block: str, style: str = "stick", bg_color: str = "#050a14"):
    """Render interactive 3D molecular viewer using py3Dmol."""
    if not mol_block:
        return None
    try:
        import py3Dmol
        view = py3Dmol.view(width=420, height=380)
        view.addModel(mol_block, "mol")
        style_map = {
            "stick": {"stick": {"colorscheme": "jmolColors", "radius": 0.15}},
            "ball_stick": {"stick": {"radius": 0.1}, "sphere": {"radius": 0.35, "colorscheme": "jmolColors"}},
            "surface": {"surface": {"opacity": 0.75, "colorscheme": "whiteCarbon"}},
            "cartoon": {"cartoon": {"colorscheme": "ssJmol"}},
        }
        view.setStyle(style_map.get(style, style_map["stick"]))
        view.setBackgroundColor(bg_color)
        view.zoomTo()
        view.spin(True)
        return view
    except Exception:
        return None


def render_3d_viewer_html(mol_block: str, style: str = "stick"):
    """Renders 3D viewer as raw HTML for st.components.v1.html."""
    if not mol_block:
        return None
    try:
        import py3Dmol
        view = py3Dmol.view(width=420, height=380)
        view.addModel(mol_block, "mol")
        style_map = {
            "stick": {"stick": {"colorscheme": "jmolColors", "radius": 0.15}},
            "ball_stick": {"stick": {"radius": 0.1}, "sphere": {"radius": 0.35, "colorscheme": "jmolColors"}},
            "surface": {"surface": {"opacity": 0.75, "colorscheme": "whiteCarbon"}},
        }
        view.setStyle(style_map.get(style, style_map["stick"]))
        view.setBackgroundColor("#050a14")
        view.zoomTo()
        view.spin(True)
        return view._make_html()
    except Exception:
        return None


def get_route_badge(route: str) -> str:
    """Return styled HTML badge for route of administration."""
    rl = route.lower()
    if "oral" in rl:
        cls = "route-badge-oral"
        icon = "💊"
    elif "iv" in rl or "infusion" in rl:
        cls = "route-badge-iv"
        icon = "💉"
    elif "subcutaneous" in rl or "subq" in rl:
        cls = "route-badge-subq"
        icon = "🩺"
    else:
        cls = "route-badge-subq"
        icon = "🔬"
    return f'<span class="{cls}">{icon} {route}</span>'


def get_fda_badge(status: str) -> str:
    """Return styled FDA status text."""
    sl = status.lower()
    if "approved" in sl:
        return f'<span class="fda-approved">✅ {status}</span>'
    elif "withdrawn" in sl:
        return f'<span class="fda-withdrawn">🚫 {status}</span>'
    else:
        return f'<span class="fda-investigational">🔬 {status}</span>'


def rank_drugs_for_cancer(df: pd.DataFrame, cancer_type: str, top_n: int = 8) -> pd.DataFrame:
    """Filter and rank drugs for a given cancer type."""
    # Exact match first
    exact = df[df["Cancer_Type"].str.strip() == cancer_type.strip()]
    if len(exact) == 0:
        # Fuzzy match
        cancer_lower = cancer_type.lower()
        exact = df[df["Cancer_Type"].str.lower().str.contains(
            "|".join([w for w in cancer_lower.split() if len(w) > 3]), na=False
        )]
    if len(exact) == 0:
        return pd.DataFrame()
    result = exact.sort_values("Efficacy_Score", ascending=False)
    result = result.drop_duplicates(subset=["Drug_Name"]).head(top_n)
    return result.reset_index(drop=True)


# ─── Main App ─────────────────────────────────────────────────────────────────
def main():
    # Load data
    with st.spinner("🔬 Loading OncoMatch-AI database..."):
        df = load_data()
    
    cancer_types = sorted(df["Cancer_Type"].unique().tolist())
    unique_drugs = df["Drug_Name"].nunique()
    unique_cancers = df["Cancer_Type"].nunique()
    drug_classes = df["Target_Protein_Class"].nunique()

    # ── Hero Header ──────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="hero-header">
        <h1 class="hero-title">🧬 OncoMatch-AI<span style="color:#60a5fa"> Professional</span></h1>
        <p class="hero-subtitle">Precision Oncology Drug Intelligence Platform &nbsp;|&nbsp; 
        Clinical-Grade Pharmacological Dossiers &nbsp;|&nbsp; 
        3D Structural Analysis</p>
        <div style="margin-top:12px;">
            <span class="hero-badge">✅ FDA Data Integrated</span>
            <span class="hero-badge">🧪 3D RDKit Engine</span>
            <span class="hero-badge">💊 {unique_drugs} Drugs</span>
            <span class="hero-badge">🎯 {unique_cancers} Cancer Types</span>
            <span class="hero-badge">⚠️ BBW & DDI Alerts</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Stats Row ─────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="stat-grid">
        <div class="stat-card">
            <div class="stat-number">{len(df):,}</div>
            <div class="stat-label">Cancer-Drug Mappings</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{unique_drugs}</div>
            <div class="stat-label">Unique Oncology Drugs</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{unique_cancers}</div>
            <div class="stat-label">Cancer Sub-Types</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{drug_classes}</div>
            <div class="stat-label">Drug Mechanism Classes</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Sidebar Configuration ─────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;padding:1rem 0;">
            <div style="font-size:2.5rem;">🧬</div>
            <div style="font-weight:800;font-size:1.1rem;color:#60a5fa;">OncoMatch-AI</div>
            <div style="font-size:0.78rem;color:#64748b;">Professional Edition</div>
        </div>
        <hr style="border-color:#1e293b;margin:0.5rem 0;">
        """, unsafe_allow_html=True)

        st.markdown("### 🎯 Cancer Type Search")
        selected_cancer = st.selectbox(
            "Select Cancer Type",
            options=["— Choose Cancer Type —"] + cancer_types,
            key="cancer_select",
            help="Select from 100+ molecularly-defined cancer subtypes",
        )

        st.markdown("### 🔬 Molecular Viewer Style")
        mol_style = st.radio(
            "3D Visualization Style",
            options=["stick", "ball_stick", "surface"],
            format_func=lambda x: {"stick": "🦷 Stick", "ball_stick": "⚽ Ball & Stick", "surface": "🫧 Molecular Surface"}[x],
            key="mol_style",
        )

        st.markdown("### 📊 Results Configuration")
        top_n = st.slider("Number of Top Drugs to Show", min_value=3, max_value=10, value=5, key="top_n")

        st.markdown("### 🔍 Drug Explorer")
        drug_search = st.text_input("Search Drug by Name", placeholder="e.g. Osimertinib", key="drug_search")

        st.markdown("""
        <hr style="border-color:#1e293b;margin:1rem 0;">
        <div style="background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.3);border-radius:10px;padding:0.8rem;">
            <div style="font-size:0.75rem;font-weight:700;color:#34d399;margin-bottom:6px;">⚕️ CLINICAL DISCLAIMER</div>
            <div style="font-size:0.7rem;color:#64748b;line-height:1.5;">
            This tool is for <strong>educational/research purposes only</strong>. 
            All drug recommendations must be verified by a licensed oncologist. 
            Not for clinical decision-making.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if not RDKIT_OK:
            st.warning("⚠️ RDKit not detected. 3D visualization unavailable.")
        if not PY3DMOL_OK:
            st.warning("⚠️ py3Dmol not detected. Interactive 3D viewer unavailable.")

    # ── Main Content Tabs ──────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["🎯 Drug Recommendations", "🔬 Drug Explorer", "📊 Analytics Dashboard"])

    # ════════════════════════════════════════════════════════════════════════
    # TAB 1 — DRUG RECOMMENDATIONS
    # ════════════════════════════════════════════════════════════════════════
    with tab1:
        if selected_cancer == "— Choose Cancer Type —":
            st.markdown("""
            <div style="text-align:center;padding:4rem 2rem;background:rgba(15,23,42,0.5);border:1px dashed #334155;border-radius:16px;">
                <div style="font-size:4rem;margin-bottom:1rem;">🎯</div>
                <h3 style="color:#94a3b8;font-weight:600;">Select a Cancer Type</h3>
                <p style="color:#64748b;max-width:500px;margin:0.5rem auto;">
                    Choose from 100+ molecularly-defined cancer subtypes in the sidebar to receive 
                    AI-ranked drug recommendations with complete clinical dossiers and 3D structural analysis.
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            with st.spinner(f"🔍 Matching drugs for **{selected_cancer}**..."):
                results = rank_drugs_for_cancer(df, selected_cancer, top_n)

            if len(results) == 0:
                st.error(f"No drug data found for **{selected_cancer}**. Try a related cancer subtype.")
            else:
                st.markdown(f"""
                <div class="section-header">
                    <div class="section-icon" style="background:rgba(59,130,246,0.2);">🎯</div>
                    Top {len(results)} Recommended Drugs for <span style="color:#60a5fa">&nbsp;{selected_cancer}</span>
                </div>
                """, unsafe_allow_html=True)

                for i, (_, row) in enumerate(results.iterrows()):
                    rank = i + 1
                    rank_class = {1: "rank-1", 2: "rank-2", 3: "rank-3"}.get(rank, "rank-other")
                    rank_emoji = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, f"#{rank}")
                    efficacy_pct = int(row["Efficacy_Score"] * 100)

                    # Calculate Lipinski
                    lip = calculate_lipinski(str(row.get("SMILES", "")))

                    # Generate 2D image
                    img_data = smiles_to_2d_image(str(row.get("SMILES", "")), width=350, height=260)

                    with st.expander(
                        f"{rank_emoji} #{rank} — {row['Drug_Name']} ({row.get('Brand_Name','N/A')}) | Efficacy: {efficacy_pct}%",
                        expanded=(rank <= 2)
                    ):
                        # Top row: rank badge + drug name + efficacy bar
                        st.markdown(f"""
                        <div class="drug-result-card">
                            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:1rem;">
                                <div style="display:flex;align-items:center;">
                                    <span class="rank-badge {rank_class}">{rank}</span>
                                    <div>
                                        <span style="font-size:1.4rem;font-weight:800;">{row['Drug_Name']}</span>
                                        <span style="color:#64748b;font-size:1rem;margin-left:8px;">({row.get('Brand_Name','N/A')})</span>
                                    </div>
                                </div>
                                <div style="text-align:right;">
                                    {get_route_badge(str(row.get('Route_of_Administration','N/A')))}
                                </div>
                            </div>
                            <div style="display:flex;align-items:center;gap:12px;margin-bottom:4px;">
                                <span style="color:#94a3b8;font-size:0.85rem;">Efficacy Score</span>
                                <span style="color:#60a5fa;font-weight:700;font-size:1.1rem;">{efficacy_pct}%</span>
                            </div>
                            <div class="efficacy-bar-bg">
                                <div class="efficacy-bar-fill" style="width:{efficacy_pct}%;"></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        # ── Two-column layout: Mol Viz | Clinical Dossier ────
                        mol_col, dossier_col = st.columns([1, 1.6])

                        with mol_col:
                            st.markdown("""
                            <div class="section-header" style="font-size:1rem;">
                                <div class="section-icon" style="background:rgba(6,182,212,0.2);">🔬</div>
                                Molecular Structure
                            </div>
                            """, unsafe_allow_html=True)

                            smiles = str(row.get("SMILES", ""))
                            
                            # 2D structure
                            if img_data and RDKIT_OK:
                                st.markdown(f'<div style="background:#0a0e1a;border:1px solid #1e293b;border-radius:10px;padding:8px;text-align:center;"><img src="{img_data}" style="max-width:100%;border-radius:6px;"></div>', unsafe_allow_html=True)
                            else:
                                st.code(smiles, language=None)

                            # 3D viewer
                            st.markdown("**Interactive 3D Conformation** (ETKDG)")
                            if RDKIT_OK and smiles:
                                mol_block = generate_3d_mol_block(smiles)
                                if mol_block:
                                    if PY3DMOL_OK:
                                        html_3d = render_3d_viewer_html(mol_block, style=mol_style)
                                        if html_3d:
                                            import streamlit.components.v1 as components
                                            components.html(
                                                f'<div style="background:#050a14;border-radius:10px;overflow:hidden;">{html_3d}</div>',
                                                height=400,
                                            )
                                        else:
                                            st.info("3D viewer unavailable for this molecule.")
                                    else:
                                        st.info("💡 Install `py3Dmol` for interactive 3D rotation.")
                                        st.code(smiles, language=None)
                                else:
                                    st.info("3D conformation could not be generated for this SMILES.")
                            else:
                                st.info("RDKit required for 3D visualization.")

                            # SMILES string
                            with st.expander("📋 SMILES String"):
                                st.code(smiles, language=None)

                        with dossier_col:
                            st.markdown("""
                            <div class="section-header" style="font-size:1rem;">
                                <div class="section-icon" style="background:rgba(16,185,129,0.2);">⚕️</div>
                                Pharmacist's Clinical Dossier
                            </div>
                            """, unsafe_allow_html=True)

                            # Core fields
                            st.markdown(f"""
                            <div class="dossier-grid">
                                <div class="dossier-field">
                                    <div class="dossier-label">🏛️ FDA Status</div>
                                    <div class="dossier-value">{get_fda_badge(str(row.get('FDA_Status','N/A')))}</div>
                                </div>
                                <div class="dossier-field">
                                    <div class="dossier-label">🎯 Target Protein</div>
                                    <div class="dossier-value" style="color:#a78bfa;">{row.get('Target_Protein','N/A')}</div>
                                </div>
                                <div class="dossier-field">
                                    <div class="dossier-label">🧬 Drug Class</div>
                                    <div class="dossier-value">{row.get('Target_Protein_Class','N/A')}</div>
                                </div>
                                <div class="dossier-field">
                                    <div class="dossier-label">💊 Line of Therapy</div>
                                    <div class="dossier-value">{row.get('Line_of_Therapy','N/A')}</div>
                                </div>
                                <div class="dossier-field dossier-full">
                                    <div class="dossier-label">⚙️ Mechanism of Action (Pharmacodynamics)</div>
                                    <div class="dossier-value">{row.get('Mechanism_of_Action','N/A')}</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                            # PK Metrics
                            st.markdown("""
                            <div class="section-header" style="font-size:0.95rem;margin-top:1rem;">
                                <div class="section-icon" style="background:rgba(6,182,212,0.15);font-size:0.85rem;">📈</div>
                                Pharmacokinetics (ADME)
                            </div>
                            """, unsafe_allow_html=True)

                            hl = row.get("Half_Life_h", "N/A")
                            ppb = row.get("PPB_percent", "N/A")
                            hl_str = f"{hl}h" if isinstance(hl, (int, float)) else str(hl)
                            ppb_str = f"{ppb}%" if isinstance(ppb, (int, float)) else str(ppb)

                            st.markdown(f"""
                            <div class="pk-grid">
                                <div class="pk-metric">
                                    <div class="pk-value">{hl_str}</div>
                                    <div class="pk-name">Half-Life (t½)</div>
                                    <span class="pk-unit">h = hours</span>
                                </div>
                                <div class="pk-metric">
                                    <div class="pk-value">{ppb_str}</div>
                                    <div class="pk-name">Plasma Protein Binding</div>
                                    <span class="pk-unit">% bound</span>
                                </div>
                                <div class="pk-metric">
                                    <div class="pk-value" style="font-size:1.1rem;">{row.get('Route_of_Administration','N/A').split('(')[0].strip()}</div>
                                    <div class="pk-name">Route of Admin</div>
                                    <span class="pk-unit">administration</span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                            # Lipinski RO5
                            if lip:
                                ro5_badge = f'<span class="lipinski-pass">✅ PASS</span>' if lip["RO5_Pass"] else f'<span class="lipinski-fail">❌ FAIL (Biologic/Large MW)</span>'
                                st.markdown(f"""
                                <div style="margin-top:0.8rem;">
                                    <div class="dossier-label">🧪 Lipinski's Rule of 5 — {ro5_badge}</div>
                                    <div class="lipinski-grid">
                                        <div class="lipinski-rule">
                                            <span>MW</span>
                                            <span style="color:{'#10b981' if lip['MW']<=500 else '#ef4444'}">{lip['MW']} Da {'✓' if lip['MW']<=500 else '✗'}</span>
                                        </div>
                                        <div class="lipinski-rule">
                                            <span>LogP</span>
                                            <span style="color:{'#10b981' if lip['LogP']<=5 else '#ef4444'}">{lip['LogP']} {'✓' if lip['LogP']<=5 else '✗'}</span>
                                        </div>
                                        <div class="lipinski-rule">
                                            <span>HBD</span>
                                            <span style="color:{'#10b981' if lip['HBD']<=5 else '#ef4444'}">{lip['HBD']} {'✓' if lip['HBD']<=5 else '✗'}</span>
                                        </div>
                                        <div class="lipinski-rule">
                                            <span>HBA</span>
                                            <span style="color:{'#10b981' if lip['HBA']<=10 else '#ef4444'}">{lip['HBA']} {'✓' if lip['HBA']<=10 else '✗'}</span>
                                        </div>
                                        <div class="lipinski-rule">
                                            <span>TPSA</span>
                                            <span style="color:#94a3b8;">{lip['TPSA']} Å²</span>
                                        </div>
                                        <div class="lipinski-rule">
                                            <span>RotBonds</span>
                                            <span style="color:#94a3b8;">{lip['RotBonds']}</span>
                                        </div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)

                            # Safety Profile
                            st.markdown("""
                            <div class="section-header" style="font-size:0.95rem;margin-top:1rem;">
                                <div class="section-icon" style="background:rgba(239,68,68,0.15);font-size:0.85rem;">⚠️</div>
                                Safety Profile
                            </div>
                            """, unsafe_allow_html=True)

                            bbw = str(row.get("Major_BBW", "None"))
                            ddi = str(row.get("Significant_DDI", "N/A"))

                            st.markdown(f"""
                            <div class="bbw-box">
                                <div class="bbw-label">⬛ Black Box Warning (BBW)</div>
                                <div class="bbw-text">{bbw if bbw and bbw.lower() != 'none' else '⬛ No Black Box Warning on label'}</div>
                            </div>
                            <div class="ddi-box" style="margin-top:0.5rem;">
                                <div class="ddi-label">⚡ Significant Drug–Drug Interactions</div>
                                <div class="ddi-text">{ddi}</div>
                            </div>
                            """, unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════
    # TAB 2 — DRUG EXPLORER (individual drug lookup)
    # ════════════════════════════════════════════════════════════════════════
    with tab2:
        st.markdown("""
        <div class="section-header">
            <div class="section-icon" style="background:rgba(139,92,246,0.2);">🔬</div>
            Individual Drug Deep-Dive
        </div>
        """, unsafe_allow_html=True)

        all_drug_names = sorted(df["Drug_Name"].unique().tolist())
        col_search, col_btn = st.columns([3, 1])
        with col_search:
            selected_drug = st.selectbox("Select Drug for Full Profile", options=["— Select Drug —"] + all_drug_names, key="drug_explorer_select")

        if selected_drug != "— Select Drug —":
            drug_row = df[df["Drug_Name"] == selected_drug].iloc[0]
            smiles = str(drug_row.get("SMILES", ""))
            lip = calculate_lipinski(smiles)

            # All cancers this drug treats
            drug_cancers = df[df["Drug_Name"] == selected_drug]["Cancer_Type"].unique().tolist()

            col_struct, col_info = st.columns([1, 1.6])
            with col_struct:
                st.markdown("#### 🧪 2D Structure")
                img_data = smiles_to_2d_image(smiles, width=380, height=280)
                if img_data:
                    st.markdown(f'<div style="background:#0a0e1a;border:1px solid #1e293b;border-radius:10px;padding:8px;"><img src="{img_data}" style="max-width:100%;"></div>', unsafe_allow_html=True)
                
                st.markdown("#### 🌐 3D Conformation")
                if RDKIT_OK and smiles:
                    mol_block = generate_3d_mol_block(smiles)
                    if mol_block and PY3DMOL_OK:
                        html_3d = render_3d_viewer_html(mol_block, style=mol_style)
                        if html_3d:
                            import streamlit.components.v1 as components
                            components.html(f'<div style="background:#050a14;border-radius:10px;overflow:hidden;">{html_3d}</div>', height=400)
                    elif mol_block:
                        st.info("Install py3Dmol for interactive 3D viewer.")
                
                with st.expander("📋 SMILES"):
                    st.code(smiles)

            with col_info:
                st.markdown(f"## {drug_row['Drug_Name']}")
                st.markdown(f"**Brand Name:** {drug_row.get('Brand_Name', 'N/A')}")
                st.markdown(get_route_badge(str(drug_row.get("Route_of_Administration", "N/A"))), unsafe_allow_html=True)
                st.markdown(f"""
                <div style="margin:1rem 0;">
                    {get_fda_badge(str(drug_row.get('FDA_Status','N/A')))}
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"**Mechanism of Action:**\n> {drug_row.get('Mechanism_of_Action', 'N/A')}")
                
                st.markdown(f"""
                **Pharmacokinetics:**
                - **Half-Life (t½):** {drug_row.get('Half_Life_h', 'N/A')} hours  
                - **Plasma Protein Binding:** {drug_row.get('PPB_percent', 'N/A')}%  
                - **Target:** {drug_row.get('Target_Protein', 'N/A')} ({drug_row.get('Target_Protein_Class', 'N/A')})
                """)

                if lip:
                    ro5_status = "✅ PASSES Lipinski RO5" if lip["RO5_Pass"] else "❌ Violates Lipinski RO5 (may be biologic)"
                    st.markdown(f"**Lipinski RO5:** {ro5_status}")
                    st.markdown(f"> MW={lip['MW']} Da | LogP={lip['LogP']} | HBD={lip['HBD']} | HBA={lip['HBA']} | TPSA={lip['TPSA']} Å²")

                st.markdown(f"""
                <div class="bbw-box" style="margin-top:1rem;">
                    <div class="bbw-label">⬛ Black Box Warnings</div>
                    <div class="bbw-text">{drug_row.get('Major_BBW','None')}</div>
                </div>
                <div class="ddi-box" style="margin-top:0.6rem;">
                    <div class="ddi-label">⚡ Drug–Drug Interactions</div>
                    <div class="ddi-text">{drug_row.get('Significant_DDI','N/A')}</div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("#### 🎯 Approved Cancer Indications")
                for cancer in drug_cancers[:15]:
                    st.markdown(f"- {cancer}")
                if len(drug_cancers) > 15:
                    st.markdown(f"*...and {len(drug_cancers)-15} more*")

    # ════════════════════════════════════════════════════════════════════════
    # TAB 3 — ANALYTICS DASHBOARD
    # ════════════════════════════════════════════════════════════════════════
    with tab3:
        st.markdown("""
        <div class="section-header">
            <div class="section-icon" style="background:rgba(245,158,11,0.2);">📊</div>
            Database Analytics & Insights
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 🎯 Drug Classes Distribution")
            class_counts = df.groupby("Target_Protein_Class")["Drug_Name"].nunique().sort_values(ascending=False)
            st.bar_chart(class_counts, use_container_width=True)

        with col2:
            st.markdown("#### 💊 Route of Administration")
            route_counts = df.groupby("Route_of_Administration")["Drug_Name"].nunique().sort_values(ascending=False)
            st.bar_chart(route_counts, use_container_width=True)

        st.markdown("#### 🌡️ Efficacy Score Distribution by Drug Class")
        efficacy_by_class = df.groupby("Target_Protein_Class")["Efficacy_Score"].mean().sort_values(ascending=False)
        st.bar_chart(efficacy_by_class, use_container_width=True)

        st.markdown("#### 📋 Full Drug Database Preview")
        display_cols = ["Cancer_Type", "Drug_Name", "Brand_Name", "Target_Protein_Class",
                       "FDA_Status", "Route_of_Administration", "Efficacy_Score", "Line_of_Therapy"]
        st.dataframe(
            df[display_cols].style.background_gradient(subset=["Efficacy_Score"], cmap="Blues"),
            use_container_width=True,
            height=400,
        )

        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            csv_download = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Download Full Database (CSV)",
                data=csv_download,
                file_name="oncomatc_drug_database.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with col_dl2:
            json_download = df.to_json(orient="records", indent=2).encode("utf-8")
            st.download_button(
                "⬇️ Download Database (JSON)",
                data=json_download,
                file_name="oncomatc_drug_database.json",
                mime="application/json",
                use_container_width=True,
            )

    # ── Footer ─────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="footer">
        <strong>OncoMatch-AI Professional</strong> &nbsp;|&nbsp;
        Built with ❤️ for Oncology & Clinical Pharmacy
        &nbsp;|&nbsp; Powered by RDKit · Streamlit · py3Dmol &nbsp;|&nbsp;
        ⚕️ For <u>Research & Educational Use Only</u>. Not a substitute for clinical judgment.
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
