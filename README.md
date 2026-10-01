# TenOrNot

Is it a 10 or not? Estimate your card's grade before you send it in.

TenOrNot is a phone-friendly web app for Pokémon collectors. Photograph the front and back of a card and it measures centering against PSA's standards, telling you the highest grade the card can get before you pay to submit. v2 adds AI scoring of edges, corners, and surface, grade odds ("60% PSA 10, 35% PSA 9"), and a submit-or-not calculation in dollars.

> Estimates only. Not affiliated with or endorsed by PSA.

**Status:** Early design. See [docs/prd.md](docs/prd.md) for what it does and why.

## Stack
Vue 3 + TypeScript frontend, Python FastAPI + OpenCV backend on Google Cloud Run, Firebase Auth. Reasoning in [ADR 0002](docs/adr/0002-vue-fastapi-cloud-run-firebase.md).

## Prerequisites
- Python 3.12+ and [uv](https://docs.astral.sh/uv/)
- Node.js 20+
- A Firebase project (Google and GitHub sign-in enabled)
- Google Cloud SDK (`gcloud`) for deploying

## How we work
Spec Kit for design, Superpowers for implementation. See [CLAUDE.md](CLAUDE.md).
