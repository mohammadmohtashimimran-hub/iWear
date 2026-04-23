# iWear System Architecture – Week 1

```mermaid
flowchart TB
    subgraph Tier1["Tier 1: Presentation"]
        User["User"]
        React["React Frontend<br/>(Browser)"]
        User -->|"uses"| React
    end

    subgraph Tier2["Tier 2: Application"]
        Flask["Flask Backend API"]
        AI["AI Business Insights<br/>Assistant"]
        Flask <-->|"calls"| AI
    end

    subgraph Tier3["Tier 3: Data"]
        subgraph Docker["Docker"]
            PostgreSQL["PostgreSQL<br/>Database"]
        end
    end

    React -->|"HTTP requests"| Flask
    Flask -->|"queries"| PostgreSQL
    AI ---|"uses backend only"| Flask

    style Tier1 fill:#e3f2fd
    style Tier2 fill:#f3e5f5
    style Tier3 fill:#e8f5e9
    style Docker fill:#fff3e0
```

## Request flow

1. **User → React → Flask API → PostgreSQL**  
   User actions in the browser hit the React app, which calls the Flask API; the API talks to PostgreSQL for data.

2. **AI Assistant**  
   The AI Business Insights Assistant lives inside the backend layer and interacts with the database only through the Flask backend (no direct DB access).

3. **Docker**  
   PostgreSQL runs inside a Docker container; the Flask API connects to it via the configured host/port (e.g. `127.0.0.1:5433`).
