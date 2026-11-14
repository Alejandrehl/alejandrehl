<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/hero-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/hero-light.svg">
  <img src="./assets/hero-dark.svg" width="820" alt="Alejandro in Claude Code: diagnose before you build, plan reviewed, independent review passed, ship it. Beside it, a merge request moving through its own ephemeral environment and review to production.">
</picture>

# Alejandro Hernández Lara

**Senior Software Architect · Platform Engineering · Applied AI**

*I build the platforms engineering teams ship on, and the AI tooling that makes them faster.*

<p>
  <a href="https://www.alehernandez.cl"><img src="https://img.shields.io/badge/alehernandez.cl-0A0A0A?style=flat-square" alt="alehernandez.cl"></a>
  <a href="https://www.linkedin.com/in/alejandrehl/"><img src="https://img.shields.io/badge/LinkedIn-alejandrehl-0A66C2?style=flat-square" alt="LinkedIn"></a>
  <a href="mailto:alejandrehl@icloud.com"><img src="https://img.shields.io/badge/Email-let's_talk-D97757?style=flat-square&logo=icloud&logoColor=white" alt="Email"></a>
  <img src="https://img.shields.io/badge/Santiago-Chile%20%F0%9F%87%A8%F0%9F%87%B1-0A0A0A?style=flat-square&logo=googlemaps&logoColor=white" alt="Based in Santiago, Chile">
</p>

</div>

---

I design and build internal platforms and AI tooling for engineering teams: self-service infrastructure, ephemeral environments, and agents that run in production. I read a system end to end, from the database to the business outcome, and fix root causes instead of symptoms.

## Selected work

<table>
<tr>
<td width="50%" valign="top">

#### 🌱 Ephemeral environments, per merge request

Designed and built the core of an ephemeral-environments platform on GCP for a leading Latin American airline. Every merge request gets its own running environment, provisioned on demand and torn down automatically.

`Cloud Run` `Cloud SQL` `Terraform Cloud API` `Automatic DNS` `TTL cleanup`

</td>
<td width="50%" valign="top">

#### 🤖 A shared AI-agent workspace for a platform team

Built the Claude Code workspace a platform-engineering team works from: reusable agent skills, MCP servers, and CI quality gates. Recognized as the technical reference for generative AI on that engagement.

`Claude Code` `MCP` `Agent skills` `CI gates`

</td>
</tr>
<tr>
<td width="50%" valign="top">

#### 🔄 Self-service change data capture over MCP

Led the production rollout of an MCP server that lets teams set up PostgreSQL change data capture through self-service, with per-team authorization and audit logging.

`Python` `FastAPI` `PostgreSQL` `MCP`

</td>
<td width="50%" valign="top">

#### 🏦 Banking at national scale

Designed solution architecture for the mobile app and website of the bank with the most customers in Chile, and migrated the bank's email delivery to AWS SES.

`Solution architecture` `AWS` `AWS SES`

</td>
</tr>
</table>

## How I work

- **Diagnose first.** Read the code, the data, and the operations, and find the root cause before writing anything.
- **Plan, then review.** Non-trivial changes start as a reviewed plan and ship only after an independent review and green CI.
- **No deferred fixes.** No placeholders and no "later" TODOs; the docs match the system.

[Claude Code](https://claude.com/claude-code) is my primary environment: I orchestrate agents to design, build, modernize, and audit software with the same rigor.

## Stack

<table>
<tr>
<td><b>Cloud &amp; data</b></td>
<td>

![GCP](https://img.shields.io/badge/GCP-4285F4?style=flat-square&logo=googlecloud&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-232F3E?style=flat-square)
![Terraform](https://img.shields.io/badge/Terraform-7B42BC?style=flat-square&logo=terraform&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=flat-square&logo=mongodb&logoColor=white)
![Railway](https://img.shields.io/badge/Railway-0B0D0E?style=flat-square&logo=railway&logoColor=white)

</td>
</tr>
<tr>
<td><b>AI</b></td>
<td>

![Anthropic Claude](https://img.shields.io/badge/Claude-D97757?style=flat-square&logo=anthropic&logoColor=white)
![MCP](https://img.shields.io/badge/MCP-0A0A0A?style=flat-square&logo=modelcontextprotocol&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=flat-square)

</td>
</tr>
<tr>
<td><b>Languages</b></td>
<td>

![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Go](https://img.shields.io/badge/Go-00ADD8?style=flat-square&logo=go&logoColor=white)
![PHP](https://img.shields.io/badge/PHP-777BB4?style=flat-square&logo=php&logoColor=white)
![Dart](https://img.shields.io/badge/Dart-0175C2?style=flat-square&logo=dart&logoColor=white)

</td>
</tr>
<tr>
<td><b>Frameworks</b></td>
<td>

![NestJS](https://img.shields.io/badge/NestJS-E0234E?style=flat-square&logo=nestjs&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-000000?style=flat-square&logo=nextdotjs&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=flat-square&logo=react&logoColor=61DAFB)
![Laravel](https://img.shields.io/badge/Laravel-FF2D20?style=flat-square&logo=laravel&logoColor=white)
![React Native](https://img.shields.io/badge/React%20Native-20232A?style=flat-square&logo=react&logoColor=61DAFB)
![Flutter](https://img.shields.io/badge/Flutter-02569B?style=flat-square&logo=flutter&logoColor=white)

</td>
</tr>
</table>

For my own deployments I use **Railway**.

<a href="https://railway.com?referralCode=KJa0VN"><img src="https://img.shields.io/badge/Deploy_on_Railway-referral_code_KJa0VN-8B5CF6?style=for-the-badge&logo=railway&logoColor=white" alt="Deploy on Railway with referral code KJa0VN"></a>

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

<div align="center">

**Building something that has to work in production?** [Let's talk](mailto:alejandrehl@icloud.com) · [LinkedIn](https://www.linkedin.com/in/alejandrehl/)

*Zero tolerance for mediocrity.*

</div>
