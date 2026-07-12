# Dwarka Expressway Projects — Static Mirror

A faithful, fully-static rebuild of **dwarkaexpresswayprojects.in**, generated from a complete
scrape of the site's live GraphQL data API (`api.propularity.in`). Every page is pre-rendered
HTML — no build step, no server, no database. Deploy to Vercel in one click.

## What's included
- **1 homepage** (`index.html`)
- **11 category/route pages**: residential, commercial, affordable, SCO plots, upcoming,
  ready-to-move, best-deals, all-projects, luxury, contact, privacy-policy
- **65 builder / sector / budget landing pages** (e.g. `godrej-properties.html`,
  `projects-in-sector-83-gurgaon.html`, `3bhk-apartment-on-dwarka-expressway.html`)
- **176 project detail pages** (`projects/<slug>.html`) — full data: price, floor plans,
  amenities, gallery, Leaflet map, builder, SEO

Total: **255 HTML pages**, each generated from real scraped content.

## Features
- Live **search-by-project-name** overlay (client-side, instant)
- **Enquiry / lead forms** on every page + detail pages (post to the original Google-Sheets endpoint)
- **Image gallery lightbox** and **Leaflet location maps** on detail pages
- Responsive design, RERA/trust badges, floating call button, original brand assets

## Data source
The original site is a React SPA backed by a GraphQL API. The data was extracted via:
```
POST https://api.propularity.in/graphql
  query { dwarkaProjectDetails(...) { projects { ...full schema... } } }
```
Saved locally as: `projects.json` (176 projects, full detail), `seo.json` (68 pages),
`allurls.json` (site map). Real project images are hotlinked from the public S3 bucket
(`dwarkaexpressway-bucket.s3.ap-south-1.amazonaws.com`) — no local mirroring needed.

## Rebuild (optional)
```bash
python build.py   # regenerates all HTML from the JSON data files
```

## Deploy to Vercel
- Drag the project folder into https://vercel.com/new , or import the Git repo.
- No framework / no build step (static). `vercel.json` already configures this.
- All links are relative, so it works from any base path.

## File structure
```
index.html, *.html        # all top-level + landing + category pages
projects/*.html           # 176 individual project detail pages
css/style.css             # design system (matches original tokens)
js/site.js                # search, enquiry, gallery, map logic
assets/                   # logo, phone gif, RERA/badge icons
projects.json, seo.json, allurls.json   # scraped data
build.py                  # generator (data -> HTML)
```
