import streamlit as st

def style_background_home():
    
    st.markdown("""
        <style>
            .stApp, [data-testid="stAppViewContainer"] {
                background: #0E1428 !important;
            }

            /* Custom styling for the cards on the home screen */
            div[data-testid="column"]:has(.card-marker) {
                background-color: #EFEFFA !important;  /* Soft light lavender/gray */
                border-radius: 40px !important;
                padding: 40px 35px !important;
                border: 2px solid #7B9E89 !important; /* Sage green border */
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.35) !important;
                transition: transform 0.3s ease, box-shadow 0.3s ease !important;
            }

            div[data-testid="column"]:has(.card-marker):hover {
                transform: translateY(-8px) !important;
                box-shadow: 0 25px 50px rgba(0, 0, 0, 0.45) !important;
            }

            div[data-testid="column"]:has(.card-marker) > div[data-testid="stVerticalBlock"] {
                align-items: center !important;
                gap: 20px !important;
            }

            /* Card Header text styling */
            .card-header {
                display: flex;
                flex-direction: column;
                align-items: center;
                align-self: center;
                text-align: center;
                font-family: 'Plus Jakarta Sans', sans-serif;
                color: #0E1428;
            }

            .card-sub-header {
                font-size: 1.6rem;
                font-weight: 700;
                line-height: 1.1;
                letter-spacing: -0.02em;
            }

            .card-main-header {
                font-size: 2.8rem;
                font-weight: 800;
                line-height: 1.0;
                margin-top: -4px;
                letter-spacing: -0.03em;
            }

            /* Centering the images */
            div[data-testid="column"]:has(.card-marker) [data-testid="stImage"] {
                display: flex !important;
                justify-content: center !important;
                margin: 15px 0 !important;
            }

            /* Centering the button container */
            div[data-testid="column"]:has(.card-marker) .stButton {
                align-self: center !important;
                width: auto !important;
            }

            /* Portal Button Styling inside cards */
            div[data-testid="column"]:has(.card-marker) .stButton > button {
                background-color: #0E1428 !important; /* Matches page background */
                color: #EFEFFA !important;
                border-radius: 100px !important;
                padding: 12px 28px !important;
                font-weight: 600 !important;
                font-size: 1rem !important;
                border: 2px solid transparent !important;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
                box-shadow: 0 4px 12px rgba(14, 20, 40, 0.15) !important;
            }

            div[data-testid="column"]:has(.card-marker) .stButton > button:hover {
                background-color: #F18805 !important; /* Orange accent on hover */
                color: white !important;
                transform: translateY(-2px) scale(1.02) !important;
                box-shadow: 0 6px 20px rgba(241, 136, 5, 0.4) !important;
            }
            
            /* Footer branding style */
            .footer-branding {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                margin-top: 40px;
                color: #7B9E89; /* Sage Green */
                font-family: 'Inter', sans-serif;
                font-size: 0.9rem;
                font-weight: 500;
            }
            
            .footer-branding span.heart {
                color: #D95D39; /* Terracotta Red-Orange */
                display: inline-block;
                animation: heartbeat 1.5s infinite;
            }
            
            @keyframes heartbeat {
                0% { transform: scale(1); }
                50% { transform: scale(1.15); }
                100% { transform: scale(1); }
            }
        </style>
    """,unsafe_allow_html=True)

    
def style_background_dashboard():
    
    st.markdown("""
        <style>
            .stApp, [data-testid="stAppViewContainer"] {
                background: #E0E3FF !important;
            }
        </style>
    """,unsafe_allow_html=True)


def style_base_layout():
    
    st.markdown("""
        <style>
            /* @import must be the absolute first statement in the style block */
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');
            @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');

            /*HIDE TOOL BAR OF STREAMLIT*/
            #MainMenu, footer, header {
                visibility: hidden !important;
            }
            .block-container {
                padding-top: 1.5rem !important;
            }

            /* Apply font classes / custom variables globally in Streamlit */
            html, body, [class*="css"], .stApp, [data-testid="stAppViewContainer"], p, span, div, h1, h2, h3, h4, h5, h6, button {
                font-family: 'Inter', sans-serif !important;
            }
            h1, h2, h3, h4, h5, h6 {
                font-family: 'Plus Jakarta Sans', sans-serif !important;
            }
            code, pre, .tabular-data, .metric {
                font-family: 'JetBrains Mono', monospace !important;
                font-variant-numeric: tabular-nums !important;
            }

            /* General Button Styling (Primary) */
            .stButton > button, button {
                border-radius: 15rem !important;
                background-color: #F18805 !important; /* Vibrant Orange */
                color: white !important;
                padding: 10px 20px !important;
                border: none !important;
                transition: transform 0.25s ease-in-out, background-color 0.25s !important;
            }
            
            /* Secondary Button Styling */
            .stButton > button[data-testid="baseButton-secondary"], button[kind="Secondary"] {
                border-radius: 15rem !important;
                background-color: #7B9E89 !important; /* Sage Green */
                color: white !important;
                padding: 10px 20px !important;
                border: none !important;
                transition: transform 0.25s ease-in-out, background-color 0.25s !important;
            }
            
            /* Tertiary Button Styling */
            .stButton > button[data-testid="baseButton-tertiary"], button[kind="tertiary"] {
                border-radius: 15rem !important;
                background-color: #0E1428 !important; /* Dark Navy Blue */
                color: white !important;
                padding: 10px 20px !important;
                border: none !important;
                transition: transform 0.25s ease-in-out, background-color 0.25s !important;
            }

            /* Hover micro-animations for responsiveness */
            .stButton > button:hover, button:hover {
                transform: scale(1.05) !important;
                opacity: 0.95 !important;
            }

            /* Custom styling for inputs */
            div[data-testid="stTextInput"] input {
                border-radius: 12px !important;
                background-color: #FFFFFF !important;
                border: 2px solid transparent !important;
                font-size: 1rem !important;
                padding: 12px 18px !important;
                color: #0E1428 !important;
                box-shadow: inset 0 2px 4px rgba(0,0,0,0.03) !important;
                transition: all 0.25s ease !important;
            }
            
            div[data-testid="stTextInput"] input:focus {
                border-color: #F18805 !important; /* Orange Focus Border */
                background-color: #FFFFFF !important;
            }

            /* Style input labels */
            div[data-testid="stTextInput"] label {
                font-family: 'Inter', sans-serif !important;
                font-size: 0.95rem !important;
                font-weight: 600 !important;
                color: #0E1428 !important;
                margin-bottom: 6px !important;
                margin-left: 2px !important;
            }

            /* Style native Streamlit password toggle button to display FontAwesome icons inside a navy circle pill */
            div[data-testid="stTextInput"]:has(input[type="password"]) button,
            div[data-testid="stTextInput"]:has(input[type="text"]) button {
                background-color: #0E1428 !important; /* Dark Navy Blue */
                color: white !important;
                border-radius: 50% !important;
                width: 32px !important;
                height: 32px !important;
                min-height: 32px !important;
                max-height: 32px !important;
                padding: 0 !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                border: none !important;
                box-shadow: 0 2px 6px rgba(14, 20, 40, 0.15) !important;
                transition: all 0.2s ease-in-out !important;
                margin-right: 4px !important;
            }

            div[data-testid="stTextInput"]:has(input[type="password"]) button:hover,
            div[data-testid="stTextInput"]:has(input[type="text"]) button:hover {
                background-color: #F18805 !important; /* Accent orange on hover */
                transform: scale(1.08) !important;
                box-shadow: 0 4px 10px rgba(241, 136, 5, 0.3) !important;
            }

            div[data-testid="stTextInput"] button svg {
                display: none !important; /* Hide native SVGs */
            }

            div[data-testid="stTextInput"] button::before {
                font-family: "Font Awesome 6 Free" !important;
                font-weight: 900 !important;
                color: white !important;
                font-size: 0.95rem !important;
            }

            /* Password hidden -> show eye icon */
            div[data-testid="stTextInput"]:has(input[type="password"]) button::before {
                content: "\f06e" !important; /* fa-eye */
            }

            /* Password shown -> show eye-slash icon */
            div[data-testid="stTextInput"]:has(input[type="text"]) button::before {
                content: "\f070" !important; /* fa-eye-slash */
            }
        </style>
    """,unsafe_allow_html=True)