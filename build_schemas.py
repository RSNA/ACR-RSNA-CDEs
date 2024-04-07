#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

SET_SCHEMA_FILENAME = "cde.schema.json"
SET_LIST_SCHEMA_FILENAME = "cde_set_list.schema.json"
ELEMENT_SCHEMA_FILENAME = "cde_element.schema.json"
ELEMENT_LIST_SCHEMA_FILENAME = "cde_element_list.schema.json"

with open(SET_SCHEMA_FILENAME, "r") as f:
    set_schema = json.load(f)

COMMON_DEFINITIONS = ["version", "schema_version", "status", "index_code", "contributors", "event", "specialty", "reference", "integer_value", "value_set", "float_value", "boolean_value", "person", "organization", "value", "image"]
ELEMENT_DEFINITIONS = ["element", *COMMON_DEFINITIONS]

element_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$ref": "#/definitions/element",
    "$id": set_schema["$id"].replace(SET_SCHEMA_FILENAME, ELEMENT_SCHEMA_FILENAME),
    "definitions": { def_name: set_schema["definitions"][def_name] for def_name in ELEMENT_DEFINITIONS }
}

with open(ELEMENT_SCHEMA_FILENAME, "w") as f:
    json.dump(element_schema, f, indent=4)