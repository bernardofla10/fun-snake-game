# Snake Game

## 1. Product Vision

Build a modern version of the classic Snake game in Python that is simple and fun enough to be played by a child, while being engineered with enough quality, structure and documentation to serve as a software engineering portfolio project.

The project should preserve the simplicity of the original Snake game while gradually introducing additional game modes, mechanics and technical features.

---

## 2. Primary Users

### Primary user

A casual player who wants a simple and enjoyable Snake game.

### Secondary audience

Developers and recruiters visiting the GitHub repository who want to understand how the project was designed, implemented, tested and maintained.

---

## 3. Product Goals

The game should:

* be easy to launch and play;
* have intuitive controls;
* provide responsive gameplay;
* preserve the core mechanics of classic Snake;
* progressively introduce additional gameplay features;
* keep game logic separated from graphical rendering where practical;
* have automated tests for important game rules;
* have clear documentation;
* follow a professional Git workflow;
* remain simple enough for the architecture to be easily understood.

---

## 4. MVP — v0.1

The first playable version must support:

* game window;
* snake rendering;
* keyboard controls using arrow keys and/or WASD;
* continuous snake movement;
* food spawning;
* snake growth after eating food;
* score counting;
* collision with walls;
* collision with the snake's own body;
* game-over state;
* game restart.

No additional gameplay features are required for v0.1.

---

## 5. Delivered Post-MVP Features

### 008 — Responsive Fullscreen Board

The game now:

* starts in fullscreen at the desktop resolution;
* preserves its fixed 32×24 logical grid while scaling square cells;
* centers the board inside a garden-themed frame;
* displays score in a separate responsive HUD;
* supports F11 fullscreen toggling and a resizable window;
* preserves the active match across display changes.

### 009 — Screens and Navigation

The game now:

* opens with a short, skippable welcome animation;
* provides a mouse-operated Home menu for playing, previewing styles, or exiting;
* previews the default Snake and apple in separate Style tabs;
* shows restart and Home actions over the frozen final board;
* keeps application navigation separate from the match rules.

### 010 — Local Profiles

The game now:

* requires a local profile selection after every Welcome;
* creates and lists any number of profiles through a paginated mouse interface;
* stores profile identity and initial progress in a local SQLite database;
* gives each new profile the default Snake and apple;
* supports switching profiles from Home and retrying storage failures.

### 011 — Coins and Purchases

The game now:

* grants one persistent profile coin for every food consumed;
* distinguishes current score, match earnings, and total saved balance;
* shows the balance throughout menus, gameplay, and Game Over;
* supports atomic purchases with typed failure results and no negative balances;
* recovers failed coin credits without duplicating rewards.

---

## 6. Future Features

Potential post-MVP features include:

* progressive difficulty;
* increasing snake speed;
* obstacles;
* different food types;
* power-ups;
* difficulty selection;
* pause system;
* high-score persistence;
* sound effects;
* music;
* themes or skins;
* animated UI;
* multiple game modes;
* replay system;
* AI-controlled Snake.

These features are candidates rather than requirements and will receive individual specifications before implementation.

---

## 7. Engineering Goals

The project should demonstrate:

* Python project organization;
* separation of concerns;
* object-oriented and/or domain-oriented design where useful;
* Git version control;
* feature branches;
* meaningful commits;
* automated tests;
* linting and formatting;
* CI using GitHub Actions;
* project documentation;
* incremental software delivery;
* AI-assisted development with human review.

---

## 8. Non-Goals for the MVP

The first version will not attempt to include:

* online multiplayer;
* user accounts;
* databases;
* networking;
* cloud infrastructure;
* microservices;
* complex game engines;
* generative AI.

These could add complexity without improving the main learning objective.

---

## 9. Success Criteria for v0.1

The MVP is complete when:

1. the game starts successfully;
2. the player can control the snake;
3. food can be consumed;
4. consuming food increases snake length and score;
5. collisions correctly trigger game over;
6. the game can be restarted;
7. core game-rule tests pass;
8. linting passes;
9. CI passes;
10. another person can clone the repository and run the game using the README instructions.
