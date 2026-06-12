# Architecture

## Overview

The Recipe Selector Agent uses a multi-agent architecture where each agent handles a specific aspect of the recipe discovery and cooking workflow.

## Component Architecture

```
┌─────────────────────────────────────┐
│     User Interface / CLI            │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      Agent Orchestration            │
│  (Main Agent Router)                │
└──────┬───────────────────────────┬──┘
       │                           │
   ┌───▼────────┐          ┌──────▼────┐
   │Recipe Agent │          │Constraint │
   │(Discovery)  │          │ Validator │
   └────────────┘          └──────────┘
       │
   ┌───▼────────┐
   │Data Layer  │
   │(APIs/DB)   │
   └────────────┘
```

## Agent Responsibilities

- **Recipe Agent**: Searches and recommends recipes
- **Constraint Validator**: Checks dietary requirements
- **Cooking Guide Agent**: Provides step-by-step instructions
- **Ingredient Substitution**: Suggests alternatives

## Data Flow

1. User provides ingredients and preferences
2. Constraint Validator filters options
3. Recipe Agent searches database
4. Results ranked by relevance
5. Cooking Guide Agent provides instructions
