# Q-SYNC architecture

## Module boundaries

| Module | Responsibility |
|---|---|
| `app.models` | Strict API validation for timestamped digital, physical, Wi-Fi, metadata and mode fields. |
| `app.database` | SQLite initialization, connections, and JSON persistence. |
| `app.services` | Assessment policy, component health, persistence orchestration, and clearly-labelled simulations. |
| `app.main` | Versioned REST API, OpenAPI publication, CORS and WebSocket fan-out. |
| `frontend` | React console consuming REST history/current/incidents and push updates. |

## Storage design

- `observations`: immutable raw validated observation JSON, assessment JSON, mode, timestamp and creation time.
- `incidents`: a separate record referencing its observation; includes status, severity, title and preserved evidence.
- `experiments`: scenario, lifecycle status, serialized actual pipeline result and time.

`initialize()` is the documented idempotent schema migration strategy for this local prototype.

## Decision policy

The consistency engine does not produce a security percentage. A CPU value at least 90%, object temperature at least 65°C, motion at least 2g, or more than 15 observed APs each creates a documented indicator. One indicator is a low warning; two or more are a medium incident. Wi-Fi findings are explicitly contextual. Unavailable components and Wi-Fi scans create uncertainty rather than attacks.

## Integration requirements

1. A serial adapter must parse the approved ESP32 message format, reject malformed/duplicate records, and POST the validated observation to `/api/v1/telemetry`.
2. Add model adapters that write model version, reason codes, scores, fidelity, classical baselines and error states into the supplied schema before ingestion.
3. Label experiment outcomes before using the research metrics endpoint for actual confusion matrices or ablations.

The server should remain on loopback in local use. No endpoint executes commands, accesses arbitrary files, or performs automated response actions.
