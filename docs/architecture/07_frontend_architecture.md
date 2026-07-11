# Frontend Architecture Specification

This document details the architecture and design of the frontend for the MedScope AI platform, which serves as the primary interface for laboratory professionals to interact with the unified digital microscopy system.

## 1. Technology Stack
The frontend is built using a modern React-based stack to ensure performance, type safety, and a highly responsive user experience.

- **Framework**: Next.js 15+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: ShadCN UI (Radix Primitives)
- **Data Fetching**: React Query (TanStack Query) + Axios
- **State Management**: Zustand (for lightweight global state)

## 2. Core Workflows (User Journeys)

The frontend is designed around the following primary workflows:

### A. The "Analyze Smear" Workflow
This is the core feature of the platform. A laboratory technician uploads a microscope image and receives a comprehensive, multi-disease analysis.

1. **Upload & Image Quality Check**: The user uploads an image. The frontend immediately displays it and queries the backend for the EfficientNet quality assessment (e.g., checking for blur or poor lighting).
2. **Unified Analysis Execution**: The frontend sends the image to the backend orchestration endpoint (`/api/analyze`), which cascades through the YOLOv11 and Swin Transformer models.
3. **Interactive Results Viewer**: 
   - Displays the original image with overlaid bounding boxes (toggled on/off).
   - Shows total cell counts (RBC, WBC, Platelets).
   - Flags regions of interest (e.g., Malaria parasites, Leukemic blasts).
4. **Explainability Mode**: The user can toggle a "heatmap" overlay (GradCAM/SHAP) to see *why* the AI flagged a specific cell as abnormal.

### B. The "Clinical Copilot" Workflow
An interactive sidebar available during analysis.

- Powered by a local LLM (Qwen 2.5 7B) + RAG (Qdrant).
- Allows the user to ask contextual questions: *"Why was this flagged as a Schizont rather than a Trophozoite?"* or *"What are the standard protocols for this WBC count?"*
- The chat interface retains context about the currently loaded image.

## 3. Directory Structure (`frontend/`)

```text
frontend/
├── src/
│   ├── app/                  # Next.js App Router (Pages & Layouts)
│   │   ├── analyze/          # The main workspace for image analysis
│   │   ├── history/          # Dashboard for past analyses
│   │   └── settings/         # User/System configurations
│   ├── components/
│   │   ├── ui/               # Reusable ShadCN components (buttons, cards, etc.)
│   │   ├── viewer/           # Custom canvas/WebGL components for drawing bounding boxes
│   │   └── chat/             # Chat UI for the Clinical Copilot
│   ├── lib/                  # Utility functions and API clients (Axios configs)
│   ├── hooks/                # Custom React hooks (React Query fetching hooks)
│   └── store/                # Zustand stores (e.g., activeImageStore)
└── public/                   # Static assets (icons, placeholder images)
```

## 4. Key Component Designs

### The Image Viewer Component
Because we are visualizing high-resolution medical images with potentially hundreds of bounding boxes, the image viewer must be highly performant.
- Implement zooming and panning functionality.
- Render bounding boxes on a separate `<canvas>` layer overlaid on the `<img />` tag.
- Implement hover tooltips on bounding boxes that display confidence scores and classifications.

### The Dashboard / Analysis History
- A tabular view of past analyses, stored in the PostgreSQL database.
- Sortable by date, patient ID, and flagged diseases (e.g., filtering for only slides flagged positive for Leukemia).

## 5. Security & Authentication
While not the primary focus of the initial AI prototype, the frontend architecture includes placeholders for role-based access control (RBAC):
- **Technician Role**: Can upload images and generate reports.
- **Pathologist Role**: Can review, override AI predictions, and formally sign-off on reports.
