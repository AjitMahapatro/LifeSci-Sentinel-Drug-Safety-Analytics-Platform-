# LifeSci Sentinel

LifeSci Sentinel is a data engineering project that ingests drug safety event data from the OpenFDA API, processes it through an ETL pipeline, and loads it into a data warehouse for analytics and further use by downstream applications.

## Architecture

The project follows a modern data stack architecture, ensuring data quality, scalability, and ease of use for analytics and AI-driven applications.

```mermaid
graph TD
    subgraph "Data Ingestion"
        A[OpenFDA API]
    end

    subgraph "Data Platform"
        subgraph "ETL & Warehousing"
            B(Python ETL Scripts)
            C{Data Quality Checks}
            D[(PostgreSQL Data Warehouse)]
        end

        subgraph "Serving & Analytics"
            E(Analytics Views)
            F[Power BI Dashboard]
        end
    end

    subgraph "Applications"
        G(FastAPI Backend)
        H(LLM Assistant)
    end

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    D --> G
    G --> H
```