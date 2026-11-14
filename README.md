<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/hero-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/hero-light.svg">
  <img src="./assets/hero-light.svg" width="100%" alt="Alejandro in Claude Code: diagnose before you build, read the whole system from the database to the business outcome, plan reviewed, independent review passed, ship it. Beside it, a list of shipped work checks off: ephemeral environments, an agent workspace, change data capture over MCP, and solution architecture for a bank.">
</picture>

# Alejandro Hernández&nbsp;Lara

**Senior&nbsp;Software&nbsp;Architect**<br>
Platform&nbsp;Engineering · Applied&nbsp;AI

*I build the platforms that engineering teams ship on, and the AI tooling they build with.*

[alehernandez.cl](https://www.alehernandez.cl) &nbsp;·&nbsp; [LinkedIn](https://www.linkedin.com/in/alejandrehl/) &nbsp;·&nbsp; [Email](mailto:alejandrehl@icloud.com)

</div>

I have shipped internal platforms, AI agent tooling, and solution architecture to production for a leading Latin American airline and for the bank with the most customers in Chile.

## Selected work

### Ephemeral environments, per merge&nbsp;request

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/work-ephemeral-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/work-ephemeral-light.svg">
  <img src="./assets/work-ephemeral-light.svg" width="100%" alt="Diagram: each merge request gets its own ephemeral environment on Cloud Run, Cloud SQL, and DNS; a time to live (TTL) runs down and the environment is torn down automatically.">
</picture>

Designed and built the core of an ephemeral-environments platform on GCP for a leading Latin American airline. Every merge request gets its own running environment, provisioned on demand and torn down automatically.

<code>GCP</code> <code>Cloud&nbsp;Run</code> <code>Cloud&nbsp;SQL</code> <code>Terraform&nbsp;Cloud&nbsp;API</code>

### A shared AI-agent workspace for a platform&nbsp;team

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/work-agents-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/work-agents-light.svg">
  <img src="./assets/work-agents-light.svg" width="100%" alt="Diagram: engineers on a platform team work from one shared Claude Code workspace with reusable agent skills, MCP servers, and CI quality gates.">
</picture>

Built the Claude Code workspace a platform engineering team works from: reusable agent skills, MCP servers, and CI quality gates. I served as the technical reference for generative AI there.

<code>Claude&nbsp;Code</code> <code>MCP</code> <code>Agent&nbsp;Skills</code>

### Self-service change data capture over&nbsp;MCP

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/work-cdc-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/work-cdc-light.svg">
  <img src="./assets/work-cdc-light.svg" width="100%" alt="Diagram: a team asks an MCP server for change data capture; the server checks the team's authorization, writes an audit entry, and enables CDC on PostgreSQL, whose change events then stream out.">
</picture>

Led the production rollout of an MCP server that lets teams set up PostgreSQL change data capture through self-service, with per-team authorization and audit logging.

<code>Python</code> <code>FastAPI</code> <code>PostgreSQL</code> <code>MCP</code>

### Banking at national&nbsp;scale

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/work-bank-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/work-bank-light.svg">
  <img src="./assets/work-bank-light.svg" width="100%" alt="Diagram: a bank's mobile app and website served by backend services, and the bank's email delivery migrated from its previous setup to Amazon SES, with messages flowing out to customers.">
</picture>

Designed solution architecture for the mobile app and website of the bank with the most customers in Chile, and coordinated the migration of the bank's email delivery to Amazon SES.

<code>AWS</code> <code>Amazon&nbsp;SES</code>

## How I work

- **Diagnose first.** Find the root cause in the code, the data, and the operations before changing anything.
- **Plan, then review.** Non-trivial changes start as a reviewed plan and ship only after an independent review and green CI.
- **No deferred fixes.** No placeholders and no TODOs for later; the docs match the system.

[Claude Code](https://claude.com/claude-code) is my primary environment: I orchestrate agents to design, build, modernize, and audit software under these same three rules.

## Stack

<table>
<tr><td><b>Cloud &amp; data</b></td><td><code>GCP</code> <code>AWS</code> <code>Terraform</code> <code>Docker</code> <code>PostgreSQL</code> <code>MongoDB</code> <code>Railway</code></td></tr>
<tr><td><b>AI</b></td><td><code>Claude</code> <code>MCP</code></td></tr>
<tr><td><b>Languages</b></td><td><code>TypeScript</code> <code>Python</code> <code>Go</code> <code>PHP</code> <code>Dart</code></td></tr>
<tr><td><b>Frameworks</b></td><td><code>NestJS</code> <code>FastAPI</code> <code>Next.js</code> <code>React</code> <code>Laravel</code> <code>React&nbsp;Native</code> <code>Flutter</code></td></tr>
</table>

[![Deploy on Railway with referral code KJa0VN](https://img.shields.io/badge/Deploy_on_Railway-referral_code_KJa0VN-D97757?style=flat-square&logo=railway&logoColor=white&labelColor=0A0A0A)](https://railway.com?referralCode=KJa0VN)

I deploy my own projects on **Railway**. Sign up with referral code **`KJa0VN`** at [railway.com](https://railway.com?referralCode=KJa0VN) and we both get credit.

## Activity

<div align="center">

[![Followers](https://img.shields.io/github/followers/Alejandrehl?style=flat-square&logo=github&logoColor=white&label=Followers&labelColor=0A0A0A&color=1A1A1A)](https://github.com/Alejandrehl?tab=followers)
[![Public Repos](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fapi.github.com%2Fusers%2FAlejandrehl&query=%24.public_repos&style=flat-square&logo=github&logoColor=white&label=Public%20Repos&labelColor=0A0A0A&color=1A1A1A)](https://github.com/Alejandrehl?tab=repositories)

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Alejandrehl/alejandrehl/output/github-contribution-grid-snake-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/Alejandrehl/alejandrehl/output/github-contribution-grid-snake.svg">
  <img alt="Alejandro's contribution graph as a snake game" src="https://raw.githubusercontent.com/Alejandrehl/alejandrehl/output/github-contribution-grid-snake.svg">
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
