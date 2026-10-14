"""Oppimisympäristön yhteinen kuvaajatyyli ja esimerkkiasetusten valinta."""
import plotly.graph_objects as go
import streamlit as st

COLORS = ["#2563EB", "#D97706", "#059669", "#9333EA", "#DB2777", "#0891B2", "#64748B"]
INK = "#172B4D"
MUTED = "#64748B"
POTENTIAL = "#334155"
THRESHOLD = "#DC2626"
SELECTED = "#9333EA"


def style_plot(fig, height=None):
    """Yhtenäinen, vaaleapohjainen ja luettava tyyli kaikille kuvaajille."""
    fig.update_layout(
        template="plotly_white", colorway=COLORS,
        font=dict(family="Arial, sans-serif", size=14, color=INK),
        title_font=dict(size=19, color=INK), paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF", margin=dict(l=65, r=30, t=75, b=85),
        legend=dict(orientation="h", yanchor="top", y=-.24, x=0,
                    font=dict(size=12), bgcolor="rgba(255,255,255,0)"),
        hoverlabel=dict(bgcolor="#FFFFFF", font_size=13),
    )
    if height is not None:
        fig.update_layout(height=height)
    fig.update_xaxes(gridcolor="#E9EEF5", zerolinecolor="#CBD5E1", title_standoff=15,
                     ticks="outside", tickcolor="#CBD5E1", automargin=True)
    fig.update_yaxes(gridcolor="#E9EEF5", zerolinecolor="#CBD5E1", title_standoff=15,
                     ticks="outside", tickcolor="#CBD5E1", automargin=True)
    return fig


def show_plot(fig, **kwargs):
    return st.plotly_chart(style_plot(fig), width="stretch", config={
        "displaylogo": False, "scrollZoom": False,
        "toImageButtonOptions": {"format": "png", "filename": "kuvaaja", "scale": 2},
    }, **kwargs)


def initialise(defaults):
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def preset_picker(prefix, examples, descriptions=None, container=None):
    """Lataa nimetty alkutilanne ennen saman sivun parametrien näyttämistä."""
    container = st.sidebar if container is None else container
    options = ["Vapaa tutkiminen", *examples]
    key = f"{prefix}_example"
    if st.session_state.get(key, options[0]) not in options:
        st.session_state[key] = options[0]

    def apply_example():
        choice = st.session_state[key]
        for name, value in examples.get(choice, {}).items():
            st.session_state[name] = value

    choice = container.selectbox("Valmis esimerkki", options, key=key, on_change=apply_example)
    container.button("Palauta esimerkin asetukset", key=f"{prefix}_reload",
                     on_click=apply_example, disabled=choice == options[0])
    if descriptions and choice in descriptions:
        container.caption(descriptions[choice])
    return choice


def orbital_energy_figure(result, selected, include_core=False):
    """Valittavat HF-energiatasot; mukautettu tieto sisältää orbitaalin indeksin."""
    homo, n = result["homo_idx"], result["n_basis"]
    indices = list(range(n)) if include_core else sorted(
        set(range(max(0, homo - 3), min(n, homo + 5))) | {int(selected)})
    fig = go.Figure()
    groups = [("Miehitetty", [i for i in indices if i <= homo and i != selected], COLORS[0]),
              ("Miehittämätön", [i for i in indices if i > homo and i != selected], COLORS[1]),
              ("Valittu orbitaali", [int(selected)], SELECTED)]
    for name, group, color in groups:
        if not group:
            continue
        labels = ["HOMO" if i == homo else "LUMO" if i == result["lumo_idx"] else f"Orbitaali {i+1}"
                  for i in group]
        fig.add_trace(go.Scatter(
            x=[i + 1 for i in group], y=[result["evals"][i] for i in group],
            mode="markers", name=name,
            marker=dict(symbol="line-ew", size=38, color=color, line=dict(color=color, width=5)),
            customdata=[[i, label, 2 if i <= homo else 0] for i, label in zip(group, labels)],
            hovertemplate="%{customdata[1]}<br>Energia: %{y:.6f} Eh<br>Elektroneja: %{customdata[2]}<extra></extra>",
            selected=dict(marker=dict(color=SELECTED)),
        ))
    for i in indices:
        if i <= homo:
            fig.add_annotation(x=i+1, y=result["evals"][i], text="↑↓", showarrow=False,
                               yshift=14, font=dict(size=15, color=INK))
    for i, label in [(homo, "HOMO"), (result["lumo_idx"], "LUMO")]:
        if i is not None and i in indices:
            fig.add_annotation(x=i+1, y=result["evals"][i], text=label, showarrow=False,
                               yshift=-21, font=dict(size=12, color=MUTED))
    fig.update_layout(title="Molekyyliorbitaalien energiatasot", height=400,
                       xaxis_title="Orbitaalin numero", yaxis_title="Orbitaalienergia (Eh)",
                       clickmode="event+select", dragmode="select")
    fig.update_xaxes(tickmode="array", tickvals=[i+1 for i in indices], showgrid=False)
    return style_plot(fig)
