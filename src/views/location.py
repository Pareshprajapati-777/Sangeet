"""Location intelligence view."""

import streamlit as st
import streamlit.components.v1 as components

from src.repositories.locations import LocationRepository
from src.services.location import LocationService
from src.utils.theme import render_hero_banner


def render_location_map():
    render_hero_banner(
        "chart",
        "Artist & Filming Locations",
        "Explore public studios, filming locations, and musical works linked to each place.",
    )

    location_repo = LocationRepository()
    location_service = LocationService()
    locations = location_repo.get_all_locations()
    if not locations:
        st.info("No public locations are available yet.")
        return

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    total_locs = len(locations)
    studios_count = sum(1 for loc in locations if any(w in (loc["location_type"] or "").lower() for w in ["studio", "sound", "mixing", "recording", "audio", "acoustic"]))
    film_count = sum(1 for loc in locations if any(w in (loc["location_type"] or "").lower() for w in ["film", "shooting", "lot", "complex"]))
    cities_count = len({loc["city"] for loc in locations if loc["city"]})

    with col_m1:
        st.metric("Total Landmarks & Studios", f"{total_locs:,}")
    with col_m2:
        st.metric("Acoustic Studios", f"{studios_count:,}")
    with col_m3:
        st.metric("Filming Hubs & Lots", f"{film_count:,}")
    with col_m4:
        st.metric("Active Cultural Cities", f"{cities_count:,}")

    col_filter, col_hint = st.columns([2, 3])
    with col_filter:
        location_types = ["All"] + sorted({location["location_type"] for location in locations})
        selected_type = st.selectbox(
            "Filter by category / facility type:",
            location_types,
            format_func=lambda value: value.replace("_", " ").title(),
            key="location_type_filter",
        )
    with col_hint:
        st.markdown("""
        <div style="background: rgba(99,102,241,0.08); border-radius: 12px; padding: 12px 16px; border: 1px solid rgba(99,102,241,0.2); margin-top: 24px; font-size: 0.85rem; color: #3730a3;">
            ✨ <strong>Interactive Map:</strong> Hover cursor over any map pin to instantly view studio metadata & acoustic description. Click any pin to open linked songs!
        </div>
        """, unsafe_allow_html=True)

    map_object = location_service.build_map(selected_type)

    try:
        from streamlit_folium import st_folium

        st_folium(map_object, height=650, use_container_width=True, returned_objects=[])
    except ImportError:
        components.html(map_object._repr_html_(), height=650, scrolling=False)
