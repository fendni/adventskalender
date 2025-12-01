import streamlit as st
import streamlit.components.v1 as components
import html
import json

st.set_page_config(page_title="Adventskalender — Liste mit Popup", layout="wide")

# -------------------------
# DATEN (Tag -> (Titel, song.link, Notiz))
# Ersetze die song.link-URLs und Notizen nach Bedarf.
# -------------------------
SONGS = {
    1: ("Love u", "https://song.link/s/0JzH4bb8aZlolWGaKQmBD0", "das ist ein tolles lied"),
    2: ("Luna Creciente", "https://song.link/s/6IwecaOWZm1ZAFvizsi8wK", "Kurze Info zu Song 2."),
    3: ("Titel 3", "https://song.link/SONGLINK_URL_3", "Kurze Info zu Song 3."),
    4: ("Titel 4", "https://song.link/SONGLINK_URL_4", ""),
    5: ("Titel 5", "https://song.link/SONGLINK_URL_5", ""),
    6: ("Titel 6", "https://song.link/SONGLINK_URL_6", ""),
    7: ("Titel 7", "https://song.link/SONGLINK_URL_7", ""),
    8: ("Titel 8", "https://song.link/SONGLINK_URL_8", ""),
    9: ("Titel 9", "https://song.link/SONGLINK_URL_9", ""),
    10: ("Titel 10", "https://song.link/SONGLINK_URL_10", ""),
    11: ("Titel 11", "https://song.link/SONGLINK_URL_11", ""),
    12: ("Titel 12", "https://song.link/SONGLINK_URL_12", ""),
    13: ("Titel 13", "https://song.link/SONGLINK_URL_13", ""),
    14: ("Titel 14", "https://song.link/SONGLINK_URL_14", ""),
    15: ("Titel 15", "https://song.link/SONGLINK_URL_15", ""),
    16: ("Titel 16", "https://song.link/SONGLINK_URL_16", ""),
    17: ("Titel 17", "https://song.link/SONGLINK_URL_17", ""),
    18: ("Titel 18", "https://song.link/SONGLINK_URL_18", ""),
    19: ("Titel 19", "https://song.link/SONGLINK_URL_19", ""),
    20: ("Titel 20", "https://song.link/SONGLINK_URL_20", ""),
    21: ("Titel 21", "https://song.link/SONGLINK_URL_21", ""),
    22: ("Titel 22", "https://song.link/SONGLINK_URL_22", ""),
    23: ("Titel 23", "https://song.link/SONGLINK_URL_23", ""),
    24: ("Titel 24", "https://song.link/SONGLINK_URL_24", ""),
}

# -------------------------
# Styles: Zahl + Button linksbündig, kompakt
# -------------------------
st.markdown(
    """
    <style>
    .row { display:flex; align-items:center; gap:10px; padding:6px 0; border-bottom:1px solid #eee; }
    .day { width: 48px; font-weight:700; }
    .btn-placeholder { /* container for button, keeps it left */ }
    .open-button {
        background:#2b6cb0;
        color:white;
        padding:6px 12px;
        border-radius:6px;
        text-decoration:none;
        font-weight:600;
        border: none;
        cursor: pointer;
    }
    .open-button:active { transform: translateY(1px); }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------
# Helper: inject popup into PARENT DOM (no gap — iframe height = 0)
# -------------------------
def inject_popup(day: int, title: str, url: str, note: str):
    """
    Injects a floating overlay into the parent.document via a tiny iframe (components.html).
    Strings are JSON-encoded to avoid JS/Python interpolation issues (dollar signs, quotes, etc.).
    """
    js_title = json.dumps(title)
    js_note = json.dumps(note if note else "Keine Zusatzinfo.")
    js_url = json.dumps(url)

    # Note: use double braces {{ }} in f-string to emit literal { } for JS template literals like `${...}`
    js = f"""
    <script>
    (function() {{
        try {{
            const parentDoc = parent.document;

            // Remove any existing overlay with same id
            const existing = parentDoc.getElementById('st_popup_overlay');
            if (existing) existing.remove();

            // Create overlay
            const overlay = parentDoc.createElement('div');
            overlay.id = 'st_popup_overlay';
            Object.assign(overlay.style, {{
                position: 'fixed',
                inset: '0',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background: 'rgba(0,0,0,0.55)',
                zIndex: '9999999'
            }});

            // Create box
            const box = parentDoc.createElement('div');
            box.id = 'st_popup_box';
            Object.assign(box.style, {{
                background: 'white',
                color: '#111',
                padding: '20px',
                borderRadius: '12px',
                maxWidth: '640px',
                width: '90%',
                boxShadow: '0 12px 36px rgba(0,0,0,0.35)',
                textAlign: 'center'
            }});

            const titleVar = {js_title};
            const noteVar  = {js_note};
            const urlVar   = {js_url};

            // Use JS template literal with literal ${...} - must escape braces in Python f-string as {{ and }}
            box.innerHTML = `
                <h3>Tür {day} — ${{titleVar}}</h3>
                <div style="color:#333; margin-bottom:14px;">${{noteVar}}</div>
                <div style="display:flex; gap:12px; justify-content:center; margin-top:8px;">
                    <a href="${{urlVar}}" target="_blank" rel="noopener noreferrer"
                       style="text-decoration:none; padding:10px 16px; border-radius:8px; background:#2b6cb0; color:white; font-weight:700;">
                       Song öffnen
                    </a>
                    <button id="st_popup_close" style="padding:10px 16px; border-radius:8px; background:#eee; border:1px solid #bbb; font-weight:600;">
                       Schließen
                    </button>
                </div>
            `;

            overlay.appendChild(box);
            parentDoc.body.appendChild(overlay);

            // clicking outside the box (on overlay) removes it
            overlay.addEventListener('click', function(e) {{
                if (e.target === overlay) {{
                    overlay.remove();
                }}
            }}, true);

            // close button
            const closeBtn = parentDoc.getElementById('st_popup_close');
            if (closeBtn) {{
                closeBtn.addEventListener('click', function(e) {{
                    e.preventDefault();
                    overlay.remove();
                }});
            }}
        }} catch (err) {{
            console.error('Popup injection failed', err);
            try {{ parent.alert('Popup konnte nicht geöffnet werden.'); }} catch(e){{ }}
        }}
    }})();
    </script>
    """

    # Render with zero height -> no gap in layout
    components.html(js, height=0, scrolling=False)


# -------------------------
# Hauptliste: Zahl + "Öffnen"-Button linksbündig
# -------------------------
st.title("Nikos Adventskalender")

st.markdown("<div style='margin-bottom:8px; color:#555;'></div>", unsafe_allow_html=True)

for day in range(1, 25):
    title, url, note = SONGS.get(day, (f"(kein Titel {day})", "", ""))

    # Render a compact left-aligned row: number + button
    cols = st.columns([0.06, 0.18, 0.76])  # narrow number, button next, rest spacer
    date_str = f"{day:02d}.12."
    cols[0].markdown(f"<div class='day'>{date_str}</div>", unsafe_allow_html=True)


    # Button: on click -> server calls inject_popup which injects overlay in parent
    if cols[1].button("Öffnen", key=f"open_{day}"):
        inject_popup(day, title, url, note)

    # keep the third column empty / for alignment
    cols[2].markdown("")

# small spacer at bottom
st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
