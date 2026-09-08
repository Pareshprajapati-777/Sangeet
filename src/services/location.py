"""
Location and Geospatial Intelligence Service for Sangeet.
Constructs interactive Folium maps with categorized markers, tooltips,
and rich popups connecting musical works to real-world points of interest.
"""

from typing import List, Dict, Any, Optional
import html
import folium
from folium.plugins import MarkerCluster
from src.repositories.locations import LocationRepository

class LocationService:
    def __init__(self):
        self.location_repo = LocationRepository()

    def build_map(self, location_type_filter: Optional[str] = None) -> folium.Map:
        """Constructs and returns a Folium Map object with music points of interest."""
        records = self.location_repo.get_locations_with_songs()

        # Center map initially near central India / global overview (Bright, clean Light mode)
        m = folium.Map(
            location=[20.5937, 78.9629],
            zoom_start=5,
            tiles="CartoDB positron",
            control_scale=True
        )

        cluster = MarkerCluster(name="Studios & Landmarks").add_to(m)

        def get_marker_style(loc_type: str):
            lt = (loc_type or "").lower()
            if any(w in lt for w in ["music", "recording", "mixing", "sound", "acoustic", "audio", "scoring"]):
                return "blue", "headphones", "fa"
            elif any(w in lt for w in ["film", "shooting", "lot", "complex", "cine"]):
                return "red", "film", "fa"
            elif "birthplace" in lt:
                return "darkgreen", "star", "glyphicon"
            elif any(w in lt for w in ["concert", "venue", "dargah", "stage"]):
                return "purple", "music", "glyphicon"
            return "cadetblue", "info-sign", "glyphicon"

        # Deduplicate locations while grouping songs
        loc_groups: Dict[str, Dict[str, Any]] = {}
        for r in records:
            lid = r["location_id"]
            if location_type_filter and location_type_filter != "All" and r["location_type"] != location_type_filter:
                continue

            if lid not in loc_groups:
                loc_groups[lid] = {
                    "id": lid,
                    "name": r["location_name"],
                    "location_type": r["location_type"],
                    "lat": r["latitude"],
                    "lon": r["longitude"],
                    "city": r["city"],
                    "country": r["country"],
                    "desc": r["description"],
                    "songs": []
                }
            if r.get("song_title"):
                loc_groups[lid]["songs"].append({
                    "title": r["song_title"],
                    "artist": r.get("artist_name"),
                    "context": r.get("context_type"),
                    "notes": r.get("scene_notes")
                })

        for loc in loc_groups.values():
            color, icon_name, prefix = get_marker_style(loc["location_type"])

            # Build rich HTML Hover Tooltip (appears immediately on hover)
            desc_preview = html.escape(str(loc['desc'] or ''))
            if len(desc_preview) > 180:
                desc_preview = desc_preview[:180] + "..."

            tooltip_html = f"""
            <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; min-width: 220px; max-width: 300px; padding: 6px; background: #ffffff; border-radius: 8px; box-shadow: 0 4px 14px rgba(0,0,0,0.15); color: #0f172a;">
                <div style="font-weight: 800; font-size: 14px; color: #1e293b; margin-bottom: 3px; display: flex; align-items: center; gap: 6px;">
                    <span>📍</span> <span>{html.escape(str(loc['name']))}</span>
                </div>
                <div style="font-size: 11px; margin-bottom: 4px; display: flex; flex-wrap: wrap; gap: 4px;">
                    <span style="background: #e0e7ff; color: #3730a3; padding: 2px 7px; border-radius: 4px; font-weight: 700;">
                        {html.escape(str(loc['location_type']).replace('_', ' '))}
                    </span>
                    <span style="background: #f1f5f9; color: #475569; padding: 2px 6px; border-radius: 4px;">
                        🏙️ {html.escape(str(loc['city'] or ''))}
                    </span>
                </div>
                <div style="font-size: 11.5px; line-height: 1.4; color: #334155; margin-top: 4px; border-top: 1px solid #f1f5f9; padding-top: 4px;">
                    {desc_preview}
                </div>
                {'<div style="margin-top: 5px; font-size: 11px; font-weight: 700; color: #4f46e5;">🎵 ' + str(len(loc["songs"])) + ' linked musical works (click pin for details)</div>' if loc["songs"] else '<div style="margin-top: 4px; font-size: 10px; color: #94a3b8; font-style: italic;">Click pin to view full details</div>'}
            </div>
            """

            # Build rich HTML Click Popup
            song_items = ""
            for s in loc["songs"][:6]:
                song_items += f"""
                <li style="margin-bottom: 6px;">
                    <strong style="color: #4f46e5;">🎵 {html.escape(str(s['title']))}</strong><br/>
                    <small style="color: #64748b;">Artist: {html.escape(str(s['artist'] or 'Various'))}</small><br/>
                    <small style="color: #334155;"><em>{html.escape(str(s['notes'] or ''))}</em></small>
                </li>
                """

            popup_html = f"""
            <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; min-width: 250px; max-width: 340px; color: #1e293b; padding: 4px;">
                <h4 style="margin: 0 0 4px 0; color: #0f172a; font-size: 16px; border-bottom: 2px solid #4f46e5; padding-bottom: 4px;">
                    📍 {html.escape(str(loc['name']))}
                </h4>
                <div style="margin-bottom: 8px; font-size: 12px; color: #64748b;">
                    <span style="background: #e0e7ff; color: #3730a3; padding: 2px 6px; border-radius: 4px; text-transform: uppercase; font-size: 10px; font-weight: 700;">
                        {html.escape(str(loc['location_type']).replace('_', ' '))}
                    </span>
                    &nbsp;•&nbsp; {html.escape(str(loc['city'] or ''))}, {html.escape(str(loc['country'] or ''))}
                </div>
                <p style="font-size: 12px; line-height: 1.45; margin: 0 0 8px 0; color: #334155;">
                    {html.escape(str(loc['desc'] or ''))}
                </p>
                {f'<h5 style="margin: 6px 0 4px 0; font-size: 12px; color: #0f172a;">Linked Musical Works:</h5><ul style="padding-left: 16px; margin: 0; font-size: 12px;">{song_items}</ul>' if song_items else ''}
            </div>
            """

            folium.Marker(
                location=[loc["lat"], loc["lon"]],
                tooltip=folium.Tooltip(tooltip_html, sticky=True),
                popup=folium.Popup(popup_html, max_width=360),
                icon=folium.Icon(color=color, icon=icon_name, prefix=prefix)
            ).add_to(cluster)

        return m
