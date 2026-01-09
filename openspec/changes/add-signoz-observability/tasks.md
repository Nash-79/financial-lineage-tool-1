## 1. Implementation
- [ ] 1.1 Add OpenTelemetry dependencies and configure OTLP exporter settings.
- [ ] 1.2 Instrument FastAPI and HTTPX; wire logging to OTLP.
- [ ] 1.3 Add docker compose file to run SigNoz locally and document usage.
- [ ] 1.4 Add environment variables for service name, OTLP endpoint, and enable/disable flags.
- [ ] 1.5 Add tests or a smoke check to verify OTLP export is initialized.

## 2. Validation
- [ ] 2.1 Manual: start SigNoz stack and confirm traces/logs appear.
