from pathlib import Path
from rdflib import Graph

ROOT = Path(__file__).resolve().parent.parent
p = ROOT / "standalone" / "radcde-standalone.ttl"

if not p.exists():
    print("SKIP optional standalone not generated:", p)
else:
    g = Graph().parse(p, format="turtle")
    print(p.name, len(g), "triples")
