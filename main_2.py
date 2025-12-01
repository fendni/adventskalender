import streamlit as st
import streamlit.components.v1 as components
import json
import html

st.set_page_config(page_title="Adventskalender — Liste mit Popup", layout="wide")

# -------------------------
# DATEN (Tag -> (Titel, song.link, Notiz))
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
# CSS: Layout & grüne Öffnen-Buttons
# -------------------------
st.markdown(
    """
    <style>
    /* Row layout: datum + button inline, vertikal zentriert */
    .row { display:flex; align-items:center; gap:10px; padding:8px 0; border-bottom:1px solid #eee; }
    .day { min-width:72px; width:72px; font-weight:700; text-align:left; }
    /* Streamlit buttons: style all primary buttons to green */
    .stButton>button {
        background-color: #28a745 !important;
        border-color: #28a745 !important;
        color: white !important;
    }
    .stButton>button:active { transform: translateY(1px); }
    .stButton>button:hover { filter: brightness(0.95); }
    /* Make the popup headline not wrap on larger screens, but allow wrap on small */
    .st-popup-h3 { font-size:1.15rem; font-weight:700; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
    @media (max-width: 480px) {
        .st-popup-h3 { white-space:normal; }
        .day { width:64px; min-width:64px; }
        .stButton>button { padding:6px 10px !important; font-size:0.95rem !important; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------
# inject_popup: robust, uses json.dumps for safe string embedding
# - First tries to set parent.frameElement fixed and render overlay inside iframe (no gap)
# - Then tries parent.document injection
# - Fallback: overlay inside iframe
# -------------------------
def inject_popup(day: int, title: str, url: str, note: str):
    js_title = json.dumps(title)
    js_note = json.dumps(note if note else "Keine Zusatzinfo.")
    js_url = json.dumps(url)

    js = f"""
    <script>
    (function() {{
        const titleVar = {js_title};
        const noteVar = {js_note};
        const urlVar = {js_url};

        const htmlContent = `
            <div class="st-popup-box" style="
                background:white;color:#111;padding:20px;border-radius:12px;
                max-width:720px;width:90%;box-shadow:0 12px 36px rgba(0,0,0,0.35);text-align:center;">
                <h3 class="st-popup-h3">Tür {day} — ${'{'}titleVar{'}'}</h3>
                <div style="color:#333;margin-bottom:14px;">${'{'}noteVar{'}'}</div>
                <div style="display:flex;gap:12px;justify-content:center;margin-top:8px;">
                    <a href="${'{'}urlVar{'}'}" target="_blank" rel="noopener noreferrer"
                       style="text-decoration:none;padding:10px 16px;border-radius:8px;background:#2b6cb0;color:white;font-weight:700;">
                       Song öffnen
                    </a>
                    <button id="st_popup_close" style="padding:10px 16px;border-radius:8px;background:#eee;border:1px solid #bbb;font-weight:600;cursor:pointer;">
                       Schließen
                    </button>
                </div>
            </div>
        `;

        function createOverlay(doc) {{
            try {{
                const existing = doc.getElementById('st_popup_overlay');
                if (existing) existing.remove();

                const overlay = doc.createElement('div');
                overlay.id = 'st_popup_overlay';
                Object.assign(overlay.style, {{
                    position: 'fixed', inset: '0', display: 'flex', alignItems: 'center',
                    justifyContent: 'center', background: 'rgba(0,0,0,0.55)', zIndex: '2147483647'
                }});

                const container = doc.createElement('div');
                container.innerHTML = htmlContent;
                overlay.appendChild(container);
                doc.body.appendChild(overlay);

                overlay.addEventListener('click', function(e) {{
                    if (e.target === overlay) overlay.remove();
                }}, true);

                const closeBtn = doc.getElementById('st_popup_close');
                if (closeBtn) closeBtn.addEventListener('click', function(e) {{
                    e.preventDefault();
                    overlay.remove();
                }});
                return true;
            }} catch (err) {{
                return false;
            }}
        }}

        // 1) Try to make the iframe element fixed (so it covers viewport, no gap)
        try {{
            if (parent && parent.frameElement) {{
                try {{
                    const fe = parent.frameElement;
                    fe.style.position = 'fixed';
                    fe.style.inset = '0';
                    fe.style.width = '100vw';
                    fe.style.height = '100vh';
                    fe.style.zIndex = '2147483646';
                    fe.style.border = 'none';
                    fe.style.margin = '0';
                    fe.style.padding = '0';
                    // create overlay inside this iframe's document
                    const ok = createOverlay(window.document);
                    if (ok) return;
                }} catch (errInner) {{
                    // fall through
                }}
            }}
        }} catch(e){{ }}

        // 2) Try to inject into parent.document
        try {{
            if (parent && parent.document) {{
                const ok2 = createOverlay(parent.document);
                if (ok2) return;
            }}
        }} catch(e2){{ }}

        // 3) Fallback: create overlay inside iframe document
        try {{
            createOverlay(window.document);
            return;
        }} catch(e3){{ console.error('Popup fallback failed', e3); }}
    }})();
    </script>
    """

    # Use minimal height to avoid layout gap. parent.frameElement styling ensures iframe covers viewport in most browsers.
    components.html(js, height=1, scrolling=False)


# -------------------------
# Hauptliste: Datum als 01.12. + Öffnen-Button linksbündig & mittig
# -------------------------
st.title("Adventskalender — Liste")
st.markdown("<div style='margin-bottom:8px; color:#555;'>Klicke 'Öffnen', um Details im Popup zu sehen.</div>", unsafe_allow_html=True)

for day in range(1, 25):
    title, url, note = SONGS.get(day, (f"(kein Titel {day})", "", ""))
    date_str = f"{day:02d}.12."

    # Layout: zwei Spalten, links Datum, rechts Button (both left-aligned visually)
    c1, c2, c3 = st.columns([0.12, 0.18, 0.70])
    c1.markdown(f"<div class='day'>{date_str}</div>", unsafe_allow_html=True)

    # The Streamlit button triggers server-side injection reliably on all browsers
    if c2.button("Öffnen", key=f"open_{day}"):
        inject_popup(day, title, url, note)

    c3.markdown("", unsafe_allow_html=True)

# spacer
st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
