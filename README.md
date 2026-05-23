<div align="right">
  <a href="https://buymeacoffee.com/stop6g" target="_blank">
    <img src="https://img.shields.io/badge/Buy%20Me%20a%20Coffee-ffdd00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black" alt="Buy Me A Coffee">
  </a>
</div>

# stop6g.eu Threat Awards 2026

> A second reading of the EU's official 6G research portfolio.

This repository hosts the code and data behind the **stop6g.eu Threat Awards 2026**, an independent audit of the 188 key achievements published by the European Union's Smart Networks and Services Joint Undertaking (SNS JU) in 2025.

**Live site:** [https://stop6g.github.io/6G-THREAT-AWARDS/](https://stop6g.github.io/6G-THREAT-AWARDS/)  
**Source data:** [SNS JU Key Achievements 2025](https://smart-networks.europa.eu/key-achievements/)

---

## Manifesto

Every year, the European Union publishes the key achievements of its Smart Networks and Services Joint Undertaking, the academic and industrial consortium tasked with designing the infrastructure of the next generation of mobile communications.

In 2025, that list ran to **188 achievements**, across **63 projects**, funded by the European taxpayer through Horizon Europe.

**We read them all.**

What follows is not a parody. The projects described here are real. The funding is real. The technical achievements are real. Every citation links to the official SNS JU website, where you can read the original description in the language of the engineers who wrote it. That language is, almost without exception, the language of optimization, efficiency, resilience, and sustainability.

**We are simply offering a second reading.**

The stop6g.eu Threat Awards 2026 recognize outstanding contributions to the construction of a planetary-scale sensing, identification, prediction, and control infrastructure. An infrastructure that its architects call 6G, and that we call something else.

### The Awards

- **The Invisible Eye** · for device-free human sensing through radio waves.
- **The Ghost in the Network** · for building living computational copies of people.
- **The Oracle** · for AI that anticipates behavior before it happens.
- **The Permanent Suspect** · for architectures that demand continuous proof of innocence.
- **The Wallbreaker** · for frequencies that make walls, darkness and distance irrelevant.
- **The Good Samaritan** · for the most elegant dual-use technology.
- **The Everywhere Machine** · for bringing inference inside the cell tower.
- **The Last Horizon** · for closing the last geographic escape route.
- **The Green Curtain** · for the most sophisticated use of sustainability language to describe surveillance infrastructure.
- **The Full Stack (Grand Prix)** · for the project advancing the most threat categories simultaneously.

### The Numbers

- **147 out of 188 achievements (78%)** touch at least one threat category.
- Only **41 are clean**.
- Of the 147 flagged, **4 score CRITICAL** and **29 score HIGH or above**.
- Meanwhile **125 of the 188**, two thirds of the entire list, mention sustainability, green technology, or human-centric values somewhere in their description.
- Of those, **48 use at least two sustainability terms**, enough to qualify for The Green Curtain pool.

We are not saying the engineers are lying. We are saying that the words "green", "inclusive" and "privacy-preserving" appearing in a project description are not evidence of those properties.

**They are evidence of good communications.**

The battle started today. Enjoy the ceremony.

---

## How We Score

The source data is the official SNS JU Key Achievements 2025 database, published by the Smart Networks and Services Joint Undertaking. The database is publicly accessible via the SNS JU WordPress REST API at `smart-networks.europa.eu/wp-json/wp/v2/key_achievement`.

For each achievement we concatenate three fields from the official record: the **title**, the **description**, and the **sub-categories**. We lowercase the result and search for the presence of specific keyword phrases corresponding to eight threat categories.

### Weighted Scoring

Not all categories are equally proximate to the core threat model. Categories corresponding to direct human sensing or identity control carry more weight than infrastructure categories that are necessary but not sufficient for surveillance.

| Category | Threat | Weight |
|---|---|---|
| ISAC / Sensing | The Invisible Eye | 2.0 |
| Digital Twin | The Ghost in the Network | 2.0 |
| AI Predictive | The Oracle | 1.5 |
| Zero Trust | The Permanent Suspect | 2.0 |
| High-frequency | The Wallbreaker | 1.0 |
| Surveillance / PPDR | The Good Samaritan | 1.5 |
| Edge / Cloud | The Everywhere Machine | 0.5 |
| NTN / Satellite | The Last Horizon | 1.0 |

The total weighted danger score runs from **0 to 11.5**. Thresholds are:

- **CRITICAL** ≥ 5.0
- **HIGH** ≥ 3.5
- **MED** ≥ 2.0
- **LOW** ≥ 1.0
- **TRACE** > 0
- **CLEAR** = 0

### Award Selection Rules

Award selection uses a **specialist rule**. Each award goes to the achievement that matches the most keywords within that specific category, not the achievement with the highest overall score. An omnibus reference architecture touching every category should not win every award. The weighted danger score is used only as a tiebreaker.

- **The Green Curtain** is awarded to the highest-scoring achievement among those mentioning at least two sustainability-vocabulary terms.
- **The Full Stack** is awarded to the achievement with the highest overall weighted danger score across all eight categories.

### What This Is (And What It Is Not)

This is **keyword matching**, not semantic analysis. It detects the presence of specific technical terms that correspond to threat-relevant technologies. It does not interpret context. A project describing ISAC for industrial robotics scores identically to one describing ISAC for crowd tracking, because both are advancing the same underlying capability, regardless of stated intent.

### A Note on Intent

The engineers who built the railways did not intend the Holocaust. The mathematicians who developed linear programming did not intend to optimize bombing campaigns. The computer scientists who designed packet-switched networks did not intend mass surveillance.

In each case, the technology preceded its application by decades. In each case, the people who warned about the application were told they were being paranoid.

We are not accusing the researchers behind these 188 achievements of malicious intent. We have no reason to believe they are anything other than what they appear to be: scientists and engineers solving interesting technical problems, advancing the state of the art, publishing results, collecting grants.

**That is precisely the problem.**

An ISAC system that can detect a human heartbeat through a wall to locate a trapped firefighter uses the same physics, the same signal processing, and the same infrastructure as one that locates a protestor hiding in a building. The mathematics does not have a conscience. The antenna does not ask why. The edge server processing the radar return does not check whether the target consented to being sensed.

Infrastructure is not neutral because its creators are well-intentioned. Infrastructure is neutral in a different and more dangerous sense: **it works for whoever holds the keys.**

The history of technology is not a history of evil inventors. It is a history of capabilities that accumulated quietly, in research labs and standards bodies and funding calls, until one day a government or a corporation or a conflict discovered that the infrastructure was already there, already deployed, already impossible to remove, and that it could be turned in an afternoon toward purposes its creators never imagined and would never have chosen.

6G is being built now. The standards are being written now. The keys have not yet been handed to anyone in particular.

**This is the last moment at which the question of who holds them is still open.**

---

## Repository Structure

| File | Purpose |
|---|---|
| `index.html` | The live site — a self-contained, single-file HTML application. Contains the full scored dataset inlined as JSON. |
| `template.html` | The UI shell used by `score_achievements.py`. Contains a `__DATA_JSON__` placeholder that gets replaced with live data. |
| `score_achievements.py` | The scoring engine. Reads the official SNS JU CSV, scores each achievement, and injects the result into the template. |
| `generate_slides.py` | Generates the 14-slide Instagram carousel (PNG, 1080x1080) for social distribution. |
| `trophy.svg` / `trophy.png` | The trophy icon used in the cover slide and the live site. |
| `slides/` | Output folder for the generated carousel images. |

---

## GitHub Pages Setup

`index.html` is a **self-contained, zero-dependency static file**. It has no build step, no external assets, and no server-side requirements. To publish it on GitHub Pages:

1. Push this repository to GitHub.
2. Go to **Settings → Pages**.
3. Set **Source** to `Deploy from a branch` → `main` → `/ (root)`.
4. GitHub Pages will serve `index.html` at `https://stop6g.github.io/6G-THREAT-AWARDS/`.

The file is deliberately self-contained so that it cannot be trivially disrupted by external CDN failures, account suspensions, or supply-chain attacks. The trophy icon is loaded as a local SVG. The dataset is inlined as a `<script>` block. The CSS is embedded. It should render identically whether opened from a web server, a file:// URL, or a mirror.

---

## License

The code in this repository is released into the public domain via **CC0 1.0 Universal**. The underlying data is sourced from official EU publications and remains subject to their respective terms. Do whatever you want with this. Mirror it, fork it, print it, shout it from rooftops. We do not require attribution. We require that people read it.

---

**stop6g.eu**  
*#stop6G  #6G  #Surveillance  #Privacy*
