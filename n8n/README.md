# n8n example workflows

Import each JSON into n8n (Workflows > Import from File) and replace the `REPLACE_WITH_*` placeholders with your own sheet IDs, credentials and endpoints. All three are inactive templates: review them before enabling.

1. `01-invoice-email-to-sheet-ocr-llm.json` - mailbox watch for invoices, LLM line-item extraction, append to Google Sheets, Slack alert on failure.
2. `02-customs-tariff-rag-assistant.json` - chat assistant over public EU TARIC/CN texts with cited answers.
3. `03-shipment-eta-alerts.json` - daily tracking poll with change detection and email alert.

No credentials, endpoints or real data are included.
