
# YourMasterOverseer Static Site

This is the static UI shell for:

- YourMasterOverseer.com
- The Genesis System portal
- Bots / Battle / Evolution / Marketplace / Economy pages

It is UI-only (no backend yet) and is designed to be deployed directly to GitHub Pages.

## Structure

- /index.html              -> Landing page
- /dashboard.html          -> High-level dashboard
- /TheGenesisSystem        -> Genesis portal
- /TheGenesisSystem/bots   -> Bots UI shell
- /TheGenesisSystem/battle -> Battle UI shell
- /TheGenesisSystem/evolution -> Evolution UI shell
- /TheGenesisSystem/marketplace -> Marketplace UI shell
- /TheGenesisSystem/economy -> Economy UI shell
- /assets/css/neon.css     -> Neon brand theme
- /assets/js/ui.js         -> Placeholder JS

## Usage

1. Run this script:
   python build_site.py

2. A folder called `YourMasterOverseerSite` will be created.

3. Push the contents of `YourMasterOverseerSite` to your GitHub repo
   (or set it as the root for GitHub Pages).

4. Later, wire backend APIs into this UI.
