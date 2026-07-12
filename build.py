#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the static Dwarka Expressway Projects site from scraped data."""
import json, os, html, re

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECTS = json.load(open(os.path.join(ROOT, "projects.json"), encoding="utf-8"))
SEO = json.load(open(os.path.join(ROOT, "seo.json"), encoding="utf-8"))
_raw = json.load(open(os.path.join(ROOT, "allurls.json"), encoding="utf-8"))
ALLURLS = [u["slug"].strip() for u in _raw.get("data", {}).get("allUrls", _raw if isinstance(_raw, list) else [])]

PHONE = "9015883288"
PHONE_FULL = "+919015883288"
WA_NUMBER = "919015883288"
LEAD_EMAIL = "sharma.manish53@gmail.com"
SITE = "https://www.dwarkaexpresswayprojects.in"  # original, for reference in footer

def slug_file(s):
    """Sanitize a project slug for use as a project detail filename (handles / & space)."""
    return s.replace("/", "-").replace("&", "and").replace(" ", "-").strip()

def page_file(slug):
    """Return the on-disk filename + link href for a site slug (handles .html/.php suffixes)."""
    s = slug.strip()
    s = re.sub(r'\.(html|php)$', '', s)
    return s + ".html"

def esc(s):
    return html.escape(str(s or ""), quote=True)

_ICON_MAP = [
    ("density", "fa-layer-group"), ("coverage", "fa-compress"), ("open area", "fa-tree"),
    ("forest", "fa-tree"), ("tower", "fa-building"), ("green", "fa-leaf"),
    ("amenit", "fa-star"), ("club", "fa-mug-hot"), ("pool", "fa-person-swimming"),
    ("security", "fa-shield-halved"), ("gym", "fa-dumbbell"), ("park", "fa-car"),
    ("location", "fa-location-dot"), ("connectivity", "fa-route"), ("luxury", "fa-gem"),
    ("view", "fa-binoculars"), ("spec", "fa-ruler-combined"), ("price", "fa-tag"),
]
def clean_rich(html_str):
    if not html_str:
        return ""
    # strip dead <img> icon tags (broken external icons / alt=undefined / empty dims)
    html_str = re.sub(r'<img\b[^>]*\bsrc="[^"]*(icons/|emoji\.php|fbcdn)[^"]*"[^>]*/?>', '', html_str, flags=re.I)
    html_str = re.sub(r'<img\b[^>]*\balt="undefined"[^>]*/?>', '', html_str, flags=re.I)
    # any remaining <img> with empty style dims -> drop (likely broken)
    html_str = re.sub(r'<img\b[^>]*style="[^"]*height:\s*;[^"]*"[^>]*/?>', '', html_str, flags=re.I)
    # add a FA icon before each <h4> highlight title
    def add_icon(m):
        title = m.group(2).lower()
        icon = "fa-circle-check"
        for key, ic in _ICON_MAP:
            if key in title:
                icon = ic; break
        return f'<div class="hl-item"><i class="fas {icon}"></i>{m.group(1)}{m.group(2)}</div>'
    html_str = re.sub(r'(<h4>)([^<]+)(</h4>)', add_icon, html_str)
    return html_str

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
MEGA = f"""
<nav class="main-nav">
  <li class="has-mega">
    <a href="residential-projects-gurgaon.html">Buy</a>
    <div class="mega"><div class="container"><div class="mega-grid">
      <div class="mega-col">
        <h5><i class="fas fa-home"></i> By Property Type</h5>
        <ul>
          <li><a href="2bhk-apartment-on-dwarka-expressway.html"><i class="fas fa-building"></i> 2 BHK Apartments</a></li>
          <li><a href="3bhk-apartment-on-dwarka-expressway.html"><i class="fas fa-building"></i> 3 BHK Apartments</a></li>
          <li><a href="4bhk-apartment-on-dwarka-expressway.html"><i class="fas fa-building"></i> 4 BHK Apartments</a></li>
          <li><a href="luxury-projects.html"><i class="fas fa-home"></i> Luxury Villas</a></li>
          <li><a href="residential-projects-gurgaon.html"><i class="fas fa-warehouse"></i> Penthouse</a></li>
          <li><a href="commercial-projects-gurgaon.html"><i class="fas fa-store"></i> Commercial Spaces</a></li>
          <li><a href="residential-projects-gurgaon.html"><i class="fas fa-couch"></i> Studio Apartments</a></li>
          <li><a href="residential-projects-gurgaon.html"><i class="fas fa-house-damage"></i> Duplex / Triplex</a></li>
        </ul>
      </div>
      <div class="mega-col">
        <h5><i class="fas fa-wallet"></i> By Budget</h5>
        <ul>
          <li><a href="projects-list.html"><span class="budget-ico">&lt;50</span> Under 50 Lakhs</a></li>
          <li><a href="projects-list.html"><span class="budget-ico">50</span> 50 Lakhs - 75 Lakhs</a></li>
          <li><a href="property-1cr-1.5cr-on-dwarka-expressway.html"><span class="budget-ico">75</span> 75 Lakhs - 1 Crore</a></li>
          <li><a href="property-1cr-1.5cr-on-dwarka-expressway.html"><span class="budget-ico">1</span> 1 Cr - 1.5 Cr</a></li>
          <li><a href="property-2cr-3cr-on-dwarka-expressway.html"><span class="budget-ico">1.5</span> 1.5 Cr - 2 Cr</a></li>
          <li><a href="property-2cr-3cr-on-dwarka-expressway.html"><span class="budget-ico">2</span> 2 Cr - 3 Cr</a></li>
          <li><a href="property-2cr-3cr-on-dwarka-expressway.html"><span class="budget-ico">3+</span> Above 3 Crores</a></li>
        </ul>
      </div>
      <div class="mega-col">
        <h5><i class="fas fa-key"></i> By Possession</h5>
        <ul>
          <li><a href="ready-to-move-flats-in-dwarka-expressway-gurgaon.html"><i class="fas fa-check-circle"></i> Ready to Move</a></li>
          <li><a href="upcoming-projects.html"><i class="fas fa-crane"></i> Under Construction</a></li>
          <li><a href="upcoming-projects.html"><i class="fas fa-rocket"></i> New Launch</a></li>
          <li><a href="ready-to-move-flats-in-dwarka-expressway-gurgaon.html"><i class="fas fa-file-alt"></i> OC Received</a></li>
          <li><a href="upcoming-projects.html"><i class="fas fa-calendar"></i> Near Possession (6 mo)</a></li>
          <li><a href="upcoming-projects.html"><i class="fas fa-calendar"></i> Near Possession (1 yr)</a></li>
        </ul>
      </div>
      <div class="mega-col">
        <h5><i class="fas fa-star"></i> By Amenities</h5>
        <ul>
          <li><a href="residential-projects-gurgaon.html"><i class="fas fa-swimmer"></i> Swimming Pool</a></li>
          <li><a href="residential-projects-gurgaon.html"><i class="fas fa-dumbbell"></i> Gym / Fitness</a></li>
          <li><a href="residential-projects-gurgaon.html"><i class="fas fa-building"></i> Club House</a></li>
          <li><a href="residential-projects-gurgaon.html"><i class="fas fa-child"></i> Kids Play Area</a></li>
          <li><a href="residential-projects-gurgaon.html"><i class="fas fa-running"></i> Jogging Track</a></li>
          <li><a href="residential-projects-gurgaon.html"><i class="fas fa-shield-alt"></i> 24/7 Security</a></li>
          <li><a href="residential-projects-gurgaon.html"><i class="fas fa-bolt"></i> Power Backup</a></li>
          <li><a href="residential-projects-gurgaon.html"><i class="fas fa-car"></i> Covered Parking</a></li>
        </ul>
      </div>
      <div class="mega-col">
        <h5><i class="fas fa-award"></i> Featured Properties</h5>
        __FEATURED__
      </div>
    </div></div></div>
  </li>
  <li class="has-mega">
    <a href="projects-list.html">Sectors</a>
    <div class="mega"><div class="container"><div class="mega-grid">
      <div class="mega-col">
        <h5><i class="fas fa-map-marker-alt"></i> Sectors 81-90</h5>
        <ul>__SEC_A__</ul>
      </div>
      <div class="mega-col">
        <h5><i class="fas fa-map-marker-alt"></i> Sectors 91-100</h5>
        <ul>__SEC_B__</ul>
      </div>
      <div class="mega-col">
        <h5><i class="fas fa-map-marker-alt"></i> Sectors 101-110</h5>
        <ul>__SEC_C__</ul>
      </div>
      <div class="mega-col">
        <h5><i class="fas fa-map-marker-alt"></i> Sectors 111-115</h5>
        <ul>__SEC_D__</ul>
      </div>
      <div class="mega-col">
        <h5><i class="fas fa-road"></i> Corridors</h5>
        <ul>
          <li><a href="projects-list.html"><i class="fas fa-road"></i> New Gurgaon</a></li>
          <li><a href="projects-list.html"><i class="fas fa-road"></i> SPR Road</a></li>
          <li><a href="projects-list.html"><i class="fas fa-road"></i> NH-8 Corridor</a></li>
        </ul>
      </div>
    </div></div></div>
  </li>
  <li class="has-mega">
    <a href="godrej-properties.html">Developers</a>
    <div class="mega"><div class="container"><div class="mega-grid">
      <div class="mega-col"><h5><i class="fas fa-building"></i> Top Developers</h5><ul>__DEV_A__</ul></div>
      <div class="mega-col"><h5><i class="fas fa-building"></i> More Developers</h5><ul>__DEV_B__</ul></div>
      <div class="mega-col"><h5><i class="fas fa-building"></i> Premium</h5><ul>__DEV_C__</ul></div>
      <div class="mega-col"><h5><i class="fas fa-building"></i> Others</h5><ul>__DEV_D__</ul></div>
      <div class="mega-col"><h5><i class="fas fa-award"></i> Featured Properties</h5>__FEATURED__</div>
    </div></div></div>
  </li>
  <li><a href="best-deals.html">Resources</a></li>
  <li><a href="contact.html">About</a></li>
  <li><a href="contact.html">Contact</a></li>
</nav>"""

POPULAR = ["DLF Projects","New Launch Projects","Ready to Move Flats","Under Construction Projects","Luxury Apartments","Golf Course Road Ext.","Sectors 102-113"]
POPULAR_LINKS = ["dlf-properties","residential-projects-gurgaon","ready-to-move-flats-in-dwarka-expressway-gurgaon","upcoming-projects","luxury-projects","projects-list","projects-list"]

def prefix_rel(html, depth):
    """Prefix internal relative hrefs/src with '../' * depth for subpages (projects/)."""
    if depth == 0:
        return html
    pref = '../' * depth
    import re as _re
    def fix(m):
        tag, quote, url = m.group(1), m.group(2), m.group(3)
        if url.startswith(('http', 'tel:', 'mailto:', 'data:', '//', '#')):
            return m.group(0)
        if url.startswith(pref):
            return m.group(0)
        return f'{tag}={quote}{pref}{url}'
    return _re.sub(r'(href|src)=("|\')([^"\']+)', fix, html)


def build_mega():
    """Fill the MEGA placeholder blocks with real data."""
    global MEGA
    # Featured properties (first 3 with images)
    feat = []
    for p in PROJECTS:
        im = first_img(p)
        if im != "assets/logo.png" and p.get("starting_price"):
            feat.append(p)
        if len(feat) >= 3: break
    feat_html = ""
    for p in feat:
        feat_html += (f'<a class="feat-card" href="projects/{esc(slug_file(p["slug"]))}.html">'
                      f'<img src="{first_img(p)}" alt="{esc(p["name"])}" loading="lazy">'
                      f'<div><div class="fc-name">{esc(p["name"])}</div>'
                      f'<div class="fc-meta">{esc(p.get("configuration") or "")} &middot; {esc(p.get("starting_price") or "")}</div>'
                      f'<div class="fc-link">View Details &rarr;</div></div></a>')
    # Sectors grouped — extract real sector number from slug
    import re as _re
    _sec=[]
    _seen=set()
    for s in ALLURLS:
        m=_re.search(r'projects-in-sector-([\d]+(?:\.[\da-z]+)?)-gurgaon\.html', s)
        if m:
            num=m.group(1)
            if num not in _seen:
                _seen.add(num); _sec.append((num, s))
    def sec_col(lo, hi):
        out=[]
        for num, sl in _sec:
            try: n=float(_re.sub(r'[a-z]','',num))
            except: n=0
            if lo<=n<=hi:
                out.append(f'<li><a href="{page_file(sl)}"><i class="fas fa-map-pin"></i> Sector {esc(num.upper())}</a></li>')
        return "".join(out[:8])
    sec_a = sec_col(81,90)
    sec_b = sec_col(91,100)
    sec_c = sec_col(101,110)
    sec_d = sec_col(111,115)
    # Developers from landing pages
    dev_map = {
        "dlf-properties.html":"DLF","vatika-properties.html":"Vatika","signature-global-gurgaon.html":"Signature Global",
        "godrej-properties.html":"Godrej","tata-projects-on-dwarka-expressway.html":"Tata Housing","sobhadevelopers.html":"Sobha",
        "ats-projects-in-gurgaon.html":"ATS","m3m-projects-gurgaon.html":"M3M","emaar-properties.html":"Emaar",
        "adani.php":"Adani","bestech-projects-on-dwarka-expressway.html":"Bestech","experion-developers.php":"Experion",
        "ansalhousing.php":"Ansal Housing","puriconstructions.php":"Puri","alphagcorp":"Alpha G Corp","ssgroup.html":"SS Group",
        "microtekinfra.html":"Microtek","assotech.html":"Assotech","landmark.html":"Landmark","vatika-properties.html":"Vatika"
    }
    dev_items = list(dev_map.items())
    dev_a = "".join(f'<li><a href="{page_file(s)}"><i class="fas fa-building"></i> {n}</a></li>' for s,n in dev_items[:5])
    dev_b = "".join(f'<li><a href="{page_file(s)}"><i class="fas fa-building"></i> {n}</a></li>' for s,n in dev_items[5:10])
    dev_c = "".join(f'<li><a href="{page_file(s)}"><i class="fas fa-building"></i> {n}</a></li>' for s,n in dev_items[10:13])
    dev_d = "".join(f'<li><a href="{page_file(s)}"><i class="fas fa-building"></i> {n}</a></li>' for s,n in dev_items[13:])
    MEGA = (MEGA
        .replace("__FEATURED__", feat_html)
        .replace("__SEC_A__", sec_a).replace("__SEC_B__", sec_b)
        .replace("__SEC_C__", sec_c).replace("__SEC_D__", sec_d)
        .replace("__DEV_A__", dev_a).replace("__DEV_B__", dev_b)
        .replace("__DEV_C__", dev_c).replace("__DEV_D__", dev_d))

def header_d(depth=0):
    return prefix_rel(header(), depth)

def header(active=""):
    build_mega()
    return f"""<header class="site-header">
  <div class="header-bar">
    <div class="container">
      <span>Your trusted partner for premium homes on Dwarka Expressway, Gurgaon</span>
      <div class="hb-right">
        <a href="tel:{PHONE_FULL}"><i class="fas fa-phone"></i> {PHONE_FULL}</a>
        <a href="contact.html">RERA Approved</a>
        <a href="contact.html">Free Site Visit</a>
      </div>
    </div>
  </div>
  <div class="container header-inner">
    <a href="index.html" class="brand"><img src="assets/logo.png" alt="Dwarka Expressway Projects logo"></a>
    {MEGA}
    <div class="header-cta">
      <a class="phone-btn" href="tel:{PHONE_FULL}"><i class="fas fa-phone"></i> {PHONE_FULL}</a>
      <button class="consult-btn" data-enquire="">Get Free Consultation</button>
      <button class="menu-toggle" aria-label="menu">&#9776;</button>
    </div>
  </div>
  <div class="popular-strip"><div class="container">
    <span class="ps-label"><i class="fas fa-search"></i> Popular Searches:</span>
    {"".join(f'<a href="{l}.html">{t}</a><span class="sep">|</span>' for t,l in zip(POPULAR,POPULAR_LINKS))}
  </div></div>
</header>"""

FOOTER = f"""<footer class="site-footer">
  <div class="footer-news">
    <div class="container">
      <div class="fn-left">
        <i class="fas fa-envelope-open-text"></i>
        <div><h4>Stay Updated with Latest Projects</h4><p>Subscribe to our newsletter and get the latest property updates, offers &amp; market insights.</p></div>
      </div>
      <form data-newsletter>
        <input type="email" name="email" placeholder="Enter your email address" required>
        <button type="submit">Subscribe</button>
      </form>
    </div>
  </div>
  <div class="container footer-grid">
    <div>
      <img class="footer-logo" src="assets/logo.png" alt="Dwarka Expressway Projects">
      <p>Your trusted partner for premium residential &amp; commercial properties along Dwarka Expressway, Gurgaon.</p>
      <p><i class="fas fa-phone"></i> <a href="tel:{PHONE_FULL}" style="color:#fff;font-weight:700">{PHONE_FULL}</a></p>
      <p><i class="fas fa-envelope"></i> info@dwarkaexpresswayprojects.com</p>
      <p><i class="fas fa-map-marker-alt"></i> Sector 88, Gurgaon, Haryana</p>
      <div class="footer-social">
        <a href="#" aria-label="facebook"><i class="fab fa-facebook-f"></i></a>
        <a href="#" aria-label="instagram"><i class="fab fa-instagram"></i></a>
        <a href="#" aria-label="linkedin"><i class="fab fa-linkedin-in"></i></a>
        <a href="#" aria-label="twitter"><i class="fab fa-twitter"></i></a>
        <a href="#" aria-label="youtube"><i class="fab fa-youtube"></i></a>
      </div>
      <a class="footer-wa" href="https://wa.me/{WA_NUMBER}" target="_blank"><i class="fab fa-whatsapp"></i> Chat on WhatsApp</a>
    </div>
    <div><h5>Properties</h5>
      <a href="{page_file('2bhk-apartment-on-dwarka-expressway.html')}">2 BHK Apartments</a>
      <a href="{page_file('3bhk-apartment-on-dwarka-expressway.html')}">3 BHK Apartments</a>
      <a href="{page_file('4bhk-apartment-on-dwarka-expressway.html')}">4 BHK Apartments</a>
      <a href="luxury-projects.html">Luxury Villas</a>
      <a href="commercial-projects-gurgaon.html">Commercial Spaces</a>
      <a href="ready-to-move-flats-in-dwarka-expressway-gurgaon.html">Ready to Move</a>
      <a href="upcoming-projects.html">Under Construction</a>
    </div>
    <div><h5>Sectors</h5>
      <a href="{page_file('projects-in-sector-81-gurgaon.html')}">Sector 81-90</a>
      <a href="{page_file('projects-in-sector-91-gurgaon.html')}">Sector 91-100</a>
      <a href="{page_file('projects-in-sector-102-gurgaon.html')}">Sector 101-110</a>
      <a href="{page_file('projects-in-sector-111-gurgaon.html')}">Sector 111-115</a>
      <a href="projects-list.html">New Gurgaon</a>
      <a href="projects-list.html">SPR Road</a>
      <a href="projects-list.html">NH-8 Corridor</a>
    </div>
    <div><h5>Developers</h5>
      <a href="dlf-properties.html">DLF</a>
      <a href="vatika-properties.html">Vatika</a>
      <a href="signature-global-gurgaon.html">Signature Global</a>
      <a href="godrej-properties.html">Godrej Properties</a>
      <a href="tata-projects-on-dwarka-expressway.html">Tata Housing</a>
      <a href="sobhadevelopers.html">Sobha</a>
      <a href="ats-projects-in-gurgaon.html">ATS</a>
      <a href="m3m-projects-gurgaon.html">M3M</a>
      <a href="emaar-properties.html">Emaar</a>
      <a href="best-deals.html">Ambience</a>
    </div>
    <div><h5>Resources</h5>
      <a href="contact.html">About Us</a>
      <a href="best-deals.html">Blog</a>
      <a href="best-deals.html">Property Guides</a>
      <a href="best-deals.html">Investment Tips</a>
      <a href="best-deals.html">Market Reports</a>
      <a href="best-deals.html">FAQs</a>
      <a href="contact.html">Contact Us</a>
      <a href="contact.html">Careers</a>
    </div>
    <div><h5>Connect With Us</h5>
      <form data-newsletter style="display:flex;gap:6px;margin-bottom:12px">
        <input type="email" name="email" placeholder="Enter your email" required style="padding:9px 12px;border:none;border-radius:8px;width:100%;font-size:13px">
        <button type="submit" style="background:var(--accent);color:#0d3a30;border:none;padding:9px 14px;border-radius:8px;font-weight:700;cursor:pointer">Go</button>
      </form>
      <p style="color:#bfd9cf;font-size:13px"><i class="fas fa-hashtag"></i> Follow Us</p>
      <div class="footer-social">
        <a href="#" aria-label="facebook"><i class="fab fa-facebook-f"></i></a>
        <a href="#" aria-label="instagram"><i class="fab fa-instagram"></i></a>
        <a href="#" aria-label="linkedin"><i class="fab fa-linkedin-in"></i></a>
        <a href="#" aria-label="twitter"><i class="fab fa-twitter"></i></a>
        <a href="#" aria-label="youtube"><i class="fab fa-youtube"></i></a>
      </div>
      <a class="footer-wa" href="https://wa.me/{WA_NUMBER}" target="_blank"><i class="fab fa-whatsapp"></i> Chat on WhatsApp</a>
    </div>
  </div>
  <div class="trust-bar"><div class="container">
    <div class="trust-item"><i class="fas fa-shield-alt"></i><div><b>RERA Registered</b><span>All projects are RERA registered for your peace of mind</span></div></div>
    <div class="trust-item"><i class="fas fa-certificate"></i><div><b>Verified Properties</b><span>100% verified properties with clean documentation</span></div></div>
    <div class="trust-item"><i class="fas fa-award"></i><div><b>10+ Years Experience</b><span>A decade of trust, transparency &amp; satisfaction</span></div></div>
  </div></div>
  <div class="footer-bottom"><div class="container">
    <span>&copy; 2025 Dwarka Expressway Projects. All Rights Reserved.</span>
    <span class="fb-links"><a href="privacy-policy.html">Privacy Policy</a> | <a href="privacy-policy.html">Terms</a> | <a href="privacy-policy.html">Disclaimer</a> | <a href="projects-list.html">Sitemap</a></span>
    <span class="footer-social">
      <a href="#"><i class="fab fa-facebook-f"></i></a>
      <a href="#"><i class="fab fa-instagram"></i></a>
      <a href="#"><i class="fab fa-linkedin-in"></i></a>
    </span>
  </div></div>
</footer>"""

def scripts(projects_js="[]"):
    # root-absolute paths so JS/CSS resolve correctly from any subpage depth
    return f"""<script>window.__PROJECTS__={projects_js};</script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css">
<script src="/js/site.js"></script>"""

def phone_field(name="phone", required=True):
    return f"""<div class="phone-field">
      <span class="flag" id="ccFlag"><img src="https://flagcdn.com/24x18/in.png" alt="flag" id="ccFlagImg"> <span id="ccCode">+91</span></span>
      <input name="{name}" id="phoneInput" inputmode="numeric" placeholder="Mobile Number" {'required' if required else ''} autocomplete="tel-national">
    </div>"""

def search_modal():
    return """<div class="search-modal" id="searchModal">
  <div class="box">
    <input id="searchBox" placeholder="Search by Project Name...">
    <div class="search-results" id="searchResults"></div>
    <div style="text-align:right;margin-top:10px"><button class="consult-btn" data-close="search">Close</button></div>
  </div>
</div>"""

def enq_modal():
    return f"""<div class="modal-overlay" id="enqModal">
  <div class="modal">
    <button class="modal-close" data-close="enq">&times;</button>
    <h3 id="enqTitle">Enquire Now</h3>
    <form data-lead>
      <input type="hidden" id="enqProject" name="project">
      <div class="form-field"><input name="name" placeholder="Your Name" required></div>
      <div class="form-field"><input name="email" type="email" placeholder="Email" required></div>
      <div class="form-field">{phone_field()}</div>
      <div class="form-field"><textarea name="note" rows="3" placeholder="Message (optional)"></textarea></div>
      <button class="submit-btn" type="submit">Submit Enquiry</button>
      <p class="form-note">We respect your privacy. Your details are safe with us.</p>
    </form>
  </div>
</div>
<div class="lightbox" id="lightbox"><span class="lb-close" onclick="closeLightbox()">&times;</span><img id="lbImg" src="" alt=""></div>
<button class="wa-float" href="https://wa.me/{WA_NUMBER}" target="_blank" aria-label="WhatsApp"><i class="fab fa-whatsapp" style="font-size:30px;color:#fff"></i></a>"""

def FOOTER_d(depth=1):
    return prefix_rel(FOOTER, depth)

def enq_modal_d(depth=1):
    return prefix_rel(enq_modal(), depth)

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
    highlights = clean_rich(p.get("highlights") or "")
    advantages = clean_rich(p.get("advantages") or "")
    features = clean_rich(p.get("features") or "")
    # map
    lat = (p.get("location") or {}).get("latitude")
    lng = (p.get("location") or {}).get("longitude")
    map_html = ""
    if lat and lng:
        map_html = f"""<div id="map" data-lat="{lat}" data-lng="{lng}"></div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script>setTimeout(()=>{{try{{var m=L.map('map').setView([{lat},{lng}],14);L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}@2x.png').addTo(m);L.marker([{lat},{lng}]).addTo(m).bindPopup('{esc(p['name'])}');}}catch(e){{}}}},300);</script>"""
    # brochure / master plan (capture lead BEFORE download)
    mp = (p.get("master_plan") or {}).get("s3_link")
    brochure = (p.get("brochure") or {}).get("s3_link")
    downloads = ""
    if mp: downloads += f'<button class="download-btn lead-gate" data-url="{esc(mp)}" data-label="Master Plan" data-enquire="{esc(p["name"])}">Download Master Plan</button> '
    if brochure: downloads += f'<button class="download-btn lead-gate" data-url="{esc(brochure)}" data-label="Brochure" data-enquire="{esc(p["name"])}">Download Brochure</button>'

    html_doc = f"""<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc((p.get('seo') or {}).get('title') or f"{p['name']} | Price, Floor Plan & Brochure")}</title>
<meta name="description" content="{esc(((p.get('seo') or {}).get('description') or desc or p['name'])[:300])}">
<link rel="stylesheet" href="../css/style.css">
</head><body>
{header_d(1)}
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
      <span class="ec-badge"><i class="fas fa-clock"></i> Quick Response</span>
      <h3>Get Best Price &amp; Site Visit</h3>
      <p class="ec-sub">Fill the form, our expert will call you with exclusive offers.</p>
      <form data-lead>
        <input type="hidden" name="project" value="{esc(p['name'])}">
        <div class="form-field"><input name="name" placeholder="Your Name" required></div>
        <div class="form-field"><input name="email" type="email" placeholder="Email" required></div>
        <div class="form-field">{phone_field()}</div>
        <div class="form-field"><textarea name="note" rows="3" placeholder="Message (optional)"></textarea></div>
        <button class="submit-btn" type="submit">Request Callback</button>
        <p class="form-note">Free site visit &amp; exclusive offers &middot; <a href="https://wa.me/{WA_NUMBER}" target="_blank" style="color:var(--primary-color);font-weight:700"><i class="fab fa-whatsapp"></i> WhatsApp</a></p>
      </form>
    </div>
  </aside>
</div></div></section>
{FOOTER_d(1)}
{search_modal()}{enq_modal_d(1)}
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
    build_listing("buy-plots", "Buy Plots on Dwarka Expressway", [p for p in PROJECTS if 'plot' in (p.get('project_type') or '').lower() or 'Plot' in (p.get('name') or '')], "Residential & SCO plots on Dwarka Expressway, Gurgaon.")
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
    # Guarantee every slug referenced by the mega menu / footer exists as a page
    guaranteed = [
        "2bhk-apartment-on-dwarka-expressway.html","3bhk-apartment-on-dwarka-expressway.html",
        "4bhk-apartment-on-dwarka-expressway.html","5bhk-apartment-on-dwarka-expressway.html",
        "property-1cr-1.5cr-on-dwarka-expressway.html","property-2cr-3cr-on-dwarka-expressway.html",
        "vatika-properties.html","dlf-properties.html","signature-global-gurgaon.html","godrej-properties.html",
        "tata-projects-on-dwarka-expressway.html","sobhadevelopers.html","ats-projects-in-gurgaon.html",
        "m3m-projects-gurgaon.html","emaar-properties.html","adani.php","bestech-projects-on-dwarka-expressway.html",
        "experion-developers.php","ansalhousing.php","puriconstructions.php","alphagcorp","ssgroup.html",
        "microtekinfra.html","assotech.html","landmark.html",
        "projects-in-sector-81-gurgaon.html","projects-in-sector-91-gurgaon.html",
        "projects-in-sector-102-gurgaon.html","projects-in-sector-111-gurgaon.html",
    ]
    for slug in guaranteed:
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
    <p><a href="tel:{PHONE_FULL}" style="color:var(--primary-color);font-weight:700">{PHONE_FULL}</a> &middot; <a href="https://wa.me/{WA_NUMBER}" target="_blank" style="color:var(--primary-color);font-weight:700"><i class="fab fa-whatsapp"></i> WhatsApp</a></p></div>
  </div>
  <aside><div class="enquiry-card"><h3>Send Enquiry</h3>
    <form data-lead>
      <input type="hidden" name="project" value="Contact Page">
      <div class="form-field"><input name="name" placeholder="Your Name" required></div>
      <div class="form-field"><input name="email" type="email" placeholder="Email" required></div>
      <div class="form-field">{phone_field()}</div>
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
    open(os.path.join(ROOT, page_file(slug)), "w", encoding="utf-8").write(html_doc)

if __name__ == "__main__":
    main()
