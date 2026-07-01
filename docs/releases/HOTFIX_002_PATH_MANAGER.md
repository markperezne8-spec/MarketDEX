# Hotfix 002 - Project Path Manager

## Purpose
Replace fragile relative paths with project-root based paths.

## New Module
app/core/paths.py

## Benefits
- Works from VS Code
- Works from launcher.py
- Works regardless of current working directory
- Centralized path management

## Future Rule
Import paths from app.core.paths instead of creating Path("...") throughout the codebase.
