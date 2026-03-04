from __future__ import annotations

import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import plotly.graph_objects as go

TYPE_COLORS = {
    "normal": "#A8A878",
    "fire": "#F08030",
    "water": "#6890F0",
    "electric": "#F8D030",
    "grass": "#78C850",
    "ice": "#98D8D8",
    "fighting": "#C03028",
    "poison": "#A040A0",
    "ground": "#E0C068",
    "flying": "#A890F0",
    "psychic": "#F85888",
    "bug": "#A8B820",
    "rock": "#B8A038",
    "ghost": "#705898",
    "dragon": "#7038F8",
    "dark": "#705848",
    "steel": "#B8B8D0",
    "fairy": "#EE99AC",
}

STAT_NAMES = {
    "hp": "HP",
    "attack": "Attack",
    "defense": "Defense",
    "special-attack": "Sp. Atk",
    "special-defense": "Sp. Def",
    "speed": "Speed",
}

# Kanto schematic coordinates: (x, y, display label)
# x: 1=west → 10=east,  y: 1=south → 10=north
KANTO_MAP: dict[str, tuple[float, float, str]] = {
    "pallet-town-area":      (4.0, 2.0,  "Pallet Town"),
    "route-1-area":          (4.0, 2.8,  "Route 1"),
    "route-21-area":         (3.2, 1.8,  "Route 21"),
    "cinnabar-island-area":  (2.8, 1.0,  "Cinnabar Island"),
    "pokemon-mansion-1f":    (2.8, 1.0,  "Pokémon Mansion"),
    "pokemon-mansion-2f":    (2.8, 1.0,  "Pokémon Mansion"),
    "pokemon-mansion-3f":    (2.8, 1.0,  "Pokémon Mansion"),
    "pokemon-mansion-b1f":   (2.8, 1.0,  "Pokémon Mansion"),
    "route-20-area":         (3.8, 1.5,  "Route 20"),
    "seafoam-islands-1f":    (3.2, 1.2,  "Seafoam Islands"),
    "seafoam-islands-b1f":   (3.2, 1.2,  "Seafoam Islands"),
    "seafoam-islands-b2f":   (3.2, 1.2,  "Seafoam Islands"),
    "seafoam-islands-b3f":   (3.2, 1.2,  "Seafoam Islands"),
    "seafoam-islands-b4f":   (3.2, 1.2,  "Seafoam Islands"),
    "viridian-city-area":    (3.5, 3.8,  "Viridian City"),
    "route-22-area":         (2.5, 3.8,  "Route 22"),
    "route-23-area":         (2.5, 5.2,  "Route 23"),
    "victory-road-1f":       (2.0, 6.2,  "Victory Road"),
    "victory-road-2f":       (2.0, 6.2,  "Victory Road"),
    "victory-road-3f":       (2.0, 6.2,  "Victory Road"),
    "route-2-area":          (3.5, 5.0,  "Route 2"),
    "viridian-forest-area":  (3.5, 4.5,  "Viridian Forest"),
    "diglett-cave-area":     (5.0, 4.2,  "Diglett's Cave"),
    "pewter-city-area":      (3.5, 7.0,  "Pewter City"),
    "route-3-area":          (4.5, 7.0,  "Route 3"),
    "mt-moon-1f":            (5.5, 7.0,  "Mt. Moon"),
    "mt-moon-b1f":           (5.5, 7.0,  "Mt. Moon"),
    "mt-moon-b2f":           (5.5, 7.0,  "Mt. Moon"),
    "route-4-area":          (6.5, 7.0,  "Route 4"),
    "cerulean-city-area":    (7.0, 8.2,  "Cerulean City"),
    "cerulean-cave-1f":      (6.5, 9.2,  "Cerulean Cave"),
    "cerulean-cave-2f":      (6.5, 9.2,  "Cerulean Cave"),
    "cerulean-cave-b1f":     (6.5, 9.2,  "Cerulean Cave"),
    "route-24-area":         (7.5, 9.0,  "Route 24"),
    "route-25-area":         (8.5, 9.5,  "Route 25"),
    "route-5-area":          (7.0, 7.5,  "Route 5"),
    "route-6-area":          (7.0, 5.8,  "Route 6"),
    "saffron-city-area":     (7.0, 6.8,  "Saffron City"),
    "vermilion-city-area":   (7.0, 5.0,  "Vermilion City"),
    "ss-anne-area":          (7.3, 5.0,  "S.S. Anne"),
    "route-9-area":          (8.0, 8.2,  "Route 9"),
    "route-10-area":         (8.5, 7.8,  "Route 10"),
    "rock-tunnel-1f":        (8.5, 7.2,  "Rock Tunnel"),
    "rock-tunnel-b1f":       (8.5, 7.2,  "Rock Tunnel"),
    "power-plant-area":      (9.2, 8.5,  "Power Plant"),
    "lavender-town-area":    (9.5, 7.0,  "Lavender Town"),
    "pokemon-tower-1f":      (9.5, 7.0,  "Pokémon Tower"),
    "pokemon-tower-2f":      (9.5, 7.0,  "Pokémon Tower"),
    "pokemon-tower-3f":      (9.5, 7.0,  "Pokémon Tower"),
    "pokemon-tower-4f":      (9.5, 7.0,  "Pokémon Tower"),
    "pokemon-tower-5f":      (9.5, 7.0,  "Pokémon Tower"),
    "pokemon-tower-6f":      (9.5, 7.0,  "Pokémon Tower"),
    "pokemon-tower-7f":      (9.5, 7.0,  "Pokémon Tower"),
    "route-8-area":          (8.5, 7.0,  "Route 8"),
    "route-7-area":          (6.8, 7.5,  "Route 7"),
    "celadon-city-area":     (6.0, 7.8,  "Celadon City"),
    "route-16-area":         (5.0, 7.8,  "Route 16"),
    "route-17-area":         (5.0, 6.5,  "Route 17"),
    "route-18-area":         (5.0, 5.2,  "Route 18"),
    "route-11-area":         (8.2, 5.5,  "Route 11"),
    "route-12-area":         (9.2, 5.5,  "Route 12"),
    "route-13-area":         (8.8, 5.0,  "Route 13"),
    "route-14-area":         (8.5, 4.5,  "Route 14"),
    "route-15-area":         (7.8, 4.5,  "Route 15"),
    "fuchsia-city-area":     (6.0, 5.0,  "Fuchsia City"),
    "safari-zone-area":      (5.5, 5.5,  "Safari Zone"),
    "safari-zone-center":    (5.5, 5.5,  "Safari Zone"),
    "safari-zone-east":      (5.5, 5.5,  "Safari Zone"),
    "safari-zone-north":     (5.5, 5.5,  "Safari Zone"),
    "safari-zone-west":      (5.5, 5.5,  "Safari Zone"),
    "route-19-area":         (6.0, 4.0,  "Route 19"),
}

st.set_page_config(page_title="Pokédex", page_icon="🔴", layout="wide")


@st.cache_data
def fetch_pokemon(name: str) -> dict | None:
    resp = requests.get(f"https://pokeapi.co/api/v2/pokemon/{name.lower().strip()}")
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return resp.json()


@st.cache_data
def fetch_species(name: str) -> dict | None:
    resp = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{name.lower().strip()}")
    if not resp.ok:
        return None
    return resp.json()


def _describe_evo(details: list) -> str:
    if not details:
        return ""
    d = details[0]
    trigger = d.get("trigger", {}).get("name", "")
    parts = []
    if trigger == "level-up":
        if d.get("min_level"):
            parts.append(f"Lv. {d['min_level']}")
        elif d.get("min_happiness"):
            parts.append("High Friendship")
        elif d.get("min_affection"):
            parts.append("High Affection")
        elif d.get("min_beauty"):
            parts.append("High Beauty")
        else:
            parts.append("Level up")
    elif trigger == "use-item":
        item = (d.get("item") or {}).get("name", "item")
        parts.append(f"Use {item.replace('-', ' ').title()}")
    elif trigger == "trade":
        held = d.get("held_item")
        parts.append(f"Trade holding {held['name'].replace('-', ' ').title()}" if held else "Trade")
    elif trigger == "shed":
        parts.append("Lv. 20 + empty slot")
    else:
        parts.append(trigger.replace("-", " ").title())
    if d.get("time_of_day"):
        parts.append(d["time_of_day"].capitalize())
    if d.get("held_item") and trigger != "trade":
        parts.append(f"Holding {d['held_item']['name'].replace('-', ' ').title()}")
    if d.get("known_move"):
        parts.append(f"Know {d['known_move']['name'].replace('-', ' ').title()}")
    if d.get("location"):
        parts.append(f"At {d['location']['name'].replace('-', ' ').title()}")
    if d.get("needs_overworld_rain"):
        parts.append("While raining")
    if d.get("turn_upside_down"):
        parts.append("Turn upside down")
    if d.get("gender"):
        parts.append({1: "Female only", 2: "Male only"}.get(d["gender"], ""))
    return ", ".join(p for p in parts if p)


@st.cache_data
def fetch_evolution_chain(url: str) -> list[list[tuple[str, str]]]:
    resp = requests.get(url)
    if not resp.ok:
        return []
    stages: list[list[tuple[str, str]]] = []

    def traverse(node: dict, depth: int) -> None:
        while len(stages) <= depth:
            stages.append([])
        name = node["species"]["name"].capitalize()
        condition = _describe_evo(node.get("evolution_details", []))
        stages[depth].append((name, condition))
        for next_node in node.get("evolves_to", []):
            traverse(next_node, depth + 1)

    traverse(resp.json()["chain"], 0)
    return stages


@st.cache_data
def fetch_sprite_url(name: str) -> str | None:
    resp = requests.get(f"https://pokeapi.co/api/v2/pokemon/{name.lower()}")
    if not resp.ok:
        return None
    d = resp.json()
    return (
        d.get("sprites", {}).get("other", {}).get("official-artwork", {}).get("front_default")
        or d.get("sprites", {}).get("front_default")
    )


@st.cache_data
def fetch_locations(pokemon_id: int) -> list[str]:
    resp = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}/encounters")
    if not resp.ok:
        return []
    frlg = {"firered", "leafgreen"}
    return [
        enc["location_area"]["name"]
        for enc in resp.json()
        if any(vd["version"]["name"] in frlg for vd in enc["version_details"])
    ]


@st.cache_data
def fetch_image(url: str) -> Image.Image:
    resp = requests.get(url)
    resp.raise_for_status()
    return Image.open(BytesIO(resp.content))


def type_badge_html(type_name: str) -> str:
    color = TYPE_COLORS.get(type_name.lower(), "#68A090")
    return (
        f'<span style="background-color:{color};color:white;padding:4px 12px;'
        f'border-radius:12px;font-weight:bold;font-size:0.85rem;margin-right:6px;'
        f'text-transform:capitalize;">{type_name}</span>'
    )


def make_stat_radar(stats: dict) -> go.Figure:
    labels = list(stats.keys())
    values = list(stats.values())
    # Close the polygon
    labels_closed = labels + [labels[0]]
    values_closed = values + [values[0]]

    fig = go.Figure(
        go.Scatterpolar(
            r=values_closed,
            theta=labels_closed,
            fill="toself",
            fillcolor="rgba(99,110,250,0.3)",
            line=dict(color="rgba(99,110,250,0.9)", width=2),
        )
    )
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 255], showticklabels=False),
        ),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=40, t=40, b=40),
        height=350,
    )
    return fig


def make_location_map(found_areas: list[str]) -> go.Figure:
    found_labels = {KANTO_MAP[a][2] for a in found_areas if a in KANTO_MAP}

    # Deduplicate by label (multiple floors → same pin)
    label_coords: dict[str, tuple[float, float]] = {}
    for _, (x, y, label) in KANTO_MAP.items():
        if label not in label_coords:
            label_coords[label] = (x, y)

    x_found, y_found, t_found = [], [], []
    x_other, y_other, t_other = [], [], []
    for label, (x, y) in label_coords.items():
        if label in found_labels:
            x_found.append(x); y_found.append(y); t_found.append(label)
        else:
            x_other.append(x); y_other.append(y); t_other.append(label)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_other, y=y_other, mode="markers+text", text=t_other,
        textposition="top center",
        textfont=dict(size=8, color="#999999"),
        marker=dict(color="#CCCCCC", size=7),
        hovertemplate="%{text}<extra></extra>",
        showlegend=False,
    ))
    fig.add_trace(go.Scatter(
        x=x_found, y=y_found, mode="markers+text", text=t_found,
        textposition="top center",
        textfont=dict(size=9, color="#CC2200", family="Arial Black"),
        marker=dict(color="#FF4422", size=14, symbol="star"),
        hovertemplate="%{text}<extra></extra>",
        showlegend=False,
    ))
    fig.update_layout(
        xaxis=dict(visible=False, range=[1.2, 10.5]),
        yaxis=dict(visible=False, range=[0.5, 10.2]),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(173,216,230,0.35)",
        height=460,
        margin=dict(l=10, r=10, t=10, b=10),
    )
    return fig


# ── UI ────────────────────────────────────────────────────────────────────────

st.title("🔴 Pokédex")
query = st.text_input("Search by name or Pokédex number", placeholder="e.g. pikachu or 25")

if query:
    with st.spinner("Fetching data…"):
        data = fetch_pokemon(query)
        species = fetch_species(query) if data else None
        description = None
        evo_stages: list[list[str]] = []
        if species:
            for entry in species.get("flavor_text_entries", []):
                if entry["language"]["name"] == "en":
                    description = entry["flavor_text"].replace("\n", " ").replace("\f", " ")
                    break
            evo_url = (species.get("evolution_chain") or {}).get("url")
            if evo_url:
                evo_stages = fetch_evolution_chain(evo_url)
        locations = fetch_locations(data["id"]) if data else []

    if data is None:
        st.error("Pokémon not found. Try a different name or number.")
    else:
        # Sprite
        sprite_url = (
            data.get("sprites", {})
            .get("other", {})
            .get("official-artwork", {})
            .get("front_default")
            or data.get("sprites", {}).get("front_default")
        )

        # Basic info
        name = data["name"].capitalize()
        poke_id = data["id"]
        types = [t["type"]["name"] for t in data["types"]]
        height_m = data["height"] / 10
        weight_kg = data["weight"] / 10
        abilities = [a["ability"]["name"].replace("-", " ").title() for a in data["abilities"]]

        # Stats
        raw_stats = {s["stat"]["name"]: s["base_stat"] for s in data["stats"]}
        display_stats = {STAT_NAMES.get(k, k): v for k, v in raw_stats.items()}

        # Layout: sprite | info
        col1, col2 = st.columns([1, 2])

        with col1:
            if sprite_url:
                img = fetch_image(sprite_url)
                st.image(img, width=280)
            else:
                st.write("No image available.")

        with col2:
            st.markdown(f"## {name} &nbsp; <span style='color:gray;font-size:1.2rem'>#{poke_id:03d}</span>", unsafe_allow_html=True)
            badges = "".join(type_badge_html(t) for t in types)
            st.markdown(badges, unsafe_allow_html=True)
            st.markdown("")
            st.markdown(f"**Height:** {height_m} m &nbsp;&nbsp; **Weight:** {weight_kg} kg")
            st.markdown(f"**Abilities:** {', '.join(abilities)}")
            if description:
                st.markdown(f"_{description}_")

        st.divider()

        # Stats section
        st.subheader("Base Stats")
        bar_col, radar_col = st.columns([1, 1])

        with bar_col:
            for stat_label, value in display_stats.items():
                type_color = TYPE_COLORS.get(types[0].lower(), "#6890F0")
                st.markdown(
                    f"<span style='color:{type_color};font-weight:bold;display:inline-block;width:80px'>{stat_label}</span> "
                    f"<span style='font-weight:bold'>{value}</span>",
                    unsafe_allow_html=True,
                )
                st.progress(value / 255)

        with radar_col:
            fig = make_stat_radar(display_stats)
            st.plotly_chart(fig, use_container_width=True)

        if evo_stages:
            st.divider()
            st.subheader("Evolution")

            def evo_card(poke_name: str, condition: str) -> str:
                sprite = fetch_sprite_url(poke_name)
                bulba_url = f"https://bulbapedia.bulbagarden.net/wiki/{poke_name}_(Pokémon)"
                img_tag = f'<img src="{sprite}" width="80" style="border-radius:8px"/>' if sprite else ""
                cond_html = f'<br/><span style="font-size:0.75rem;color:gray">{condition}</span>' if condition else ""
                return (
                    f'<div style="text-align:center;margin:0 4px">'
                    f'<a href="{bulba_url}" target="_blank">{img_tag}</a><br/>'
                    f'<a href="{bulba_url}" target="_blank" style="text-decoration:none;font-weight:bold;color:inherit">{poke_name}</a>'
                    f'{cond_html}'
                    f'</div>'
                )

            stage_htmls = [
                f'<div style="display:flex;gap:8px;align-items:center">{"".join(evo_card(n, c) for n, c in stage)}</div>'
                for stage in evo_stages
            ]
            arrow = '<span style="font-size:1.8rem;padding:0 12px">→</span>'
            st.markdown(
                f'<div style="display:flex;align-items:center;flex-wrap:wrap;padding:16px 0">{arrow.join(stage_htmls)}</div>',
                unsafe_allow_html=True,
            )

        known_locs = [a for a in locations if a in KANTO_MAP]
        if known_locs:
            st.divider()
            st.subheader("Locations in FireRed / LeafGreen")
            st.plotly_chart(make_location_map(locations), use_container_width=True)
