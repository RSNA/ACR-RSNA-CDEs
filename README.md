# RSNA/ACR Common Data Element (CDE) Project

This repository defines the data model behind the [RSNA/ACR CDE project](https://radelement.org).

This data model provides the structure and syntax of a well-formed CDE set containing elements and values. It is most useful for those developing software tools to create or consume CDEs. 

Information around the content that is represented within this structure can be found in our [authoring guide](https://radelement.org/about/guides/authoring) and our [standardization guide](https://radelement.org/about/guides/standardization). 

Our repository has an [API](https://radelement.org/about/docs)

## Repository Introduction
**cde.schema.json**
This file contains the latest version of the schema, written in JSON schema draft-07. 

**SampleDES.cdes.json**
A JSON file representing a CDE set that idenfies the questions (elements) needed to completely evaluate an adrenal nodule during adrenal protocol CT.

**build_schmeas.py**
A local development tool that creates schema files to validate json documents containing lists of sets, lists of elements, and a single element. The checks are automatic in vscode if you use the following file suffixes:

| granularity  | filename         |
| ------------ | ---------------- |
| element      | *.cde.json       |
| element list | *.cde_list.json  |
| set          | *.cdes.json      |
| set list     | *.cdes_list.json |

**deprecated**
Includes prior versions of the schema in several legacy formats

**.vscode, .gitignore**
Configuration for Visual Studio Code, and Git
