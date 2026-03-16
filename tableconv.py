#!/usr/bin/env python3
"""tableconv - Convert between table formats (CSV, JSON, TSV, Markdown, HTML). Zero deps."""
import sys, csv, json, io, os

def read_csv(text, delimiter=","):
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    return list(reader), reader.fieldnames or []

def read_json(text):
    data = json.loads(text)
    if isinstance(data, list) and data:
        return data, list(data[0].keys()) if isinstance(data[0], dict) else []
    return [], []

def read_md(text):
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    if len(lines) < 2: return [], []
    # Parse header
    headers = [h.strip() for h in lines[0].strip("|").split("|")]
    # Skip separator line
    rows = []
    for line in lines[2:]:
        vals = [v.strip() for v in line.strip("|").split("|")]
        rows.append(dict(zip(headers, vals)))
    return rows, headers

def to_csv(rows, headers, delimiter=","):
    out = io.StringIO()
    w = csv.DictWriter(out, fieldnames=headers, delimiter=delimiter)
    w.writeheader()
    w.writerows(rows)
    return out.getvalue()

def to_json(rows, headers):
    return json.dumps(rows, indent=2)

def to_md(rows, headers):
    if not headers: return ""
    widths = {h: max(len(h), max((len(str(r.get(h,""))) for r in rows), default=0)) for h in headers}
    lines = []
    lines.append("| " + " | ".join(h.ljust(widths[h]) for h in headers) + " |")
    lines.append("| " + " | ".join("-" * widths[h] for h in headers) + " |")
    for r in rows:
        lines.append("| " + " | ".join(str(r.get(h,"")).ljust(widths[h]) for h in headers) + " |")
    return "\n".join(lines)

def to_html(rows, headers):
    lines = ["<table>", "  <thead>", "    <tr>"]
    for h in headers: lines.append(f"      <th>{h}</th>")
    lines.extend(["    </tr>", "  </thead>", "  <tbody>"])
    for r in rows:
        lines.append("    <tr>")
        for h in headers: lines.append(f"      <td>{r.get(h,'')}</td>")
        lines.append("    </tr>")
    lines.extend(["  </tbody>", "</table>"])
    return "\n".join(lines)

def detect_format(text, path=""):
    ext = os.path.splitext(path)[1].lower() if path else ""
    if ext == ".csv" or (not ext and "," in text.split("\n")[0]): return "csv"
    if ext == ".tsv" or (not ext and "\t" in text.split("\n")[0]): return "tsv"
    if ext == ".json" or text.strip().startswith(("[","{")): return "json"
    if ext == ".md" or "|" in text.split("\n")[0]: return "md"
    return "csv"

READERS = {"csv": lambda t: read_csv(t), "tsv": lambda t: read_csv(t, "\t"), "json": read_json, "md": read_md}
WRITERS = {"csv": to_csv, "tsv": lambda r,h: to_csv(r,h,"\t"), "json": to_json, "md": to_md, "html": to_html}

def cmd_convert(args):
    if len(args) < 2:
        print("Usage: tableconv convert <file> <output_format>")
        print(f"Formats: {', '.join(WRITERS.keys())}")
        sys.exit(1)
    
    path = args[0]
    out_fmt = args[1].lower().lstrip(".")
    
    if path == "-":
        text = sys.stdin.read()
        in_fmt = detect_format(text)
    else:
        with open(path) as f: text = f.read()
        in_fmt = detect_format(text, path)
    
    if "--from" in args:
        in_fmt = args[args.index("--from") + 1]
    
    if in_fmt not in READERS: print(f"❌ Can't read: {in_fmt}"); sys.exit(1)
    if out_fmt not in WRITERS: print(f"❌ Can't write: {out_fmt}"); sys.exit(1)
    
    rows, headers = READERS[in_fmt](text)
    print(WRITERS[out_fmt](rows, headers))

def cmd_info(args):
    if not args: print("Usage: tableconv info <file>"); sys.exit(1)
    with open(args[0]) as f: text = f.read()
    fmt = detect_format(text, args[0])
    rows, headers = READERS.get(fmt, lambda t: ([], []))(text)
    print(f"📊 {args[0]}")
    print(f"  Format:  {fmt}")
    print(f"  Columns: {len(headers)} ({', '.join(headers[:8])}{'...' if len(headers)>8 else ''})")
    print(f"  Rows:    {len(rows)}")

CMDS = {"convert":cmd_convert,"c":cmd_convert,"info":cmd_info,"i":cmd_info}

if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] in ("-h","--help"):
        print("tableconv - Convert between table formats")
        print("Commands: convert <file> <format>, info <file>")
        print(f"Formats: {', '.join(WRITERS.keys())}")
        sys.exit(0)
    cmd = args[0]
    if cmd not in CMDS: print(f"Unknown: {cmd}"); sys.exit(1)
    CMDS[cmd](args[1:])
