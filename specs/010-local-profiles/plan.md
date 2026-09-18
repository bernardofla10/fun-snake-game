# Implementation Plan

## Persistence

Add pygame-independent profile value objects, validation, platform path
resolution, and a SQLite store. Schema version 1 will contain `schema_version`,
`profiles`, and `purchases`; a normalized unique name column will enforce the
same rule used by application validation. Profile creation will insert the
profile and its default Snake/apple purchases in one transaction.

Connections will be short lived, enable foreign keys, and translate filesystem
or SQLite failures into a typed storage error. Empty databases will be initialized
idempotently; databases declaring another version will be rejected.

## Application Flow

Inject the profile store into the application controller. Extend the state model
with Profile Select and Storage Error and keep the active profile, profile page,
creation draft, inline validation message, and failed storage operation in the
controller. Completing Welcome loads profiles instead of entering Home.

Profile creation will validate through the store, select successful profiles,
and retain the draft for validation or retry failures. Switching profile will
clear the active profile and active match before returning to selection.

## UI and Input

Replace action-only button results with typed UI commands containing an optional
integer payload. Add profile actions, four-card pagination, an inline name form,
Home profile identity and Switch Profile, and a storage-error screen.

Use pygame `TEXTINPUT` only while the inline form is open, Backspace for editing,
and mouse buttons for all form and navigation actions. Rebuild responsive geometry
after display changes as before.

## Testing and Documentation

Use temporary SQLite paths for schema, validation, transaction, ordering,
reopening, and version tests. Add controller, command payload, pagination, text
input, rendering, retry, and lifecycle coverage while retaining all existing
regressions.

Document the launch flow, default data location, profile controls, and delivered
roadmap status. Run Ruff and pytest, review the complete diff, split logical
commits, and open a pull request to `main`.
