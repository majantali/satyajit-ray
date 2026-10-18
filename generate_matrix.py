#!/usr/bin/env python3
"""
Satyajit Ray Actors & Films Matrix Generator
Reads satyajit_ray_actors.csv, checks photos/ and posters/ directories,
and generates a rich, interactive HTML matrix visualization.
"""

import csv
import json
import os
import sys

# Define all Satyajit Ray feature films and anthologies in verified chronological order
# with release years, proper filenames, and Wikipedia links.
FILMS_CHRONOLOGY = [
    {"film": "Pather Panchali", "year": 1955, "wiki": "https://en.wikipedia.org/wiki/Pather_Panchali"},
    {"film": "Aparajito", "year": 1956, "wiki": "https://en.wikipedia.org/wiki/Aparajito"},
    {"film": "Parash Pathar", "year": 1958, "wiki": "https://en.wikipedia.org/wiki/Parash_Pathar"},
    {"film": "Jalsaghar", "year": 1958, "wiki": "https://en.wikipedia.org/wiki/Jalsaghar"},
    {"film": "Apur Sansar", "year": 1959, "wiki": "https://en.wikipedia.org/wiki/Apur_Sansar"},
    {"film": "Devi", "year": 1960, "wiki": "https://en.wikipedia.org/wiki/Devi_(1960_film)"},
    {"film": "Postmaster", "year": 1961, "wiki": "https://en.wikipedia.org/wiki/Teen_Kanya"},
    {"film": "Monihara", "year": 1961, "wiki": "https://en.wikipedia.org/wiki/Teen_Kanya"},
    {"film": "Samapti", "year": 1961, "wiki": "https://en.wikipedia.org/wiki/Teen_Kanya"},
    {"film": "Kanchenjungha", "year": 1962, "wiki": "https://en.wikipedia.org/wiki/Kanchenjungha"},
    {"film": "Abhijan", "year": 1962, "wiki": "https://en.wikipedia.org/wiki/Abhijan"},
    {"film": "Mahanagar", "year": 1963, "wiki": "https://en.wikipedia.org/wiki/Mahanagar"},
    {"film": "Charulata", "year": 1964, "wiki": "https://en.wikipedia.org/wiki/Charulata"},
    {"film": "Kapurush", "year": 1965, "wiki": "https://en.wikipedia.org/wiki/Kapurush"},
    {"film": "Mahapurush", "year": 1965, "wiki": "https://en.wikipedia.org/wiki/Mahapurush"},
    {"film": "Nayak", "year": 1966, "wiki": "https://en.wikipedia.org/wiki/Nayak_(1966_film)"},
    {"film": "Chiriyakhana", "year": 1967, "wiki": "https://en.wikipedia.org/wiki/Chiriyakhana"},
    {"film": "Goopy Gyne Bagha Byne", "year": 1968, "wiki": "https://en.wikipedia.org/wiki/Goopy_Gyne_Bagha_Byne"},
    {"film": "Aranyer Din Ratri", "year": 1969, "wiki": "https://en.wikipedia.org/wiki/Aranyer_Din_Ratri"},
    {"film": "Pratidwandi", "year": 1970, "wiki": "https://en.wikipedia.org/wiki/Pratidwandi"},
    {"film": "Seemabaddha", "year": 1971, "wiki": "https://en.wikipedia.org/wiki/Seemabaddha"},
    {"film": "Asani Sanket", "year": 1973, "wiki": "https://en.wikipedia.org/wiki/Asani_Sanket"},
    {"film": "Sonar Kella", "year": 1974, "wiki": "https://en.wikipedia.org/wiki/Sonar_Kella"},
    {"film": "Jana Aranya", "year": 1975, "wiki": "https://en.wikipedia.org/wiki/Jana_Aranya"},
    {"film": "Shatranj Ke Khilari", "year": 1977, "wiki": "https://en.wikipedia.org/wiki/The_Chess_Players_(film)"},
    {"film": "Joi Baba Felunath", "year": 1978, "wiki": "https://en.wikipedia.org/wiki/Joi_Baba_Felunath_(film)"},
    {"film": "Hirak Rajar Deshe", "year": 1980, "wiki": "https://en.wikipedia.org/wiki/Hirak_Rajar_Deshe"},
    {"film": "Pikoo", "year": 1980, "wiki": "https://en.wikipedia.org/wiki/Pikoo"},
    {"film": "Sadgati", "year": 1981, "wiki": "https://en.wikipedia.org/wiki/Sadgati"},
    {"film": "Ghare-Baire", "year": 1984, "wiki": "https://en.wikipedia.org/wiki/Ghare_Baire_(film)"},
    {"film": "Ganashatru", "year": 1989, "wiki": "https://en.wikipedia.org/wiki/Ganashatru"},
    {"film": "Shakha Proshakha", "year": 1990, "wiki": "https://en.wikipedia.org/wiki/Shakha_Proshakha"},
    {"film": "Agantuk", "year": 1991, "wiki": "https://en.wikipedia.org/wiki/Agantuk"}
]


def sanitize_filename(name):
    return name.replace(" ", "_")


def load_data(csv_path="satyajit_ray_actors.csv", photos_dir="photos", posters_dir="posters"):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [r for r in reader if r.get("actor", "").strip()]

    # Count appearances per actor across all films
    actor_appearances = {}
    for r in rows:
        act = r["actor"].strip()
        actor_appearances[act] = actor_appearances.get(act, 0) + 1

    # Keep only actors who have acted in at least 2 films
    multi_actor_names = {act for act, cnt in actor_appearances.items() if cnt > 1}
    multi_rows = [r for r in rows if r["actor"].strip() in multi_actor_names]

    # Organize actor profiles and their roles
    actors = {}
    for r in multi_rows:
        act = r["actor"].strip()
        yr = int(r["year"].strip())
        flm = r["film"].strip()
        char = r.get("character", "").strip()
        com = r.get("comment", "").strip()

        if act not in actors:
            actors[act] = {
                "name": act,
                "appearances": {},  # keyed by film name
                "film_count": 0,
                "min_year": yr,
                "max_year": yr
            }

        actors[act]["min_year"] = min(actors[act]["min_year"], yr)
        actors[act]["max_year"] = max(actors[act]["max_year"], yr)

        photo_filename = f"{sanitize_filename(act)}__{yr}__{sanitize_filename(flm)}.jpg"
        photo_path = os.path.join(photos_dir, photo_filename)
        has_photo = os.path.exists(photo_path) and os.path.getsize(photo_path) > 0

        if flm not in actors[act]["appearances"]:
            actors[act]["appearances"][flm] = {
                "film": flm,
                "year": yr,
                "characters": [char] if char else [],
                "comments": [com] if com else [],
                "photo_filename": photo_filename,
                "photo_path": photo_path,
                "has_photo": has_photo,
                "file_exists": os.path.exists(photo_path),
                "file_size": os.path.getsize(photo_path) if os.path.exists(photo_path) else 0
            }
        else:
            # Handle multiple characters in the same film (e.g. Prasad Mukherjee in Goopy Gyne Bagha Byne)
            if char and char not in actors[act]["appearances"][flm]["characters"]:
                actors[act]["appearances"][flm]["characters"].append(char)
            if com and com not in actors[act]["appearances"][flm]["comments"]:
                actors[act]["appearances"][flm]["comments"].append(com)

    # Calculate actual unique film count per actor
    for act, data in actors.items():
        data["film_count"] = len(data["appearances"])

    # Prepare films metadata with poster status and actor counts
    films = []
    for f_info in FILMS_CHRONOLOGY:
        flm = f_info["film"]
        yr = f_info["year"]
        wiki = f_info["wiki"]
        poster_filename = f"{yr}__{sanitize_filename(flm)}.jpg"
        poster_path = os.path.join(posters_dir, poster_filename)
        has_poster = os.path.exists(poster_path) and os.path.getsize(poster_path) > 0

        # Count how many of our 82 recurring actors are in this film
        cast_actors = [act for act, data in actors.items() if flm in data["appearances"]]

        films.append({
            "film": flm,
            "year": yr,
            "wiki": wiki,
            "poster_filename": poster_filename,
            "poster_path": poster_path,
            "has_poster": has_poster,
            "cast_count": len(cast_actors),
            "cast_actors": cast_actors
        })

    return actors, films


def generate_html(actors, films, output_path="index.html"):
    # Sort actors initially by number of films (descending), then alphabetically
    sorted_actors = sorted(actors.values(), key=lambda a: (-a["film_count"], a["name"]))

    # Summary statistics
    total_actors = len(actors)
    total_films = len(films)
    total_roles = sum(a["film_count"] for a in actors.values())
    total_photos_available = sum(
        1 for a in actors.values() for app in a["appearances"].values() if app["has_photo"]
    )
    total_photos_pending = total_roles - total_photos_available
    total_posters_available = sum(1 for f in films if f["has_poster"])
    photo_pct = round((total_photos_available / total_roles * 100), 1) if total_roles > 0 else 0

    html = []
    html.append("<!DOCTYPE html>")
    html.append('<html lang="en">')
    html.append("<head>")
    html.append('  <meta charset="UTF-8">')
    html.append('  <meta name="viewport" content="width=device-width, initial-scale=1.0">')
    html.append('  <title>Satyajit Ray Actors &amp; Films Matrix</title>')
    html.append('  <link rel="stylesheet" href="styles.css">')
    html.append('  <link rel="preconnect" href="https://fonts.googleapis.com">')
    html.append('  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>')
    html.append('  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800&family=Playfair+Display:ital,wght@0,600;0,700;1,400&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">')
    html.append("</head>")
    html.append('<body class="density-normal theme-cinematic">')

    # Header section
    html.append('  <header class="site-header">')
    html.append('    <div class="header-container">')
    html.append('      <div class="brand">')
    html.append('        <div class="brand-badge">Satyajit Ray Filmography</div>')
    html.append('        <h1 class="brand-title">The Ensemble of Satyajit Ray</h1>')
    html.append('        <p class="brand-subtitle">An interactive matrix documenting actors who appeared in two or more of Ray’s masterpieces (1955–1991)</p>')
    html.append("      </div>")

    # Metrics overview
    html.append('      <div class="metrics-grid">')
    html.append('        <div class="metric-card">')
    html.append(f'          <div class="metric-val">{total_actors}</div>')
    html.append('          <div class="metric-lbl">Recurring Actors</div>')
    html.append("        </div>")
    html.append('        <div class="metric-card">')
    html.append(f'          <div class="metric-val">{total_films}</div>')
    html.append('          <div class="metric-lbl">Chronological Films</div>')
    html.append("        </div>")
    html.append('        <div class="metric-card">')
    html.append(f'          <div class="metric-val">{total_roles}</div>')
    html.append('          <div class="metric-lbl">Matrix Appearances</div>')
    html.append("        </div>")
    html.append('        <div class="metric-card highlight">')
    html.append(f'          <div class="metric-val" id="metric-photo-count">{total_photos_available}<span class="metric-total">/{total_roles}</span></div>')
    html.append(f'          <div class="metric-lbl">Photos Populated ({photo_pct}%)</div>')
    html.append('          <div class="metric-progress"><div class="metric-progress-bar" style="width: ' + str(photo_pct) + '%;"></div></div>')
    html.append("        </div>")
    html.append("      </div>")
    html.append("    </div>")
    html.append("  </header>")

    # Sticky Toolbar
    html.append('  <nav class="matrix-toolbar" id="toolbar" aria-label="Matrix Navigation and Filters">')
    html.append('    <div class="toolbar-container">')

    # Search box
    html.append('      <div class="toolbar-group search-group">')
    html.append('        <label for="actor-search" class="sr-only">Search actor or character</label>')
    html.append('        <div class="search-input-wrapper">')
    html.append('          <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>')
    html.append('          <input type="text" id="actor-search" placeholder="Search actor or character (e.g., Soumitra, Feluda)..." autocomplete="off">')
    html.append('          <button id="search-clear" class="btn-clear" aria-label="Clear search" title="Clear">&times;</button>')
    html.append("        </div>")
    html.append("      </div>")

    # Sorting
    html.append('      <div class="toolbar-group">')
    html.append('        <span class="toolbar-label">Sort:</span>')
    html.append('        <div class="select-wrapper">')
    html.append('          <select id="sort-select" aria-label="Sort Actors">')
    html.append('            <option value="films-desc" selected>Most Ray Films (High to Low)</option>')
    html.append('            <option value="name-asc">Actor Name (A &rarr; Z)</option>')
    html.append('            <option value="name-desc">Actor Name (Z &rarr; A)</option>')
    html.append('            <option value="debut-asc">Debut Film Year (Oldest First)</option>')
    html.append('            <option value="debut-desc">Debut Film Year (Newest First)</option>')
    html.append("          </select>")
    html.append("        </div>")
    html.append("      </div>")

    # Decade filters
    html.append('      <div class="toolbar-group decade-filters">')
    html.append('        <span class="toolbar-label">Decade:</span>')
    html.append('        <div class="btn-group" role="group" aria-label="Filter by Decade">')
    html.append('          <button type="button" class="btn-pill active" data-decade="all">All</button>')
    html.append('          <button type="button" class="btn-pill" data-decade="1950s">’50s</button>')
    html.append('          <button type="button" class="btn-pill" data-decade="1960s">’60s</button>')
    html.append('          <button type="button" class="btn-pill" data-decade="1970s">’70s</button>')
    html.append('          <button type="button" class="btn-pill" data-decade="1980s-90s">’80s–’90s</button>')
    html.append("        </div>")
    html.append("      </div>")

    # Photo status filter
    html.append('      <div class="toolbar-group">')
    html.append('        <span class="toolbar-label">Photos:</span>')
    html.append('        <div class="btn-group" role="group" aria-label="Filter by Photo Status">')
    html.append('          <button type="button" class="btn-pill active" data-photo-filter="all">All</button>')
    html.append(f'          <button type="button" class="btn-pill" data-photo-filter="filled" title="Only show cells with captured photos">Available ({total_photos_available})</button>')
    html.append(f'          <button type="button" class="btn-pill" data-photo-filter="pending" title="Highlight pending photo cells">Pending ({total_photos_pending})</button>')
    html.append("        </div>")
    html.append("      </div>")

    # Density / Zoom controls
    html.append('      <div class="toolbar-group density-group">')
    html.append('        <span class="toolbar-label">Size:</span>')
    html.append('        <div class="btn-group" role="group" aria-label="Table Density">')
    html.append('          <button type="button" class="btn-pill" data-density="compact" title="Compact size">S</button>')
    html.append('          <button type="button" class="btn-pill active" data-density="normal" title="Normal size">M</button>')
    html.append('          <button type="button" class="btn-pill" data-density="large" title="Large size">L</button>')
    html.append("        </div>")
    html.append("      </div>")

    # Toggle options
    html.append('      <div class="toolbar-group toggles-group">')
    html.append('        <label class="toggle-control" title="Toggle highlighting of row and column on cell hover">')
    html.append('          <input type="checkbox" id="crosshair-toggle" checked>')
    html.append('          <span class="toggle-slider"></span>')
    html.append('          <span class="toggle-text">Crosshair</span>')
    html.append("        </label>")
    html.append('        <label class="toggle-control" title="Highlight missing/empty photo placeholders with warning border">')
    html.append('          <input type="checkbox" id="highlight-pending-toggle">')
    html.append('          <span class="toggle-slider"></span>')
    html.append('          <span class="toggle-text">Highlight Pending</span>')
    html.append("        </label>")
    html.append("      </div>")

    html.append("    </div>")
    html.append("  </nav>")

    # Main Matrix Table Container
    html.append('  <main class="matrix-wrapper">')
    html.append('    <div class="matrix-scroll-pane" id="matrix-scroll-pane">')
    html.append('      <table class="matrix-table" id="matrix-table" aria-label="Satyajit Ray Actors and Films Matrix">')

    # Table Header (Films and Posters)
    html.append("        <thead>")
    html.append("          <tr>")

    # Top-Left Corner Header Cell (Sticky on both X and Y)
    html.append('            <th scope="col" class="corner-header sticky-col sticky-row" id="corner-header">')
    html.append('              <div class="corner-content">')
    html.append('                <div class="corner-title">Satyajit Ray</div>')
    html.append('                <div class="corner-subtitle">Actor Matrix</div>')
    html.append(f'                <div class="corner-caption"><span id="visible-actors-count">{total_actors}</span> of {total_actors} Actors</div>')
    html.append("              </div>")
    html.append("            </th>")

    # Film Column Headers
    for f in films:
        flm = f["film"]
        yr = f["year"]
        wiki = f["wiki"]
        p_filename = f["poster_filename"]
        has_poster = f["has_poster"]
        cast_count = f["cast_count"]

        decade = f"{yr // 10 * 10}s"
        if decade in ("1980s", "1990s"):
            decade_attr = "1980s-90s"
        else:
            decade_attr = decade

        html.append(f'            <th scope="col" class="film-header sticky-row" data-film="{flm}" data-year="{yr}" data-decade="{decade_attr}" data-cast-count="{cast_count}">')
        html.append('              <div class="film-header-inner">')

        # Poster card linking to Wikipedia
        html.append(f'                <a href="{wiki}" target="_blank" rel="noopener noreferrer" class="poster-link" title="Open Wikipedia page for {flm} ({yr}) in a new tab">')
        html.append(f'                  <div class="poster-frame" data-has-poster="{str(has_poster).lower()}">')

        # Poster image with automated fallback detection
        html.append(f'                    <img src="posters/{p_filename}" alt="Film poster for {flm} ({yr})" class="poster-img" loading="lazy" '
                    f'onload="this.classList.add(\'is-loaded\'); this.parentElement.querySelector(\'.poster-fallback\').classList.add(\'is-hidden\');" '
                    f'onerror="this.classList.add(\'is-hidden\'); this.parentElement.querySelector(\'.poster-fallback\').classList.remove(\'is-hidden\');">')

        # Fallback artistic poster card
        html.append('                    <div class="poster-fallback' + (' is-hidden' if has_poster else '') + '">')
        html.append('                      <div class="poster-fb-tag">RAY FILM</div>')
        html.append(f'                      <div class="poster-fb-title">{flm}</div>')
        html.append(f'                      <div class="poster-fb-year">{yr}</div>')
        html.append('                      <div class="poster-fb-icon"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="2" y="2" width="20" height="20" rx="2.18" ry="2.18"></rect><line x1="7" y1="2" x2="7" y2="22"></line><line x1="17" y1="2" x2="17" y2="22"></line><line x1="2" y1="12" x2="22" y2="12"></line><line x1="2" y1="7" x2="7" y2="7"></line><line x1="2" y1="17" x2="7" y2="17"></line><line x1="17" y1="17" x2="22" y2="17"></line><line x1="17" y1="7" x2="22" y2="7"></line></svg></div>')
        html.append('                      <span class="poster-fb-hint">Wikipedia ↗</span>')
        html.append("                    </div>")

        # Wikipedia hover pill
        html.append('                    <div class="poster-wiki-badge" title="View Wikipedia Article">Wiki ↗</div>')
        html.append("                  </div>")
        html.append("                </a>")

        # Film metadata below poster
        html.append('                <div class="film-info">')
        html.append(f'                  <div class="film-year">{yr}</div>')
        html.append(f'                  <div class="film-title" title="{flm} ({yr})">{flm}</div>')
        html.append(f'                  <div class="film-cast-meta" title="{cast_count} recurring actors in this film">{cast_count} actors</div>')
        html.append("                </div>")

        html.append("              </div>")
        html.append("            </th>")

    html.append("          </tr>")
    html.append("        </thead>")

    # Table Body (Rows = Actors)
    html.append("        <tbody id=\"matrix-tbody\">")

    for act_data in sorted_actors:
        act = act_data["name"]
        f_count = act_data["film_count"]
        min_yr = act_data["min_year"]
        max_yr = act_data["max_year"]
        initials = "".join([part[0] for part in act.split() if part])[:2].upper()

        years_active = f"{min_yr}" if min_yr == max_yr else f"{min_yr}–{max_yr}"

        # Actor's list of character names for quick client-side search indexing
        all_chars = []
        for app in act_data["appearances"].values():
            all_chars.extend(app["characters"])
        chars_search_str = " ".join(all_chars).lower()

        html.append(f'          <tr class="actor-row" data-actor="{act}" data-film-count="{f_count}" data-debut-year="{min_yr}" data-characters="{chars_search_str}">')

        # Row Header (Sticky on X)
        html.append(f'            <th scope="row" class="actor-header sticky-col" data-actor="{act}">')
        html.append('              <div class="actor-header-inner">')
        html.append(f'                <div class="actor-name" title="{act}">{act}</div>')
        html.append('                <div class="actor-subinfo">')
        html.append(f'                  <span class="film-count-badge" title="Acted in {f_count} Satyajit Ray films">{f_count} films</span>')
        html.append(f'                  <span class="actor-years-badge" title="Active period in Ray films">{years_active}</span>')
        html.append("                </div>")
        html.append("              </div>")
        html.append("            </th>")

        # Matrix Cells (Columns = Films)
        for f in films:
            flm = f["film"]
            yr = f["year"]
            decade = f"{yr // 10 * 10}s"
            if decade in ("1980s", "1990s"):
                decade_attr = "1980s-90s"
            else:
                decade_attr = decade

            if flm in act_data["appearances"]:
                app = act_data["appearances"][flm]
                has_photo = app["has_photo"]
                p_file = app["photo_filename"]
                chars = app["characters"]
                char_display = " / ".join(chars) if chars else "Role Uncredited"
                comments = app["comments"]
                comment_display = " | ".join(comments) if comments else ""

                status_class = "has-photo" if has_photo else "is-placeholder"
                cell_photo_state = "filled" if has_photo else "pending"

                html.append(f'            <td class="matrix-cell role-cell {status_class}" data-actor="{act}" data-film="{flm}" data-year="{yr}" data-decade="{decade_attr}" data-photo-state="{cell_photo_state}">')
                poster_file = f["poster_filename"]
                wiki_url = f["wiki"]
                html.append(f'              <div class="photo-cell-content" tabindex="0" role="button" aria-haspopup="dialog" '
                            f'data-actor="{act}" data-film="{flm}" data-year="{yr}" data-character="{char_display}" '
                            f'data-comments="{comment_display}" data-photo="photos/{p_file}" data-has-photo="{str(has_photo).lower()}" '
                            f'data-poster="posters/{poster_file}" data-wiki="{wiki_url}" '
                            f'title="{act} as {char_display} in {flm} ({yr})">')

                # Photo Frame
                html.append('                <div class="photo-frame">')
                # Real Image tag
                html.append(f'                  <img src="photos/{p_file}" alt="{act} in {flm} ({yr})" class="actor-photo" loading="lazy" '
                            f'onload="this.classList.add(\'is-loaded\'); this.parentElement.querySelector(\'.photo-placeholder\').classList.add(\'is-hidden\');" '
                            f'onerror="this.classList.add(\'is-hidden\'); this.parentElement.querySelector(\'.photo-placeholder\').classList.remove(\'is-hidden\');">')

                # Placeholder element
                html.append('                  <div class="photo-placeholder' + (' is-hidden' if has_photo else '') + '">')
                html.append(f'                    <span class="placeholder-avatar">{initials}</span>')
                html.append('                    <span class="placeholder-tag">Pending</span>')
                html.append("                  </div>")

                # Character pill at the bottom of the photo
                html.append(f'                  <div class="char-pill" title="{char_display}">{char_display}</div>')
                html.append("                </div>")

                # Rich Hover Tooltip (popover)
                html.append('                <div class="hover-tooltip" role="tooltip">')
                html.append('                  <div class="tooltip-header">')
                html.append(f'                    <div class="tooltip-actor">{act}</div>')
                html.append(f'                    <span class="tooltip-badge">{f_count} Ray Films</span>')
                html.append("                  </div>")
                html.append('                  <div class="tooltip-row">')
                html.append('                    <span class="tooltip-lbl">Role:</span>')
                html.append(f'                    <span class="tooltip-val role-name">{char_display}</span>')
                html.append("                  </div>")
                html.append('                  <div class="tooltip-row">')
                html.append('                    <span class="tooltip-lbl">Film:</span>')
                html.append(f'                    <span class="tooltip-val film-name">{flm} ({yr})</span>')
                html.append("                  </div>")
                if comment_display:
                    html.append('                  <div class="tooltip-row">')
                    html.append('                    <span class="tooltip-lbl">Note:</span>')
                    html.append(f'                    <span class="tooltip-val note-text">{comment_display}</span>')
                    html.append("                  </div>")
                html.append('                  <div class="tooltip-footer">')
                if has_photo:
                    html.append('                    <span class="status-indicator status-ok">&#10003; Photo Captured</span>')
                else:
                    html.append('                    <span class="status-indicator status-missing">&#9679; Photo Pending</span>')
                html.append('                    <span class="tooltip-action">Click to inspect</span>')
                html.append("                  </div>")
                html.append("                </div>")

                html.append("              </div>")
                html.append("            </td>")
            else:
                # Empty Cell (Actor was not in this film)
                html.append(f'            <td class="matrix-cell empty-cell" data-actor="{act}" data-film="{flm}" data-year="{yr}" data-decade="{decade_attr}" aria-hidden="true">')
                html.append('              <div class="empty-dot" title="No appearance in this film"></div>')
                html.append("            </td>")

        html.append("          </tr>")

    html.append("        </tbody>")
    html.append("      </table>")
    html.append("    </div>")
    html.append("  </main>")

    # Modal Lightbox for Full View
    html.append('  <div class="lightbox-modal" id="lightbox-modal" aria-hidden="true" role="dialog" aria-modal="true">')
    html.append('    <div class="lightbox-overlay" id="lightbox-backdrop"></div>')
    html.append('    <div class="lightbox-dialog">')
    html.append('      <button class="lightbox-close" id="lightbox-close" aria-label="Close modal">&times;</button>')
    html.append('      <div class="lightbox-body">')
    html.append('        <div class="lightbox-media">')
    html.append('          <img src="" alt="" id="lightbox-img" class="lightbox-img">')
    html.append('          <div id="lightbox-placeholder" class="lightbox-media-placeholder is-hidden">')
    html.append('            <div class="lb-ph-icon">🎬</div>')
    html.append('            <div class="lb-ph-text">Photo not yet captured</div>')
    html.append('            <div class="lb-ph-hint">Awaiting high-resolution screenshot from film archive</div>')
    html.append("          </div>")
    html.append("        </div>")
    html.append('        <div class="lightbox-details">')
    html.append('          <div class="lightbox-film-tag" id="lb-film-year">1964</div>')
    html.append('          <h2 class="lightbox-actor-name" id="lb-actor-name">Madhabi Mukherjee</h2>')
    html.append('          <div class="lightbox-role-box">')
    html.append('            <div class="lb-meta-label">Character / Role</div>')
    html.append('            <div class="lb-role-val" id="lb-character-name">Charulata</div>')
    html.append("          </div>")
    html.append('          <div class="lightbox-info-list">')
    html.append('            <div class="lb-info-item">')
    html.append('              <span class="lb-label">Film:</span>')
    html.append('              <span class="lb-val" id="lb-film-title">Charulata</span>')
    html.append("            </div>")
    html.append('            <div class="lb-info-item">')
    html.append('              <span class="lb-label">Director:</span>')
    html.append('              <span class="lb-val">Satyajit Ray</span>')
    html.append("            </div>")
    html.append('            <div class="lb-info-item" id="lb-comments-row">')
    html.append('              <span class="lb-label">Archive Notes:</span>')
    html.append('              <span class="lb-val" id="lb-comments">None</span>')
    html.append("            </div>")
    html.append('            <div class="lb-info-item">')
    html.append('              <span class="lb-label">Status:</span>')
    html.append('              <span class="lb-val" id="lb-photo-status">Available</span>')
    html.append("            </div>")
    html.append("          </div>")
    html.append('          <div class="lightbox-actions">')
    html.append('            <a href="#" target="_blank" rel="noopener noreferrer" id="lb-wiki-btn" class="btn-wiki">View Film on Wikipedia ↗</a>')
    html.append("          </div>")
    html.append("        </div>")
    html.append("      </div>")
    html.append("    </div>")
    html.append("  </div>")

    # Footer
    html.append('  <footer class="site-footer">')
    html.append('    <div class="footer-container">')
    html.append('      <p class="footer-note">Satyajit Ray Actors Database &bull; Compiled from film credits and photographic archives &bull; 82 recurring actors across 33 films (1955–1991)</p>')
    html.append('      <p class="footer-sub">Interactive Matrix designed for researchers, cinema historians, and film enthusiasts.</p>')
    html.append("    </div>")
    html.append("  </footer>")

    # Embed JSON Dataset for client-side instant filtering/sorting
    matrix_meta = {
        "total_actors": total_actors,
        "total_films": total_films,
        "total_roles": total_roles,
        "total_photos_available": total_photos_available,
        "total_posters_available": total_posters_available,
    }
    html.append(f'  <script id="matrix-meta-data" type="application/json">{json.dumps(matrix_meta)}</script>')
    html.append('  <script src="script.js"></script>')
    html.append("</body>")
    html.append("</html>")

    content = "\n".join(html)
    with open(output_path, mode="w", encoding="utf-8") as f:
        f.write(content)

    print(f"Successfully generated {output_path} ({len(content)} bytes).")
    print(f"  Actors: {total_actors}")
    print(f"  Films: {total_films}")
    print(f"  Total Roles: {total_roles}")
    print(f"  Photos Populated: {total_photos_available} / {total_roles} ({photo_pct}%)")
    print(f"  Posters Available: {total_posters_available} / {total_films}")


if __name__ == "__main__":
    actors, films = load_data()
    generate_html(actors, films, "index.html")
