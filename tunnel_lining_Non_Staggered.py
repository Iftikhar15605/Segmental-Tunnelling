import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(layout="wide")
st.title("Segmental Tunnel Visualization (Streamlit-Compatible, 3D Wedge View)")

# --- Sidebar inputs ---
with st.sidebar:
    st.header("Tunnel Parameters")
    outer_radius = st.slider("Outer Radius (m)", 1.0, 10.0, 4.7)
    thickness = st.slider("Lining Thickness (m)", 0.1, 1.0, 0.2)
    ring_width = st.slider("Ring Width (m)", 0.5, 5.0, 2.1)
    num_segments = st.slider("Segments per Ring", 2, 12, 6)
    num_rings = st.slider("Number of Rings", 1, 20, 10)

# Derived values
inner_radius = outer_radius - thickness
tunnel_length = ring_width * num_rings
sweep_angle = 2 * np.pi / num_segments
colors = px.colors.qualitative.Plotly

# Function to create wedge vertices for a tunnel segment
def create_segment_wedge(angle_start, angle_end, r_in, r_out, width, y_shift):
    res = 10
    angles = np.linspace(angle_start, angle_end, res)

    # Outer and inner arc at front and back faces
    outer_front = np.array([[r_out * np.cos(a), y_shift, r_out * np.sin(a)] for a in angles])
    outer_back  = np.array([[r_out * np.cos(a), y_shift + width, r_out * np.sin(a)] for a in angles])
    inner_front = np.array([[r_in * np.cos(a), y_shift, r_in * np.sin(a)] for a in reversed(angles)])
    inner_back  = np.array([[r_in * np.cos(a), y_shift + width, r_in * np.sin(a)] for a in reversed(angles)])

    vertices = np.vstack([outer_front, outer_back, inner_front, inner_back])
    return vertices

# Function to create faces from vertices
def create_faces(n_outer, n_inner):
    faces = []

    # Side faces (outer ring)
    for i in range(n_outer - 1):
        faces.append([i, i + 1, i + n_outer])
        faces.append([i + 1, i + 1 + n_outer, i + n_outer])
    offset = 2 * n_outer

    # Side faces (inner ring)
    for i in range(n_inner - 1):
        faces.append([offset + i, offset + i + 1, offset + i + n_inner])
        faces.append([offset + i + 1, offset + i + 1 + n_inner, offset + i + n_inner])

    return np.array(faces)

# --- Plotting ---
fig = go.Figure()

for r in range(num_rings):
    for s in range(num_segments):
        a_start = s * sweep_angle
        a_end = a_start + sweep_angle
        vtx = create_segment_wedge(a_start, a_end, inner_radius, outer_radius, ring_width, r * ring_width)
        face = create_faces(res := 10, res)

        fig.add_trace(go.Mesh3d(
            x=vtx[:, 0], y=vtx[:, 1], z=vtx[:, 2],
            i=face[:, 0], j=face[:, 1], k=face[:, 2],
            color=colors[s % len(colors)],
            opacity=0.85,
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


