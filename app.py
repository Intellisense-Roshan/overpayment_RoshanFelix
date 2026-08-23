"""
The Overpayment Signal - Investigation Prioritization Dashboard

A Streamlit demonstration interface for the Overpayment Signal investigation
prioritization system. This interface reads existing analytical outputs and
presents them for human investigator review.

Decision-support system — human investigation required.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import ast

from src.features.engineer import build_case_features

PROJECT_ROOT = Path(__file__).resolve().parent

# Configure page
st.set_page_config(
    page_title="The Overpayment Signal",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Main container */
    .stApp {
        background-color: #f5f7fa;
        color: #172033;
    }

    .stApp p,
    .stApp li,
    .stApp label,
    [data-testid="stMarkdownContainer"],
    [data-testid="stWidgetLabel"] p,
    [data-testid="stCaptionContainer"] {
        color: #263449 !important;
    }

    [data-testid="stSidebar"] {
        background-color: #e8eef5;
        border-right: 1px solid #c7d2df;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
        color: #172033 !important;
    }

    code {
        color: #123b62 !important;
        background-color: #e8f0f8 !important;
    }

    .main {
        padding: 1.5rem;
    }
    
    /* Header styling */
    .header-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1f3864;
        margin-bottom: 0.3rem;
    }
    
    .header-subtitle {
        font-size: 1.05rem;
        color: #334155;
        margin-bottom: 0.5rem;
    }
    
    .header-disclaimer {
        font-size: 0.95rem;
        color: #334155;
        font-style: italic;
        margin-bottom: 1.5rem;
        padding: 0.75rem 1rem;
        background-color: #f0f2f6;
        border-left: 4px solid #1f3864;
        border-radius: 4px;
    }
    
    /* Metric cards */
    .metric-card {
        background-color: #ffffff;
        padding: 1.25rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        border-top: 4px solid #1f3864;
        text-align: center;
    }
    
    .metric-value {
        font-size: 1.7rem;
        font-weight: 700;
        color: #1f3864;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: #334155;
        margin-top: 0.4rem;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.4rem;
        font-weight: 700;
        color: #1f3864;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #e0e0e0;
        padding-bottom: 0.4rem;
    }
    
    /* Evidence card */
    .evidence-card {
        background-color: #f9f9f9;
        padding: 1.25rem;
        border-radius: 8px;
        border-left: 4px solid #1f3864;
        margin: 0.75rem 0;
    }
    
    /* Governance box */
    .governance-box {
        background-color: #fef5e7;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #f39c12;
        margin: 1rem 0;
    }
    
    /* Summary card */
    .summary-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #475569;
        font-size: 0.85rem;
        margin-top: 2.5rem;
        padding-top: 1.5rem;
        border-top: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DATA LOADING
# ============================================================================

@st.cache_data
def load_worklist():
    """Load the top-20 investigation worklist."""
    path = PROJECT_ROOT / "outputs" / "top20_worklist.csv"
    if not path.exists():
        st.error("❌ outputs/top20_worklist.csv not found. Run the pipeline first.")
        st.stop()
    return pd.read_csv(path)

@st.cache_data
def load_explanations():
    """Load structured case explanations."""
    path = PROJECT_ROOT / "outputs" / "top20_explanations.csv"
    if not path.exists():
        st.error("❌ outputs/top20_explanations.csv not found. Run the pipeline first.")
        st.stop()
    return pd.read_csv(path)

@st.cache_data
def load_fairness():
    """Load fairness audit summary."""
    path = PROJECT_ROOT / "outputs" / "fairness_summary.csv"
    if not path.exists():
        st.error("❌ outputs/fairness_summary.csv not found. Run the pipeline first.")
        st.stop()
    return pd.read_csv(path)

@st.cache_data
def load_source_features():
    """Load read-only source data and derive current signal counts."""
    cases = pd.read_csv(PROJECT_ROOT / "data" / "cases.csv")
    payments = pd.read_csv(PROJECT_ROOT / "data" / "payments.csv")
    return cases, payments, build_case_features(cases, payments)

# Load all data
worklist_df = load_worklist()
explanations_df = load_explanations()
fairness_df = load_fairness()
cases_df, payments_df, source_features_df = load_source_features()
signal_counts = source_features_df['primary_signal'].value_counts()

# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================

st.sidebar.title("Navigation")
st.sidebar.markdown("---")

nav_page = st.sidebar.radio(
    "Select View:",
    [
        "📊 Overview",
        "📋 Investigation Worklist",
        "🔍 Case Investigation",
        "⚖️ Fairness Audit",
        "⚠️ Governance",
        "💡 Day-2 Feedback"
    ],
    index=0
)


st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    **System Status:** `Active`  
    **Prioritization Mode:** `Balanced (50/30/20)`  
    **Target Scope:** `Top-20 Cases`  
    **Execution Engine:** Deterministic CLI  
    """
)

# ============================================================================
# APP HEADER (Rendered across all views)
# ============================================================================

st.markdown('<div class="header-title">THE OVERPAYMENT SIGNAL</div>', unsafe_allow_html=True)
st.markdown('<div class="header-subtitle">Explainable investigation prioritization for human caseworkers</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="header-disclaimer">⚠️ <strong>Decision-Support System:</strong> Identify recurring payment patterns, prioritize limited investigation capacity, and provide traceable evidence for human review. The system does not determine whether a payment was improper.</div>',
    unsafe_allow_html=True
)

# ============================================================================
# PAGE 1: OVERVIEW
# ============================================================================
if nav_page == "📊 Overview":
    st.markdown('<div class="section-header">📊 System Overview & Key Metrics</div>', unsafe_allow_html=True)
    
    # 5 Executive KPI cards
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(
            f'<div class="metric-card"><div class="metric-value">{len(cases_df):,}</div><div class="metric-label">Total Cases Ingested</div></div>',
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f'<div class="metric-card"><div class="metric-value">{len(payments_df):,}</div><div class="metric-label">Total Payments Analyzed</div></div>',
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            f'<div class="metric-card"><div class="metric-value">{len(source_features_df) - int(signal_counts.get("None", 0)):,}</div><div class="metric-label">Total Signal Cases</div></div>',
            unsafe_allow_html=True
        )
    with col4:
        st.markdown(
            f'<div class="metric-card"><div class="metric-value">{len(worklist_df):,}</div><div class="metric-label">Investigation Worklist</div></div>',
            unsafe_allow_html=True
        )
    with col5:
        total_discrepancy = worklist_df['signal_financial_discrepancy'].sum()
        st.markdown(
            f'<div class="metric-card"><div class="metric-value">${total_discrepancy:,.2f}</div><div class="metric-label">Calculated Financial Discrepancy (Top 20)</div></div>',
            unsafe_allow_html=True
        )
        
    st.markdown("<br/>", unsafe_allow_html=True)
    
    # Signal Archetypes Breakdown
    st.markdown('<div class="section-header">🚨 Candidate Signal Archetypes</div>', unsafe_allow_html=True)
    
    col_sig1, col_sig2, col_sig3 = st.columns(3)
    
    with col_sig1:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 1.15rem; font-weight: 700; color: #1f3864;">Post-Closure Continuation</div>
            <div style="font-size: 2.2rem; font-weight: 700; color: #d73027; margin: 0.4rem 0;">{int(signal_counts.get('Post-Closure', 0))}</div>
            <div style="font-size: 0.85rem; color: #666;">Cases with payments issued after case closure</div>
        </div>
        """, unsafe_allow_html=True)

    with col_sig2:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 1.15rem; font-weight: 700; color: #1f3864;">In-Month Duplicate Disbursements</div>
            <div style="font-size: 2.2rem; font-weight: 700; color: #fc8d59; margin: 0.4rem 0;">{int(signal_counts.get('Duplicate', 0))}</div>
            <div style="font-size: 0.85rem; color: #666;">Cases with identical payments in one month</div>
        </div>
        """, unsafe_allow_html=True)

    with col_sig3:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 1.15rem; font-weight: 700; color: #1f3864;">Severe Award Spikes</div>
            <div style="font-size: 2.2rem; font-weight: 700; color: #2b83ba; margin: 0.4rem 0;">{int(signal_counts.get('Award Spike', 0))}</div>
            <div style="font-size: 0.85rem; color: #666;">Cases with payments above 1.5× monthly award</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br/>", unsafe_allow_html=True)
    
    # Compact Top-20 Signal Composition
    st.markdown('<div class="section-header">🥧 Top-20 Worklist Signal Composition</div>', unsafe_allow_html=True)
    
    col_chart, col_summary = st.columns([1.2, 1])
    
    with col_chart:
        top20_signals = worklist_df['primary_signal'].value_counts()
        fig = px.pie(
            values=top20_signals.values,
            names=top20_signals.index,
            color=top20_signals.index,
            color_discrete_map={
                'Award Spike': '#2b83ba',
                'Post-Closure': '#d73027',
                'Duplicate': '#fc8d59'
            },
            hole=0.45
        )
        fig.update_traces(textposition='inside', textinfo='label+value+percent')
        fig.update_layout(
            height=280,
            margin=dict(l=20, r=20, t=20, b=20),
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with col_summary:
        st.markdown(f"""
        <div class="summary-card">
            <h4 style="color: #1f3864; margin-top: 0;">Multi-Criteria Prioritization Highlights</h4>
            <ul style="font-size: 0.9rem; color: #444; line-height: 1.6;">
                <li><strong>100% Persistence:</strong> All 20 selected cases exhibit maximum recurrence across the 6-month observation window.</li>
                <li><strong>Financial Exposure:</strong> Top {len(worklist_df)} accounts for <strong>${total_discrepancy:,.2f}</strong> in calculated financial discrepancy.</li>
                <li><strong>Zero Demographic Scoring:</strong> Demographic fields were strictly excluded from scoring and reserved for post-ranking auditing.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# PAGE 2: INVESTIGATION WORKLIST
# ============================================================================
elif nav_page == "📋 Investigation Worklist":
    st.markdown('<div class="section-header">📋 Prioritized Top-20 Investigation Worklist</div>', unsafe_allow_html=True)
    
    st.markdown(
        """
        The table below lists the 20 cases prioritized for caseworker review based on the 
        **Balanced Multi-Criteria Scoring Model** ($0.50 \\times \\text{Financial} + 0.30 \\times \\text{Persistence} + 0.20 \\times \\text{Strength}$).
        """
    )
    st.warning("**Investigation Priority — Not a Fraud Determination**\n\nPriority scores are based on observed payment patterns. They do not represent probabilities of fraud, legal findings, or proof of wrongdoing.")
    st.caption("Context-only fields such as District, Status, Age Band, Language Preference, and Tenure do not influence the priority score.")
    
    # Complete Top-20 Table
    display_df = worklist_df[[
        'rank',
        'case_id',
        'primary_signal',
        'investigation_priority_score',
        'signal_financial_discrepancy',
        'norm_persistence',
        'norm_strength',
        'monthly_award',
        'total_payment_amount',
        'status',
        'district'
    ]].copy()
    
    display_df.columns = [
        'Rank',
        'Case ID',
        'Primary Signal',
        'Priority Score',
        'Calculated Financial Discrepancy',
        'Persistence',
        'Strength',
        'Monthly Award',
        'Total Paid',
        'Status',
        'District'
    ]
    
    display_df['Rank'] = display_df['Rank'].astype(int)
    display_df['Priority Score'] = display_df['Priority Score'].apply(lambda x: f"{x:.2f}")
    display_df['Calculated Financial Discrepancy'] = display_df['Calculated Financial Discrepancy'].apply(lambda x: f"${x:,.2f}")
    display_df['Monthly Award'] = display_df['Monthly Award'].apply(lambda x: f"${x:,.2f}")
    display_df['Total Paid'] = display_df['Total Paid'].apply(lambda x: f"${x:,.2f}")
    display_df['Persistence'] = display_df['Persistence'].apply(lambda x: f"{x:.2f}")
    display_df['Strength'] = display_df['Strength'].apply(lambda x: f"{x:.2f}")
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    st.caption("Tip: Select 'Case Investigation' from the sidebar navigation to drill down into transaction IDs and casework narratives for any case.")

# ============================================================================
# PAGE 3: CASE INVESTIGATION
# ============================================================================
elif nav_page == "🔍 Case Investigation":
    st.markdown('<div class="section-header">🔍 Case Investigation & Transaction Evidence</div>', unsafe_allow_html=True)
    
    # Case selector
    case_options = [
        (f"Rank {row['rank']}: Case {row['case_id']} ({row['primary_signal']}) — ${row['signal_financial_discrepancy']:,.2f}", row['rank'])
        for _, row in worklist_df.iterrows()
    ]
    
    selected_case_display = st.selectbox(
        "Select a case to inspect evidence:",
        options=[opt[0] for opt in case_options],
        index=0
    )
    
    selected_rank = next(opt[1] for opt in case_options if opt[0] == selected_case_display)
    selected_case = worklist_df[worklist_df['rank'] == selected_rank].iloc[0]
    selected_exp = explanations_df[explanations_df['rank'] == selected_rank].iloc[0]
    
    # Top Case Metrics
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("Case ID", selected_case['case_id'])
    with c2:
        st.metric("Worklist Rank", f"#{int(selected_case['rank'])}")
    with c3:
        st.metric("Priority Score", f"{selected_case['investigation_priority_score']:.2f} / 100")
    with c4:
        st.metric("Case Status", selected_case['status'])
    with c5:
        st.metric("Authorized Award", f"${selected_case['monthly_award']:,.2f}")
        
    st.markdown("---")
    
    # Plain-Language Summary Box
    st.info("This case was prioritized for human investigation based on observed transaction patterns. The system does not determine whether a payment was improper.")
    st.subheader("Observed Payment Pattern")
    st.info(selected_exp['plain_language_summary'])
    
    # Key Evidence Points
    col_ev1, col_ev2 = st.columns([1.2, 1])
    
    with col_ev1:
        st.subheader("Key Evidence Points")
        raw_evidence = selected_exp['evidence_points']
        if isinstance(raw_evidence, str):
            try:
                evidence_list = ast.literal_eval(raw_evidence)
            except Exception:
                evidence_list = [raw_evidence]
        else:
            evidence_list = raw_evidence
            
        for pt in evidence_list:
            st.markdown(f"- {pt}")
            
    with col_ev2:
        st.subheader("Observed Pattern Diagnostics")
        sig = selected_case['primary_signal']
        if sig == 'Award Spike':
            st.metric("Max Single-Month Ratio", f"{selected_case['max_payment_to_award_ratio']:.2f}× Award")
            st.metric("Payments > 1.5× Award", f"{int(selected_case['payments_above_1_5x_count'])} of 6 payments")
            st.metric("Calculated Financial Discrepancy", f"${selected_case['signal_financial_discrepancy']:,.2f}")
        elif sig == 'Post-Closure':
            st.metric("Closure Month Logged", str(selected_case['closure_month']))
            st.metric("Disbursements After Closure", f"{int(selected_case['post_closure_payment_count'])} payment(s)")
            st.metric("Calculated Financial Discrepancy", f"${selected_case['signal_financial_discrepancy']:,.2f}")
        elif sig == 'Duplicate':
            st.metric("Duplicate Occurrences", f"{int(selected_case['duplicate_month_count'])} separate month(s)")
            st.metric("Duplicate Records", f"{int(selected_case['duplicate_payment_count'])} transactions")
            st.metric("Calculated Excess Relative to Recorded Award", f"${selected_case['signal_financial_discrepancy']:,.2f}")

    # Transaction Evidence Details
    st.subheader("Traceable Transaction Audit Trail")
    t1, t2, t3 = st.columns(3)
    with t1:
        st.markdown(f"""
        <div class="evidence-card">
            <strong>Relevant Billing Months</strong><br/>
            <code>{selected_exp['relevant_months']}</code>
        </div>
        """, unsafe_allow_html=True)
    with t2:
        st.markdown(f"""
        <div class="evidence-card">
            <strong>Payment Amounts</strong><br/>
            <code>{selected_exp['relevant_amounts']}</code>
        </div>
        """, unsafe_allow_html=True)
    with t3:
        st.markdown(f"""
        <div class="evidence-card">
            <strong>Transaction IDs</strong><br/>
            <code>{selected_exp['relevant_payment_ids']}</code>
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# PAGE 4: FAIRNESS AUDIT
# ============================================================================
elif nav_page == "⚖️ Fairness Audit":
    st.markdown('<div class="section-header">⚖️ Demographic Fairness & Representation Audit</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="summary-card">
        <h4 style="color: #1f3864; margin-top: 0;">Auditing Scope & Demographic Independence</h4>
        <p style="font-size: 0.95rem; color: #444; margin-bottom: 0;">
            <strong>Demographic attributes are NOT used to calculate investigation priority.</strong><br/>
            Age band, language preference, district, and tenure are evaluated only after ranking to audit representation and potential disparities.<br/><br/>
            Demographic fields (<code>age_band</code>, <code>language_preference</code>, <code>district</code>, <code>tenure</code>)
            were <strong>strictly excluded</strong> from the scoring model. The charts and tables below audit representation
            and selection rates transparently against population baselines.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Top-Level Summary Cards
    st.subheader("Executive Representation Summary")
    f1, f2, f3, f4 = st.columns(4)
    for column, dimension in zip((f1, f2, f3, f4), ['age_band', 'language_preference', 'district', 'tenure']):
        with column:
            dimension_data = fairness_df[fairness_df['dimension'] == dimension]
            highlight = dimension_data.loc[dimension_data['representation_ratio'].idxmax()]
            st.metric(
                f"Highest representation: {highlight['group']}",
                f"{highlight['representation_ratio']:.2f}x",
                f"{int(highlight['top20_count'])} of {len(worklist_df)} worklist cases"
            )
        
    st.markdown("<br/>", unsafe_allow_html=True)
    
    # Demographic Trap Explanation
    st.markdown("""
    <div class="governance-box">
        <h4 style="color: #b7791f; margin-top: 0;">🛡️ Demographic Trap Avoidance</h4>
        <p style="font-size: 0.9rem; color: #744210; margin-bottom: 0;">
            Naive ranking models using administrative contact attempts (<code>contact_attempts</code>) flag non-English claimants
            at <strong>4.5× the base rate</strong> (55% Spanish / 40% Other) because language accommodation requires more caseworker calls.
            By excluding administrative proxy features, our model avoids this artificial bias trap.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Detailed Slices
    st.subheader("Detailed Demographic Breakdown by Dimension")
    
    dim_tabs = st.tabs(["Age Band", "Language Preference", "District Office", "Housing Tenure"])
    dimension_map = {
        "Age Band": "age_band",
        "Language Preference": "language_preference",
        "District Office": "district",
        "Housing Tenure": "tenure"
    }
    
    for tab, (tab_name, dim_col) in zip(dim_tabs, dimension_map.items()):
        with tab:
            dim_data = fairness_df[fairness_df['dimension'] == dim_col].copy()
            
            # Chart
            fig = go.Figure(data=[
                go.Bar(
                    name='Population %',
                    x=dim_data['group'],
                    y=dim_data['population_pct'],
                    marker_color='#1f3864',
                    opacity=0.75
                ),
                go.Bar(
                    name='Top-20 %',
                    x=dim_data['group'],
                    y=dim_data['top20_pct'],
                    marker_color='#d73027',
                    opacity=0.85
                )
            ])
            fig.update_layout(
                barmode='group',
                height=280,
                margin=dict(l=20, r=20, t=20, b=20),
                showlegend=True,
                hovermode='x unified',
                yaxis_title='Percentage (%)'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Table
            display_cols = ['group', 'population_count', 'population_pct', 'top20_count', 'top20_pct', 'selection_rate_pct', 'representation_ratio']
            table_data = dim_data[display_cols].copy()
            table_data.columns = ['Group', 'Population Count', 'Population %', 'Top-20 Count', 'Top-20 %', 'Selection Rate %', 'Representation Ratio']
            table_data['Population %'] = table_data['Population %'].apply(lambda x: f"{x:.2f}%")
            table_data['Top-20 %'] = table_data['Top-20 %'].apply(lambda x: f"{x:.2f}%")
            table_data['Selection Rate %'] = table_data['Selection Rate %'].apply(lambda x: f"{x:.3f}%")
            table_data['Representation Ratio'] = table_data['Representation Ratio'].apply(lambda x: f"{x:.2f}×")
            
            st.dataframe(table_data, use_container_width=True, hide_index=True)

# ============================================================================
# PAGE 5: GOVERNANCE
# ============================================================================
elif nav_page == "⚠️ Governance":
    st.markdown('<div class="section-header">⚠️ Governance & Human Decision Boundary</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="governance-box">
        <h2 style="color: #172033; margin-top: 0;">Human-in-the-Loop Investigation</h2>
        <p style="color: #263449; margin-bottom: 0;">The system recommends which cases deserve attention first. A human investigator reviews the evidence and makes the final determination.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    #### Human-in-the-Loop Decision Flow
    
    ```
    System Analysis
         ↓
    Identifies payment anomalies
         ↓
    Prioritizes cases using financial impact, persistence, and evidence strength.
         ↓
    Human Investigator
         ↓
    Reviews evidence and complete case records
         ↓
    Human determination of facts
         ↓
    Administrative action (if appropriate)
    ```
    """)
    
    st.markdown("""
    <div class="governance-box">
        <h4 style="color: #b7791f; margin-top: 0;">PROHIBITED AUTOMATED ACTIONS</h4>
        <p style="font-size: 0.9rem; color: #744210;">
            The Overpayment Signal system <strong>MUST NEVER</strong> automatically:
        </p>
        <ol style="font-size: 0.9rem; color: #744210; line-height: 1.6;">
            <li>Determine that a claimant committed fraud.</li>
            <li>Determine that a payment is legally improper.</li>
            <li>Automatically suspend claimant benefits.</li>
            <li>Automatically terminate a benefit case.</li>
            <li>Automatically issue a clawback or overpayment recovery demand.</li>
            <li>Automatically reduce a claimant's benefit award.</li>
            <li>Automatically contact law enforcement or refer for criminal prosecution.</li>
            <li>Automatically make an adverse eligibility decision.</li>
            <li>Use demographic characteristics to determine investigation priority.</li>
            <li>Treat the priority score as a probability of fraud.</li>
            <li>Treat a ranking position as proof of wrongdoing.</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    #### Permitted System Scope
    - Identifies cases with observed payment-pattern signals from administrative data.
    - Ranks cases to assist human caseworkers in prioritizing limited investigation capacity.
    - Explains the observable transaction evidence behind the ranking in plain language.
    - Provides transparent demographic fairness diagnostics across protected dimensions.
    - Supports, but never replaces, human caseworker judgment and statutory due process.
    
    #### Who Makes the Final Decision?
    **Human caseworkers and administrative investigators** — with full access to complete case files, claimant representations, and administrative context — make all determinations following statutory due process.
    """)

# ============================================================================
# PAGE 6: DAY-2 INVESTIGATOR FEEDBACK
# ============================================================================
elif nav_page == "💡 Day-2 Feedback":
    st.markdown('<div class="section-header">💡 Day-2 Surprise Challenge: Investigator Feedback Loop</div>', unsafe_allow_html=True)

    day2_case = source_features_df[source_features_df['case_id'] == 'C-33248'].iloc[0]
    feedback_log_path = PROJECT_ROOT / "outputs" / "investigator_feedback_log.csv"
    feedback_df = pd.read_csv(feedback_log_path) if feedback_log_path.exists() else pd.DataFrame()
    day2_feedback_rows = feedback_df[feedback_df['case_id'] == day2_case['case_id']]
    day2_feedback = day2_feedback_rows.iloc[0] if not day2_feedback_rows.empty else None
    day2_algorithmic_status = 'NO_HARD_SIGNAL' if day2_case['primary_signal'] == 'None' else day2_case['primary_signal']

    st.markdown("""
    <div class="summary-card">
        <strong>Purpose:</strong> Investigator feedback provides a human-in-the-loop mechanism for recording review outcomes and improving future prioritization behavior.<br/>
        <strong>Boundary:</strong> Human review outcomes must not be inferred from transaction data alone.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="summary-card">
        <h4 style="color: #1f3864; margin-top: 0;">Case C-33248: Two-Tier Status & Review Outcome</h4>
        <table style="width: 100%; border-collapse: collapse; font-size: 0.9rem;">
            <tr style="border-bottom: 1px solid #e2e8f0;">
                <td style="padding: 6px; font-weight: bold; width: 220px;">Case ID</td>
                <td style="padding: 6px;"><code>{day2_case['case_id']}</code></td>
            </tr>
            <tr style="border-bottom: 1px solid #e2e8f0;">
                <td style="padding: 6px; font-weight: bold;">Algorithmic Signal Status</td>
                <td style="padding: 6px;"><span class="badge badge-normal">{day2_algorithmic_status}</span> (Algorithmic observation from current payment data; not in the Top-20.)</td>
            </tr>
            <tr style="border-bottom: 1px solid #e2e8f0;">
                <td style="padding: 6px; font-weight: bold;">Human Investigator Review</td>
                <td style="padding: 6px;"><span class="badge" style="background-color: #d1fae5; color: #065f46; font-weight: bold;">{day2_feedback['review_outcome'] if day2_feedback is not None else 'NO RECORDED FEEDBACK'}</span><br/>This status is sourced from investigator feedback. It is a human determination, not an automated model conclusion.</td>
            </tr>
            <tr style="border-bottom: 1px solid #e2e8f0;">
                <td style="padding: 6px; font-weight: bold;">Investigator Reason</td>
                <td style="padding: 6px;">{day2_feedback['reason'] if day2_feedback is not None else 'No feedback record loaded.'}</td>
            </tr>
            <tr>
                <td style="padding: 6px; font-weight: bold;">Source & Decision Authority</td>
                <td style="padding: 6px;">Human caseworker feedback (<code>{day2_feedback['investigator_id'] if day2_feedback is not None else 'not recorded'}</code>) — <em>Human feedback, not model inference</em>.</td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="governance-box">
        <h4 style="color: #b7791f; margin-top: 0;">🛡️ Core Day-2 Governance Principles</h4>
        <ul style="font-size: 0.9rem; color: #744210; line-height: 1.6; margin-bottom: 0;">
            <li><strong>Administrative activity is not automatically evidence of claimant wrongdoing.</strong> (Excluding <code>contact_attempts</code> and adjustments protects 98 'busy files', 87.8% non-English).</li>
            <li><strong>Absence of a detected signal is not proof that a payment was legitimate.</strong> (Algorithms observe numbers; only human caseworkers determine legal legitimacy).</li>
            <li><strong>Investigator-confirmed findings are distinguished from algorithmic observations.</strong> (Strict two-tier status architecture).</li>
            <li><strong>Human feedback improves prioritization while preserving human decision authority and due process.</strong></li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("Investigator Review Outcome Log")
    if feedback_log_path.exists():
        st.dataframe(feedback_df, use_container_width=True, hide_index=True)
    else:
        st.info("Investigator feedback log will be created upon pipeline execution.")


# ============================================================================
# FOOTER (Rendered across all views)
# ============================================================================

st.markdown(
    '<div class="footer">The Overpayment Signal — Investigation Prioritization, Not Automated Adjudication. Built for Hackathon Evaluation.</div>',
    unsafe_allow_html=True
)

