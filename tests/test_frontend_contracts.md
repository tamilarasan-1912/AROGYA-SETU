# Frontend integration contract

This checklist documents the API contracts exercised by the demo frontend.

- `GET /api/patients` returns `{ "patients": [...] }`.
- `POST /api/patients` accepts `name`, optional `age`, optional `sex`, and `language`.
- `GET /api/patients/{id}/records` returns `{ "records": [...] }`.
- `POST /api/pipeline/analyze` accepts `patient_id` and stores the resulting encounter when supplied.
- `POST /api/pipeline/analyze-audio` accepts multipart `audio_file`, `language`, and optional `patient_id`.
- `POST /api/consultations` requires an existing `patient_id` and returns a consultation containing `id`, `room_id`, and `status`.
- `PATCH /api/consultations/{id}` accepts `scheduled`, `active`, `completed`, or `cancelled`.
- `WS /api/telemedicine/ws/{room_id}/{peer_id}` provides prototype signaling only; it is not production-grade media transport.

The clinical AI remains decision support only and must not be presented as a diagnosis.
