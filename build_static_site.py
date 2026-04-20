import os

ROOT = r"C:\PersonalMasterOverseer\YourMasterOverseerSite"

def ensure_dir(path):
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)

def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def main():
    print("Building minimal static site...")

    # Folders
    assets_css = os.path.join(ROOT, "assets", "css")
    assets_js = os.path.join(ROOT, "assets", "js")
    assets_img = os.path.join(ROOT, "assets", "img")

    ensure_dir(assets_css)
    ensure_dir(assets_js)
    ensure_dir(assets_img)

    # CSS
    style_css = """body{margin:0;font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#050816;color:#f9fafb}
a{color:#38bdf8;text-decoration:none}
a:hover{text-decoration:underline}
header{padding:20px 32px;border-bottom:1px solid #1f2933;background:rgba(3,7,18,0.9);backdrop-filter:blur(10px);position:sticky;top:0;z-index:10}
nav{display:flex;justify-content:space-between;align-items:center;max-width:1100px;margin:0 auto}
nav .logo{font-weight:700;letter-spacing:.08em;text-transform:uppercase;font-size:14px;color:#e5e7eb}
nav .links a{margin-left:18px;font-size:14px;color:#9ca3af}
main{max-width:1100px;margin:0 auto;padding:40px 20px 80px}
.hero{display:grid;grid-template-columns:minmax(0,3fr) minmax(0,2fr);gap:40px;align-items:center}
.hero h1{font-size:40px;line-height:1.1;margin-bottom:16px;color:#f9fafb}
.hero p{color:#9ca3af;font-size:15px;line-height:1.6}
.hero .tag{display:inline-flex;align-items:center;border-radius:999px;border:1px solid #1f2933;padding:4px 10px;font-size:11px;text-transform:uppercase;letter-spacing:.12em;color:#9ca3af;margin-bottom:12px}
.hero .primary-btn{display:inline-flex;align-items:center;justify-content:center;margin-top:20px;padding:10px 18px;border-radius:999px;background:linear-gradient(135deg,#22c55e,#22d3ee);color:#020617;font-weight:600;font-size:14px;border:none;cursor:pointer}
.hero .secondary-link{display:inline-flex;align-items:center;margin-top:10px;font-size:13px;color:#9ca3af}
.section{margin-top:60px}
.section h2{font-size:22px;margin-bottom:10px;color:#e5e7eb}
.section p{color:#9ca3af;font-size:14px;max-width:640px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:18px;margin-top:20px}
.card{border-radius:14px;border:1px solid #1f2933;padding:16px;background:radial-gradient(circle at top,#020617,#020617 40%,#020617)}
.card h3{font-size:15px;margin-bottom:6px;color:#e5e7eb}
.card p{font-size:13px;color:#9ca3af}
.badge{display:inline-flex;align-items:center;border-radius:999px;border:1px solid #1f2933;padding:2px 8px;font-size:11px;color:#9ca3af;margin-bottom:6px}
.footer{border-top:1px solid #1f2933;padding:18px 20px;color:#6b7280;font-size:12px;text-align:center;margin-top:60px}
@media(max-width:800px){.hero{grid-template-columns:1fr}.hero h1{font-size:30px}}
"""
    write_file(os.path.join(assets_css, "style.css"), style_css)

    # JS
    main_js = """console.log("YourMasterOverseer static site loaded.");"""
    write_file(os.path.join(assets_js, "main.js"), main_js)

    # index.html
    index_html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>YourMasterOverseer – Build Your AI Universe</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="assets/css/style.css">
  <script src="assets/js/main.js" defer></script>
</head>
<body>
<header>
  <nav>
    <div class="logo">YOURMASTEROVERSEER</div>
    <div class="links">
      <a href="index.html">Home</a>
      <a href="bots.html">Bots</a>
      <a href="how-it-works.html">How it works</a>
      <a href="roadmap.html">Roadmap</a>
      <a href="https://github.com/GenesisBots" target="_blank">GitHub</a>
    </div>
  </nav>
</header>
<main>
  <section class="hero">
    <div>
      <div class="tag">GenesisBots · YourMasterOverseer</div>
      <h1>Build your own AI universe.</h1>
      <p>
        YourMasterOverseer is your control panel for autonomous bots, self-running systems,
        and future G‑Coin powered economies. Today, it’s a clean hub for your GenesisBots.
        When you’re ready, it becomes the mainnet home for your AI world.
      </p>
      <button class="primary-btn" onclick="window.location.href='bots.html'">
        Explore the bots
      </button>
      <div class="secondary-link">
        Or visit the code on GitHub → 
      </div>
    </div>
    <div>
      <div class="card">
        <div class="badge">Live today</div>
        <h3>GenesisBots ecosystem</h3>
        <p>
          A growing collection of automation bots, app generators, and intelligence tools
          you can run locally and extend however you want.
        </p>
      </div>
      <div class="card" style="margin-top:12px;">
        <div class="badge">Future</div>
        <h3>G‑Coin mainnet</h3>
        <p>
          When you flip the switch, this site becomes the front door to a live on‑chain
          economy: treasuries, marketplaces, and evolving AI systems.
        </p>
      </div>
    </div>
  </section>

  <section class="section">
    <h2>What you can do right now</h2>
    <p>
      This version of YourMasterOverseer is intentionally minimal and public‑safe.
      It gives you a clean place to send traffic while you build out the deeper systems.
    </p>
    <div class="cards">
      <div class="card">
        <h3>Browse GenesisBots</h3>
        <p>See the bots that already exist, what they do, and where to get the code.</p>
      </div>
      <div class="card">
        <h3>Link everything to GitHub</h3>
        <p>Each bot links directly to its repo under the GenesisBots organization.</p>
      </div>
      <div class="card">
        <h3>Prepare for mainnet</h3>
        <p>When G‑Coin is ready, you already have a public‑facing home for it.</p>
      </div>
    </div>
  </section>
</main>
<div class="footer">
  YourMasterOverseer · GenesisBots · Minimal public shell until G‑Coin mainnet.
</div>
</body>
</html>
"""
    write_file(os.path.join(ROOT, "index.html"), index_html)

    # bots.html
    bots_html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Bots · YourMasterOverseer</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
<header>
  <nav>
    <div class="logo">YOURMASTEROVERSEER</div>
    <div class="links">
      <a href="index.html">Home</a>
      <a href="bots.html">Bots</a>
      <a href="how-it-works.html">How it works</a>
      <a href="roadmap.html">Roadmap</a>
      <a href="https://github.com/GenesisBots" target="_blank">GitHub</a>
    </div>
  </nav>
</header>
<main>
  <section class="section">
    <h2>GenesisBots library</h2>
    <p>
      These are the bots that live in your ecosystem today. Each one links directly to its
      GitHub repo so people can clone, run, and extend them.
    </p>
    <div class="cards">
      <div class="card">
        <div class="badge">Automation</div>
        <h3>AutoMobileAppMakerBot</h3>
        <p>Turn a simple config file into a fully generated mobile app project.</p>
        <p><a href="https://github.com/GenesisBots/AutoMobileAppMakerBot" target="_blank">View on GitHub →</a></p>
      </div>
      <div class="card">
        <div class="badge">Research</div>
        <h3>HeadlineScraperBot Pro</h3>
        <p>Scrape, cluster, and analyze headlines for trends and narratives.</p>
        <p><a href="https://github.com/GenesisBots" target="_blank">View repo →</a></p>
      </div>
      <div class="card">
        <div class="badge">Careers</div>
        <h3>JobIntelligenceBot</h3>
        <p>Map roles, skills, and job descriptions into a structured intelligence layer.</p>
        <p><a href="https://github.com/GenesisBots" target="_blank">View repo →</a></p>
      </div>
      <div class="card">
        <div class="badge">Ops</div>
        <h3>ExecutiveSidekickBot</h3>
        <p>Daily, weekly, and monthly operational support as a local AI agent.</p>
        <p><a href="https://github.com/GenesisBots" target="_blank">View repo →</a></p>
      </div>
    </div>
  </section>
</main>
<div class="footer">
  All bots are open‑source under the GenesisBots organization.
</div>
</body>
</html>
"""
    write_file(os.path.join(ROOT, "bots.html"), bots_html)

    # how-it-works.html
    hiw_html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>How it works · YourMasterOverseer</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
<header>
  <nav>
    <div class="logo">YOURMASTEROVERSEER</div>
    <div class="links">
      <a href="index.html">Home</a>
      <a href="bots.html">Bots</a>
      <a href="how-it-works.html">How it works</a>
      <a href="roadmap.html">Roadmap</a>
      <a href="https://github.com/GenesisBots" target="_blank">GitHub</a>
    </div>
  </nav>
</header>
<main>
  <section class="section">
    <h2>How this version works</h2>
    <p>
      Right now, YourMasterOverseer is a minimal public shell. It’s designed to be safe,
      simple, and focused: a clean front door for your GenesisBots and a future home for
      the G‑Coin mainnet.
    </p>
    <div class="cards">
      <div class="card">
        <h3>Static only</h3>
        <p>
          This site is pure HTML/CSS/JS. No backend logic is exposed, no private systems
          are running here. It’s built to be hosted on GitHub Pages.
        </p>
      </div>
      <div class="card">
        <h3>GitHub as the source of truth</h3>
        <p>
          Every bot and every serious system lives in your GenesisBots organization.
          This site simply points people to the right repos.
        </p>
      </div>
      <div class="card">
        <h3>Future: G‑Coin mainnet</h3>
        <p>
          When you’re ready, you can wire this shell into a real backend and chain
          integration. Until then, it stays lean and public‑safe.
        </p>
      </div>
    </div>
  </section>
</main>
<div class="footer">
  Minimal now. Expandable later. Built to evolve with you.
</div>
</body>
</html>
"""
    write_file(os.path.join(ROOT, "how-it-works.html"), hiw_html)

    # roadmap.html
    roadmap_html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Roadmap · YourMasterOverseer</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
<header>
  <nav>
    <div class="logo">YOURMASTEROVERSEER</div>
    <div class="links">
      <a href="index.html">Home</a>
      <a href="bots.html">Bots</a>
      <a href="how-it-works.html">How it works</a>
      <a href="roadmap.html">Roadmap</a>
      <a href="https://github.com/GenesisBots" target="_blank">GitHub</a>
    </div>
  </nav>
</header>
<main>
  <section class="section">
    <h2>Roadmap</h2>
    <p>
      This roadmap is intentionally high‑level. It separates what exists today from what
      you plan to light up when G‑Coin mainnet and deeper systems are ready.
    </p>
    <div class="cards">
      <div class="card">
        <div class="badge">Now</div>
        <h3>Public shell + bots</h3>
        <p>
          Minimal static site, GenesisBots library, and a clear place to send traffic
          from GitHub, Product Hunt, Reddit, and beyond.
        </p>
      </div>
      <div class="card">
        <div class="badge">Next</div>
        <h3>Dashboard + wiring</h3>
        <p>
          Connect this shell to a private backend app: dashboards, orchestration, and
          internal tools that never have to be public.
        </p>
      </div>
      <div class="card">
        <div class="badge">Later</div>
        <h3>G‑Coin mainnet</h3>
        <p>
          Turn YourMasterOverseer.com into the front door for a live economy: treasuries,
          marketplaces, and evolving AI systems.
        </p>
      </div>
    </div>
  </section>
</main>
<div class="footer">
  Roadmap is directional, not a promise. You control the pace.
</div>
</body>
</html>
"""
    write_file(os.path.join(ROOT, "roadmap.html"), roadmap_html)

    print("Static site generated successfully at:", ROOT)

if __name__ == "__main__":
    main()
