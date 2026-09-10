# -*- coding: utf-8 -*-
"""
Content specification for the RadElement next-gen alpha model.

Every RadLex code here was verified against the supplied Radlex_v4_3.csv export.
Where a concept has no RadLex code, that is recorded as a local node with a
source_status, which is itself part of what the alpha is meant to surface.
"""

RADLEX_VERSION = "4.3"

# ---------------------------------------------------------------------------
# ANATOMY  (imported. RID -> local AL node)
# Only what the modelled findings actually need, per MIREOT.
# ---------------------------------------------------------------------------

ANATOMY_SEEDS = [
    # thorax / lung
    "RID1301",  # lung
    "RID1302",  # right lung
    "RID1326",  # left lung
    "RID1303",  # upper lobe of right lung
    "RID1310",  # middle lobe of lung
    "RID1315",  # lower lobe of right lung
    "RID1316",  # superior segment of lower lobe of right lung
    "RID1327",  # upper lobe of left lung  (verified at build time)
    "RID1338",  # lower lobe of left lung  (verified at build time)
    "RID1243",  # thorax
    # thyroid
    "RID7578",  # thyroid gland
    "RID7579",  # left lobe of thyroid gland
    "RID7581",  # right lobe of thyroid gland
    "RID7584",  # isthmus of thyroid gland
    "RID50344", # lobe of thyroid gland
    # abdominal solid organs
    "RID58",    # liver
    "RID205",   # kidney
    "RID88",    # adrenal gland
    "RID170",   # pancreas
    "RID86",    # spleen
    "RID56",    # abdomen
    "RID29989", # abdomen proper
    # breast
    "RID28749", # breast
    # nodal
    "RID13296", # lymph node
    "RID28891", # mediastinal lymph node
    "RID1517",  # axillary lymph node
    "RID1496",  # pulmonary lymph node
    "RID1520",  # anterior mediastinal lymph node
    "RID7695",  # lymph node of neck
    # structure-type scope demo (IS_A rather than PART_OF)
    "RID6067",  # tendon
    "RID478",   # artery
    # spaces and non-organ places, needed by the non-focal findings
    "RID1362",  # pleura
    "RID1363",  # pleural space
    "RID1370",  # parietal pleura
    "RID1371",  # visceral pleura
    "RID1384",  # mediastinum
    "RID35739", # lung parenchyma
    "RID5978",  # parenchyma
    "RID28538", # airspace
    "RID1361",  # secondary pulmonary lobule
    "RID431",   # retroperitoneum
    "RID434",   # perirenal space
    "RID228",   # renal pelvis
    # neuro, vascular, skeletal
    "RID6434",  # brain
    "RID9080",  # head
    "RID16996", # cerebral white matter
    "RID7124",  # lateral ventricle
    "RID585",   # internal carotid artery
    "RID684",   # external carotid artery
    "RID974",   # pulmonary artery
    "RID2471",  # rib
    "RID34694", # lobe of lung, the kind a pulmonary scope refines to
    "RID1333",  # lingula, already Part_Of upper lobe of left lung upstream
    "RID1339",  # superior segment of lower lobe of left lung, balancing the right
    "RID92",    # cortex of adrenal gland
    "RID89",    # limb of adrenal gland
    # intracranial compartments
    "RID6383",  # intracranial
    "RID7111",  # epidural space
    "RID7119",  # subarachnoid space
    "RID7120",  # subdural space
    "RID7123",  # cerebral ventricle
    "RID648",   # anterior cerebral artery
    "RID665",   # middle cerebral artery
    "RID804",   # posterior cerebral artery
    "RID791",   # basilar artery
    "RID6437",  # telencephalon
]

# Locally coined AnatomicLocations: concepts the source does not name.
# These exercise source / source_status / request and the empty-bindings case.
LOCAL_ANATOMY = [
    dict(local="AL-L0001", name="lung periphery",
         definition="The outer third of the lung parenchyma, measured from the "
                    "pleural surface toward the hilum.",
         source_status="pending_request", request="RADLEX-REQ-0101",
         part_of="RID1301",
         note="A zone, not a structure. RadLex names no peripheral zone of lung, and a zone "
              "defined by distance from a surface has no concept there at all."),
    dict(local="AL-L0006", name="zone of adrenal gland",
         definition="A gross anatomic zone of the adrenal gland, as distinguished on "
                    "cross-sectional imaging.",
         source_status="pending_request", request="RADLEX-REQ-0640",
         part_of="RID88",
         note="The kind an adrenal scope refines to. RadLex has no gross zoning of the gland: "
              "it carries the histological zonae, the cortex and medulla, and a childless "
              "limb concept, none of which is what a radiologist describes."),
    dict(local="AL-L0003", name="body of adrenal gland",
         definition="The central confluence where the two limbs of the gland meet.",
         source_status="pending_request", request="RADLEX-REQ-0641",
         part_of="AL-L0006",
         note="RadLex carries limb of adrenal gland RID89 with no children and no body "
              "concept, so the gross morphology axis a radiologist uses is not expressible "
              "upstream at all."),
    dict(local="AL-L0004", name="medial limb of adrenal gland",
         definition="The limb running medially from the body of the gland.",
         source_status="pending_request", request="RADLEX-REQ-0642",
         part_of="AL-L0006"),
    dict(local="AL-L0005", name="lateral limb of adrenal gland",
         definition="The limb running laterally from the body of the gland.",
         source_status="pending_request", request="RADLEX-REQ-0643",
         part_of="AL-L0006"),
    dict(local="AL-L0002", name="subpleural region of lung",
         definition="The region of lung parenchyma immediately deep to the visceral pleura.",
         source_status="post_coordinated",
         anchor_base=("RID46032", "subpleural"), anchor_modifiers=[("RID1301", "lung")],
         part_of="AL-L0001",
         note=""),
]


# Gap-fill edges between imported nodes. The node exists upstream; the
# relationship does not. Authored locally as a placeholder while the change
# request is processed, and removed on the release that carries it.
#
# Both were checked against the Parents chain first, because the RadLex release
# notes warn that some part-of links were inadvertently converted to is-a and a
# semantically part-of link sitting only in `Parents` would not appear in the
# part-of counts. Neither chain contains one: adrenal gland runs
# corticomedullary organ -> parenchymatous organ -> solid organ, and lung
# parenchyma runs parenchyma -> organ component -> cardinal organ part. Both are
# genuine type hierarchies, so the missing relationship is a real gap.

LOCAL_ANATOMY_EDGES = [
    # RadLex organises the nervous system as an organ system, not as a regional part
    # of the head: brain climbs to nervous system and then to human body, never
    # through head. The intracranial spaces are worse, being only IS_A nervous
    # system space with no location at all. RadLex has no cranial cavity concept
    # either. Without these, nothing intracranial has a body region and a haemorrhage
    # in the subdural space cannot be shown to be inside the head.
    dict(frm="RID6434", to="RID9080", prop="containedIn", family="location",
         source_status="pending_request", request="RADLEX-REQ-0631",
         note="brain is located in the head."),
    dict(frm="RID7111", to="RID9080", prop="containedIn", family="location",
         source_status="pending_request", request="RADLEX-REQ-0632",
         note="epidural space, cranial portion, is located in the head."),
    dict(frm="RID7119", to="RID9080", prop="containedIn", family="location",
         source_status="pending_request", request="RADLEX-REQ-0633",
         note="subarachnoid space is located in the head."),
    dict(frm="RID7120", to="RID9080", prop="containedIn", family="location",
         source_status="pending_request", request="RADLEX-REQ-0634",
         note="subdural space is located in the head."),
    dict(frm="RID7123", to="RID9080", prop="containedIn", family="location",
         source_status="pending_request", request="RADLEX-REQ-0635",
         note="cerebral ventricle is located in the head."),
    dict(frm="RID35739", to="RID1301", prop="generalPartOf", family="mereology",
         source_status="pending_request", request="RADLEX-REQ-0501",
         note="lung parenchyma has exactly one edge in RadLex 4.3, IS_A parenchyma. It is not "
              "connected to the lung. Without this, anything scoped to lung parenchyma derives "
              "no body region and fails scope congruence against lung."),
    dict(frm="RID88", to="RID431", prop="containedIn", family="location",
         source_status="pending_request", request="RADLEX-REQ-0502",
         note="adrenal gland carries Has_Part, Has_Regional_Part and Has_Constitutional_Part "
              "downward and Member_Of to 'set of adrenal glands', but nothing upward. RadLex "
              "never says where the adrenal gland is."),
]


# Values whose binding is deliberately loose: the code is the nearest concept
# RadLex has, not a synonym of our label. Read by the builders and by
# verify_codes.py, which would otherwise report the label difference as a wrong code.
LOOSE_VALUE_MATCHES = {
    "V-000412": ("RID3829", "closeMatch", "cicatricial atelectasis is contraction of scar; "
                                          "RadLex has scar and no cicatricial concept"),
}


# ---------------------------------------------------------------------------
# DATA ELEMENTS
# In OWL each becomes an ObjectProperty plus a value-domain class.
# `values` are (local_id, name, radlex_or_None, definition, rank_or_None)
# ---------------------------------------------------------------------------

DATA_ELEMENTS = [
    dict(id="DE-000039", prop="hasPulmonaryMargin", name="pulmonary margin",
         definition="The character of the interface between a pulmonary lesion and the "
                    "surrounding lung.",
         radlex=None, anchor_base=("RID43359", "lesion margin"),
         anchor_modifiers=[("RID1301", "lung")],
         scoped_to=['RID1301'],
         values=[("V-000380", "smooth", "RID5714", "The interface is even and uninterrupted.", None),
                 ("V-000381", "lobulated", "RID5711", "The interface undulates with rounded protrusions.", None),
                 ("V-000382", "irregular", "RID5715", "The interface is uneven without a dominant pattern.", None),
                 ("V-000383", "spiculated", "RID5713", "Radiating linear projections extend from the interface.", None)]),

    dict(id="DE-000040", prop="hasThyroidMargin", name="thyroid margin",
         definition="The character of the interface between a thyroid nodule and the "
                    "surrounding gland.",
         radlex=None, anchor_base=("RID43359", "lesion margin"),
         anchor_modifiers=[("RID7578", "thyroid gland")],
         scoped_to=['RID7578'],
         values=[("V-000390", "smooth", "RID5714", "Even and uninterrupted.", None),
                 ("V-000391", "ill-defined", "RID5709",
                  "Merges imperceptibly with the surrounding parenchyma. Not a suspicious "
                  "feature, and not to be conflated with irregular.", None),
                 ("V-000392", "lobulated", "RID5711", "Undulating with rounded protrusions.", None),
                 ("V-000393", "irregular", "RID5715",
                  "Jagged, spiculated or with sharp angles.", None),
                 ("V-000394", "extra-thyroidal extension", "RID49885",
                  "Frank invasion beyond the thyroid capsule. Scored under margin by TI-RADS "
                  "although it is a claim about invasion rather than about the interface.", None)]),

    dict(id="DE-000041", prop="hasThyroidComposition", name="thyroid composition",
         definition="The internal make-up of a thyroid nodule, on the ACR TI-RADS axis.",
         radlex=None, anchor_base=("RID39409", "composition"),
         anchor_modifiers=[("RID7578", "thyroid gland")],
         scoped_to=['RID7578'],
         values=[("V-000400", "cystic or almost completely cystic", "RID5739",
                  "Entirely or nearly entirely fluid.", 1),
                 ("V-000401", "spongiform", "RID49880",
                  "Aggregated microcystic spaces in more than half the nodule. Benign.", 2),
                 ("V-000402", "mixed cystic and solid", "RID50517",
                  "Substantial fluid and solid components.", 3),
                 ("V-000403", "solid or almost completely solid", "RID5741",
                  "Entirely or nearly entirely soft tissue.", 4)]),

    dict(id='DE-000046', prop='hasHemorrhageAge', name='hemorrhage age',
         definition='How old intracranial blood is, read from its density or signal on a '
                    'single study.',
         radlex=None,
         scoped_to=['RID9080'],
         values=[('V-000450', 'hyperacute', None,
                  'Within hours. Still largely oxygenated.', 1),
                 ('V-000451', 'acute', 'RID5718',
                  'Roughly the first three days. Deoxyhaemoglobin.', 2),
                 ('V-000452', 'early subacute', None,
                  'Roughly days three to seven. Intracellular methaemoglobin.', 3),
                 ('V-000453', 'late subacute', None,
                  'Roughly one to four weeks. Extracellular methaemoglobin.', 4),
                 ('V-000454', 'chronic', 'RID5719',
                  'Beyond a month. Haemosiderin and ferritin.', 5),
                 ('V-000455', 'indeterminate age', 'RID39110',
                  'The appearance does not permit dating.', 6)],
         note='Blood passes through five '
              'stages with distinct MR signal, and early and late subacute are different '
              'stages that look different and mean different things. Forcing them into a list '
              'built around healing and healed would be reusing an orthopaedic vocabulary for '
              'a haemoglobin degradation sequence. Only acute, chronic and indeterminate have '
              'RadLex concepts; the rest are local.'),

    dict(id='DE-000044', prop='hasFlowCharacter', name='flow character',
         definition='How blood moves through the segment on colour Doppler.',
         radlex=None,
         modality=['US'],
         values=[('V-000430', 'laminar', 'RID5931',
                  'Ordered flow, uniform colour.', 1),
                 ('V-000431', 'turbulent', 'RID5932',
                  'Disordered flow, visible swirling and colour mixing distal to the '
                  'narrowing.', 2)]),

    dict(id='DE-000045', prop='hasEcaStenosisSignificance', name='ECA stenosis significance',
         definition='Whether an external carotid stenosis is haemodynamically significant, '
                    'read from velocity rather than from a diameter ratio.',
         radlex=None,
         scoped_to=['RID684'],
         values=[('V-000440', 'non-significant', None,
                  'Under 50 percent. Velocity stays low and steady through the segment.', 1),
                 ('V-000441', 'significant', None,
                  '50 percent or more. Velocity surges through the narrowed gap, usually with '
                  'turbulence distal to it.', 2)],
         note='The '
              'external carotid is graded on two velocity-based bands where the internal '
              'carotid takes five NASCET diameter-ratio bands, so mild and moderate do not '
              'mean the same thing in the two vessels and must not share values.'),

    dict(id='DE-000042', prop='hasAtelectasisMechanism', name='atelectasis mechanism',
         definition='Why the lung has lost volume. The axis that changes management: '
                    'obstructive implies an obstructing lesion and should prompt a search for one.',
         radlex=None,
         scoped_to=['RID1301'],
         values=[('V-000410', 'compressive', 'RID4741',
                  'Adjacent space-occupying process compressing the lung.', None),
                 ('V-000411', 'obstructive', 'RID4962',
                  'Resorption of gas distal to an obstructed airway. Implies an obstructing lesion.', None),
                 ('V-000412', 'cicatricial', 'RID3829',
                  'Fibrous contraction of scarred parenchyma. Bound to scar: RadLex has no '
                  'cicatricial concept.', None),
                 ('V-000413', 'passive', None,
                  'Relaxation of lung away from the chest wall, as with a pneumothorax.', None),
                 ('V-000414', 'adhesive', None,
                  'Surfactant deficiency with alveolar collapse.', None)],
         note='Compressive, obstructive and cicatricial post-coordinate from RadLex; passive '
              'and adhesive have no concept and are local.'),

    dict(id='DE-000043', prop='hasAtelectasisMorphology', name='atelectasis morphology',
         definition='What the volume loss looks like.',
         radlex=None,
         scoped_to=['RID1301'],
         values=[('V-000420', 'rounded', 'RID28494',
                  'A rounded subpleural opacity with vessels swirling into it, associated with '
                  'pleural disease. A mass mimic.', None),
                 ('V-000421', 'linear', 'RID28513',
                  'A thin band, usually basal. Also called discoid or plate-like.', None),
                 ('V-000422', 'lobar', None, 'A whole lobe.', None),
                 ('V-000423', 'segmental', None, 'A named bronchopulmonary segment.', None),
                 ('V-000424', 'subsegmental', None, 'Less than a segment.', None)],
         note='RadLex carries the two morphologic terms as concepts, rounded RID28494 and linear '
              'RID28513, and none of the mechanistic ones. It classifies atelectasis by '
              'appearance rather than by mechanism.'),

    dict(id='DE-000001',
         prop='hasPresence',
         name='presence',
         definition='Whether the observation is judged to be present on this examination.',
         radlex=None,
         values=[('V-000001', 'present', 'RID28472',
  'Observation can be confidently categorized as present based on the data presented '
  'to the interpreter.',
  None),
 ('V-000002', 'absent', 'RID28473',
  'Observation can be confidently categorized as absent based on the data presented to '
  'the interpreter.',
  None),
 ('V-000003', 'indeterminate', 'RID39110',
  'The data presented do not permit categorization as present or absent.', None),
 ('V-000004', 'unknown', 'RID5655',
  'No determination was made, or the examination did not address it.', None)]),

    dict(id='DE-000002',
         prop='hasAttenuation',
         name='attenuation',
         definition='The density characteristics of a pulmonary nodule on CT.',
         radlex=None,
         synonyms=[('density', 'synonym')],
         scoped_to=['RID1301'],
         modality=['CT'],
         values=[('V-000010', 'solid', 'RID50151',
  'The nodule completely obscures the underlying lung parenchyma.', 1),
 ('V-000011', 'part-solid', 'RID50152',
  'The nodule contains both a solid component and a ground-glass component.', 2),
 ('V-000012', 'non-solid', 'RID50153',
  'The nodule does not obscure the underlying lung parenchyma. Pure ground-glass.', 3)]),

dict(id='DE-000004',
         prop='hasCalcification',
         name='calcification',
         definition='The presence and pattern of calcium within the lesion.',
         radlex=None,
         multi_select=True,
         cardinality_note=('Multi-select. A lesion may carry more than one calcification pattern at once. This '
 'is the shape of the TI-RADS echogenic foci case'),
         exclusive_none='V-000030',
         values=[('V-000030', 'none', None, 'No calcification is identified.', None),
 ('V-000031', 'central', None, 'Calcification occupies the centre of the lesion.',
  None),
 ('V-000032', 'popcorn', None, 'Coarse, clustered, chondroid calcification.', None),
 ('V-000033', 'punctate', None, 'Small discrete foci of calcification.', None),
 ('V-000034', 'coarse', None, 'Dense, chunky calcification without a specific pattern.',
  None),
 ('V-000035', 'peripheral / rim', None, 'Calcification at the margin of the lesion.',
  None)]),

    dict(id='DE-000005',
         prop='hasEchogenicity',
         name='echogenicity',
         definition='The reflectivity of the lesion relative to the adjacent parenchyma on ultrasound.',
         radlex='RID6045',
         modality=['US'],
         values=[('V-000040', 'anechoic', 'RID34360', 'No internal echoes.', 1),
 ('V-000041', 'very hypoechoic', 'RID49881',
  'Markedly less echogenic than adjacent strap muscle.', 2),
 ('V-000042', 'hypoechoic', 'RID6046', 'Less echogenic than the adjacent parenchyma.',
  3),
 ('V-000043', 'isoechoic', 'RID6047',
  'Equal in echogenicity to the adjacent parenchyma.', 4),
 ('V-000044', 'hyperechoic', 'RID6048', 'More echogenic than the adjacent parenchyma.',
  5)]),

    dict(id='DE-000006',
         prop='hasComposition',
         name='composition',
         definition='The internal make-up of the lesion in terms of solid and fluid content.',
         radlex='RID39409',
         values=[('V-000050', 'cystic', 'RID5739', 'Entirely fluid.', None),
 ('V-000051', 'predominantly cystic', 'RID49879',
  'Mostly fluid with a minority solid component.', None),
 ('V-000052', 'mixed cystic and solid', 'RID50517',
  'Substantial fluid and solid components.', None),
 ('V-000053', 'solid', 'RID5741', 'Entirely soft tissue.', None)]),

    dict(id='DE-000007',
         prop='hasEnhancementPattern',
         name='enhancement pattern',
         definition='The distribution of contrast uptake within the lesion.',
         radlex='RID6058',
         values=[('V-000060', 'none', None, 'No appreciable contrast uptake.', None),
 ('V-000061', 'homogeneous', None, 'Uniform uptake throughout.', None),
 ('V-000062', 'heterogeneous', None, 'Non-uniform uptake.', None),
 ('V-000063', 'peripheral nodular discontinuous', None,
  'Discontinuous nodular uptake at the margin.', None),
 ('V-000064', 'arterial hyperenhancement with washout', None,
  'Uptake exceeding parenchyma in the arterial phase with subsequent relative '
  'hypoenhancement.',
  None)]),

    dict(id='DE-000008',
         prop='hasWallCharacter',
         name='wall character',
         definition='The thickness and regularity of the wall bounding a fluid-filled structure.',
         radlex=None,
         values=[('V-000070', 'imperceptible', None, 'No discernible wall.', 1),
 ('V-000071', 'thin', None, 'A discernible but hairline wall.', 2),
 ('V-000072', 'thickened', None, 'A wall of measurable thickness.', 3),
 ('V-000073', 'enhancing', None, 'A wall demonstrating contrast uptake.', 4)]),

    dict(id='DE-000011',
         prop='hasNodalArchitecture',
         name='nodal architecture',
         definition='The internal organisation of a lymph node as seen on imaging.',
         radlex=None,
         multi_select=True,
         cardinality_note='Multi-select. Cortical thickening and central necrosis co-occur.',
         values=[('V-000100', 'preserved fatty hilum', None, 'A central fatty hilum is retained.',
  None),
 ('V-000101', 'effaced fatty hilum', None, 'The central fatty hilum is lost.', None),
 ('V-000102', 'cortical thickening', None,
  'The cortex is thickened relative to the hilum.', None),
 ('V-000103', 'central necrosis', None, 'A non-enhancing centre within the node.',
  None)]),

    dict(id='DE-000012',
         prop='hasNodalShape',
         name='nodal shape',
         definition='The gross outline of a lymph node.',
         radlex=None,
         values=[('V-000110', 'elongated', None, 'Long axis substantially exceeds short axis.', None),
 ('V-000111', 'rounded', None, 'Long and short axes approach one another.', None)]),

    dict(id='DE-000013',
         prop='hasDistribution',
         name='distribution',
         definition='The spatial pattern of a multifocal finding across the organ or region.',
         radlex=None,
         values=[('V-000120', 'solitary', None, 'A single lesion.', None),
 ('V-000121', 'scattered', None, 'Several lesions without a discernible pattern.',
  None),
 ('V-000122', 'clustered', None, 'Lesions grouped in one part of the organ.', None),
 ('V-000123', 'random', None,
  'Lesions distributed without respect to secondary lobular anatomy.', None),
 ('V-000124', 'centrilobular', None,
  'Lesions centred on the secondary pulmonary lobule.', None),
 ('V-000125', 'perilymphatic', None, 'Lesions along lymphatic pathways.', None),
 ('V-000126', 'miliary', None, 'Innumerable uniform tiny lesions throughout.', None)]),

    dict(id='DE-000014',
         prop='hasFdgAvidity',
         name='FDG avidity',
         definition='The degree of fluorodeoxyglucose uptake relative to background.',
         radlex=None,
         modality=['PET'],
         values=[('V-000130', 'none', None, 'Uptake not exceeding background.', 1),
 ('V-000131', 'mild', None, 'Uptake mildly exceeding background.', 2),
 ('V-000132', 'moderate', None, 'Uptake moderately exceeding background.', 3),
 ('V-000133', 'intense', None, 'Uptake markedly exceeding background.', 4)]),

    dict(id='DE-000015',
         prop='hasIntervalChange',
         name='interval change',
         definition='The relationship of the finding to the same finding on a prior comparable examination.',
         radlex=None,
         values=[('V-000140', 'new', None, 'Not present on the prior examination.', None),
 ('V-000141', 'unchanged', None,
  'Without appreciable difference from the prior examination.', None),
 ('V-000142', 'increased', None,
  'Larger or more numerous than on the prior examination.', None),
 ('V-000143', 'decreased', None,
  'Smaller or less numerous than on the prior examination.', None),
 ('V-000144', 'no prior available', None,
  'No comparable prior examination was available.', None)]),

    dict(id='DE-000037',
         prop='hasVascularTerritory',
         name='vascular territory',
         definition=('Which arterial supply the infarct conforms to. A territorial infarct implicates the '
 'named artery; a watershed pattern implicates global hypoperfusion instead.'),
         radlex=None,
         scoped_to=['RID6434'],
         values=[('V-000360', 'anterior cerebral artery', 'RID648',
  'Parasagittal frontal and medial parietal.', None),
 ('V-000361', 'middle cerebral artery', 'RID665',
  'Lateral frontal, temporal and parietal. The commonest territory.', None),
 ('V-000362', 'posterior cerebral artery', 'RID804', 'Occipital and medial temporal.',
  None),
 ('V-000363', 'posterior circulation', None,
  'Brainstem and cerebellum, from the vertebrobasilar supply. Local: RadLex has the '
  'basilar and vertebral arteries but no concept for the territory they supply.', None),
 ('V-000364', 'watershed', 'RID6408',
  'Between two territories. Implies hypoperfusion rather than occlusion of one vessel.',
  None),
 ('V-000365', 'non-territorial', None,
  'Conforming to no arterial territory. Argues against arterial infarction.', None)],
         note=('A stub. Territory is expressed here as a value list because the anatomy layer has no '
 'notion of an arterial supply region as distinct from an artery: RadLex carries the '
 'vessels but not the parenchyma each supplies.')),

    dict(id='DE-000038',
         prop='hasCollectionShape',
         name='collection shape',
         definition='The outline a collection takes, which reflects the space containing it.',
         radlex=None,
         values=[('V-000370', 'biconvex', None,
  'Lentiform. Bounded by sutures, where the dura is anchored.', None),
 ('V-000371', 'crescentic', None,
  'Concave toward the brain. Crosses sutures but not dural reflections.', None),
 ('V-000372', 'conforming', None,
  'Filling and taking the shape of the space, such as sulci and cisterns.', None),
 ('V-000373', 'rounded', None, 'Roughly spherical, as within parenchyma.', None)],
         note=('The sign that separates the intracranial compartments on imaging, and the reason '
 'those subtypes are classes rather than restatements of scope.')),

    dict(id='DE-000035',
         prop='hasPneumothoraxSize',
         name='pneumothorax size',
         definition='How much of the hemithorax the pneumothorax occupies, on the coarse scale reports use.',
         radlex=None,
         scoped_to=['RID1363'],
         values=[('V-000340', 'small', 'RID5774', 'A thin rim of pleural air.', 1),
 ('V-000341', 'moderate', 'RID5672', 'Between small and large.', 2),
 ('V-000342', 'large', 'RID5778', 'Occupying much of the hemithorax.', 3)],
         note=('Reported as an estimate. Several measured conventions exist (Light, Collins, BTS '
 'interpleural distance) and none is carried here.')),

    dict(id='DE-000034',
         prop='hasAcuity',
         name='acuity',
         definition=('How old the finding is, judged from its appearance rather than from a comparison. A '
 'healed fracture on a first study has no prior to compare against and is still '
 'recognisably old.'),
         radlex=None,
         anchor_base=('RID5716', 'temporal descriptor'),
         values=[('V-000330', 'acute', 'RID5718',
  'Recent. Sharp fracture margins without callus; haemorrhage still dense.', 1),
 ('V-000331', 'subacute', None,
  'Intermediate. Between the acute and chronic appearances.', 2),
 ('V-000332', 'healing', 'RID6352',
  'Callus formation with fracture margins becoming indistinct.', 3),
 ('V-000333', 'healed', 'RID6353',
  'Bridging callus with corticated margins. Also reported as old or remote.', 4),
 ('V-000334', 'chronic', 'RID5719', 'Long-standing.', 5),
 ('V-000335', 'indeterminate age', 'RID39110',
  'The appearance does not permit dating. Radiologists report this explicitly.', 6)],
         note=('Distinct from interval change, which relates a finding to a prior study. Acuity is '
 'read off a single study. Subacute has no RadLex concept although it is standard '
 'radiology usage, particularly for haemorrhage.')),

    dict(id='DE-000033',
         prop='hasEchogenicFoci',
         name='echogenic foci',
         multi_select=True,
         definition=('Bright foci within a nodule on ultrasound. Not a synonym for calcification: a '
 'comet-tail artifact is a reverberation artifact in colloid, not calcium, and is a '
 'reassuring feature.'),
         radlex=None,
         cardinality_note=('Multi-select. ACR TI-RADS is explicit that more than one may apply and that their '
 'points are additive; it is the only one of its five categories that works this way.'),
         scoped_to=['RID7578'],
         modality=['US'],
         values=[('V-000320', 'none', None, 'No echogenic foci.', 1),
 ('V-000321', 'large comet-tail artifact', 'RID49887',
  'V-shaped reverberation artifact greater than 1 mm in a cystic component. Indicates '
  'colloid and is a benign feature.',
  2),
 ('V-000322', 'macrocalcifications', 'RID34369',
  'Coarse calcification causing acoustic shadowing.', 3),
 ('V-000323', 'peripheral rim calcifications', 'RID49886',
  'Calcification complete or incomplete along the margin.', 4),
 ('V-000324', 'punctate echogenic foci', 'RID50571',
  'Non-shadowing bright foci, which may have small comet-tail artifacts. Corresponds '
  'to what is loosely called microcalcification.',
  5)]),

    dict(id='DE-000016',
         prop='hasAmount',
         name='amount',
         unvalidated=True,
         definition='How much material is present, on a coarse ordinal scale.',
         radlex=None,
         anchor_base=('RID5761', 'quantity descriptor'),
         values=[('V-000150', 'trace', None, 'Barely detectable.', 1),
 ('V-000151', 'small', 'RID5774', 'Present but of little consequence.', 2),
 ('V-000152', 'moderate', None, 'Substantial without dominating the space.', 3),
 ('V-000153', 'large', 'RID5778', 'Filling much of the available space.', 4)]),

    dict(id='DE-000017',
         prop='hasInternalComplexity',
         name='internal complexity',
         multi_select=True,
         unvalidated=True,
         definition='Features within a collection beyond uniform homogeneous content.',
         radlex=None,
         cardinality_note='Multi-select. Septations and loculation co-occur routinely.',
         values=[('V-000160', 'septations', None, 'Linear strands crossing the collection.', None),
 ('V-000161', 'loculation', None,
  'Fixed in a non-dependent or lenticular configuration.', None),
 ('V-000162', 'gas', 'RID39157',
  'Gas within the collection without prior instrumentation.', None),
 ('V-000163', 'dependent debris', None, 'Layering higher-attenuation material.', None),
 ('V-000164', 'fluid-fluid level', 'RID35228', 'Two layers of differing attenuation.',
  None)]),

    dict(id='DE-000019',
         prop='hasExtent',
         name='extent',
         unvalidated=True,
         definition='How much of the containing structure a non-discrete process involves.',
         radlex=None,
         values=[('V-000180', 'focal', 'RID5702', 'One limited area.', 1),
 ('V-000181', 'multifocal', 'RID5703', 'Several discrete areas.', 2),
 ('V-000182', 'segmental', 'RID5694', 'Conforming to a named anatomic segment.', 3),
 ('V-000183', 'lobar', None, 'Involving a whole lobe.', 4),
 ('V-000184', 'diffuse', 'RID5701', 'Throughout the structure.', 5)]),

    dict(id='DE-000020',
         prop='hasSeverity',
         name='severity',
         unvalidated=True,
         definition='Graded magnitude of a process where no measurement is taken.',
         radlex=None,
         values=[('V-000190', 'minimal', 'RID5670', 'At the threshold of reportability.', 1),
 ('V-000191', 'mild', 'RID5671', 'Present and of limited degree.', 2),
 ('V-000192', 'moderate', 'RID5672', 'Of intermediate degree.', 3),
 ('V-000193', 'severe', 'RID5673', 'Of marked degree.', 4)]),

    dict(id='DE-000021',
         prop='hasDirection',
         name='direction',
         unvalidated=True,
         definition='Which way a structure is displaced from its expected position.',
         radlex=None,
         values=[('V-000200', 'leftward', None, "Toward the patient's left.", None),
 ('V-000201', 'rightward', None, "Toward the patient's right.", None),
 ('V-000202', 'superior', None, 'Toward the head.', None),
 ('V-000203', 'inferior', None, 'Toward the feet.', None),
 ('V-000204', 'anterior', None, 'Toward the front.', None),
 ('V-000205', 'posterior', None, 'Toward the back.', None)]),

    dict(id='DE-000023',
         prop='hasNarrowingDegree',
         name='degree of narrowing',
         unvalidated=True,
         definition=('How much a lumen is reduced, on the ordinal scale reports use.'),
         radlex=None,
         values=[('V-000220', 'mild', 'RID5671',
  'Under 50 percent. NASCET bands, which are the convention these words carry in carotid '
  'reporting; another convention means something else by the same word.', 1),
 ('V-000221', 'moderate', 'RID5672', '50 to 69 percent, NASCET.', 2),
 ('V-000222', 'severe', 'RID5673', '70 to 99 percent, NASCET, and not near-occlusion.', 3),
 ('V-000224', 'near-occlusion', None,
  'The distal lumen is collapsed rather than merely narrowed, so a percentage understates it. '
  'Read from the string sign rather than from a ratio, which is why it is a band and never a '
  'number.', 4),
 ('V-000223', 'occluded', None, 'No flow through the segment.', 5)],
         note=('Recorded independently of any percentage. A report saying moderate gives this '
 'value and no number; one saying 55 percent gives a number and no value; one saying both '
 'gives both. Nothing here derives one from the other, converts between them, or treats '
 'either as a substitute for the other: the graph records what was said. '
 'The percentage bands are NASCET-flavoured and are certainly wrong for other '
 'territories. The ordinal and the percentage measurement MS-000010 are two encodings '
 'of one criterion, which is the Lung-RADS diameter-versus-volume problem in another '
 'organ.')),

    dict(id='DE-000024',
         prop='hasOcclusiveness',
         name='occlusiveness',
         unvalidated=True,
         definition='Whether intraluminal content obstructs flow through the lumen.',
         radlex=None,
         values=[('V-000230', 'non-occlusive', None, 'Flow persists around the content.', None),
 ('V-000231', 'partially occlusive', None, 'Flow reduced but present.', None),
 ('V-000232', 'occlusive', 'RID4962', 'No flow through the segment.', None)]),

    dict(id='DE-000025',
         prop='hasDeviceIntegrity',
         name='device integrity',
         unvalidated=True,
         definition='Whether a device is intact and functioning as placed.',
         radlex=None,
         values=[('V-000240', 'intact', 'RID39115', 'No abnormality of the device itself.', None),
 ('V-000241', 'fractured', None, 'The device is broken.', None),
 ('V-000242', 'migrated', None, 'The device has moved from its placed position.', None),
 ('V-000243', 'kinked', None, 'The device is acutely angulated.', None),
 ('V-000244', 'disconnected', None, 'A junction has separated.', None)]),

    dict(id='DE-000026',
         prop='hasTipPositionStatus',
         name='tip position status',
         unvalidated=True,
         definition=('Whether a device tip lies where it is intended to lie. The intended position itself '
 'is a property of the device class, not of this element.'),
         radlex=None,
         values=[('V-000250', 'appropriate', None, 'At the intended site.', None),
 ('V-000251', 'suboptimal', None, 'Away from the intended site but functional.', None),
 ('V-000252', 'malpositioned', None, 'In a position that is wrong or unsafe.', None)],
         note=('The intended position varies per device, so a shared value list can only carry '
 'the verdict and not the criterion, which sits on the class.')),

    dict(id='DE-000027',
         prop='hasFractureDisplacement',
         name='fracture displacement',
         unvalidated=True,
         definition='Whether fracture fragments have moved out of alignment.',
         radlex=None,
         values=[('V-000260', 'non-displaced', None, 'Fragments in anatomic alignment.', 1),
 ('V-000261', 'minimally displaced', None, 'Slight loss of alignment.', 2),
 ('V-000262', 'displaced', 'RID5840', 'Clear loss of alignment.', 3)]),

    dict(id='DE-000028',
         prop='hasComminution',
         name='comminution',
         unvalidated=True,
         definition='Whether a fracture has more than two fragments.',
         radlex=None,
         values=[('V-000270', 'simple', None, 'Two fragments.', None),
 ('V-000271', 'comminuted', None, 'More than two fragments.', None)]),

dict(id='DE-000031',
         prop='hasLaterality',
         name='laterality',
         definition='Which side of a paired structure the finding involves.',
         radlex=None,
         anchor_components=[],
         values=[('V-000300', 'left', 'RID5824', "The patient's left.", None),
 ('V-000301', 'right', 'RID5825', "The patient's right.", None),
 ('V-000302', 'bilateral', 'RID5771', 'Both sides.', None),
 ('V-000303', 'midline', 'RID5826', 'Neither side; on the midline.', None)],
         note=('Applies only where the scoped structure is paired or sided. The bilateral value does '
 'not settle whether a bilateral finding is one instance or two; that remains open.')),
]


MEASUREMENTS = [
    dict(id="MS-000001", cls="LongAxisDiameter", name="long-axis diameter",
         definition="The greatest diameter of the lesion on the plane showing its maximal dimension.",
         quantity_kind="length", permitted_units=["mm", "cm"],
         method="Greatest diameter on a single plane, measured on the sequence or window in which the lesion is best seen."),
    dict(id="MS-000002", cls="ShortAxisDiameter", name="short-axis diameter",
         definition="The greatest diameter perpendicular to the long axis, on the same plane.",
         quantity_kind="length", permitted_units=["mm", "cm"],
         method="Perpendicular to the long axis on the plane of maximal dimension."),
    dict(id="MS-000003", cls="MeanDiameter", name="mean diameter",
         definition="The mean of the long- and short-axis diameters on the plane showing the maximal dimension.",
         quantity_kind="length", permitted_units=["mm", "cm"],
         method="Mean of long and short axis on a single plane; lung windows; Fleischner 2017 convention.",
         components=["MS-000001", "MS-000002"],
         derived_from=["MS-000001", "MS-000002"]),
    dict(id="MS-000004", cls="SolidComponentDiameter", name="solid component diameter",
         definition="The greatest diameter of the solid component of a part-solid nodule.",
         quantity_kind="length", permitted_units=["mm", "cm"],
         method="Greatest diameter of the solid component, lung windows."),
    dict(id="MS-000005", cls="AttenuationHU", name="attenuation (Hounsfield units)",
         definition="The mean CT attenuation of the lesion measured within a region of interest.",
         quantity_kind="ct-attenuation", permitted_units=["[hnsf'U]"],
         method="Mean value within a region of interest covering at least two thirds of the lesion, on unenhanced images."),
    dict(id="MS-000006", cls="LesionCount", name="lesion count",
         definition="The number of discrete lesions of this class identified.",
         quantity_kind="count", permitted_units=["1"],
         method="Count of discrete lesions; 'innumerable' is recorded as unbounded rather than as a number."),
    dict(id="MS-000007", cls="WallThickness", name="wall thickness",
         definition="The greatest thickness of the wall bounding a fluid-filled or cavitated structure.",
         quantity_kind="length", permitted_units=["mm"],
         method="Greatest thickness measured perpendicular to the wall."),
    # Descriptor of a normal structure. Attaches to no FindingClass.
]


# ---------------------------------------------------------------------------
# ASSESSMENT SCHEMES  (modelled as their own node type - see DECISIONS.md)
# ---------------------------------------------------------------------------

EXTRA_MEASUREMENTS = [
    dict(id="MS-000009", cls="Volume", name="volume",
         definition="The three-dimensional extent of a lesion or collection.",
         quantity_kind="volume", permitted_units=["mL", "cm3"],
         method="Segmented volume, or the ellipsoid approximation where stated."),
    dict(id="MS-000014", cls="NASCETPercentStenosis", name="NASCET percent stenosis",
         definition="Percentage reduction of the internal carotid lumen, by the NASCET method.",
         quantity_kind="fraction", permitted_units=["%"],
         method="Residual lumen at the stenosis divided by the diameter of the normal distal "
                "internal carotid artery, beyond the bulb. The denominator is the landmark "
                "that makes this method carotid-specific.",
         note="Separate from the ECST method rather than a value on one measurement, because "
              "they are different numbers from the same image: roughly 70 percent NASCET is "
              "85 percent ECST. A model that lets a consumer read one as the other is worse "
              "than one carrying neither."),

    dict(id="MS-000015", cls="ECSTPercentStenosis", name="ECST percent stenosis",
         definition="Percentage reduction of the internal carotid lumen, by the ECST method.",
         quantity_kind="fraction", permitted_units=["%"],
         method="Residual lumen at the stenosis divided by the estimated original lumen at the "
                "same level."),

    dict(id="MS-000017", cls="PeakSystolicVelocity", name="peak systolic velocity",
         definition="The highest flow velocity reached during systole in the segment.",
         quantity_kind="velocity", permitted_units=["cm/s"],
         method="Angle-corrected spectral Doppler at the point of maximal narrowing, "
                "insonation angle 60 degrees or less.",
         note="The axis the external carotid is graded on. Diameter ratios are not used there: "
              "the vessel is small and tortuous and the ratio is unreliable, so velocity "
              "carries the judgement instead."),

    dict(id="MS-000018", cls="EndDiastolicVelocity", name="end diastolic velocity",
         definition="Flow velocity at end diastole in the segment.",
         quantity_kind="velocity", permitted_units=["cm/s"],
         method="Angle-corrected spectral Doppler at the same point as the peak systolic "
                "velocity."),

    dict(id="MS-000016", cls="ResidualLumenDiameter", name="residual lumen diameter",
         definition="The narrowest internal diameter remaining at a stenosis.",
         quantity_kind="length", permitted_units=["mm"],
         method="Narrowest inner-to-inner diameter on the plane of maximal narrowing.",
         note="The numerator both percentage methods share, recorded in its own right because "
              "reports state it."),

dict(id="MS-000011", cls="DisplacementDistance", name="displacement distance",
         definition="How far a structure lies from its expected position.",
         quantity_kind="length", permitted_units=["mm", "cm"],
         method="Perpendicular distance from the expected midline or reference plane."),
    dict(id="MS-000012", cls="RenalLength", name="renal length",
         definition="The greatest pole-to-pole dimension of the kidney.",
         quantity_kind="length", permitted_units=["mm", "cm"],
         method="Greatest pole-to-pole length on the plane of maximal dimension.",
         scoped_to_anatomy=True, scope_target="RID205",
         note="Named for the kidney, not for organs generally, because the method is a kidney "
              "method: pole-to-pole is not how a liver or a spleen is measured. A measurement "
              "IS its method, so a generic organ length with no method would carry no content, "
              "and a generic one with several methods would not say which applied. Another "
              "organ needing a length gets its own measurement with its own method. Nothing is "
              "lost by not having a shared parent: quantity_kind already groups every length. "
              "A normal-structure descriptor; renal enlargement is an interpretation of this "
              "value, not a measurement of its own."),
    dict(id="MS-000013", cls="InvolvedLength", name="involved length",
         definition="The length of a tubular structure affected by a process.",
         quantity_kind="length", permitted_units=["mm", "cm"],
         method="Along the long axis of the structure."),
]

MEASUREMENTS = MEASUREMENTS + EXTRA_MEASUREMENTS


ETIOLOGIES = [
    ("ET-000001", "Infectious", "infectious", "RID3710", "Caused by an infecting organism."),
    ("ET-000002", "Neoplastic", "neoplastic", "RID3957", "Caused by a neoplasm."),
    ("ET-000003", "Inflammatory", "inflammatory", "RID3382", "Caused by a non-infectious inflammatory process."),
    ("ET-000004", "Traumatic", "traumatic", "RID4630", "Caused by physical injury."),
    ("ET-000005", "Vascular", "vascular", None, "Caused by disturbance of blood supply or drainage."),
    ("ET-000006", "Congenital", "congenital", None, "Present from birth."),
    ("ET-000007", "Iatrogenic", "iatrogenic", None, "Caused by medical intervention."),
    ("ET-000008", "Degenerative", "degenerative", "RID5045", "Caused by wear or ageing."),
    ("ET-000009", "Metabolic", "metabolic", None, "Caused by a metabolic derangement."),
    ("ET-000010", "Idiopathic", "idiopathic", "RID5664", "No cause established."),
]


ASSESSMENT_SCHEMES = [
    dict(id="AS-000001", cls="LungRADS", name="Lung-RADS", radlex="RID50134",
         authority="American College of Radiology", scheme_version="2022",
         scope="observation", applies_to=["PulmonaryNodule"],
         categories=[("Lung-RADS 1", "RID50136", 1), ("Lung-RADS 2", "RID50137", 2),
                     ("Lung-RADS 3", "RID50138", 3), ("Lung-RADS 4A", "RID50139", 4),
                     ("Lung-RADS 4B", "RID50140", 5), ("Lung-RADS 4X", "RID50141", 6),
                     ("Lung-RADS S", "RID50710", 7)]),
    dict(id="AS-000002", cls="TIRADS", name="ACR TI-RADS", radlex="RID50503",
         authority="American College of Radiology", scheme_version="2017",
         scope="observation", applies_to=["ThyroidNodule"],
         categories=[("TR1", None, 1), ("TR2", None, 2), ("TR3", None, 3),
                     ("TR4", None, 4), ("TR5", None, 5)]),
    dict(id="AS-000003", cls="LIRADS", name="LI-RADS", radlex="RID49823",
         authority="American College of Radiology", scheme_version="2018",
         scope="observation", applies_to=["Mass"],
         categories=[("LR-1", None, 1), ("LR-2", None, 2), ("LR-3", None, 3),
                     ("LR-4", None, 4), ("LR-5", None, 5), ("LR-M", None, 6),
                     ("LR-TIV", "RID39483", 7)]),
    dict(id="AS-000004", cls="BosniakClassification", name="Bosniak classification", radlex="RID50660",
         authority="Originating author; ACR-referenced", scheme_version="2019",
         scope="observation", applies_to=["Cyst"],
         categories=[("Bosniak I", "RID50661", 1), ("Bosniak II", "RID50662", 2),
                     ("Bosniak IIF", "RID50663", 3), ("Bosniak III", "RID50664", 4),
                     ("Bosniak IV", "RID50665", 5)]),
    dict(id="AS-000005", cls="BIRADS", name="BI-RADS assessment", radlex="RID36027",
         authority="American College of Radiology", scheme_version="5th edition",
         scope="exam", applies_to=["Mass", "Cyst"],
         categories=[("BI-RADS 0", None, 0), ("BI-RADS 1", None, 1), ("BI-RADS 2", None, 2),
                     ("BI-RADS 3", None, 3), ("BI-RADS 4", None, 4), ("BI-RADS 5", None, 5),
                     ("BI-RADS 6", None, 6)]),
]


# ---------------------------------------------------------------------------
# MODALITY / SUBSPECIALTY
# ---------------------------------------------------------------------------

# The RadElement modality list. RadLex codes verified against their labels.
MODALITIES = [
    ("CT",  "CT",  "Computed Tomography",           "RID10321"),
    ("FL",  "FL",  "Fluoroscopy",                   "RID10361"),
    ("MR",  "MR",  "Magnetic Resonance Imaging",    "RID10312"),
    ("NM",  "NM",  "Nuclear Medicine",              "RID10330"),
    ("PET", "PET", "Positron Emission Tomography",  "RID10337"),
    ("US",  "US",  "Ultrasound",                    "RID10326"),
    ("XR",  "XR",  "Projection Radiography",        "RID10345"),
]

# The RadElement subspecialty list, verbatim. Codes are RadElement's, not ours.
SUBSPECIALTIES = [
    ("AB", "AB", "Abdominal Radiology"),
    ("BR", "BR", "Breast Imaging"),
    ("CA", "CA", "Cardiac Radiology"),
    ("CH", "CH", "Chest Radiology"),
    ("ER", "ER", "Emergency Radiology"),
    ("GI", "GI", "Gastrointestinal Radiology"),
    ("GU", "GU", "Genitourinary Radiology"),
    ("HN", "HN", "Head and Neck"),
    ("IR", "IR", "Interventional Radiology"),
    ("MI", "MI", "Molecular Imaging"),
    ("MK", "MK", "Musculoskeletal Radiology"),
    ("NR", "NR", "Neuroradiology"),
    ("OB", "OB", "OB/GYN Radiology"),
    ("OI", "OI", "Oncologic Imaging"),
    ("OT", "OT", "Other"),
    ("PD", "PD", "Pediatric Radiology"),
    ("QI", "QI", "Quality Improvement"),
    ("RS", "RS", "Research"),
    ("VI", "VI", "Vascular Imaging"),
]


# ---------------------------------------------------------------------------
# PATTERNS
#
# Recurring bundles of elements and measurements that show up wherever a
# particular kind of finding is authored. Patterns are NOT nodes. They are not
# written to the graph, they carry no identifier a consumer can reference, and
# nothing subclasses them.
#
# This follows DOSDP (Dead Simple OWL Design Patterns), the practice used across
# OBO by Mondo and uPheno: a pattern is a template that generates axioms for
# each instantiation, and the pattern itself never appears in the ontology.
# Consistency comes from generation plus a lint check at authoring time rather
# than from inheritance at reasoning time.
#
# `anchor` records the source concept the pattern corresponds to, so a reviewer
# can see that RID38780 lesion was considered and deliberately not made a node.
#
# ---------------------------------------------------------------------------

PATTERNS = [
    dict(name="focal-lesion", topics=["margin", "size", "distribution", "calcification"],
         note="A discrete, bounded abnormality."),
    dict(name="nodule", topics=["size"], applies_with="focal-lesion",
         note="A rounded lesion, small relative to what contains it."),
    dict(name="mass", topics=["composition", "enhancement", "size", "effect on neighbours"],
         applies_with="focal-lesion",
         note="A space-occupying lesion that acts on the structures around it."),
    dict(name="cyst", topics=["wall character", "internal contents", "composition"],
         applies_with="focal-lesion", note="A fluid-filled structure bounded by a wall."),
    dict(name="collection", topics=["amount", "internal complexity", "attenuation"],
         note="Material accumulated in a space or potential space."),
    dict(name="parenchymal-alteration", topics=["extent", "pattern", "distribution"],
         note="A change in the character of tissue across a region, without discrete borders."),
    dict(name="volume-alteration", topics=["severity", "extent"],
         note="Loss or gain of tissue volume relative to expected."),
    dict(name="luminal-alteration", topics=["degree", "length involved", "calibre"],
         note="A change in the calibre of a tubular or hollow structure."),
    dict(name="intraluminal-content", topics=["occlusiveness", "length involved"],
         note="Material within a lumen that does not belong there."),
    dict(name="discontinuity", topics=["displacement", "comminution", "acuity"],
         note="A break in a normally continuous structure."),
    dict(name="displacement", topics=["direction", "distance"],
         note="A structure lying away from its expected position."),
    dict(name="device", topics=["integrity", "tip position"],
         note="A man-made object placed in or on the patient."),
    dict(name="variant", topics=["presence"],
         note="Normal alternative anatomy, reported because it can be mistaken for disease."),
]

# PATTERNS ARE NOT NODES AND ARE NOT ELEMENTS.
#
# A pattern lists the TOPICS a kind of finding is usually described by. It names
# no DataElement and inserts nothing. An author writing a new finding sees the
# topics as a checklist, then chooses: reuse an existing element if one genuinely
# fits, or write a new one. Reuse is never forced.
#
# The earlier design had patterns hold element ids and splice them into each class
# at build time. That pushed a shared element onto classes it did not suit, and the
# only way to make it fit was to widen the published element. `margin` reaching nine
# values across three societies, so that a tendon lesion could be reported as
# extra-thyroidal extension, is what that produced. Published elements should not
# move to accommodate new findings.
#
# Discoverability is the useful part and is anatomy-aware: an author scoping a
# finding to the lung should be shown lung-scoped distribution elements, not ones
# whose values come from another organ. That belongs in the authoring tool.

# Lint rules the authoring tool applies. Not schema, not published.
PATTERN_LINT = [
    dict(rule="no-single-value-narrowing",
         says="A narrow list never reduces an element to one value. An element every user "
              "answers the same way is not recording an observation, it is restating the "
              "class definition, and belongs in the definition instead."),
    dict(rule="location-anchored",
         says="A FindingClass says where it is, unless it is reached only through HAS_COMPONENT "
              "and takes its location from the whole that contains it. It does so either with "
              "its own SCOPED_TO, or by inheriting one from a parent. A class with neither "
              "describes a shape without saying where, which is a topic rather than a finding."),
    dict(rule="presence-in-disguise",
         says="An element whose values are only present and absent is a finding wearing an "
              "element's clothes. The thing being asserted belongs in the graph as a "
              "FindingClass or a Diagnosis, and its presence is then carried by the presence "
              "element every finding already has."),
    dict(rule="narrowing-applies",
         says="A narrow list names an element the class actually carries. Narrowing an element "
              "the class does not apply is dead configuration that reads as a constraint."),
    dict(rule="no-duplicate-value-sets",
         says="Two elements must not carry identical value sets. If they do, they are one "
              "element under two names, or one of them was split without the split producing "
              "any difference."),
    dict(rule="element-scope-agrees",
         says="An element or measurement that carries its own anatomic scope is only attached "
              "to a class whose scope is the same location or below it. Attaching thyroid "
              "margin to a renal cyst, or renal length to a pulmonary nodule, is not caught by "
              "anything else. A class may sit BELOW the scope: carotid stenosis at the "
              "internal carotid artery may use a measurement scoped to artery. "
              "CAVEAT: a measurement may also be defined against a landmark in another "
              "anatomic context, as NASCET divides by the diameter of the distal internal "
              "carotid rather than the segment being measured. That is not worked out and this "
              "rule assumes one scope is the whole story."),
    dict(rule="no-ancestor-overlap",
         says="A diagnosis does not point at both a class and one of its ancestors. The "
              "subtype inherits the ancestor edge, so it would carry two claims at once, and "
              "if their strengths differ nothing says which applies. Point at the level where "
              "the claim actually holds: all the subtypes, or the parent, not both."),
    dict(rule="occurs-with-same-type",
         says="OCCURS_WITH relates two findings or two diagnoses. Between a diagnosis and a "
              "finding a more specific edge already exists (MAY_MANIFEST_AS or MAY_CAUSE), so "
              "reaching for co-occurrence there is declining to say which."),
    dict(rule="anchor-verdict",
         says="Every node records an anchor verdict: anchored, post_coordinated, "
              "unanchored_requestable or out_of_primary_scope."),
]


# ---------------------------------------------------------------------------
# FINDING CLASSES
#
# Every one is anchored at a location. There are no abstract genera: `lesion`,
# `nodule`, `mass` and `cyst` are patterns above, applied by name.
# ---------------------------------------------------------------------------

FINDING_CLASSES = [
    dict(id='FC-000005',
         cls='PulmonaryNodule',
         name='pulmonary nodule',
         radlex='RID50149',
         anchor_verdict='anchored',
         definition='A nodule within the lung parenchyma.',
         defined=False,
         elements=['DE-000001', 'DE-000015', 'DE-000039', 'DE-000013', 'DE-000004', 'DE-000031',
 'DE-000002', 'DE-000014'],
         seen_on=['CT', 'MR', 'US', 'XR', 'PET'],
                  modality_scoped={'DE-000002': ['CT'], 'DE-000014': ['PET']},
         scoped_to=[('RID1301', 'region', 'required')],
         refine_to=[('RID1301', 'RID34694', 'lobe of lung')],
         assessed_by=['AS-000001'],
         in_subspecialty=['CH'],
         disjoint_with=['PulmonaryMass'],
         criterion=('Distinguished from pulmonary mass at 30 mm greatest dimension (Fleischner Society, '
 'chest). Organ- and modality-specific; does not generalise.'),
         synonyms=[('lung nodule', 'synonym'), ('SPN', 'abbreviation')],
         synonym_scope={'SPN': 'narrow'},
         measurements=['MS-000001', 'MS-000006', 'MS-000003']),

    dict(id='FC-000006',
         cls='SolidPulmonaryNodule',
         name='solid pulmonary nodule',
         radlex='RID50151',
         anchor_verdict='anchored',
         definition='A pulmonary nodule that completely obscures the underlying lung parenchyma.',
         parent='PulmonaryNodule',
         defined=True,
         differentia=[('hasAttenuation', 'V-000010')],
         elements=['DE-000001', 'DE-000015'],
         seen_on=['CT', 'MR', 'US', 'XR']),

    dict(id='FC-000007',
         cls='PartSolidPulmonaryNodule',
         name='part-solid pulmonary nodule',
         radlex='RID50152',
         anchor_verdict='anchored',
         definition='A pulmonary nodule containing both a solid and a ground-glass component.',
         parent='PulmonaryNodule',
         defined=True,
         differentia=[('hasAttenuation', 'V-000011')],
         components=[('SolidComponentOfPartSolidNodule', 'required')],
         elements=['DE-000001', 'DE-000015'],
         seen_on=['CT', 'MR', 'US', 'XR']),

    dict(id='FC-000008',
         cls='NonSolidPulmonaryNodule',
         name='non-solid pulmonary nodule',
         radlex='RID50153',
         anchor_verdict='anchored',
         definition='A pulmonary nodule that does not obscure the underlying lung parenchyma.',
         parent='PulmonaryNodule',
         defined=True,
         differentia=[('hasAttenuation', 'V-000012')],
         synonyms=[('pure ground-glass pulmonary nodule', 'synonym')],
         elements=['DE-000001', 'DE-000015'],
         seen_on=['CT', 'MR', 'US', 'XR']),

    dict(id='FC-000009',
         cls='SolidComponentOfPartSolidNodule',
         name='solid component of part-solid pulmonary nodule',
         radlex='RID50154',
         anchor_verdict='anchored',
         definition='The solid portion of a part-solid pulmonary nodule.',
         defined=False,
         component=True,
         component_of='PartSolidPulmonaryNodule',
         fixed=[('hasAttenuation', 'V-000010')],
         note='Attenuation is fixed to solid as a class axiom, not offered as an element: nobody chooses it, and a single-value element would be a definition wearing an element. The axiom is what lets a report stating both part-solid and solid resolve, because the two values then sit on two entities rather than one.',
         elements=['DE-000001'],
         measurements=['MS-000004'],
         seen_on=['CT']),

    dict(id='FC-000010',
         cls='ThyroidNodule',
         name='thyroid nodule',
         radlex='RID50509',
         anchor_verdict='anchored',
         definition='A nodule within the thyroid gland.',
         defined=False,
         elements=['DE-000001', 'DE-000015', 'DE-000040', 'DE-000031', 'DE-000005', 'DE-000041',
 'DE-000033'],
         seen_on=['CT', 'MR', 'US', 'XR'],
                  modality_scoped={'DE-000005': ['US'], 'DE-000033': ['US']},
         scoped_to=[('RID7578', 'region', 'required')],
         assessed_by=['AS-000002'],
         in_subspecialty=['HN'],
         note=('Margin values follow ACR TI-RADS 2017: smooth, ill-defined, lobulated or irregular, '
 'extra-thyroidal extension. Lobulated and irregular are one scoring category in the '
 'scheme and are kept separate here, because a radiologist can say which and the '
 "scheme discarding that is the scheme's choice, not ours. Spiculated is subsumed "
 'under irregular, which TI-RADS defines as jagged, spiculated or sharp angles.'),
         measurements=['MS-000001', 'MS-000006', 'MS-000003']),

    dict(id='FC-000011',
         cls='AdrenalNodule',
         name='adrenal nodule',
         anchor_verdict='post_coordinated',
         anchor_base=('RID3875', 'nodule'),
         anchor_modifiers=[('RID88', 'adrenal gland')],
         definition='A nodule within the adrenal gland.',
         defined=False,
         elements=['DE-000001', 'DE-000015', 'DE-000004', 'DE-000031'],
         measurements=['MS-000001', 'MS-000006', 'MS-000003', 'MS-000005'],
         scoped_to=[('RID88', 'region', 'required')],
         refine_to=[('RID88', 'AL-L0006', 'zone of adrenal gland')],
         in_subspecialty=['AB'],
         seen_on=['CT', 'MR', 'US', 'XR']),

    dict(id='FC-000017',
         cls='PulmonaryMass',
         name='pulmonary mass',
         anchor_verdict='post_coordinated',
         anchor_base=('RID3874', 'mass'),
         anchor_modifiers=[('RID1301', 'lung')],
         definition='A space-occupying lesion of the lung exceeding 30 mm.',
         defined=False,
         elements=['DE-000001', 'DE-000015', 'DE-000039', 'DE-000013', 'DE-000004', 'DE-000031'],
         narrow={'DE-000013': ['V-000120', 'V-000121', 'V-000122']},
         scoped_to=[('RID1301', 'region', 'required')],
         in_subspecialty=['CH'],
         measurements=['MS-000001', 'MS-000006'],
         seen_on=['CT', 'MR', 'US', 'XR']),

    dict(id='FC-000018',
         cls='HepaticMass',
         name='hepatic mass',
         anchor_verdict='post_coordinated',
         anchor_base=('RID3874', 'mass'),
         anchor_modifiers=[('RID58', 'liver')],
         definition='A space-occupying lesion of the liver.',
         defined=False,
         elements=['DE-000001', 'DE-000015', 'DE-000007', 'DE-000004'],
         scoped_to=[('RID58', 'region', 'required')],
         assessed_by=['AS-000003'],
         in_subspecialty=['AB'],
         measurements=['MS-000001', 'MS-000006'],
         seen_on=['CT', 'MR', 'US', 'XR']),

    dict(id='FC-000019',
         cls='RenalMass',
         name='renal mass',
         radlex='RID50658',
         match='closeMatch',
         source_label='kidney mass',
         anchor_verdict='anchored',
         definition='A space-occupying lesion of the kidney.',
         defined=False,
         elements=['DE-000001', 'DE-000015', 'DE-000007', 'DE-000004', 'DE-000031'],
         scoped_to=[('RID205', 'region', 'required')],
         in_subspecialty=['AB'],
         note=('Kept distinct from renal lesion. Radiologists say both with a real difference: a '
 'mass asserts space-occupying behaviour, a lesion does not.'),
         measurements=['MS-000001', 'MS-000006'],
         seen_on=['CT', 'MR', 'US', 'XR']),

    dict(id='FC-000020',
         cls='RenalLesion',
         name='renal lesion',
         anchor_verdict='post_coordinated',
         anchor_base=('RID38780', 'lesion'),
         anchor_modifiers=[('RID205', 'kidney')],
         definition='A focal abnormality of the renal parenchyma, not further characterised.',
         defined=False,
         elements=['DE-000001', 'DE-000015', 'DE-000004', 'DE-000031'],
         scoped_to=[('RID205', 'region', 'required')],
         in_subspecialty=['AB'],
         note=('The focal-lesion pattern at the kidney with no further commitment. Distinct from '
 'renal mass, which asserts behaviour.'),
         measurements=['MS-000001', 'MS-000006'],
         seen_on=['CT', 'MR', 'US', 'XR']),

    dict(id='FC-000004',
         cls='RenalCyst',
         name='renal cyst',
         anchor_verdict='post_coordinated',
         anchor_base=('RID3890', 'cyst'),
         anchor_modifiers=[('RID205', 'kidney')],
         definition='A fluid-filled structure bounded by a wall, within the kidney.',
         defined=False,
         elements=['DE-000001', 'DE-000015', 'DE-000008', 'DE-000006', 'DE-000031'],
         scoped_to=[('RID205', 'region', 'required')],
         assessed_by=['AS-000004'],
         in_subspecialty=['AB'],
         measurements=['MS-000001', 'MS-000006', 'MS-000007'],
         seen_on=['CT', 'MR', 'US', 'XR']),

    dict(id='FC-000016',
         cls='SimpleRenalCyst',
         name='simple renal cyst',
         radlex='RID49690',
         match='broadMatch',
         source_label='simple cyst',
         anchor_verdict='anchored',
         definition='A renal cyst with uniformly fluid contents.',
         parent='RenalCyst',
         defined=True,
         differentia=[('hasComposition', 'V-000050')],
         elements=['DE-000001', 'DE-000015'],
         seen_on=['CT', 'MR', 'US', 'XR']),

    dict(id='FC-000015',
         cls='ComplexRenalCyst',
         name='complex renal cyst',
         anchor_verdict='post_coordinated',
         anchor_base=('RID3890', 'cyst'),
         anchor_modifiers=[('RID205', 'kidney')],
         definition='A renal cyst whose contents are not uniformly fluid.',
         note='Carries calcification; the parent does not. A simple cyst does not calcify, and a calcified renal cyst is Bosniak II or above, which is complex by definition.',
         parent='RenalCyst',
         defined=True,
         differentia=[('hasComposition', 'V-000052')],
         elements=['DE-000001', 'DE-000004', 'DE-000015'],
         seen_on=['CT', 'MR', 'US', 'XR']),

    dict(id='FC-000014',
         cls='MuralNodule',
         name='mural nodule',
         anchor_verdict='structurally_expressed',
         anchor_base=('RID3875', 'nodule'),
         definition='A solid nodular projection from the wall of a fluid-filled structure.',
         defined=False,
         component=True,
         component_of='ComplexRenalCyst',
         elements=['DE-000001', 'DE-000007', 'DE-000015'],
         measurements=['MS-000001'],
         note=('No request filed. It is a nodule, and the mural part is already carried by '
 'COMPONENT_OF: a nodule that is a component of a cyst is a mural nodule. Asking for '
 'the pre-coordinated term would duplicate what the graph already says.')),

    dict(id='FC-000021',
         cls='PleuralEffusion',
         name='pleural effusion',
         radlex='RID34539',
         anchor_verdict='anchored',
         definition='Fluid within the pleural space beyond the physiologic few millilitres.',
         defined=False,
         elements=['DE-000001', 'DE-000015', 'DE-000016', 'DE-000017', 'DE-000031'],
         seen_on=['CT', 'US', 'XR'],
         scoped_to=[('RID1363', 'specific', 'required')],
         in_subspecialty=['CH'],
         occurs_with=['Atelectasis', 'Consolidation', 'GroundGlassOpacity', 'MediastinalLymphadenopathy'],
         synonyms=[('pleural fluid', 'synonym'), ('effusion', 'synonym')],
         note=('The first non-focal finding in the build. No margin, no size measurement, no '
 'distribution. Amount, attenuation and internal complexity instead. Its '
 'co-occurrences are the honest statement where no causal or evidential claim is '
 'warranted: an effusion is often seen with these, and saying which produced which '
 'would be guessing. Stored once, symmetric.'),
         measurements=['MS-000009', 'MS-000005']),

    dict(id='FC-000022',
         cls='Pneumothorax',
         name='pneumothorax',
         radlex='RID5352',
         anchor_verdict='anchored',
         definition='Gas within the pleural space.',
         defined=False,
         elements=['DE-000001', 'DE-000015', 'DE-000031', 'DE-000035'],
         scoped_to=[('RID1363', 'specific', 'required')],
         in_subspecialty=['CH'],
         note=('Gas rather than fluid, which is why the collection pattern is about material in a '
 'space rather than fluid in a space. Tension is NOT an element here. It is a '
 'physiological state concluded from a constellation of signs, so it is a Diagnosis '
 'reached by MAY_MANIFEST_AS, the same shape as empyema over pleural effusion.'),
         seen_on=['CT', 'MR', 'US', 'XR']),

    dict(id='FC-000023',
         cls='IntracranialHemorrhage',
         name='intracranial hemorrhage',
         anchor_verdict='post_coordinated',
         anchor_base=('RID4700', 'hemorrhage'),
         anchor_modifiers=[('RID6383', 'intracranial')],
         definition=('Blood within the cranial cavity. The compartment it occupies is the clinically '
 'decisive fact and is carried by the subtypes.'),
         defined=False,
         elements=['DE-000001', 'DE-000015', 'DE-000016', 'DE-000046', 'DE-000038'],
         seen_on=['CT', 'MR', 'US', 'XR'],
         narrow={},
         scoped_to=[('RID9080', 'region', 'required')],
         in_subspecialty=['NR'],
         note=('Anchored to the intracranial region, so it is a class rather than an abstraction. '
 'Acute versus chronic is a temporal-descriptor value on the class, not a further '
 'subtype: RadLex carries acute and chronic as children of temporal descriptor and has '
 'no acute-haemorrhage concept.'),
         measurements=['MS-000009', 'MS-000005']),

    dict(id='FC-000043',
         cls='EpiduralHematoma',
         name='epidural hematoma',
         anchor_verdict='post_coordinated',
         anchor_base=('RID4700', 'hemorrhage'),
         anchor_modifiers=[('RID7111', 'epidural space')],
         definition=('Blood in the potential space between the skull and the dura, characteristically '
 'biconvex and not crossing sutures.'),
         parent='IntracranialHemorrhage',
         defined=False,
         scoped_to=[('RID7111', 'specific', 'required')],
         note='Biconvex: the dura is anchored at the sutures, so the collection cannot cross them.',
         elements=['DE-000001', 'DE-000015'],
         seen_on=['CT', 'MR', 'US', 'XR']),

    dict(id='FC-000044',
         cls='SubduralHematoma',
         name='subdural hematoma',
         anchor_verdict='post_coordinated',
         anchor_base=('RID4700', 'hemorrhage'),
         anchor_modifiers=[('RID7120', 'subdural space')],
         definition=('Blood in the space between the dura and the arachnoid, characteristically crescentic '
 'and crossing sutures.'),
         parent='IntracranialHemorrhage',
         defined=False,
         scoped_to=[('RID7120', 'specific', 'required')],
         note='Crescentic: crosses sutures because the subdural space is not bounded by them.',
         elements=['DE-000001', 'DE-000015'],
         seen_on=['CT', 'MR', 'US', 'XR']),

    dict(id='FC-000045',
         cls='SubarachnoidHemorrhage',
         name='subarachnoid hemorrhage',
         anchor_verdict='post_coordinated',
         anchor_base=('RID4700', 'hemorrhage'),
         anchor_modifiers=[('RID7119', 'subarachnoid space')],
         definition='Blood in the subarachnoid space, filling sulci and basal cisterns.',
         parent='IntracranialHemorrhage',
         defined=False,
         scoped_to=[('RID7119', 'specific', 'required')],
         synonyms=[('SAH', 'abbreviation')],
         note='Conforming: fills sulci and basal cisterns rather than forming a mass.',
         elements=['DE-000001', 'DE-000015'],
         seen_on=['CT', 'MR', 'US', 'XR']),

    dict(id='FC-000046',
         cls='IntraventricularHemorrhage',
         name='intraventricular hemorrhage',
         anchor_verdict='post_coordinated',
         anchor_base=('RID4700', 'hemorrhage'),
         anchor_modifiers=[('RID7123', 'cerebral ventricle')],
         definition='Blood within the ventricular system.',
         parent='IntracranialHemorrhage',
         defined=False,
         scoped_to=[('RID7123', 'specific', 'required')],
         note='Conforming: layers dependently within the ventricles.',
         elements=['DE-000001', 'DE-000015'],
         seen_on=['CT', 'MR', 'US', 'XR']),

    dict(id='FC-000047',
         cls='IntraparenchymalHemorrhage',
         name='intraparenchymal hemorrhage',
         anchor_verdict='post_coordinated',
         anchor_base=('RID4700', 'hemorrhage'),
         anchor_modifiers=[('RID6434', 'brain')],
         definition='Blood within the brain parenchyma itself.',
         parent='IntracranialHemorrhage',
         defined=False,
         scoped_to=[('RID6434', 'region', 'required')],
         note=('Rounded: displaces parenchyma rather than filling a space. Scoped to telencephalon '
 'as a stub. Deep grey, brainstem and cerebellar haemorrhages differ in cause and '
 'prognosis and are not distinguished here.'),
         elements=['DE-000001', 'DE-000015'],
         seen_on=['CT', 'MR', 'US', 'XR']),

    dict(id='FC-000024',
         cls='Consolidation',
         name='consolidation',
         radlex='RID43255',
         anchor_verdict='anchored',
         definition=('Replacement of alveolar air by fluid, cells or other material, obscuring the '
 'underlying vessels.'),
         defined=False,
         elements=['DE-000001', 'DE-000015', 'DE-000019', 'DE-000013', 'DE-000031'],
         seen_on=['CT', 'MR', 'US', 'XR'],
         scoped_to=[('RID35739', 'specific', 'required')],
         in_subspecialty=['CH'],
         synonyms=[('airspace opacity', 'synonym')],
         note=('Scoped to lung parenchyma, which reaches lung only through a locally authored '
 'gap-fill edge. Without it this class derives no body region.')),

    dict(id='FC-000025',
         cls='GroundGlassOpacity',
         name='ground-glass opacity',
         radlex='RID28531',
         anchor_verdict='anchored',
         definition='Hazy increased lung attenuation that does not obscure the vessels.',
         defined=False,
         elements=['DE-000001', 'DE-000015', 'DE-000019', 'DE-000013', 'DE-000031'],
         scoped_to=[('RID35739', 'specific', 'required')],
         in_subspecialty=['CH'],
         seen_on=['CT', 'MR', 'US', 'XR']),

    dict(id='FC-000026',
         cls='StriatedNephrogram',
         name='striated nephrogram',
         anchor_verdict='post_coordinated',
         anchor_base=('RID35573', 'spotted nephrogram'),
         anchor_modifiers=[('RID205', 'kidney')],
         definition=('Alternating linear bands of higher and lower attenuation radiating from the papilla '
 'to the cortex on contrast-enhanced imaging.'),
         defined=False,
         elements=['DE-000001', 'DE-000015', 'DE-000031'],
         scoped_to=[('RID205', 'specific', 'required')],
         in_subspecialty=['AB'],
         note=('The nearest RadLex concept is spotted nephrogram, a different appearance. '
 'Post-coordination here is weaker than usual and a request may be better.'),
         seen_on=['CT', 'MR', 'US', 'XR']),

    dict(id='FC-000027',
         cls='PerinephricStranding',
         name='perinephric fat stranding',
         anchor_verdict='unanchored_requestable',
         request='RADLEX-REQ-0603',
         definition='Increased attenuation with linear or hazy strands in the perirenal fat.',
         defined=False,
         elements=['DE-000001', 'DE-000015', 'DE-000031'],
         scoped_to=[('RID434', 'specific', 'required')],
         in_subspecialty=['AB'],
         note=('RadLex has no concept for stranding at all, by label or synonym, so this cannot be '
 'post-coordinated. A genuine descriptor gap within radiology scope.'),
         seen_on=['CT', 'MR', 'US', 'XR']),

    dict(id='FC-000028',
         cls='WhiteMatterHyperintensity',
         name='white matter hyperintensity',
         anchor_verdict='post_coordinated',
         anchor_base=('RID35805', 'hyperintense'),
         anchor_modifiers=[('RID16996', 'cerebral white matter')],
         definition='Increased T2 signal in the cerebral white matter.',
         defined=False,
         elements=['DE-000001', 'DE-000015'],
         seen_on=['CT', 'MR', 'US', 'XR'],
         scoped_to=[('RID16996', 'specific', 'required')],
         in_subspecialty=['NR'],
         note=('Burden is graded by a named scale (Fazekas), which the model has no home for: an '
 'AssessmentScheme whose input is an extent rather than a set of elements.')),

    dict(id='FC-000029',
         cls='AcuteInfarct',
         name='acute infarct',
         anchor_verdict='post_coordinated',
         anchor_base=('RID5172', 'infarction'),
         anchor_modifiers=[('RID5718', 'acute')],
         definition=('Recent ischaemic tissue death, with restricted diffusion and loss of grey-white '
 'differentiation.'),
         defined=False,
         elements=['DE-000001', 'DE-000015', 'DE-000031', 'DE-000037'],
         seen_on=['CT', 'MR', 'US', 'XR'],
         scoped_to=[('RID6434', 'region', 'required')],
         in_subspecialty=['NR'],
         note=('Scoped to brain, with the arterial territory carried as an element rather than as '
 'scope. RadLex has the cerebral arteries but no concept for the parenchyma each '
 'supplies, so territory cannot currently be an anatomic scope claim.')),

    dict(id='FC-000006B',
         cls='Atelectasis',
         name='atelectasis',
         radlex='RID28493',
         anchor_verdict='anchored',
         definition='Incomplete expansion or collapse of lung tissue.',
         note='One class with two independent axes rather than five subtypes. Mechanism and morphology co-occur, so neither partitions the other, and the five classes this replaces were distinguished by nothing in the model: identical scope, identical elements, no defining value.',
         defined=False,
         elements=['DE-000001', 'DE-000042', 'DE-000043', 'DE-000015', 'DE-000019', 'DE-000031'],
         seen_on=['CT', 'MR', 'US', 'XR'],
         scoped_to=[('RID1301', 'region', 'required')],
         in_subspecialty=['CH'],
         synonyms=[('collapse', 'synonym')]),

dict(id='FC-000030',
         cls='CerebralAtrophy',
         name='cerebral atrophy',
         anchor_verdict='post_coordinated',
         anchor_base=('RID5046', 'atrophy'),
         anchor_modifiers=[('RID6434', 'brain')],
         definition='Loss of brain parenchymal volume beyond that expected for age.',
         defined=False,
         scoped_to=[('RID6434', 'region', 'required')],
         in_subspecialty=['NR'],
         note=('A diffuse burden finding with no discrete lesion and no measurement in routine '
 'reporting. Severity carries the whole content.'),
         elements=['DE-000001', 'DE-000015', 'DE-000020'],
         seen_on=['CT', 'MR', 'US', 'XR']),

    dict(id='FC-000031',
         cls='Encephalomalacia',
         name='encephalomalacia',
         radlex='RID39076',
         anchor_verdict='anchored',
         definition=('Established parenchymal loss with cystic change, the sequela of prior injury or '
 'infarction.'),
         defined=False,
         elements=['DE-000001', 'DE-000015', 'DE-000031'],
         scoped_to=[('RID6434', 'region', 'required')],
         in_subspecialty=['NR'],
         note=('The far end of the MAY_PROGRESS_TO example in D-17. Infarct and encephalomalacia are '
 'genuinely two classes, unlike acute and chronic hemorrhage.'),
         seen_on=['CT', 'MR', 'US', 'XR']),

    dict(id='FC-000032',
         cls='RenalEnlargement',
         name='renal enlargement',
         anchor_verdict='post_coordinated',
         anchor_base=('RID3775', 'enlargement'),
         anchor_modifiers=[('RID205', 'kidney')],
         measurements=['MS-000012'],
         definition='Renal length beyond the expected range for age and body size.',
         defined=False,
         elements=['DE-000001', 'DE-000015', 'DE-000031'],
         scoped_to=[('RID205', 'region', 'required')],
         in_subspecialty=['AB'],
         synonyms=[('nephromegaly', 'synonym')],
         note='An interpretation of the organ-length measurement, not a measurement of its own.',
         seen_on=['CT', 'MR', 'US', 'XR']),

    dict(id='FC-000033',
         cls='RenalCorticalScarring',
         name='renal cortical scarring',
         anchor_verdict='post_coordinated',
         anchor_base=('RID3829', 'scar'),
         anchor_modifiers=[('RID205', 'kidney')],
         definition='Focal cortical thinning with retraction of the overlying contour.',
         defined=False,
         elements=['DE-000001', 'DE-000015', 'DE-000031'],
         scoped_to=[('RID205', 'region', 'required')],
         in_subspecialty=['AB'],
         seen_on=['CT', 'MR', 'US', 'XR']),

    dict(id='FC-000012',
         cls='MediastinalLymphadenopathy',
         name='mediastinal lymphadenopathy',
         radlex='RID3798',
         match='broadMatch',
         source_label='lymphadenopathy',
         anchor_verdict='post_coordinated',
         anchor_base=('RID3798', 'lymphadenopathy'),
         anchor_modifiers=[('RID1384', 'mediastinum')],
         definition='Enlargement of one or more mediastinal lymph nodes.',
         defined=False,
         elements=['DE-000001', 'DE-000015', 'DE-000011', 'DE-000012', 'DE-000014'],
         measurements=['MS-000002'],
         seen_on=['CT', 'MR', 'US', 'XR', 'PET'],
         modality_scoped={'DE-000014': ['PET']},
         scoped_to=[('RID28891', 'class', 'required', 'imported')],
         in_subspecialty=['CH'],
         synonyms=[('adenopathy', 'synonym')],
         note=('Nodal enlargement is a volume alteration whose direction is gain. RadLex asserts '
 'Anatomical_Site RID3798 -> RID13296, so the scope is imported.')),

    dict(id='FC-000053',
         cls='ExternalCarotidArteryStenosis',
         name='external carotid artery stenosis',
         anchor_verdict='post_coordinated',
         anchor_base=('RID5016', 'stenosis'),
         anchor_modifiers=[('RID684', 'external carotid artery')],
         elements=['DE-000001', 'DE-000015', 'DE-000031', 'DE-000045', 'DE-000044'],
         measurements=['MS-000017', 'MS-000018'],
         definition='Narrowing of the external carotid artery lumen.',
         parent=None,
         defined=False,
         in_subspecialty=['NR'],
         scoped_to=[('RID684', 'specific', 'required')],
         seen_on=['CT', 'MR', 'US'],
         note=('Shares a name with internal carotid artery stenosis and almost nothing else. '
               'The internal carotid is graded on five NASCET diameter-ratio bands with two '
               'competing percentage methods; the external carotid is graded on two bands read '
               'from velocity, because the vessel is small and tortuous and a diameter ratio is '
               'unreliable there. Different element, different measurements, different '
               'modality emphasis. '
               'This is why the authoring patterns are topics rather than element bundles: a '
               'pattern that inserted the stenosis machinery into everything called a stenosis '
               'would have put NASCET percentages on this class.')),

    dict(id='FC-000034',
         cls='InternalCarotidArteryStenosis',
         name='internal carotid artery stenosis',
         anchor_verdict='post_coordinated',
         anchor_base=('RID5016', 'stenosis'),
         anchor_modifiers=[('RID585', 'internal carotid artery')],
         note=('Named for the vessel it is scoped to. Carotid stenosis names a family: the common and external carotid arteries stenose too, and their measurements take different baseline landmarks, so they are separate classes rather than values on one. '
         'Carries both the ordinal band and the percentage, and both NASCET and ECST. They are not alternatives and nothing converts between them: 70 percent NASCET is roughly 85 percent ECST, so a consumer reading one as the other would be wrong by a management threshold.'),
         definition='Narrowing of the internal carotid artery lumen.',
         defined=False,
         elements=['DE-000001', 'DE-000015', 'DE-000023', 'DE-000031'],
         scoped_to=[('RID585', 'specific', 'required')],
         in_subspecialty=['NR'],
                  measurements=['MS-000013', 'MS-000016', 'MS-000014', 'MS-000015'],
         seen_on=['CT', 'MR', 'US']),

    dict(id='FC-000035',
         cls='Hydronephrosis',
         name='hydronephrosis',
         radlex='RID34393',
         anchor_verdict='anchored',
         definition='Dilation of the renal collecting system.',
         defined=False,
         elements=['DE-000001', 'DE-000015', 'DE-000020', 'DE-000031'],
         scoped_to=[('RID228', 'specific', 'required')],
         in_subspecialty=['AB'],
         seen_on=['CT', 'MR', 'US', 'XR']),

    dict(id='FC-000036',
         cls='PulmonaryArteryFillingDefect',
         name='pulmonary artery filling defect',
         anchor_verdict='unanchored_requestable',
         request='RADLEX-REQ-0605',
         definition='Intraluminal material within a pulmonary artery on contrast-enhanced CT.',
         defined=False,
         elements=['DE-000001', 'DE-000015', 'DE-000024', 'DE-000031'],
         seen_on=['CT', 'MR', 'US', 'XR'],
         scoped_to=[('RID974', 'specific', 'required')],
         in_subspecialty=['CH'],
         note=('The finding a radiologist sees. Pulmonary embolism is the diagnosis it may '
 'represent, and RadLex carries the diagnosis (RID4834) but not the finding. The same '
 'word naming both is exactly what the finding/diagnosis split is for.'),
         measurements=['MS-000013']),

    dict(id='FC-000037',
         cls='RibFracture',
         name='rib fracture',
         anchor_verdict='post_coordinated',
         anchor_base=('RID4650', 'fracture'),
         anchor_modifiers=[('RID2471', 'rib')],
         definition='A break in the cortex of a rib.',
         defined=False,
         elements=['DE-000001', 'DE-000015', 'DE-000027', 'DE-000028', 'DE-000031', 'DE-000034'],
         seen_on=['CT', 'MR', 'US', 'XR'],
         narrow={'DE-000034': ['V-000330', 'V-000332', 'V-000333', 'V-000335']},
         scoped_to=[('RID2471', 'class', 'required')],
         in_subspecialty=['CH'],
         note=('Acuity is the question in trauma: acute, healing, healed, or of indeterminate age. '
 'Displacement and comminution matter far less. Plurality is the unhandled part: '
 "reports say 'fractures of the left fourth through seventh ribs' and the model has no "
 'way to hold a set.'),
         measurements=['MS-000011']),

    dict(id='FC-000038',
         cls='MidlineShift',
         name='midline shift',
         anchor_verdict='post_coordinated',
         anchor_base=('RID4751', 'displacement'),
         anchor_modifiers=[('RID6434', 'brain')],
         definition='Displacement of midline intracranial structures from the midline.',
         defined=False,
         narrow={'DE-000021': ['V-000200', 'V-000201']},
         scoped_to=[('RID6434', 'region', 'required')],
         in_subspecialty=['NR'],
         elements=['DE-000001', 'DE-000015', 'DE-000021'],
         measurements=['MS-000011'],
         seen_on=['CT', 'MR', 'US', 'XR']),

    dict(id='FC-000039',
         cls='MediastinalShift',
         name='mediastinal shift',
         anchor_verdict='post_coordinated',
         anchor_base=('RID4751', 'displacement'),
         anchor_modifiers=[('RID1384', 'mediastinum')],
         definition='Displacement of the mediastinum from the midline.',
         defined=False,
         narrow={'DE-000021': ['V-000200', 'V-000201']},
         scoped_to=[('RID1384', 'specific', 'required')],
         in_subspecialty=['CH'],
         elements=['DE-000001', 'DE-000015', 'DE-000021'],
         measurements=['MS-000011'],
         seen_on=['CT', 'MR', 'US', 'XR']),

    dict(id='FC-000040',
         cls='VentricularShuntCatheter',
         name='ventricular shunt catheter',
         anchor_verdict='post_coordinated',
         anchor_base=('RID5576', 'catheter'),
         anchor_modifiers=[('RID7123', 'cerebral ventricle')],
         definition='A catheter placed to divert cerebrospinal fluid from the ventricular system.',
         defined=False,
         elements=['DE-000001', 'DE-000015', 'DE-000025', 'DE-000026', 'DE-000031'],
         scoped_to=[('RID7124', 'specific', 'expected')],
         in_subspecialty=['NR'],
         criterion=('Intended tip position is the frontal horn of a lateral ventricle. The criterion sits '
 'here because it varies per device; the element carries only the verdict.'),
         note=('Whether a '
 'malpositioned tip gates a complication component is the open question.'),
         seen_on=['CT', 'MR', 'US', 'XR']),

    dict(id='FC-000041',
         cls='AzygosFissure',
         name='azygos fissure',
         radlex='RID43259',
         anchor_verdict='anchored',
         definition=('An accessory fissure formed by the azygos vein invaginating the right upper lobe '
 'during development.'),
         defined=False,
         scoped_to=[('RID1303', 'region', 'required')],
         in_subspecialty=['CH'],
         note=('Not an abnormality. It takes no severity and its interval change is meaningless, '
 'which is why the variant pattern supplies neither. A pattern set built only from '
 'lesions could not express this at all.'),
         elements=['DE-000001'],
         seen_on=['CT', 'MR', 'US', 'XR']),

    dict(id='FC-000013',
         cls='TendinousLesion',
         name='tendon lesion',
         anchor_verdict='post_coordinated',
         anchor_base=('RID38780', 'lesion'),
         anchor_modifiers=[('RID6067', 'tendon')],
         definition='A lesion involving a tendon.',
         defined=False,
         elements=['DE-000001', 'DE-000015'],
         scoped_to=[('RID6067', 'class', 'required')],
         note=('Exercises SCOPED_TO kind=class, where tendons share no container so PART_OF cannot '
 'express the scope.'),
         measurements=['MS-000001', 'MS-000006'],
         seen_on=['CT', 'MR', 'US', 'XR']),
]


# ---------------------------------------------------------------------------
# DIAGNOSES
#
# A diagnosis carries its own DataElements. Presence is on every one: a report
# saying "findings suggestive of pyelonephritis" and one saying "no evidence of
# pyelonephritis" are different assertions about the same diagnosis, and without
# presence the two are indistinguishable. Severity is on the three a radiologist
# grades directly. Acuity is deliberately absent pending a rule for when acuity
# is pre-coordinated into the name, as in acute infarct, and when it is an
# element, as on rib fracture.
# ---------------------------------------------------------------------------

DIAGNOSES = [
    # ---- thoracic focal ---------------------------------------------------
    dict(id="DX-000001", cls="PulmonaryHamartoma", name="pulmonary hamartoma",
         radlex="RID4335", match="broadMatch", source_label="hamartoma",
         anchor_verdict="post_coordinated",
         anchor_base=("RID4335", "hamartoma"),
         anchor_modifiers=[("RID1301", "lung")],
         elements=["DE-000001"],
         scoped_to=[("RID1301", "region", "required")],
         definition="A benign lung neoplasm of disorganised mesenchymal tissue, "
                    "characteristically containing fat and chondroid calcification.",
         manifests_as=[("SolidPulmonaryNodule", "frequent", "suggestive")],
         etiology=["ET-000006"]),

    dict(id="DX-000002", cls="PulmonaryGranuloma", name="pulmonary granuloma",
         radlex="RID3953", match="broadMatch", source_label="granuloma",
         anchor_verdict="post_coordinated",
         anchor_base=("RID3953", "granuloma"),
         anchor_modifiers=[("RID1301", "lung")],
         elements=["DE-000001"],
         scoped_to=[("RID1301", "region", "required")],
         definition="A focus of granulomatous inflammation in the lung, usually the sequela "
                    "of prior granulomatous infection.",
         manifests_as=[("SolidPulmonaryNodule", "very_frequent", "suggestive")],
         etiology=["ET-000001"]),

    dict(id="DX-000003", cls="IntrapulmonaryLymphNode", name="intrapulmonary lymph node",
         radlex="RID1496", match="exactMatch", source_label="pulmonary lymph node",
         anchor_verdict="anchored", synonym_only_hit=True,
         elements=["DE-000001"],
         scoped_to=[("RID1301", "region", "required")],
         definition="A normal lymph node within the lung parenchyma, characteristically "
                    "perifissural, oval and subpleural.",
         manifests_as=[("SolidPulmonaryNodule", "frequent", "suggestive")],
         note="RID1496 is labelled 'pulmonary lymph node'; the term used here is a synonym. "
              "A label-only duplicate check would have missed it."),

    dict(id="DX-000004", cls="LungCancer", name="lung cancer", radlex="RID45686",
         anchor_verdict="anchored",
         elements=["DE-000001"],
         scoped_to=[("RID1301", "region", "required")],
         definition="Primary malignant neoplasm arising from lung tissue.",
         synonyms=[("bronchogenic carcinoma", "synonym")],
         manifests_as=[("SolidPulmonaryNodule", "frequent", "suggestive"),
                       ("PartSolidPulmonaryNodule", "frequent", "highly_suggestive"),
                       ("NonSolidPulmonaryNodule", "occasional", "suggestive"),
                       ("PulmonaryMass", "frequent", "suggestive"),
                       ("MediastinalLymphadenopathy", "frequent", "suggestive"),
                       ("Atelectasis", "occasional", "suggestive")],
         causes=[("PleuralEffusion", "occasional")],
         etiology=["ET-000002"],
         note="Points at each attenuation subtype separately rather than at the parent. "
              "Singling out one subtype while the rest relied on the parent edge implied that "
              "solid and non-solid nodules were not suggestive of cancer, and left part-solid "
              "carrying two specificities at once, one inherited and one direct. "
              "NEEDS A RADIOLOGIST: the three specificity values. The claim as written is that "
              "part-solid is the most specific for malignancy, solid the commonest "
              "presentation but least specific because most solid nodules are benign, and "
              "non-solid occasional and indolent. "
              "It also reaches a finding by two different edges in different roles: it "
              "manifests as a nodule and it causes an effusion."),

    # ---- pleural ----------------------------------------------------------
    dict(id="DX-000011", cls="Empyema", name="empyema", radlex="RID3714",
         anchor_verdict="anchored",
         elements=["DE-000001"],
         scoped_to=[("RID1363", "specific", "required")],
         definition="Infected pleural fluid: pus in the pleural space.",
         synonyms=[("pleural empyema", "synonym")],
         manifests_as=[("PleuralEffusion", "obligate", "suggestive")],
         etiology=["ET-000001"],
         note="Modelled as a Diagnosis that manifests as a pleural effusion with typicality "
              "obligate, not as a subtype of the finding. 'Empyema without effusion' is not a "
              "meaningful sentence, and obligate is how that is said without collapsing the "
              "finding and diagnosis layers."),

    dict(id="DX-000012", cls="Hemothorax", name="hemothorax", radlex="RID34595",
         anchor_verdict="anchored",
         elements=["DE-000001"],
         scoped_to=[("RID1363", "specific", "required")],
         definition="Blood in the pleural space.",
         manifests_as=[("PleuralEffusion", "obligate", "suggestive")],
         etiology=["ET-000004", "ET-000007"]),

    dict(id="DX-000013", cls="Chylothorax", name="chylothorax", radlex=None,
         anchor_verdict="post_coordinated",
         anchor_base=("RID1545", "chyle"),
         anchor_modifiers=[("RID1363", "pleural space")],
         elements=["DE-000001"],
         scoped_to=[("RID1363", "specific", "required")],
         definition="Chyle in the pleural space from disruption or obstruction of the "
                    "thoracic duct.",
         manifests_as=[("PleuralEffusion", "obligate", "highly_suggestive")],
         etiology=["ET-000004", "ET-000007"],
         note="Absent from RadLex by label and synonym, and a radiologist reports seeing it, "
              "so this is a legitimate request rather than an out-of-scope clinical term."),

    dict(id="DX-000014", cls="ParapneumonicEffusion", name="parapneumonic effusion",
         radlex=None, anchor_verdict="post_coordinated",
         anchor_base=("RID34539", "pleural effusion"),
         anchor_modifiers=[("RID5350", "pneumonia")],
         elements=["DE-000001"],
         scoped_to=[("RID1363", "specific", "required")],
         definition="Pleural effusion accompanying pneumonia, before it becomes an empyema.",
         manifests_as=[("PleuralEffusion", "obligate", "suggestive")],
         progresses_to=["Empyema"],
         etiology=["ET-000001"]),

    # ---- non-imaging diagnoses: causal targets ----------------------------
    dict(id="DX-000027", cls="TensionPneumothorax", name="tension pneumothorax",
         radlex="RID28525", anchor_verdict="anchored",
         elements=["DE-000001"],
         scoped_to=[("RID1363", "specific", "required")],
         definition="A pneumothorax under positive pressure, displacing the mediastinum and "
                    "impairing venous return. A physiological state concluded from imaging "
                    "signs together with the clinical picture, not a feature seen directly.",
         manifests_as=[("Pneumothorax", "obligate", "suggestive"),
                       ("MediastinalShift", "frequent", "highly_suggestive"),
                       ("Atelectasis", "occasional", "suggestive")],
         etiology=["ET-000004", "ET-000007"],
         note="Was briefly modelled as a present/absent DataElement on pneumothorax. That is "
              "the legacy habit of recreating presence as the name of a thing: the value list "
              "was the giveaway. No single sign establishes tension, which is what makes it a "
              "conclusion rather than an attribute."),

    dict(id="DX-000015", cls="HeartFailure", name="heart failure", radlex="RID34795",
         anchor_verdict="anchored",
         elements=["DE-000001"],
         note="Causes the oedema rather than manifesting as it: heart failure raises left "
              "atrial pressure and fluid accumulates, which is production of a second entity. "
              "Nothing here shows itself as anything, which is why it has no manifestation "
              "edge at all. Carried as a node so causal edges have a target; it has no imaging "
              "elements of its own and is not something a radiologist reports seeing.",
         definition="Inability of the heart to maintain adequate output, with venous congestion.",
         causes=[("PulmonaryEdema", "frequent"), ("PleuralEffusion", "frequent")],
         no_imaging_elements=True),

    dict(id="DX-000016", cls="Pneumonia", name="pneumonia", radlex="RID5350",
         anchor_verdict="anchored",
         elements=["DE-000001"],
         scoped_to=[("RID35739", "specific", "required")],
         definition="Infection of the lung parenchyma.",
         manifests_as=[("Consolidation", "very_frequent", "suggestive"),
                       ("GroundGlassOpacity", "frequent", "suggestive")],
         causes=[("PleuralEffusion", "frequent")],
         etiology=["ET-000001"]),

    dict(id="DX-000017", cls="PulmonaryEdema", name="pulmonary edema", radlex="RID4866",
         anchor_verdict="anchored",
         elements=["DE-000001", "DE-000020"],
         scoped_to=[("RID1301", "region", "required")],
         definition="Accumulation of fluid in the lung, most often from raised left atrial "
                    "pressure.",
         manifests_as=[("GroundGlassOpacity", "frequent", "suggestive"),
                       ("Consolidation", "occasional", "suggestive")],
         causes=[("PleuralEffusion", "frequent")],
         etiology=["ET-000005"]),

    dict(id="DX-000018", cls="MalignantNeoplasticDisease", name="malignant neoplastic disease",
         radlex="RID34616", anchor_verdict="anchored",
         elements=["DE-000001"],
         definition="Any malignant neoplasm, primary or metastatic.",
         causes=[("MalignantPleuralEffusion", "occasional")],
         no_imaging_elements=True, etiology=["ET-000002"]),

    dict(id="DX-000026", cls="MalignantPleuralEffusion", name="malignant pleural effusion",
         radlex=None, anchor_verdict="post_coordinated",
         anchor_base=("RID34539", "pleural effusion"),
         anchor_modifiers=[("RID15655", "malignant")],
         elements=["DE-000001"],
         scoped_to=[("RID1363", "specific", "required")],
         definition="Pleural effusion from involvement of the pleura by malignancy.",
         manifests_as=[("PleuralEffusion", "obligate", "suggestive")],
         etiology=["ET-000002"],
         note="Present so the malignant-neoplastic-disease node has somewhere to point. "
              "Without it that node connects to nothing but an etiology, which the graph "
              "evaluator flags as a detached component."),

    dict(id="DX-000019", cls="NephroticSyndrome", name="nephrotic syndrome", radlex=None,
         anchor_verdict="out_of_primary_scope",
         elements=["DE-000001"],
         definition="Heavy proteinuria with hypoalbuminemia and edema.",
         causes=[("PleuralEffusion", "frequent")],
         no_imaging_elements=True,
         note="A clinical syndrome, not something a radiologist observes. RadLex has no "
              "concept and should not be asked for one. SNOMED CT is primary here, which is "
              "the case the out_of_primary_scope verdict exists for."),

    # ---- vascular ---------------------------------------------------------
    dict(id="DX-000020", cls="PulmonaryEmbolism", name="pulmonary embolism", radlex="RID4834",
         anchor_verdict="anchored",
         elements=["DE-000001"],
         scoped_to=[("RID974", "specific", "required")],
         definition="Thromboembolic occlusion of pulmonary arteries.",
         manifests_as=[("PulmonaryArteryFillingDefect", "obligate", "pathognomonic")],
         causes=[("PleuralEffusion", "frequent")],
         etiology=["ET-000005"],
         note="RadLex carries the diagnosis but not the finding it manifests as. The finding "
              "is what a radiologist sees on the images; the diagnosis is the conclusion."),

    # ---- renal ------------------------------------------------------------
    dict(id="DX-000021", cls="AcutePyelonephritis", name="acute pyelonephritis", radlex=None,
         anchor_verdict="post_coordinated",
         anchor_base=("RID3547", "pyelonephritis"),
         anchor_modifiers=[("RID5718", "acute")],
         elements=["DE-000001", "DE-000020"],
         scoped_to=[("RID205", "region", "required")],
         definition="Active bacterial infection of the renal parenchyma and collecting system.",
         manifests_as=[("StriatedNephrogram", "frequent", "highly_suggestive"),
                       ("PerinephricStranding", "frequent", "suggestive"),
                       ("RenalEnlargement", "frequent", "suggestive")],
         etiology=["ET-000001"],
         note="No unqualified parent. A radiologist always chooses a side, because the "
              "acute and chronic pictures look completely different and leaving it ambiguous "
              "would be unhelpful to the treating physician. The unqualified term exists for "
              "billing, not for reporting. "
              "The two are separate classes rather than one class with an acuity element "
              "because acuity changes WHICH FINDINGS the diagnosis reaches, not merely what "
              "they look like: an acuity value on one class would make chronic pyelonephritis "
              "manifest as a striated nephrogram. Compare intracranial haemorrhage, where "
              "acuity is an element because acute and chronic blood are the same finding at "
              "different densities and nothing else changes. "
              "This is also the case that breaks a binary evidential edge: no single "
              "manifestation makes the diagnosis, it is the combination, and specificity "
              "grades each one alone."),

    dict(id="DX-000022", cls="ChronicPyelonephritis", name="chronic pyelonephritis",
         radlex=None, anchor_verdict="post_coordinated",
         anchor_base=("RID3547", "pyelonephritis"),
         anchor_modifiers=[("RID5719", "chronic")],
         elements=["DE-000001"],
         scoped_to=[("RID205", "region", "required")],
         definition="Pyelonephritis with established parenchymal damage from prior or "
                    "recurrent infection.",
         manifests_as=[("RenalCorticalScarring", "very_frequent", "suggestive")],
         etiology=["ET-000001"],
         note="Post-coordinable: RadLex has pyelonephritis and chronic independently. Whether "
              "this is a distinct Diagnosis or a temporal-descriptor value on Pyelonephritis "
              "is the same question probe C3 asks about hemorrhage, and it is answered "
              "differently here because acute and chronic pyelonephritis manifest differently."),

    dict(id="DX-000023", cls="RenalCellCarcinoma", name="renal cell carcinoma",
         radlex="RID4230", match="exactMatch", source_label="renal adenocarcinoma",
         anchor_verdict="anchored", synonym_only_hit=True,
         elements=["DE-000001"],
         scoped_to=[("RID205", "region", "required")],
         definition="A primary malignant neoplasm arising from renal tubular epithelium.",
         synonyms=[("RCC", "abbreviation"), ("hypernephroma", "synonym")],
         manifests_as=[("RenalMass", "frequent", "suggestive"),
                       ("ComplexRenalCyst", "occasional", "suggestive")],
         etiology=["ET-000002"]),

    # ---- other focal ------------------------------------------------------
    dict(id="DX-000005", cls="HepatocellularCarcinoma", name="hepatocellular carcinoma",
         radlex="RID4271", anchor_verdict="anchored",
         elements=["DE-000001"],
         scoped_to=[("RID58", "region", "required")],
         definition="A primary malignant neoplasm arising from hepatocytes.",
         synonyms=[("HCC", "abbreviation")],
         manifests_as=[("HepaticMass", "frequent", "suggestive")],
         assessed_by=["AS-000003"], etiology=["ET-000002"]),

    dict(id="DX-000008", cls="AdrenalAdenoma", name="adrenal adenoma", radlex="RID4211",
         match="broadMatch", source_label="adenoma", anchor_verdict="post_coordinated",
         anchor_base=("RID4211", "adenoma"),
         anchor_modifiers=[("RID92", "cortex of adrenal gland")],
         elements=["DE-000001"],
         scoped_to=[("RID92", "specific", "required")],
         definition="A benign neoplasm of the adrenal cortex.",
         manifests_as=[("AdrenalNodule", "very_frequent", "suggestive")],
         etiology=["ET-000002"]),

    dict(id="DX-000009", cls="MetastaticDisease", name="metastatic disease", radlex="RID5231",
         match="closeMatch", source_label="metastasis", anchor_verdict="anchored",
         elements=["DE-000001"],
         definition="Neoplasm that has spread from a primary site to a discontiguous site.",
         manifests_as=[("PulmonaryNodule", "frequent", "suggestive"),
                       ("HepaticMass", "frequent", "suggestive"),
                       ("MediastinalLymphadenopathy", "frequent", "suggestive"),
                       ("AdrenalNodule", "occasional", "suggestive")],
         etiology=["ET-000002"]),

    dict(id="DX-000010", cls="ReactiveLymphadenopathy", name="reactive lymphadenopathy",
         radlex=None, anchor_verdict="post_coordinated",
         anchor_base=("RID3798", "lymphadenopathy"),
         anchor_modifiers=[("RID3382", "inflammation")],
         elements=["DE-000001"],
         scoped_to=[("RID13296", "class", "required")],
         definition="Lymph node enlargement secondary to a benign immune response.",
         manifests_as=[("MediastinalLymphadenopathy", "frequent", "suggestive")],
         etiology=["ET-000003"]),

    # ---- neuro ------------------------------------------------------------
    dict(id="DX-000024", cls="CerebralInfarction", name="cerebral infarction",
         radlex="RID5172", match="broadMatch", source_label="infarction",
         anchor_verdict="post_coordinated",
         anchor_base=("RID5172", "infarction"),
         anchor_modifiers=[("RID6434", "brain")],
         elements=["DE-000001"],
         scoped_to=[("RID6434", "region", "required")],
         definition="Tissue death in the brain from interruption of arterial supply.",
         manifests_as=[("AcuteInfarct", "obligate", "pathognomonic")],
         causes=[("MidlineShift", "occasional"),
                 ("Encephalomalacia", "very_frequent")],
         etiology=["ET-000005"],
         note="The progression case from D-17. Acute infarct and encephalomalacia are two "
              "genuinely different findings, unlike acute and chronic hemorrhage, which are "
              "one finding with a temporal-descriptor value."),

    dict(id="DX-000025", cls="ChronicSmallVesselDisease", name="chronic small vessel disease",
         radlex=None, anchor_verdict="unanchored_requestable", request="RADLEX-REQ-0612",
         elements=["DE-000001", "DE-000020"],
         scoped_to=[("RID6434", "region", "required")],
         definition="Chronic ischaemic change of the cerebral small vessels.",
         manifests_as=[("WhiteMatterHyperintensity", "obligate", "suggestive"),
                       ("CerebralAtrophy", "frequent", "suggestive")],
         etiology=["ET-000005"]),
]


# ---------------------------------------------------------------------------
# SCOPE RESOLUTION
#
# Why a mention carries no anatomic scope. `stated` and `indeterminate` describe
# a coded finding. `not stated` and `unresolved` describe a mention that never
# became one: with no abstract genus there is no class to put it in, so it is
# recorded as an UnresolvedMention rather than as a vague finding.
#
# ---------------------------------------------------------------------------

SCOPE_RESOLUTION = [
    ("SR-000001", "ScopeStated", "stated",
     "The source names an anatomic location and it was resolved to a node."),
    ("SR-000002", "ScopeNotStated", "not stated",
     "The source names no anatomic location. A fact about the report. Produces an "
     "UnresolvedMention, not a finding."),
    ("SR-000003", "ScopeIndeterminate", "indeterminate",
     "The source refers to a location that cannot be resolved to a single node."),
    ("SR-000004", "ScopeUnresolved", "unresolved",
     "The source names a location that extraction did not resolve. A fact about the "
     "pipeline and a defect rather than a finding. Produces an UnresolvedMention."),
]


SCOPE_ASSERTIONS = []


# ---------------------------------------------------------------------------
# INSTANCE EXAMPLES
# ---------------------------------------------------------------------------

# Deliberately empty.
#
# There were six worked instances and two unresolved mentions. Each paired a
# sentence borrowed from the modelling corpora with a representation authored
# here: which class, which element values, which measurement. The sentence was
# real; the representation was a set of choices, and several asserted things the
# sentence did not say. One example carried distribution=solitary and a
# mean-diameter reading of "5 mm" when the text stated neither, and rendered in
# the OWL indistinguishably from a value that had been derived or checked.
#
# They were removed rather than corrected because they added no coverage. Every
# entailment they tested is tested by a class-level probe that invents nothing:
# probe A3 asserts that a pulmonary nodule whose attenuation is part-solid
# classifies as PartSolidPulmonaryNodule, which is the same claim without a
# fabricated sentence around it.
#
# Instance-level validation needs data nobody here can author: either instances
# written by a radiologist, or the output of something that actually reads text.
# Until one exists, the probes are the honest test.
INSTANCE_EXAMPLES = []

# ---------------------------------------------------------------------------
# UNRESOLVED MENTIONS
#
# Text that names something finding-shaped but does not become a coded finding.
# Not a FindingClass and not in the reportable output: an extraction artifact,
# countable so that underspecification can be measured, and carrying the reason
# so a report that said nothing is distinguishable from a pipeline that missed
# something.
# ---------------------------------------------------------------------------

UNRESOLVED_MENTIONS = []

# ---------------------------------------------------------------------------
# PATTERN EXPANSION AND LINT
#
# The generator applies patterns; the graph never sees them. Provenance is kept
# so a reviewer can tell an authored element from a generated one, which is the
# thing inheritance used to give for free.
# ---------------------------------------------------------------------------

PATTERN_BY_NAME = {p["name"]: p for p in PATTERNS}


PATTERN_BY_NAME = {p["name"]: p for p in PATTERNS}


def expand(fc):
    """Return a class's own content. Patterns supply nothing.

    Kept as a function because the builders call it, but it no longer merges
    anything: a class carries exactly the elements, measurements and modalities
    its author wrote. The empty provenance map is returned for compatibility.
    """
    return (list(fc.get("elements", [])), list(fc.get("measurements", [])),
            list(fc.get("seen_on", [])), {})


def lint():
    """Authoring checks. Advisory: nothing here is enforced by a reasoner, and none
    of it constrains what an author may write. Returns a list of findings."""
    out = []
    seen = {}
    for de in DATA_ELEMENTS:
        key = tuple(sorted(v[1].lower() for v in de["values"]))
        if key in seen:
            out.append(("no-duplicate-value-sets", de["id"],
                        f"has the same value set as {seen[key]}: {list(key)}"))
        else:
            seen[key] = de["id"]

    # A class may be scoped at or BELOW the measurement's scope: carotid stenosis sits at
    # the internal carotid artery and luminal caliber is scoped to artery, which is correct.
    # Needs the anatomy module to walk; skipped when it is not on disk.
    ms_scope = {m["id"]: m["scope_target"] for m in MEASUREMENTS if m.get("scoped_to_anatomy")}
    for de in DATA_ELEMENTS:
        for r in de.get("scoped_to", []):
            ms_scope[de["id"]] = r
    if ms_scope:
        import json as _json, os as _os
        _p = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "anatomy.json")
        up = {}
        if _os.path.exists(_p):
            _a = _json.load(open(_p))
            for _e in _a["is_a"] + _a["part_of"] + _a.get("local_edges", []):
                up.setdefault(_e["frm"], []).append(_e["to"])

            def below(x, target, depth=12):
                seen, front = {x}, [x]
                for _ in range(depth):
                    nxt = []
                    for c in front:
                        for t in up.get(c, []):
                            if t == target:
                                return True
                            if t not in seen:
                                seen.add(t); nxt.append(t)
                    front = nxt
                return False

            for fc in FINDING_CLASSES:
                cls_scope = [x[0] for x in fc.get("scoped_to", [])]
                for msid in list(fc.get("measurements", [])) + list(fc.get("elements", [])):
                    tgt = ms_scope.get(msid)
                    if not tgt or not cls_scope:
                        continue
                    if not any(c == tgt or below(c, tgt) for c in cls_scope):
                        out.append(("element-scope-agrees", fc["cls"],
                                    f"attaches {msid}, scoped to {tgt}, but is scoped to "
                                    f"{cls_scope}, which is not at or below it"))

    par = {f["cls"]: f.get("parent") for f in FINDING_CLASSES}
    def ancestors(c):
        out = []
        while par.get(c):
            c = par[c]; out.append(c)
        return out
    for dx in DIAGNOSES:
        tgts = {t for t, _, _ in dx.get("manifests_as", [])}
        for t in sorted(tgts):
            overlap = [a for a in ancestors(t) if a in tgts]
            if overlap:
                out.append(("no-ancestor-overlap", dx["cls"],
                            f"points at {t} and its ancestor {overlap[0]}"))

    for de in DATA_ELEMENTS:
        if de["id"] == "DE-000001":
            continue
        names = {v[1].lower() for v in de["values"]}
        if names and names <= {"present", "absent", "yes", "no"}:
            out.append(("presence-in-disguise", de["id"],
                        f"'{de['name']}' has only presence-shaped values {sorted(names)}"))

    for fc in FINDING_CLASSES:
        for k, v in (fc.get("narrow") or {}).items():
            if len(v) < 2:
                out.append(("no-single-value-narrowing", fc["cls"],
                            f"narrows {k} to one value, which is part of the definition"))

        # A class may narrow an element it inherits from its parent, so the check
        # walks the ancestor chain rather than only this class's own expansion.
        by_cls = {f["cls"]: f for f in FINDING_CLASSES}
        eff_el, _, _, _ = expand(fc)
        eff_el = list(eff_el)
        anc = fc.get("parent")
        seen_anc = set()
        while anc and anc in by_cls and anc not in seen_anc:
            seen_anc.add(anc)
            eff_el += expand(by_cls[anc])[0]
            anc = by_cls[anc].get("parent")
        for k in (fc.get("narrow") or {}):
            if k not in eff_el:
                out.append(("narrowing-applies", fc["cls"],
                            f"narrows {k}, which the class does not carry"))

        fc_names = {f["cls"] for f in FINDING_CLASSES}
        for tgt in fc.get("occurs_with", []):
            if tgt not in fc_names:
                out.append(("occurs-with-same-type", fc["cls"],
                            f"OCCURS_WITH points at '{tgt}', which is not a FindingClass"))

        anchored = bool(fc.get("scoped_to")) or any(
            d[0].startswith("scopedTo") for d in fc.get("differentia", []))
        if not anchored and not fc.get("component") and not fc.get("parent"):
            out.append(("location-anchored", fc["cls"],
                        "has no anatomic anchor, so it is a pattern that escaped into the graph"))
    return out
