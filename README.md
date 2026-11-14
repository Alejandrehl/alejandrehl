<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/hero-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/hero-light.svg">
  <img src="./assets/hero-light.svg" width="100%" alt="A Claude Code session: diagnose before you build, read the whole system from the database to the business outcome, plan reviewed, independent review passed, ship it. Beside it, a list of shipped work checks off: platform tooling, an agent workspace, mobile apps, a production ERP, and a side project.">
</picture>

# Alejandro&nbsp;Exequiel Hernández&nbsp;Lara

**Senior&nbsp;Software&nbsp;Architect**<br>
Platform&nbsp;Engineering · Applied&nbsp;AI

*I build the platforms that engineering teams ship on, and whole products, from the database to the app store.*

[alehernandez.cl](https://www.alehernandez.cl) &nbsp;·&nbsp; [LinkedIn](https://www.linkedin.com/in/alejandrehl/) &nbsp;·&nbsp; [Email](mailto:alejandrehl@icloud.com)

</div>

## Platform engineering

Internal platforms and AI agent tooling I built and shipped for a leading Latin American airline.

### Ephemeral environments per merge&nbsp;request

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/work-ephemeral-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/work-ephemeral-light.svg">
  <img src="./assets/work-ephemeral-light.svg" width="100%" alt="Diagram: each merge request gets its own ephemeral environment on Cloud Run, Cloud SQL, and DNS; a time to live (TTL) runs down and the environment is torn down automatically.">
</picture>

Designed and built the core of an ephemeral-environments platform on GCP. Every merge request gets its own running environment, provisioned on demand and torn down automatically.

<code>GCP</code> <code>Cloud&nbsp;Run</code> <code>Cloud&nbsp;SQL</code> <code>Terraform&nbsp;Cloud&nbsp;API</code>

### Shared AI agent workspace for a platform&nbsp;team

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/work-agents-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/work-agents-light.svg">
  <img src="./assets/work-agents-light.svg" width="100%" alt="Diagram: engineers on a platform team work from one shared Claude Code workspace with reusable agent skills, MCP servers, and CI quality gates.">
</picture>

Built the Claude Code workspace a platform engineering team works from: reusable agent skills, MCP servers, and CI quality gates. I was also the person the team turned to for generative AI.

<code>Claude&nbsp;Code</code> <code>MCP</code> <code>Agent&nbsp;Skills</code>

### Self-service change data capture over&nbsp;MCP

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/work-cdc-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/work-cdc-light.svg">
  <img src="./assets/work-cdc-light.svg" width="100%" alt="Diagram: a team asks an MCP server for change data capture; the server checks the team's authorization, writes an audit entry, and enables CDC on PostgreSQL, whose change events then stream out.">
</picture>

Led the production rollout of an MCP server that lets teams enable PostgreSQL change data capture on their own, with per-team authorization and audit logging.

<code>Python</code> <code>FastAPI</code> <code>PostgreSQL</code> <code>MCP</code>

## Products

Apps and systems I built or co-built, for clients and for myself.

### Mobile apps on both&nbsp;stores

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/work-mobile-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/work-mobile-light.svg">
  <img src="./assets/work-mobile-light.svg" width="100%" alt="Two phones. NutriCoach: a meal photo is scanned and logged, and its protein, carbs, and fat rings fill. An art marketplace: a gallery of artworks scrolls and one is saved to favorites.">
</picture>

**NutriCoach** is a nutrition and training tracker I built as its sole developer: snap a meal and it gets logged, and an optional coaching chat runs on Claude. [App&nbsp;Store](https://apps.apple.com/cl/app/nutricoach-calor%C3%ADas-y-entreno/id6790234920) · [Google&nbsp;Play](https://play.google.com/store/apps/details?id=cl.nutricoach.app)

<code>React&nbsp;Native</code> <code>Expo</code> <code>NestJS</code> <code>Prisma</code> <code>Claude&nbsp;API</code>

For an **art marketplace**, I was the main author of its Flutter app and co-authored its API and web front ends.

<code>Flutter</code> <code>Dart</code>

### Production ERP for a distribution&nbsp;company

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/work-erp-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/work-erp-light.svg">
  <img src="./assets/work-erp-light.svg" width="100%" alt="Diagram: an ERP dashboard for a distribution company, with modules for sales, inventory, customers, suppliers, payments, commissions, and dispatch; sales charts grow, documents arrive, and a pending sales order turns paid. A coverage-gate badge shows it is covered by tests.">
</picture>

Sales, inventory, customers, suppliers, payments, seller commissions, and delivery notes for a Chilean distribution company, in production with a coverage gate and its test suite running in CI.

<code>Laravel</code> <code>Filament</code> <code>MySQL</code> <code>Railway</code>

### micodigopostal.fun

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/work-postal-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/work-postal-light.svg">
  <img src="./assets/work-postal-light.svg" width="100%" alt="micodigopostal.fun: a search box looks up Arica, Santiago, Puerto Montt, and Punta Arenas in turn; a slot-machine counter rolls to each city's base postal code (1000000, 8320000, 5480000, 6200000) while a pin hops down Chile, drawn sideways from north to south.">
</picture>

A side project that went live: look up any Chilean postal code by municipality or street address, with a public API. [micodigopostal.fun](https://micodigopostal.fun)

<code>Astro</code> <code>NestJS</code> <code>Prisma</code> <code>PostgreSQL</code> <code>Railway</code>

## Stack

- <b>AI</b> &nbsp; <code>Claude&nbsp;API</code> <code>Claude&nbsp;Code</code> <code>MCP</code> <code>Agent&nbsp;Skills</code>
- <b>Languages</b> &nbsp; <code>TypeScript</code> <code>Python</code> <code>PHP</code> <code>Dart</code> <code>Go</code>
- <b>Frameworks</b> &nbsp; <code>NestJS</code> <code>FastAPI</code> <code>Next.js</code> <code>Astro</code> <code>React&nbsp;Native</code> <code>Expo</code> <code>Flutter</code> <code>Laravel</code> <code>Filament</code>
- <b>Cloud &amp; data</b> &nbsp; <code>GCP</code> <code>AWS</code> <code>Terraform</code> <code>Docker</code> <code>PostgreSQL</code> <code>MySQL</code> <code>MongoDB</code> <code>Railway</code>

[![Railway referral code KJa0VN](https://img.shields.io/badge/Railway-referral_code_KJa0VN-D97757?style=flat-square&logo=railway&logoColor=white&labelColor=0A0A0A)](https://railway.com?referralCode=KJa0VN)

I deploy my own projects on **Railway**. Sign up through [my referral link](https://railway.com?referralCode=KJa0VN) (code **`KJa0VN`**) and you get Railway credits.

## Activity

<div align="center">

[![Followers](https://img.shields.io/github/followers/Alejandrehl?style=flat-square&logo=github&logoColor=white&label=Followers&labelColor=0A0A0A&color=1A1A1A)](https://github.com/Alejandrehl?tab=followers)
[![Public Repos](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fapi.github.com%2Fusers%2FAlejandrehl&query=%24.public_repos&style=flat-square&logo=github&logoColor=white&label=Public%20Repos&labelColor=0A0A0A&color=1A1A1A)](https://github.com/Alejandrehl?tab=repositories)

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Alejandrehl/alejandrehl/output/github-contribution-grid-snake-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/Alejandrehl/alejandrehl/output/github-contribution-grid-snake.svg">
  <img alt="Contribution graph drawn as a snake game" src="https://raw.githubusercontent.com/Alejandrehl/alejandrehl/output/github-contribution-grid-snake.svg">
</picture>

</div>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/cta-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/cta-light.svg">
  <img src="./assets/cta-light.svg" width="100%" alt="A Claude Code prompt reads: let's build something that has to work in production.">
</picture>

<div align="center">

**[Let's talk](mailto:alejandrehl@icloud.com)** &nbsp;·&nbsp; [LinkedIn](https://www.linkedin.com/in/alejandrehl/)

*Zero tolerance for mediocrity.*

</div>
