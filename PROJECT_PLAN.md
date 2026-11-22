# Modern Military Tower Defence - Game Architecture & Project Plan

## 1. Project Overview
A fast-paced, modern military-themed Tower Defence game built in **Python (Pygame)**.
Designed specifically for zero-friction setup on **Windows**, with one-click bat launcher (`run.bat`), virtual environment scripts, and PyInstaller bundling support for standalone `.exe` distribution.

---

## 2. Directory & Module Structure

```
Game-tower-defence/
│
├── run.bat                 # 1-Click Windows execution launcher (auto-checks python/pygame)
├── build_exe.bat           # 1-Click Windows PyInstaller packager to build standalone .exe
├── requirements.txt        # Python dependencies (pygame >= 2.5.0)
├── main.py                 # Application entry point & game loop
├── README.md               # Project documentation & Windows quickstart guide
│
├── assets/                 # Generated audio/procedural visual resources
│   ├── sounds/             # Sound effects (synthesized / sound generation)
│   └── images/             # Sprites / icons (optional or generated dynamically)
│
└── src/                    # Core Game Architecture
    ├── __init__.py
    ├── config.py           # Window dimensions, colors, grid sizes, balance constants
    ├── sound.py            # Synthesized procedural audio (firing, explosions, alert SFX)
    ├── map_grid.py         # Grid, waypoint paths, tile management (buildable vs path)
    ├── enemy.py            # Enemy base class & subtypes (Scout, Humvee, APC, Heavy Tank, Boss)
    ├── tower.py            # Tower base class & subtypes:
    │                       #   - Vulcan Minigun (High fire rate, single target)
    │                       #   - Patriot Missile Launcher (Long range, Area of Effect splash)
    │                       #   - Heavy Sniper (Extreme range, armor piercing)
    │                       #   - Tesla / EMP Coil (Chain lightning, slowing/disabling)
    ├── projectile.py       # Bullets, homing rockets, sniper beams, electric arcs
    ├── wave_manager.py     # Wave progression, enemy spawning schedules, scaling logic
    ├── ui.py               # HUD (Cash, Lives, Wave, Timer, Tower Shop cards, Upgrade panel)
    └── game.py             # Top-level state machine (MENU, PLAYING, PAUSED, GAME_OVER, VICTORY)
```

---

## 3. Core Military Arsenal (Towers)

| Tower | Role | Damage Type | Target Priority | Special Ability |
|---|---|---|---|---|
| **Vulcan Gatling** | Anti-infantry / Rapid DPS | Kinetic (Single) | First / Lowest HP | Spins up fire rate |
| **Missile Battery** | Swarm control / Splash | Explosive (AoE) | Cluster / Strongest | Splash damage radius |
| **Heavy Anti-Materiel** | Elite / Boss Buster | Armor-Piercing | Strongest / Furthest | Ignores 50% armor, high critical |
| **EMP Shockwave** | Crowd control | Electrical (Chain/Slow) | Closest | Slows vehicles by 50% for 2s |

---

## 4. Hostile Military Forces (Enemies)

| Enemy Unit | Speed | Armor / HP | Threat Level | Special Trait |
|---|---|---|---|---|
| **Recon Bike / Drone** | Very Fast | Low | Early-Wave Scout | Hard to hit with slow rockets |
| **Armed Technical** | Medium-Fast | Moderate | Standard Skirmisher | Regular infantry support |
| **Armored APC** | Medium | High | Shielded Transport | Drops infantry or absorbs bullets |
| **Main Battle Tank** | Slow | Heavy Armor | Siege Breaker | Resists light gunfire |
| **Mobile Command Base** | Very Slow | Colossal | Boss Unit | Emits periodic repair pulse |

---

## 5. Key Windows Portability Features
1. **`run.bat`**: Double-clicking on Windows checks if Python is installed, creates `.venv` if missing, installs `pygame`, and launches `main.py`.
2. **Procedural Vector Sprites & Audio**: No external binary asset dependencies required to run right out of the box. Runs smoothly at 60 FPS on any Windows PC.
3. **Resizable & Scale-Aware**: Crisp UI fonts and high-DPI friendly window sizing (1280x720).
4. **`build_exe.bat`**: Bundles the game into `dist/ModernDefense.exe` with no Python installation needed by end users.
