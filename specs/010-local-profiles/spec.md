# 010 — Local Profiles

## Goal

Add local player profiles backed by SQLite so each player can select an identity
and retain the initial progress fields needed by later economy and cosmetic
features.

## Functional Requirements

### FR-001 — Profile Selection

After Welcome, every launch must show Profile Select before Home. Selecting an
existing profile must make it active and open Home.

### FR-002 — Profile Creation

Profile Select must provide an inline form for creating a profile. Successful
creation must activate the new profile and open Home.

### FR-003 — Name Validation

Names must be trimmed, contain 1 through 20 characters, and be unique without
case distinctions. Unicode-equivalent names must use a normalized comparison
key. Invalid and duplicate names must show an inline message without leaving the
form.

### FR-004 — Initial Progress

Every new profile must start with zero coins, the Snake and apple equipped, and
the Snake and apple recorded as acquired items.

### FR-005 — Persistent Storage

Profiles and their initial progress must remain available after closing and
reopening the database. Storage must use SQLite from the Python standard library.

### FR-006 — Profile Browsing

Profile Select must show at most four profile cards per page, ordered by name.
Previous and Next mouse buttons must expose every stored profile and be disabled
when no adjacent page exists.

### FR-007 — Switch Profile

Home must identify the active profile and provide a mouse-operated Switch Profile
action that clears the active selection and returns to Profile Select.

### FR-008 — Storage Failure

An initialization or creation failure must show a responsive error screen with
Retry and Exit. Retry must repeat the failed operation.

### FR-009 — Platform Data Location

Production storage must use the operating system's user-data directory: honor
`XDG_DATA_HOME` on Linux, use `LOCALAPPDATA` on Windows, and use
`~/Library/Application Support` on macOS.

## Engineering Requirements

### ER-001

Persistence and profile validation must not depend on pygame.

### ER-002

The database path must be injectable, and automated tests must use temporary
paths only.

### ER-003

Schema creation and profile creation must be transactional and enable SQLite
foreign-key enforcement.

### ER-004

The database must contain an explicit schema version and reject unsupported
versions without modifying them.

### ER-005

Dynamic profile cards must emit typed UI commands carrying profile identifiers.

### ER-006

Existing navigation, gameplay, fullscreen, resizing, timing, and Game Over
behavior must remain stable.

## Acceptance Criteria

Given a launch completes Welcome, Profile Select appears even when profiles
already exist.

Given no profile exists, a player can open the inline form, create one, and reach
Home with that profile active.

Given `Ana` exists, attempts to create `ana` or a Unicode-equivalent spelling are
rejected as duplicates.

Given more than four profiles, all profiles can be reached with Previous and
Next, and unavailable directions are disabled.

Given an active profile, Switch Profile returns to selection and prevents Home,
Style, or Play until another profile is selected.

Given the database is reopened, all profiles and their default progress remain.

Given storage fails, the player can retry or exit while the window remains
responsive.

## Non-Goals

Do not implement:

- deletion, passwords, avatars, or a maximum profile count;
- automatic selection of the last-used profile;
- earning or spending coins;
- purchasing or equipping alternative cosmetics;
- keyboard menu navigation or mouse-wheel scrolling;
- schema migrations beyond schema version 1.
