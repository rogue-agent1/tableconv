# tableconv

Convert between table formats. Zero dependencies.

## Usage

```bash
tableconv convert data.csv md       # CSV → Markdown
tableconv convert data.csv json     # CSV → JSON
tableconv convert data.json html    # JSON → HTML
tableconv convert data.tsv csv      # TSV → CSV
tableconv info data.csv             # Show columns/rows
cat data.csv | tableconv convert - md  # Pipe mode
```

## Formats

CSV, TSV, JSON, Markdown, HTML — auto-detects input format.

## Requirements

- Python 3.6+ (stdlib only)
