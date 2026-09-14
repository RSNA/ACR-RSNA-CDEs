# -*- coding: utf-8 -*-
"""Verify every RadLex binding against the configured source index."""
from pathlib import Path
import json
from radlex_config import RADLEX_VERSION

ROOT = Path(__file__).resolve().parent.parent
LOOSE = {"broadMatch", "narrowMatch", "closeMatch", "relatedMatch"}

def main():
    ai=json.loads((Path(__file__).with_name("anatomy.json")).read_text())
    g=json.loads((ROOT/"graph"/"definition-graph.json").read_text())
    used=[]
    for n in g["nodes"]:
        # Native AnatomicLocation nodes are RadLex concepts themselves, not local
        # concepts whose bindings need terminology-label verification.
        if n.get("node") == "AnatomicLocation":
            continue
        for b in n.get("bindings",[]):
            if b.get("system")=="RADLEX":
                used.append((b["code"], b.get("source_label") or n.get("name"), b.get("match","exactMatch"), f"{n['node']} {n['id']} {n.get('name','')}"))
        comp=n.get("radlex_composition") or {}
        base=comp.get("base")
        if base:
            used.append((base["code"], base.get("label") or base["code"], "exactMatch", f"{n['node']} {n['id']} {n.get('name','')} radlex_composition base"))
        for m in comp.get("modifiers",[]):
            used.append((m["code"], m.get("label") or m["code"], "exactMatch", f"{n['node']} {n['id']} {n.get('name','')} radlex_composition modifier"))
    unresolved=[]; mismatched=[]; loose=[]; seen=set()
    for code, recorded, match, where in used:
        seen.add(code)
        nd=ai["classes"].get(code)
        if not nd:
            unresolved.append((code,recorded,where)); continue
        actual=nd.get("label") or code
        if match in LOOSE:
            loose.append((code,recorded,actual,match,where)); continue
        accepted={actual.lower()}
        accepted.update(x.lower() for x in nd.get("synonyms",[]))
        accepted.update(x.lower() for x in nd.get("acronyms",[]))
        if recorded.lower() not in accepted:
            mismatched.append((code,recorded,actual,where))
    print(f"RadLex {RADLEX_VERSION} parsed: {sum(1 for r,n in ai['classes'].items() if n.get('label') and n.get('label') != r):,} English labels")
    print(f"{len(seen)} distinct RadLex codes")
    print(f"{len(used)} references")
    if unresolved:
        print("UNRESOLVED:")
        for x in unresolved: print(" ",x)
    if mismatched:
        print("STRICT LABEL MISMATCH:")
        for x in mismatched: print(" ",x)
    if loose:
        print(f"{len(loose)} declared loose matches")
    bad=len(unresolved)+len(mismatched)
    print("every code resolves and every strict label agrees" if not bad else f"{bad} problems")
    return 1 if bad else 0

if __name__ == "__main__": raise SystemExit(main())
