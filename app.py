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
