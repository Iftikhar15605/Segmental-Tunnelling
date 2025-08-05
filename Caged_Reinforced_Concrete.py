import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(layout="wide")
st.title("Staggered Tunnel with Circular Rebars (Streamlit-Compatible)")

# Sidebar Parameters
with st.sidebar:
    st.header("Tunnel Parameters")
    outer_radius = st.slider("Outer Radius (m)", 2.0, 10.0, 4.7)
    lining_thickness = st.slider("Lining Thickness (m)", 0.1, 1.0, 0.3)
    ring_width = st.slider("Ring Width (m)", 0.5, 5.0, 2.1)
    num_segments = st.slider("Segments per Ring", 2, 12, 6)
    num_rings = st.slider("Number of Rings", 1, 20, 10)
    show_tunnel = st.checkbox("Show Tunnel Lining", value=True)

    st.header("Reinforcement Parameters")
    show_reinforcement = st.checkbox("Show Circular Rebars (Hoops)", value=True)
    rebar_radius = st.slider("Rebar Radius (m)", 0.01, 0.1, 0.03)
    concrete_cover = st.slider("Concrete Cover (m)", 0.01, 0.2, 0.05)
    num_hoops_per_ring = st.slider("Circular Rebars (Hoops) per Ring", 1, 10, 4)

tunnel_length = num_rings * ring_width
inner_radius = outer_radius - lining_thickness
st.markdown(f"### Total Tunnel Length: **{tunnel_length:.2f} m**")

sweep_angle = 2 * np.pi / num_segments
colors = px.colors.qualitative.Plotly

# --- Functions ---

def create_ring_segment(angle_start, angle_end, r_in, r_out, y0, width, resolution=30):
    theta = np.linspace(angle_start, angle_end, resolution)

    # Outer arc
    x_outer = r_out * np.cos(theta)
    z_outer = r_out * np.sin(theta)

    # Inner arc
    x_inner = r_in * np.cos(theta[::-1])
    z_inner = r_in * np.sin(theta[::-1])

    x = np.concatenate([x_outer, x_inner])
    z = np.concatenate([z_outer, z_inner])
    y = np.full_like(x, y0)

    # Extrude in Y
    x_full = np.concatenate([x, x])
    y_full = np.concatenate([y, y + width])
    z_full = np.concatenate([z, z])

    n = len(x)
    faces = []
    for i in range(n - 1):
        faces.append([i, i + 1, i + n + 1])
        faces.append([i, i + n + 1, i + n])
    return x_full, y_full, z_full, np.array(faces)

def create_circular_hoop(r_mid, r_thick, y_pos, resolution=30):
    theta = np.linspace(0, 2 * np.pi, resolution)
    x = r_mid * np.cos(theta)
    z = r_mid * np.sin(theta)
    y = np.full_like(x, y_pos)

    # Create tube by extrusion
    x_full = np.concatenate([x, x])
    y_full = np.concatenate([y - r_thick, y + r_thick])
    z_full = np.concatenate([z, z])

    n = len(x)
    faces = []
    for i in range(n - 1):
        faces.append([i, i + 1, i + n + 1])
        faces.append([i, i + n + 1, i + n])
    return x_full, y_full, z_full, np.array(faces)

# --- Build Geometry ---

fig = go.Figure()

for r in range(num_rings):
    y_pos = r * ring_width
    angle_offset = sweep_angle / 2 if r % 2 == 1 else 0

    for s in range(num_segments):
        angle_start = s * sweep_angle + angle_offset
        angle_end = angle_start + sweep_angle

        if show_tunnel:
            x, y, z, faces = create_ring_segment(angle_start, angle_end, inner_radius, outer_radius, y_pos, ring_width)
            fig.add_trace(go.Mesh3d(
                x=x, y=y, z=z,
                i=faces[:, 0], j=faces[:, 1], k=faces[:, 2],
                color=colors[s % len(colors)],
                opacity=0.85,
                name=f"Ring {r + 1} Segment {s + 1}"
            ))

    if show_reinforcement:
        hoop_radius = outer_radius - lining_thickness + concrete_cover
        for h in range(num_hoops_per_ring):
            y_hoop = y_pos + (ring_width / (num_hoops_per_ring + 1)) * (h + 1)
            x, y_, z, faces = create_circular_hoop(hoop_radius, rebar_radius, y_hoop)
            fig.add_trace(go.Mesh3d(
                x=x, y=y_, z=z,
                i=faces[:, 0], j=faces[:, 1], k=faces[:, 2],
                color='red',
                opacity=1.0,
                name=f"Hoop {h+1} @ Ring {r+1}"
            ))

fig.update_layout(
    scene=dict(
        xaxis_title="X",
        yaxis_title="Y (Tunnel Length)",
        zaxis_title="Z",
        aspectmode='data'
    ),
    margin=dict(l=0, r=0, t=30, b=0)
)

st.plotly_chart(fig, use_container_width=True)
