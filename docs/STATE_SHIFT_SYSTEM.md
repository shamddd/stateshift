# STATE / SHIFT: Design System & Technical Architecture Specification

**Identity**: STATE / SHIFT
**Subject**: Sham Satish Thakare
**Research Paradigm**: Reliable Adaptive Intelligent Systems
**Core Vocabulary**: `REASON · ADAPT · VERIFY · RECOVER`
**Author**: Creative Architecture & Performance Engineering Agent
**Version**: 1.0.0 (Production Release)

---

## 1. Philosophical Foundation & Core Identity

STATE / SHIFT is designed not merely as a portfolio, but as a living representation of a research-engineering program.

The entire aesthetic and interaction grammar is anchored around:
- **State Invariance**: Systems operate under explicit state conditions rather than implicit assumptions.
- **Topological Transitions**: Navigating the portfolio shifts the underlying latent graph rather than rendering disconnected cards.
- **Uncertainty Calibration**: Visual motion communicates stability, perturbation, verification, and recovery.
- **Strict Empirical Truth**: Every metric, date, affiliation, and manuscript status is rigorously governed.

---

## 2. Visual & Design Grammar

### 2.1 Color Tokens
The color palette uses deep, restrained tones to evoke an experimental systems interface:

| Token Name | Dark Mode Value | Light Mode Value | Semantic Role |
|---|---|---|---|
| `--bg-primary` | `#07090e` | `#fafaf9` | Deep console base canvas |
| `--bg-surface` | `#0d121b` | `#f4f4f5` | Elevated state container panels |
| `--bg-panel` | `#121926` | `#e4e4e7` | Interactive sub-components |
| `--border-color` | `#1c2738` | `#cbd5e1` | Structural boundaries |
| `--text-primary` | `#f1f5f9` | `#09090b` | High-contrast editorial titles |
| `--text-muted` | `#94a3b8` | `#475569` | Research prose and abstracts |
| `--text-dim` | `#64748b` | `#64748b` | Telemetry labels and metadata |
| `--state-reason` | `#38bdf8` | `#0284c7` | Reasoning reliability & RLVR |
| `--state-adapt` | `#a855f7` | `#9333ea` | Representation geometry & plasticity |
| `--state-verify` | `#10b981` | `#059669` | Policy verification & invariants |
| `--state-recover`| `#f59e0b` | `#d97706` | Quorum adaptation & state recovery |

### 2.2 Typography Hierarchy
- **Display Typography**: `JetBrains Mono` / `Instrument Serif` pairing for high-discipline academic presence.
- **Prose & Body**: Clean `Inter` font with strict line-length constraints ($65\text{–}75$ characters per line) and optimized line-height ($1.6\text{–}1.7$).
- **Telemetry & Labels**: Monospace `JetBrains Mono` with uppercase tracking (`tracking-wider`, `tracking-widest`).

---

## 3. WebGL Latent Research Topology Architecture

The signature 3D WebGL scene (`components/webgl/ResearchTopologyCanvas.tsx`) renders the 6 research domains as an evolving graph in 3D projective space:

1. **Hardware Quality Tiers**:
   - **HIGH (Discrete GPU)**: 180 particles, full antialiasing, dynamic line buffer updates at $60\text{ fps}$.
   - **MEDIUM (Integrated GPU)**: 60 particles, reduced geometry subdivisions.
   - **LOW (Mobile)**: 30 particles, pixel ratio clamped to $1.0$.
   - **STATIC (Reduced Motion / Unsupported)**: Zero WebGL execution; replaced by a 2D SVG topological diagram.
2. **IntersectionObserver Throttling**: The rendering animation loop pauses completely whenever the canvas scrolls out of the viewport, eliminating unnecessary background GPU burn.
3. **Pointer Proximity Physics**: Raycasting calculates pointer distance to nodes, applying smooth spring-physics scale and rotation deformation rather than chaotic cursor-chasing particles.
4. **Accessible Text Equivalent**: Full screen-reader semantic DOM fallback included beneath canvas.

---

## 4. Motion Design System

All motion is purposeful and governed by standardized easing curves:

- **Micro-interactions** (`140ms`): Button hovers, toggle states.
- **Interaction Transitions** (`280ms`, `cubic-bezier(0.16, 1, 0.3, 1)`): Card expansion, dialog opens.
- **Section Reveals** (`600ms`, `cubic-bezier(0.16, 1, 0.3, 1)`): Scroll-triggered component reveals.
- **Cinematic Topology Shifts** (`1200ms`, `cubic-bezier(0.22, 1, 0.36, 1)`): WebGL domain morphing.

### Reduced Motion Mode
- Automatically synchronizes with OS preference (`prefers-reduced-motion: reduce`).
- Manual toggle available via Navbar, Command Palette (`⌘K`), and system controls.
- Instantly disables WebGL, parallax, cursor motion, and smooth scrolling while preserving 100% visual styling.

---

## 5. Command Palette (`⌘K`) Specification

- Accessible via `⌘K` (Mac), `Ctrl+K` (Linux/Windows), or `/` key.
- Quick jumps to research domains (`01 / REASON`, `02 / ADAPT`, `03 / VERIFY`, `04 / RECOVER`).
- Fuzzy search across all 7 research projects, 7 manuscripts, and technical essays.
- Built-in system telemetry Easter eggs (`trace`, `rollback`, `recover`).
- Full keyboard trap and `Escape` dismissal.

---

## 6. GitHub Profile Integration & SVG Assets

GitHub profile README renders identical identity without arbitrary JavaScript:
- `assets/github/state-shift-hero.svg`: Dark/light mode compatible animated SVG with pulsing domain nodes and moving topological dashed edges.
- `assets/github/research-map.svg`: 4-column breakdown of the core research paradigms.
- `assets/github/system-flow.svg`: Deterministic 6-stage agent safety interception flow.
