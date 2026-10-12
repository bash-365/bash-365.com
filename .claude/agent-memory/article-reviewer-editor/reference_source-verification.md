---
name: reference-source-verification
description: How to actually fetch and verify the primary sources bash-365.com posts cite — which hosts block WebFetch, and how to read GAO PDFs
metadata:
  type: reference
---

Verifying an external citation in a bash-365.com post means reading the primary text, not a summary. These hosts need workarounds; a fetch failure on them is **not** evidence of a dead link — they all work in a normal browser, so do not flag the link as broken.

**`dl.acm.org`** — returns HTTP 403 to WebFetch. Verify ACM papers from the DOI metadata or a mirror; the `https://dl.acm.org/doi/10.1145/...` link itself is fine to ship.

**`www.nature.com`** — 303-redirects bots to `idp.nature.com/authorize?...`. WebFetch will not follow it. Verify the abstract via WebSearch (the abstract text is widely indexed) or the Antikythera Mechanism Research Project mirror at `antikythera-mechanism.gr/project/publications/nature-2006`.

**`www.gao.gov` PDFs** — `https://www.gao.gov/assets/<report-id>.pdf` downloads fine but WebFetch cannot read the binary. The report *summary* page (`/products/<report-id>`) is readable and usually enough. For exact figures, decompress the PDF streams and pull the text operators:

```python
import zlib, re
data = open(pdf_path, 'rb').read()
blob = b'\n'.join(
    zlib.decompress(m.group(1))
    for m in re.finditer(rb'stream\r?\n(.*?)endstream', data, re.S)
    if _try(m)  # wrap decompress in try/except; not every stream is flate
)
txt = b' '.join(re.findall(rb'\((?:\\.|[^\\()])*\)', blob))
```
Kerning splits words across `(...)` runs, so search the whitespace-stripped string (`s.replace(' ', '')`) for `COBOL`, `dwindling`, etc., then read the surrounding ±400 chars. `pdftotext` and `pypdf` are not installed in the remote session.

**House rule that constrains all of this:** external links go only to vendor docs, primary sources, or regulators — never a blog or news outlet. So when the only available source for a claim is journalism, the fix is to attribute it in-text and ship it unlinked, not to link the news story. See the New Jersey COBOL trap in [[reference-post-standards]].

See [[feedback-recurring-issues]] for the editorial side of citation handling.
