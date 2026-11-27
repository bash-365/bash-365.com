# Data Directory

This directory contains YAML data files used by Jekyll to generate the site.

## Directory Structure

```
_data/
├── README.md           # This file
├── entity/             # Entity data (organization, contact info)
├── loop/               # The content loop's data: config, sources, ledger (runs/), session trace
├── org/                # The org brain's data: repos.yml (registry), standard.yml, brain.yml
└── navigation/         # Navigation configuration files
    ├── README.md       # Navigation schema documentation
    ├── main.yml        # Primary site navigation (navbar)
    ├── about.yml       # About section sidebar
    ├── docs.yml        # Documentation sidebar
    ├── posts.yml       # Blog category navigation
    ├── home.yml        # Homepage quick links
    └── services.yml    # Services sidebar
```

## Navigation Files

Navigation files follow the **zer0-mistakes theme v0.22+** schema. See [`navigation/README.md`](navigation/README.md) for the complete schema definition.

### Quick Reference

```yaml
- title: string        # Required - Display text
  url: string          # Optional - Link URL
  icon: string         # Optional - Bootstrap Icons class (bi-*)
  children: array      # Optional - Nested items
```

## Content loop data

`loop/` holds everything the [content loop](../docs/content-loop.md) needs to decide and remember: `config.yml` (cadence, caps, rotation, signal weights), `sources.yml` (which repositories it may mine), `runs/*.yml` (the ledger — one record per run, written by `scripts/loop/ledger.py` in the loop's own pull request), and `sessions.jsonl` (the committed AI-session trace, synced from the local hook queue by `scripts/loop/trace.py --sync`). See [`loop/README.md`](loop/README.md).

## Org brain data

`org/` holds what the [org brain](../docs/brain.md) needs to know about the organization rather than the site: `repos.yml` (the member repositories and the upstreams the org builds on), `standard.yml` (the agent-readiness checks, each citing the hub's UPS id) and `brain.yml` (which files are notes, of what kind). All three use the YAML subset `loop/_lib.py` reads. Validate with `python3 scripts/brain/brain.py repos --check`.

## Entity Data

The `entity/` directory contains organization-related data like company info, team members, and contact details.

## Usage in Templates

Access data files in Liquid templates:

```liquid
{% for item in site.data.navigation.main %}
  <a href="{{ item.url }}">{{ item.title }}</a>
{% endfor %}
```

## Contributing

When adding or modifying data files:
1. Validate YAML syntax before committing
2. Follow existing naming conventions
3. Update this README if adding new directories

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.