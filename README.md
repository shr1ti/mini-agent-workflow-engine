## Workflow Diagram – Code Review Mini-Agent

```mermaid
graph TD
    A[Start] --> B[extract_functions]
    B --> C[check_complexity]
    C --> D[detect_issues]
    D --> E[suggest_improvements]
    E --> F[evaluate_quality]

    F -->|quality_score < threshold| C
    F -->|quality_score >= threshold| G[End]
