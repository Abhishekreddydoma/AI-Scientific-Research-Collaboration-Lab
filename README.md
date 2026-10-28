# AI Scientific Research Collaboration Lab — Frontend (Sprint 2)

A minimalist scientific research frontend built with Next.js, TypeScript, Tailwind CSS, and React Flow, designed for AI-assisted research workspaces.

## Features

- **Scientific Workspace Aesthetic**: Restrained warm orange and white palette, clear Inter typography, subtle borders, and generous whitespace.
- **Real Backend Integration**: Directly connected to the Sprint 1 FastAPI backend (`/api/research`, `/api/users`, `/api/agents`, `/api/results`, `/api/reports`).
- **Research Workspace**: 3-zone layout with virtual agent status cards, interactive React Flow research pipeline DAG, and activity audit panel.
- **Scientific Honesty**: Zero fake papers, simulated metrics, or placeholder hallucinated findings. Unexecuted agents show `Waiting` state, and future sections present clean `EmptyState` views.
- **Route-Based Navigation**: Overview, Agents, Literature, Datasets, Hypotheses, Experiments, Review, and Report.

## Getting Started

### Prerequisites

- Node.js 18+
- Sprint 1 FastAPI backend running on `http://localhost:8000`

### Setup

```bash
# 1. Install dependencies
npm install

# 2. Configure environment
cp .env.local.example .env.local

# 3. Start development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the application.

## Build

```bash
npm run build
npm run start
```
