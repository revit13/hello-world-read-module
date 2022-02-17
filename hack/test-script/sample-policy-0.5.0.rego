package dataapi.authz

rule[{"action": {"name":"RedactAction", "columns": column_names}, "policy": description}] {
  description := "Redact columns tagged as PII in datasets tagged with finance = true"
  input.action.actionType == "read"
  input.resource.tags.finance
  column_names := [input.resource.columns[i].name | input.resource.columns[i].tags.PII]
  count(column_names) > 0
}

rule[{"action": {"name":"RedactAction", "columns": column_names}, "policy": description}] {
  description := "Redact columns tagged as sensitive in datasets tagged with finance = true"
  input.action.actionType == "read"
  input.resource.tags.finance
  column_names := [input.resource.columns[i].name | input.resource.columns[i].tags.sensitive]
  count(column_names) > 0
}

