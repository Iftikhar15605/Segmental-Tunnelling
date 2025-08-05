import streamlit as st
import trimesh
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(layout="wide")
st.title("Segmental Tunnel (Same Axis as Rhino IronPython)")

# --- Sidebar parameters ---
with st.sidebar:
    st.header("Tunnel Parameters")
    outer_radius = st.slider("Outer Radius (m)", 1.0, 10.0, 4.7)
    thickness = st.slider("Lining Thickness (m)", 0.1, 1.0, 0.2)
    ring_width = st.slider("Ring Width (m)", 0.5, 5.0, 2.1)
    num_segments = st.slider("Segments per Ring", 2, 12, 6)
    num_rings = st.slider("Number of Rings", 1, 20, 10)

# Calculate tunnel length
tunnel_length = num_rings * ring_width
st.markdown(f"### Total Tunnel Length: **{tunnel_length:.2f} m**")

def create_ring_segment(outer_radius, thickness, width, start_angle, sweep_angle):
    inner_radius = outer_radius - thickness

    # Create hollow ring (outer - inner)
    outer_cyl = trimesh.creation.cylinder(radius=outer_radius, height=width)
    inner_cyl = trimesh.creation.cylinder(radius=inner_radius, height=width)
    hollow_ring = outer_cyl.difference(inner_cyl)

    # Slice for segment
    seg = hollow_ring.copy()
    normal1 = [np.sin(np.radians(start_angle)), -np.cos(np.radians(start_angle)), 0]
    normal2 = [-np.sin(np.radians(start_angle + sweep_angle)), np.cos(np.radians(start_angle + sweep_angle)), 0]
    origin = [0, 0, 0]

    seg = seg.slice_plane(plane_origin=origin, plane_normal=normal1)
    seg = seg.slice_plane(plane_origin=origin, plane_normal=normal2)

    # Rotate around X-axis (like IronPython script)
    rotation_matrix = trimesh.transformations.rotation_matrix(np.radians(90), [1, 0, 0])
    seg.apply_transform(rotation_matrix)

    return seg

def create_tunnel(outer_radius, thickness, ring_width, num_segments, num_rings):
    sweep_angle = 360 / num_segments
    segments = []

    # Create segments for one ring
    for i in range(num_segments):
        start_angle = i * sweep_angle
        seg = create_ring_segment(outer_radius, thickness, ring_width, start_angle, sweep_angle)
        segments.append(seg)

    # Stack rings along Y-axis
    tunnel = []
    for r in range(num_rings):
        y_pos = r * ring_width
        for seg in segments:
            seg_copy = seg.copy()
            seg_copy.apply_translation([0, y_pos, 0])  # Move ring along Y-axis
            tunnel.append(seg_copy)

    return tunnel

# Build tunnel geometry
tunnel_segments = create_tunnel(outer_radius, thickness, ring_width, num_segments, num_rings)

# Plot the tunnel
colors = px.colors.qualitative.Plotly
fig = go.Figure()

for idx, seg in enumerate(tunnel_segments):
    verts = np.array(seg.vertices)
    faces = np.array(seg.faces)
    x, y, z = verts.T
    i, j, k = faces.T

    fig.add_trace(go.Mesh3d(
        x=x, y=y, z=z,
        i=i, j=j, k=k,
        opacity=0.85,
        color=colors[idx % len(colors)],
        name=f"Ring {idx // num_segments + 1} - Segment {idx % num_segments + 1}",
        hoverinfo="name"
    ))

fig.update_layout(
    scene=dict(
        xaxis=dict(title='X (m)'),
        yaxis=dict(title='Y (Tunnel Length)'),
        zaxis=dict(title='Z (m)'),
        aspectmode='data'
    ),
    margin=dict(l=0, r=0, t=30, b=0)
)

st.plotly_chart(fig, use_container_width=True)
