import streamlit as st
import vsketch
import pandas as pd
import textwrap
import os
import io
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
from google import genai
from supabase import create_client, Client
from dotenv import load_dotenv

# ==========================================
# 1. INITIALIZATION & CONNECTIONS
# ==========================================
load_dotenv()
st.set_page_config(page_title="Barcias Realty Engine", layout="wide", initial_sidebar_state="expanded")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

available_fonts = [f for f in os.listdir('.') if f.endswith('.ttf')]
if not available_fonts:
    available_fonts = ["No Fonts Found"]
DEFAULT_FONT = 'FeasiblySingleLine-z8D90.ttf'

# ==========================================
# 2. CORE DRAWING TOOLS
# ==========================================
def draw_smiley(vsk, x, y, size_inches=0.22):
    s = size_inches * 96 
    vsk.stroke(1) 
    with vsk.pushMatrix():
        vsk.translate(x, y)
        vsk.bezier(0, s/2, s*0.1, -s*0.1, s*0.9, -s*0.1, s, s/2)   
        vsk.circle(s*0.3, s*0.35, radius=s*0.04)
        vsk.circle(s*0.7, s*0.35, radius=s*0.04)
        vsk.bezier(s*0.25, s*0.6, s*0.4, s*0.8, s*0.6, s*0.8, s*0.75, s*0.6)

def generate_ai_note(first_name, address, topic_prompt, signature):
    prompt = f"Write a 1-sentence note to {first_name} at {address}. Theme: {topic_prompt}. Max 14 words. End with: '{signature}'"
    try:
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        return response.text.strip().replace('"', '')
    except:
        return f"Thinking of selling {address} in this market? Scan for a value update! {signature}"

# ==========================================
# 3. SIDEBAR (CONTROLS)
# ==========================================
with st.sidebar:
    st.title("⚙️ Campaign Control")
    campaign_name = st.text_input("Campaign Name", value="Chicago_Farming_2026")
    dest_url = st.text_input("QR Base URL", "https://barcias.com/value/")
    st.divider()
    uploaded_file = st.file_uploader("Upload Remine/MLS CSV", type="csv")
    st.divider()
    st.header("🎨 Typography")
    selected_font = st.selectbox("Font Selection:", available_fonts, index=available_fonts.index(DEFAULT_FONT) if DEFAULT_FONT in available_fonts else 0)
    g_size = st.slider("Greeting Font Size", 20, 50, 32)
    n_size = st.slider("Note Font Size", 15, 40, 24)
    st.divider()
    st.header("🧠 Message Brain")
    mode = st.radio("Content Source:", ["Gemini AI", "Manual Template"])
    if mode == "Gemini AI":
        topic = st.selectbox("Topic Preset:", ["Hot Market", "Home Value", "Merry Christmas", "Custom..."])
        instructions = st.text_area("AI Context:", topic if topic != "Custom..." else "Personalized market update")
    else:
        instructions = st.text_area("Template:", "Merry Christmas {name}! Thinking of selling {address}? Scan for info!")
    signature = st.text_input("Signature", "— Bernard 708-314-0477")
    batch_size = st.number_input("Cards per Batch", 1, 50, 10)

# ==========================================
# 4. MAIN INTERFACE
# ==========================================
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    total_batches = (len(df) // batch_size) + (1 if len(df) % batch_size > 0 else 0)
    batch_idx = st.number_input("Select Batch #", 1, total_batches, 1)

    fingerprint = f"{mode}-{instructions}-{batch_idx}-{signature}-{campaign_name}"
    start, end = (batch_idx - 1) * batch_size, min(batch_idx * batch_size, len(df))
    batch_df = df.iloc[start:end]

    if "current_notes" not in st.session_state or st.session_state.get("last_fp") != fingerprint:
        with st.spinner("Generating fresh notes..."):
            notes_list = []
            for _, row in batch_df.iterrows():
                fn = str(row.get('Owner 1 First Name', 'Neighbor')).split()[0].title()
                ad = str(row.get('Property Address', 'your home')).title()
                if mode == "Gemini AI" and client:
                    notes_list.append(generate_ai_note(fn, ad, instructions, signature))
                else:
                    msg = instructions.replace("{name}", fn).replace("{address}", ad)
                    notes_list.append(msg if signature in msg else f"{msg} {signature}")
            st.session_state.current_notes = notes_list
            st.session_state.last_fp = fingerprint
            if "ready_svg" in st.session_state: del st.session_state.ready_svg

    st.subheader(f"🖋 Preview: {campaign_name}")
    final_notes = []
    for i, note in enumerate(st.session_state.current_notes):
        final_notes.append(st.text_input(f"Postcard {i+1}", value=note, key=f"inp_{i}_{fingerprint}"))

    col1, col2 = st.columns(2)
    
    if col1.button("💾 1. Sync Leads to Supabase"):
        if supabase:
            with st.spinner("Uploading..."):
                payload = []
                for idx, row in batch_df.iterrows():
                    payload.append({
                        "id": int(idx),
                        "first_name": str(row.get('Owner 1 First Name', '')).title(),
                        "last_name": str(row.get('Owner 1 Last Name', '')).title(),
                        "address": str(row.get('Property Address', '')).title(),
                        "campaign": campaign_name,
                        "qr_url": f"{dest_url}?id={idx}"
                    })
                supabase.table("prospects").upsert(payload).execute()
                st.success("Synced!")

    if col2.button("🛠️ 2. Build Graphtec SVG"):
        if not selected_font or selected_font == "No Fonts Found":
            st.error("No font detected.")
            st.stop()

        vsk = vsketch.Vsketch()
        vsk.size("13x24in")
        INCH = 96
        # Fix: Ensure absolute path and clean string conversion for TextPath
        font_path = os.path.abspath(selected_font)
        f_prop = FontProperties(fname=font_path)

        for i, (idx, row) in enumerate(batch_df.iterrows()):
            col, row_num = i % 2, i // 2
            card_x, card_y = (0.5 * INCH) + (col * 5.5 * INCH), (1.0 * INCH) + (row_num * 4.25 * INCH)

            # Greeting
            f_name = str(row.get('Owner 1 First Name', 'Neighbor')).split()[0].title()
            with vsk.pushMatrix():
                vsk.translate(card_x + (0.4 * INCH), card_y + (0.9 * INCH))
                t_path = TextPath((0, 0), str(f"Hi {f_name},"), prop=f_prop, size=g_size)
                for poly in t_path.to_polygons(): vsk.polygon(poly[:, 0], -poly[:, 1], close=False)

            # Note body
            wrapped = textwrap.wrap(final_notes[i], width=21)
            curr_y = card_y + (1.5 * INCH)
            for line_idx, line in enumerate(wrapped[:6]):
                with vsk.pushMatrix():
                    vsk.translate(card_x + (0.4 * INCH), curr_y)
                    t_path = TextPath((0, 0), str(line), prop=f_prop, size=n_size)
                    for poly in t_path.to_polygons(): vsk.polygon(poly[:, 0], -poly[:, 1], close=False)
                if line_idx == len(wrapped[:6]) - 1:
                    draw_smiley(vsk, card_x + (2.3 * INCH), curr_y - (0.1 * INCH))
                curr_y += 0.52 * INCH

            # Recipient Address
            zip_clean = str(row.get('ZIP 5', row.get('Zip', ''))).split('.')[0]
            addr_x, addr_y = card_x + (3.1 * INCH), card_y + (2.3 * INCH)
            addr_lines = [
                f"{row.get('Owner 1 First Name', '')} {row.get('Owner 1 Last Name', '')}".upper(),
                str(row.get('Property Address', '')).upper(),
                f"CHICAGO, IL {zip_clean}".upper()
            ]
            for l_idx, line in enumerate(addr_lines):
                with vsk.pushMatrix():
                    vsk.translate(addr_x, addr_y + (l_idx * 0.35 * INCH))
                    t_path = TextPath((0, 0), str(line), prop=f_prop, size=18)
                    for poly in t_path.to_polygons(): vsk.polygon(poly[:, 0], -poly[:, 1], close=False)

        tmp_name = "plotter_temp.svg"
        vsk.save(tmp_name)
        with open(tmp_name, "r") as f:
            st.session_state.ready_svg = f.read()
        os.remove(tmp_name)
        st.success("SVG Generated!")

    if "ready_svg" in st.session_state:
        st.download_button("📥 DOWNLOAD SVG", st.session_state.ready_svg, f"{campaign_name}_B{batch_idx}.svg", "image/svg+xml")