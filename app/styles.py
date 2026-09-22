"""FinGuard AI - Modern Fintech Glassmorphism Custom Styling"""

CUSTOM_CSS = """
<style>
/* Modern Fonts & Global Reset */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Main background with subtle fintech ambient mesh gradient */
.stApp {
    background: radial-gradient(circle at 10% 20%, rgba(0, 210, 255, 0.05) 0%, transparent 40%),
                radial-gradient(circle at 90% 80%, rgba(112, 0, 255, 0.05) 0%, transparent 40%),
                #080C16;
}

/* Sidebar Custom Styling */
[data-testid="stSidebar"] {
    background: #0B1120 !important;
    border-right: 1px solid rgba(255, 255, 255, 0.07) !important;
}

.nav-section-title {
    font-size: 0.72rem;
    font-weight: 800;
    color: #00D2FF;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin: 14px 0 6px 4px;
    display: flex;
    align-items: center;
    gap: 6px;
}

/* Glassmorphism Cards */
.metric-card {
    background: rgba(19, 28, 46, 0.7);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 18px 20px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    transition: all 0.3s ease;
    margin-bottom: 14px;
}

.metric-card:hover {
    border-color: rgba(0, 210, 255, 0.4);
    transform: translateY(-2px);
    box-shadow: 0 12px 36px 0 rgba(0, 210, 255, 0.15);
}

.metric-title {
    font-size: 0.78rem;
    font-weight: 600;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 6px;
}

.metric-value {
    font-size: 1.7rem;
    font-weight: 800;
    color: #FFFFFF;
    letter-spacing: -0.02em;
    line-height: 1.2;
}

.metric-delta {
    font-size: 0.8rem;
    font-weight: 600;
    margin-top: 6px;
    display: inline-flex;
    align-items: center;
    gap: 4px;
}

.delta-pos {
    color: #10B981;
}

.delta-neg {
    color: #EF4444;
}

.delta-neutral {
    color: #94A3B8;
}

/* Alert & Risk Badges */
.risk-badge {
    display: inline-block;
    padding: 5px 12px;
    border-radius: 9999px;
    font-weight: 700;
    font-size: 0.78rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

.risk-low {
    background: rgba(16, 185, 129, 0.15);
    color: #34D399;
    border: 1px solid rgba(16, 185, 129, 0.4);
}

.risk-moderate {
    background: rgba(245, 158, 11, 0.15);
    color: #FBBF24;
    border: 1px solid rgba(245, 158, 11, 0.4);
}

.risk-high {
    background: rgba(239, 68, 68, 0.15);
    color: #F87171;
    border: 1px solid rgba(239, 68, 68, 0.4);
}

.risk-critical {
    background: rgba(185, 28, 28, 0.25);
    color: #FCA5A5;
    border: 1px solid rgba(239, 68, 68, 0.8);
}

/* Gradient Hero Header */
.hero-header {
    background: linear-gradient(135deg, #00D2FF 0%, #3A7BD5 50%, #7000FF 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
    font-size: 2.1rem;
    letter-spacing: -0.03em;
    margin-bottom: 4px;
}

.hero-subtitle {
    color: #94A3B8;
    font-size: 0.95rem;
    font-weight: 400;
    margin-bottom: 20px;
}

/* Onboarding Hero Box for Fresh Accounts */
.onboarding-hero {
    background: linear-gradient(135deg, rgba(0, 210, 255, 0.08) 0%, rgba(112, 0, 255, 0.08) 100%);
    border: 1px solid rgba(0, 210, 255, 0.25);
    border-radius: 18px;
    padding: 32px 30px;
    margin-bottom: 24px;
}

.onboarding-title {
    font-size: 1.8rem;
    font-weight: 800;
    color: #FFFFFF;
    margin-bottom: 8px;
}

.onboarding-subtitle {
    color: #94A3B8;
    font-size: 1rem;
    line-height: 1.5;
    margin-bottom: 24px;
    max-width: 750px;
}

.action-card {
    background: rgba(19, 28, 46, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 18px 20px;
    transition: all 0.25s ease;
    height: 100%;
}

.action-card:hover {
    border-color: rgba(0, 210, 255, 0.4);
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 210, 255, 0.15);
}

.action-card-title {
    font-weight: 700;
    font-size: 1rem;
    color: #FFFFFF;
    margin-bottom: 6px;
}

.action-card-desc {
    color: #94A3B8;
    font-size: 0.85rem;
    line-height: 1.4;
}

/* X-Ray Risk Card */
.xray-card {
    background: rgba(19, 28, 46, 0.85);
    border-left: 4px solid #00D2FF;
    border-radius: 0 12px 12px 0;
    padding: 18px 20px;
    margin-bottom: 14px;
    border-top: 1px solid rgba(255, 255, 255, 0.05);
    border-right: 1px solid rgba(255, 255, 255, 0.05);
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.xray-warning {
    border-left-color: #F59E0B;
}

.xray-danger {
    border-left-color: #EF4444;
}

.xray-success {
    border-left-color: #10B981;
}

/* Demo Status Pill */
.demo-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(0, 210, 255, 0.12);
    color: #38BDF8;
    border: 1px solid rgba(0, 210, 255, 0.3);
    padding: 6px 14px;
    border-radius: 9999px;
    font-size: 0.82rem;
    font-weight: 600;
    margin-bottom: 14px;
}

/* Chat UI Bubbles */
.chat-msg-user {
    background: rgba(0, 210, 255, 0.15);
    border: 1px solid rgba(0, 210, 255, 0.3);
    border-radius: 14px 14px 2px 14px;
    padding: 12px 16px;
    margin: 8px 0;
    color: #E2E8F0;
    max-width: 85%;
    margin-left: auto;
}

.chat-msg-bot {
    background: rgba(19, 28, 46, 0.9);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px 14px 14px 2px;
    padding: 14px 18px;
    margin: 8px 0;
    color: #CBD5E1;
    max-width: 90%;
}

/* Auth Login & Signup Container */
.auth-box {
    max-width: 480px;
    margin: 20px auto;
    background: rgba(19, 28, 46, 0.8);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(0, 210, 255, 0.2);
    border-radius: 20px;
    padding: 32px 30px;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.5);
}

/* Form & Input Overrides */
div[data-testid="stMetricValue"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

button[kind="primary"] {
    background: linear-gradient(135deg, #00D2FF 0%, #3A7BD5 100%) !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    color: #FFFFFF !important;
    box-shadow: 0 4px 15px rgba(0, 210, 255, 0.3) !important;
    transition: all 0.2s ease !important;
}

button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(0, 210, 255, 0.5) !important;
}
</style>
"""
