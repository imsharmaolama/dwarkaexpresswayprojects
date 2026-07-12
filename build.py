#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the static Dwarka Expressway Projects site from scraped data."""
import json, os, html, re

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECTS = json.load(open(os.path.join(ROOT, "projects.json"), encoding="utf-8"))
SEO = json.load(open(os.path.join(ROOT, "seo.json"), encoding="utf-8"))
_raw = json.load(open(os.path.join(ROOT, "allurls.json"), encoding="utf-8"))
ALLURLS = [u["slug"].strip() for u in _raw.get("data", {}).get("allUrls", _raw if isinstance(_raw, list) else [])]

PHONE = "9999063322"
SITE = "https://www.dwarkaexpresswayprojects.in"  # original, for reference in footer

def slug_file(s):
    return s.replace("/", "-").strip()

def esc(s):
    return html.escape(str(s or ""), quote=True)

def img_link(im):
    if isinstance(im, dict):
        img = im.get("image") or {}
        if isinstance(img, dict):
            return img.get("s3_link") or ""
    return ""

def first_img(p):
    for im in (p.get("images") or []):
        l = img_link(im)
        if l:
            return l
    return "assets/logo.png"

def loc_addr(p):
    loc = p.get("location") or {}
    addr = loc.get("address") or ""
    city = (loc.get("city") or [{}])[0].get("name") if isinstance(loc.get("city"), list) else (loc.get("city") or {}).get("name")
    mic = (loc.get("micro_location") or [{}])[0].get("name") if isinstance(loc.get("micro_location"), list) else (loc.get("micro_location") or {}).get("name")
    parts = [x for x in [addr, mic, city] if x]
    return ", ".join(parts) if parts else "Dwarka Expressway, Gurgaon"

def builder_name(p):
    b = p.get("builder")
    if isinstance(b, list) and b:
        return b[0].get("name") or ""
    if isinstance(b, dict):
        return b.get("name") or ""
    return ""

# ---------- shared fragments ----------
NAV = """
<nav class="main-nav">
  <li><a href="residential-projects-gurgaon.html">New Launch</a></li>
  <li><a href="sco-plots-gurgaon.html">SCO Plots</a></li>
  <li><a href="best-deals.html">Best Projects</a></li>
  <li><a href="ready-to-move-flats-in-dwarka-expressway-gurgaon.html">Ready To Move</a></li>
</nav>"""

def header(active=""):
    return f"""<header class="site-header">
  <div class="container header-inner">
    <a href="index.html" class="brand"><img src="assets/logo.png" alt="Dwarka Expressway logo">Dwarka Expressway</a>
    {NAV}
    <div class="header-cta">
      <a class="phone-btn" href="tel:{PHONE}"><img src="assets/phone.gif" alt="phone"> {PHONE}</a>
      <button class="enquire-btn" data-enquire="">Enquire Now</button>
      <button class="menu-toggle" aria-label="menu">&#9776;</button>
    </div>
  </div>
</header>"""

FOOTER = f"""<footer class="site-footer">
  <div class="container footer-grid">
    <div>
      <h5>Dwarka Expressway Projects</h5>
      <p>Dwarka Expressway is the upcoming residential hub. Because of its strategic location, it is the top pick by residents of Gurgaon &amp; Delhi. A grade social &amp; physical infrastructure, fast-paced connectivity &amp; landscape greenery all around make it an ideal site to live flawlessly in NCR.</p>
      <div class="footer-social">
        <a href="#" aria-label="facebook"><i class="fab fa-facebook-f"></i></a>
        <a href="#" aria-label="instagram"><i class="fab fa-instagram"></i></a>
        <a href="#" aria-label="linkedin"><i class="fab fa-linkedin-in"></i></a>
      </div>
    </div>
    <div>
      <h5>Popular Searches</h5>
      <div class="link-col">
        <a href="best-deals.html">Best Projects on Dwarka Expressway</a>
        <a href="residential-projects-gurgaon.html">New Launch Projects</a>
        <a href="sco-plots-gurgaon.html">SCO Plots in Gurgaon</a>
        <a href="residential-projects-gurgaon.html">Residential Projects</a>
        <a href="commercial-projects-gurgaon.html">Commercial Projects</a>
        <a href="projects-list.html">All Projects</a>
      </div>
    </div>
    <div>
      <h5>Buy Property</h5>
      <div class="link-col">
        <a href="affordable-housing-projects.html">Affordable Housing</a>
        <a href="residential-projects-gurgaon.html">Apartments</a>
        <a href="buy-plots.html">Plots</a>
        <a href="commercial-projects-gurgaon.html">Shops</a>
        <a href="luxury-projects.html">Villas</a>
      </div>
    </div>
    <div>
      <h5>Contact Us</h5>
      <p>7C, Level Ground, Omaxe Gurgaon Mall, Sohna Road, Gurgaon</p>
      <p><a href="tel:{PHONE}" style="color:#fff;font-weight:700">{PHONE}</a></p>
      <p><a href="contact.html" style="color:#fff">Enquire Now</a></p>
    </div>
  </div>
  <div class="container footer-bottom">&copy; {2026} Dwarka Expressway Projects. All rights reserved. RERA Approved &middot; Free Site Visit &middot; Special Price Offers.</div>
</footer>"""

def scripts(projects_js="[]"):
    return f"""<script>window.__PROJECTS__={projects_js};</script>
<script src="https://kit.fontawesome.com/c260689fd1.js" crossorigin="anonymous"></script>
<script src="js/site.js"></script>"""

def search_modal():
    return """<div class="search-modal" id="searchModal">
  <div class="box">
    <input id="searchBox" placeholder="Search by Project Name...">
    <div class="search-results" id="searchResults"></div>
    <div style="text-align:right;margin-top:10px"><button class="enquire-btn" data-close="search">Close</button></div>
  </div>
</div>"""

def enq_modal():
    return """<div class="modal-overlay" id="enqModal">
  <div class="modal">
    <button class="modal-close" data-close="enq">&times;</button>
    <h3 id="enqTitle">Enquire Now</h3>
    <form data-lead>
      <input type="hidden" id="enqProject" name="project">
      <div class="form-field"><input name="name" placeholder="Your Name" required></div>
      <div class="form-field"><input name="email" type="email" placeholder="Email" required></div>
      <div class="form-field"><input name="phone" placeholder="Mobile Number" required></div>
      <div class="form-field"><textarea name="note" rows="3" placeholder="Message (optional)"></textarea></div>
      <button class="submit-btn" type="submit">Submit Enquiry</button>
      <p class="form-note">We respect your privacy. Your details are safe with us.</p>
    </form>
  </div>
</div>
<div class="lightbox" id="lightbox"><span class="lb-close" onclick="closeLightbox()">&times;</span><img id="lbImg" src="" alt=""></div>
<button class="phone-float" onclick="location.href='tel:9999063322'"><img src="assets/phone.gif" alt="Call"></button>"""

def card(p):
    img = first_img(p)
    tag = p.get("project_tag") or ""
    rating = p.get("ratings")
    rating_html = f'<span class="rating-badge">&#9733; {rating}</span>' if rating else ""
    tag_html = f'<span class="project_tag">{esc(tag)}</span>' if tag else ""
    return f"""<div class="project_card">
  <div class="img_card">
    <a href="projects/{esc(slug_file(p['slug']))}.html"><img class="img_cover" src="{img}" alt="{esc(p['name'])}" loading="lazy"></a>
    {tag_html}{rating_html}
  </div>
  <div class="card_body">
    <a href="projects/{esc(slug_file(p['slug']))}.html" class="card_title">{esc(p['name'])}</a>
    <div class="property_location"><i class="fas fa-map-marker-alt"></i> {esc(loc_addr(p))}</div>
    <div class="property_price">{esc(p.get('starting_price') or 'Call for Price')}</div>
  </div>
  <div class="card_footer">
    <a href="projects/{esc(slug_file(p['slug']))}.html">View Details</a>
    <button class="enq" data-enquire="{esc(p['name'])}">Enquire</button>
  </div>
</div>"""

def section(title, sub, plist, viewall):
    cards = "".join(card(p) for p in plist[:8])
    return f"""<section class="section"><div class="container">
  <div class="section-head"><h2 class="best_project_heading">{esc(title)}</h2>
  {f'<a class="view-all" href="{viewall}">View All &rarr;</a>' if viewall else ''}</div>
  <p class="section-sub">{esc(sub)}</p>
  <div class="grid">{cards}</div>
</section>"""

# ---------- index ----------
def build_index():
    new = [p for p in PROJECTS if p.get("project_status")=="New Launch"]
    ready = [p for p in PROJECTS if p.get("project_status")=="Ready To Move"]
    comm = [p for p in PROJECTS if p.get("project_type")=="commercial"]
    intro = (SEO.get("", {}) or {}).get("header_description") or ("Dwarka Expressway is the upcoming residential hub. Because of its strategic location, it is the top pick by residents of Gurgaon & Delhi. A grade Social & Physical Infrastructure, Fast-Paced Connectivity, & Landscape Greenery all around make it an ideal place to live in NCR.")
    html_doc = f"""<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Dwarka Expressway Projects - {len(PROJECTS)}+ Real Estate / Property for sale on Dwarka Expressway</title>
<meta name="description" content="Explore {len(PROJECTS)}+ residential & commercial projects on Dwarka Expressway, Gurgaon. New Launch, Ready to Move, SCO Plots & Affordable Housing with RERA approved listings.">
<link rel="stylesheet" href="css/style.css">
</head><body>
{header()}
<section class="hero">
  <div class="container">
    <div class="badges">
      <span><img src="assets/rs-sign.gif" alt="RERA"> RERA Approved</span>
      <span><img src="assets/discount.svg" alt="offer"> Free Site-Visit</span>
      <span><img src="assets/discount.svg" alt="offer"> Special Price Offers</span>
    </div>
    <h1>Explore Dwarka Expressway<br>Projects in Gurgaon</h1>
    <div class="search-wrap"><input class="search-box" placeholder="Search by Project Name" data-search-open></div>
  </div>
</section>
{section("New Launch Projects on Dwarka Expressway", intro, new, "residential-projects-gurgaon.html")}
{section("Ready To Move Projects on Dwarka Expressway", "", ready, "ready-to-move-flats-in-dwarka-expressway-gurgaon.html")}
{section("Commercial Projects on Dwarka Expressway", "", comm, "commercial-projects-gurgaon.html")}
{FOOTER}
{search_modal()}{enq_modal()}
{scripts(json.dumps([mini(p) for p in PROJECTS], ensure_ascii=False))}
</body></html>"""
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(html_doc)

def mini(p):
    return {"name":p.get("name"),"slug":p.get("slug"),"file":slug_file(p.get("slug") or ""),"starting_price":p.get("starting_price"),
            "configuration":p.get("configuration"),"location":p.get("location"),
            "images":[{"image":{"s3_link":img_link(im)}} for im in (p.get("images") or []) if img_link(im)]}

# ---------- category / listing pages ----------
def build_listing(slug, title, plist, blurb="", is_home_route=False):
    cards = "".join(card(p) for p in plist)
    seo = SEO.get(slug) or {}
    h1 = seo.get("title") or title
    desc = seo.get("footer_description") or blurb or (f"Browse {len(plist)} {title.lower()} on Dwarka Expressway, Gurgaon. RERA approved listings with prices, floor plans & amenities.")
    html_doc = f"""<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(h1)}</title>
<meta name="description" content="{esc((seo.get('description') or desc)[:300])}">
<link rel="stylesheet" href="css/style.css">
</head><body>
{header()}
<div class="breadcrumb"><div class="container"><a href="index.html">Home</a> / {esc(title)}</div></div>
<section class="section"><div class="container">
  <h1 class="best_project_heading">{esc(title)}</h1>
  <p class="section-sub">{esc(desc)}</p>
  <div class="listing-grid">{cards}</div>
</section>
<div class="container"><div class="seo-content">{seo_block(seo)}</div></div>
{FOOTER}
{search_modal()}{enq_modal()}
{scripts(json.dumps([mini(p) for p in PROJECTS], ensure_ascii=False))}
</body></html>"""
    fn = "index.html" if is_home_route else f"{slug}.html"
    open(os.path.join(ROOT, fn), "w", encoding="utf-8").write(html_doc)

def seo_block(seo):
    out = ""
    if seo.get("footer_title"):
        out += f"<h2>{esc(seo['footer_title'])}</h2>"
    if seo.get("footer_description"):
        out += f"<p>{esc(seo['footer_description'])}</p>"
    return out or "<h2>About Dwarka Expressway</h2><p>Dwarka Expressway (also known as Northern Peripheral Road) is a 29.5 km expressway connecting Dwarka in Delhi to Kherki Daula on NH-48 in Gurgaon, emerging as the most sought-after real estate corridor in NCR.</p>"

# ---------- detail pages ----------
def build_detail(p):
    slug = p["slug"]
    imgs = [img_link(im) for im in (p.get("images") or [])]
    imgs = [i for i in imgs if i]
    gallery = "".join(f'<img src="{i}" alt="{esc(p["name"])}" loading="lazy" onclick="openLightbox(\'{i}\')">' for i in imgs) or f'<img src="{first_img(p)}" alt="{esc(p["name"])}">'
    loc = loc_addr(p)
    bname = builder_name(p)
    price = p.get("starting_price") or "Call for Price"
    # price table
    plans = p.get("plans") or []
    rows = ""
    for pl in plans:
        if not pl.get("should_show", True): continue
        cat = (pl.get("category") or {}).get("name") if isinstance(pl.get("category"), dict) else pl.get("category")
        size = f"{pl.get('size','')} {pl.get('size_sq','')}".strip()
        rows += f"<tr><td>{esc(cat or '—')}</td><td>{esc(size)}</td><td>{esc(pl.get('price') or 'Call for Price')}</td></tr>"
    price_table = f'<table class="price-table"><tr><th>Configuration</th><th>Size</th><th>Price</th></tr>{rows}</table>' if rows else f'<p>Starting Price: <b>{esc(price)}</b></p>'
    # amenities
    ams = p.get("amenties") or []
    amen = "".join(f"<span>{esc(a.get('name'))}</span>" for a in ams) or "<span>Amenities available on request</span>"
    # description / highlights / advantages
    desc = p.get("description") or p.get("short_descrip") or ""
    highlights = p.get("highlights") or ""
    advantages = p.get("advantages") or ""
    features = p.get("features") or ""
    # map
    lat = (p.get("location") or {}).get("latitude")
    lng = (p.get("location") or {}).get("longitude")
    map_html = ""
    if lat and lng:
        map_html = f"""<div id="map" data-lat="{lat}" data-lng="{lng}"></div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script>setTimeout(()=>{{try{{var m=L.map('map').setView([{lat},{lng}],14);L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}@2x.png').addTo(m);L.marker([{lat},{lng}]).addTo(m).bindPopup('{esc(p['name'])}');}}catch(e){{}}}},300);</script>"""
    # brochure / master plan
    mp = (p.get("master_plan") or {}).get("s3_link")
    brochure = (p.get("brochure") or {}).get("s3_link")
    downloads = ""
    if mp: downloads += f'<a class="view-all" href="{mp}" target="_blank">Download Master Plan</a> '
    if brochure: downloads += f'<a class="view-all" href="{brochure}" target="_blank">Download Brochure</a>'

    html_doc = f"""<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc((p.get('seo') or {}).get('title') or f"{p['name']} | Price, Floor Plan & Brochure")}</title>
<meta name="description" content="{esc(((p.get('seo') or {}).get('description') or desc or p['name'])[:300])}">
<link rel="stylesheet" href="../css/style.css">
</head><body>
{header().replace('assets/','../assets/').replace('css/','../css/').replace('js/','../js/').replace('index.html','../index.html').replace('projects/','')}
<div class="breadcrumb"><div class="container"><a href="../index.html">Home</a> / <a href="../residential-projects-gurgaon.html">Projects</a> / {esc(p['name'])}</div></div>
<section class="detail-hero"><div class="container">
  <h1 class="detail-title">{esc(p['name'])}</h1>
  <div class="detail-meta">
    <span><b>Builder:</b> {esc(bname or '—')}</span>
    <span><b>Type:</b> {esc(p.get('project_type') or '—')}</span>
    <span><b>Status:</b> {esc(p.get('project_status') or '—')}</span>
    <span><b>Location:</b> {esc(loc)}</span>
  </div>
  <div class="property_price" style="font-size:20px">Starting from {esc(price)}</div>
  {downloads}
  <div class="gallery">{gallery}</div>
</div></section>
<section class="section"><div class="container"><div class="detail-grid">
  <div>
    <div class="detail-block"><h3>Overview</h3>{desc or '<p>'+esc(p.get('banner_bullets') or 'Project details coming soon.')+'</p>'}</div>
    {f'<div class="detail-block"><h3>Highlights</h3>{highlights}</div>' if highlights.strip() else ''}
    {f'<div class="detail-block"><h3>Price & Floor Plans</h3>{price_table}</div>' if 'table' in price_table else f'<div class="detail-block"><h3>Price</h3>{price_table}</div>'}
    <div class="detail-block"><h3>Amenities</h3><div class="amenity-chips">{amen}</div></div>
    {f'<div class="detail-block"><h3>Advantages</h3>{advantages}</div>' if advantages.strip() else ''}
    {f'<div class="detail-block"><h3>Features</h3>{features}</div>' if features.strip() else ''}
    {f'<div class="detail-block"><h3>Location Map</h3>{map_html}</div>' if map_html else ''}
  </div>
  <aside>
    <div class="enquiry-card">
      <h3>Get Best Price & Site Visit</h3>
      <form data-lead>
        <input type="hidden" name="project" value="{esc(p['name'])}">
        <div class="form-field"><input name="name" placeholder="Your Name" required></div>
        <div class="form-field"><input name="email" type="email" placeholder="Email" required></div>
        <div class="form-field"><input name="phone" placeholder="Mobile Number" required></div>
        <div class="form-field"><textarea name="note" rows="3" placeholder="Message (optional)"></textarea></div>
        <button class="submit-btn" type="submit">Request Callback</button>
        <p class="form-note">Free site visit & exclusive offers</p>
      </form>
    </div>
  </aside>
</div></div></section>
{FOOTER.replace('assets/','../assets/').replace('css/','../css/').replace('index.html','../index.html')}
{search_modal()}{enq_modal().replace('assets/','../assets/')}
{scripts(json.dumps([mini(p) for p in PROJECTS], ensure_ascii=False))}
</body></html>"""
    d = os.path.join(ROOT, "projects")
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, f"{slug_file(slug)}.html"), "w", encoding="utf-8").write(html_doc)

# ---------- build all ----------
def main():
    build_index()
    # core routes
    new = [p for p in PROJECTS if p.get("project_status")=="New Launch"]
    ready = [p for p in PROJECTS if p.get("project_status")=="Ready To Move"]
    comm = [p for p in PROJECTS if p.get("project_type")=="commercial"]
    under = [p for p in PROJECTS if p.get("project_status")=="Under Construction"]
    res = [p for p in PROJECTS if p.get("project_type")=="residential"]
    build_listing("residential-projects-gurgaon", "Residential Projects in Gurgaon", res, "Explore premium residential apartments on Dwarka Expressway, Gurgaon.")
    build_listing("commercial-projects-gurgaon", "Commercial Projects in Gurgaon", comm, "Best commercial & retail spaces on Dwarka Expressway.")
    build_listing("affordable-housing-projects", "Affordable Housing Projects", [p for p in PROJECTS if 'affordable' in (p.get('project_tag') or '').lower() or 'Affordable' in (p.get('configuration') or '')], "Upcoming affordable housing projects on Dwarka Expressway.")
    build_listing("sco-plots-gurgaon", "SCO Plots for Sale in Gurgaon", [p for p in PROJECTS if 'sco' in (p.get('project_type') or '').lower() or 'SCO' in (p.get('name') or '')], "Buy SCO plots on Dwarka Expressway, Gurgaon.")
    build_listing("upcoming-projects", "Upcoming Projects on Dwarka Expressway", under+new, "Upcoming & New Launch projects on Dwarka Expressway.")
    build_listing("ready-to-move-flats-in-dwarka-expressway-gurgaon", "Ready To Move Flats", ready, "Ready to move flats on Dwarka Expressway, Gurgaon.")
    build_listing("best-deals", "Best Projects on Dwarka Expressway", sorted(PROJECTS, key=lambda x:-(x.get('ratings') or 0))[:20], "Hand-picked best-rated projects on Dwarka Expressway.")
    build_listing("projects-list", "All Projects on Dwarka Expressway", PROJECTS, "Complete list of projects on Dwarka Expressway, Gurgaon.")
    build_listing("luxury-projects", "Luxury Projects", [p for p in PROJECTS if 'luxury' in (p.get('tagline') or '').lower() or 'Luxury' in (p.get('project_tag') or '')], "Luxury residences on Dwarka Expressway.")
    # contact + privacy
    build_contact()
    build_privacy()
    # landing pages from allUrls (skip ones already built as core routes)
    core = {"residential-projects-gurgaon","commercial-projects-gurgaon","affordable-housing-projects",
            "sco-plots-gurgaon","upcoming-projects","ready-to-move-flats-in-dwarka-expressway-gurgaon",
            "best-deals","contact","privacy-policy","dwarka-expressway-map","projects-list","luxury-projects",""}
    for slug in ALLURLS:
        if slug in core: continue
        build_landing(slug)
    # detail pages
    for p in PROJECTS:
        build_detail(p)
    print("Built index + category pages +", len(ALLURLS)-len(core), "landing pages +", len(PROJECTS), "detail pages")

def build_contact():
    html_doc = f"""<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Contact Us - Dwarka Expressway Projects</title>
<link rel="stylesheet" href="css/style.css"></head><body>
{header()}
<div class="breadcrumb"><div class="container"><a href="index.html">Home</a> / Contact</div></div>
<section class="section"><div class="container"><div class="detail-grid">
  <div>
    <h1 class="best_project_heading">Contact Us</h1>
    <p class="section-sub">Get in touch for the best deals, free site visits and expert advice on Dwarka Expressway properties.</p>
    <div class="detail-block"><h3>Office</h3><p>7C, Level Ground, Omaxe Gurgaon Mall, Sohna Road, Gurgaon</p>
    <p><a href="tel:{PHONE}" style="color:var(--primary-color);font-weight:700">{PHONE}</a></p></div>
  </div>
  <aside><div class="enquiry-card"><h3>Send Enquiry</h3>
    <form data-lead>
      <input type="hidden" name="project" value="Contact Page">
      <div class="form-field"><input name="name" placeholder="Your Name" required></div>
      <div class="form-field"><input name="email" type="email" placeholder="Email" required></div>
      <div class="form-field"><input name="phone" placeholder="Mobile Number" required></div>
      <div class="form-field"><textarea name="note" rows="3" placeholder="Message"></textarea></div>
      <button class="submit-btn" type="submit">Submit</button>
    </form></div></aside>
</div></div></section>
{FOOTER}{search_modal()}{enq_modal()}{scripts("[]")}
</body></html>"""
    open(os.path.join(ROOT,"contact.html"),"w",encoding="utf-8").write(html_doc)

def build_privacy():
    html_doc = f"""<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Dwarka Expressway Privacy Policy</title>
<link rel="stylesheet" href="css/style.css"></head><body>
{header()}
<div class="policy_main">
<h1>Dwarka Expressway Privacy Policy</h1>
<p>Dwarka Expressway Projects ("DEW") understands the need to protect the privacy of the personal information you provide to DEW with respect to your access and use of our Websites and Mobile Application (collectively, the "Platforms").</p>
<p>Therefore, we have adopted this privacy policy. This Privacy Policy governs how we collect and use your personal information wherever you use our Platforms. By using or accessing the Platforms, you hereby agree to the terms of this Privacy Policy, especially the terms with respect to collection, storage, processing and sharing of your personal information.</p>
<p>We collect information you provide voluntarily such as your name, email, phone number and property preferences when you submit an enquiry. This information is used solely to respond to your queries and share relevant property information.</p>
<p>We do not sell your personal information to third parties. We may share it with builders/developers solely for the purpose of addressing your enquiry. You may request deletion of your data at any time by contacting us.</p>
</div>
{FOOTER}{search_modal()}{enq_modal()}{scripts("[]")}
</body></html>"""
    open(os.path.join(ROOT,"privacy-policy.html"),"w",encoding="utf-8").write(html_doc)

def build_landing(slug):
    # pick projects related to this landing (builder / sector / type keyword)
    kw = re.sub(r'\.(php|html)$','',slug).lower()
    kw = kw.replace('-',' ')
    related = [p for p in PROJECTS if kw.split() and any(
        (w in (p.get('name') or '').lower()) or (w in (builder_name(p).lower())) or (w in (loc_addr(p).lower()))
        for w in kw.split() if len(w)>2)]
    # if none, show all
    if not related: related = PROJECTS[:12]
    seo = SEO.get(slug) or {}
    title = seo.get("title") or slug.replace('-',' ').replace('.php','').replace('.html','').title()
    title = re.sub(r'\bDwarka Expressway\b','Dwarka Expressway',title)
    desc = seo.get("footer_description") or f"Explore {title} on Dwarka Expressway, Gurgaon. Find RERA approved projects, prices, floor plans & amenities."
    cards = "".join(card(p) for p in related)
    html_doc = f"""<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc((seo.get('description') or desc)[:300])}">
<link rel="stylesheet" href="css/style.css"></head><body>
{header()}
<div class="breadcrumb"><div class="container"><a href="index.html">Home</a> / {esc(title)}</div></div>
<section class="section"><div class="container">
  <h1 class="best_project_heading">{esc(title)}</h1>
  <p class="section-sub">{esc(desc)}</p>
  <div class="listing-grid">{cards}</div>
</section>
<div class="container"><div class="seo-content">{seo_block(seo)}</div></div>
{FOOTER}{search_modal()}{enq_modal()}{scripts(json.dumps([mini(p) for p in PROJECTS], ensure_ascii=False))}
</body></html>"""
    open(os.path.join(ROOT, f"{slug}.html"), "w", encoding="utf-8").write(html_doc)

if __name__ == "__main__":
    main()
