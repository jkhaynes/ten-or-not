# 0002. Stack: Vue + FastAPI/OpenCV on Cloud Run, Firebase Auth

**Status:** Accepted
**Date:** 2026-10-01

## Context
v1 measures card centering from phone photos and must be deployed so it works from a phone anywhere, on a budget of a few dollars a month, with access limited to an allowlist. v2 adds AI condition scoring and grade odds. The builder is strongest in .NET/C# and Angular, wants to build Python/AI experience, and values the right tool for the job. The target employer (Collectors) lists JavaScript, TypeScript, and Vue.js. Photos are not stored.

## Options Considered
1. **Backend**
   - **Python (FastAPI + OpenCV)**: the standard computer-vision toolkit; the AI ecosystem v2 needs is Python-first. New language for the builder.
   - **.NET API + Python service**: familiar stack, but two backends to deploy, secure, and pay for.
   - **In-browser OpenCV.js**: free to run, but awkward to debug, builds no Python skills, and v2 needs a server anyway.
2. **Frontend**
   - **Angular**: strongest skill.
   - **React**: largest job market, steeper switch from Angular.
   - **Vue 3 + TypeScript**: matches the target employer's stack; templates are close to Angular's, so it's quick to learn.
3. **Hosting**
   - **Google Cloud Run + Cloudflare Pages**: scales to zero, about $0 at this scale, a few seconds of startup after idle.
   - **Azure Container Apps**: similar, but no existing Azure preference.
   - **Fly.io / Render**: Render's free tier wakes too slowly; Fly costs about $2–5/month.
   - **VPS**: always on, but the builder maintains the server.
4. **Sign-in**
   - **Firebase Authentication**: free, Google + GitHub providers, part of Google Cloud.
   - **Custom OAuth in FastAPI**: the most security-sensitive code to own.
   - **Clerk / Auth0**: an extra vendor, and the allowlist lives in their dashboard.

## Decision
- **Frontend:** Vue 3 + TypeScript (Vite), hosted on Cloudflare Pages.
- **Backend:** Python FastAPI + OpenCV in a container on Google Cloud Run.
- **Sign-in:** Firebase Authentication (Google, GitHub). The backend verifies Firebase tokens and enforces an email allowlist from an environment variable.
- **Storage:** no database in v1; photos are processed in memory and never stored.

## Consequences
- Image and AI work sits in the Python ecosystem, so v2 builds on the same codebase.
- The builder is learning Python and Vue at the same time; keeping the frontend small limits the cost.
- The first request after an idle period has a few seconds of Cloud Run startup.
- Changing the allowlist means a redeploy. Move it to Firestore if v2 brings in a database.
- No stored photos means no saved history (matches the non-goals) and no user photos to protect.
