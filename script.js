/**
 * Satyajit Ray Actors & Films Matrix Interactive Client Script
 * Provides real-time filtering, multi-criteria sorting, column decade filters,
 * density switching, crosshair highlighting, and detail lightbox modal.
 */

document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements
  const tbody = document.getElementById("matrix-tbody");
  const table = document.getElementById("matrix-table");
  const searchInput = document.getElementById("actor-search");
  const searchClearBtn = document.getElementById("search-clear");
  const sortSelect = document.getElementById("sort-select");
  const decadeButtons = document.querySelectorAll("[data-decade]");
  const photoFilterButtons = document.querySelectorAll("[data-photo-filter]");
  const densityButtons = document.querySelectorAll("[data-density]");
  const crosshairToggle = document.getElementById("crosshair-toggle");
  const highlightPendingToggle = document.getElementById("highlight-pending-toggle");
  const visibleActorsCount = document.getElementById("visible-actors-count");
  
  // Lightbox Elements
  const modal = document.getElementById("lightbox-modal");
  const modalCloseBtn = document.getElementById("lightbox-close");
  const modalBackdrop = document.getElementById("lightbox-backdrop");
  const lbImg = document.getElementById("lightbox-img");
  const lbPlaceholder = document.getElementById("lightbox-placeholder");
  const lbActorName = document.getElementById("lb-actor-name");
  const lbCharName = document.getElementById("lb-character-name");
  const lbFilmTitle = document.getElementById("lb-film-title");
  const lbFilmYear = document.getElementById("lb-film-year");
  const lbComments = document.getElementById("lb-comments");
  const lbCommentsRow = document.getElementById("lb-comments-row");
  const lbPhotoStatus = document.getElementById("lb-photo-status");
  const lbWikiBtn = document.getElementById("lb-wiki-btn");

  let currentActiveDecade = "all";
  let currentPhotoFilter = "all";
  let crosshairEnabled = crosshairToggle ? crosshairToggle.checked : true;

  // Cache actor rows
  const allRows = Array.from(tbody.querySelectorAll(".actor-row"));
  const allFilmHeaders = Array.from(table.querySelectorAll(".film-header"));

  // =========================================================================
  // 1. Search Filtering (Actor name & Character name)
  // =========================================================================
  function applyFilters() {
    const query = (searchInput.value || "").trim().toLowerCase();
    searchClearBtn.classList.toggle("visible", query.length > 0);

    let visibleCount = 0;

    allRows.forEach((row) => {
      const actorName = (row.dataset.actor || "").toLowerCase();
      const characters = (row.dataset.characters || "").toLowerCase();

      // Check text search
      const matchesSearch = !query || actorName.includes(query) || characters.includes(query);

      // Check photo filter across row
      let matchesPhotoFilter = true;
      if (currentPhotoFilter === "filled") {
        // Show row if it has at least one filled photo
        const hasFilled = row.querySelector('.role-cell[data-photo-state="filled"]');
        matchesPhotoFilter = Boolean(hasFilled);
      } else if (currentPhotoFilter === "pending") {
        // Show row if it has at least one pending photo
        const hasPending = row.querySelector('.role-cell[data-photo-state="pending"]');
        matchesPhotoFilter = Boolean(hasPending);
      }

      if (matchesSearch && matchesPhotoFilter) {
        row.style.display = "";
        visibleCount++;
      } else {
        row.style.display = "none";
      }
    });

    if (visibleActorsCount) {
      visibleActorsCount.textContent = visibleCount;
    }
  }

  if (searchInput) {
    searchInput.addEventListener("input", applyFilters);
  }

  if (searchClearBtn) {
    searchClearBtn.addEventListener("click", () => {
      searchInput.value = "";
      searchInput.focus();
      applyFilters();
    });
  }

  // =========================================================================
  // 2. Sorting (Films Count, Alphabetical, Debut Year)
  // =========================================================================
  function sortRows() {
    const sortVal = sortSelect.value;
    const rows = Array.from(tbody.querySelectorAll(".actor-row"));

    rows.sort((a, b) => {
      const nameA = a.dataset.actor || "";
      const nameB = b.dataset.actor || "";
      const countA = parseInt(a.dataset.filmCount, 10) || 0;
      const countB = parseInt(b.dataset.filmCount, 10) || 0;
      const debutA = parseInt(a.dataset.debutYear, 10) || 0;
      const debutB = parseInt(b.dataset.debutYear, 10) || 0;

      switch (sortVal) {
        case "films-desc":
          if (countB !== countA) return countB - countA;
          return nameA.localeCompare(nameB);

        case "name-asc":
          return nameA.localeCompare(nameB);

        case "name-desc":
          return nameB.localeCompare(nameA);

        case "debut-asc":
          if (debutA !== debutB) return debutA - debutB;
          return nameA.localeCompare(nameB);

        case "debut-desc":
          if (debutB !== debutA) return debutB - debutA;
          return nameA.localeCompare(nameB);

        default:
          return 0;
      }
    });

    // Re-append sorted rows to tbody
    rows.forEach((r) => tbody.appendChild(r));
  }

  if (sortSelect) {
    sortSelect.addEventListener("change", sortRows);
  }

  // =========================================================================
  // 3. Decade Column Filtering
  // =========================================================================
  function setDecadeFilter(decade) {
    currentActiveDecade = decade;
    decadeButtons.forEach((btn) => {
      btn.classList.toggle("active", btn.dataset.decade === decade);
    });

    // For each film column header and its cells in each row
    allFilmHeaders.forEach((th, colIdx) => {
      const filmDecade = th.dataset.decade;
      const matches = decade === "all" || filmDecade === decade;
      const displayVal = matches ? "" : "none";

      th.style.display = displayVal;

      // Update matching cells in every row (colIdx + 1 because col 0 is actor header)
      const cellIndex = colIdx + 1;
      allRows.forEach((row) => {
        const cell = row.children[cellIndex];
        if (cell) {
          cell.style.display = displayVal;
        }
      });
    });
  }

  decadeButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      setDecadeFilter(btn.dataset.decade);
    });
  });

  // =========================================================================
  // 4. Photo Status Filter (All / Available / Pending)
  // =========================================================================
  photoFilterButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      photoFilterButtons.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      currentPhotoFilter = btn.dataset.photoFilter;
      applyFilters();
    });
  });

  // =========================================================================
  // 5. Density / Zoom Controls
  // =========================================================================
  densityButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      densityButtons.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      const density = btn.dataset.density;
      document.body.classList.remove("density-compact", "density-normal", "density-large");
      document.body.classList.add(`density-${density}`);
    });
  });

  // =========================================================================
  // 6. Highlight Pending Toggle
  // =========================================================================
  if (highlightPendingToggle) {
    highlightPendingToggle.addEventListener("change", () => {
      document.body.classList.toggle("highlight-pending-active", highlightPendingToggle.checked);
    });
  }

  // =========================================================================
  // 7. Crosshair Row & Column Highlighting on Hover
  // =========================================================================
  if (crosshairToggle) {
    crosshairToggle.addEventListener("change", () => {
      crosshairEnabled = crosshairToggle.checked;
      if (!crosshairEnabled) {
        clearHighlights();
      }
    });
  }

  let activeColHeader = null;
  let activeRow = null;

  function clearHighlights() {
    if (activeColHeader) {
      activeColHeader.classList.remove("col-highlight");
      activeColHeader = null;
    }
    if (activeRow) {
      activeRow.classList.remove("row-highlight");
      const actorTh = activeRow.querySelector(".actor-header");
      if (actorTh) actorTh.classList.remove("row-highlight");
      activeRow = null;
    }
    // Remove from any cells
    document.querySelectorAll(".matrix-cell.col-highlight").forEach((c) => {
      c.classList.remove("col-highlight");
    });
  }

  tbody.addEventListener("mouseover", (e) => {
    if (!crosshairEnabled) return;

    const cell = e.target.closest(".matrix-cell");
    if (!cell) return;

    const row = cell.closest(".actor-row");
    if (!row) return;

    const cellIdx = cell.cellIndex; // 1-based because index 0 is actor header
    if (cellIdx < 1) return;

    const colHeader = allFilmHeaders[cellIdx - 1];

    if (row !== activeRow || colHeader !== activeColHeader) {
      clearHighlights();

      activeRow = row;
      activeRow.classList.add("row-highlight");
      const actorTh = activeRow.querySelector(".actor-header");
      if (actorTh) actorTh.classList.add("row-highlight");

      if (colHeader) {
        activeColHeader = colHeader;
        activeColHeader.classList.add("col-highlight");
      }

      // Highlight cells in that column
      allRows.forEach((r) => {
        const c = r.children[cellIdx];
        if (c && c !== cell) {
          c.classList.add("col-highlight");
        }
      });
    }
  });

  tbody.addEventListener("mouseleave", () => {
    if (crosshairEnabled) {
      clearHighlights();
    }
  });

  // =========================================================================
  // 8. Lightbox Modal
  // =========================================================================
  function openLightbox(data) {
    lbActorName.textContent = data.actor;
    lbCharName.textContent = data.character || "Role Uncredited";
    lbFilmTitle.textContent = data.film;
    lbFilmYear.textContent = data.year;

    if (data.comments) {
      lbComments.textContent = data.comments;
      lbCommentsRow.style.display = "flex";
    } else {
      lbCommentsRow.style.display = "none";
    }

    if (data.wiki) {
      lbWikiBtn.href = data.wiki;
      lbWikiBtn.textContent = `View “${data.film}” on Wikipedia ↗`;
      lbWikiBtn.style.display = "inline-flex";
    } else {
      lbWikiBtn.style.display = "none";
    }

    const hasPhoto = data.hasPhoto === "true";
    if (hasPhoto) {
      lbImg.src = data.photo;
      lbImg.alt = `${data.actor} as ${data.character} in ${data.film} (${data.year})`;
      lbImg.style.display = "block";
      lbPlaceholder.classList.add("is-hidden");
      lbPhotoStatus.textContent = "Photo Populated";
      lbPhotoStatus.style.color = "var(--accent-ok)";
    } else {
      lbImg.src = "";
      lbImg.style.display = "none";
      lbPlaceholder.classList.remove("is-hidden");
      lbPhotoStatus.textContent = "Photo Pending Capture";
      lbPhotoStatus.style.color = "var(--accent-warn)";
    }

    modal.classList.add("is-open");
    modal.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
    modalCloseBtn.focus();
  }

  function closeLightbox() {
    modal.classList.remove("is-open");
    modal.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
    lbImg.src = "";
  }

  // Open modal on click or Enter/Space on photo card
  tbody.addEventListener("click", (e) => {
    const trigger = e.target.closest(".photo-cell-content");
    if (trigger) {
      openLightbox({
        actor: trigger.dataset.actor,
        film: trigger.dataset.film,
        year: trigger.dataset.year,
        character: trigger.dataset.character,
        comments: trigger.dataset.comments,
        photo: trigger.dataset.photo,
        hasPhoto: trigger.dataset.hasPhoto,
        poster: trigger.dataset.poster,
        wiki: trigger.dataset.wiki,
      });
    }
  });

  tbody.addEventListener("keydown", (e) => {
    if (e.key === "Enter" || e.key === " ") {
      const trigger = e.target.closest(".photo-cell-content");
      if (trigger) {
        e.preventDefault();
        openLightbox({
          actor: trigger.dataset.actor,
          film: trigger.dataset.film,
          year: trigger.dataset.year,
          character: trigger.dataset.character,
          comments: trigger.dataset.comments,
          photo: trigger.dataset.photo,
          hasPhoto: trigger.dataset.hasPhoto,
          poster: trigger.dataset.poster,
          wiki: trigger.dataset.wiki,
        });
      }
    }
  });

  if (modalCloseBtn) modalCloseBtn.addEventListener("click", closeLightbox);
  if (modalBackdrop) modalBackdrop.addEventListener("click", closeLightbox);

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && modal.classList.contains("is-open")) {
      closeLightbox();
    }
  });
});
