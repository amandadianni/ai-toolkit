---
name: pipefy-html-interfaces
description: >
  Use when the user wants to create, read, or rewrite a Pipefy HTML interface:
  a page whose content is one HTML document, optionally showing live data from
  pipes and tables. Covers choosing data sources, creating the page, and
  rewriting it. Needs HTML interfaces enabled on the organization. For
  grid-layout portals, pages, and sub-portals, use `pipefy-portal-setup`.
tags: [pipefy, interfaces, html, pages, data-sources]
metadata:
  surfaces: "mcp"
---

# HTML interfaces

MCP clients: read [references/mcp.md](references/mcp.md).

An HTML interface is a page whose single element is a `customCode` element holding one HTML document. The element can declare data sources (pipes or tables) that the HTML reads by source id. Writing the HTML publishes it: there is no draft.

## When to use

- "Build a page that shows our open requests", "make a dashboard page from this pipe."
- "Change the layout / copy / colors of my HTML interface."
- "Add the table X as a data source to my page."
- "List my HTML interfaces", "show me the HTML of page Y."

**When not to use:** grid-layout portals, their pages and elements, and sub-portals live in `pipefy-portal-setup` (`list_portals` and `get_portal` cover those, and `get_interface_html` refuses them). Pipes, fields, and cards themselves live in `pipefy-pipes-and-cards`.

## Prerequisites

- **HTML interfaces enabled on the organization.** If a call fails because the feature is not enabled, stop and tell the user: an organization admin has to enable it, and no tool can.
- **Organization id.** Use the numeric id from `list_organizations` (its `id`). `list_interface_repos` accepts only the numeric id; `create_html_interface` and `list_interfaces` accept it too.
- **Admin access to the pipes and tables** the page shows. `list_interface_repos` lists only published pipes and tables the caller administers.

## Operations

| Operation | Read-only | Purpose |
|-----------|-----------|---------|
| `get_interface_html_guidelines` | Yes | The rules the HTML must follow, the `data-pfy-*` vocabulary, the filter format, and a design-system catalog. |
| `list_interface_repos` | Yes | Pipes and tables that can be a data source. |
| `get_interface_repo_fields` | Yes | A pipe's or table's custom fields, to pick a source's `fieldKeys`. |
| `list_interfaces` | Yes | The organization's HTML interfaces. |
| `get_interface_html` | Yes | One interface's pages, elements, data sources, and live HTML. |
| `create_html_interface` | No | Create an interface and write its first page, with optional sources. |
| `set_interface_sources` | No | Replace an element's data sources. |
| `write_interface_html` | No | Replace and publish an element's HTML. |

## Rules that hold in every flow

- **Read the guidelines first.** Call `get_interface_html_guidelines` before writing any HTML, and follow it. This skill does not repeat the rules: the guidelines are their single source, and they change with the platform.
- **Sources before HTML.** Declare a source before the HTML that reads it. HTML that names a source the element does not have renders blank, with no error.
- **Writing is publishing.** `create_html_interface` and `write_interface_html` make the page live at once. Before rewriting a page someone already uses, show the user the change and get their approval.
- **Fix every violation before writing again.** A rejected write stores nothing and lists every violation. Fix all of them in one pass, then write again.

## Steps — create a page

1. **Read the rules.**

   ```text
   get_interface_html_guidelines
   ```

2. **Pick the data** (skip for a page without live data). List candidate repos, then the fields of each one you use:

   ```text
   list_interface_repos organization_id=<org_id> repo_name=<name_fragment>
   get_interface_repo_fields repo_uuid=<repo_uuid>
   ```

   A source is `{"id", "name", "repoId", "fieldKeys", "filters"}`. `repoId` is the repo's `uuid`. `fieldKeys` holds 1 to 30 keys: a custom field's `uuid` (not its `id`), or a built-in key such as `title` (the guidelines list built-in keys under `filters.fixedColumnNames`). `filters` is optional and follows the guidelines' filter format. `id` and `name` are unique within the element; the HTML reads the source by `id`. An element holds at most 10 sources.

3. **Write the HTML** against the guidelines, reading each source by its `id`.

4. **Create the interface** with its sources and HTML in one call:

   ```text
   create_html_interface organization_uuid=<org_id> name="Open requests" html=<document> data_sources=[{"id": "requests", "name": "Open requests", "repoId": <repo_uuid>, "fieldKeys": ["title", <field_uuid>]}]
   ```

   The result carries the new interface's `uuid` and its page and element ids.

## Steps — change an existing page

1. **Find it and read it** right before changing it, since a write replaces the whole document:

   ```text
   list_interfaces organization_uuid=<org_id> search_term=<name_fragment>
   get_interface_html interface_uuid=<interface_uuid>
   ```

   Take `page_id` from `pages[].uuid`, `element_id` from `pages[].elements[].uuid`, and the current sources from the element's `dataSources`.

2. **Change the sources** if the new HTML needs different data. Send the complete list: it replaces the element's sources, and `[]` removes them all. Keep the `id` of every source you keep, because the HTML reads sources by `id`.

   ```text
   set_interface_sources interface_uuid=<interface_uuid> page_id=<page_id> element_id=<element_id> data_sources=[...]
   ```

3. **Write the new HTML**, starting from the document you just read:

   ```text
   write_interface_html page_id=<page_id> element_id=<element_id> content=<document>
   ```

## Success criteria

- The create or write returns success, with no violations.
- `get_interface_html` shows the new document and the expected `dataSources` on the element.
- Every source id the HTML reads is in the element's `dataSources`.

## Failure modes

- **The create succeeded but the write failed.** The interface exists with a blank page, and the error gives its `uuid`, `page_id`, and `element_id`. Resolve the error (fix the HTML for a rejection), then call `write_interface_html` with those ids. Do not call `create_html_interface` again: it would create a second, orphaned interface.
- **The create returned no page to write into.** The interface may exist anyway, and the error gives its `uuid`. Check it with `get_interface_html` before doing anything else, and never retry the create blindly.
- **The HTML was rejected on a write.** Nothing was stored. Fix every listed violation against the guidelines and write again.
- **The page renders blank sections.** The HTML reads a source id that the element does not declare, or one that was renamed or removed. Compare the HTML with `dataSources` from `get_interface_html`, then fix the sources or the HTML.
- **A repo is missing from `list_interface_repos`.** It is unpublished, or the caller is not its admin. An empty list can also mean the organization id is wrong: the listing does not report an unknown organization or interface.
- **`get_interface_html` refuses the interface.** It is a grid-layout portal or sub-portal; use `pipefy-portal-setup`.
- **Unsure what a source update stored.** `set_interface_sources` returns the sources as sent, not as stored. Read them back with `get_interface_html`.

## See also

- `pipefy-portal-setup`: grid-layout portals, pages, elements, and sub-portals.
- `pipefy-pipes-and-cards`: create the pipes and fields a page reads.
