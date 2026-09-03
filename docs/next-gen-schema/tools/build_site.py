#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["markdown>=3.6", "pyyaml>=6"]
# ///
"""Build the browsable static site from the canonical graph and the document bundle.

  uv run docs/next-gen-schema/tools/build_site.py [--out site]

Output: one page per node (every edge a link), one page per reified relationship, an index
per node type, the relationship-type catalog, one page per constellation example with the
diagram's chips linked, and every document in docs/next-gen-schema and notes rendered from
Markdown with links rewritten. No server needed: open site/index.html.
"""
import argparse, glob, html, json, os, re, shutil, sys

import markdown, yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from graph import load_graph, canonical_text, BASE, EXAMPLES_DIR  # noqa: E402
from render_cards import Cards, render_view  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(BASE))
NOTES = os.path.join(ROOT, "notes")
DOSSIERS = {"RDE2_000123": "fc-neighborhood.svg", "RDE2_000124": "thyroid-neighborhood.svg", "RDE2_000001": "de-presence.svg",
            "RDE2_000077": "de-severity.svg", "RDE2_000014": "de-size-mean-diameter.svg", "RID199": "al-common-bile-duct.svg"}
TYPE_ORDER = ["FindingClass", "Diagnosis", "Grouping", "DataElement", "Value", "AnatomicLocation", "Concept", "RelationshipType"]
TYPE_LABEL = {"FindingClass": "Finding classes", "Diagnosis": "Diagnoses", "Grouping": "Grouping nodes", "DataElement": "Data elements",
              "Value": "Values", "AnatomicLocation": "Anatomic locations", "Concept": "Concept nodes", "RelationshipType": "Relationship types"}
CONTEXT_EDGES = {"HAS_ETIOLOGY", "SEEN_ON", "IN_REGION", "IN_SUBSPECIALTY", "SEX", "AGE_APPLICABILITY", "TIME_COURSE"}
MAP_EDGES = {"exactMatch", "closeMatch"}

CSS = """
:root{--ink:#1f2937;--muted:#64748b;--rule:#e2e8f0;--bg:#ffffff;--soft:#f8fafc;--link:#1d4ed8}
*{box-sizing:border-box}body{margin:0;font:15px/1.55 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;color:var(--ink);background:var(--bg)}
a{color:var(--link);text-decoration:none}a:hover{text-decoration:underline}
header.top{border-bottom:1px solid var(--rule);background:var(--soft);padding:10px 24px;display:flex;gap:18px;align-items:center;flex-wrap:wrap}
header.top .brand{font-weight:700;color:var(--ink)}header.top nav a{margin-right:14px;color:#334155}
header.top .search{margin-left:auto;position:relative}header.top input{padding:6px 10px;border:1px solid #cbd5e1;border-radius:6px;width:280px;font:inherit}
#hits{position:absolute;right:0;top:36px;background:#fff;border:1px solid #cbd5e1;border-radius:6px;min-width:360px;max-height:360px;overflow:auto;display:none;z-index:10;box-shadow:0 6px 24px rgba(0,0,0,.08)}
#hits a{display:block;padding:6px 10px;border-bottom:1px solid var(--rule);color:var(--ink)}#hits a:hover{background:var(--soft)}#hits .k{color:var(--muted);font-size:12px;margin-left:6px}
main{max-width:1100px;margin:0 auto;padding:24px}
h1{font-size:26px;margin:.2em 0 .3em}h2{font-size:17px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);border-bottom:1px solid var(--rule);padding-bottom:4px;margin-top:2em}
h3{font-size:16px;margin-top:1.4em}
.badge{display:inline-block;padding:2px 9px;border-radius:999px;font-size:12px;font-weight:600;letter-spacing:.03em;border:1px solid transparent;margin-right:6px}
.b-FindingClass{background:#eff6ff;color:#1e3a8a;border-color:#bfdbfe}.b-Diagnosis{background:#f5f3ff;color:#4c1d95;border-color:#ddd6fe}.b-Grouping{background:#f8fafc;color:#334155;border-color:#cbd5e1}
.b-DataElement,.b-Value{background:#f0fdf4;color:#14532d;border-color:#bbf7d0}.b-AnatomicLocation{background:#fffbeb;color:#78350f;border-color:#fde68a}.b-Concept,.b-RelationshipType{background:#f8fafc;color:#475569;border-color:#cbd5e1}
.meta{color:var(--muted);font-size:13px}.defn{font-size:16px;max-width:820px}.note{background:#fffbeb;border-left:3px solid #f59e0b;padding:8px 12px;margin:10px 0;font-size:14px}
table{border-collapse:collapse;width:100%;font-size:14px;margin:8px 0}th,td{text-align:left;vertical-align:top;padding:6px 8px;border-bottom:1px solid var(--rule)}th{color:var(--muted);font-weight:600;font-size:12px;letter-spacing:.04em;text-transform:uppercase}
code,pre{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:13px}pre{background:var(--soft);border:1px solid var(--rule);border-radius:6px;padding:12px;overflow-x:auto}
.props{color:#7c3aed;font-size:13px}.rid{color:var(--muted);font-size:12px}
ul.edges{list-style:none;padding:0}ul.edges li{padding:5px 0;border-bottom:1px dashed var(--rule)}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px;margin:16px 0}.card{border:1px solid var(--rule);border-radius:10px;padding:14px;background:#fff}.card h3{margin:0 0 6px}.card p{margin:0;color:var(--muted);font-size:14px}
.diagram{border:1px solid var(--rule);border-radius:10px;padding:8px;overflow-x:auto;background:#fff}.diagram svg{max-width:100%;height:auto}.diagram a:hover rect:first-child{stroke:#2563eb;stroke-width:2}
.doc{max-width:860px}.doc img{max-width:100%}.fm{background:var(--soft);border:1px solid var(--rule);border-radius:8px;padding:10px 14px;font-size:13px;margin-bottom:18px}.fm dt{font-weight:600;color:var(--muted);display:inline;margin-right:4px}.fm dd{display:inline;margin:0 14px 0 0}
blockquote{border-left:3px solid #cbd5e1;margin:0;padding:2px 14px;color:#334155}
.treepanel{position:sticky;bottom:12px;background:#fff;border:1px solid #94a3b8;border-radius:10px;padding:12px 16px;box-shadow:0 8px 30px rgba(0,0,0,.12);margin-top:12px;font-size:14px}.treepanel h4{margin:8px 0 4px;font-size:12px;letter-spacing:.05em;text-transform:uppercase;color:#64748b}.treepanel ul{margin:0;padding-left:18px}.treepanel .lbl{color:#64748b;font-size:12px;letter-spacing:.03em;text-transform:uppercase;margin-right:6px}.treepanel .tp-head{font-size:16px;margin-bottom:6px}
.diagram .mini{cursor:pointer}.diagram a:hover{text-decoration:none}.diagram a:hover .mini rect:first-child{stroke:#2563eb;stroke-width:2}.tree-page .diagram .detail{display:none !important}
"""

JS = """
(function(){var idx=null,inp=document.getElementById('q'),box=document.getElementById('hits'),rel=document.body.dataset.rel||'';
function load(cb){if(idx){cb();return}fetch(rel+'search.json').then(r=>r.json()).then(d=>{idx=d;cb()})}
function show(q){q=q.trim().toLowerCase();if(!q){box.style.display='none';return}var hits=idx.filter(e=>e.t.toLowerCase().includes(q)||(e.s||'').toLowerCase().includes(q)).slice(0,40);
box.innerHTML=hits.map(e=>'<a href="'+rel+e.u+'">'+e.t+'<span class="k">'+e.k+'</span></a>').join('')||'<a>no match</a>';box.style.display='block'}
if(inp){inp.addEventListener('input',()=>load(()=>show(inp.value)));inp.addEventListener('focus',()=>load(()=>show(inp.value)));document.addEventListener('click',e=>{if(!box.contains(e.target)&&e.target!==inp)box.style.display='none'})}})();
"""


def esc(s): return html.escape(str(s), quote=True)
def fname(nid): return re.sub(r"[^A-Za-z0-9_.-]", "_", nid)


class Site:
    def __init__(self, out):
        self.out = out
        self.g = load_graph()
        self.views = {}
        for p in sorted(glob.glob(os.path.join(EXAMPLES_DIR, "*.mat.json")) + glob.glob(os.path.join(EXAMPLES_DIR, "*.tree.json"))):
            v = json.load(open(p, encoding="utf-8")); v["file"] = os.path.basename(p)
            self.views[os.path.basename(p).rsplit(".", 2)[0] + "-" + v["kind"]] = v
        self.cards = Cards(self.g)
        self.reltypes = {n["id"]: n for n in self.g.nodes.values() if n["node"] == "RelationshipType"}
        self.search = []

    # ---- helpers -------------------------------------------------------------------
    def node_href(self, nid, rel): return f'{rel}nodes/{fname(nid)}.html'
    def edge_href(self, eid, rel): return f'{rel}edges/{fname(eid)}.html'

    def link(self, nid, rel, with_type=False):
        n = self.g.nodes.get(nid)
        if not n:
            return f'<code>{esc(nid)}</code>'
        t = f' <span class="rid">{esc(n["node"])}</span>' if with_type else ''
        return f'<a href="{self.node_href(nid, rel)}">{esc(n["name"])}</a>{t}'

    def props_html(self, e, rel):
        p = dict(e.get("props", {}))
        bits = []
        for k in ("typicality", "specificity"):
            if k in p: bits.append(f'{k} {esc(p.pop(k)).replace("_", " ")}')
        if "expected" in p:
            bits.append("expected " + "; ".join(f'{esc(k)}: {esc(v)}' for k, v in sorted(p.pop("expected").items())))
        for k, v in sorted(p.items()):
            if k == "display": continue
            bits.append(f'{esc(k)} {esc(v)}' if not isinstance(v, bool) else esc(k))
        s = " · ".join(bits)
        if e.get("id"):
            s = f'<a class="rid" href="{self.edge_href(e["id"], rel)}">{esc(e["id"])}</a>' + (" · " + s if s else "")
        return f'<span class="props">{s}</span>' if s else ""

    def page(self, path, title, body, rel, extra_head=""):
        nav = "".join(f'<a href="{rel}{u}">{t}</a>' for t, u in [("Home", "index.html"), ("Examples", "examples.html"), ("Browse", "browse.html"),
                                                               ("Relationships", "relationships.html"), ("Documents", "documents.html")])
        doc = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
               f'<title>{esc(title)}</title><link rel="stylesheet" href="{rel}site.css">{extra_head}</head><body data-rel="{rel}">'
               f'<header class="top"><a class="brand" href="{rel}index.html">Next-gen CDE vocabulary</a><nav>{nav}</nav>'
               f'<div class="search"><input id="q" type="search" placeholder="Search nodes and documents…" autocomplete="off"><div id="hits"></div></div></header>'
               f'<main>{body}</main><script src="{rel}search.js"></script></body></html>')
        full = os.path.join(self.out, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        open(full, "w", encoding="utf-8").write(doc)

    def linked_svg(self, svg, rel):
        return re.sub(r'<g class="mini" id="m-([^"]+)" data-node="([^"]+)">(.*?)</g>',
                      lambda m: f'<a href="{self.node_href(m.group(2), rel)}"><g class="mini" id="m-{m.group(1)}" data-node="{m.group(2)}">{m.group(3)}</g></a>', svg, flags=re.S)

    # ---- node pages ------------------------------------------------------------------
    def values_table(self, eid, rel):
        vals = [(e, self.g.nodes[e["to"]]) for e in self.g.out_edges(eid) if e["edge"] == "member" and e["to"] in self.g.nodes]
        vals.sort(key=lambda t: (t[0].get("props", {}).get("rank", 0), t[1]["id"]))
        if not vals: return ""
        rows = []
        for e, v in vals:
            codes = ", ".join(f'{esc(m["to"])} “{esc(m.get("props", {}).get("display", ""))}”' for m in self.g.out_edges(v["id"]) if m["edge"] in MAP_EDGES)
            rank = e.get("props", {}).get("rank", "")
            rows.append(f'<tr><td><a href="{self.node_href(v["id"], rel)}">{esc(v["name"])}</a></td><td><code>{esc(v.get("value",""))}</code></td>'
                        f'<td>{esc(rank)}</td><td>{esc(v.get("definition",""))}</td><td class="rid">{codes}</td></tr>')
        return f'<h2>Values · skos:member ×{len(vals)}</h2><table><tr><th>value</th><th>machine value</th><th>rank</th><th>definition</th><th>codes</th></tr>{"".join(rows)}</table>'

    def node_page(self, n):
        nid, rel = n["id"], "../"
        t = n["node"]
        head = f'<span class="badge b-{t}">{esc(t)}</span>'
        if n.get("entity_type"): head += f'<span class="badge b-{t}">entity_type: {esc(n["entity_type"])}</span>'
        if n.get("kind"): head += f'<span class="badge b-{t}">{esc(n["kind"])}{" · ordered" if n.get("ordered") else ""}{" · multi-select" if n.get("multi_select") else ""}</span>'
        if n.get("scheme"): head += f'<span class="badge b-{t}">{esc(n["scheme"])}</span>'
        meta = " · ".join(filter(None, [nid, f'v{n["version"]}' if n.get("version") else None, n.get("status"), n.get("status_date"),
                                        f'defined in {self.g.origin[nid][0]}' if nid in self.g.origin else None]))
        body = [f'<div>{head}</div><h1>{esc(n["name"])}</h1><div class="meta">{esc(meta)}</div>']
        if n.get("definition"): body.append(f'<p class="defn">{esc(n["definition"])}</p>')
        syn = n.get("synonyms") or []
        if syn:
            body.append('<p class="meta">Synonyms: ' + " · ".join(f'{esc(s["term"])}' + (f' <i>({esc(s["type"])})</i>' if s.get("type") not in (None, "synonym") else "") for s in syn) + "</p>")
        if n.get("note"): body.append(f'<div class="note">{esc(n["note"])}</div>')
        if t == "DataElement":
            q = [f'{k}: {esc(n[k])}' for k in ("quantity_type", "units", "min", "max", "step") if n.get(k) is not None]
            if q: body.append('<p class="meta">' + " · ".join(q) + "</p>")
            if n.get("method"): body.append(f'<p><b>Method.</b> {esc(n["method"])}</p>')
        if t == "RelationshipType":
            rows = [(k, n[k]) for k in ("formal", "inverse", "symmetric", "transitive", "domain", "range", "props") if n.get(k) is not None]
            body.append("<table>" + "".join(f'<tr><th>{esc(k)}</th><td>{esc(v)}</td></tr>' for k, v in rows) + "</table>")
            uses = [e for e in self.g.edges if e["edge"] == nid]
            body.append(f'<h2>Assertions of this type ×{len(uses)}</h2>' + self.edge_table(uses, rel))
        if t in ("AnatomicLocation",) and n.get("owner"):
            body.append(f'<p class="meta">{esc(n["owner"])}</p>')
        # the mat: the node as context object, one hop out
        if t in ("FindingClass", "Diagnosis", "Grouping"):
            body.append('<h2>Mat</h2><p class="meta">Hover a card for its detail; click it to go to its own mat.</p><div class="diagram">' + self.linked_svg(self.cards.mat(nid), rel) + "</div>")
            trees = [k for k, v in self.views.items() if v["kind"] == "tree" and nid in self.tree_members(v["hub"])]
            if trees: body.append('<p class="meta">In the tree: ' + " · ".join(f'<a href="{rel}examples/{k}.html">{esc(self.g.nodes[self.views[k]["hub"]]["name"])}</a>' for k in trees) + "</p>")
        if nid in DOSSIERS:
            body.append(f'<h2>Dossier</h2><div class="diagram"><img src="{rel}docs/next-gen-schema/diagrams/{DOSSIERS[nid]}" alt="dossier diagram for {esc(n["name"])}"></div>')
        outs, ins = self.g.out_edges(nid), self.g.in_edges(nid)
        # elements
        els = [e for e in outs if e["edge"] == "HAS_ELEMENT"]
        if els:
            rows = []
            for e in els:
                el = self.g.nodes.get(e["to"], {"name": e["to"]})
                vals = [self.g.nodes[m["to"]]["name"] for m in self.g.out_edges(e["to"]) if m["edge"] == "member" and m["to"] in self.g.nodes]
                p = e.get("props", {})
                rows.append(f'<tr><td>{self.link(e["to"], rel)}</td><td>{esc(el.get("kind",""))}</td>'
                            f'<td>{esc(p.get("note",""))}</td><td>{esc(", ".join(vals))}</td><td class="rid">{self.props_html({"id": e.get("id")}, rel) if e.get("id") else ""}</td></tr>')
            body.append(f'<h2>Elements · HAS_ELEMENT ×{len(els)}</h2><table><tr><th>element</th><th>kind</th><th>note</th><th>values</th><th>binding id</th></tr>{"".join(rows)}</table>')
        body.append(self.values_table(nid, rel))
        if t == "Value":
            par = [e["from"] for e in ins if e["edge"] == "member"]
            if par: body.append(f'<h2>Value of</h2><p>{self.link(par[0], rel, True)}</p>')
        # relationships out
        groups = {}
        for e in outs:
            if e["edge"] in ("HAS_ELEMENT", "member") or e["edge"] in MAP_EDGES or e["edge"] in CONTEXT_EDGES: continue
            groups.setdefault(e["edge"], []).append(e)
        for et in sorted(groups):
            rt = self.reltypes.get(et, {})
            items = []
            for e in groups[et]:
                if et == "INTERPRETED_FROM":
                    b = self.g.edge_by_id(e["to"])
                    tgt = (f'the {self.link(b["to"], rel)} binding on {self.link(b["from"], rel)} (<a href="{self.edge_href(e["to"], rel)}">{esc(e["to"])}</a>)'
                           if b else self.link(e["to"], rel, True))
                else:
                    tgt = self.link(e["to"], rel, True)
                items.append(f'<li>{tgt} {self.props_html(e, rel)}</li>')
            body.append(f'<h2><a href="{rel}relationships/{fname(et)}.html">{esc(et)}</a> · {esc(rt.get("name", et))}</h2><ul class="edges">{"".join(items)}</ul>')
        # relationships in
        groups = {}
        for e in ins:
            if e["edge"] == "member": continue
            groups.setdefault(e["edge"], []).append(e)
        for et in sorted(groups):
            rt = self.reltypes.get(et, {})
            label = rt.get("inverse") or (f'{et} (symmetric)' if rt.get("symmetric") else f'← {et}')
            title = {"HAS_ELEMENT": "BOUND_BY · bound by", "SCOPED_TO": "SCOPE_OF · classes scoped here"}.get(et, f'{label} · inverse of {et}')
            items = [f'<li>{self.link(e["from"], rel, True)} {self.props_html(e, rel)}</li>' for e in groups[et]]
            body.append(f'<h2>{esc(title)}</h2><ul class="edges">{"".join(items)}</ul>')
        ctx = [e for e in outs if e["edge"] in CONTEXT_EDGES]
        if ctx:
            body.append('<h2>Context</h2><p>' + " · ".join(f'{esc(e["edge"])} {self.link(e["to"], rel)}' + (f' <span class="props">{esc(e["props"]["note"])}</span>' if e.get("props", {}).get("note") else "") for e in ctx) + "</p>")
        maps = [e for e in outs if e["edge"] in MAP_EDGES]
        if maps:
            rows = "".join(f'<tr><td>{esc(e["to"].split(":",1)[0])}</td><td><code>{esc(e["to"].split(":",1)[1])}</code></td><td>{esc(e.get("props",{}).get("display",""))}</td><td>skos:{esc(e["edge"])}</td></tr>' for e in maps)
            body.append(f'<h2>Mappings</h2><table><tr><th>system</th><th>code</th><th>term as stated there</th><th>match</th></tr>{rows}</table>')
        ex = [k for k, v in self.views.items() if v["hub"] == nid or (v["kind"] == "tree" and nid in self.tree_members(v["hub"]))]
        if ex:
            body.append('<h2>Appears in</h2><p>' + " · ".join(f'<a href="{rel}examples/{k}.html">{esc(self.g.nodes[self.views[k]["hub"]]["name"])}: the {self.views[k]["kind"]}</a>' for k in ex) + "</p>")
        self.page(f"nodes/{fname(nid)}.html", n["name"], "".join(body), rel)
        self.search.append({"t": n["name"], "u": f"nodes/{fname(nid)}.html", "k": t, "s": nid + " " + " ".join(s["term"] for s in syn)})

    def edge_table(self, edges, rel):
        rows = "".join(f'<tr><td>{self.link(e["from"], rel, True)}</td><td class="rid">{esc(e["edge"])}</td><td>{self.link(e["to"], rel, True) if e["to"] in self.g.nodes else (self.binding_desc(e["to"], rel) if self.g.edge_by_id(e["to"]) else "<code>" + esc(e["to"]) + "</code>")}</td><td>{self.props_html(e, rel) or esc(e.get("props", {}).get("display", ""))}</td></tr>'
                       for e in sorted(edges, key=lambda e: (e["from"], e["to"])))
        return f'<table><tr><th>from</th><th>edge</th><th>to</th><th>properties</th></tr>{rows}</table>'

    def binding_desc(self, eid, rel):
        b = self.g.edge_by_id(eid)
        if not b: return f'<code>{esc(eid)}</code>'
        return f'the {self.link(b["to"], rel)} binding on {self.link(b["from"], rel)} (<a href="{self.edge_href(eid, rel)}">{esc(eid)}</a>)'

    def edge_page(self, e):
        rel = "../"
        rt = self.reltypes.get(e["edge"], {})
        body = [f'<span class="badge b-RelationshipType">reified relationship</span><h1>{esc(e["id"])}</h1>',
                f'<p class="defn">{self.link(e["from"], rel, True)} <b>{esc(e["edge"])}</b> {self.link(e["to"], rel, True) if e["to"] in self.g.nodes else esc(e["to"])}</p>',
                f'<p>{self.props_html({k: v for k, v in e.items() if k != "id"}, rel)}</p>',
                f'<p class="meta">{esc(rt.get("definition", ""))}</p>']
        cites = [x for x in self.g.edges if x["to"] == e["id"]]
        if cites: body.append("<h2>Cited by</h2>" + self.edge_table(cites, rel))
        self.page(f'edges/{fname(e["id"])}.html', e["id"], "".join(body), rel)
        self.search.append({"t": f'{e["id"]} ({e["edge"]})', "u": f'edges/{fname(e["id"])}.html', "k": "relationship"})

    # ---- index pages -----------------------------------------------------------------
    def type_index(self, t):
        nodes = sorted(self.g.by_type(t), key=lambda n: n["name"].lower())
        rows = "".join(f'<tr><td>{self.link(n["id"], "../")}</td><td class="rid">{esc(n["id"])}</td><td class="rid">{esc(n.get("entity_type") or n.get("kind") or n.get("scheme") or "")}</td>'
                       f'<td>{esc((n.get("definition") or "")[:160])}</td></tr>' for n in nodes)
        body = f'<span class="badge b-{t}">{esc(t)}</span><h1>{esc(TYPE_LABEL[t])} · {len(nodes)}</h1><table><tr><th>name</th><th>id</th><th></th><th>definition</th></tr>{rows}</table>'
        self.page(f"types/{t}.html", TYPE_LABEL[t], body, "../")

    def browse(self):
        cards = "".join(f'<div class="card"><h3><a href="types/{t}.html">{esc(TYPE_LABEL[t])}</a></h3><p>{len(self.g.by_type(t))} nodes</p></div>' for t in TYPE_ORDER)
        self.page("browse.html", "Browse", f'<h1>Browse the graph</h1><div class="cards">{cards}</div>', "")

    def relationships(self):
        rows = []
        for rid in sorted(self.reltypes):
            n = self.reltypes[rid]; cnt = sum(1 for e in self.g.edges if e["edge"] == rid)
            rows.append(f'<tr><td><a href="relationships/{fname(rid)}.html">{esc(rid)}</a></td><td>{esc(n.get("inverse") or ("symmetric" if n.get("symmetric") else ""))}</td>'
                        f'<td class="rid">{esc(n.get("formal",""))}</td><td class="rid">{esc(n.get("domain",""))} → {esc(n.get("range",""))}</td><td class="rid">{esc(", ".join(n.get("props") or []))}</td><td>{cnt}</td></tr>')
            uses = [e for e in self.g.edges if e["edge"] == rid]
            self.page(f"relationships/{fname(rid)}.html", rid, f'<span class="badge b-RelationshipType">RelationshipType</span><h1>{esc(rid)} · {esc(n.get("name",""))}</h1>'
                      f'<p class="defn">{esc(n.get("definition",""))}</p><p class="meta">{self.link(rid, "../")} · node page</p><h2>Assertions ×{len(uses)}</h2>' + self.edge_table(uses, "../"), "../")
        self.page("relationships.html", "Relationship types", f'<h1>Relationship types</h1><p class="meta">The catalog of 07 §1 plus the structural edges of 03 §2, as declared in the graph.</p>'
                  f'<table><tr><th>type</th><th>inverse</th><th>formal</th><th>domain → range</th><th>properties</th><th>uses</th></tr>{"".join(rows)}</table>', "")

    def tree_members(self, root):
        out, stack = [], [root]
        while stack:
            n = stack.pop()
            if n in out: continue
            out.append(n); stack.extend(self.cards.children(n))
        return out

    def tree_page_js(self, root, rel):
        """Interactive layer: click a card to light up its relationships within the tree and show a detail panel."""
        members = self.tree_members(root)
        c = self.cards
        info = {}
        for nid in members:
            n = self.g.nodes[nid]
            anat, inh = c.anatomy_str(nid)
            rels = []
            for label, etype, direction in __import__("render_cards").CONTAINERS:
                for e in self.g.edges:
                    if e["edge"] != etype: continue
                    other = None
                    if direction in ("out", "both") and e["from"] == nid and e["to"] in members: other = e["to"]
                    elif direction in ("in", "both") and e["to"] == nid and e["from"] in members: other = e["from"]
                    if other: rels.append({"label": label.lower(), "other": other, "props": c.edge_line(e)})
            ctx = {k: [c.name(x) for x in v[0]] for k, v in c.context(nid).items() if v[0]}
            info[nid] = {"name": n["name"], "kind": c.kind(nid), "definition": n.get("definition", ""), "anatomy": anat + (f" (inherited from {c.name(inh)})" if inh else ""),
                         "mappings": [c.code_str(*m) for m in c.mappings(nid)], "context": ctx, "rels": rels, "href": self.node_href(nid, rel)}
        js = """
(function(){var INFO=%s;var panel=document.getElementById('treepanel');var svg=document.querySelector('.diagram svg');
function clear(){svg.querySelectorAll('.mini').forEach(g=>{g.classList.remove('lit','sel');var r=g.querySelector('rect');r.setAttribute('stroke','#cbd5e1');r.setAttribute('stroke-width','1')});}
function lit(id,color){var g=svg.querySelector('#m-'+CSS.escape(id));if(!g)return;var r=g.querySelector('rect');r.setAttribute('stroke',color);r.setAttribute('stroke-width','2.5');}
function show(id){clear();var d=INFO[id];if(!d)return;lit(id,'#1f2937');
var h='<div class="tp-head"><b>'+d.name+'</b> <span class="rid">'+d.kind+' · '+id+'</span> · <a href="'+d.href+'">open its mat</a></div>';
if(d.definition)h+='<p>'+d.definition+'</p>';h+='<p class="meta">'+d.anatomy+'</p>';
if(d.rels.length){h+='<h4>Relationships within this tree</h4><ul>';d.rels.forEach(r=>{lit(r.other,'#7c3aed');h+='<li><span class="lbl">'+r.label+'</span> <a href="#" data-go="'+r.other+'">'+INFO[r.other].name+'</a>'+(r.props?' <span class="props">'+r.props+'</span>':'')+'</li>'});h+='</ul>'}else{h+='<p class="meta">No relationships to other members of this tree.</p>'}
if(d.mappings.length)h+='<p class="meta">'+d.mappings.join(' · ')+'</p>';
var ctx=Object.keys(d.context).map(k=>k.toLowerCase()+': '+d.context[k].join(', ')).join(' · ');if(ctx)h+='<p class="meta">'+ctx+'</p>';
panel.innerHTML=h;panel.hidden=false;panel.querySelectorAll('a[data-go]').forEach(a=>a.addEventListener('click',e=>{e.preventDefault();show(a.dataset.go)}));}
svg.querySelectorAll('.mini').forEach(g=>{g.addEventListener('click',e=>{e.preventDefault();show(g.dataset.node)});g.style.cursor='pointer'});
})();""" % json.dumps(info, ensure_ascii=False)
        return js

    def examples(self):
        cards = []
        REPORTS = {"pleural-effusion-mat": "pleural-effusion.report.jsonl", "acute-pyelonephritis-mat": "pyelonephritis.report.jsonl"}
        for k, v in self.views.items():
            rel = "../"
            hub = self.g.nodes[v["hub"]]
            title = f'{hub["name"]}: the {v["kind"]}'
            if v["kind"] == "mat":
                svg = self.linked_svg(self.cards.mat(v["hub"]), rel)
                intro = "One context object, drawn in full, with everything one relationship away as cards in labelled containers. Hover a card for its detail; click it to open its own mat."
                extra = ""
            else:
                svg = self.cards.tree(v["hub"])   # not linked: click is the interaction here
                intro = "The is-a outline of the family: one mini-card per row, indented by subsumption. Click a card to see its relationships within the tree and a fuller card."
                extra = f'<div id="treepanel" class="treepanel" hidden></div><script>document.querySelector("main").classList.add("tree-page");{self.tree_page_js(v["hub"], rel)}</script>'
            report = os.path.join(EXAMPLES_DIR, REPORTS.get(k, "_"))
            rep = f'<h2>Report-plane sample</h2><p class="meta">Observations pointing into the vocabulary, with report edges citing the relationship they express (03 §5).</p><pre>{esc(open(report, encoding="utf-8").read())}</pre>' if os.path.exists(report) else ""
            body = (f'<h1>{esc(title)}</h1><p class="meta">{intro} · View: <a href="{rel}docs/next-gen-schema/examples/{v["file"]}">{v["file"]}</a> · '
                    f'discussed in <a href="{rel}docs/next-gen-schema/08-worked-examples.html">08</a> · decisions in <a href="{rel}docs/plans/2026-09-02-mat-and-tree-decisions.html">the mat-and-tree document</a></p>'
                    f'<div class="diagram">{svg}</div>{extra}{rep}')
            self.page(f"examples/{k}.html", title, body, rel)
            cards.append(f'<div class="card"><h3><a href="examples/{k}.html">{esc(title)}</a></h3><p>{esc(intro[:120])}…</p></div>')
            self.search.append({"t": title, "u": f"examples/{k}.html", "k": "example"})
        dossiers = "".join(f'<div class="card"><h3>{self.link(nid, "")}</h3><p>object dossier · <a href="docs/next-gen-schema/diagrams/{svg}">diagram</a></p></div>' for nid, svg in DOSSIERS.items())
        self.page("examples.html", "Examples", f'<h1>Worked examples</h1><h2>Mats and trees</h2><div class="cards">{"".join(cards)}</div>'
                  f'<h2>Object dossiers</h2><p class="meta">The earlier single-node examples, rendered from examples/*.json by render_neighborhood.py.</p><div class="cards">{dossiers}</div>', "")

    # ---- documents -------------------------------------------------------------------
    def render_md(self, src, dst, rel, title_fallback):
        text = open(src, encoding="utf-8").read()
        fm, body = None, text
        m = re.match(r'^---\n(.*?)\n---\n', text, re.S)
        if m:
            try: fm = yaml.safe_load(m.group(1))
            except Exception: fm = None
            body = text[m.end():]
        # links: .md -> .html, dir/ -> dir/index.html
        body = re.sub(r'\]\(([^)\s]+?)\.md(#[^)]*)?\)', lambda mm: f']({mm.group(1)}.html{mm.group(2) or ""})', body)
        body = re.sub(r'\]\(([^)\s:]+?)/\)', r'](\1/index.html)', body)
        htmlb = markdown.markdown(body, extensions=["tables", "fenced_code", "toc", "sane_lists", "md_in_html"])
        title = (fm or {}).get("title") or title_fallback
        fmh = ""
        if fm:
            items = []
            for k in ("type", "status", "tags", "generated", "verified"):
                if fm.get(k) is not None: items.append(f'<dt>{esc(k)}</dt><dd>{esc(fm[k] if not isinstance(fm[k], (dict, list)) else json.dumps(fm[k], default=str))}</dd>')
            srcs = fm.get("sources") or []
            if srcs:
                ss = []
                for s in srcs:
                    if not isinstance(s, dict): continue
                    r = str(s.get("resource", ""))
                    href = r if r.startswith("http") else rel + r.lstrip("/").replace(".md", ".html")
                    ss.append(f'<a href="{esc(href)}">{esc(s.get("title") or r)}</a>')
                items.append("<dt>sources</dt><dd>" + " · ".join(ss) + "</dd>")
            if fm.get("description"): fmh += f'<p class="defn">{esc(fm["description"])}</p>'
            fmh += f'<dl class="fm">{"".join(items)}</dl>'
        self.page(dst, title, f'<div class="doc">{fmh}{htmlb}</div>', rel)
        self.search.append({"t": title, "u": dst, "k": "document", "s": (fm or {}).get("description", "")})

    def dir_index(self, dst, label, rel):
        files = sorted(f for f in os.listdir(dst) if f != "index.html")
        items = "".join(f'<li><a href="{esc(f)}">{esc(f)}</a></li>' for f in files)
        self.page(os.path.join(os.path.relpath(dst, self.out), "index.html"), label, f'<h1>{esc(label)}/</h1><ul>{items}</ul>', rel)

    def documents(self):
        # copy the bundle's non-markdown assets so relative links keep working
        for sub in ("diagrams", "examples", "tools", "graph", "archive", "explorations"):
            s = os.path.join(BASE, sub)
            if not os.path.isdir(s): continue
            dst = os.path.join(self.out, "docs/next-gen-schema", sub)
            shutil.copytree(s, dst, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__"))
            self.dir_index(dst, f"docs/next-gen-schema/{sub}", "../../../")
        plans = os.path.join(ROOT, "docs/plans")
        if os.path.isdir(plans):
            for p in sorted(glob.glob(os.path.join(plans, "*.md"))):
                self.render_md(p, f"docs/plans/{os.path.basename(p)[:-3]}.html", "../../", os.path.basename(p))
            self.dir_index(os.path.join(self.out, "docs/plans"), "docs/plans", "../../")
        shutil.copy(os.path.join(ROOT, "docs/check_bundle.py"), os.path.join(self.out, "docs/check_bundle.py"))
        for f in ("cde.schema.json", "SampleDES.cdes.json"):
            if os.path.exists(os.path.join(ROOT, f)): shutil.copy(os.path.join(ROOT, f), os.path.join(self.out, f))
        for p in sorted(glob.glob(os.path.join(BASE, "**", "*.md"), recursive=True)):
            relp = os.path.relpath(p, BASE)
            if relp.startswith(("tools/", "diagrams/", "examples/")): continue
            self.render_md(p, f'docs/next-gen-schema/{relp[:-3]}.html', "../" * (1 + relp.count("/")) + "../", os.path.basename(p))
        for p in sorted(glob.glob(os.path.join(NOTES, "*.md"))):
            self.render_md(p, f'notes/{os.path.basename(p)[:-3]}.html', "../", os.path.basename(p))
        self.render_md(os.path.join(ROOT, "index.md"), "bundle.html", "", "Knowledge bundle")
        docs = [(os.path.basename(p)[:-3], p) for p in sorted(glob.glob(os.path.join(BASE, "*.md"))) if not p.endswith("index.md")]
        notes = [(os.path.basename(p)[:-3], p) for p in sorted(glob.glob(os.path.join(NOTES, "*.md"))) if not p.endswith("index.md")]
        def row(name, p, d):
            t = open(p, encoding="utf-8").read()
            m = re.search(r'^title:\s*(.+)$', t, re.M); desc = re.search(r'^description:\s*(.+)$', t, re.M)
            return f'<tr><td><a href="{d}/{name}.html">{esc((m.group(1) if m else name).strip().strip(chr(34)))}</a></td><td class="rid">{esc((desc.group(1) if desc else "").strip().strip(chr(34)))}</td></tr>'
        self.page("documents.html", "Documents", f'<h1>Documents</h1><h2>Next-gen schema analysis</h2><table>{"".join(row(n, p, "docs/next-gen-schema") for n, p in docs)}</table>'
                  f'<h2>Notes</h2><table>{"".join(row(n, p, "notes") for n, p in notes)}</table><p class="meta"><a href="bundle.html">Bundle index</a> · <a href="docs/next-gen-schema/graph/README.html">Graph format</a></p>', "")

    def home(self):
        counts = " · ".join(f'<a href="types/{t}.html">{len(self.g.by_type(t))} {TYPE_LABEL[t].lower()}</a>' for t in TYPE_ORDER)
        ex = "".join(f'<div class="card"><h3><a href="examples/{k}.html">{esc(self.g.nodes[v["hub"]]["name"])}: the {v["kind"]}</a></h3><p>{"one object, one hop out, cards in containers" if v["kind"] == "mat" else "the is-a outline of the family, click a card for its relationships"}</p></div>' for k, v in self.views.items())
        body = (f'<h1>Next-generation CDE vocabulary</h1><p class="defn">The working graph behind the RSNA/ACR common data element redesign: finding classes, diagnoses, data elements, anatomy, '
                f'and the typed relationships between them, generated from the canonical form in <a href="docs/next-gen-schema/graph/README.html">docs/next-gen-schema/graph</a>. Every node is a page; every edge is a link.</p>'
                f'<p class="meta">{counts} · {len(self.g.edges)} edges · <a href="graph.jsonl">graph.jsonl</a></p>'
                f'<h2>Worked examples</h2><div class="cards">{ex}</div>'
                f'<h2>Start from</h2><div class="cards"><div class="card"><h3><a href="browse.html">Browse by node type</a></h3><p>Indexes of every node.</p></div>'
                f'<div class="card"><h3><a href="relationships.html">Relationship types</a></h3><p>The edge catalog with every assertion listed.</p></div>'
                f'<div class="card"><h3><a href="documents.html">Documents</a></h3><p>The analysis bundle and the sanitized notes.</p></div></div>')
        self.page("index.html", "Next-generation CDE vocabulary", body, "")

    def build(self):
        if os.path.isdir(self.out): shutil.rmtree(self.out)
        os.makedirs(self.out)
        open(os.path.join(self.out, "site.css"), "w").write(CSS)
        open(os.path.join(self.out, ".nojekyll"), "w").write("")
        open(os.path.join(self.out, "graph.jsonl"), "w", encoding="utf-8").write(canonical_text(self.g.objects()))
        for n in self.g.nodes.values(): self.node_page(n)
        for e in self.g.edges:
            if e.get("id"): self.edge_page(e)
        for t in TYPE_ORDER: self.type_index(t)
        self.browse(); self.relationships(); self.examples(); self.documents(); self.home()
        open(os.path.join(self.out, "search.json"), "w", encoding="utf-8").write(json.dumps(self.search, ensure_ascii=False))
        open(os.path.join(self.out, "search.js"), "w").write(JS)
        return len(self.g.nodes), len(self.search)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default=os.path.join(ROOT, "site"))
    a = ap.parse_args()
    n, s = Site(a.out).build()
    print(f"built {a.out}: {n} node pages, {s} search entries")
