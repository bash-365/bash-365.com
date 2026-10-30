# ==============================================================================
# Zer0-Mistakes Jekyll Theme - Gemfile
# ==============================================================================
# 
# Philosophy: ZERO VERSION PINS
# - Let Bundler resolve the latest compatible versions at build time
# - Build fails immediately if incompatible → caught in CI, not production
# - Production always gets exactly what passed TEST (via Gemfile.lock)
#
# Inherited from the theme repo, where it is documented in full:
# https://github.com/bamr87/zer0-mistakes/blob/main/docs/systems/ZERO_PIN_STRATEGY.md
# (there is no copy of that doc in this repo).
#
# Two honest caveats for this repo: the theme below is pinned to a local path
# whenever one is there, and no Gemfile.lock is committed (it is in .gitignore
# and _config.yml `exclude`), so "production gets exactly what passed TEST" does
# not hold here. Production is GitHub Pages, which resolves its own gem set
# anyway. build-validate.yml builds with its own generated Gemfile; the fleet's
# shared gate (.github/workflows/ci.yml) builds with this one.
# ==============================================================================

source "https://rubygems.org"

# Load gem specification (contains runtime dependencies)
# gemspec

# ------------------------------------------------------------------------------
# Core Dependencies - No version constraints → always latest compatible
# ------------------------------------------------------------------------------

# GitHub Pages gem (includes jekyll and most plugins)
# Note: When using GitHub Pages hosting, this provides:
#   - jekyll-remote-theme
#   - jekyll-feed
#   - jekyll-sitemap
#   - jekyll-seo-tag
#   - jekyll-paginate
# Note: github-pages uses Jekyll 3.x (not 4.x) - this is by design for GitHub Pages stability
# We use >= 228 to ensure we get a version compatible with Ruby 3.x
gem "github-pages", ">= 228", group: :jekyll_plugins

# Zer0-Mistakes theme gem (needed for local/Docker dev with theme: in _config_dev.yml)
#
# This path gem is a deliberate LOCAL-DEV MOUNT, not a workaround: it lets the
# Docker/devcontainer stack render against a live theme checkout so theme work
# can be tried here before it ships. It is local-dev only — production
# (GitHub Pages) uses `remote_theme` from _config.yml, Azure uses the published
# gem from Gemfile.azure, and build-validate.yml writes its own Gemfile
# without this line.
#
# The old reason for the path — "waiting for a gem version with admin
# includes" — is obsolete: the published gem has shipped _layouts/admin.html
# and _includes/navigation/admin-nav.html since v1.26.0. Switching this line
# back to `gem "jekyll-theme-zer0"` is therefore possible, but docker-compose.yml,
# Dockerfile, and .claude/agents/jekyll-build-validator.md all expect the
# /zer0-mistakes mount, so that is a migration of its own.
#
# Path resolution:
#   - Docker/devcontainer: compose mounts the theme checkout at /zer0-mistakes (default)
#   - Host-side bundling:  export ZER0_MISTAKES_PATH=/path/to/zer0-mistakes first
#   - Neither (the shared CI gate, a fresh clone): the published gem, the same
#     one Gemfile.azure uses. A ZER0_MISTAKES_PATH that is set is always used,
#     so a mistyped path still fails instead of quietly building the published
#     theme.
zer0_mistakes = ENV["ZER0_MISTAKES_PATH"] || ("/zer0-mistakes" if File.directory?("/zer0-mistakes"))
if zer0_mistakes
  gem "jekyll-theme-zer0", path: zer0_mistakes
else
  gem "jekyll-theme-zer0"
end

# The zer0 stack's preview-banner engine (bamr87/zer0-image-generator). Adds
# `bundle exec jekyll preview-images` (--list-missing, --dry-run, -f <file>) and
# reads the one `preview_images:` block in _config.yml. It registers only that
# command — nothing runs during `jekyll build` — so it lives here, in the local
# dev stack, and not in Gemfile.azure or CI's Gemfile.ci: generation is never
# part of a production build. It replaced the vendored
# _plugins/preview_image_generator.rb. Constrained, unlike the rest of this
# file, because the gem is pre-1.0 and a minor release may change the command.
gem "zer0-image-generator", "~> 0.6", group: :jekyll_plugins

# Web server for Ruby 3.0+ (required since WEBrick removed from stdlib)
gem "webrick"

# FFI for native extensions
gem "ffi"

# CommonMarker for Markdown processing
gem "commonmarker"

# Mermaid diagram support
gem "jekyll-mermaid"

# Faraday retry middleware for Faraday v2.0+
gem "faraday-retry"

# ------------------------------------------------------------------------------
# Development & Test - Only installed in dev/test environments
# ------------------------------------------------------------------------------
group :development, :test do
  # HTML validation and link checking
  gem "html-proofer"
  
  # Testing framework
  gem "rspec"
  
  # Task automation
  gem "rake"
  
  # Code linting (optional but recommended)
  gem "rubocop"
  gem "rubocop-rake"
end

# ------------------------------------------------------------------------------
# Platform-specific dependencies
# ------------------------------------------------------------------------------
# Ensure native gems work across platforms
platforms :windows, :jruby do
  gem "tzinfo"
  gem "tzinfo-data"
end

# Performance booster for watching directories on Windows
gem "wdm", :platforms => [:windows]