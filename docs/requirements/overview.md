# Insider - Product Insights Tracker

## Problem Statement

Developer Advocates gather valuable product insights from community interactions, conference talks, support channels, and user feedback. These insights often get lost across scattered documents, Slack messages, and personal notes - never reaching the Product Managers who need them to make informed decisions.

## Solution

Insider is a centralized platform where Developer Advocates can capture, organize, and share product insights with Product Managers.

## Goals

1. **Capture insights quickly** - Low friction input so insights are recorded in the moment
2. **Organize effectively** - Tag, categorize, and link insights to products/features
3. **Surface patterns** - Make it easy to see recurring themes across multiple insights
4. **Share with stakeholders** - Product Managers can access and filter relevant insights

## Non-Goals (v1)

- Real-time collaboration / commenting
- Integration with external tools (Jira, Slack, etc.)
- Analytics dashboards
- Mobile app

## Users

| Role | Description | Needs |
|------|-------------|-------|
| Developer Advocate | Creates insights from community feedback | Quick capture, tagging, linking to products |
| Product Manager | Consumes insights for decision-making | Search, filter, view trends |

## Success Metrics

- Time from insight capture to PM visibility
- Number of insights captured per week
- Insights referenced in product decisions

## Constraints

- Test-first development (TDD)
- All code must pass SonarCloud quality gates
- Python/FastAPI for initial prototype
