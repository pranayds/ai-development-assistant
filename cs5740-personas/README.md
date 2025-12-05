# AI Agent Personas & Challenges

A collection of attributed AI agent personas, synthesized expert prompts, and challenge scenarios for evaluating AI system behavior across different professional roles.

## Overview

This repository contains three key components for AI agent development and evaluation:

1. **Attributed Personas** - Individual agent personas based on real-world professionals
2. **Synthesized Expert Personas** - Aggregated best-practice prompts combining multiple expert perspectives
3. **Challenge Scenarios** - Complex, realistic scenarios for testing persona effectiveness

## Repository Structure

```
personas/
├── design_architecture/
│   ├── data_specialists/
│   ├── system_architects/
│   └── ux_ui_designers/
├── development/
│   ├── software_engineers/
│   └── specialized_engineers/
├── operations_deployment/
│   ├── devops_engineers/
│   └── release_engineers/
├── planning_requirements/
│   ├── product_managers/
│   └── requirements_analysts/
└── quality_testing/
    ├── performance_engineers/
    ├── qa_engineers/
    └── security_engineers/

challenges/
└── [mirrors personas/ structure]
```

## Component Types

### 1. Attributed Personas (Individual Files)

Individual persona files represent specific professional perspectives, each authored by a contributor and attributed accordingly. Examples:

- `Carlos.md` - Security-focused DevOps engineer
- `Emily.md` - Senior software engineer
- `Carissa.md` - Strategic product manager

These personas capture:
- Core identity and communication style
- Professional values and priorities
- Behavioral patterns and decision-making frameworks
- Domain expertise and technical knowledge

### 2. Aggregate Expert Synthesis (Synthesized Personas)

Each subdirectory contains an `Aggregate_Expert_Synthesis.md` file that synthesizes best practices from multiple attributed personas into a comprehensive expert prompt.

**Key features:**
- Combines strengths from multiple individual personas
- Provides comprehensive behavioral frameworks
- Includes structured decision-making processes
- Defines clear guardrails and priorities

**Example:** `personas/operations_deployment/devops_engineers/Aggregate_Expert_Synthesis.md` synthesizes expertise from 12+ DevOps personas into a single comprehensive prompt.

### 3. Challenge Scenarios

Each subdirectory in `challenges/` contains a `CHALLENGE_PROMPT.md` with complex, realistic scenarios designed to test persona effectiveness.

**Challenges typically include:**
- High-stakes decision-making situations
- Conflicting stakeholder requirements
- Time-sensitive pressures
- Ethical dilemmas
- Technical and business trade-offs

**Example:** The UX/UI Designer challenge presents an accessibility crisis conflicting with business goals, requiring the persona to balance legal requirements, user needs, and commercial pressures.

## Usage

### Testing Individual Personas

1. Select a persona from the `personas/` directory
2. Load it as a system prompt in your AI tool
3. Present the corresponding challenge from `challenges/`
4. Evaluate how well the persona handles the scenario

### Using Synthesized Expert Personas

1. Navigate to any subdirectory in `personas/`
2. Use `Aggregate_Expert_Synthesis.md` as your system prompt
3. This provides the most comprehensive expert behavior for that role
4. Test against the corresponding challenge scenario

### Comparing Approaches

Compare how different personas handle the same challenge:
- Individual attributed personas vs. synthesized expert
- Cross-role perspectives (e.g., DevOps vs. Security Engineer on same infrastructure problem)
- Evolution of persona effectiveness over iterations

## Persona Categories

### Design & Architecture
- **Data Specialists**: Database architects, data engineers, ML engineers
- **System Architects**: Cloud architects, distributed systems experts, pragmatic designers
- **UX/UI Designers**: User researchers, interaction designers, accessibility experts

### Development
- **Software Engineers**: Full-stack, backend, frontend developers
- **Specialized Engineers**: Technical leads, platform engineers, domain experts

### Operations & Deployment
- **DevOps Engineers**: SREs, infrastructure automation, CI/CD specialists
- **Release Engineers**: Release management, deployment automation

### Planning & Requirements
- **Product Managers**: Strategic PMs, agile coaches, stakeholder managers
- **Requirements Analysts**: Business analysts, systems analysts

### Quality & Testing
- **Performance Engineers**: Load testing, optimization specialists
- **QA Engineers**: Test automation, quality assurance
- **Security Engineers**: AppSec, security architects, compliance experts

## Attribution

Each persona includes attribution metadata indicating:
- Original author
- Course context (CS5740 Fall 2025)
- Classification category

## Contributing

When adding new personas:
1. Place attributed personas in appropriate `personas/` subdirectory
2. Update `Aggregate_Expert_Synthesis.md` to incorporate new insights
3. Create or update corresponding challenge scenarios in `challenges/`
4. Include proper attribution metadata

## License

Educational use - CS5740 Fall 2025, Virginia Tech
