import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(layout="wide")
st.title("Segmental Tunnel (Streamlit Compatible Replica)")

# Sidebar Parameters
with st.sidebar:
    st.header("Tunnel Parameters")
    outer_radius = st.slider("Outer Radius (m)", 1.0, 10.0, 4.7)
    thickness = st.slider("Lining Thickness (m)", 0.1, 1.0, 0.2)
    ring_width = st.slider("Ring Width (m)", 0.5, 5.0, 2.1)
    num_segments = st.slider("Segments per Ring", 2, 12, 6)
    num_rings = st.slider("Number of Rings", 1, 20, 10)

inner_radius = outer_radius - thickness
tunnel_length = ring_width * num_rings
sweep_angle = 2 * np.pi / num_segments
colors = px.colors.qualitative.Plotly

st.markdown(f"### Total Tunnel Length: **{tunnel_length:.2f} m**")

# Function to build 3D wedge-like segment geometry
def create_segment_mesh(a0, a1, r_in, r_out, y0, width, resolution=10):
    angles = np.linspace(a0, a1, resolution)

    # Outer arcs
    x_outer_front = r_out * np.cos(angles)
    z_outer_front = r_out * np.sin(angles)
    x_outer_back = x_outer_front
    z_outer_back = z_outer_front

    # Inner arcs
    x_inner_front = r_in * np.cos(angles[::-1])
    z_inner_front = r_in * np.sin(angles[::-1])
    x_inner_back = x_inner_front
    z_inner_back = z_inner_front

    # Y positions
    y_front = np.full_like(x_outer_front, y0)
    y_back = np.full_like(x_outer_front, y0 + width)

    # Stack all vertices
    x = np.concatenate([x_outer_front, x_inner_front, x_outer_back, x_inner_back])
    y = np.concatenate([y_front, y_front, y_back, y_back])
    z = np.concatenate([z_outer_front, z_inner_front, z_outer_back, z_inner_back])

    n = len(angles)
    faces = []

    # Side faces
    for i in range(n - 1):
        # Front ring wall
        faces.append([i, i + 1, n + i + 1])
        faces.append([i, n + i + 1, n + i])

        # Back ring wall
        faces.append([2 * n + i, 2 * n + i + 1, 3 * n + i + 1])
        faces.append([2 * n + i, 3 * n + i + 1, 3 * n + i])

        # Outer arc connection
        faces.append([i, 2 * n + i, 2 * n + i + 1])
        faces.append([i, 2 * n + i + 1, i + 1])

        # Inner arc connection
        faces.append([n + i, 3 * n + i, 3 * n + i + 1])
        faces.append([n + i, 3 * n + i + 1, n + i + 1])

    return x, y, z, np.array(faces)

# Plotting
fig = go.Figure()

for r in range(num_rings):
    for s in range(num_segments):
        angle_start = s * sweep_angle
        angle_end = angle_start + sweep_angle
        y_pos = r * ring_width

        x, y, z, faces = create_segment_mesh(angle_start, angle_end, inner_radius, outer_radius, y_pos, ring_width)

        fig.add_trace(go.Mesh3d(
            x=x, y=y, z=z,
            i=faces[:, 0], j=faces[:, 1], k=faces[:, 2],
            color=colors[s % len(colors)],
            opacity=0.85,
            name=f"Ring {r + 1} Segment {s + 1}",
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

st.plotly_chart(fig, use_container_width=True)
