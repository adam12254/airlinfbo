#!/usr/bin/env python3
"""
Airlin FBO — static site generator.

Renders the seven pages from one layout so the header, footer and floating
actions exist in a single place. Run `python3 build.py` after any edit.

Copy is carried over from the WordPress site verbatim, except for the
character-level corruptions listed in TYPO_FIXES below — every one of those is
recorded so the change is reviewable rather than silent.
"""

import io
import os
import re
import sys

OUT = os.path.dirname(os.path.abspath(__file__))

# --------------------------------------------------------------------------
# Corrections applied to the original copy. Nothing here changes meaning,
# tone, or anybody's name — only demonstrable spelling and spacing faults.
# --------------------------------------------------------------------------
TYPO_FIXES = [
    ("tocrew facilities",        "to crew facilities"),
    ("end-to aviation",          "end-to-end aviation"),
    ("exeptional",               "exceptional"),
    ("perfetecd",                "perfected"),
    ("securty",                  "security"),
    ("Ground Handing",           "Ground Handling"),
    ("Our Facillities",          "Our Facilities"),
    ("environment here you can", "environment where you can"),
    ("Weather Birefing",         "Weather Briefing"),
    ("aviation.If",              "aviation. If"),
    ("skills.From",              "skills. From"),
    ("scenes.We",                "scenes. We"),
    ("industry.Fields:",         "industry. Fields:"),
    ("grow.The",                 "grow. The"),
    # The founder's name appeared both ways in the source copy. Confirmed by
    # the owner as Anzari.
    ("Mishal Ansari",            "Mishal Anzari"),
]

SITE = {
    "name":      "Airlin FBO",
    "legal":     "Airlin FBO FZ LLC",
    "tel_href":  "tel:+971585880827",
    "tel_label": "+971 58 588 0827",
    "whatsapp":  "https://wa.me/971585880827",
    "instagram": "https://www.instagram.com/airlinfbo/",
    "email":     "sales@airlinexecutive.com",
    "careers":   "careers@airlinfbo.com",
    "map":       ("https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3612.7062671384087"
                  "!2d56.33328609999999!3d25.111802599999994!2m3!1f0!2f0!3f0!3m2!1i1024!2i768"
                  "!4f13.1!3m3!1m2!1s0x8167a0c30c3e8d9d%3A0x2ea62aa050ef6710!2sAirlin%20FBO"
                  "!5e0!3m2!1sen!2slk!4v1778066244911!5m2!1sen!2slk"),
}

NAV = [
    ("index.html",           "Home"),
    ("collaborations.html",  "Collaborations"),
    ("facilities.html",      "Facilities"),
    ("why-airlin-fbo.html",  "Why Airlin FBO"),
    ("about.html",           "About Us"),
    ("careers.html",         "Careers"),
    ("contact.html",         "Contact"),
]

ICON = {
    "phone": '<path d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.2.4 2.4.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1A17 17 0 0 1 3 4c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.3 0 .7-.2 1l-2.3 2.2z"/>',
    "wa":    '<path d="M12 2a10 10 0 0 0-8.6 15L2 22l5.1-1.3A10 10 0 1 0 12 2zm5.8 14.2c-.2.7-1.4 1.3-2 1.4-.5.1-1.1.1-1.8-.1-.4-.1-1-.3-1.7-.6-3-1.3-4.9-4.3-5-4.5-.2-.2-1.2-1.6-1.2-3s.7-2.1 1-2.4c.2-.3.5-.4.7-.4h.5c.2 0 .4 0 .6.5l.8 2c.1.2.1.4 0 .5l-.3.5-.4.4c-.1.1-.3.3-.1.6.2.3.8 1.3 1.7 2.1 1.2 1 2.1 1.4 2.4 1.5.3.1.5.1.6-.1l.9-1c.2-.2.3-.2.6-.1l2 .9c.3.1.5.2.5.4v1z"/>',
    "ig":    '<path d="M12 2.2c3.2 0 3.6 0 4.9.1 1.2.1 1.8.2 2.2.4.6.2 1 .5 1.4 1 .5.4.8.8 1 1.4.2.4.3 1 .4 2.2.1 1.3.1 1.7.1 4.9s0 3.6-.1 4.9c-.1 1.2-.2 1.8-.4 2.2-.2.6-.5 1-1 1.4-.4.5-.8.8-1.4 1-.4.2-1 .3-2.2.4-1.3.1-1.7.1-4.9.1s-3.6 0-4.9-.1c-1.2-.1-1.8-.2-2.2-.4-.6-.2-1-.5-1.4-1-.5-.4-.8-.8-1-1.4-.2-.4-.3-1-.4-2.2-.1-1.3-.1-1.7-.1-4.9s0-3.6.1-4.9c.1-1.2.2-1.8.4-2.2.2-.6.5-1 1-1.4.4-.5.8-.8 1.4-1 .4-.2 1-.3 2.2-.4 1.3-.1 1.7-.1 4.9-.1zm0 3.3a6.5 6.5 0 1 0 0 13 6.5 6.5 0 0 0 0-13zm0 10.7a4.2 4.2 0 1 1 0-8.4 4.2 4.2 0 0 1 0 8.4zm6.8-11a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0z"/>',
    "menu":  '<path d="M3 6h18v2H3V6zm0 5h18v2H3v-2zm0 5h18v2H3v-2z"/>',
    "mail":  '<path d="M20 4H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2zm0 4.2-8 5-8-5V6l8 5 8-5v2.2z"/>',
    "pin":   '<path d="M12 2a7 7 0 0 0-7 7c0 5.2 7 13 7 13s7-7.8 7-13a7 7 0 0 0-7-7zm0 9.5A2.5 2.5 0 1 1 12 6a2.5 2.5 0 0 1 0 5.5z"/>',
    # The outer disc and the ring cutout must wind in opposite directions or the
    # whole face fills in and the icon renders as a solid dot.
    "clock": '<path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/>',
}


def svg(name, cls=""):
    c = ' class="%s"' % cls if cls else ""
    return '<svg%s viewBox="0 0 24 24" aria-hidden="true" focusable="false">%s</svg>' % (c, ICON[name])


def fix(text):
    for bad, good in TYPO_FIXES:
        text = text.replace(bad, good)
    return text


def header(active):
    links = []
    for href, label in NAV:
        cur = ' aria-current="page"' if href == active else ""
        links.append('<a href="%s"%s>%s</a>' % (href, cur, label))
    return """<header class="site-header">
  <div class="wrap site-header__inner">
    <a class="site-header__logo" href="index.html" aria-label="Airlin FBO — home">
      <img src="assets/img/fbo-relogo2.png" alt="Airlin FBO" width="150" height="28">
    </a>
    <nav class="nav" id="primary-nav" aria-label="Primary">
      %s
    </nav>
    <div class="header-cta">
      <a class="btn btn--call" href="%s">%s<span class="btn__label">%s</span></a>
    </div>
    <button class="nav-toggle" type="button" aria-expanded="false"
            aria-controls="primary-nav" aria-label="Open menu">%s</button>
  </div>
</header>""" % ("\n      ".join(links), SITE["tel_href"], svg("phone"), SITE["tel_label"], svg("menu"))


def footer():
    col = lambda title, items: (
        '<div><h2>%s</h2><ul class="footer-links">%s</ul></div>'
        % (title, "".join('<li><a href="%s">%s</a></li>' % (h, t) for h, t in items))
    )
    return """<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div class="footer-brand">
        <img src="assets/img/fbo-relogo2.png" alt="Airlin FBO" width="160" height="30">
        <p>End-to-end aviation support at Fujairah International Airport — permits, ground
           handling, fuel and VIP services, delivered with speed and precision.</p>
        <div class="socials">
          <a href="%s" aria-label="Airlin FBO on Instagram">%s</a>
          <a href="%s" aria-label="Airlin FBO on WhatsApp">%s</a>
          <a href="%s" aria-label="Call Airlin FBO">%s</a>
        </div>
      </div>
      %s
      %s
      %s
    </div>
    <div class="footer-bottom">
      <p>&copy; %s %s. All rights reserved.</p>
      <nav aria-label="Footer">
        <a href="contact.html">Contact</a>
        <a href="careers.html">Careers</a>
      </nav>
    </div>
  </div>
</footer>""" % (
        SITE["instagram"], svg("ig"), SITE["whatsapp"], svg("wa"), SITE["tel_href"], svg("phone"),
        col("Quick Links", [("index.html", "Home"), ("collaborations.html", "Collaborations"),
                            ("facilities.html", "Facilities"), ("why-airlin-fbo.html", "Why Airlin FBO")]),
        col("Company", [("about.html", "About Us"), ("contact.html", "Contact"),
                        ("careers.html", "Careers")]),
        col("Resources", [(SITE["tel_href"], "Flight Planning"), (SITE["tel_href"], "Weather Briefing"),
                          (SITE["tel_href"], "Regulations"), (SITE["tel_href"], "Documentation")]),
        2026, SITE["legal"])


def fabs():
    return """<div class="fab-stack">
  <a class="fab" href="%s" aria-label="Message Airlin FBO on WhatsApp">%s</a>
  <a class="fab" href="%s" aria-label="Call Airlin FBO">%s</a>
</div>""" % (SITE["whatsapp"], svg("wa"), SITE["tel_href"], svg("phone"))


def layout(page, title, desc, body):
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title>
<meta name="description" content="%s">
<link rel="icon" href="assets/img/fbo-relogo2.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Josefin+Sans:wght@200;300;400;600&family=Urbanist:wght@300;400;500;600&display=swap">
<link rel="stylesheet" href="assets/css/site.css">
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
%s
<main id="main">
%s
</main>
%s
%s
<script src="assets/js/site.js" defer></script>
</body>
</html>
""" % (title, desc, header(page), body, footer(), fabs())


# --------------------------------------------------------------------------
# Reusable blocks
# --------------------------------------------------------------------------

def page_hero(title, sub, image, kicker="Airlin FBO"):
    """Every inner page carries its own photograph. alt is empty on purpose:
    these are atmospheric backdrops behind an <h1> that already names the page,
    so describing them would only add a redundant announcement. fetchpriority is
    high because this is the largest element in the initial viewport."""
    return """<section class="page-hero">
  <div class="page-hero__media">
    <img src="assets/img/%s" alt="" width="1536" height="1024" fetchpriority="high">
  </div>
  <div class="wrap">
    <p class="breadcrumb"><a href="index.html">Home</a> &nbsp;&mdash;&nbsp; %s</p>
    <span class="kicker">%s</span>
    <h1>%s</h1>
    <p>%s</p>
  </div>
</section>""" % (image, title, kicker, title, sub)


def head_block(kicker, title, sub="", center=False):
    cls = "section-head section-head--center" if center else "section-head"
    s = '<p>%s</p>' % sub if sub else ""
    k = '<span class="kicker">%s</span>' % kicker if kicker else ""
    return '<div class="%s js-reveal">%s<h2 class="section-title">%s</h2>%s</div>' % (cls, k, title, s)


def card(icon, title, items, slot=True):
    """`slot` keeps an empty icon box for cards that have no icon, so headings
    stay on a common baseline across a row. Only six of the services shipped
    with artwork; without the placeholder the seventh rides up."""
    lis = "".join("<li>%s</li>" % i for i in items)
    if icon:
        ic = ('<div class="card__icon"><img src="assets/img/%s" alt="" width="56" height="56" '
              'loading="lazy"></div>') % icon
    elif slot:
        ic = '<div class="card__icon" aria-hidden="true"></div>'
    else:
        ic = ""
    return '<article class="card js-reveal">%s<h3>%s</h3><ul class="checklist">%s</ul></article>' % (ic, title, lis)


def stat(value, label):
    return '<div class="stat"><span class="stat__value">%s</span><span class="stat__label">%s</span></div>' % (value, label)


def feature(img, alt, title, text, stats, flip=False):
    return """<div class="feature js-reveal%s">
  <div class="feature__media"><img src="assets/img/%s" alt="%s" width="880" height="660" loading="lazy"></div>
  <div class="feature__body">
    <h2>%s</h2>
    <p>%s</p>
    <div class="feature__stats">%s</div>
  </div>
</div>""" % (" feature--flip" if flip else "", img, alt, title, text, "".join(stats))


CREDENTIALS = [
    "ADNOC &amp; EPPCO fuel supply",
    "Jet A1 &amp; Avgas",
    "ICAO-aligned standards",
    "FANS certified",
    "CPDLC &amp; ADS-C capable",
    "Permits in 15 minutes",
    "In-house customs &amp; immigration",
    "24/7 operations",
]


def marquee(items, dark=False):
    """The list is emitted twice: the track animates to exactly -50%, so the
    second copy is under the cursor at the moment the first finishes and the
    wrap is seamless. aria-hidden on the duplicate keeps it out of the a11y
    tree, which would otherwise read every credential twice."""
    one = "".join('<li class="marquee__item">%s</li>' % i for i in items)
    two = "".join('<li class="marquee__item" aria-hidden="true">%s</li>' % i for i in items)
    return """<div class="marquee%s">
  <ul class="marquee__track" aria-label="Accreditations and capabilities">%s%s</ul>
</div>""" % (" marquee--dark" if dark else "", one, two)


def cta_band():
    return """<section class="cta">
  <div class="wrap js-reveal">
    <span class="kicker">Get started today</span>
    <h2>Ready to Experience Effortless Efficiency and Precision?</h2>
    <p>We simplify every aspect of your flight operations through speed, precision, and
       real-time coordination. With a focus on minimizing delays and maximizing performance,
       Airlin FBO delivers reliable support you can depend on &mdash; every time.</p>
    <div class="cta__actions">
      <a class="btn btn--onnavy" href="contact.html">Contact us</a>
      <a class="btn btn--outline-light" href="%s">%s%s</a>
    </div>
  </div>
</section>""" % (SITE["tel_href"], svg("phone"), SITE["tel_label"])


# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------

SERVICES = [
    ("Aviation-Icons-14.png", "Ground Handing", [
        "Premium ramp equipment with trained handlers available 24/7",
        "Efficient baggage handling with tractors, trolleys, and crew/PAX transport",
        "Seamless aircraft turnaround with full airside coordination"]),
    ("Aviation-Icons-15.png", "Flight Operations", [
        "Landing permits obtained within 15 minutes with 72-hour validity",
        "Unlimited schedule revisions with real-time operational support",
        "Next landing permits arranged while aircraft is still on ground"]),
    ("Aviation-Icons-18.png", "Fuel Services", [
        "Fuel farm located just 2 minutes from aircraft parking stand",
        "Trusted suppliers: ADNOC &amp; EPPCO",
        "Jet A1 and Avgas readily available for all aircraft types"]),
    ("Aviation-Icons-17.png", "Crew &amp; Passenger Services", [
        "Access to premium VIP lounge with dedicated crew rest facilities",
        "Flight planning support, refreshments, and high-speed Wi-Fi",
        "Airside and landside transportation for crew and passengers"]),
    ("Aviation-Icons-16.png", "Catering &amp; Laundry Services", [
        "Wide range of international cuisine tailored to client preferences",
        "Direct delivery to aircraft with flexible revisions",
        "Laundry services available for crew convenience"]),
    (None, "Customs &amp; Immigration", [
        "In-house", "2 minute clearance", "Clearance for crew, passengers, and pets."]),
]

QUOTES = [
    ("Handling with Airlin FBO was smooth from start to finish. Permits were arranged quickly, and the team stayed in constant coordination with us. Everything was handled efficiently without delays.", "Capt. Arjun Mehta"),
    ("Very professional and responsive team. Schedule changes were managed instantly, and ground handling was perfectly coordinated. Made our turnaround fast and stress-free.", "Capt. Dmitry Volkov"),
    ("Excellent support from the operations team. Clear communication, quick responses, and a very efficient process overall. Definitely a reliable FBO to work with.", "Capt. James Walker"),
    ("The experience was seamless. From arrival to departure, everything was well organized. The staff was polite, helpful, and made the entire process very comfortable.", "Anastasia Ivanova"),
    ("Really impressed with how smooth everything was. No waiting, quick coordination, and a very professional team. The service felt premium and efficient.", "Luca Moretti"),
    ("Great experience overall. The staff was friendly, attentive, and ensured everything was handled quickly. It made the journey much more convenient and stress-free.", "Oliver Bennett"),
]


def build_home():
    services = "".join(card(i, t, its) for i, t, its in SERVICES)
    quotes = "".join(
        '<figure class="quote js-reveal"><span class="quote__mark" aria-hidden="true">&ldquo;</span>'
        '<blockquote><p>%s</p></blockquote>'
        '<figcaption class="quote__who">&mdash; %s</figcaption></figure>' % (q, who)
        for q, who in QUOTES)

    body = """<section class="hero">
  <div class="hero__media" data-hero-slideshow>
    <img class="is-active" src="assets/img/hero.jpg" alt="" width="1717" height="916" fetchpriority="high">
    <img src="assets/img/Aircraft-Parking-Facilities.jpg" alt="" width="1536" height="1024" loading="lazy">
    <img src="assets/img/VIP-Terminal-Lounge.jpg" alt="" width="1536" height="1024" loading="lazy">
  </div>
  <div class="wrap">
    <span class="kicker">Fujairah International Airport</span>
    <h1>Welcome to <span class="accent">Airlin FBO</span></h1>
    <p>End-to-end aviation support at Fujairah &mdash; permits in minutes, fuel two minutes
       from stand, and VIP handling that keeps your schedule intact.</p>
    <div class="hero__actions">
      <a class="btn btn--onnavy" href="contact.html">Contact us</a>
      <a class="btn btn--outline-light" href="facilities.html">Our facilities</a>
    </div>
    <div class="hero__meta">
      <span>Permits in 15 minutes</span>
      <span>Fuel 2 minutes from stand</span>
      <span>24/7 operations</span>
    </div>
  </div>
</section>

<div class="wrap">%s</div>

<section class="section">
  <div class="wrap">
    %s
    <div class="grid grid--3">%s</div>
  </div>
</section>

<section class="section section--surface">
  <div class="wrap">
    %s
    <div class="grid" style="gap:clamp(3rem,2rem+4vw,5rem)">
      %s
      %s
      %s
    </div>
  </div>
</section>

<section class="section section--dark">
  <div class="wrap">
    %s
    <div class="slider" data-slider>
      <div class="slider__track" tabindex="0" role="group"
           aria-roledescription="carousel" aria-label="Client testimonials">%s</div>
    </div>
  </div>
</section>

%s""" % (
        marquee(CREDENTIALS),
        head_block("Aviation Services Excellence", "Everything your flight needs, on the ground",
                   "Six coordinated service lines run by one team, so nothing waits on a hand-off."),
        services,
        head_block("World-Class Infrastructure", "Premium Facilities",
                   "Purpose-built terminal, fuel farm and parking, all within minutes of the stand."),
        feature("IMG_8725-scaled.jpg",
                "Seating and the branded feature wall in the Airlin FBO lounge",
                "VIP Terminal &amp; Lounges",
                "A premium and comfortable lounge designed for passengers to relax in privacy before "
                "departure or after arrival, ensuring a smooth and efficient experience.",
                [stat("35 PAX", "Lounge capacity"),
                 stat("2 Minutes", "In House Customs &amp; Immigration"),
                 stat("1 Minute", "From Landside to Airside")]),
        feature("Aircraft-Parking-Facilities.jpg",
                "Business jets parked on the ramp with ground crew in attendance",
                "Aircraft Parking",
                "Secure parking positions and climate-controlled hangars for aircraft of all sizes "
                "with 24/7 securty monitoring.",
                [stat("20+ Positions", "Parking Spots"),
                 stat("10+ Positions", "Maintenance Spots"),
                 stat("24/7 Monitored", "Security")], flip=True),
        feature("IMG_8721-scaled.jpg",
                "The Airlin FBO terminal interior",
                "Crew Rest Facilities",
                "Luxurious passenger-facilities with premium amenities, private meeting rooms and "
                "dedicated concierge services.",
                [stat("01 Available", "Crew lounge"),
                 stat("Full Amenities", "Meeting room"),
                 stat("24/7 Available", "Lounges and High Speed WiFi")]),
        head_block("Client Testimonials", "Trusted by the crews who fly here",
                   "Hear from the Captains, Crews, and Passengers who rely on Airlin FBO.", center=True),
        quotes, cta_band())

    return layout("index.html",
                  "Airlin FBO — Executive Aviation Support at Fujairah",
                  "Ground handling, flight operations, fuel and VIP crew and passenger services "
                  "at Fujairah International Airport. Permits in 15 minutes, 24/7 support.",
                  body)


FACILITIES = [
    ("VIP-Terminal-Lounge.jpg", "VIP Terminal Lounge",
     "A premium and comfortable lounge designed for passengers to relax in privacy before departure "
     "or after arrival, ensuring a smooth and efficient experience.",
     ["High-Speed Wifi", "Refreshments &amp; Catering", "Concierge Support", "Comfortable Seating"]),
    ("fuel-farm.jpg", "Fuel Farm",
     "Strategically located just 2 minutes from the aircraft parking stand, ensuring fast refueling "
     "and minimal turnaround time.",
     ["ADNOC &amp; EPPCO Fuel Supply", "Jet A1 &amp; Avgas Available", "Credit Facility Available",
      "Rapid Refueling Coordination"]),
    ("Aircraft-Parking-Facilities.jpg", "Aircraft Parking Facilities",
     "Safe, secure, and well-organized parking designed for efficient aircraft positioning and quick access.",
     ["Spacious Parking Bays", "Easy Ramp Access", "24/7 Security Coordination", "Efficient Ground Movement"]),
    ("crew-rest-facilities.jpg", "Crew Rest Facilities",
     "Dedicated crew rest areas providing comfort and privacy, helping crew stay refreshed and "
     "operationally ready.",
     ["Quiet &amp; Rest Areas", "High-Speed Wi-Fi", "Refreshments Available", "24/7 Accessibility"]),
    ("ground-support-equipment.jpg", "Ground Support Equipment",
     "Full coordination of ground support equipment ensuring smooth aircraft handling and fast turnaround.",
     ["GPU &amp; ASU Support", "Baggage Tractors &amp; Trolleys", "Aircraft Cleaning Coordination",
      "24/7 Ground Handling Team"]),
    ("crew-passenger-transport.jpg", "Crew &amp; Passenger Transport",
     "Seamless airside and landside transportation arranged efficiently for both crew and passengers.",
     ["Airside Transfers", "Landside Transportation", "Executive Vehicles", "On-Time Coordination"]),
]

CERTS = [
    ("1.png", "Regulatory Compliance",
     "Airlin FBO operates in alignment with international civil aviation standards, maintaining full "
     "compliance with regulatory authorities, safety protocols, and operational requirements.",
     ["ICAO-Aligned Operational Standards", "Safety &amp; Compliance Procedures",
      "Approved Ground Handling Practices"]),
    ("2.png", "FANS Certified Operations",
     "Airlin FBO supports FANS (Future Air Navigation Systems) operations, enabling advanced "
     "communication, improved situational awareness, and enhanced efficiency in modern air traffic "
     "environments.",
     ["FANS Certified", "CPDLC &amp; ADS-C Capabilities", "Optimized Flight Communication"]),
    ("3.png", "Quality Assurance &amp; Operational Excellence",
     "Our operations are driven by structured procedures, trained personnel, and continuous "
     "performance monitoring, ensuring consistent service quality and operational efficiency.",
     ["Trained &amp; Qualified Personnel", "Standard Operating Procedures (SOPs)",
      "Continuous Performance Monitoring"]),
]


def build_facilities():
    cards = []
    for img, title, text, items in FACILITIES:
        media = ('<div class="card__media"><img src="assets/img/%s" alt="%s" width="880" '
                 'height="587" loading="lazy"></div>'
                 % (img, title.replace("&amp;", "and")) if img else "")
        cards.append('<article class="card js-reveal">%s<h3>%s</h3><p>%s</p><ul class="checklist">%s</ul></article>'
                     % (media, title, text, "".join("<li>%s</li>" % i for i in items)))

    certs = []
    for img, title, text, items in CERTS:
        certs.append('<article class="card js-reveal"><div class="card__icon">'
                     '<img src="assets/img/%s" alt="" width="56" height="56" loading="lazy"></div>'
                     '<h3>%s</h3><p>%s</p><ul class="checklist">%s</ul></article>'
                     % (img, title, text, "".join("<li>%s</li>" % i for i in items)))

    body = """%s

<section class="section">
  <div class="wrap">
    %s
    <div class="grid grid--3">%s</div>
  </div>
</section>

<section class="section section--surface">
  <div class="wrap">
    %s
    <div class="grid grid--3">%s</div>
  </div>
</section>

%s""" % (page_hero("Facilities",
                   "Comprehensive infrastructure designed for seamless and efficient aviation operations",
                   "VIP-Terminal-Lounge.jpg"),
         head_block("Our Facillities", "Built for fast, predictable turnarounds"),
         "".join(cards),
         head_block("Certifications &amp; Compliance", "Operating to international standards",
                    "Operating in accordance with international aviation standards, ensuring safety, "
                    "compliance, and efficient operational control at all times."),
         "".join(certs), cta_band())

    return layout("facilities.html", "Facilities — Airlin FBO",
                  "VIP terminal lounge, fuel farm, aircraft parking, crew rest and ground support "
                  "equipment at Fujairah International Airport.", body)


def build_collaborations():
    groups = [
        ("WHO WE WORK WITH", ["Aircraft Operators", "Charter Brokers", "Flight Dispatch Teams",
                              "Government &amp; Diplomatic Flights", "Cargo &amp; Special Mission Operators"]),
        ("WHY PARTNER WITH US", ["24/7 operational support", "Fast permit approvals (within minutes)",
                                 "Real-time coordination with airport authorities",
                                 "Flexible and responsive team", "Competitive and transparent pricing"]),
        ("WHAT WE OFFER PARTNERS", ["Ground Handling Coordination", "Landing &amp; Overflight Permits",
                                    "Fuel Arrangements", "Crew &amp; Passenger Support",
                                    "Catering &amp; Logistics", "On-ground supervision &amp; updates"]),
    ]
    # Every card here is icon-less, so no placeholder is needed to keep them level.
    cards = "".join(card(None, t, items, slot=False) for t, items in groups)

    body = """%s

<section class="section">
  <div class="wrap">
    <div class="section-head section-head--center">
      <span class="kicker">Collaboration Approach</span>
      <h2 class="section-title">Let&rsquo;s Work Together</h2>
      <p>&ldquo;Efficiency is best delivered through strong partnerships &mdash; and that&rsquo;s
         what we build at Airlin FBO.&rdquo;</p>
    </div>
    <div class="grid grid--3">%s</div>
  </div>
</section>

%s""" % (page_hero("Collaborations",
                   "Partnerships with operators, brokers and dispatch teams who need ground support they can rely on",
                   "airline-slider.jpg"),
         cards, cta_band())

    return layout("collaborations.html", "Collaborations — Airlin FBO",
                  "Partner with Airlin FBO for ground handling coordination, permits, fuel and crew "
                  "support at Fujairah.", body)


def build_why():
    paras = [
        "Airlin FBO is built around one core principle — efficiency. In the fast-moving aviation industry, we provide quick, reliable, and well-organized support to keep flights operating smoothly and on time.",
        "From obtaining landing permits and arranging fuel to coordinating ground handling and managing last-minute schedule changes, our team works with speed, accuracy, and clear communication. We stay closely involved in every operation, working directly with airport authorities, crew, and service providers to ensure seamless coordination from arrival to departure.",
        "What sets Airlin FBO apart is our hands-on and responsive approach. We provide real-time support without unnecessary delays, allowing operators and crew to focus on their journey while we handle everything on the ground.",
        "We understand that aviation plans can change at any moment, so our operations are flexible and adaptable. Whether it is an urgent request or a schedule revision, we respond quickly to deliver smooth and efficient solutions.",
        "Beyond operations, we also ensure a comfortable experience for crew and passengers by arranging services such as VIP lounges, crew rest areas, transport, catering, and on-ground assistance without complications.",
        "At Airlin FBO, we continuously improve our processes to maintain high standards of speed, precision, and reliability. Our mission is simple — to make aviation operations faster, smoother, and more efficient with professionalism and confidence every step of the way.",
    ]
    founder = [
        "Mishal Ansari founded Airlin FBO with a vision to deliver fast, reliable, and professional aviation support. With a strong background in flight operations and ground handling, he established the company to provide seamless coordination, rapid permit approvals, and exceptional service for crew and passengers.",
        "Today, Airlin FBO is recognized for its efficiency, reliability, and commitment to operational excellence.",
        "Seeing the growing importance of Fujairah in executive aviation, Mishal established Airlin FBO to focus on speed, smooth coordination, and operational excellence. Under his leadership, the company has become known for fast permit approvals, dependable ground handling, and efficient support for crew and passengers.",
    ]

    body = """%s

<section class="section">
  <div class="wrap" style="max-width:74ch">
    <div class="section-head">
      <span class="kicker">Our approach</span>
      <h2 class="section-title">Efficiency, as an operating principle</h2>
    </div>
    <div class="grid" style="gap:1.15rem">%s</div>
  </div>
</section>

<section class="section section--dark">
  <div class="wrap">
    <blockquote class="pullquote js-reveal">
      <p>&ldquo;In aviation, success comes from precision, preparation, and delivering reliable
         results when they matter most.&rdquo;</p>
      <cite>Mishal Ansari &mdash; Founder &amp; President, Airlin FBO</cite>
    </blockquote>
  </div>
</section>

<section class="section">
  <div class="wrap" style="max-width:74ch">
    <div class="section-head">
      <span class="kicker">Mishal Ansari</span>
      <h2 class="section-title">Founder &amp; President</h2>
    </div>
    <div class="grid" style="gap:1.15rem">%s</div>
  </div>
</section>

%s""" % (page_hero("Why Airlin FBO",
                   "From fuel supply to crew facilities, we provide end to end aviation support and "
                   "services with transparent pricing and exceptional reliability. Your operations, perfected.",
                   "IMG_8725-scaled.jpg"),
         "".join("<p>%s</p>" % p for p in paras),
         "".join("<p>%s</p>" % p for p in founder), cta_band())

    return layout("why-airlin-fbo.html", "Why Airlin FBO — Airlin FBO",
                  "Why operators choose Airlin FBO: speed, real-time coordination, and reliable "
                  "ground support at Fujairah.", body)


def build_about():
    paras = [
        "From fuel supply tocrew facilities, we provide end-to aviation support services with transparent pricing and exeptional reliability. Your operations, perfetecd.",
        "From the moment a request is received, our team works proactively to ensure every detail is handled with speed and accuracy. Whether it is obtaining landing permits within minutes, coordinating ground handling, arranging fuel, or managing last-minute schedule changes, our approach is always centered around reducing waiting time and simplifying the process for our clients.",
    ]
    founder = [
        "In the demanding world of private aviation, where timing, precision, and trust are critical, Mishal Anzari has built Airlin FBO with a clear and disciplined vision — to deliver efficiency at every level of operation. His journey into aviation was driven by curiosity, which later evolved into a deep understanding of flight operations, logistics, and VIP ground handling.",
        "Rather than following a conventional path, Mishal developed his expertise through hands-on experience, working closely with real-time operations, aircraft movements, and client coordination. This practical exposure shaped his ability to manage complex situations with clarity and control.",
        "Mishal’s leadership style is rooted in discipline and accountability. He believes that strong systems, preparation, and attention to detail are the foundations of consistent performance. His approach ensures that every operation — whether routine or time-critical — is executed with precision.",
        "Looking ahead, his vision is to expand Airlin FBO into a globally recognized network of operations while maintaining the same high standards of efficiency, trust, and professionalism. For Mishal Anzari, success is not defined by scale alone, but by consistency, reliability, and the ability to deliver under pressure.",
    ]

    body = """%s

<section class="section">
  <div class="wrap" style="max-width:74ch">
    <div class="grid" style="gap:1.15rem">%s</div>
  </div>
</section>

<section class="section section--surface">
  <div class="wrap" style="max-width:74ch">
    <div class="section-head">
      <span class="kicker">Mishal Anzari</span>
      <h2 class="section-title">Founder &amp; President &ndash; Airlin FBO</h2>
    </div>
    <div class="grid" style="gap:1.15rem">%s</div>
  </div>
</section>

%s""" % (page_hero("About us", "Who we are and how we work.", "IMG_8721-scaled.jpg"),
         "".join("<p>%s</p>" % p for p in paras),
         "".join("<p>%s</p>" % p for p in founder), cta_band())

    return layout("about.html", "About Us — Airlin FBO",
                  "Airlin FBO delivers end-to-end aviation support with transparent pricing and "
                  "exceptional reliability at Fujairah International Airport.", body)


def build_careers():
    learn = ["Flight operations and ground handling coordination",
             "Permit processing and aviation documentation (GENDEC, API, etc.)",
             "Real-time problem solving in high-pressure situations",
             "Communication with international crew and operators",
             "Time management and efficiency-driven execution",
             "Customer service in a premium aviation environment"]
    why = ["Dynamic and fast-paced aviation environment",
           "Strong focus on efficiency and real operations",
           "Hands-on learning with real flight movements",
           "Opportunity to grow within the aviation industry",
           "Exposure to international standards and clients",
           "Supportive and professional team culture"]
    fields = ["Aviation Management", "Logistics &amp; Operations", "Customer Service"]

    body = """%s

<section class="section">
  <div class="wrap" style="max-width:74ch">
    <div class="section-head">
      <span class="kicker">Join a Team That Keeps Aviation Moving</span>
      <h2 class="section-title">Build Your Career in Aviation</h2>
    </div>
    <div class="grid" style="gap:1.15rem">
      <p>At Airlin FBO, we deliver seamless ground handling, efficient flight support, and premium
         passenger services &mdash; all driven by speed, precision, and coordination. Behind every
         smooth operation is a team that understands the importance of efficiency in aviation.If
         you&rsquo;re passionate about aviation and want to be part of a fast-paced, real-time
         operational environment, Airlin FBO is the place to grow.</p>
      <p>Whether you are experienced or just starting out, Airlin FBO provides an environment here
         you can develop real, hands-on aviation skills.From day one, you will be exposed to live
         operations &mdash; handling flights, coordinating with crew, managing permits, and
         understanding how aviation works behind the scenes.We believe in learning by doing. Our
         team is constantly involved in real-time decision-making, giving you the confidence and
         experience needed to excel in the aviation industry.</p>
    </div>
  </div>
</section>

<section class="section section--surface">
  <div class="wrap">
    <div class="grid grid--2">
      %s
      %s
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="grid grid--2">
      <div>
        <div class="section-head">
          <span class="kicker">Internship Opportunities</span>
          <h2 class="section-title">Start where the aircraft are</h2>
          <p>We welcome students and fresh graduates who are eager to enter the aviation
             industry.Fields:</p>
        </div>
        <ul class="checklist">%s</ul>
        <p style="margin-top:1rem">Gain practical experience, develop industry skills, and
           understand how real aviation operations are managed.</p>
      </div>
      <div>
        <div class="section-head">
          <span class="kicker">How to Apply</span>
          <h2 class="section-title">Send us your CV</h2>
        </div>
        <div class="contact-item">
          <span class="contact-item__icon">%s</span>
          <dl style="margin:0">
            <dt>Applications</dt>
            <dd><a href="mailto:%s">%s</a></dd>
          </dl>
        </div>
        <p style="margin-top:1rem">Subject Line: Application for [Position Name]</p>
        <p style="margin-top:1.25rem">At Airlin FBO, you don&rsquo;t just work &mdash; you grow.The
           fast-paced environment, real responsibilities, and continuous learning make this a place
           where individuals develop strong operational skills and build long-term careers.</p>
      </div>
    </div>
  </div>
</section>

%s""" % (page_hero("Careers at Airlin FBO",
                   "Discover your potential. Build your future. Experience aviation the Airlin way.",
                   "IMG_8727-scaled.jpg"),
         card(None, "What You Will Learn", learn, slot=False),
         card(None, "Why Work With Airlin FBO", why, slot=False),
         "".join("<li>%s</li>" % f for f in fields),
         svg("mail"), SITE["careers"], SITE["careers"], cta_band())

    return layout("careers.html", "Careers — Airlin FBO",
                  "Careers and internships at Airlin FBO: hands-on aviation operations experience "
                  "at Fujairah International Airport.", body)


def build_contact():
    body = """%s

<section class="section">
  <div class="wrap">
    <div class="contact-grid">
      <div>
        <div class="section-head">
          <span class="kicker">Contact Details</span>
          <h2 class="section-title">We&rsquo;re Available 24/7</h2>
          <p>From handling requests to operational coordination, our team ensures quick responses
             and seamless communication at every stage.</p>
        </div>
        <dl class="contact-list">
          <div class="contact-item">
            <span class="contact-item__icon">%s</span>
            <div><dt>Support line</dt><dd><a href="%s">%s</a></dd></div>
          </div>
          <div class="contact-item">
            <span class="contact-item__icon">%s</span>
            <div><dt>Email</dt><dd><a href="mailto:%s">%s</a></dd></div>
          </div>
          <div class="contact-item">
            <span class="contact-item__icon">%s</span>
            <div><dt>WhatsApp</dt><dd><a href="%s">%s</a></dd></div>
          </div>
          <div class="contact-item">
            <span class="contact-item__icon">%s</span>
            <div><dt>Location</dt><dd>Fujairah International Airport, UAE</dd></div>
          </div>
          <div class="contact-item">
            <span class="contact-item__icon">%s</span>
            <div><dt>Hours</dt><dd>24 hours, 7 days a week</dd></div>
          </div>
        </dl>
      </div>
      <div>
        <iframe class="map" src="%s" title="Airlin FBO on Google Maps"
                loading="lazy" referrerpolicy="no-referrer-when-downgrade"
                allowfullscreen></iframe>
      </div>
    </div>
  </div>
</section>

<section class="section section--surface">
  <div class="wrap">
    %s
    <form class="form js-reveal" data-enquiry="%s" novalidate>
      <div class="form__row">
        <div class="field">
          <label for="f-name">Name</label>
          <input id="f-name" name="name" type="text" autocomplete="name" required>
          <span class="field__error" aria-live="polite"></span>
        </div>
        <div class="field">
          <label for="f-email">Email</label>
          <input id="f-email" name="email" type="email" autocomplete="email" required>
          <span class="field__error" aria-live="polite"></span>
        </div>
      </div>
      <div class="form__row">
        <div class="field">
          <label for="f-company">Company / operator</label>
          <input id="f-company" name="company" type="text" autocomplete="organization">
          <span class="field__error" aria-live="polite"></span>
        </div>
        <div class="field">
          <label for="f-aircraft">Aircraft type / registration</label>
          <input id="f-aircraft" name="aircraft" type="text">
          <span class="field__error" aria-live="polite"></span>
        </div>
      </div>
      <div class="field">
        <label for="f-date">Date of movement</label>
        <input id="f-date" name="date" type="date">
        <span class="field__error" aria-live="polite"></span>
      </div>
      <div class="field">
        <label for="f-message">How can we help?</label>
        <textarea id="f-message" name="message" rows="5" required></textarea>
        <span class="field__error" aria-live="polite"></span>
      </div>
      <div>
        <button class="btn btn--primary" type="submit">Send enquiry</button>
      </div>
      <p class="form__status" role="status" aria-live="polite"></p>
    </form>
  </div>
</section>

%s""" % (page_hero("Get in Touch", "Operational support, around the clock.",
                   "Aircraft-Parking-Facilities.jpg"),
         svg("phone"), SITE["tel_href"], SITE["tel_label"],
         svg("mail"), SITE["email"], SITE["email"],
         svg("wa"), SITE["whatsapp"], SITE["tel_label"],
         svg("pin"), svg("clock"), SITE["map"],
         head_block("Request handling", "Send us your movement details",
                    "Tell us the aircraft, the date and what you need on the ground. "
                    "We reply within the hour, day or night."),
         SITE["email"],
         cta_band())

    return layout("contact.html", "Contact — Airlin FBO",
                  "Contact Airlin FBO at Fujairah International Airport. Available 24/7 by phone, "
                  "WhatsApp and email.", body)


PAGES = {
    "index.html":          build_home,
    "facilities.html":     build_facilities,
    "collaborations.html": build_collaborations,
    "why-airlin-fbo.html": build_why,
    "about.html":          build_about,
    "careers.html":        build_careers,
    "contact.html":        build_contact,
}


FOUNDER = "Mishal Anzari"


def emphasise_name(html):
    """Set the founder's name in the heavier weight wherever it appears.

    Applied to the generated HTML rather than written into each copy string, so
    the name stays a single plain-text value in one place and cannot drift out
    of sync with the correction list. Only the weight is set — colour is left to
    inherit, so the name still reads gold inside the pull quote on the dark
    section and ink inside body prose.
    """
    return html.replace(FOUNDER, '<strong class="name">%s</strong>' % FOUNDER)


_STAMP_CACHE = {}


def stamp(html):
    """Append a content version to every local asset URL.

    Filenames here are stable while their contents are not — the icons were
    re-cut in place, and site.css changes constantly. Browsers cache both
    heuristically (a plain static server sends no Cache-Control), so an edit can
    keep serving the old bytes long after deploy. Keying the query string to the
    file's mtime means only what actually changed gets a new URL.
    """
    def rewrite(m):
        rel = m.group(1)
        if rel not in _STAMP_CACHE:
            path = os.path.join(OUT, rel)
            try:
                _STAMP_CACHE[rel] = str(int(os.path.getmtime(path)))[-6:]
            except OSError:
                _STAMP_CACHE[rel] = ""
        v = _STAMP_CACHE[rel]
        return rel + ("?v=" + v if v else "")

    return re.sub(r'(assets/(?:css|js|img)/[A-Za-z0-9._-]+)', rewrite, html)


def main():
    total = 0
    for name, fn in PAGES.items():
        html = stamp(emphasise_name(fix(fn())))
        path = os.path.join(OUT, name)
        io.open(path, "w", encoding="utf-8").write(html)
        size = os.path.getsize(path)
        total += size
        print("  %-24s %7d bytes" % (name, size))
    print("  %-24s %7d bytes total" % ("", total))

    # Guard: the fixes must actually have landed, and no fixed string may survive.
    stale = []
    pages_text = {}
    for name in PAGES:
        text = io.open(os.path.join(OUT, name), encoding="utf-8").read()
        pages_text[name] = text
        for bad, _ in TYPO_FIXES:
            if bad in text:
                stale.append("%s: %r" % (name, bad))
    if stale:
        print("\nUNFIXED TYPOS STILL PRESENT:")
        for s in stale:
            print("   ", s)
        return 1

    # Guard: every modifier class emitted must exist in the stylesheet. Renaming
    # .section--navy to .section--dark in the CSS once left this file emitting a
    # class nothing matched, so a whole section rendered white-on-white.
    css_path = os.path.join(OUT, "assets", "css", "site.css")
    css = io.open(css_path, encoding="utf-8").read()
    orphans = set()
    for name, text in pages_text.items():
        for attr in re.findall(r'class="([^"]+)"', text):
            for cls in attr.split():
                if "--" in cls and ("." + cls) not in css:
                    orphans.add("%s  (in %s)" % (cls, name))
    if orphans:
        print("\nCLASSES WITH NO MATCHING CSS RULE:")
        for o in sorted(orphans):
            print("   ", o)
        return 1

    print("\n  %d copy corrections applied cleanly." % len(TYPO_FIXES))
    print("  all modifier classes matched to stylesheet rules.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
