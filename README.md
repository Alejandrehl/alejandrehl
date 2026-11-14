<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/hero-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/hero-light.svg">
  <img src="./assets/hero-light.svg" width="100%" alt="Alejandro in Claude Code: diagnose before you build, read the whole system from the database to the business outcome, plan reviewed, independent review passed, ship it. Beside it, a merge request moves through its own ephemeral environment and review to production.">
</picture>

# Alejandro Hernández&nbsp;Lara

**Senior&nbsp;Software&nbsp;Architect · Platform&nbsp;Engineering · Applied&nbsp;AI**

*I build the platforms engineering teams ship on, and the AI tooling that makes them faster.*

[alehernandez.cl](https://www.alehernandez.cl) &nbsp;·&nbsp; [LinkedIn](https://www.linkedin.com/in/alejandrehl/) &nbsp;·&nbsp; [Email](mailto:alejandrehl@icloud.com) &nbsp;·&nbsp; Santiago,&nbsp;Chile

</div>

---

I design and build internal platforms and AI tooling for engineering teams: self-service infrastructure, ephemeral environments, and agents that run in production. I read a system end to end, from the database to the business outcome, and fix root causes instead of symptoms.

## Selected work

### Ephemeral environments, per merge&nbsp;request

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/work-ephemeral-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/work-ephemeral-light.svg">
  <img src="./assets/work-ephemeral-light.svg" width="100%" alt="Diagram: each merge request gets its own ephemeral environment on Cloud Run, Cloud SQL, and DNS; a time to live runs down and the environment is torn down automatically.">
</picture>

Designed and built the core of an ephemeral-environments platform on GCP for a leading Latin American airline. Every merge request gets its own running environment, provisioned on demand and torn down automatically.

`Cloud Run` `Cloud SQL` `Terraform Cloud API` `Automatic DNS` `TTL cleanup`

### A shared AI-agent workspace for a platform team

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/work-agents-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/work-agents-light.svg">
  <img src="./assets/work-agents-light.svg" width="100%" alt="Diagram: engineers on a platform team work from one shared Claude Code workspace with reusable agent skills, MCP servers, and CI quality gates; every change leaves with its gates green.">
</picture>

Built the Claude Code workspace a platform-engineering team works from: reusable agent skills, MCP servers, and CI quality gates. Recognized as the technical reference for generative AI on that engagement.

`Claude Code` `MCP` `Agent skills` `CI gates`

### Self-service change data capture over&nbsp;MCP

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/work-cdc-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/work-cdc-light.svg">
  <img src="./assets/work-cdc-light.svg" width="100%" alt="Diagram: a team asks an MCP server for change data capture; the server checks the team's authorization, writes an audit entry, and enables CDC on PostgreSQL, whose change events then stream out.">
</picture>

Led the production rollout of an MCP server that lets teams set up PostgreSQL change data capture through self-service, with per-team authorization and audit logging.

`Python` `FastAPI` `PostgreSQL` `MCP`

### Banking at national scale

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/work-bank-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/work-bank-light.svg">
  <img src="./assets/work-bank-light.svg" width="100%" alt="Diagram: solution architecture for a bank's mobile app and website, and the bank's email delivery migrated from a legacy server to AWS SES, with messages flowing out to customers.">
</picture>

Designed solution architecture for the mobile app and website of the bank with the most customers in Chile, and migrated the bank's email delivery to AWS SES.

`Solution architecture` `AWS` `AWS SES`

## How I work

- **Diagnose first.** Read the code, the data, and the operations, and find the root cause before writing anything.
- **Plan, then review.** Non-trivial changes start as a reviewed plan and ship only after an independent review and green CI.
- **No deferred fixes.** No placeholders and no "later" TODOs; the docs match the system.

[Claude Code](https://claude.com/claude-code) is my primary environment: I orchestrate agents to design, build, modernize, and audit software with the same rigor.

## Stack

<table>
<tr><td><b>Cloud &amp; data</b></td><td><code>GCP</code> <code>AWS</code> <code>Terraform</code> <code>Docker</code> <code>PostgreSQL</code> <code>MongoDB</code> <code>Railway</code></td></tr>
<tr><td><b>AI</b></td><td><code>Claude</code> <code>MCP</code> <code>OpenAI</code></td></tr>
<tr><td><b>Languages</b></td><td><code>TypeScript</code> <code>Python</code> <code>Go</code> <code>PHP</code> <code>Dart</code></td></tr>
<tr><td><b>Frameworks</b></td><td><code>NestJS</code> <code>FastAPI</code> <code>Next.js</code> <code>React</code> <code>Laravel</code> <code>React Native</code> <code>Flutter</code></td></tr>
</table>

For my own deployments I use **Railway**.

[![Deploy on Railway with referral code KJa0VN](https://img.shields.io/badge/Deploy_on_Railway-referral_code_KJa0VN-D97757?style=flat-square&logo=railway&logoColor=white&labelColor=0A0A0A)](https://railway.com?referralCode=KJa0VN)

> Use referral code **`KJa0VN`** ([railway.com?referralCode=KJa0VN](https://railway.com?referralCode=KJa0VN)) and we both get credit.

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

---

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/cta-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/cta-light.svg">
  <img src="./assets/cta-light.svg" width="100%" alt="A Claude Code prompt reads: let's build something that has to work in production. Below it, alejandrehl@icloud.com and linkedin.com/in/alejandrehl.">
</picture>

<div align="center">

**[Let's talk](mailto:alejandrehl@icloud.com)** &nbsp;·&nbsp; [LinkedIn](https://www.linkedin.com/in/alejandrehl/)

*Zero tolerance for mediocrity.*

</div>
