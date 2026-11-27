import html
from pathlib import Path

import streamlit as st
import prototype as rg
import auth as local_auth


st.set_page_config(
    page_title="RogueGuard | Identity Security Workbench",
    page_icon="RG",
    layout="wide",
    initial_sidebar_state="expanded",
)



def render_auth_screen():
    """Render first-run local admin setup or the local sign-in screen."""
    setup_mode = local_auth.user_count() == 0
    st.markdown(
        '<div class="rg-masthead"><div class="rg-brand"><div class="rg-mark">RG/</div>'
        '<div><div class="rg-brand-name">ROGUEGUARD</div>'
        '<div class="rg-brand-sub">LOCAL OPERATOR ACCESS / V1.0</div></div></div>'
        '<div class="rg-top-right"><div class="rg-top-label">SECURE WORKSPACE ENTRY</div>'
        '<div class="rg-live">AUTH GATE</div></div></div>',
        unsafe_allow_html=True,
    )
    left, right = st.columns([1.08, .92], gap="large")
    with left:
        st.markdown(
            '<div class="rg-auth-intro"><div class="rg-auth-kicker">IDENTITY SECURITY / LOCAL WORKSPACE</div>'
            '<div class="rg-auth-title">ACCESS IS A<br>PRIVILEGE.<br><em>PROVE YOURS.</em></div>'
            '<div class="rg-auth-copy">A controlled environment for investigating identity exposure, '
            'permission drift and response decisions. Authenticate to enter the analyst workbench.</div>'
            '<div class="rg-auth-stamp">LOCAL DATABASE &nbsp; / &nbsp; PARAMETERISED AUTH QUERIES &nbsp; / &nbsp; PBKDF2 HASHING</div></div>',
            unsafe_allow_html=True,
        )
    with right:
        if setup_mode:
            st.markdown(
                '<div class="rg-auth-heading">INITIALISE OPERATOR</div>'
                '<div class="rg-auth-sub">No local operator exists yet. Create the first administrator account to initialise this workspace. '
                'Public self-registration is disabled after setup.</div>',
                unsafe_allow_html=True,
            )
            with st.form("rg_initial_setup", clear_on_submit=False):
                username = st.text_input("OPERATOR USERNAME", placeholder="e.g. ayush.admin", max_chars=32)
                password = st.text_input("PASSWORD", type="password", placeholder="At least 12 characters", max_chars=128)
                confirmation = st.text_input("CONFIRM PASSWORD", type="password", max_chars=128)
                submitted = st.form_submit_button("CREATE LOCAL ADMIN", type="primary", width="stretch")
            if submitted:
                try:
                    created = local_auth.create_first_user(username, password, confirmation)
                    st.session_state["rg_auth_user"] = created
                    st.session_state["rg_auth_role"] = "ADMIN"
                    st.success("Local administrator created. Opening the workbench.")
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))
        else:
            st.markdown(
                '<div class="rg-auth-heading">OPERATOR SIGN IN</div>'
                '<div class="rg-auth-sub">Authenticate with the local operator account configured on this machine.</div>',
                unsafe_allow_html=True,
            )
            with st.form("rg_login_form", clear_on_submit=True):
                username = st.text_input("USERNAME", placeholder="Local operator", max_chars=64)
                password = st.text_input("PASSWORD", type="password", max_chars=512)
                submitted = st.form_submit_button("AUTHENTICATE", type="primary", width="stretch")
            if submitted:
                user = local_auth.authenticate(username, password)
                if user:
                    st.session_state["rg_auth_user"] = user["username"]
                    st.session_state["rg_auth_role"] = user["role"]
                    st.success("Authentication successful.")
                    st.rerun()
                else:
                    st.error("Sign-in failed. Check your credentials or wait for the temporary lockout to expire.")
        st.markdown(
            '<div class="rg-auth-footnote">PASSWORDS ARE STORED AS SALTED PBKDF2-HMAC-SHA256 HASHES. '
            'AUTHENTICATION LOOKUPS USE PARAMETERISED SQLITE QUERIES. FIVE FAILED ATTEMPTS TRIGGER A FIVE-MINUTE LOCKOUT. '
            'THIS IS A LOCAL PROTOTYPE AUTH GATE, NOT ENTERPRISE SSO.</div>',
            unsafe_allow_html=True,
        )
    st.markdown(
        '<div class="rg-footer"><span>ROGUEGUARD / IDENTITY SECURITY WORKBENCH</span>'
        '<span>NO CLOUD ACCESS / LOCAL SIMULATION</span><span>AUTHENTICATED SESSION REQUIRED</span></div>',
        unsafe_allow_html=True,
    )


def inject_theme():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:ital,wght@0,500;0,600;0,700;0,800;0,900;1,700;1,800;1,900&family=Space+Grotesk:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600;700&display=swap');
        :root {
            color-scheme: light;
            --paper: #eeede8;
            --surface: #f8f7f2;
            --ink: #17191b;
            --muted: #73777a;
            --line: #25282b;
            --soft-line: #d2d0c9;
            --acid: #c9f36a;
            --chrome: #b9c0c4;
            --red: #e34e3d;
            --amber: #dc9c32;
            --blue: #4c79a7;
        }
        html, body, [data-testid="stAppViewContainer"] {
            background: var(--paper) !important;
            color: var(--ink) !important;
            font-family: Inter, "Helvetica Neue", Arial, sans-serif;
        }
        [data-testid="stHeader"] {
            background: transparent !important;
            height: 2.2rem;
        }
        [data-testid="stMainBlockContainer"] {
            max-width: 1540px;
            padding: 1.65rem 3.1rem 3.6rem;
        }
        [data-testid="stToolbar"] { right: 1.2rem; }
        [data-testid="stSidebar"] {
            background: #17191b !important;
            border-right: 1px solid #3a3d40;
        }
        [data-testid="stSidebar"] * {
            color: #f3f2ed !important;
            font-family: "Space Grotesk", "Helvetica Neue", Arial, sans-serif !important;
        }
        [data-testid="stSidebar"] .rg-sidebar-brand-name,
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] strong {
            font-family: "Barlow Condensed", Impact, "Arial Narrow", sans-serif !important;
            font-weight: 900 !important;
            text-transform: uppercase !important;
            letter-spacing: .025em !important;
        }
        [data-testid="stSidebar"] .rg-sidebar-brand-name {
            display: block;
            font-size: 2rem !important;
            line-height: .88 !important;
            letter-spacing: -.025em !important;
        }
        [data-testid="stSidebar"] .rg-sidebar-brand-sub {
            display: block;
            margin-top: .35rem;
            color: #a6aaad !important;
            font: 700 .58rem/1.5 "IBM Plex Mono", monospace !important;
            letter-spacing: .15em !important;
            text-transform: uppercase;
        }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] strong {
            display: inline-block;
            font-size: 1.15rem !important;
            line-height: 1 !important;
        }
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p,
        [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
            font-family: "IBM Plex Mono", monospace !important;
            color: #a6aaad !important;
            font-size: .61rem !important;
            letter-spacing: .075em !important;
        }
        [data-testid="stSidebar"] [data-testid="stButton"] button {
            font-family: "Barlow Condensed", Impact, "Arial Narrow", sans-serif !important;
            font-size: 1.08rem !important;
            font-weight: 800 !important;
            letter-spacing: .09em !important;
        }
        [data-testid="stSidebar"] [data-baseweb="select"] * {
            font-family: "Space Grotesk", "Helvetica Neue", Arial, sans-serif !important;
        }
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
            color: #a6aaad !important;
        }
        [data-testid="stSidebar"] [data-baseweb="select"] > div,
        [data-testid="stSidebar"] input {
            background: #24272a !important;
            border: 1px solid #555a5e !important;
            border-radius: 2px !important;
        }
        [data-testid="stSidebar"] [data-testid="stButton"] button {
            background: var(--acid) !important;
            color: #17191b !important;
            border: 2px solid #0c0d0e !important;
            box-shadow: 3px 3px 0 #6d7e46 !important;
            font-weight: 800 !important;
        }
        [data-testid="stSidebar"] hr { border-color: #42464a !important; }
        h1, h2, h3, h4, p, label, li, span, div {
            font-family: Inter, "Helvetica Neue", Arial, sans-serif;
        }
        h1, h2, h3, h4 { color: var(--ink) !important; letter-spacing: -0.04em; }
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] li { color: var(--ink); }
        [data-testid="stCaptionContainer"] p {
            color: var(--muted) !important;
            font-size: .76rem !important;
        }
        [data-testid="stMetric"] {
            background: var(--surface);
            border: 1.5px solid var(--line);
            border-radius: 2px;
            padding: 1rem 1rem .85rem;
            box-shadow: 4px 4px 0 rgba(23,25,27,.14);
            min-height: 112px;
        }
        [data-testid="stMetricLabel"] p {
            color: #666b6f !important;
            text-transform: uppercase;
            letter-spacing: .11em;
            font-size: .66rem !important;
            font-weight: 800 !important;
        }
        [data-testid="stMetricValue"] {
            color: var(--ink) !important;
            font-size: 2rem !important;
            font-weight: 850 !important;
            letter-spacing: -.06em;
        }
        [data-testid="stMetricDelta"] { font-size: .7rem !important; }
        [data-testid="stTabs"] { margin-top: 1.2rem; }
        [data-testid="stTabs"] [data-baseweb="tab-list"] {
            gap: .45rem;
            border-bottom: 1.5px solid var(--line);
            background: transparent;
        }
        [data-testid="stTabs"] button[role="tab"] {
            color: #5c6063 !important;
            border: 1px solid transparent;
            border-radius: 2px 2px 0 0;
            padding: .65rem 1rem;
            font-size: .76rem;
            font-weight: 800;
            letter-spacing: .045em;
        }
        [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
            color: var(--ink) !important;
            background: var(--acid) !important;
            border: 1.5px solid var(--line) !important;
            border-bottom-color: var(--acid) !important;
        }
        [data-testid="stTabs"] [data-baseweb="tab-highlight"] { background: var(--ink) !important; }
        [data-testid="stTabs"] [data-baseweb="tab-border"] { display: none; }
        [data-testid="stButton"] button,
        [data-testid="stFormSubmitButton"] button,
        [data-testid="stDownloadButton"] button {
            color: var(--ink) !important;
            background: var(--surface) !important;
            border: 1.5px solid var(--line) !important;
            border-radius: 2px !important;
            box-shadow: 3px 3px 0 rgba(23,25,27,.2) !important;
            font-weight: 800 !important;
            letter-spacing: .015em;
            transition: transform .12s ease, box-shadow .12s ease;
        }
        [data-testid="stButton"] button:hover,
        [data-testid="stFormSubmitButton"] button:hover,
        [data-testid="stDownloadButton"] button:hover {
            transform: translate(-1px,-1px);
            box-shadow: 5px 5px 0 rgba(23,25,27,.24) !important;
            border-color: var(--ink) !important;
        }
        [data-testid="stButton"] button[kind="primary"],
        [data-testid="stFormSubmitButton"] button[kind="primary"] {
            background: var(--acid) !important;
        }
        [data-testid="stTextInput"] input,
        [data-testid="stTextArea"] textarea,
        [data-testid="stSelectbox"] [data-baseweb="select"] > div,
        [data-testid="stMultiSelect"] [data-baseweb="select"] > div,
        [data-testid="stDateInput"] input {
            background: var(--surface) !important;
            border: 1px solid #9d9d96 !important;
            border-radius: 2px !important;
            color: var(--ink) !important;
        }
        [data-testid="stDataFrame"] {
            border: 1px solid var(--line);
            border-radius: 2px;
            overflow: hidden;
        }
        [data-testid="stExpander"] {
            background: rgba(248,247,242,.72);
            border: 1px solid var(--soft-line);
            border-radius: 2px;
        }
        [data-testid="stAlert"] { border-radius: 2px; }
        hr { border-color: var(--soft-line) !important; }
        .rg-masthead {
            display:flex; align-items:center; justify-content:space-between;
            padding: .25rem 0 1.1rem; border-bottom: 1.5px solid var(--line);
            margin-bottom: 1.6rem;
        }
        .rg-brand { display:flex; align-items:center; gap:.85rem; }
        .rg-mark {
            display:flex; align-items:center; justify-content:center;
            width:42px; height:42px; background:var(--ink); color:var(--acid);
            font-size:1rem; font-weight:900; letter-spacing:-.1em;
            border:1.5px solid var(--ink); box-shadow:4px 4px 0 var(--acid);
        }
        .rg-brand-name { color:var(--ink); font-size:1.05rem; font-weight:900; letter-spacing:-.045em; }
        .rg-brand-sub { color:var(--muted); font:700 .58rem/1.5 ui-monospace, SFMono-Regular, monospace; letter-spacing:.16em; }
        .rg-top-right { display:flex; align-items:center; gap:1rem; }
        .rg-top-label { font:700 .62rem ui-monospace, monospace; color:#676c70; letter-spacing:.12em; }
        .rg-live {
            display:inline-flex; align-items:center; gap:.45rem; padding:.45rem .65rem;
            color:var(--ink); background:var(--acid); border:1.5px solid var(--line);
            font:900 .62rem ui-monospace, monospace; letter-spacing:.09em;
            box-shadow:3px 3px 0 var(--line);
        }
        .rg-live:before { content:""; width:7px; height:7px; border-radius:50%; background:#26351a; }
        .rg-hero {
            display:grid; grid-template-columns:minmax(0,1.6fr) minmax(180px,.6fr);
            align-items:center; gap:2rem; padding:1.8rem 1.9rem;
            background:var(--surface); border:1.5px solid var(--line);
            box-shadow:6px 6px 0 var(--line); position:relative; overflow:hidden;
            margin-bottom:1.15rem;
        }
        .rg-kicker { color:#656a6c; font:800 .63rem ui-monospace,monospace; letter-spacing:.18em; text-transform:uppercase; }
        .rg-hero h1 { margin:.45rem 0 .35rem; font-size:clamp(2rem,4vw,3.6rem); line-height:.98; font-weight:900; letter-spacing:-.075em; }
        .rg-hero h1 em { font-style:normal; color:#667d3e; }
        .rg-hero p { max-width:650px; color:#62676a; font-size:.9rem; line-height:1.55; margin:.75rem 0 0; }
        .rg-chrome-wrap { display:flex; justify-content:center; align-items:center; min-height:155px; }
        .rg-chrome {
            width:145px; height:145px; border-radius:50%; position:relative;
            background:
                radial-gradient(circle at 32% 24%, #ffffff 0 5%, #eef1f2 9%, transparent 22%),
                radial-gradient(circle at 70% 76%, #4e565d 0 2%, #aab1b6 12%, transparent 32%),
                radial-gradient(circle at 38% 38%, #f9fbfc 0 8%, #c8ced1 22%, #7e888e 40%, #f7f8f8 57%, #69747b 72%, #dce0e2 84%, #59646a 100%);
            box-shadow:inset -13px -14px 22px rgba(23,25,27,.42), inset 8px 9px 16px rgba(255,255,255,.9), 0 12px 24px rgba(23,25,27,.22);
        }
        .rg-chrome:before {
            content:""; position:absolute; inset:18px -14px 18px -14px;
            border:1px solid rgba(105,115,122,.65); border-radius:50%;
            transform:rotate(-28deg); box-shadow:0 0 0 5px rgba(255,255,255,.2);
        }
        .rg-chrome:after {
            content:""; position:absolute; left:18%; top:16%; width:43%; height:19%;
            border-radius:50%; background:linear-gradient(90deg,rgba(255,255,255,.9),rgba(255,255,255,0));
            filter:blur(5px); transform:rotate(-32deg);
        }
        .rg-safety {
            display:flex; align-items:center; gap:.8rem; padding:.72rem .9rem;
            background:#fff3dc; border:1.5px solid #8c5a15; color:#563b15;
            font-size:.76rem; font-weight:700; margin:1rem 0 1.25rem;
        }
        .rg-safety b { font:900 .62rem ui-monospace,monospace; letter-spacing:.12em; white-space:nowrap; }
        .rg-context {
            display:flex; justify-content:space-between; flex-wrap:wrap; gap:.6rem;
            padding:.55rem .75rem; border-top:1px solid var(--soft-line);
            border-bottom:1px solid var(--soft-line); margin-bottom:.4rem;
            color:#686d70; font:700 .65rem ui-monospace,monospace; letter-spacing:.06em;
        }
        .rg-context strong { color:var(--ink); }
        .rg-section { margin:.35rem 0 1rem; }
        .rg-section .rg-kicker { margin-bottom:.35rem; }
        .rg-section-title { font-size:1.38rem; font-weight:900; letter-spacing:-.055em; color:var(--ink); margin:0; }
        .rg-section-copy { color:#72777a; font-size:.78rem; line-height:1.5; margin:.25rem 0 0; }
        .rg-panel {
            background:var(--surface); border:1.2px solid var(--line); border-radius:2px;
            padding:1rem 1.05rem; box-shadow:4px 4px 0 rgba(23,25,27,.12);
            height:100%;
        }
        .rg-panel-head { display:flex; align-items:center; justify-content:space-between; gap:.5rem; margin-bottom:.75rem; }
        .rg-panel-title { color:var(--ink); font-size:.92rem; font-weight:900; letter-spacing:-.035em; }
        .rg-panel-tag { color:#73787b; font:700 .58rem ui-monospace,monospace; letter-spacing:.1em; }
        .rg-stat-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:.55rem; }
        .rg-stat {
            background:var(--surface); border:1.2px solid var(--line); padding:.75rem .85rem;
            box-shadow:3px 3px 0 rgba(23,25,27,.14); min-height:83px;
        }
        .rg-stat-label { color:#707578; font:800 .58rem ui-monospace,monospace; letter-spacing:.12em; text-transform:uppercase; }
        .rg-stat-value { color:var(--ink); font-size:1.7rem; font-weight:900; letter-spacing:-.07em; margin-top:.2rem; }
        .rg-stat-note { color:#808487; font-size:.62rem; margin-top:.1rem; }
        .rg-bar-row { display:grid; grid-template-columns:75px 1fr 24px; gap:.65rem; align-items:center; margin:.76rem 0; }
        .rg-bar-label { color:#5e6467; font:800 .62rem ui-monospace,monospace; }
        .rg-bar-track { height:10px; background:#e3e2dc; border:1px solid #c3c3bd; }
        .rg-bar-fill { height:100%; background:var(--ink); }
        .rg-bar-fill.critical { background:var(--red); }
        .rg-bar-fill.high { background:#d48c29; }
        .rg-bar-fill.medium { background:#748aa1; }
        .rg-bar-fill.low { background:#aab2b8; }
        .rg-bar-count { color:var(--ink); text-align:right; font:900 .7rem ui-monospace,monospace; }
        .rg-table { width:100%; border-collapse:collapse; font-size:.69rem; }
        .rg-table th {
            padding:.55rem .55rem; text-align:left; background:#e6e5df;
            border-bottom:1.5px solid var(--line); color:#666c6f;
            font:800 .57rem ui-monospace,monospace; text-transform:uppercase; letter-spacing:.09em;
        }
        .rg-table td { padding:.58rem .55rem; border-bottom:1px solid #deddd6; color:#282c2e; vertical-align:top; }
        .rg-table tr:last-child td { border-bottom:0; }
        .rg-mono { font-family:ui-monospace,SFMono-Regular,Menlo,monospace !important; font-size:.66rem; }
        .rg-pill {
            display:inline-block; padding:.2rem .4rem; border:1px solid currentColor;
            font:900 .55rem ui-monospace,monospace; letter-spacing:.06em; white-space:nowrap;
        }
        .rg-pill.critical { background:#fde4df; color:#a22e21; }
        .rg-pill.high { background:#ffedcf; color:#8a5a14; }
        .rg-pill.medium { background:#e3edf6; color:#395c7c; }
        .rg-pill.low { background:#e6e9e9; color:#596368; }
        .rg-pill.neutral { background:#eeeee8; color:#4e5558; }
        .rg-pill.good { background:#e6f2cd; color:#465d20; }
        .rg-relationship {
            display:grid; grid-template-columns:minmax(0,1fr) 90px minmax(0,1fr);
            align-items:center; gap:.6rem; padding:.7rem .65rem;
            border:1px solid #d2d1ca; margin:.45rem 0; background:#f3f2ec;
        }
        .rg-node { padding:.6rem; border:1.2px solid var(--line); background:#fff; font-size:.67rem; font-weight:800; overflow-wrap:anywhere; }
        .rg-edge { text-align:center; color:#6c7376; font:800 .55rem ui-monospace,monospace; letter-spacing:.04em; }
        .rg-edge:after { content:"  →"; color:var(--ink); font-size:1rem; }
        .rg-note { color:#757a7c; font-size:.65rem; line-height:1.5; margin-top:.6rem; }
        .rg-feature {
            display:flex; justify-content:space-between; gap:1rem; align-items:flex-start;
            padding:.8rem 0; border-top:1px solid #deddd6;
        }
        .rg-feature:first-child { border-top:0; }
        .rg-feature strong { color:var(--ink); font-size:.77rem; }
        .rg-feature span { color:#757a7c; font-size:.69rem; text-align:right; }
        .rg-detail {
            padding:1rem; border:1.5px solid var(--line); background:#f8f7f2;
            box-shadow:4px 4px 0 rgba(23,25,27,.13); margin:.5rem 0 1rem;
        }
        .rg-detail-title { font-size:1.1rem; font-weight:900; letter-spacing:-.045em; color:var(--ink); }
        .rg-detail-sub { margin-top:.3rem; font-size:.7rem; color:#72777a; }
        .rg-footer {
            display:flex; justify-content:space-between; flex-wrap:wrap; gap:.5rem;
            border-top:1.5px solid var(--line); margin-top:2rem; padding-top:.8rem;
            color:#777c7e; font:700 .58rem ui-monospace,monospace; letter-spacing:.07em;
        }
        @media (max-width: 900px) {
            [data-testid="stMainBlockContainer"] { padding:1rem 1rem 2.5rem; }
            .rg-hero { grid-template-columns:1fr; }
            .rg-chrome-wrap { display:none; }
            .rg-stat-grid { grid-template-columns:repeat(2,minmax(0,1fr)); }
            .rg-relationship { grid-template-columns:1fr; }
            .rg-edge { text-align:left; }
        }

        html, body, [data-testid="stAppViewContainer"], input, textarea, button {
            font-family: "Space Grotesk", "Helvetica Neue", Arial, sans-serif !important;
        }
        h1, h2, h3, h4,
        .rg-brand-name, .rg-hero h1, .rg-section-title,
        .rg-panel-title, .rg-stat-value, .rg-detail-title {
            font-family: "Barlow Condensed", Impact, "Arial Narrow", sans-serif !important;
            font-weight: 900 !important;
            text-transform: uppercase;
        }
        .rg-brand-name {
            font-size: 1.55rem !important;
            letter-spacing: -.035em !important;
            line-height: .88 !important;
        }
        .rg-brand-sub {
            font-family: "IBM Plex Mono", monospace !important;
            font-size: .58rem !important;
            letter-spacing: .19em !important;
        }
        .rg-hero {
            min-height: 320px;
            padding: 2.3rem 2.25rem 2.1rem;
            background:
                linear-gradient(112deg, rgba(255,255,255,.98) 0%, rgba(248,247,242,.96) 56%, rgba(225,228,222,.88) 100%);
        }
        .rg-hero:after {
            content: "RG / 09";
            position: absolute;
            right: 15%;
            bottom: -2.1rem;
            color: rgba(23,25,27,.045);
            font: 900 clamp(7rem,15vw,13rem)/.8 "Barlow Condensed", Impact, sans-serif;
            letter-spacing: -.075em;
            pointer-events: none;
            z-index: 0;
        }
        .rg-hero > div:first-child { position:relative; z-index:1; }
        .rg-hero h1 {
            margin: .65rem 0 .55rem !important;
            font-size: clamp(4.1rem, 7.8vw, 7.7rem) !important;
            line-height: .79 !important;
            letter-spacing: -.055em !important;
            font-weight: 900 !important;
            text-transform: uppercase;
            max-width: 850px;
        }
        .rg-hero h1 em {
            color: #718b43 !important;
            font-style: italic;
            letter-spacing: -.065em;
            white-space: nowrap;
        }
        .rg-hero p {
            max-width: 590px;
            font-size: .92rem;
            line-height: 1.62;
            letter-spacing: -.012em;
        }
        .rg-kicker {
            font-family: "IBM Plex Mono", monospace !important;
            font-size: .67rem !important;
            letter-spacing: .2em !important;
            font-weight: 700 !important;
        }
        .rg-section-title {
            font-size: 2.05rem !important;
            line-height: .95;
            letter-spacing: -.035em !important;
        }
        .rg-section-copy {
            font-size: .82rem !important;
            max-width: 680px;
        }
        .rg-panel-title {
            font-size: 1.35rem !important;
            line-height: .95;
            letter-spacing: -.015em !important;
        }
        .rg-stat-value {
            font-size: 2.65rem !important;
            line-height: .9;
            letter-spacing: -.025em !important;
        }
        .rg-stat-label, .rg-stat-note, .rg-panel-tag,
        .rg-table th, .rg-pill, .rg-bar-label, .rg-bar-count,
        .rg-top-label, .rg-context, .rg-footer,
        .rg-live, .rg-safety b {
            font-family: "IBM Plex Mono", monospace !important;
        }
        .rg-stat-label {
            font-size: .63rem !important;
            letter-spacing: .15em !important;
        }
        .rg-table th {
            font-size: .61rem !important;
            letter-spacing: .12em !important;
        }
        [data-testid="stTabs"] button[role="tab"] {
            font-family: "Barlow Condensed", Impact, sans-serif !important;
            font-size: 1.02rem !important;
            font-weight: 800 !important;
            letter-spacing: .035em !important;
        }
        [data-testid="stMetricValue"] {
            font-family: "Barlow Condensed", Impact, sans-serif !important;
            font-size: 2.55rem !important;
            font-weight: 900 !important;
        }
        [data-testid="stMetricLabel"] p {
            font-family: "IBM Plex Mono", monospace !important;
            letter-spacing: .14em !important;
        }
        .rg-detail-title {
            font-size: 1.85rem !important;
            line-height: .95;
            letter-spacing: -.03em !important;
        }
        .rg-node {
            font-family: "Space Grotesk", sans-serif !important;
            font-size: .76rem;
            font-weight: 700;
        }
        .rg-feature strong {
            font-family: "Barlow Condensed", Impact, sans-serif !important;
            font-size: 1.12rem !important;
            text-transform: uppercase;
            letter-spacing: .015em;
        }
        @media (max-width: 900px) {
            .rg-hero { min-height: 0; padding: 1.7rem 1.3rem; }
            .rg-hero h1 { font-size: clamp(3.4rem, 12vw, 5.5rem) !important; }
            .rg-hero h1 em { white-space: normal; }
            .rg-hero:after { right: 3%; font-size: 7rem; }
        }

        .rg-hero {
            grid-template-columns: minmax(0, 1fr) minmax(145px, .34fr) !important;
        }
        .rg-hero h1 {
            font-size: clamp(3.15rem, 5.1vw, 5.65rem) !important;
            line-height: .9 !important;
            max-width: 100% !important;
            overflow-wrap: normal !important;
        }
        .rg-hero h1 span, .rg-hero h1 em {
            display: block !important;
            white-space: normal !important;
        }
        .rg-hero h1 em {
            font-size: .92em;
            letter-spacing: -.055em !important;
        }
        .rg-auth-intro {
            min-height: 440px; display:flex; flex-direction:column; justify-content:center;
            background:linear-gradient(135deg,#17191b 0%,#252a2c 64%,#39443a 100%);
            color:#f8f7f2; border:1.5px solid #17191b; box-shadow:8px 8px 0 #17191b;
            padding:clamp(1.5rem,4vw,3.2rem); position:relative; overflow:hidden;
        }
        .rg-auth-intro:after {
            content:"RG /"; position:absolute; right:-1rem; bottom:-3rem;
            color:rgba(255,255,255,.055); font:900 clamp(8rem,17vw,15rem)/.8 "Barlow Condensed",Impact,sans-serif;
            pointer-events:none;
        }
        .rg-auth-kicker {
            color:#c9f36a; font:700 .66rem "IBM Plex Mono",monospace;
            letter-spacing:.18em; text-transform:uppercase;
        }
        .rg-auth-title {
            position:relative; z-index:1; margin:1.1rem 0 .9rem;
            color:#f8f7f2; font:900 clamp(3.4rem,6vw,6.2rem)/.82 "Barlow Condensed",Impact,sans-serif;
            letter-spacing:-.035em; text-transform:uppercase;
        }
        .rg-auth-title em { color:#c9f36a; font-style:italic; }
        .rg-auth-copy { max-width:430px; color:#c2c6c4; line-height:1.65; font-size:.88rem; }
        .rg-auth-stamp {
            position:relative; z-index:1; margin-top:2.2rem; padding-top:.8rem;
            border-top:1px solid #50575a; color:#aeb5b2;
            font:600 .61rem "IBM Plex Mono",monospace; letter-spacing:.14em;
        }
        .rg-auth-heading {
            color:#17191b; font:900 2.1rem/.95 "Barlow Condensed",Impact,sans-serif;
            text-transform:uppercase; letter-spacing:-.02em; margin:.2rem 0 .45rem;
        }
        .rg-auth-sub { color:#757a7c; font-size:.78rem; line-height:1.55; margin-bottom:1.3rem; }
        [data-testid="stForm"] {
            background:#f8f7f2; border:1.5px solid #25282b; border-radius:2px;
            padding:1.35rem 1.35rem 1.1rem; box-shadow:6px 6px 0 rgba(23,25,27,.18);
        }
        .rg-auth-footnote {
            color:#747a7b; font:600 .6rem/1.6 "IBM Plex Mono",monospace;
            letter-spacing:.035em; margin-top:1rem;
        }
        @media (max-width: 900px) {
            .rg-auth-intro { min-height:300px; }
            .rg-auth-title { font-size:clamp(3.4rem,13vw,5.2rem); }
            .rg-hero { grid-template-columns:1fr !important; }
            .rg-hero h1 { font-size:clamp(3.2rem,10vw,5rem) !important; }
        }

        /* Explicit typography coverage for Streamlit's separately rendered sidebar. */
        [data-testid="stSidebar"],
        [data-testid="stSidebar"] * {
            font-family: "Space Grotesk", "Helvetica Neue", Arial, sans-serif !important;
        }
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] h4,
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] strong {
            font-family: "Barlow Condensed", Impact, "Arial Narrow", sans-serif !important;
            font-weight: 800 !important;
            letter-spacing: .015em !important;
            text-transform: uppercase;
        }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] input,
        [data-testid="stSidebar"] button,
        [data-testid="stSidebar"] [data-baseweb="select"] {
            font-family: "Space Grotesk", "Helvetica Neue", Arial, sans-serif !important;
        }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] strong {
            font-size: 1.08rem !important;
        }
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
            font-size: .72rem !important;
            line-height: 1.55 !important;
            letter-spacing: .015em !important;
        }
        [data-testid="stSidebar"] label {
            font-size: .76rem !important;
            font-weight: 600 !important;
            letter-spacing: .01em !important;
        }
        [data-testid="stSidebar"] [data-testid="stButton"] button {
            font-family: "Barlow Condensed", Impact, sans-serif !important;
            font-size: 1.12rem !important;
            font-weight: 800 !important;
            letter-spacing: .06em !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def esc(value):
    return html.escape(str(value if value is not None else ""))


def section(kicker, title, copy=""):
    st.markdown(
        f'<div class="rg-section"><div class="rg-kicker">{esc(kicker)}</div>'
        f'<div class="rg-section-title">{esc(title)}</div>'
        f'<div class="rg-section-copy">{esc(copy)}</div></div>',
        unsafe_allow_html=True,
    )


def table(headers, rows, empty="No records to display."):
    if not rows:
        st.caption(empty)
        return
    head = "".join(f"<th>{esc(h)}</th>" for h in headers)
    body = "".join(
        "<tr>" + "".join(f'<td>{esc(value)}</td>' for value in row) + "</tr>"
        for row in rows
    )
    st.markdown(
        f'<div style="overflow-x:auto"><table class="rg-table"><thead><tr>{head}</tr></thead>'
        f"<tbody>{body}</tbody></table></div>",
        unsafe_allow_html=True,
    )


def pill(value, kind="neutral"):
    return f'<span class="rg-pill {esc(kind)}">{esc(value)}</span>'


def severity_kind(value):
    return str(value).lower() if str(value).lower() in {"critical", "high", "medium", "low"} else "neutral"


def metric_grid(items):
    cards = []
    for label, value, note in items:
        cards.append(
            f'<div class="rg-stat"><div class="rg-stat-label">{esc(label)}</div>'
            f'<div class="rg-stat-value">{esc(value)}</div>'
            f'<div class="rg-stat-note">{esc(note)}</div></div>'
        )
    st.markdown('<div class="rg-stat-grid">' + "".join(cards) + "</div>", unsafe_allow_html=True)


def distribution_panel(findings):
    order = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    counts = {level: sum(f["severity"] == level for f in findings) for level in order}
    maximum = max(counts.values(), default=0) or 1
    rows = []
    for level in order:
        width = int(counts[level] / maximum * 100) if counts[level] else 0
        rows.append(
            f'<div class="rg-bar-row"><div class="rg-bar-label">{level}</div>'
            f'<div class="rg-bar-track"><div class="rg-bar-fill {level.lower()}" style="width:{width}%"></div></div>'
            f'<div class="rg-bar-count">{counts[level]}</div></div>'
        )
    st.markdown('<div class="rg-panel"><div class="rg-panel-head"><div class="rg-panel-title">Severity index</div>'
                '<div class="rg-panel-tag">FINDINGS / LEVEL</div></div>'
                + "".join(rows) +
                '<div class="rg-note">Distribution reflects the currently loaded synthetic scenario.</div></div>',
                unsafe_allow_html=True)


def relationship_panel(relationships):
    if not relationships:
        st.info("This scenario has no relationship edges.")
        return
    rows = []
    for item in relationships:
        rows.append(
            '<div class="rg-relationship">'
            f'<div class="rg-node">{esc(item["source_principal"])}</div>'
            f'<div class="rg-edge">{esc(item["relationship_type"])}</div>'
            f'<div class="rg-node">{esc(item["target_principal"])}</div></div>'
        )
    st.markdown(
        '<div class="rg-panel"><div class="rg-panel-head"><div class="rg-panel-title">Trust-path assertions</div>'
        '<div class="rg-panel-tag">FIXTURE GRAPH</div></div>'
        + "".join(rows)
        + '<div class="rg-note">Relationship edges are synthetic fixture assertions, not independently discovered trust paths.</div></div>',
        unsafe_allow_html=True,
    )


def finding_rows(items):
    return [
        [f["finding_id"], f["severity"], f["status"], f["rule_id"], f["principal"]]
        for f in items
    ]


inject_theme()
local_auth.initialize_auth()
effects_path = Path(__file__).with_name("assets") / "rogueguard-effects.html"
st.html(effects_path, unsafe_allow_javascript=True)

if not st.session_state.get("rg_auth_user"):
    render_auth_screen()
    st.stop()

rg.initialize_prototype()
available = rg.available_scenarios()
loaded = rg.list_scenarios()

if not available:
    st.error("No synthetic scenario fixtures were found in fixtures/scenarios.")
    st.stop()

available_ids = {x["scenario_id"] for x in available}
if "rg_scenario_id" not in st.session_state or st.session_state.rg_scenario_id not in available_ids:
    st.session_state.rg_scenario_id = loaded[0]["scenario_id"] if loaded else available[0]["scenario_id"]

with st.sidebar:
    st.markdown(
        '<div class="rg-sidebar-brand"><span class="rg-sidebar-brand-name">ROGU<span style="color:#c9f36a">E</span>GUARD</span>'
        '<span class="rg-sidebar-brand-sub">IDENTITY SECURITY / V0.9</span></div>',
        unsafe_allow_html=True,
    )
    st.divider()
    st.markdown("**WORKSPACE CONTROL**")
    selected_scenario = st.selectbox(
        "Scenario fixture",
        options=[x["scenario_id"] for x in available],
        index=[x["scenario_id"] for x in available].index(st.session_state.rg_scenario_id),
        format_func=lambda sid: next(x["name"] for x in available if x["scenario_id"] == sid),
    )
    loaded_ids = {x["scenario_id"] for x in rg.list_scenarios()}
    if st.button("LOAD / ANALYSE SCENARIO", type="primary", use_container_width=True):
        try:
            if selected_scenario not in loaded_ids:
                info = rg.load_scenario(selected_scenario)
                st.success(f"Loaded {info['name']}")
            results = rg.analyze_scenario(selected_scenario)
            st.session_state.rg_scenario_id = selected_scenario
            st.session_state.rg_selected_finding = None
            st.success(f"Analysis complete: {len(results)} findings.")
            st.rerun()
        except Exception as exc:
            st.error(str(exc))
    st.divider()
    st.markdown("**SIMULATION BOUNDARY**")
    st.caption("Synthetic identities, bindings, approvals and evidence only.")
    st.caption("Response actions affect the local SQLite model only.")
    st.caption("Hash manifests detect changes; they are not immutable storage.")
    st.markdown(
        '<div style="margin-top:1.2rem;padding:.7rem;border:1px solid #565b5e;background:#202326">'
        '<div style="font:800 .58rem ui-monospace,monospace;letter-spacing:.13em;color:#c9f36a">ENVIRONMENT</div>'
        '<div style="font-size:.78rem;font-weight:800;margin-top:.25rem">LOCAL / SYNTHETIC</div></div>',
        unsafe_allow_html=True,
    )
    st.divider()
    st.caption(f"AUTHENTICATED OPERATOR / {st.session_state.get('rg_auth_user', 'unknown')}")
    if st.button("SIGN OUT", use_container_width=True, key="rg_sign_out"):
        local_auth.clear_auth_state(st.session_state)
        st.rerun()

sid = st.session_state.rg_scenario_id
loaded_now = {x["scenario_id"] for x in rg.list_scenarios()}
if sid not in loaded_now:
    try:
        rg.load_scenario(sid)
    except Exception as exc:
        st.error(f"Could not load scenario: {exc}")
        st.stop()

if not rg.list_findings(sid):
    rg.analyze_scenario(sid)

summary = rg.dashboard_summary(sid)
scenario_record = next((x for x in rg.list_scenarios() if x["scenario_id"] == sid), {})
findings = rg.list_findings(sid)
identities = rg.list_identities(sid)
cases = rg.list_cases(sid)
open_findings = sum(f["status"] not in {"RESOLVED", "RETESTED", "FALSE_POSITIVE"} for f in findings)

st.markdown(
    '<div class="rg-masthead"><div class="rg-brand"><div class="rg-mark">RG/</div>'
    '<div><div class="rg-brand-name">ROGUEGUARD</div><div class="rg-brand-sub">IDENTITY EXPOSURE / PERMISSION INTELLIGENCE</div></div></div>'
    '<div class="rg-top-right"><div class="rg-top-label">SECURITY OPERATIONS CONSOLE</div><div class="rg-live">LOCAL SIMULATION</div></div></div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="rg-hero"><div><div class="rg-kicker">IDENTITY SECURITY WORKBENCH / 0.9</div>'
    '<h1><span>SEE THE ACCESS.</span><em>CONTROL THE EXPOSURE.</em></h1>'
    '<p>Investigate identity posture, understand permission drift, and validate response decisions through a controlled synthetic workflow.</p></div>'
    '<div class="rg-chrome-wrap"><div class="rg-chrome"></div></div></div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="rg-safety"><b>SIMULATION ONLY</b><span>This workbench does not connect to or modify Google Cloud IAM, credentials, storage, secrets, or production resources.</span></div>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<div class="rg-context"><span>ACTIVE SCENARIO <strong>{esc(scenario_record.get("name", sid))}</strong></span>'
    f'<span>FIXTURE VERSION <strong>{esc(scenario_record.get("version", "unknown"))}</strong></span>'
    '<span>DATA CLASS <strong>SYNTHETIC DEMO</strong></span></div>',
    unsafe_allow_html=True,
)

overview, identities_tab, findings_tab, response_tab, cases_tab = st.tabs([
    "01  /  OVERVIEW", "02  /  IDENTITIES", "03  /  FINDINGS",
    "04  /  RESPONSE LAB", "05  /  CASES + EVIDENCE",
])

with overview:
    section("01 / SITUATION REPORT", "Security overview", "A compact readout of identity exposure across the active scenario.")
    metric_grid([
        ("IDENTITIES", summary["identities"], f'{summary["active"]} active / {summary["quarantined"]} quarantined'),
        ("OPEN FINDINGS", open_findings, f'{len(findings)} total detections'),
        ("CRITICAL", summary["critical"], "Highest severity"),
        ("HIGH", summary["high"], "Elevated severity"),
    ])
    st.write("")
    left, right = st.columns([.88, 1.12], gap="large")
    with left:
        distribution_panel(findings)
    with right:
        st.markdown(
            '<div class="rg-panel"><div class="rg-panel-head"><div class="rg-panel-title">Priority queue</div>'
            f'<div class="rg-panel-tag">{len(findings)} RECORDS</div></div>',
            unsafe_allow_html=True,
        )
        if findings:
            queue = sorted(findings, key=lambda f: (["CRITICAL", "HIGH", "MEDIUM", "LOW"].index(f["severity"])
                                                     if f["severity"] in ["CRITICAL", "HIGH", "MEDIUM", "LOW"] else 9,
                                                     f["finding_id"]))[:8]
            table(["FINDING ID", "SEVERITY", "STATE", "RULE", "IDENTITY"],
                  finding_rows(queue))
        else:
            st.caption("No findings. Run analysis or load another scenario.")
        st.markdown("</div>", unsafe_allow_html=True)
    st.write("")
    section("02 / RELATIONSHIP CONTEXT", "Identity relationship map", "A simplified view of declared fixture relationships. These are not live-discovered trust paths.")
    relationship_panel(rg.list_relationships(sid))
    st.write("")
    left, right = st.columns([1, 1], gap="large")
    with left:
        st.markdown(
            '<div class="rg-panel"><div class="rg-panel-head"><div class="rg-panel-title">Response lifecycle</div>'
            '<div class="rg-panel-tag">CONTROL SEQUENCE</div></div>'
            '<div class="rg-feature"><strong>01 / Investigate</strong><span>Review identity and finding evidence</span></div>'
            '<div class="rg-feature"><strong>02 / Plan</strong><span>Generate a before / after dry-run</span></div>'
            '<div class="rg-feature"><strong>03 / Approve</strong><span>Record an independent reviewer decision</span></div>'
            '<div class="rg-feature"><strong>04 / Verify</strong><span>Compare actual state to reviewed target</span></div></div>',
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(
            '<div class="rg-panel"><div class="rg-panel-head"><div class="rg-panel-title">Prototype boundary</div>'
            '<div class="rg-panel-tag">READ BEFORE DEMO</div></div>'
            '<div class="rg-feature"><strong>Execution</strong><span>Local SQLite simulation only</span></div>'
            '<div class="rg-feature"><strong>Approval</strong><span>Distinct reviewer label; no real authentication</span></div>'
            '<div class="rg-feature"><strong>Evidence</strong><span>Exported JSON / CSV with SHA-256 manifest</span></div>'
            '<div class="rg-feature"><strong>Cloud integration</strong><span>Not implemented or claimed</span></div></div>',
            unsafe_allow_html=True,
        )

with identities_tab:
    section("02 / INVENTORY", "Identity explorer", "Inspect identity ownership, declared intent, lifecycle and resource-level access.")
    if identities:
        principal = st.selectbox("SELECT IDENTITY", [x["principal"] for x in identities], key="rg_identity")
        identity = rg.get_identity(sid, principal)
        if identity:
            baseline = identity["baseline"] or {}
            st.markdown(
                f'<div class="rg-detail"><div class="rg-kicker">IDENTITY RECORD / {esc(identity["identity_type"])}</div>'
                f'<div class="rg-detail-title">{esc(principal)}</div>'
                f'<div class="rg-detail-sub">{esc(identity.get("purpose") or "Purpose not documented")}</div></div>',
                unsafe_allow_html=True,
            )
            a, b, c = st.columns(3)
            a.metric("Lifecycle", identity["lifecycle_state"])
            b.metric("Resource bindings", len(identity["bindings"]))
            c.metric("Baseline approval", baseline.get("approval_state", "MISSING"))
            left, right = st.columns([1, 1], gap="large")
            with left:
                st.markdown('<div class="rg-panel"><div class="rg-panel-title">Ownership & context</div>', unsafe_allow_html=True)
                table(["ATTRIBUTE", "VALUE"], [
                    ["Owner", identity.get("owner") or "Unassigned"],
                    ["Identity type", identity["identity_type"]],
                    ["Environment", identity["environment"]],
                    ["Last observed", identity.get("last_observed_at") or "Unknown"],
                    ["Review due", identity.get("review_due_at") or "Not set"],
                ])
                st.markdown("</div>", unsafe_allow_html=True)
            with right:
                st.markdown('<div class="rg-panel"><div class="rg-panel-title">Declared baseline</div>', unsafe_allow_html=True)
                table(["ATTRIBUTE", "VALUE"], [
                    ["Version", baseline.get("version", "n/a")],
                    ["Rationale", baseline.get("rationale") or "No rationale supplied"],
                    ["Required roles", ", ".join(baseline.get("required_roles", [])) or "None"],
                ])
                st.markdown("</div>", unsafe_allow_html=True)
            st.write("")
            st.markdown('<div class="rg-panel"><div class="rg-panel-head"><div class="rg-panel-title">Resource-level bindings</div>'
                        f'<div class="rg-panel-tag">{len(identity["bindings"])} BINDINGS</div></div>', unsafe_allow_html=True)
            table(["ROLE", "RESOURCE", "SCOPE", "SENSITIVITY", "SOURCE", "CONDITION", "INHERITED"], [
                [x["role"], x["resource_name"], x["resource_type"], x["sensitivity"],
                 x["source"], x["condition"] or "None", "YES" if x["inherited"] else "NO"]
                for x in identity["bindings"]
            ], empty="No bindings are recorded for this identity.")
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No identities are available in this scenario.")

with findings_tab:
    section("03 / DETECTION", "Finding inbox", "Filter, triage and group synthetic detection results into an investigation case.")
    filter_row = st.columns(4)
    status_options = ["ALL", "NEW", "TRIAGED", "ACCEPTED", "FALSE_POSITIVE",
                      "REMEDIATION_PLANNED", "CONTAINED", "RESOLVED", "RETESTED"]
    chosen_status = filter_row[0].selectbox("STATE", status_options)
    severity_options = ["ALL", "CRITICAL", "HIGH", "MEDIUM", "LOW"]
    chosen_severity = filter_row[1].selectbox("SEVERITY", severity_options)
    owners = sorted({i.get("owner") or "Unassigned" for i in identities})
    chosen_owner = filter_row[2].selectbox("OWNER", ["ALL"] + owners)
    search_text = filter_row[3].text_input("SEARCH IDENTITY / RULE")
    visible = findings
    if chosen_status != "ALL":
        visible = [f for f in visible if f["status"] == chosen_status]
    if chosen_severity != "ALL":
        visible = [f for f in visible if f["severity"] == chosen_severity]
    if chosen_owner != "ALL":
        owner_lookup = {i["principal"]: i.get("owner") or "Unassigned" for i in identities}
        visible = [f for f in visible if owner_lookup.get(f["principal"], "Unassigned") == chosen_owner]
    if search_text.strip():
        term = search_text.strip().casefold()
        visible = [f for f in visible if term in f["principal"].casefold()
                   or term in f["rule_id"].casefold() or term in f["title"].casefold()]
    st.caption(f"Showing {len(visible)} of {len(findings)} findings.")
    if visible:
        table(["FINDING ID", "SEVERITY", "STATE", "RULE", "IDENTITY"], finding_rows(visible))
        finding_ids = [f["finding_id"] for f in visible]
        selected_fid = st.selectbox(
            "INSPECT FINDING", finding_ids,
            format_func=lambda fid: next(
                f'{x["severity"]}  /  {x["title"]}  /  {x["principal"]}'
                for x in visible if x["finding_id"] == fid
            ),
        )
        detail = next(x for x in visible if x["finding_id"] == selected_fid)
        st.markdown(
            f'<div class="rg-detail"><div class="rg-kicker">{esc(detail["rule_id"])} / {esc(detail["finding_id"])}</div>'
            f'<div class="rg-detail-title">{esc(detail["title"])}</div>'
            f'<div class="rg-detail-sub">{esc(detail["description"])}</div></div>',
            unsafe_allow_html=True,
        )
        d1, d2, d3 = st.columns(3)
        d1.metric("Severity", detail["severity"])
        d2.metric("Evidence confidence", detail["confidence"])
        d3.metric("Workflow state", detail["status"])
        left, right = st.columns([1, 1], gap="large")
        with left:
            st.markdown("**RECOMMENDATION**")
            st.write(detail["recommendation"])
        with right:
            st.markdown("**EVIDENCE SNAPSHOT**")
            with st.expander("Inspect structured evidence"):
                st.json(detail["evidence"])
        with st.expander("Decision history"):
            history = rg.list_finding_history(selected_fid)
            table(["ACTOR", "FROM", "TO", "REASON", "TIMESTAMP"], [
                [h["actor"], h["old_status"], h["new_status"], h["reason"], h["created_at"]]
                for h in history
            ], empty="No analyst state changes recorded yet.")
        allowed = sorted(rg.FINDING_TRANSITIONS.get(detail["status"], set()))
        if allowed:
            st.markdown("#### Update finding state")
            with st.form("finding_transition_form"):
                c1, c2 = st.columns(2)
                next_state = c1.selectbox("MOVE TO", allowed)
                actor = c2.text_input("ANALYST", value="analyst")
                reason = st.text_input("REASON FOR STATE CHANGE")
                submitted = st.form_submit_button("UPDATE FINDING STATE")
            if submitted:
                try:
                    rg.update_finding_status(selected_fid, next_state, actor, reason)
                    st.success("Finding state updated.")
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))
        else:
            st.caption("No further state transition is available from this state.")
        st.divider()
        section("CASE MANAGEMENT", "Create investigation case", "Group related findings so the response workflow and evidence remain linked.")
        selected_for_case = st.multiselect(
            "FINDINGS TO INCLUDE",
            [x["finding_id"] for x in findings if x["status"] not in {"FALSE_POSITIVE", "RETESTED"}],
            default=[selected_fid],
            format_func=lambda fid: next(
                f'{x["severity"]}  /  {x["title"]}' for x in findings if x["finding_id"] == fid
            ),
        )
        with st.form("create_case_form"):
            c1, c2 = st.columns(2)
            title = c1.text_input("CASE TITLE", value=f'Review: {detail["principal"]}')
            creator = c2.text_input("CASE CREATOR", value="analyst")
            create_submitted = st.form_submit_button("CREATE CASE")
        if create_submitted:
            try:
                case_id = rg.create_case(sid, title, creator, selected_for_case)
                st.success(f"Created {case_id}")
            except Exception as exc:
                st.error(str(exc))
    else:
        st.info("No findings match the selected filters.")

with response_tab:
    section("04 / CONTROL", "Response planning lab", "Generate a dry-run, require independent review, simulate the action and verify the resulting state.")
    st.markdown(
        '<div class="rg-safety"><b>LOCAL EXECUTION</b><span>Approval and execution below change the synthetic SQLite model only. They do not change cloud permissions.</span></div>',
        unsafe_allow_html=True,
    )
    cases = rg.list_cases(sid)
    if not cases:
        st.info("Create a case from one or more findings before planning a response.")
    else:
        case_ids = [x["case_id"] for x in cases]
        chosen_case = st.selectbox(
            "SELECT CASE", case_ids,
            format_func=lambda cid: next(
                f'{x["case_id"]}  /  {x["title"]}  /  {x["status"]}' for x in cases if x["case_id"] == cid
            ), key="response_case"
        )
        case = rg.get_case(chosen_case)
        case_principals = sorted({f["principal"] for f in case["findings"]})
        if not case_principals:
            case_principals = [x["principal"] for x in identities]
        with st.form("create_plan_form"):
            target = st.selectbox("TARGET IDENTITY", case_principals)
            action_options = ["REMOVE_EXCESS", "QUARANTINE"] + (
                ["REACTIVATE"] if rg.get_identity(sid, target)["lifecycle_state"] == "QUARANTINED" else []
            )
            action = st.selectbox(
                "RESPONSE ACTION", action_options,
                format_func=lambda x: {
                    "REMOVE_EXCESS": "Remove excess permissions only",
                    "QUARANTINE": "Quarantine identity only",
                    "REACTIVATE": "Reactivate after remediation only",
                }[x],
            )
            reason = st.text_area("OPERATOR REASON", placeholder="Explain why this simulated action is appropriate.")
            creator = st.text_input("PLAN CREATOR", value="analyst")
            plan_submitted = st.form_submit_button("GENERATE DRY-RUN PLAN")
        if plan_submitted:
            try:
                related_ids = [f["finding_id"] for f in case["findings"] if f["principal"] == target]
                plan_id = rg.create_action_plan(chosen_case, target, action, reason, creator, related_ids)
                st.session_state.rg_plan_id = plan_id
                st.success(f"Dry-run plan created: {plan_id}")
                st.rerun()
            except Exception as exc:
                st.error(str(exc))
        plans = rg.list_plans(chosen_case)
        if plans:
            plan_ids = [p["plan_id"] for p in plans]
            default_plan = st.session_state.get("rg_plan_id")
            index = plan_ids.index(default_plan) if default_plan in plan_ids else 0
            chosen_plan = st.selectbox("REVIEW EXISTING PLAN", plan_ids, index=index, key="review_plan")
            plan = rg.get_plan(chosen_plan)
            st.markdown(
                f'<div class="rg-detail"><div class="rg-kicker">ACTION PLAN / {esc(plan["plan_id"])}</div>'
                f'<div class="rg-detail-title">{esc(plan["action_type"])}</div>'
                f'<div class="rg-detail-sub">STATUS: {esc(plan["status"])} &nbsp; / &nbsp; CREATED BY: {esc(plan["created_by"])}</div>'
                f'<div class="rg-detail-sub">RATIONALE: {esc(plan["reason"])}</div></div>',
                unsafe_allow_html=True,
            )
            def binding_rows(snapshot):
                return [[b["role"], b["resource_id"], b["source"], b.get("condition") or "None"]
                        for b in snapshot["bindings"]]
            before, after = st.columns(2, gap="large")
            with before:
                st.markdown('<div class="rg-panel"><div class="rg-panel-title">01 / BEFORE STATE</div>', unsafe_allow_html=True)
                st.metric("Bindings", len(plan["before"]["bindings"]))
                table(["ROLE", "RESOURCE", "SOURCE", "CONDITION"], binding_rows(plan["before"]))
                st.markdown("</div>", unsafe_allow_html=True)
            with after:
                st.markdown('<div class="rg-panel"><div class="rg-panel-title">02 / PROPOSED STATE</div>', unsafe_allow_html=True)
                st.metric("Bindings", len(plan["after"]["bindings"]))
                table(["ROLE", "RESOURCE", "SOURCE", "CONDITION"], binding_rows(plan["after"]))
                st.markdown("</div>", unsafe_allow_html=True)
            changed_bindings = len(plan["before"]["bindings"]) - len(plan["after"]["bindings"])
            if plan["action_type"] == "QUARANTINE":
                st.info("Impact preview: identity lifecycle state changes to QUARANTINED; role bindings remain unchanged.")
            elif plan["action_type"] == "REACTIVATE":
                st.info("Impact preview: identity lifecycle state changes to ACTIVE; no permissions are restored.")
            else:
                st.info(f"Impact preview: {max(changed_bindings, 0)} binding(s) will be removed in the local simulator.")
            if plan["status"] == "PENDING_APPROVAL":
                st.markdown("#### Independent review")
                with st.form("approval_form"):
                    c1, c2 = st.columns(2)
                    reviewer = c1.text_input("REVIEWER (MUST DIFFER FROM CREATOR)", value="reviewer")
                    decision = c2.selectbox("DECISION", ["APPROVED", "REJECTED"])
                    approval_reason = st.text_input("REVIEW RATIONALE")
                    approval_submitted = st.form_submit_button("RECORD REVIEW DECISION")
                if approval_submitted:
                    try:
                        rg.approve_action_plan(chosen_plan, reviewer, decision, approval_reason)
                        st.success(f"Plan {decision.lower()}.")
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))
            elif plan["status"] == "APPROVED":
                operator = st.text_input("EXECUTION OPERATOR", value="operator", key="execute_actor")
                execution_confirmed = st.checkbox(
                    "I reviewed the before / after diff and approve this local simulation action.",
                    key=f"execution_confirm_{chosen_plan}",
                )
                if st.button("EXECUTE SIMULATED ACTION", type="primary", disabled=not execution_confirmed):
                    try:
                        rg.execute_action_plan(chosen_plan, operator)
                        st.success("Local simulation action executed.")
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))
            elif plan["status"] == "EXECUTED":
                verifier = st.text_input("VERIFIER", value="verifier", key="verify_actor")
                if st.button("VERIFY POST-ACTION STATE", type="primary"):
                    try:
                        result = rg.verify_action_plan(chosen_plan, verifier)
                        st.success(f'Verification: {result["result"]}')
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))
            elif plan["status"] in {"VERIFIED", "FAILED", "REJECTED"}:
                st.info(f'Plan finalised with status: {plan["status"]}')
            if plan["approvals"]:
                st.markdown("#### Approval history")
                table(["REVIEWER", "DECISION", "RATIONALE", "TIMESTAMP"], [
                    [a["reviewer"], a["decision"], a["reason"], a["created_at"]]
                    for a in plan["approvals"]
                ])

with cases_tab:
    section("05 / EVIDENCE", "Cases & evidence", "Track investigation state, inspect response events and export a portable case bundle.")
    cases = rg.list_cases(sid)
    if not cases:
        st.info("No cases have been created for this scenario yet.")
    else:
        selected_case_id = st.selectbox(
            "SELECT CASE", [x["case_id"] for x in cases],
            format_func=lambda cid: next(
                f'{x["case_id"]}  /  {x["title"]}  /  {x["status"]}' for x in cases if x["case_id"] == cid
            ), key="evidence_case"
        )
        case = rg.get_case(selected_case_id)
        metric_grid([
            ("CASE STATE", case["status"], "Investigation lifecycle"),
            ("LINKED FINDINGS", len(case["findings"]), "Evidence references"),
            ("CREATED BY", case["created_by"], "Case owner label"),
            ("TIMELINE EVENTS", len(rg.list_events(selected_case_id)), "Recorded local events"),
        ])
        st.write("")
        st.markdown('<div class="rg-panel"><div class="rg-panel-head"><div class="rg-panel-title">Linked findings</div>'
                    '<div class="rg-panel-tag">CASE CONTENTS</div></div>', unsafe_allow_html=True)
        table(["FINDING ID", "SEVERITY", "STATE", "RULE", "PRINCIPAL", "TITLE"], [
            [f["finding_id"], f["severity"], f["status"], f["rule_id"], f["principal"], f["title"]]
            for f in case["findings"]
        ])
        st.markdown("</div>", unsafe_allow_html=True)
        with st.expander("Case timeline"):
            events = rg.list_events(selected_case_id)
            table(["EVENT", "ACTOR", "ACTION", "DETAIL", "STATUS", "TIMESTAMP"], [
                [e["event_id"], e["actor"], e["event_type"], e["reason"], e["status"], e["created_at"]]
                for e in events
            ], empty="No response events have been recorded yet.")
        c1, c2 = st.columns(2, gap="large")
        with c1:
            st.markdown("#### Case state")
            case_state_options = sorted(rg.CASE_TRANSITIONS.get(case["status"], set()))
            if case_state_options:
                new_case_state = st.selectbox("MOVE CASE TO", case_state_options)
                if st.button("UPDATE CASE STATE"):
                    try:
                        rg.update_case_status(selected_case_id, new_case_state)
                        st.success("Case state updated.")
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))
            else:
                st.caption("This case is closed. Reopen it to continue working.")
        with c2:
            st.markdown("#### Evidence export")
            redact = st.checkbox("Redact sensitive strings in export", value=True)
            if st.button("EXPORT CASE EVIDENCE BUNDLE", type="primary"):
                try:
                    paths = rg.export_case_bundle(selected_case_id, redact=redact)
                    st.session_state.rg_export_paths = paths
                    st.success("Evidence bundle exported. Synthetic simulation notice included.")
                except Exception as exc:
                    st.error(str(exc))
        if st.session_state.get("rg_export_paths"):
            paths = st.session_state.rg_export_paths
            st.markdown("#### Download evidence")
            cols = st.columns(3)
            for col, label, key in zip(
                cols, ["CASE JSON", "FINDINGS CSV", "SHA-256 MANIFEST"],
                ["json", "csv", "manifest"]
            ):
                path = paths.get(key)
                if path and Path(path).exists():
                    with col:
                        st.download_button(
                            label,
                            data=Path(path).read_bytes(),
                            file_name=Path(path).name,
                            mime="application/json" if key != "csv" else "text/csv",
                            key=f"download_{key}",
                            use_container_width=True,
                        )

st.markdown(
    '<div class="rg-footer"><span>ROGUEGUARD / V0.9 FINAL-PROTOTYPE WORKBENCH</span>'
    '<span>SYNTHETIC DATA ONLY</span><span>CLOUD INTEGRATION NOT IMPLEMENTED</span></div>',
    unsafe_allow_html=True,
)
