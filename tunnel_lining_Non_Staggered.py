import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(layout="wide")
st.title("Segmental Tunnel Visualization (Without Trimesh)")

# --- Sidebar inputs ---
with st.sidebar:
    st.header("Tunnel Parameters")
    outer_radius = st.slider("Outer Radius (m)", 1.0, 10.0, 4.7)
    thickness = st.slider("Lining Thickness (m)", 0.1, 1.0, 0.2)
    ring_width = st.slider("Ring Width (m)", 0.5, 5.0, 2.1)
    num_segments = st.slider("Segments per Ring", 2, 12, 6)
    num_rings = st.slider("Number of Rings", 1, 20, 10)

# Calculate derived values
inner_radius = outer_radius - thickness
tunnel_length = ring_width * num_rings
sweep_angle = 2 * np.pi / num_segments
colors = px.colors.qualitative.Plotly

# Function to create vertices of a ring segment
def create_segment(angle_start, angle_end, radius_in, radius_out, width, y_shift):
    resolution = 30  # number of points per arc
    angles = np.linspace(angle_start, angle_end, resolution)

    # Outer arc
    x_outer = radius_out * np.cos(angles)
    z_outer = radius_out * np.sin(angles)

    # Inner arc (reversed for continuity)
    x_inner = (radius_in * np.cos(angles[::-1]))
    z_inner = (radius_in * np.sin(angles[::-1]))

    x = np.concatenate([x_outer, x_inner])
    z = np.concatenate([z_outer, z_inner])
    y = np.full_like(x, y_shift)

    return x, y, z

# --- Plotting ---
fig = go.Figure()

for r in range(num_rings):
    for s in range(num_segments):
        angle_start = s * sweep_angle
        angle_end = angle_start + sweep_angle

        x, y, z = create_segment(angle_start, angle_end, inner_radius, outer_radius, ring_width, r * ring_width)

        fig.add_trace(go.Mesh3d(
            x=np.concatenate([x, x]),
            y=np.concatenate([y, y + ring_width]),
            z=np.concatenate([z, z]),
            i=[0, 1, 2],
            j=[3, 4, 5],
            k=[6, 7, 8],
            opacity=0.8,
            color=colors[s % len(colors)],
            name=f"Ring {r+1} Segment {s+1}",
            hoverinfo="name"
        ))

fig.update_layout(
    scene=dict(
        xaxis_title="X (m)",
        yaxis_title="Y (Tunnel Length)",
        zaxis_title="Z (m)",
        aspectmode='data'
    ),
    margin=dict(l=0, r=0, t=30, b=0)
)

st.markdown(f"### Total Tunnel Length: **{tunnel_length:.2f} m**")
st.plotly_chart(fig, use_container_width=True)
