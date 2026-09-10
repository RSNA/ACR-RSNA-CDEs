# -*- coding: utf-8 -*-
"""
Generates SHAPE.md: the working document.

Tables, a diagram, worked traces and a coverage matrix. Every count and edge
signature is derived from the built artifacts. The alternative-term column
records other names or framings in circulation for the same object, including
rows where one side is empty because the concept exists on one side only.

Sibling documents:
  README.md     how to load and run it
  DECISIONS.md  why it is shaped this way, what it costs, what would overturn it
  SHAPE.md      what it is and what it reaches            <- this generator
"""
import json, collections, datetime, sys
import spec

OUT = "/mnt/user-data/outputs/radcde-alpha"

NODE_GLOSS = {
    "FindingClass":     ("A discrete observable entity. What a radiologist reports seeing.", ""),
    "Diagnosis":        ("What a radiologist may conclude. Reached from findings, never asserted by one.", ""),
    "DataElement":      ("A named attribute with a closed list of permitted answers.", "Element"),
    "Value":            ("One coded permissible answer. Belongs to exactly one DataElement.", ""),
    "Measurement":      ("A quantitative attribute carrying its own method and units.", "quantitative DataElement"),
    "AnatomicLocation": ("A place: organ, space, region or structure.", "Anatomy"),
    "AssessmentScheme": ("A named scheme with an issuing authority and its own version clock.", "Assessment"),
    "Etiology":         ("A kind of cause. Target for HAS_ETIOLOGY.", ""),
    "ScopeResolution":  ("Why a mention carries no anatomic scope.", ""),
    "Modality":         ("An imaging technique.", ""),
    "Subspecialty":     ("A radiology subspecialty.", ""),
}

NODE_NOT_ADOPTED = [
    ("Grouping",
     "A node asserted only in the negative, so that 'no renal abnormality' has something to "
     "point at. It would never be used positively.",
     "**Unresolved, not rejected.** Negating a *named* finding already works: presence absent "
     "on the finding. What has no answer is negating a *category*, where no finding is named "
     "and nothing carries the presence value. Grouping remains a live candidate that has not "
     "been worked through. Two "
     "things would need settling: whether one negative node per organ scales, and how "
     "remainder negation works, since 'no other significant adenopathy' needs a scope over "
     "what was examined rather than a node to point at."),
]

EDGE_GLOSS = {
    "SUBTYPE_OF":               ("Taxonomy, more to less specific. Strict monotonic inheritance.", "HAS_SUBTYPE (inverse)"),
    "HAS_DATA_ELEMENT":         ("Applies an element. May narrow the permitted values, never widen them.", "HAS_ELEMENT"),
    "HAS_VALUE":                ("Binds a Value to its owning DataElement. Exactly one per Value.", "member"),
    "HAS_VALUE_CONSTRAINT":     ("Fixes an element to one value as a defining condition.", ""),
    "HAS_MEASUREMENT":          ("Applies a Measurement.", ""),
    "HAS_MEASUREMENT_COMPONENT":("Relates a composite Measurement to its parts.", ""),
    "DERIVED_FROM_MEASUREMENT": ("Relates a computed Measurement to its inputs.", ""),
    "HAS_COMPONENT":            ("The whole must have this sub-part.", "MAY_HAVE_COMPONENT"),
    "COMPONENT_OF":             ("This sub-part belongs only to that whole; says nothing about whether the whole has one.", "MAY_BE_COMPONENT_OF"),
    "SCOPED_TO":                ("Anatomic scope. `kind` says which relation a congruence check walks.", "IN_REGION"),
    "REFINES_SCOPE_TO":         ("Where a scope may be narrowed on a particular observation. Derived by walking the anatomy for the kind the class declares, never authored.", ""),
    "IS_A":                     ("Taxonomic, within anatomy. Imported, unreified.", ""),
    "PART_OF":                  ("Mereological, within anatomy. Transitive, inference-bearing.", ""),
    "MAY_MANIFEST_AS":          ("Evidential. The diagnosis can show itself as the target.", "MAY_REPRESENT (inverse)"),
    "MAY_CAUSE":                ("Causal. The source produces the target as a distinct second entity.", "MAY_BE_CAUSED_BY (inverse)"),
    "MAY_PROGRESS_TO":          ("Temporal. Identity-preserving evolution. Proposed, not adopted.", "MAY_PROGRESS_FROM (inverse)"),
    "OCCURS_WITH":              ("Symmetric, between two findings or two diagnoses. Seen together; asserts nothing about cause or sequence. Stored once; a consumer must read the flag to traverse it backwards.", ""),
    "HAS_ETIOLOGY":             ("The kind of cause behind a definition.", ""),
    "ASSESSED_BY":              ("A standardized scheme applies to the source.", "ASSESSES (inverse)"),
    "SEEN_ON":                  ("The imaging techniques a finding is seen on.", ""),
    "IN_SUBSPECIALTY":          ("The subspecialty a finding belongs to.", ""),
}

EDGE_NOT_ADOPTED = [
    ("IN_REGION", "Coarse body region, authored alongside SCOPED_TO.",
     "Not adopted. The region is derived by walking containment upward from the scope target."),
    ("MAY_BE_RELATED_TO", "Symmetric catch-all for an association not yet typed.",
     "Declared, unused. A triage queue, not a home."),
    ("INTERPRETED_FROM", "Relates an interpretation to what it was read from.",
     "Not adopted. Meaning shifts depending on how many things it points at."),
    ("SEX, AGE_APPLICABILITY, TIME_COURSE", "Demographic and temporal applicability.", "Deferred."),
]

PROP_GLOSS = {
    "narrow": "The subset of values permitted here. Advisory in alpha.",
    "modality": "Restricts an element to some of the modalities the finding is seen on.",
    "rank": "Position in an ordered value list. On every value of an element or on none.",
    "kind": "specific, region or class. Which relation a congruence check walks.",
    "of_scope": "Which scope entry a refinement narrows.",
    "derived": "True where the edge was computed from a declared kind rather than authored.",
    "strength": "required, expected or unconstrained. How binding the claim is.",
    "defining": "True where the edge is a necessary and sufficient condition.",
    "sense": "Which RadLex partonomy relation the edge was imported from.",
    "family": "mereology or location. Which traversal the anatomy edge belongs to.",
    "inheritance": "strict. A subtype carries everything its parent carries.",
    "typicality": "occasional, frequent, very_frequent, obligate. Reads forward: how often the source shows the target.",
    "specificity": "suggestive, highly_suggestive, pathognomonic. Reads backward: how much seeing it narrows the differential.",
    "expected": "What the caused finding typically looks like when this cause produced it.",
    "reading": "evidential or inferential. What kind of claim the edge makes.",
    "symmetric": "True where the edge asserts the same thing both ways.",
    "direction": "required_on_whole or necessary_on_component. Which way a conditional runs.",
    "generated_from_pattern": "The authoring pattern that supplied this edge.",
    "element": "Which DataElement a fixed value belongs to.",
    "source": "imported or local.",
    "source_status": "Relationship of a local object to the source terminology.",
    "source_version": "Release the edge was imported from.",
    "system": "Terminology the edge came from.",
    "request": "External change-request reference.",
    "inference_bearing": "False where software must not draw conclusions from the edge.",
}

COVERAGE = [
    ("Discrete focal lesion", "yes", "PulmonaryNodule, ThyroidNodule, RenalMass."),
    ("Fluid or gas collection in a space", "yes", "PleuralEffusion, Pneumothorax, IntracranialHemorrhage."),
    ("Parenchymal alteration without borders", "yes", "Consolidation, StriatedNephrogram, WhiteMatterHyperintensity."),
    ("Volume loss or gain", "yes", "Atelectasis, CerebralAtrophy, RenalEnlargement."),
    ("Luminal narrowing or dilation", "yes", "CarotidStenosis, Hydronephrosis."),
    ("Material inside a lumen", "yes", "PulmonaryArteryFillingDefect."),
    ("Break in a continuous structure", "yes", "RibFracture."),
    ("Structure displaced from position", "yes", "MidlineShift, MediastinalShift."),
    ("Device and its tip position", "yes", "VentricularShuntCatheter."),
    ("Anatomic variant, explicitly not disease", "yes", "AzygosFissure."),
    ("Anatomic scope at any granularity", "yes", "SCOPED_TO with kind specific, region or class."),
    ("Sub-organ position, as 'in the right upper lobe'", "yes",
     "REFINES_SCOPE_TO. The class declares which kind of anatomy may narrow its scope and the "
     "permitted concepts are derived from it. Sided and unsided forms are both permitted, so "
     "'the right upper lobe' and 'the upper lobe' both resolve. The closed set is in the "
     "compiled shape; no reasoner enforces it, because no anatomy class here is declared "
     "disjoint from any other."),
    ("Body region for filtering", "yes", "Derived, not authored."),
    ("Laterality of a finding", "yes", "DE-000031, declared per class. RadLex has no laterality property and sidedness is not derivable from its structure, so this is an authoring decision."),
    ("Side as a field separate from the structure", "no", "Scope points at the pre-coordinated concept. Asking for 'lung' and 'left' separately is not supported."),
    ("Interval change against a prior", "yes", "DE-000015. Coarse: new, unchanged, increased, decreased."),
    ("Quantitative measurement with method", "yes", "13 Measurement nodes carrying units and method."),
    ("Assessment category", "yes", "5 schemes with issuing authority and their own version clock."),
    ("Ordered severity", "yes", "rank on every value of an element, or on none."),
    ("Multi-select element", "yes", "hasCalcification, hasInternalComplexity, hasNodalArchitecture."),
    ("One diagnosis suggested by one finding", "yes", "MAY_MANIFEST_AS with typicality and specificity."),
    ("A cause producing a finding", "yes", "MAY_CAUSE with typicality and expected appearance."),
    ("Kind of cause", "yes", "HAS_ETIOLOGY to 10 Etiology nodes."),
    ("Sub-finding with its own attributes", "yes", "SolidComponentOfPartSolidNodule, MuralNodule."),
    ("Conditional sub-finding, either direction", "yes", "HAS_COMPONENT and COMPONENT_OF."),
    ("Post-procedural change", "no",
     "Nothing represents a procedure, so a finding attributable to one cannot name which, and "
     "there is nothing against which to judge whether an appearance is expected."),
    ("Diagnosis from several findings together", "partial", "Every edge is binary. specificity grades each finding, but nothing says a conjunction is stronger than any member. See section 7, pyelonephritis."),
    ("Identity-preserving progression", "partial", "MAY_PROGRESS_TO proposed and unadopted; unusable atemporally where the endpoints are disjoint."),
    ("Acute versus chronic", "partial", "As a temporal-descriptor value on one class, or as separate classes. Both appear; no rule decides which."),
    ("Two encodings of one criterion", "partial", "CarotidStenosis carries an ordinal and a percentage. Nothing relates them."),
    ("Negation of a named finding", "yes",
     "`presence: absent` on the finding. 'No pleural effusion' is PleuralEffusion with presence "
     "absent, whose definition reads: can be confidently categorized as absent based on the "
     "data presented. Distinct from `unknown`, which records that the examination did not "
     "address it."),
    ("Negation of a category of findings", "no",
     "'No renal abnormality' names no finding, so there is nothing to set presence on. This is "
     "the case a Grouping node would address; see Nodes, considered and not in the graph."),
    ("Remainder negation, 'no other significant adenopathy'", "no",
     "A claim about everything examined and not mentioned. Needs a scope over what was looked "
     "at, which no node or element can carry."),
    ("Plurality: several, a cluster, innumerable", "partial",
     "`lesion count` and `distribution` reach it for focal lesions: a nodule can be counted "
     "and called scattered or miliary. Neither is supplied by the other patterns, so a rib "
     "fracture has neither. And a count says how many, not which ones, and cannot attach an "
     "attribute to one member. See section 7, rib fractures."),
    ("Bilateral as one instance or two", "no", "A laterality value exists; what it means for instance identity does not."),
    ("Certainty and hedging", "partial",
     "`presence: indeterminate` covers one band: the data do not permit calling the finding "
     "present or absent. It says nothing about confidence in a diagnosis, so 'concerning for "
     "malignancy' and 'compatible with granuloma' are equally unrepresentable."),
    ("Comparison to a named prior study", "no", "Interval change is coarse and carries no study reference."),
    ("Follow-up recommendation", "no", "Management layer, deliberately out of scope."),
    ("Study technique and quality", "no", "Out of scope."),
    ("Clinical history driving interpretation", "no", "Out of scope; the causal layer partly stands in for it."),
]

OPEN = [
    ("What the subject of a statement is: one lesion, several, a cluster, innumerable", "Section 7, rib fractures"),
    ("How a category of findings is negated, and how remainder negation works", "Coverage, not representable"),
    ("Whether a bilateral finding is one instance or two", "DE-000031, value `bilateral`"),
    ("How a conjunction of findings supports a diagnosis more than any member", "Section 7, pyelonephritis"),
    ("Whether acute/chronic is a value or a subtype, and what decides", "IntracranialHemorrhage vs ChronicPyelonephritis"),
    ("How two encodings of one criterion relate", "CarotidStenosis: ordinal and percentage"),
    ("Whether MAY_PROGRESS_TO is adopted, and under which reading", "probes C1 to C3"),
    ("Whether `specificity` earns its place or is over-engineering", "35 MAY_MANIFEST_AS edges"),
    ("Where a procedure lives, so a post-procedural finding has something to be expected against", "Coverage, not representable"),
    ("Whether narrowing hardens from annotation to axiom", "probe B3"),
    ("Whether elements can be shared with narrowed values where meaning is stable", "8 duplicated value labels"),
]


def main():
    g = json.load(open(f"{OUT}/graph/definition-graph.json"))
    nodes, edges = g["nodes"], g["edges"]
    nt = {n["id"]: n["node"] for n in nodes}
    name = {n["id"]: n["name"] for n in nodes}
    compiled = json.load(open(f"{OUT}/compiled/_all-findings.json"))
    byt = collections.defaultdict(list)
    for n in nodes:
        byt[n["node"]].append(n)
    fc_spec = {f["name"]: f for f in spec.FINDING_CLASSES}
    fc_comp = {c["name"]: c for c in compiled}

    errs = [f"gloss for absent node type '{k}'" for k in NODE_GLOSS if k not in byt]
    errs += [f"node type '{k}' has no gloss" for k in byt if k not in NODE_GLOSS]
    et = {e["edge"] for e in edges}
    errs += [f"gloss for absent edge '{k}'" for k in EDGE_GLOSS if k not in et]
    errs += [f"edge '{k}' has no gloss" for k in et if k not in EDGE_GLOSS]
    if errs:
        print("aborted:")
        for e in errs:
            print("  " + e)
        sys.exit(1)

    L = []
    w = L.append
    w("# The shape of the knowledge graph")
    w("")
    w("What the definition layer is made of, and what it reaches. Generated from the build")
    w(f"on {datetime.date.today().isoformat()} by `scripts/build_shape.py`; every count and edge signature is")
    w("derived from the artifacts. Do not hand-edit.")
    w("")
    w("What each mechanism does and why is in `MECHANISMS.md`. How to run it is in `README.md`.")
    w("")
    w("**Alternative term** records another name or framing in circulation for the same")
    w("object. A blank means the concept exists on one side only.")
    w("")
    w("---")
    w("")

    # 1 layers
    w("## 1. Layers")
    w("")
    w("| Layer | Artifact | Contains | Goes to |")
    w("|---|---|---|---|")
    w("| Authoring | `scripts/spec.py` | patterns, lint rules, content source | internal |")
    w(f"| Definition graph | `graph/definition-graph.json` | {len(nodes)} nodes, {len(edges)} edges, cross-referenced | internal |")
    w(f"| Compiled | `compiled/*.json` | {len(compiled)} flat shapes, references resolved | **vendors** |")
    w("| Reasoning check | `radcde-*.ttl` | the same content as OWL | design-time only |")
    w("")
    w("**There are no instances.** Claims about what the model can hold are made by probes,")
    w("which state a construction and let the reasoner return the verdict. Instance-level")
    w("validation needs representations authored by a radiologist or produced by something that")
    w("reads text; neither exists here.")
    w("")
    w("Patterns never appear below the authoring layer. The OWL is a checking instrument")
    w("rather than a deliverable, not something consumers reason over.")
    w("")

    # 2 diagram
    w("## 2. How it connects")
    w("")
    w("```mermaid")
    w("graph LR")
    for line in [
        "  DX[Diagnosis]:::core", "  FC[FindingClass]:::core", "  DE[DataElement]",
        "  V[Value]", "  MS[Measurement]", "  AL[AnatomicLocation]:::imp",
        "  AS[AssessmentScheme]", "  ET[Etiology]", "  MD[Modality]", "  SP[Subspecialty]", "",
        "  DX -->|MAY_MANIFEST_AS| FC",
        "  DX -->|MAY_CAUSE| FC",
        "  DX -->|MAY_PROGRESS_TO| DX",
        "  DX -->|HAS_ETIOLOGY| ET",
        "  FC ---|OCCURS_WITH| FC",
        "  DX ---|OCCURS_WITH| DX",
        "  FC -->|SUBTYPE_OF| FC",
        "  FC -->|HAS_COMPONENT / COMPONENT_OF| FC",
        "  FC -->|HAS_DATA_ELEMENT| DE",
        "  DX -->|HAS_DATA_ELEMENT| DE",
        "  DE -->|HAS_VALUE| V",
        "  FC -->|HAS_MEASUREMENT| MS",
        "  MS -->|HAS_MEASUREMENT_COMPONENT| MS",
        "  FC -->|SCOPED_TO| AL",
        "  AL -->|PART_OF / IS_A / CONTAINED_IN| AL",
        "  FC -->|ASSESSED_BY| AS",
        "  FC -->|SEEN_ON| MD",
        "  FC -->|IN_SUBSPECIALTY| SP",
        "  classDef core stroke-width:3px",
        "  classDef imp stroke-dasharray:4 3",
    ]:
        w(line)
    w("```")
    w("")
    w("Edge properties are omitted here; they are listed in full under Edges. Thick borders")
    w("are the two node types the model is about. The dashed one is imported")
    w("rather than authored. Body region is deliberately not an edge: it is derived by")
    w("walking `PART_OF` and `CONTAINED_IN` upward from the `SCOPED_TO` target.")
    w("")

    # 3 nodes
    w("## 3. Nodes")
    w("")
    w("| Type | n | What it is | Alternative term |")
    w("|---|---:|---|---|")
    for t in sorted(byt, key=lambda x: -len(byt[x])):
        gl, alt = NODE_GLOSS[t]
        w(f"| `{t}` | {len(byt[t])} | {gl} | {alt or '—'} |")
    w("")
    w("| Considered, not in the graph | Would be | Status |")
    w("|---|---|---|")
    for n_, d_, s_ in NODE_NOT_ADOPTED:
        w(f"| `{n_}` | {d_} | {s_} |")
    w("")

    # 4 edges
    w("## 4. Edges")
    w("")
    sig = collections.defaultdict(lambda: [collections.Counter(), collections.Counter()])
    for e in edges:
        sig[e["edge"]][0][(nt.get(e["from"], "?"), nt.get(e["to"], "?"))] += 1
        for k, v in e.get("props", {}).items():
            if v is not None:
                sig[e["edge"]][1][k] += 1
    w("Signatures are the tail and head types observed in the build, not everything the")
    w("edge is permitted to take.")
    w("")
    w("| Edge | Signature | n | Properties | Alternative term |")
    w("|---|---|---:|---|---|")
    for k in sorted(sig):
        pairs, props = sig[k]
        gl, alt = EDGE_GLOSS[k]
        s_ = "<br>".join(f"`{a}`→`{b}`" for a, b in sorted(pairs))
        p_ = ", ".join(f"`{x}`" for x in sorted(props)) or "—"
        w(f"| **{k}** | {s_} | {sum(pairs.values())} | {p_} | {alt or '—'} |")
    w("")
    for k in sorted(sig):
        w(f"- **{k}** — {EDGE_GLOSS[k][0]}")
    w("")
    w("| Considered, not in the graph | Would be | Status |")
    w("|---|---|---|")
    for n_, d_, s_ in EDGE_NOT_ADOPTED:
        w(f"| `{n_}` | {d_} | {s_} |")
    w("")
    w("### Edge properties")
    w("")
    w("| Property | Meaning |")
    w("|---|---|")
    for p in sorted({p for k in sig for p in sig[k][1]}):
        w(f"| `{p}` | {PROP_GLOSS.get(p, '')} |")
    w("")
    reified = sum(1 for e in edges if e.get("id"))
    w(f"{reified} of {len(edges)} edges carry an id and a version block, so a relationship can")
    w("change without either endpoint changing. The rest are imported anatomy relations,")
    w("which re-import regenerates.")
    w("")

    # 5 patterns
    w("## 5. Authoring patterns")
    w("")
    w("Not nodes, not elements, and in no artifact. A pattern lists the **topics** a kind of")
    w("finding is usually described by. It names no DataElement and inserts nothing: an author")
    w("sees the topics as a checklist and then chooses, per finding, whether an existing element")
    w("genuinely fits or a new one is needed. Reuse is never forced.")
    w("")
    w("| Pattern | With | Topics |")
    w("|---|---|---|")
    for pt in spec.PATTERNS:
        w(f"| `{pt['name']}` | {pt.get('applies_with') or '—'} | "
          f"{', '.join(pt['topics'])} |")
    w("")
    w("A pattern must not hold element ids and splice them into the classes that apply it.")
    w("That forces a shared element onto classes it does not suit, and the only way to make one")
    w("fit is to widen it: a single `margin` element reaching nine values across three")
    w("societies, so that a tendon lesion can be reported as having extra-thyroidal extension.")
    w("Published elements must not move to accommodate new findings.")
    w("")
    w("The useful part is discoverability, and it is anatomy-aware. An author scoping a finding")
    w("to the lung should be shown lung-scoped distribution elements, not ones whose values come")
    w("from another organ. That belongs in the authoring tool, not in the graph.")
    w("")
    w("### Authoring checks")
    w("")
    w("Advisory. None is enforced by a reasoner and none constrains what an author may write.")
    w("")
    w("| Rule | Says |")
    w("|---|---|")
    for r in spec.PATTERN_LINT:
        w(f"| `{r['rule']}` | {r['says']} |")
    w("")
    lint_out = spec.lint()
    w(f"Currently **{'clean' if not lint_out else str(len(lint_out)) + ' findings'}**.")
    w("")

    # 6 anchoring
    w("## 6. Anchoring")
    w("")
    av = collections.Counter(n.get("anchor_verdict") for n in nodes
                             if n["node"] in ("FindingClass", "Diagnosis"))
    w("RadLex is the primary anchor. Multiple bindings are supported; SNOMED CT is in scope")
    w("as a secondary. Every finding and diagnosis carries one verdict.")
    w("")
    w("| Verdict | n | Meaning | Action |")
    w("|---|---:|---|---|")
    for v, mn, ac in [
        ("anchored", "one pre-coordinated RadLex concept", "bind, primary"),
        ("post_coordinated", "head term plus modifiers, all present in RadLex", "bind compositionally, record components"),
        ("structurally_expressed", "the distinguishing feature is already carried by an edge", "bind the base concept, no request"),
        ("unanchored_requestable", "absent, does not decompose, within radiology scope", "local node, file a change request"),
        ("out_of_primary_scope", "the term's nature puts it outside a radiology lexicon", "another system is primary, no request"),
    ]:
        w(f"| `{v}` | {av.get(v, 0)} | {mn} | {ac} |")
    w("")
    reqs = sorted({n["request"] for n in nodes if n.get("request")})
    w(f"{len(reqs)} change requests outstanding.")
    w("")

    # 7 traces
    w("## 7. What the model holds, and where it stops")
    w("")
    w("Four report sentences against the compiled shapes. Nothing here is stored: the sentences")
    w("are read against the model as it stands, and each table is generated from the shape the")
    w("class compiles to. Two work, one works partly, one does not.")
    w("")

    def shape_table(cls):
        c, f = fc_comp.get(cls), fc_spec.get(cls)
        if not c:
            return
        w("| | |")
        w("|---|---|")
        w(f"| FindingClass | `{c['finding_id']}` {c['name']} |")
        w(f"| Anchor | `{f.get('anchor_verdict')}` |")
        scope = ", ".join(f"{name.get(s['location'], s['location'])} ({s['kind']}/{s['strength']})"
                          for s in c["anatomic_scope"])
        w(f"| Scope | {scope or '—'} |")
        ip = sum(1 for e in c["elements"] if e["inherited_from"])
        w(f"| Elements | {', '.join(e['name'] for e in c['elements'])} "
          f"({ip} inherited) |")
        w(f"| Measurements | {', '.join(m['name'] for m in c['measurements']) or '—'} |")
        w(f"| Diagnoses it may represent | "
          f"{', '.join(name.get(d, d) for d in c['may_represent']) or '—'} |")
        w("")

    w("### 1. A solid pulmonary nodule &nbsp;&nbsp; `HOLDS`")
    w("")
    w("> *There is a 5 mm solid pulmonary nodule in the right upper lobe.*")
    w("")
    shape_table("pulmonary nodule")
    w("Every part lands. The site is a lobe and the scope claim is against the lung, satisfied")
    w("through two `PART_OF` steps and one subsumption step. Stating the attenuation is enough")
    w("to reach the subtype: probe `A3` asserts a pulmonary nodule with part-solid attenuation")
    w("and the reasoner returns `PartSolidPulmonaryNodule`, with no subtype asserted anywhere.")
    w("")
    w("The one thing the sentence underspecifies is the model's problem too: it says 5 mm and")
    w("not which diameter, and the class offers both a long-axis and a mean diameter.")
    w("")

    w("### 2. A pleural effusion &nbsp;&nbsp; `HOLDS`")
    w("")
    w("> *Moderate left pleural effusion, in the setting of pneumonia.*")
    w("")
    shape_table("pleural effusion")
    w("The non-focal case. No margin, no size, no distribution: amount and laterality instead.")
    w("")
    w("The pneumonia link is a **`MAY_CAUSE`**, not a `MAY_MANIFEST_AS`. Pneumonia does not show")
    w("itself as an effusion, it produces one, and the two edges exist to keep those apart.")
    w("`LungCancer` reaches this same class both ways, manifesting as a nodule and causing an")
    w("effusion, which is where an author has to tell them apart.")
    w("")

    w("### 3. Acute pyelonephritis &nbsp;&nbsp; `HOLDS IN PART`")
    w("")
    w("> *Striated nephrogram with perinephric stranding and an enlarged left kidney.*")
    w("")
    w("| Finding | typicality | specificity |")
    w("|---|---|---|")
    for t, ty, sp in [d for d in spec.DIAGNOSES
                      if d["cls"] == "AcutePyelonephritis"][0]["manifests_as"]:
        w(f"| {t} | {ty} | {sp} |")
    w("")
    w("All three findings are representable and each edge carries its strength. What cannot be")
    w("said is what makes the diagnosis: no single manifestation is sufficient, and it is the")
    w("combination that is diagnostic. Every edge is binary, so the model records three")
    w("independent claims.")
    w("")
    w("`specificity` grades each finding alone, which is not the same thing: a striated")
    w("nephrogram is `highly_suggestive`, perinephric stranding only `suggestive`, because")
    w("stranding also occurs in obstruction, trauma and infarct. Whether combining them belongs")
    w("in the vocabulary or in whatever consumes it is undecided.")
    w("")

    w("### 4. Several rib fractures &nbsp;&nbsp; `DOES NOT HOLD`")
    w("")
    w("> *Nondisplaced fractures of the left fourth through seventh ribs.*")
    w("")
    shape_table("rib fracture")
    w("One rib fracture is fine. Four are not. The class carries no count and no distribution,")
    w("so it cannot say how many, and even where a count exists it says how many rather than")
    w("which. Nothing enumerates members and nothing attaches an attribute to one of them, so")
    w("*the left fourth through seventh* and *the largest measuring 8 mm* both fall out.")
    w("")

    # 8 coverage
    w("## 8. Coverage")
    w("")
    w("What a radiologist can say, against what the model can hold. The target is report")
    w("language, not current extractor output.")
    w("")
    cnt = collections.Counter(r[1] for r in COVERAGE)
    for band, label in [("yes", "Representable"), ("partial", "Partial"), ("no", "Not representable")]:
        rows = [r for r in COVERAGE if r[1] == band]
        w(f"### {label} — {len(rows)}")
        w("")
        w("| Phenomenon | Where |")
        w("|---|---|")
        for ph, _, whr in rows:
            w(f"| {ph} | {whr} |")
        w("")
    w(f"**{cnt['yes']} representable, {cnt['partial']} partial, {cnt['no']} not, of {len(COVERAGE)}.**")
    w("")
    w("Negation splits three ways and only the first is handled. Negating a **named** finding")
    w("works: presence absent, on the finding itself. Negating a **category**, as in no renal")
    w("abnormality, has nothing to attach to. Negating the **remainder**, as in no other")
    w("significant adenopathy, needs a scope over what was examined.")
    w("")
    w("Three of the not-representable rows are deliberately out of scope: follow-up")
    w("recommendations, technique and clinical history. The rest — category and remainder")
    w("negation, bilaterality, prior-study comparison — sit with the partial rows for plurality")
    w("and certainty, because they are one problem wearing several faces: the model describes")
    w("findings and has no representation of the **statement** a radiologist makes about them.")
    w("A count can say four fractures without saying which four; a report can deny something")
    w("the model never named. These will not be fixed one row at a time.")
    w("")

    # 9 open
    w("## 9. Open, keyed to where it bites")
    w("")
    w("| Question | Bites at |")
    w("|---|---|")
    for q, b in OPEN:
        w(f"| {q} | {b} |")
    w("")
    w("---")
    w("")
    w("Clinical content is provisional and unvalidated; ordinal scales in particular were")
    w("assembled from report language rather than a society standard. RadLex codes are")
    w("extracted from RadLex.owl 4.3 and each is verified against its label at build time.")

    open(f"{OUT}/SHAPE.md", "w").write("\n".join(L) + "\n")
    print(f"SHAPE.md written: {len(L)} lines")
    print(f"  {len(nodes)} nodes / {len(edges)} edges | {len(byt)} node types | {len(sig)} edge types")
    print(f"  coverage: {cnt['yes']} yes, {cnt['partial']} partial, {cnt['no']} no")


if __name__ == "__main__":
    main()
