#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

JSON_SCHEMA_URL = "http://json-schema.org/draft-07/schema#"

SET_SCHEMA_FILENAME = "cde.schema.json"
SET_LIST_SCHEMA_FILENAME = "cde_set_list.schema.json"
ELEMENT_SCHEMA_FILENAME = "cde_element.schema.json"
ELEMENT_LIST_SCHEMA_FILENAME = "cde_element_list.schema.json"

with open(SET_SCHEMA_FILENAME, "r") as f:
    set_schema = json.load(f)

ELEMENT_DEFINITIONS = [
    "element",
    "version",
    "schema_version",
    "status",
    "index_code",
    "contributors",
    "event",
    "specialty",
    "reference",
    "integer_value",
    "value_set",
    "float_value",
    "boolean_value",
    "person",
    "organization",
    "value",
    "image",
]

element_definitions = {
    def_name: set_schema["definitions"][def_name] for def_name in ELEMENT_DEFINITIONS
}

element_schema = {
    "$schema": JSON_SCHEMA_URL,
    "$ref": "#/definitions/element",
    "$id": set_schema["$id"].replace(SET_SCHEMA_FILENAME, ELEMENT_SCHEMA_FILENAME),
    "definitions": element_definitions,
}

set_list_schema = {
    "$schema": JSON_SCHEMA_URL,
    "$ref": "#/definitions/set_list",
    "$id": set_schema["$id"].replace(SET_SCHEMA_FILENAME, SET_LIST_SCHEMA_FILENAME),
    "definitions": {
        "set_list": {
            "type": "array",
            "items": {"$ref": "#/definitions/element_set"},
        },
        **set_schema["definitions"],
    },
}

element_list_schema = {
    "$schema": JSON_SCHEMA_URL,
    "$ref": "#/definitions/element_list",
    "$id": set_schema["$id"].replace(SET_SCHEMA_FILENAME, ELEMENT_LIST_SCHEMA_FILENAME),
    "definitions": {
        "element_list": {
            "type": "array",
            "items": {"$ref": "#/definitions/element"},
        },
        **element_definitions,
    },
}


def write_schema_file(filename, schema):
    with open(filename, "w") as f:
        json.dump(schema, f, indent=4)


write_schema_file(ELEMENT_SCHEMA_FILENAME, element_schema)
write_schema_file(SET_LIST_SCHEMA_FILENAME, set_list_schema)
write_schema_file(ELEMENT_LIST_SCHEMA_FILENAME, element_list_schema)
