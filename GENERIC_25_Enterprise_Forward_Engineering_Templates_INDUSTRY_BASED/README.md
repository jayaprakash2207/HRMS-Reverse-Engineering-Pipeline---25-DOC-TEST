# Generic Enterprise Forward-Engineering Template Pack — 25 Artifacts

This is the domain-neutral version of the 25-document package.

## Intended use

The same templates can be used for:
- ERP
- CRM
- Banking
- Insurance
- Healthcare
- Manufacturing
- Retail
- Logistics
- Education
- Government
- Telecom
- SaaS
- Internal enterprise systems
- Legacy modernization / migration
- Package replacement
- Application rationalization
- Custom software reconstruction

The project supplies `{{DOMAIN}}`, source-system context, target-system context, and domain vocabulary. The templates themselves do not assume HRMS.

## Industrial basis

The package is intentionally a synthesis rather than a claim that one standard defines all 25 artifacts.

Primary foundations include:
- ISO/IEC/IEEE 29148 — requirements engineering and required information items/content.
- ISO/IEC/IEEE 15288 — system life-cycle processes.
- ISO/IEC/IEEE 12207 — software life-cycle processes.
- ISO/IEC 25010 — product quality model.
- ISO/IEC 11179 — metadata/data-element concepts and metadata registries.
- TOGAF — enterprise architecture content, catalogs, matrices, views/viewpoints and architecture governance.
- UML — standardized modeling language for structural/behavioral models.
- BPMN — business process modeling notation.
- OpenAPI — language-agnostic HTTP API description.
- NIST systems-security engineering guidance.
- SEI Views and Beyond — architecture documentation through views/viewpoints.
- ISO 9241-210 — human-centred design.

## Important distinction

These are enterprise-grade templates derived from recognized standards and industry practices. They are not verbatim copies of proprietary consulting-firm templates and are not themselves official ISO/IEEE/OMG standards.

## Domain-neutral population rule

Do not write HR-specific examples into a generic document unless the project domain is HRMS. Use:
- `{{DOMAIN}}`
- `{{BUSINESS_ENTITY}}`
- `{{PROCESS}}`
- `{{ACTOR}}`
- `{{SERVICE}}`
- `{{DATA_ENTITY}}`
- `{{BUSINESS_RULE}}`

Domain-specific examples belong in project instances, not in the reusable template.

## Evidence discipline

Every material statement must be classified:
OBSERVED / DERIVED / INFERRED / ASSUMED / UNKNOWN / CONTRADICTED.

Never turn a domain assumption into an observed fact.

## Mandatory pipeline gates

1. Evidence completeness
2. Structural completeness
3. Cross-artifact consistency
4. Traceability
5. Critical-scope completeness
6. Quality/NFR completeness
7. Forward-engineering readiness
