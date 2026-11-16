---
title: Theme Customizer
description: The admin Theme Customizer previews this site's theme skins, edits and saves custom ones, generates color palettes, and exports the settings as YAML
preview: /images/previews/theme-customizer.jpg
layout: admin
icon: bi-palette
permalink: /about/settings/theme/
excerpt: Preview theme skins, generate palettes, customize CSS variables, and export YAML configuration.
lastmod: 2026-04-06T00:00:00.000Z
---

<!-- chroma.js — color manipulation library (BSD-3, 36 KB min) -->
<script src="https://cdn.jsdelivr.net/npm/chroma-js@2.4.2/chroma.min.js"></script>

<!-- ═══ Mode + Skin bar (always visible) ═══ -->
<div class="d-flex flex-wrap align-items-center gap-3 mb-4 p-3 bg-body-tertiary rounded-3 border">
  <div class="d-flex align-items-center gap-2">
    <i class="bi bi-moon-stars"></i>
    <span class="fw-semibold small">Mode:</span>
    {% include components/halfmoon.html %}
  </div>
  <div class="vr d-none d-sm-block"></div>
  <div class="d-flex align-items-center gap-2 flex-grow-1">
    <i class="bi bi-palette2"></i>
    <span class="fw-semibold small">Skin:</span>
    {% assign skins_list = "air,aqua,contrast,dark,dirt,neon,mint,plum,sunrise" | split: "," %}
    {% assign active_skin = site.theme_skin | default: "dark" %}
    <div class="d-flex flex-wrap gap-1" id="quickSkinBar">
      {% for s in skins_list %}
      <button class="btn btn-sm {% if s == active_skin %}btn-primary{% else %}btn-outline-secondary{% endif %}" data-quick-skin="{{ s }}" title="{{ s | capitalize }}">{{ s | capitalize }}</button>
      {% endfor %}
    </div>
  </div>
</div>

<ul class="nav nav-tabs" id="themeTabs" role="tablist">
  <li class="nav-item" role="presentation">
    <button class="nav-link active" id="tab-skins" data-bs-toggle="tab" data-bs-target="#pane-skins" type="button" role="tab" aria-controls="pane-skins" aria-selected="true">
      <i class="bi bi-brush me-1"></i>Skins
    </button>
  </li>
  <li class="nav-item" role="presentation">
    <button class="nav-link" id="tab-skin-editor" data-bs-toggle="tab" data-bs-target="#pane-skin-editor" type="button" role="tab" aria-controls="pane-skin-editor" aria-selected="false">
      <i class="bi bi-pencil-square me-1"></i>Skin Editor
    </button>
  </li>
  <li class="nav-item" role="presentation">
    <button class="nav-link" id="tab-palette" data-bs-toggle="tab" data-bs-target="#pane-palette" type="button" role="tab" aria-controls="pane-palette" aria-selected="false">
      <i class="bi bi-rainbow me-1"></i>Palette Generator
    </button>
  </li>
  <li class="nav-item" role="presentation">
    <button class="nav-link" id="tab-live" data-bs-toggle="tab" data-bs-target="#pane-live" type="button" role="tab" aria-controls="pane-live" aria-selected="false">
      <i class="bi bi-sliders me-1"></i>Live Preview
    </button>
  </li>
  <li class="nav-item" role="presentation">
    <button class="nav-link" id="tab-colors" data-bs-toggle="tab" data-bs-target="#pane-colors" type="button" role="tab" aria-controls="pane-colors" aria-selected="false">
      <i class="bi bi-palette2 me-1"></i>Color Editor
    </button>
  </li>
  <li class="nav-item" role="presentation">
    <button class="nav-link" id="tab-export" data-bs-toggle="tab" data-bs-target="#pane-export" type="button" role="tab" aria-controls="pane-export" aria-selected="false">
      <i class="bi bi-download me-1"></i>Export
    </button>
  </li>
</ul>

<div class="tab-content pt-4" id="themeTabContent">

  <!-- ═══════ Skin Preview Tab ═══════ -->
  <div class="tab-pane fade show active" id="pane-skins" role="tabpanel">
    {% include components/theme-customizer.html %}
  </div>

  <!-- ═══════ Skin Editor Tab ═══════ -->
  <div class="tab-pane fade" id="pane-skin-editor" role="tabpanel">

    <p class="text-body-secondary mb-3">
      Edit any built-in skin or create your own. Adjust gradient colors, preview palettes, tune the SVG filter, then apply live.
    </p>

    <!-- Toolbar -->
    <div class="d-flex flex-wrap gap-2 mb-4 align-items-end">
      <div>
        <label class="form-label fw-semibold small" for="skin-editor-select">Base Skin</label>
        <select class="form-select form-select-sm" id="skin-editor-select" style="min-width:160px"></select>
      </div>
      <div>
        <label class="form-label fw-semibold small" for="skin-editor-name">Name</label>
        <input type="text" class="form-control form-control-sm" id="skin-editor-name" placeholder="my-custom-skin" style="min-width:160px">
      </div>
      <button class="btn btn-sm btn-outline-success" id="skin-editor-save" title="Save to localStorage">
        <i class="bi bi-save me-1"></i>Save Custom
      </button>
      <button class="btn btn-sm btn-outline-danger" id="skin-editor-delete" title="Delete custom skin" disabled>
        <i class="bi bi-trash me-1"></i>Delete
      </button>
    </div>

    <!-- Gradient stop color pickers -->
    <h6 class="fw-semibold"><i class="bi bi-palette me-1"></i>Gradient Colors</h6>
    <div class="row g-3 mb-4" id="skin-editor-stops"></div>

    <!-- Live gradient preview -->
    <h6 class="fw-semibold"><i class="bi bi-image me-1"></i>Gradient Preview</h6>
    <div id="skin-editor-preview" class="rounded-3 overflow-hidden mb-4" style="height:120px;border:1px solid rgba(128,128,128,.15)"></div>

    <!-- Auto-generated palettes (colorffy-style) -->
    <div id="skin-editor-palettes" class="mb-4"></div>

    <!-- Advanced SVG filter controls -->
    <details class="mb-4">
      <summary class="fw-semibold"><i class="bi bi-sliders2 me-1"></i>Advanced: SVG Filter Controls</summary>
      <div id="skin-editor-filters" class="mt-3"></div>
    </details>

    <!-- Action buttons -->
    <div class="d-flex flex-wrap gap-2">
      <button class="btn btn-primary" id="skin-editor-apply">
        <i class="bi bi-check-circle me-1"></i>Apply Live
      </button>
      <button class="btn btn-outline-secondary" id="skin-editor-reset">
        <i class="bi bi-arrow-counterclockwise me-1"></i>Reset to Built-in
      </button>
      <button class="btn btn-outline-secondary" id="skin-editor-download-gradient">
        <i class="bi bi-download me-1"></i>Download Gradient SVG
      </button>
      <button class="btn btn-outline-secondary" id="skin-editor-download-pattern">
        <i class="bi bi-download me-1"></i>Download Pattern SVG
      </button>
      <button class="btn btn-outline-secondary" id="skin-editor-copy-css">
        <i class="bi bi-clipboard me-1"></i>Copy CSS
      </button>
    </div>

    <div class="alert alert-info mt-4 small">
      <i class="bi bi-info-circle me-1"></i>
      Custom skins are stored in your browser's localStorage and persist across visits.
      Use <strong>Apply Live</strong> to see your changes on this page instantly.
    </div>

  </div>

  <!-- ═══════ Palette Generator Tab ═══════ -->
  <div class="tab-pane fade" id="pane-palette" role="tabpanel">

    <p class="text-body-secondary mb-3">Generate harmonious color palettes from a base color using color theory algorithms.</p>

    <div class="row g-3 mb-4 align-items-end">
      <div class="col-auto">
        <label class="form-label fw-semibold small" for="palette-base">Base Color</label>
        <div class="input-group input-group-sm">
          <input type="color" class="form-control form-control-color" id="palette-base" value="#0d6efd" title="Choose base color">
          <input type="text" class="form-control" id="palette-base-hex" value="#0d6efd" style="max-width:100px">
        </div>
      </div>
      <div class="col-auto">
        <label class="form-label fw-semibold small" for="palette-harmony">Harmony</label>
        <select class="form-select form-select-sm" id="palette-harmony">
          <option value="complementary">Complementary</option>
          <option value="analogous">Analogous</option>
          <option value="triadic" selected>Triadic</option>
          <option value="split-complementary">Split-Complementary</option>
          <option value="tetradic">Tetradic</option>
          <option value="monochromatic">Monochromatic</option>
        </select>
      </div>
      <div class="col-auto">
        <button class="btn btn-sm btn-primary" id="palette-generate">
          <i class="bi bi-palette me-1"></i>Generate
        </button>
      </div>
    </div>

    <div id="palette-swatches"></div>

  </div>

  <!-- ═══════ Live Preview Tab ═══════ -->
  <div class="tab-pane fade" id="pane-live" role="tabpanel">

    <div class="d-flex justify-content-between align-items-center mb-3">
      <p class="text-body-secondary mb-0">Edit Bootstrap CSS variables below. Changes render instantly on this page.</p>
      <button class="btn btn-sm btn-outline-warning" id="live-reset">
        <i class="bi bi-arrow-counterclockwise me-1"></i>Reset
      </button>
    </div>

    <div id="live-editor-fields"></div>

    <div class="alert alert-info mt-4 small">
      <i class="bi bi-info-circle me-1"></i>
      Changes are live on this page only. Use the <strong>Export</strong> tab to copy your configuration for permanent use.
    </div>

  </div>

  <!-- ═══════ Color Editor Tab ═══════ -->
  <div class="tab-pane fade" id="pane-colors" role="tabpanel">

    <p class="text-body-secondary mb-3">
      Fine-tune individual theme colors. These map to <code>site.theme_color</code> in your <code>_config.yml</code>.
    </p>

    <div class="row g-3" id="color-editor-fields">
      {% for pair in site.theme_color %}
      <div class="col-sm-6 col-lg-4">
        <label class="form-label fw-semibold small">{{ pair[0] | capitalize }}</label>
        <div class="input-group input-group-sm">
          <input type="color" class="form-control form-control-color" value="{{ pair[1] }}" data-color-key="{{ pair[0] }}">
          <input type="text" class="form-control" value="{{ pair[1] }}" data-color-text="{{ pair[0] }}">
        </div>
      </div>
      {% endfor %}
    </div>

  </div>

  <!-- ═══════ Export YAML Tab ═══════ -->
  <div class="tab-pane fade" id="pane-export" role="tabpanel">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h5 class="mb-0"><i class="bi bi-filetype-yml me-1"></i> Theme Configuration YAML</h5>
      <div class="d-flex gap-2">
        <button class="btn btn-sm btn-outline-primary" id="theme-copy-yaml" title="Copy to clipboard">
          <i class="bi bi-clipboard me-1"></i>Copy
        </button>
        <button class="btn btn-sm btn-outline-secondary" id="theme-download-yaml" title="Download .yml file">
          <i class="bi bi-download me-1"></i>Download
        </button>
      </div>
    </div>
    <pre class="bg-dark text-light p-3 rounded" style="max-height:500px;overflow:auto;font-size:.85rem"><code id="theme-yaml-output">Loading...</code></pre>
  </div>

</div>

<!-- Quick skin bar integration -->
<script>
document.addEventListener('DOMContentLoaded', function () { if (typeof zer0Bg === 'undefined') return; document.querySelectorAll('#quickSkinBar [data-quick-skin]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      zer0Bg.setSkin(this.dataset.quickSkin);
      document.querySelectorAll('#quickSkinBar [data-quick-skin]').forEach(function (b) {
        b.classList.replace('btn-primary', 'btn-outline-secondary');
      });
      this.classList.replace('btn-outline-secondary', 'btn-primary');
    });
}); });
</script>
<script src="{{ '/assets/js/theme-customizer.js' | relative_url }}" defer></script>
<script src="{{ '/assets/js/palette-generator.js' | relative_url }}" defer></script>
<script src="{{ '/assets/js/skin-editor.js' | relative_url }}" defer></script>
