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
    1: ("Las Copas", "https://song.link/s/3h7aOWSNMYCqmNHgDqPxwr", "intro to an emotional and intense record."),
    2: ("Luna Creciente", "https://song.link/s/6IwecaOWZm1ZAFvizsi8wK", "blending folk forms into modernist songs or sensual and spiritual power. it doesn't get much better than this."),
    3: ("two moons", "https://song.link/s/6qcUFIPZU2sJXiI1sqzwZG", "i like toe."),
    4: ("Comafields", "https://song.link/s/7C041UO4n5LmaPVcRaQfzc", "hypnotizing."),
    5: ("On the Beach", "https://song.link/s/1Y8L4hT9CDJH6ROK2XGxgO", "the saddest beach album to ever exist, but one of the best tracks ever recorded."),
    6: ("Retrato Em Branco E Preto", "https://song.link/s/2qT5u5tjgcMoo3kIGehYTg", "harmony wrapped up in music."),
    7: ("I Wanted You to Feel the Same", "https://song.link/s/1BdovansNUKOu0ZrmZAqGj", "4:30pm overcast driving alone music"),
    8: ("Ice In My OJ", "https://song.link/s/5mmnCxPS0eJIVySUDVNGsV", "just fun."),
    9: ("Oganesson", "https://song.link/s/5kvcdd6qitCHttxm8R9GTS", "as fun as post-rock can get."),
    10: ("Ah Te Vi Entre Las Luces", "https://song.link/s/3uZfEOQOiAmHXDV02FZM4e", "progressive rock at its best. it's hard to suppress a smile."),
    11: ("Yulquen", "https://song.link/s/7oZwhOIxuFxRzqKmOKDgiO", "melancholia dripping from iron cogs."),
    12: ("Direccion", "https://song.link/s/2siqNGLzLa2akxxAOTiaUp", "transcended."),
    13: ("June Guitar", "https://song.link/s/1leMmYw98725djni7wSYhq", "written for summer and catching memories."),
    14: ("Forgetting in the Static", "https://song.link/s/4YFmWrIkTcZGSRGqcZAdrp", "solid ambient stuff."),
    15: ("In Your Room", "https://song.link/s/7c7XYwFipX776UmPzHNYIa", "some pretty great sheogaze."),
    16: ("Cherry Blue", "https://song.link/s/3go8gVfny946UDXxtqosA3", "this album is living and breathing."),
    17: ("The Tinker", "https://song.link/s/6D3XmDC4X7PwtOZJgI4BLi", "sax off the scale."),
    18: ("New Grass", "https://song.link/s/51Lt2RN3W0u2xI0LiARCRm", "absolutely one of the most beautiful pieces of music ever recorded."),
    19: ("The Tinman", "https://song.link/s/5DF3wNvPgRcIOyKsSdUycz", "rain come down on me, but i feel alive."),
    20: ("Seriously Deep", "https://song.link/s/6zjfTbw3329mWvWprVrlWH", "take your time and soak it in."),
    21: ("September Come Take This Heart Away", "https://song.link/s/1bnEw1xzEc5f05KdbU9M7r", "*wiping tears from eyes*"),
    22: ("Three Over Steel", "https://song.link/s/7I9yTWyCFi66PBhhhqZkyH", "exploring space through communal joy."),
    23: ("君のもとへ還るその日を夢見て", "https://song.link/s/3ZP6Ncsl16eNbDIketdOQt", "let yourself go and be carried away."),
    24: ("Waco, Texas", "https://song.link/s/1gVsiqgAxncJ4sKcuT7HW6", "bleak yet beautiful record."),
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
st.title("Niko's Adventskalender")

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
