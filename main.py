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
    Robust inject_popup:
    - versucht parent.frameElement auf position:fixed zu setzen (damit iframe das Viewport-overlay wird; keine Lücke)
    - wenn parent.frameElement nicht zugreifbar, versucht parent.document injection (alt)
    - falls beides nicht geht -> fallback: overlay inside iframe und iframe bleibt sichtbar (größere height)
    """
    import json
    js_title = json.dumps(title)
    js_note = json.dumps(note if note else "Keine Zusatzinfo.")
    js_url = json.dumps(url)

    js = f"""
    <script>
    (function() {{
        const titleVar = {js_title};
        const noteVar  = {js_note};
        const urlVar   = {js_url};

        const htmlContent = `
            <div id="st_popup_box" style="
                background:white;color:#111;padding:20px;border-radius:12px;
                max-width:640px;width:90%;box-shadow:0 12px 36px rgba(0,0,0,0.35);text-align:center;">
                <h3 style="margin:0 0 8px 0;">Tür {day} — ${{titleVar}}</h3>
                <div style="color:#333;margin-bottom:14px;">${{noteVar}}</div>
                <div style="display:flex;gap:12px;justify-content:center;margin-top:8px;">
                    <a href="${{urlVar}}" target="_blank" rel="noopener noreferrer"
                       style="text-decoration:none;padding:10px 16px;border-radius:8px;background:#2b6cb0;color:white;font-weight:700;">
                       Song öffnen
                    </a>
                    <button id="st_popup_close" style="padding:10px 16px;border-radius:8px;background:#eee;border:1px solid #bbb;font-weight:600;cursor:pointer;">
                       Schließen
                    </button>
                </div>
            </div>`;

        // helper to create overlay inside a given document (doc)
        function createOverlayInDoc(doc, useWrapper=false) {{
            try {{
                // remove existing
                const old = doc.getElementById('st_popup_overlay');
                if (old) old.remove();

                const overlay = doc.createElement('div');
                overlay.id = 'st_popup_overlay';
                Object.assign(overlay.style, {{
                    position: 'fixed',
                    inset: '0',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    background: 'rgba(0,0,0,0.55)',
                    zIndex: '2147483647'
                }});

                const container = doc.createElement(useWrapper ? 'div' : 'div');
                container.innerHTML = htmlContent;
                overlay.appendChild(container);
                doc.body.appendChild(overlay);

                // close handlers
                overlay.addEventListener('click', function(e) {{
                    if (e.target === overlay) overlay.remove();
                }}, true);

                const closeBtn = doc.getElementById('st_popup_close');
                if (closeBtn) closeBtn.addEventListener('click', function(e) {{ e.preventDefault(); overlay.remove(); }});

                return true;
            }} catch (err) {{
                return false;
            }}
        }}

        // 1) Try to make the iframe element fixed (so it doesn't take layout space) and render overlay inside iframe
        try {{
            if (parent && parent.frameElement) {{
                try {{
                    // style the iframe element in parent so it overlays the viewport and doesn't create a gap
                    const fe = parent.frameElement;
                    fe.style.position = 'fixed';
                    fe.style.inset = '0';
                    fe.style.width = '100vw';
                    fe.style.height = '100vh';
                    fe.style.zIndex = '2147483646';
                    fe.style.border = 'none';
                    fe.style.margin = '0';
                    fe.style.padding = '0';
                    // Now create overlay INSIDE the iframe's document (this document)
                    // because iframe itself now covers viewport, the overlay will appear above page without layout shift
                    const ok = createOverlayInDoc(document, false);
                    if (ok) return;
                }} catch (errInner) {{
                    // if frameElement styling fails, fall through to parent.document attempt
                }}
            }}
        }} catch (err) {{
            // ignore
        }}

        // 2) Try to inject directly into parent.document (older approach)
        try {{
            if (parent && parent.document) {{
                const ok = createOverlayInDoc(parent.document, true);
                if (ok) return;
            }}
        }} catch (err) {{
            // ignore
        }}

        // 3) Fallback: create overlay inside this iframe (may require iframe to have visible height)
        try {{
            // remove existing fallback overlay
            const old2 = document.getElementById('st_iframe_popup_overlay');
            if (old2) old2.remove();

            const overlay2 = document.createElement('div');
            overlay2.id = 'st_iframe_popup_overlay';
            Object.assign(overlay2.style, {{
                position: 'fixed',
                inset: '0',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background: 'rgba(0,0,0,0.55)',
                zIndex: '2147483647'
            }});

            const box2 = document.createElement('div');
            box2.innerHTML = htmlContent;
            overlay2.appendChild(box2);
            document.body.appendChild(overlay2);

            overlay2.addEventListener('click', function(e) {{
                if (e.target === overlay2) overlay2.remove();
            }}, true);

            const closeBtn2 = document.getElementById('st_popup_close');
            if (closeBtn2) closeBtn2.addEventListener('click', function(e) {{ e.preventDefault(); overlay2.remove(); }});
            return;
        }} catch (err) {{
            console.error('Final popup fallback failed', err);
        }}

    }})();
    </script>
    """

    # Render injector with minimal height (1px) so normal cases do not produce visible gap.
    # Because we set parent.frameElement to position:fixed, the iframe will not take layout space.
    components.html(js, height=1, scrolling=False)

    

    # End of inject_popup


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
