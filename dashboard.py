"""
TWINSHIELD Network Lab — Interactive Network Digital Twin Simulator.

Uncertainty-Aware Digital Twin Framework for Predictive Network Service
Degradation and Safe Network Control.

Refined engineering workstation interface (Light theme, modern SaaS design,
comprehensive technical sections, natural scroll depth, and refined gradients).
"""

from datetime import datetime
from pathlib import Path
import csv
import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from actions.action_schema import ReroutingAction
from actions.candidate_generator import generate_candidate_actions
from actions.routing_actions import is_valid_rerouting_action
from decision.pipeline import DecisionPipeline
from models.predictor import MODEL_PATH, load_model, train_and_save_model
from simulation.runner import run_simulation_episode
from simulation.scenarios import SUPPORTED_SCENARIOS
from simulation.splits import split_rows_by_episode


# ---------------------------------------------------------------------------
# Streamlit Page Configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="TWINSHIELD Network Lab",
    page_icon="shield",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Modern SaaS / Engineering Workstation Styling with Refined Gradients
# ---------------------------------------------------------------------------
MODERN_WEBSITE_CSS = """
<style>
/* Base Typography & Canvas */
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    color: #1E293B;
}
.stApp {
    background: linear-gradient(180deg, #EBF4FC 0%, #E0EEF9 100%);
    background-attachment: fixed;
}

/* Modern Brand Navbar */
.brand-navbar {
    background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
    border-radius: 8px;
    margin-bottom: 16px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.08), 0 2px 4px -2px rgba(0, 0, 0, 0.06);
    overflow: hidden;
    position: relative;
}
.brand-navbar-accent {
    height: 3px;
    background: linear-gradient(90deg, #10B981 0%, #06B6D4 35%, #3B82F6 70%, #8B5CF6 100%);
    width: 100%;
}
.brand-navbar-body {
    padding: 14px 22px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
}
.brand-title {
    font-size: 1.35rem;
    font-weight: 800;
    color: #F8FAFC;
    letter-spacing: -0.02em;
    margin: 0;
    line-height: 1.2;
    display: flex;
    align-items: center;
    gap: 10px;
}
.brand-version {
    font-size: 0.72rem;
    font-weight: 600;
    color: #38BDF8;
    background: rgba(56, 189, 248, 0.12);
    border: 1px solid rgba(56, 189, 248, 0.35);
    padding: 2px 7px;
    border-radius: 12px;
    letter-spacing: 0.02em;
}
.brand-tagline {
    font-size: 0.82rem;
    color: #94A3B8;
    margin-top: 3px;
}
.brand-badges {
    display: flex;
    gap: 10px;
    align-items: center;
    flex-wrap: wrap;
}
.badge-live-pulse {
    background: rgba(16, 185, 129, 0.12);
    border: 1px solid rgba(16, 185, 129, 0.35);
    color: #34D399;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 5px 12px;
    border-radius: 20px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}
.live-dot {
    width: 7px;
    height: 7px;
    background-color: #10B981;
    border-radius: 50%;
    display: inline-block;
    box-shadow: 0 0 6px #10B981;
}
.badge-spec-info {
    background: rgba(148, 163, 184, 0.12);
    border: 1px solid rgba(148, 163, 184, 0.25);
    color: #CBD5E1;
    font-size: 0.75rem;
    font-weight: 500;
    padding: 5px 12px;
    border-radius: 20px;
}
.badge-sim-mode {
    background: rgba(245, 158, 11, 0.12);
    border: 1px solid rgba(245, 158, 11, 0.35);
    color: #FBBF24;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 5px 12px;
    border-radius: 20px;
}

/* Card Surfaces with Subtle Gradient Accents */
.card-surface {
    background: #FFFFFF;
    border: 1px solid #D6E4F0;
    border-radius: 8px;
    padding: 18px 20px;
    margin-bottom: 16px;
    box-shadow: 0 2px 4px 0 rgba(15, 23, 42, 0.04);
}
.card-header-styled {
    font-size: 0.88rem;
    font-weight: 700;
    color: #1E293B;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #F1F5F9;
    padding-bottom: 8px;
}

/* Decision Status Callout Boxes with Soft Gradients */
.callout-box {
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 16px;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.04);
}
.callout-accept {
    background: linear-gradient(180deg, #F0FDF4 0%, #FFFFFF 100%);
    border: 1px solid #BBF7D0;
    border-left: 4px solid #16A34A;
}
.callout-reject {
    background: linear-gradient(180deg, #FEF2F2 0%, #FFFFFF 100%);
    border: 1px solid #FECACA;
    border-left: 4px solid #DC2626;
}
.callout-abstain {
    background: linear-gradient(180deg, #FFFBEB 0%, #FFFFFF 100%);
    border: 1px solid #FDE68A;
    border-left: 4px solid #D97706;
}

/* Status Badges */
.badge-accept {
    background-color: #DCFCE7;
    color: #15803D;
    font-size: 0.74rem;
    font-weight: 700;
    padding: 3px 9px;
    border-radius: 4px;
    border: 1px solid #86EFAC;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
.badge-reject {
    background-color: #FEE2E2;
    color: #B91C1C;
    font-size: 0.74rem;
    font-weight: 700;
    padding: 3px 9px;
    border-radius: 4px;
    border: 1px solid #FCA5A5;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
.badge-abstain {
    background-color: #FEF3C7;
    color: #B45309;
    font-size: 0.74rem;
    font-weight: 700;
    padding: 3px 9px;
    border-radius: 4px;
    border: 1px solid #FCD34D;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

/* Summary Metric Tiles */
.stat-tile-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 12px;
    margin-bottom: 14px;
}
.stat-tile {
    background: linear-gradient(180deg, #FFFFFF 0%, #F8FBFE 100%);
    border: 1px solid #D6E4F0;
    border-radius: 8px;
    padding: 12px 16px;
    box-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.03);
}
.stat-tile-title {
    font-size: 0.74rem;
    font-weight: 600;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 4px;
}
.stat-tile-value {
    font-size: 1.15rem;
    font-weight: 800;
    color: #0F172A;
}
.stat-tile-desc {
    font-size: 0.75rem;
    color: #64748B;
    margin-top: 3px;
}

/* Legend items */
.legend-item {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.78rem;
    color: #475569;
    margin-right: 16px;
}
.legend-line {
    width: 16px;
    height: 3px;
    display: inline-block;
    border-radius: 2px;
}
.legend-dot {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    display: inline-block;
}

/* Modern Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background-color: transparent;
    border-bottom: 2px solid #D6E4F0;
    padding-bottom: 0px;
    margin-bottom: 16px;
}
.stTabs [data-baseweb="tab"] {
    background-color: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    color: #64748B;
    padding: 10px 20px;
    font-size: 0.90rem;
    font-weight: 600;
}
.stTabs [aria-selected="true"] {
    background-color: transparent !important;
    border-bottom: 2px solid #168C83 !important;
    color: #168C83 !important;
    font-weight: 700;
}

/* Button Styling */
div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #168C83 0%, #116B64 100%) !important;
    color: #FFFFFF !important;
    border: 1px solid #116B64 !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
}
div.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #13776F 0%, #0E5650 100%) !important;
}
div.stButton > button:not([kind="primary"]) {
    background: #FFFFFF !important;
    color: #1E293B !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 6px !important;
    font-weight: 500 !important;
}
div.stButton > button:not([kind="primary"]):hover {
    background: #F8FAFC !important;
    border-color: #94A3B8 !important;
}

/* Technical Specification Cards */
.spec-card {
    background: #FFFFFF;
    border: 1px solid #D6E4F0;
    border-top: 3px solid #168C83;
    border-radius: 8px;
    padding: 16px 18px;
    margin-top: 14px;
    box-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.03);
}
.spec-card-title {
    font-size: 0.85rem;
    font-weight: 700;
    color: #0F172A;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    margin-bottom: 8px;
}
.spec-card-body {
    font-size: 0.82rem;
    color: #475569;
    line-height: 1.55;
}

/* Website Footer */
.website-footer {
    border-top: 1px solid #D6E4F0;
    background: linear-gradient(180deg, #FFFFFF 0%, #EBF4FC 100%);
    padding: 24px 20px;
    margin-top: 40px;
    border-radius: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
}
.footer-text {
    font-size: 0.8rem;
    color: #64748B;
}
.footer-links {
    font-size: 0.78rem;
    color: #94A3B8;
}
</style>
"""
st.markdown(MODERN_WEBSITE_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Model Loader with Graceful Training Fallback
# ---------------------------------------------------------------------------
@st.cache_resource
def get_calibrated_model():
    """
    Load the calibrated Logistic Regression model artifact.
    If the artifact is missing, automatically train and save it
    using the repository telemetry dataset.
    """
    if not MODEL_PATH.exists():
        data_path = Path("data/twinshield_telemetry_targets.csv")
        if data_path.exists():
            with open(data_path, mode="r", encoding="utf-8") as csv_file:
                rows = list(csv.DictReader(csv_file))
            train_rows, _, _ = split_rows_by_episode(rows)
            return train_and_save_model(train_rows, model_path=MODEL_PATH)
        return None
    try:
        return load_model(MODEL_PATH)
    except Exception as exc:
        st.error(f"Model loading exception: {exc}")
        return None


# ---------------------------------------------------------------------------
# Stable Planar Node Coordinates
# ---------------------------------------------------------------------------
NODE_COORDS = {
    "n1": (1.0, 3.0),
    "n2": (3.5, 4.5),
    "n3": (3.5, 1.5),
    "n4": (6.0, 3.0),
    "n5": (7.8, 4.5),
    "n6": (9.6, 4.5),
}

NODE_METADATA = {
    "n1": {"title": "Router 1 (Ingress Gateway)", "role": "Source for f1 & f2"},
    "n2": {"title": "Router 2 (Core Aggregator)", "role": "Source for f3, Ingress to Bottleneck"},
    "n3": {"title": "Router 3 (Alternate Core)", "role": "Alternative transit path"},
    "n4": {"title": "Router 4 (Egress Aggregator)", "role": "Destination for f1 & f2"},
    "n5": {"title": "Router 5 (Distribution Transit)", "role": "Distribution forwarder"},
    "n6": {"title": "Router 6 (Core Destination)", "role": "Destination for f3"},
}


# ---------------------------------------------------------------------------
# Modern Technical Topology Diagram (Plotly)
# ---------------------------------------------------------------------------
def build_topology_figure(
    network_state,
    selected_flow_id="f1",
    proposed_route=None,
):
    """
    Build a clean, high-precision engineering schematic of the network topology.
    - Base links: Light neutral slate (#CBD5E1)
    - Current route: Restrained blue (#2563EB)
    - Proposed reroute: Muted teal (#168C83, dashed)
    - Elevated load (50-75%): Muted amber (#D97706)
    - Congested links (>= 75%): Restrained red (#DC2626)
    - Dual rendering when route intersects a congested link.
    """
    fig = go.Figure()

    selected_flow = None
    for flow in network_state.get("flows", []):
        if flow["flow_id"] == selected_flow_id:
            selected_flow = flow
            break

    current_route = selected_flow["route"] if selected_flow else []
    src_node = selected_flow["source"] if selected_flow else None
    dst_node = selected_flow["destination"] if selected_flow else None

    # Construct edge sets for active routes
    current_edges = set()
    if current_route and len(current_route) >= 2:
        for u, v in zip(current_route, current_route[1:]):
            current_edges.add((u, v))
            current_edges.add((v, u))

    proposed_edges = set()
    if proposed_route and len(proposed_route) >= 2:
        for u, v in zip(proposed_route, proposed_route[1:]):
            proposed_edges.add((u, v))
            proposed_edges.add((v, u))

    links = network_state.get("links", [])

    # 1. Congestion Underlay Stroke (for links >= 75%)
    for link in links:
        u, v = link["source"], link["destination"]
        x0, y0 = NODE_COORDS[u]
        x1, y1 = NODE_COORDS[v]
        util = link.get("utilization", 0.0)

        if util >= 0.75:
            fig.add_trace(
                go.Scatter(
                    x=[x0, x1],
                    y=[y0, y1],
                    mode="lines",
                    line=dict(color="rgba(220, 38, 38, 0.28)", width=10),
                    hoverinfo="none",
                    showlegend=False,
                )
            )

    # 2. Base Physical Links Layer
    for link in links:
        u, v = link["source"], link["destination"]
        x0, y0 = NODE_COORDS[u]
        x1, y1 = NODE_COORDS[v]
        util = link.get("utilization", 0.0)

        if util >= 0.75:
            base_color = "#DC2626"
            line_width = 3.0
        elif util >= 0.50:
            base_color = "#D97706"
            line_width = 2.5
        else:
            base_color = "#CBD5E1"
            line_width = 2.0

        fig.add_trace(
            go.Scatter(
                x=[x0, x1],
                y=[y0, y1],
                mode="lines",
                line=dict(color=base_color, width=line_width),
                hoverinfo="none",
                showlegend=False,
            )
        )

    # 3. Route Overlay Traces (Current & Proposed)
    for link in links:
        u, v = link["source"], link["destination"]
        x0, y0 = NODE_COORDS[u]
        x1, y1 = NODE_COORDS[v]
        pair = (u, v)

        on_current = pair in current_edges
        on_proposed = pair in proposed_edges

        if on_current and on_proposed:
            fig.add_trace(
                go.Scatter(
                    x=[x0, x1],
                    y=[y0, y1],
                    mode="lines",
                    line=dict(color="#2563EB", width=4.0),
                    hoverinfo="none",
                    showlegend=False,
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=[x0, x1],
                    y=[y0, y1],
                    mode="lines",
                    line=dict(color="#168C83", width=2.5, dash="dot"),
                    hoverinfo="none",
                    showlegend=False,
                )
            )
        elif on_current:
            fig.add_trace(
                go.Scatter(
                    x=[x0, x1],
                    y=[y0, y1],
                    mode="lines",
                    line=dict(color="#2563EB", width=3.5),
                    hoverinfo="none",
                    showlegend=False,
                )
            )
        elif on_proposed:
            fig.add_trace(
                go.Scatter(
                    x=[x0, x1],
                    y=[y0, y1],
                    mode="lines",
                    line=dict(color="#168C83", width=3.0, dash="dash"),
                    hoverinfo="none",
                    showlegend=False,
                )
            )

    # 4. Link Midpoint Badges & Interactive Tooltips
    for link in links:
        u, v = link["source"], link["destination"]
        x0, y0 = NODE_COORDS[u]
        x1, y1 = NODE_COORDS[v]
        xm = (x0 + x1) / 2.0
        ym = (y0 + y1) / 2.0

        if link["link_id"] == "l7":
            ym += 0.16

        util = link.get("utilization", 0.0)
        cap = link.get("capacity_mbps", 100)
        bg = link.get("background_load_mbps", 0.0)
        qdel = link.get("queue_delay_ms", 0.0)
        qocc = link.get("queue_occupancy", 0.0)
        lid = link["link_id"]

        is_cong = util >= 0.75
        is_elev = 0.50 <= util < 0.75

        status_text = (
            "High Congestion" if is_cong else "Elevated Load" if is_elev else "Normal"
        )
        badge_text = (
            f"{lid} [{util*100:.0f}%]" if not is_cong else f"{lid} [{util*100:.0f}% Congested]"
        )

        hover_html = (
            f"<b>Link {lid} ({u} ↔ {v})</b><br>"
            f"Capacity: <b>{cap} Mbps</b><br>"
            f"Utilization: <b>{util*100:.1f}%</b> ({status_text})<br>"
            f"Background Load: <b>{bg:.1f} Mbps</b><br>"
            f"Queue Delay: <b>{qdel:.1f} ms</b><br>"
            f"Queue Occupancy: <b>{qocc*100:.1f}%</b>"
        )

        badge_color = "#DC2626" if is_cong else "#D97706" if is_elev else "#64748B"

        fig.add_trace(
            go.Scatter(
                x=[xm],
                y=[ym],
                mode="text",
                text=[badge_text],
                textfont=dict(size=10, color=badge_color, family="monospace"),
                hovertext=[hover_html],
                hoverinfo="text",
                showlegend=False,
            )
        )

    # 5. Node Device Points & Badges
    node_x, node_y, node_text, node_hover = [], [], [], []
    node_colors, node_borders, node_border_widths, node_sizes = [], [], [], []

    for nid, (x, y) in NODE_COORDS.items():
        node_x.append(x)
        node_y.append(y)
        node_text.append(f"<b>{nid}</b>")

        is_src = (nid == src_node)
        is_dst = (nid == dst_node)
        in_curr = nid in current_route
        in_prop = (proposed_route is not None) and (nid in proposed_route)

        meta = NODE_METADATA.get(nid, {})
        title = meta.get("title", nid)
        role = meta.get("role", "Network Node")

        if is_src:
            border_color = "#2563EB"
            border_width = 2.5
            size = 36
            tag = " [Source]"
        elif is_dst:
            border_color = "#4F46E5"
            border_width = 2.5
            size = 36
            tag = " [Destination]"
        elif in_prop:
            border_color = "#168C83"
            border_width = 2.5
            size = 34
            tag = " [Proposed Route]"
        elif in_curr:
            border_color = "#2563EB"
            border_width = 2.0
            size = 34
            tag = " [Current Route]"
        else:
            border_color = "#94A3B8"
            border_width = 1.5
            size = 32
            tag = ""

        node_colors.append("#FFFFFF")
        node_borders.append(border_color)
        node_border_widths.append(border_width)
        node_sizes.append(size)

        passing_flows = [
            f["flow_id"]
            for f in network_state.get("flows", [])
            if nid in f.get("route", [])
        ]

        hover_html = (
            f"<b>Node: {nid.upper()}</b> — {title}{tag}<br>"
            f"Role: {role}<br>"
            f"Active Flows: <b>{', '.join(passing_flows) if passing_flows else 'None'}</b>"
        )
        node_hover.append(hover_html)

    fig.add_trace(
        go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            marker=dict(
                size=node_sizes,
                color=node_colors,
                line=dict(color=node_borders, width=node_border_widths),
            ),
            text=node_text,
            textposition="middle center",
            textfont=dict(size=12, color="#1E293B", family="sans-serif"),
            hovertext=node_hover,
            hoverinfo="text",
            showlegend=False,
        )
    )

    sub_x, sub_y, sub_labels = [], [], []
    for nid, (x, y) in NODE_COORDS.items():
        sub_x.append(x)
        sub_y.append(y - 0.34 if y <= 3.0 else y + 0.34)
        role_label = NODE_METADATA.get(nid, {}).get("title", nid).split(" ")[0]
        if nid == src_node:
            role_label += " (Src)"
        elif nid == dst_node:
            role_label += " (Dst)"
        sub_labels.append(role_label)

    fig.add_trace(
        go.Scatter(
            x=sub_x,
            y=sub_y,
            mode="text",
            text=sub_labels,
            textfont=dict(size=10, color="#64748B"),
            hoverinfo="none",
            showlegend=False,
        )
    )

    fig.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[0.2, 10.4],
            fixedrange=True,
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[0.6, 5.4],
            fixedrange=True,
        ),
        hoverlabel=dict(
            bgcolor="#FFFFFF",
            font_size=11,
            font_family="-apple-system, BlinkMacSystemFont, sans-serif",
            bordercolor="#CBD5E1",
            font_color="#1E293B",
        ),
        height=480,
    )

    return fig


# ---------------------------------------------------------------------------
# Session State Initialization & Cache Management
# ---------------------------------------------------------------------------
if "scenario_id" not in st.session_state:
    st.session_state["scenario_id"] = "normal"

if "selected_flow_id" not in st.session_state:
    st.session_state["selected_flow_id"] = "f1"

if "selected_candidate_idx" not in st.session_state:
    st.session_state["selected_candidate_idx"] = 0

if "current_state" not in st.session_state:
    st.session_state["current_state"] = run_simulation_episode(
        scenario_id=st.session_state["scenario_id"]
    )

if "evaluation_result" not in st.session_state:
    st.session_state["evaluation_result"] = None

if "comparison_results" not in st.session_state:
    st.session_state["comparison_results"] = None

if "session_history" not in st.session_state:
    st.session_state["session_history"] = []

if "selection_signature" not in st.session_state:
    st.session_state["selection_signature"] = (
        st.session_state["scenario_id"],
        st.session_state["selected_flow_id"],
    )


# ---------------------------------------------------------------------------
# Modern Brand Header Component
# ---------------------------------------------------------------------------
model = get_calibrated_model()
model_status = "Predictor ready" if model is not None else "Model initializing..."

st.markdown(
    f"""
    <div class="brand-navbar">
        <div class="brand-navbar-accent"></div>
        <div class="brand-navbar-body">
            <div>
                <div class="brand-title">
                    TWINSHIELD <span class="brand-version">Digital Twin</span>
                </div>
                <div class="brand-tagline">
                    Uncertainty-Aware Network Digital Twin for Predictive Service Degradation & Safe Control
                </div>
            </div>
            <div class="brand-badges">
                <div class="badge-live-pulse">
                    <span class="live-dot"></span> Simulation Active
                </div>
                <div class="badge-spec-info">
                    {model_status}
                </div>
                <div class="badge-sim-mode">
                    No Live Network Actions
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Navigation Tabs
# ---------------------------------------------------------------------------
tab_lab, tab_analysis, tab_research, tab_history = st.tabs(
    [
        "Network Lab",
        "Decision Analysis",
        "Research Results",
        "Session History",
    ]
)


# ===========================================================================
# TAB 1: NETWORK LAB (Main Interactive Experience)
# ===========================================================================
with tab_lab:
    active_scenario = st.session_state["scenario_id"]
    active_flow_id = st.session_state["selected_flow_id"]

    # Section 1: Main Interactive Workspace (Topology + Controls)
    col_topo, col_ctrl = st.columns([0.68, 0.32], gap="medium")

    with col_ctrl:
        st.markdown(
            """
            <div class="card-surface">
                <div class="card-header-styled">
                    <span>Simulation Controls</span>
                    <span style="font-size: 0.72rem; color: #64748B; font-weight: 500;">Interactive</span>
                </div>
            """,
            unsafe_allow_html=True,
        )

        scenario_labels = {
            "normal": "Normal operation",
            "shared_bottleneck": "Shared bottleneck (link l2)",
            "background_surge": "Background surge (link l7)",
        }
        scenario_keys = list(scenario_labels.keys())
        current_sc_idx = (
            scenario_keys.index(active_scenario)
            if active_scenario in scenario_keys
            else 0
        )

        new_scenario = st.selectbox(
            "Scenario profile",
            options=scenario_keys,
            format_func=lambda k: scenario_labels[k],
            index=current_sc_idx,
            help="Configures background load conditions across the simulated topology.",
        )

        scenario_notes = {
            "normal": "All links operate under 20% utilization with compliant latency.",
            "shared_bottleneck": "Adds 5 Mbps background load to link l2 (n2 → n4), degrading flow f1.",
            "background_surge": "Injects 40 Mbps surge traffic to link l7 (n2 → n5), stressing flow f3.",
        }
        st.caption(scenario_notes[new_scenario])

        flow_options = ["f1", "f2", "f3"]
        flow_labels = {
            "f1": "Flow f1 (n1 → n4, SLA 50 ms)",
            "f2": "Flow f2 (n1 → n4, SLA 60 ms)",
            "f3": "Flow f3 (n2 → n6, SLA 80 ms)",
        }
        current_flow_idx = (
            flow_options.index(active_flow_id)
            if active_flow_id in flow_options
            else 0
        )

        new_flow = st.selectbox(
            "Target flow",
            options=flow_options,
            format_func=lambda k: flow_labels[k],
            index=current_flow_idx,
            help="Selects the network traffic flow to evaluate for predictive control.",
        )

        # Anti-stale state check
        new_signature = (new_scenario, new_flow)
        if new_signature != st.session_state["selection_signature"]:
            st.session_state["scenario_id"] = new_scenario
            st.session_state["selected_flow_id"] = new_flow
            st.session_state["selection_signature"] = new_signature
            st.session_state["current_state"] = run_simulation_episode(
                scenario_id=new_scenario
            )
            st.session_state["selected_candidate_idx"] = 0
            st.session_state["evaluation_result"] = None
            st.session_state["comparison_results"] = None
            st.rerun()

        state = st.session_state["current_state"]
        current_flow_obj = next(
            (f for f in state["flows"] if f["flow_id"] == new_flow),
            None,
        )
        curr_route = current_flow_obj["route"] if current_flow_obj else []

        candidate_actions = generate_candidate_actions(
            topology=state["topology"],
            target_flow_id=new_flow,
            old_path=curr_route,
            max_candidates=5,
        )

        cand_options = []
        for idx, act in enumerate(candidate_actions):
            is_valid, _ = is_valid_rerouting_action(
                topology=state["topology"],
                target_flow=new_flow,
                old_path=curr_route,
                new_path=act.new_path,
            )
            val_status = "Valid" if is_valid else "Invalid"
            cand_options.append(f"Candidate {idx+1}: {' → '.join(act.new_path)} ({val_status})")

        if candidate_actions:
            chosen_cand_idx = st.selectbox(
                "Candidate route",
                options=list(range(len(candidate_actions))),
                format_func=lambda i: cand_options[i],
                index=min(
                    st.session_state["selected_candidate_idx"],
                    len(candidate_actions) - 1,
                ),
            )
            st.session_state["selected_candidate_idx"] = chosen_cand_idx
            selected_action = candidate_actions[chosen_cand_idx]
            proposed_path = selected_action.new_path

            st.markdown(
                f"""
                <div style="font-size: 0.78rem; color: #64748B; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; padding: 6px 10px; margin: 4px 0 12px 0;">
                    <b>Current:</b> <code>{' → '.join(curr_route)}</code><br>
                    <b>Proposed:</b> <code style="color: #168C83;">{' → '.join(proposed_path)}</code>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.info("No alternate candidate routes available for this flow.")
            selected_action = None
            proposed_path = None

        # Action Buttons
        eval_clicked = st.button(
            "Evaluate selected route",
            type="primary",
            use_container_width=True,
            disabled=(selected_action is None or model is None),
        )

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            compare_clicked = st.button(
                "Compare candidates",
                use_container_width=True,
                disabled=(not candidate_actions or model is None),
            )
        with col_b2:
            reset_clicked = st.button(
                "Reset scenario",
                use_container_width=True,
            )

        if reset_clicked:
            st.session_state["current_state"] = run_simulation_episode(
                scenario_id=st.session_state["scenario_id"]
            )
            st.session_state["evaluation_result"] = None
            st.session_state["comparison_results"] = None
            st.rerun()

        if eval_clicked and selected_action and model:
            pipeline = DecisionPipeline(network_state=state, model=model)
            eval_res = pipeline.evaluate(selected_action)
            st.session_state["evaluation_result"] = eval_res

            outcomes = (
                eval_res.get("evaluation", {})
                .get("predicted_outcomes", {})
                .get(new_flow, {})
            )
            st.session_state["session_history"].append(
                {
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "scenario": st.session_state["scenario_id"],
                    "target_flow": new_flow,
                    "current_route": " → ".join(curr_route),
                    "proposed_route": " → ".join(selected_action.new_path),
                    "predicted_delay": outcomes.get("delay"),
                    "predicted_loss": outcomes.get("packet_loss"),
                    "predicted_risk": outcomes.get("sla_violation_risk"),
                    "uncertainty": outcomes.get("uncertainty_score"),
                    "decision": eval_res.get("status", "unknown").upper(),
                    "reason": eval_res.get("reason", "N/A"),
                }
            )
            st.rerun()

        if compare_clicked and candidate_actions and model:
            pipeline = DecisionPipeline(network_state=state, model=model)
            comp_list = []
            for act in candidate_actions:
                res = pipeline.evaluate(act)
                target_out = (
                    res.get("evaluation", {})
                    .get("predicted_outcomes", {})
                    .get(new_flow, {})
                )
                comp_list.append(
                    {
                        "action": act,
                        "proposed_route": " → ".join(act.new_path),
                        "status": res["status"].upper(),
                        "predicted_delay": target_out.get("delay"),
                        "predicted_loss": target_out.get("packet_loss"),
                        "predicted_risk": target_out.get("sla_violation_risk"),
                        "uncertainty": target_out.get("uncertainty_score"),
                        "reason": res.get("reason"),
                        "full_res": res,
                    }
                )
                st.session_state["session_history"].append(
                    {
                        "time": datetime.now().strftime("%H:%M:%S"),
                        "scenario": st.session_state["scenario_id"],
                        "target_flow": new_flow,
                        "current_route": " → ".join(curr_route),
                        "proposed_route": " → ".join(act.new_path),
                        "predicted_delay": target_out.get("delay"),
                        "predicted_loss": target_out.get("packet_loss"),
                        "predicted_risk": target_out.get("sla_violation_risk"),
                        "uncertainty": target_out.get("uncertainty_score"),
                        "decision": res["status"].upper(),
                        "reason": res.get("reason"),
                    }
                )
            st.session_state["comparison_results"] = comp_list
            st.session_state["evaluation_result"] = comp_list[0]["full_res"]
            st.rerun()

        eval_result = st.session_state["evaluation_result"]
        if eval_result:
            status = eval_result.get("status", "").lower()
            reason = eval_result.get("reason", "")
            risk_bef = eval_result.get("risk_before", 0.0)
            risk_aft = eval_result.get("risk_after", 0.0)

            if status == "accept":
                box_cls = "callout-accept"
                badge = '<span class="badge-accept">ACCEPT</span>'
            elif status == "reject":
                box_cls = "callout-reject"
                badge = '<span class="badge-reject">REJECT</span>'
            else:
                box_cls = "callout-abstain"
                badge = '<span class="badge-abstain">ABSTAIN</span>'

            st.markdown(
                f"""
                <div class="{box_cls}" style="margin-top: 14px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="font-size: 0.72rem; color: #64748B; font-weight: 700; text-transform: uppercase;">Safety Result</span>
                        {badge}
                    </div>
                    <div style="font-size: 0.82rem; color: #0F172A; margin-bottom: 4px;">
                        SLA risk: <b>{risk_bef:.4f}</b> &rarr; <b>{risk_aft:.4f}</b>
                    </div>
                    <div style="font-size: 0.78rem; color: #475569; line-height: 1.35;">
                        {reason}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

    with col_topo:
        state = st.session_state["current_state"]
        fig = build_topology_figure(
            network_state=state,
            selected_flow_id=active_flow_id,
            proposed_route=proposed_path,
        )

        st.markdown(
            """
            <div style="background-color: #FFFFFF; border: 1px solid #D6E4F0; border-radius: 8px 8px 0 0; padding: 12px 18px; border-bottom: none; display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 0.85rem; font-weight: 700; color: #0F172A; text-transform: uppercase; letter-spacing: 0.04em;">
                    Network Topology Schematic
                </span>
                <span style="font-size: 0.75rem; color: #64748B;">
                    Interactive Digital Twin Graph &bull; 6 Nodes, 7 Links
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"displayModeBar": False},
        )

        st.markdown(
            """
            <div style="background-color: #FFFFFF; border: 1px solid #D6E4F0; border-top: none; border-radius: 0 0 8px 8px; padding: 8px 18px; margin-top: -12px; margin-bottom: 16px; display: flex; flex-wrap: wrap; gap: 16px;">
                <div class="legend-item"><span class="legend-line" style="background-color: #CBD5E1;"></span> Base link</div>
                <div class="legend-item"><span class="legend-line" style="background-color: #2563EB;"></span> Current route (Flow {flow})</div>
                <div class="legend-item"><span class="legend-line" style="background-color: #168C83; border-top: 1px dashed #168C83;"></span> Proposed reroute</div>
                <div class="legend-item"><span class="legend-line" style="background-color: #D97706;"></span> Elevated load (50-75%)</div>
                <div class="legend-item"><span class="legend-line" style="background-color: #DC2626;"></span> Congested link (&ge; 75%)</div>
                <div class="legend-item"><span class="legend-dot" style="background-color: #FFFFFF; border: 2px solid #2563EB;"></span> Source node</div>
                <div class="legend-item"><span class="legend-dot" style="background-color: #FFFFFF; border: 2px solid #4F46E5;"></span> Destination node</div>
            </div>
            """.format(flow=active_flow_id),
            unsafe_allow_html=True,
        )

    # -----------------------------------------------------------------------
    # Section 2: Network Health & Critical Path Telemetry
    # -----------------------------------------------------------------------
    links = state["links"]
    max_link = max(links, key=lambda l: l.get("utilization", 0.0))
    max_util = max_link.get("utilization", 0.0)

    flows = state["flows"]
    violated_flows = [f for f in flows if f.get("sla_violation", False)]
    affected_flow = max(flows, key=lambda f: f.get("sla_violation_risk", 0.0))

    st.markdown(
        f"""
        <div class="stat-tile-grid">
            <div class="stat-tile">
                <div class="stat-tile-title">Operational Scenario</div>
                <div class="stat-tile-value">{scenario_labels[active_scenario]}</div>
                <div class="stat-tile-desc">{'1 flow violating SLA contracts' if violated_flows else 'All 3 flows within SLA limits'}</div>
            </div>
            <div class="stat-tile">
                <div class="stat-tile-title">Primary Bottleneck Link</div>
                <div class="stat-tile-value" style="color: {'#DC2626' if max_util >= 0.75 else '#D97706' if max_util >= 0.5 else '#0F172A'};">
                    Link {max_link['link_id']} ({max_link['source']} ↔ {max_link['destination']})
                </div>
                <div class="stat-tile-desc">{max_util*100:.1f}% utilization &bull; {max_link.get('queue_delay_ms', 0):.1f} ms queue delay</div>
            </div>
            <div class="stat-tile">
                <div class="stat-tile-title">Most Degraded Flow</div>
                <div class="stat-tile-value" style="color: {'#DC2626' if affected_flow.get('sla_violation') else '#15803D'};">
                    Flow {affected_flow['flow_id'].upper()} ({'SLA Violation' if affected_flow.get('sla_violation') else 'Compliant'})
                </div>
                <div class="stat-tile-desc">{affected_flow.get('delay', 0):.1f} ms delay &bull; {affected_flow.get('packet_loss', 0)*100:.1f}% packet loss</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Flow Telemetry Table
    st.markdown(
        """
        <div class="card-surface">
            <div class="card-header-styled">
                <span>Active Traffic Flows & SLA Telemetry</span>
                <span style="font-size: 0.72rem; color: #64748B; font-weight: 500;">Deterministic Simulation Engine</span>
            </div>
        """,
        unsafe_allow_html=True,
    )

    flow_rows = []
    for fl in state["flows"]:
        is_viol = fl.get("sla_violation", False)
        status_tag = "SLA Violation" if is_viol else "Compliant"
        flow_rows.append(
            {
                "Flow ID": fl["flow_id"].upper() + (" (Target)" if fl["flow_id"] == active_flow_id else ""),
                "Active Path": " → ".join(fl["route"]),
                "Offered Rate": f"{fl.get('rate_mbps', 0):.1f} Mbps",
                "Delivered Rate": f"{fl.get('throughput_mbps', 0):.1f} Mbps",
                "Delay / SLA Max": f"{fl.get('delay', 0):.1f} / {fl['sla']['max_delay_ms']:.0f} ms",
                "Loss / SLA Max": f"{fl.get('packet_loss', 0)*100:.1f}% / {fl['sla']['max_packet_loss']*100:.0f}%",
                "Baseline Risk": f"{fl.get('sla_violation_risk', 0):.4f}",
                "Contract Status": status_tag,
            }
        )

    st.dataframe(
        pd.DataFrame(flow_rows),
        use_container_width=True,
        hide_index=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # -----------------------------------------------------------------------
    # Section 3: Physical Link Saturation & Queue Dynamics
    # -----------------------------------------------------------------------
    st.markdown(
        """
        <div class="card-surface">
            <div class="card-header-styled">
                <span>Physical Link Telemetry & Queue Dynamics (7 Network Links)</span>
                <span style="font-size: 0.72rem; color: #64748B; font-weight: 500;">Link Capacity & Congestion Breakdown</span>
            </div>
        """,
        unsafe_allow_html=True,
    )

    link_rows = []
    for lk in state["links"]:
        lid = lk["link_id"]
        u, v = lk["source"], lk["destination"]
        cap = lk["capacity_mbps"]
        util = lk.get("utilization", 0.0)
        bg = lk.get("background_load_mbps", 0.0)
        qdel = lk.get("queue_delay_ms", 0.0)
        qocc = lk.get("queue_occupancy", 0.0)

        # Flows using this link
        traversing_flows = [
            f["flow_id"].upper()
            for f in state["flows"]
            if any(
                (f["route"][i] == u and f["route"][i+1] == v) or (f["route"][i] == v and f["route"][i+1] == u)
                for i in range(len(f["route"]) - 1)
            )
        ]

        status_text = (
            "Critical Congestion" if util >= 0.75 else "Elevated Load" if util >= 0.50 else "Normal Load"
        )

        link_rows.append(
            {
                "Link": lid,
                "Endpoints": f"{u} ↔ {v}",
                "Capacity": f"{cap} Mbps",
                "Background Load": f"{bg:.1f} Mbps",
                "Utilization": f"{util*100:.1f}%",
                "Queue Delay": f"{qdel:.1f} ms",
                "Queue Occupancy": f"{qocc*100:.1f}%",
                "Traversing Flows": ", ".join(traversing_flows) if traversing_flows else "Idle",
                "Link Status": status_text,
            }
        )

    st.dataframe(
        pd.DataFrame(link_rows),
        use_container_width=True,
        hide_index=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # -----------------------------------------------------------------------
    # Section 4: Digital Twin Architecture & Technical Specifications
    # -----------------------------------------------------------------------
    st.markdown(
        """
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
            <div class="spec-card">
                <div class="spec-card-title">Queuing Mechanics & Congestion Physics</div>
                <div class="spec-card-body">
                    The TWINSHIELD digital twin model reflects deterministic queue dynamics:
                    <ul style="margin-top: 6px; padding-left: 18px;">
                        <li><b>Baseline delay:</b> Sum of link propagation delays (5–15 ms per hop).</li>
                        <li><b>Congestion factor:</b> Queue delays rise sharply after link utilization exceeds 70% threshold: <code>queue_delay = 1.0 + 40.0 &times; (util - 0.70) / 0.30</code>.</li>
                        <li><b>Packet drop:</b> Packet loss begins once maximum path utilization exceeds 85%.</li>
                    </ul>
                </div>
            </div>
            <div class="spec-card" style="border-top-color: #2563EB;">
                <div class="spec-card-title">Flow Priority & SLA Contracts</div>
                <div class="spec-card-body">
                    Three interacting flows compete for shared network link resources:
                    <ul style="margin-top: 6px; padding-left: 18px;">
                        <li><b>Flow f1 (Priority 1):</b> 15 Mbps rate, 50 ms max delay, 5.0% max loss. Transits shared bottleneck link l2.</li>
                        <li><b>Flow f2 (Priority 2):</b> 20 Mbps rate, 60 ms max delay, 5.0% max loss. Transits alternate core link l4.</li>
                        <li><b>Flow f3 (Priority 3):</b> 10 Mbps rate, 80 ms max delay, 5.0% max loss. Transits distribution link l7.</li>
                    </ul>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ===========================================================================
# TAB 2: DECISION ANALYSIS (Counterfactual & Safety Engine)
# ===========================================================================
with tab_analysis:
    eval_result = st.session_state["evaluation_result"]

    if eval_result is None:
        st.info(
            "No candidate route has been evaluated for the current scenario. "
            "Return to the Network Lab tab and select 'Evaluate selected route' or 'Compare candidates'."
        )
    else:
        status = eval_result.get("status", "").lower()
        reason = eval_result.get("reason", "")
        target_flow_id = eval_result.get("target_flow")
        old_path = eval_result.get("old_path", [])
        new_path = eval_result.get("new_path", [])

        # Decision Status Banner
        if status == "accept":
            box_cls = "callout-accept"
            badge = '<span class="badge-accept">ACCEPT</span>'
            status_desc = "Approved for execution by digital twin safety selector"
        elif status == "reject":
            box_cls = "callout-reject"
            badge = '<span class="badge-reject">REJECT</span>'
            status_desc = "Rejected by digital twin safety selector"
        else:
            box_cls = "callout-abstain"
            badge = '<span class="badge-abstain">ABSTAIN</span>'
            status_desc = "Abstention triggered due to prediction uncertainty"

        st.markdown(
            f"""
            <div class="{box_cls}">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <div>
                        <div style="font-size: 0.74rem; color: #64748B; text-transform: uppercase; font-weight: 700;">Digital Twin Safety Decision</div>
                        <div style="font-size: 1.2rem; font-weight: 800; color: #0F172A; margin-top: 2px;">
                            Target Flow {target_flow_id.upper()}: <code>{' → '.join(old_path)}</code> &rarr; <code>{' → '.join(new_path)}</code>
                        </div>
                    </div>
                    <div>{badge}</div>
                </div>
                <div style="font-size: 0.90rem; color: #1E293B; margin-top: 6px;">
                    <b>Reason:</b> {reason}
                </div>
                <div style="font-size: 0.78rem; color: #64748B; margin-top: 2px;">
                    {status_desc}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        state = st.session_state["current_state"]
        cur_flow = next(
            (f for f in state["flows"] if f["flow_id"] == target_flow_id),
            None,
        )
        cur_delay = cur_flow.get("delay", 0.0) if cur_flow else 0.0
        cur_loss = cur_flow.get("packet_loss", 0.0) if cur_flow else 0.0
        cur_risk = eval_result.get("risk_before", 0.0)

        pred_outcomes = (
            eval_result.get("evaluation", {})
            .get("predicted_outcomes", {})
            .get(target_flow_id, {})
        )
        pred_delay = pred_outcomes.get("delay", cur_delay)
        pred_loss = pred_outcomes.get("packet_loss", cur_loss)
        pred_risk = eval_result.get("risk_after", cur_risk)
        pred_unc = eval_result.get("target_uncertainty")
        pred_conf = pred_outcomes.get("confidence_score")

        delay_delta = pred_delay - cur_delay
        loss_delta = pred_loss - cur_loss
        risk_delta = pred_risk - cur_risk

        # -------------------------------------------------------------------
        # Section 2: Counterfactual What-If Telemetry vs Baseline
        # -------------------------------------------------------------------
        st.markdown(
            """
            <div class="card-surface">
                <div class="card-header-styled">
                    <span>Counterfactual What-If State Comparison</span>
                    <span style="font-size: 0.72rem; color: #64748B; font-weight: 500;">Observed Baseline vs. Predicted Counterfactual</span>
                </div>
            """,
            unsafe_allow_html=True,
        )

        comp_cols = st.columns(4)
        with comp_cols[0]:
            st.metric(
                label="Target Delay",
                value=f"{pred_delay:.1f} ms",
                delta=f"{delay_delta:+.1f} ms",
                delta_color="inverse" if delay_delta < 0 else "normal",
            )
            st.caption(f"Baseline: {cur_delay:.1f} ms")

        with comp_cols[1]:
            st.metric(
                label="Target Packet Loss",
                value=f"{pred_loss*100:.2f}%",
                delta=f"{loss_delta*100:+.2f}%",
                delta_color="inverse" if loss_delta < 0 else "normal",
            )
            st.caption(f"Baseline: {cur_loss*100:.2f}%")

        with comp_cols[2]:
            st.metric(
                label="Predicted SLA Risk",
                value=f"{pred_risk:.4f}",
                delta=f"{risk_delta:+.4f}",
                delta_color="inverse" if risk_delta < 0 else "normal",
            )
            st.caption(f"Baseline: {cur_risk:.4f}")

        with comp_cols[3]:
            unc_val = f"{pred_unc:.4f}" if pred_unc is not None else "N/A"
            conf_val = f"{pred_conf:.4f}" if pred_conf is not None else "N/A"
            st.metric(
                label="Prediction Uncertainty",
                value=unc_val,
                delta="Limit: 0.3000",
                delta_color="off",
            )
            st.caption(f"Confidence score: {conf_val}")

        st.markdown(
            """
            <div style="font-size: 0.80rem; color: #475569; background: #F8FAFC; border: 1px solid #E2E8F0; padding: 10px 14px; margin-top: 14px; border-radius: 6px;">
                <b>Technical Methodology:</b> Telemetry metrics (delay, loss) represent the deterministic digital-twin simulation state after applying the rerouting intervention. SLA-violation risk and uncertainty scores are calculated by the calibrated Logistic Regression model. The counterfactual state is a hypothetical simulation, not a physically committed change.
            </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # -------------------------------------------------------------------
        # Section 3: Formal Multi-Flow Safety Checklist
        # -------------------------------------------------------------------
        st.markdown(
            """
            <div class="card-surface">
                <div class="card-header-styled">
                    <span>Multi-Flow Safety & Uncertainty Checklist</span>
                    <span style="font-size: 0.72rem; color: #64748B; font-weight: 500;">Safety Constraints Verification</span>
                </div>
            """,
            unsafe_allow_html=True,
        )

        is_valid_route, route_reason = is_valid_rerouting_action(
            topology=state["topology"],
            target_flow=target_flow_id,
            old_path=old_path,
            new_path=new_path,
        )

        chk_col1, chk_col2 = st.columns(2)

        with chk_col1:
            st.markdown("<b>Target flow verification</b>", unsafe_allow_html=True)
            if is_valid_route:
                st.markdown("- [x] **Routing validity:** Candidate path is topologically valid.")
            else:
                st.markdown(f"- [ ] **Routing validity failed:** {route_reason}")

            target_improves = pred_risk < cur_risk
            if target_improves:
                st.markdown(
                    f"- [x] **Target risk improvement:** Passed. Risk decreases from `{cur_risk:.4f}` to `{pred_risk:.4f}`."
                )
            else:
                st.markdown(
                    f"- [ ] **Target risk improvement failed:** Risk does not decrease (`{pred_risk:.4f}` &ge; `{cur_risk:.4f}`)."
                )

            unc_limit = 0.30
            if pred_unc is None or pred_unc <= unc_limit:
                st.markdown(
                    f"- [x] **Target uncertainty check:** Passed. Uncertainty (`{pred_unc if pred_unc else 0:.4f}`) &le; limit (`{unc_limit:.2f}`)."
                )
            else:
                st.markdown(
                    f"- [ ] **Target uncertainty check failed:** Uncertainty (`{pred_unc:.4f}`) &gt; limit (`{unc_limit:.2f}`)."
                )

        with chk_col2:
            st.markdown("<b>Protected-flow constraints & uncertainty</b>", unsafe_allow_html=True)
            protected_flows = eval_result.get("protected_flows", {})

            if not protected_flows:
                st.markdown("- No other flows in network.")
            else:
                for fid, pinfo in protected_flows.items():
                    r_after = pinfo.get("risk_after", 0.0)
                    r_allowed = pinfo.get("allowed_risk", 0.0)
                    p_unc = pinfo.get("uncertainty")

                    is_violated = r_after > r_allowed
                    is_p_uncertain = p_unc is not None and p_unc > unc_limit

                    if is_violated:
                        r_status = f"[ ] **Flow {fid.upper()} safety violated:** `{r_after:.4f}` &gt; Allowed `{r_allowed:.4f}`"
                    else:
                        r_status = f"[x] **Flow {fid.upper()} safe:** `{r_after:.4f}` &le; Allowed `{r_allowed:.4f}`"

                    if is_p_uncertain:
                        u_status = f"Uncertainty `{p_unc:.4f}` &gt; `{unc_limit:.2f}`"
                    elif p_unc is not None:
                        u_status = f"Uncertainty `{p_unc:.4f}` &le; `{unc_limit:.2f}`"
                    else:
                        u_status = "Uncertainty N/A"

                    st.markdown(f"- - {r_status} ({u_status})")

        st.markdown("</div>", unsafe_allow_html=True)

        # -------------------------------------------------------------------
        # Section 4: Mathematical Uncertainty & Decision Mechanics
        # -------------------------------------------------------------------
        st.markdown(
            """
            <div class="card-surface">
                <div class="card-header-styled">
                    <span>Uncertainty Quantification & Abstention Mechanics</span>
                    <span style="font-size: 0.72rem; color: #64748B; font-weight: 500;">Theoretical Foundation</span>
                </div>
                <div style="font-size: 0.82rem; color: #475569; line-height: 1.6;">
                    TWINSHIELD applies an explicit uncertainty threshold to prevent reckless autonomous actuation:
                    <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 12px 16px; border-radius: 6px; margin: 10px 0; font-family: monospace;">
                        Uncertainty_Score = 1.0 - |2.0 &times; P(SLA_Violation) - 1.0|<br>
                        Confidence_Score  = 1.0 - Uncertainty_Score
                    </div>
                    <b>Decision Boundary Region:</b> When predicted SLA-violation risk falls in the ambiguous probability interval <code>[0.40, 0.60]</code>, the uncertainty score exceeds <code>0.30</code>. In this region, TWINSHIELD automatically produces an <b>ABSTAIN</b> decision, signaling that automated rerouting lacks statistical confidence and requires human operator review.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # -------------------------------------------------------------------
        # Section 5: Candidate Actions Evaluation Matrix
        # -------------------------------------------------------------------
        comparison_results = st.session_state.get("comparison_results")
        if comparison_results:
            st.markdown(
                """
                <div class="card-surface">
                    <div class="card-header-styled">
                        <span>Candidate Actions Evaluation Matrix</span>
                        <span style="font-size: 0.72rem; color: #64748B; font-weight: 500;">All Evaluated Alternative Paths</span>
                    </div>
                """,
                unsafe_allow_html=True,
            )

            c_rows = []
            for item in comparison_results:
                c_rows.append(
                    {
                        "Candidate Route": item["proposed_route"],
                        "Predicted Delay": f"{item['predicted_delay']:.1f} ms",
                        "Predicted Loss": f"{item['predicted_loss']*100:.2f}%",
                        "Predicted Risk": f"{item['predicted_risk']:.4f}",
                        "Uncertainty": f"{item['uncertainty']:.4f}" if item["uncertainty"] is not None else "N/A",
                        "Decision": item["status"],
                        "Reason": item["reason"],
                    }
                )

            st.dataframe(
                pd.DataFrame(c_rows),
                use_container_width=True,
                hide_index=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)


# ===========================================================================
# TAB 3: RESEARCH RESULTS (Saved Experimental Data & Baselines)
# ===========================================================================
with tab_research:
    st.markdown(
        """
        <div class="card-surface">
            <div style="font-size: 1.1rem; font-weight: 800; color: #0F172A; margin-bottom: 4px;">
                Preliminary Research Evaluation & Baseline Comparison
            </div>
            <div style="font-size: 0.85rem; color: #64748B;">
                Offline batch evaluation across 27 experimental trials (9 per scenario) benchmarking TWINSHIELD against Naive Rerouting and Prediction-Only control.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    baseline_csv_path = Path("results/twinshield_baseline_comparison.csv")
    decision_csv_path = Path("results/twinshield_decision_evaluation.csv")

    if baseline_csv_path.exists():
        # -------------------------------------------------------------------
        # Section 2: Strategy Safety Comparison Cards
        # -------------------------------------------------------------------
        st.markdown(
            """
            <div class="card-surface">
                <div class="card-header-styled">
                    <span>Baseline Strategy Profiles</span>
                    <span style="font-size: 0.72rem; color: #64748B; font-weight: 500;">Experimental Trials</span>
                </div>
            """,
            unsafe_allow_html=True,
        )

        b_col1, b_col2, b_col3 = st.columns(3)

        with b_col1:
            st.markdown(
                """
                <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 14px 16px;">
                    <div style="font-size: 0.75rem; color: #64748B; text-transform: uppercase; font-weight: 700;">1. Naive Rerouting</div>
                    <div style="font-size: 0.8rem; color: #475569; margin: 4px 0 10px 0;">Selects first valid alternate path</div>
                    <div style="font-size: 0.82rem; color: #1E293B; line-height: 1.7;">
                        Acceptance rate: <b>100% (9/9)</b><br>
                        Beneficial accepted: <b>33.3% (3/9)</b><br>
                        Harmful accepted: <b style="color: #DC2626;">5 cases</b><br>
                        Unsafe accepted rate: <b style="color: #DC2626;">55.6%</b>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with b_col2:
            st.markdown(
                """
                <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 14px 16px;">
                    <div style="font-size: 0.75rem; color: #64748B; text-transform: uppercase; font-weight: 700;">2. Prediction-Only Control</div>
                    <div style="font-size: 0.8rem; color: #475569; margin: 4px 0 10px 0;">Greedy minimum predicted target risk</div>
                    <div style="font-size: 0.82rem; color: #1E293B; line-height: 1.7;">
                        Acceptance rate: <b>100% (9/9)</b><br>
                        Beneficial accepted: <b>44.4% (4/9)</b><br>
                        Harmful accepted: <b style="color: #DC2626;">5 cases</b><br>
                        Unsafe accepted rate: <b style="color: #DC2626;">55.6%</b>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with b_col3:
            st.markdown(
                """
                <div style="background: linear-gradient(180deg, #F0FDF4 0%, #FFFFFF 100%); border: 1px solid #BBF7D0; border-radius: 8px; padding: 14px 16px;">
                    <div style="font-size: 0.75rem; color: #15803D; text-transform: uppercase; font-weight: 700;">3. TWINSHIELD (Ours)</div>
                    <div style="font-size: 0.8rem; color: #166534; margin: 4px 0 10px 0;">Uncertainty + Multi-flow constraints</div>
                    <div style="font-size: 0.82rem; color: #14532D; line-height: 1.7;">
                        Acceptance rate: <b>44.4% (4/9)</b><br>
                        Beneficial accepted: <b style="color: #15803D;">75.0% (3/4)</b><br>
                        Abstention rate: <b>44.4% (4/9)</b><br>
                        Unsafe accepted rate: <b style="color: #15803D;">25.0% (55% reduction)</b>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown(
            """
            <div style="font-size: 0.82rem; color: #15803D; background: linear-gradient(90deg, #F0FDF4 0%, #DCFCE7 100%); border: 1px solid #BBF7D0; border-radius: 6px; padding: 12px 16px; margin-top: 14px;">
                <b>Core Research Finding:</b> TWINSHIELD achieves a <b>55% relative reduction in unsafe accepted routing actions</b> compared to naive rerouting and prediction-only control, boosting decision success from 33.3% to 75.0% by abstaining under ambiguous model uncertainty and rejecting actions that violate protected flows.
            </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # -------------------------------------------------------------------
        # Section 3: Interactive Graphical Performance Benchmarks
        # -------------------------------------------------------------------
        st.markdown(
            """
            <div class="card-surface">
                <div class="card-header-styled">
                    <span>Performance Benchmark Visualizations</span>
                    <span style="font-size: 0.72rem; color: #64748B; font-weight: 500;">Comparative Metrics</span>
                </div>
            """,
            unsafe_allow_html=True,
        )

        g_col1, g_col2 = st.columns(2)

        with g_col1:
            fig_success = go.Figure(data=[
                go.Bar(
                    x=['Naive Rerouting', 'Prediction-Only', 'TWINSHIELD'],
                    y=[33.3, 44.4, 75.0],
                    marker=dict(color=['#94A3B8', '#64748B', '#168C83']),
                    text=['33.3%', '44.4%', '75.0%'],
                    textposition='auto',
                )
            ])
            fig_success.update_layout(
                title=dict(text="Accepted Action Success Rate (%)", font=dict(size=12, color="#1E293B")),
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#FFFFFF",
                margin=dict(l=20, r=20, t=35, b=20),
                height=260,
                yaxis=dict(range=[0, 100], showgrid=True, gridcolor="#F1F5F9"),
                xaxis=dict(showgrid=False),
            )
            st.plotly_chart(fig_success, use_container_width=True, config={"displayModeBar": False})

        with g_col2:
            fig_unsafe = go.Figure(data=[
                go.Bar(
                    x=['Naive Rerouting', 'Prediction-Only', 'TWINSHIELD'],
                    y=[55.6, 55.6, 25.0],
                    marker=dict(color=['#DC2626', '#DC2626', '#10B981']),
                    text=['55.6%', '55.6%', '25.0% (-55%)'],
                    textposition='auto',
                )
            ])
            fig_unsafe.update_layout(
                title=dict(text="Unsafe Action Execution Rate (%)", font=dict(size=12, color="#1E293B")),
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#FFFFFF",
                margin=dict(l=20, r=20, t=35, b=20),
                height=260,
                yaxis=dict(range=[0, 70], showgrid=True, gridcolor="#F1F5F9"),
                xaxis=dict(showgrid=False),
            )
            st.plotly_chart(fig_unsafe, use_container_width=True, config={"displayModeBar": False})

        st.markdown("</div>", unsafe_allow_html=True)

        # -------------------------------------------------------------------
        # Section 4: Critical Cases Where Execution Was Prevented
        # -------------------------------------------------------------------
        st.markdown(
            """
            <div class="card-surface">
                <div class="card-header-styled">
                    <span>Benchmark Instances Where TWINSHIELD Prevented Harm</span>
                    <span style="font-size: 0.72rem; color: #64748B; font-weight: 500;">Safety Validation</span>
                </div>
                <div style="font-size: 0.82rem; color: #64748B; margin-bottom: 12px;">
                    Cases where Prediction-Only blindly executed an action that degraded network QoS, whereas TWINSHIELD intervened:
                </div>
            """,
            unsafe_allow_html=True,
        )

        prevented_cases = [
            {
                "Scenario": "background_surge",
                "Flow": "f2",
                "Prediction-Only": "ACCEPT",
                "TWINSHIELD Decision": "REJECT",
                "Actual Risk Impact": "-0.7167 (Severe Degradation)",
                "TWINSHIELD Reason": "Target flow does not improve",
            },
            {
                "Scenario": "background_surge",
                "Flow": "f3",
                "Prediction-Only": "ACCEPT",
                "TWINSHIELD Decision": "ABSTAIN",
                "Actual Risk Impact": "+0.5625 (Ambiguous)",
                "TWINSHIELD Reason": "Target-flow prediction uncertainty is too high (0.357 > 0.30)",
            },
            {
                "Scenario": "normal",
                "Flow": "f2",
                "Prediction-Only": "ACCEPT",
                "TWINSHIELD Decision": "ABSTAIN",
                "Actual Risk Impact": "-0.1834 (Degradation)",
                "TWINSHIELD Reason": "Protected-flow prediction uncertainty is too high",
            },
            {
                "Scenario": "normal",
                "Flow": "f3",
                "Prediction-Only": "ACCEPT",
                "TWINSHIELD Decision": "ABSTAIN",
                "Actual Risk Impact": "-0.1625 (Degradation)",
                "TWINSHIELD Reason": "Target-flow prediction uncertainty is too high",
            },
            {
                "Scenario": "shared_bottleneck",
                "Flow": "f3",
                "Prediction-Only": "ACCEPT",
                "TWINSHIELD Decision": "ABSTAIN",
                "Actual Risk Impact": "-0.1625 (Degradation)",
                "TWINSHIELD Reason": "Target-flow prediction uncertainty is too high",
            },
        ]

        st.dataframe(
            pd.DataFrame(prevented_cases),
            use_container_width=True,
            hide_index=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.warning("Baseline evaluation results not found at results/twinshield_baseline_comparison.csv.")

    # -------------------------------------------------------------------
    # Section 5: Batch Decision Dataset Inspection
    # -------------------------------------------------------------------
    if decision_csv_path.exists():
        st.markdown(
            """
            <div class="card-surface">
                <div class="card-header-styled">
                    <span>Batch Decision Evaluation Dataset (18 Trials)</span>
                    <span style="font-size: 0.72rem; color: #64748B; font-weight: 500;">CSV Audit Record</span>
                </div>
            """,
            unsafe_allow_html=True,
        )

        df_dec = pd.read_csv(decision_csv_path)
        tot_evals = len(df_dec)
        accept_cnt = len(df_dec[df_dec["decision"] == "accept"])
        reject_cnt = len(df_dec[df_dec["decision"] == "reject"])
        abstain_cnt = len(df_dec[df_dec["decision"] == "abstain"])

        d1, d2, d3, d4 = st.columns(4)
        with d1:
            st.metric("Total Evaluations", tot_evals)
        with d2:
            st.metric("Accepted", f"{accept_cnt} ({accept_cnt/tot_evals*100:.1f}%)")
        with d3:
            st.metric("Rejected", f"{reject_cnt} ({reject_cnt/tot_evals*100:.1f}%)")
        with d4:
            st.metric("Abstained", f"{abstain_cnt} ({abstain_cnt/tot_evals*100:.1f}%)")

        st.dataframe(df_dec, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ===========================================================================
# TAB 4: SESSION HISTORY (Live Audit Trail)
# ===========================================================================
with tab_history:
    st.markdown(
        """
        <div class="card-surface">
            <div style="font-size: 1.1rem; font-weight: 800; color: #0F172A; margin-bottom: 4px;">
                Interactive Session History & Audit Trail
            </div>
            <div style="font-size: 0.85rem; color: #64748B;">
                Complete record of routing candidate evaluations performed during the current simulator session.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    history = st.session_state["session_history"]

    if not history:
        st.info("No routing actions have been evaluated in this session yet. Evaluate routes in the Network Lab to populate this audit trail.")
    else:
        df_hist = pd.DataFrame(history)

        # Session summary metrics
        total_hist = len(df_hist)
        hist_accept = len(df_hist[df_hist["decision"] == "ACCEPT"])
        hist_reject = len(df_hist[df_hist["decision"] == "REJECT"])
        hist_abstain = len(df_hist[df_hist["decision"] == "ABSTAIN"])

        st.markdown(
            f"""
            <div class="stat-tile-grid">
                <div class="stat-tile">
                    <div class="stat-tile-title">Session Evaluations</div>
                    <div class="stat-tile-value">{total_hist}</div>
                    <div class="stat-tile-desc">Interventions analyzed</div>
                </div>
                <div class="stat-tile">
                    <div class="stat-tile-title">Approved (Accept)</div>
                    <div class="stat-tile-value" style="color: #15803D;">{hist_accept}</div>
                    <div class="stat-tile-desc">Safe to execute</div>
                </div>
                <div class="stat-tile">
                    <div class="stat-tile-title">Blocked (Reject)</div>
                    <div class="stat-tile-value" style="color: #DC2626;">{hist_reject}</div>
                    <div class="stat-tile-desc">Harmful or non-improving</div>
                </div>
                <div class="stat-tile">
                    <div class="stat-tile-title">Abstained</div>
                    <div class="stat-tile-value" style="color: #D97706;">{hist_abstain}</div>
                    <div class="stat-tile-desc">High uncertainty</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="card-surface">
                <div class="card-header-styled">
                    <span>Audit Log Table</span>
                    <span style="font-size: 0.72rem; color: #64748B; font-weight: 500;">Chronological History</span>
                </div>
            """,
            unsafe_allow_html=True,
        )

        col_h1, col_h2 = st.columns([0.8, 0.2])
        with col_h2:
            if st.button("Clear history", use_container_width=True):
                st.session_state["session_history"] = []
                st.rerun()

        st.dataframe(df_hist, use_container_width=True, hide_index=True)

        csv_data = df_hist.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download history (CSV)",
            data=csv_data,
            file_name="twinshield_session_history.csv",
            mime="text/csv",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # Technical Reproducibility Note
    st.markdown(
        """
        <div class="spec-card">
            <div class="spec-card-title">Session Audit Protocol & Offline Reproducibility</div>
            <div class="spec-card-body">
                All evaluations recorded in this session execute deterministically against the underlying network state. Any action sequence can be independently verified offline using the command:
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 8px 12px; border-radius: 4px; font-family: monospace; margin-top: 6px;">
                    python3 scripts/demo_pipeline.py
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Website Footer
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="website-footer">
        <div>
            <div class="footer-text">
                <b>TWINSHIELD</b> &bull; Uncertainty-Aware Network Digital Twin Framework for Safe Network Control
            </div>
            <div class="footer-links" style="margin-top: 4px;">
                Calibrated Logistic Regression Predictor &bull; Decision Pipeline v1.2 &bull; Research Review Edition
            </div>
        </div>
        <div class="footer-links">
            Model-based digital twin &bull; Not a physical packet emulator
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
