## graphify (antigravity)

This project has a graphify knowledge graph at graphify-out/. A live MCP server
is registered under @mcp:graphify — use it as your primary source of truth for
all architectural and discovery tasks. Do not grep or glob for structural
information while the graph is available.

### Graph-first policy

1. At the start of any architectural, search, or impact-analysis task, verify
   the graph is live by calling @mcp:graphify:graph_stats.
2. Read graphify-out/GRAPH_REPORT.md for the high-level map of communities and
   god nodes before querying in detail.
3. Use @mcp:graphify:query_graph as your primary search mechanism.
4. Only fall back to full-repo grep or glob if graph search yields no results.
5. Before proposing major architectural changes, confirm your plan aligns with
   existing community structures and god nodes from GRAPH_REPORT.md.

### Available MCP tools

| Tool          | Parameters                   | Use for                                         |
| ------------- | ---------------------------- | ----------------------------------------------- |
| query_graph   | query (string)               | Keyword search → relevant subgraph. Start here. |
| get_node      | id (string)                  | Full metadata for a specific node               |
| get_neighbors | id (string)                  | Adjacent nodes and edge types                   |
| get_community | community_id (string)        | All nodes in a Leiden cluster                   |
| god_nodes     | none                         | Most connected hub nodes                        |
| graph_stats   | none                         | Node counts, edge types, density                |
| shortest_path | start (string), end (string) | Direct connection between two concepts          |

### Query patterns

**Architecture / "how does X work?"**

1. @mcp:graphify:god_nodes — identify load-bearing hubs
2. @mcp:graphify:query_graph("X") — find X and its context
3. @mcp:graphify:get_neighbors(X.id) — understand dependencies
4. Read GRAPH_REPORT.md community section for X's architectural layer

**Code search / "where is X implemented?"**

1. @mcp:graphify:query_graph("X") — find candidate nodes
2. @mcp:graphify:get_node(best_match.id) — confirm source_file
3. @mcp:graphify:get_neighbors(best_match.id) — confirm correct X by its
   connections

**Impact analysis / "what breaks if I change X?"**

1. @mcp:graphify:query_graph("X") — find X
2. @mcp:graphify:get_neighbors(X.id) — direct dependents
3. @mcp:graphify:get_community(X.community_id) — everything tightly coupled to X
4. Repeat get_neighbors for each critical dependent for second-order impact

**Relationship tracing / "how are X and Y connected?"**

1. @mcp:graphify:query_graph("X") and query_graph("Y") — confirm both exist
2. @mcp:graphify:shortest_path(X.label, Y.label) — find the connection
3. Explain each hop in plain language

**Community exploration / "show me the auth layer"**

1. @mcp:graphify:god_nodes — find the anchor node for that layer
2. @mcp:graphify:get_community(anchor.community_id) — list all nodes in the
   cluster
3. Summarise the community's responsibility and key internal edges

### Keeping the graph current

If the graph seems stale after recent code changes:

- Incremental refresh: run `graphify-rs build --update` in the terminal
- Full rebuild: run `graphify-rs build .`
- Re-call @mcp:graphify:graph_stats to confirm updated node/edge counts

### Honesty rules

- Never invent a relationship not present in the graph. If a connection is
  absent, say so explicitly.
- Always cite the edge type (EXTRACTED / INFERRED / AMBIGUOUS) when confidence
  is relevant to your answer.
- If the graph is stale and you know it, say so before answering.
- Never skip the graph_stats check — a disconnected MCP server produces silent
  "no results" that look like genuine absence.
