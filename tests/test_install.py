"""Tests for graphify install --platform routing."""
from pathlib import Path
from unittest.mock import patch
import pytest
import json as _json


PLATFORMS = {
    "claude": (".claude/skills/graphify/SKILL.md",),
    "codex": (".agents/skills/graphify/SKILL.md",),
    "opencode": (".config/opencode/skills/graphify/SKILL.md",),
    "claw": (".claw/skills/graphify/SKILL.md",),
    "droid": (".factory/skills/graphify/SKILL.md",),
    "trae": (".trae/skills/graphify/SKILL.md",),
    "trae-cn": (".trae-cn/skills/graphify/SKILL.md",),
    "windows": (".claude/skills/graphify/SKILL.md",),
}


def _install(tmp_path, platform):
    from graphify.__main__ import install
    with patch("graphify.__main__.Path.home", return_value=tmp_path):
        install(platform=platform)


def test_install_default_claude(tmp_path):
    _install(tmp_path, "claude")
    assert (tmp_path / ".claude" / "skills" / "graphify" / "SKILL.md").exists()


def test_install_codex(tmp_path):
    _install(tmp_path, "codex")
    assert (tmp_path / ".agents" / "skills" / "graphify" / "SKILL.md").exists()


def test_install_opencode(tmp_path):
    _install(tmp_path, "opencode")
    assert (tmp_path / ".config" / "opencode" / "skills" / "graphify" / "SKILL.md").exists()


def test_install_claw(tmp_path):
    _install(tmp_path, "claw")
    assert (tmp_path / ".claw" / "skills" / "graphify" / "SKILL.md").exists()


def test_install_droid(tmp_path):
    _install(tmp_path, "droid")
    assert (tmp_path / ".factory" / "skills" / "graphify" / "SKILL.md").exists()


def test_install_trae(tmp_path):
    _install(tmp_path, "trae")
    assert (tmp_path / ".trae" / "skills" / "graphify" / "SKILL.md").exists()


def test_install_trae_cn(tmp_path):
    _install(tmp_path, "trae-cn")
    assert (tmp_path / ".trae-cn" / "skills" / "graphify" / "SKILL.md").exists()


def test_install_windows(tmp_path):
    _install(tmp_path, "windows")
    assert (tmp_path / ".claude" / "skills" / "graphify" / "SKILL.md").exists()


def test_install_unknown_platform_exits(tmp_path):
    with pytest.raises(SystemExit):
        _install(tmp_path, "unknown")


def test_codex_skill_contains_spawn_agent():
    """Codex skill file must reference spawn_agent."""
    import graphify
    skill = (Path(graphify.__file__).parent / "skill-codex.md").read_text()
    assert "spawn_agent" in skill


def test_opencode_skill_contains_mention():
    """OpenCode skill file must reference @mention."""
    import graphify
    skill = (Path(graphify.__file__).parent / "skill-opencode.md").read_text()
    assert "@mention" in skill


def test_claw_skill_is_sequential():
    """OpenClaw skill file must describe sequential extraction."""
    import graphify
    skill = (Path(graphify.__file__).parent / "skill-claw.md").read_text()
    assert "sequential" in skill.lower()
    assert "spawn_agent" not in skill
    assert "@mention" not in skill


def test_all_skill_files_exist_in_package():
    """All installable platform skill files must be present in the installed package."""
    import graphify
    pkg = Path(graphify.__file__).parent
    for name in ("skill.md", "skill-codex.md", "skill-opencode.md", "skill-claw.md", "skill-windows.md", "skill-droid.md", "skill-trae.md"):
        assert (pkg / name).exists(), f"Missing: {name}"


def test_claude_install_registers_claude_md(tmp_path):
    """Claude platform install writes CLAUDE.md; others do not."""
    _install(tmp_path, "claude")
    assert (tmp_path / ".claude" / "CLAUDE.md").exists()


def test_codex_install_does_not_write_claude_md(tmp_path):
    _install(tmp_path, "codex")
    assert not (tmp_path / ".claude" / "CLAUDE.md").exists()


# --- always-on AGENTS.md install/uninstall tests ---

def _agents_install(tmp_path, platform):
    from graphify.__main__ import _agents_install as _install_fn
    _install_fn(tmp_path, platform)


def _agents_uninstall(tmp_path):
    from graphify.__main__ import _agents_uninstall as _uninstall_fn
    _uninstall_fn(tmp_path)


def test_codex_agents_install_writes_agents_md(tmp_path):
    _agents_install(tmp_path, "codex")
    agents_md = tmp_path / "AGENTS.md"
    assert agents_md.exists()
    assert "graphify" in agents_md.read_text()
    assert "GRAPH_REPORT.md" in agents_md.read_text()


def test_opencode_agents_install_writes_agents_md(tmp_path):
    _agents_install(tmp_path, "opencode")
    assert (tmp_path / "AGENTS.md").exists()


def test_claw_agents_install_writes_agents_md(tmp_path):
    _agents_install(tmp_path, "claw")
    assert (tmp_path / "AGENTS.md").exists()


def test_agents_install_idempotent(tmp_path):
    """Installing twice does not duplicate the section."""
    _agents_install(tmp_path, "codex")
    _agents_install(tmp_path, "codex")
    content = (tmp_path / "AGENTS.md").read_text()
    assert content.count("## graphify") == 1


def test_agents_install_appends_to_existing(tmp_path):
    """Installs into an existing AGENTS.md without overwriting other content."""
    agents_md = tmp_path / "AGENTS.md"
    agents_md.write_text("# Existing rules\n\nDo not break things.\n")
    _agents_install(tmp_path, "codex")
    content = agents_md.read_text()
    assert "Do not break things." in content
    assert "## graphify" in content


def test_agents_uninstall_removes_section(tmp_path):
    _agents_install(tmp_path, "codex")
    _agents_uninstall(tmp_path)
    agents_md = tmp_path / "AGENTS.md"
    # File deleted when it only contained graphify section
    assert not agents_md.exists()


def test_agents_uninstall_preserves_other_content(tmp_path):
    """Uninstall keeps pre-existing content."""
    agents_md = tmp_path / "AGENTS.md"
    agents_md.write_text("# Existing rules\n\nDo not break things.\n")
    _agents_install(tmp_path, "codex")
    _agents_uninstall(tmp_path)
    assert agents_md.exists()
    content = agents_md.read_text()
    assert "Do not break things." in content
    assert "## graphify" not in content


def test_agents_uninstall_no_op_when_not_installed(tmp_path, capsys):
    _agents_uninstall(tmp_path)
    out = capsys.readouterr().out
    assert "nothing to do" in out


# --- OpenCode plugin tests ---

def test_opencode_agents_install_writes_plugin(tmp_path):
    """opencode install writes .opencode/plugins/graphify.js."""
    _agents_install(tmp_path, "opencode")
    plugin = tmp_path / ".opencode" / "plugins" / "graphify.js"
    assert plugin.exists()
    assert "tool.execute.before" in plugin.read_text()


def test_opencode_agents_install_registers_plugin_in_config(tmp_path):
    """opencode install registers the plugin in opencode.json."""
    _agents_install(tmp_path, "opencode")
    config_file = tmp_path / "opencode.json"
    assert config_file.exists()
    import json as _json
    config = _json.loads(config_file.read_text())
    assert any("graphify.js" in p for p in config.get("plugin", []))


def test_opencode_agents_install_merges_existing_config(tmp_path):
    """opencode install preserves existing opencode.json keys."""
    import json as _json
    config_file = tmp_path / "opencode.json"
    config_file.write_text(_json.dumps({"model": "claude-opus-4-5", "plugin": []}))
    _agents_install(tmp_path, "opencode")
    config = _json.loads(config_file.read_text())
    assert config["model"] == "claude-opus-4-5"
    assert any("graphify.js" in p for p in config["plugin"])


def test_opencode_agents_uninstall_removes_plugin(tmp_path):
    """opencode uninstall removes the plugin file and deregisters from opencode.json."""
    import json as _json
    _agents_install(tmp_path, "opencode")
    _agents_uninstall(tmp_path)
    plugin = tmp_path / ".opencode" / "plugins" / "graphify.js"
    assert not plugin.exists()
    config_file = tmp_path / "opencode.json"
    if config_file.exists():
        config = _json.loads(config_file.read_text())
        assert not any("graphify.js" in p for p in config.get("plugin", []))


# ── Cursor ────────────────────────────────────────────────────────────────────

def test_cursor_install_writes_rule(tmp_path):
    """cursor install writes .cursor/rules/graphify.mdc."""
    from graphify.__main__ import _cursor_install
    _cursor_install(tmp_path)
    rule = tmp_path / ".cursor" / "rules" / "graphify.mdc"
    assert rule.exists()
    content = rule.read_text()
    assert "alwaysApply: true" in content
    assert "graphify-out/GRAPH_REPORT.md" in content


def test_cursor_install_idempotent(tmp_path):
    """cursor install does not overwrite an existing rule file."""
    from graphify.__main__ import _cursor_install
    _cursor_install(tmp_path)
    rule = tmp_path / ".cursor" / "rules" / "graphify.mdc"
    original = rule.read_text()
    _cursor_install(tmp_path)
    assert rule.read_text() == original


def test_cursor_uninstall_removes_rule(tmp_path):
    """cursor uninstall removes the rule file."""
    from graphify.__main__ import _cursor_install, _cursor_uninstall
    _cursor_install(tmp_path)
    _cursor_uninstall(tmp_path)
    rule = tmp_path / ".cursor" / "rules" / "graphify.mdc"
    assert not rule.exists()


def test_cursor_uninstall_noop_if_not_installed(tmp_path):
    """cursor uninstall does nothing if rule was never written."""
    from graphify.__main__ import _cursor_uninstall
    _cursor_uninstall(tmp_path)  # should not raise


# ── Gemini CLI ────────────────────────────────────────────────────────────────

def test_gemini_install_writes_gemini_md(tmp_path):
    from graphify.__main__ import gemini_install
    gemini_install(tmp_path)
    md = tmp_path / "GEMINI.md"
    assert md.exists()
    assert "graphify-out/GRAPH_REPORT.md" in md.read_text()

def test_gemini_install_writes_hook(tmp_path):
    import json as _json
    from graphify.__main__ import gemini_install
    gemini_install(tmp_path)
    settings = _json.loads((tmp_path / ".gemini" / "settings.json").read_text())
    hooks = settings["hooks"]["BeforeTool"]
    assert any("graphify" in str(h) for h in hooks)

def test_gemini_install_idempotent(tmp_path):
    from graphify.__main__ import gemini_install
    gemini_install(tmp_path)
    gemini_install(tmp_path)
    md = tmp_path / "GEMINI.md"
    assert md.read_text().count("## graphify") == 1

def test_gemini_install_merges_existing_gemini_md(tmp_path):
    from graphify.__main__ import gemini_install
    (tmp_path / "GEMINI.md").write_text("# My project rules\n")
    gemini_install(tmp_path)
    content = (tmp_path / "GEMINI.md").read_text()
    assert "# My project rules" in content
    assert "graphify-out/GRAPH_REPORT.md" in content

def test_gemini_uninstall_removes_section(tmp_path):
    from graphify.__main__ import gemini_install, gemini_uninstall
    gemini_install(tmp_path)
    gemini_uninstall(tmp_path)
    md = tmp_path / "GEMINI.md"
    assert not md.exists()

def test_gemini_uninstall_removes_hook(tmp_path):
    import json as _json
    from graphify.__main__ import gemini_install, gemini_uninstall
    gemini_install(tmp_path)
    gemini_uninstall(tmp_path)
    settings_path = tmp_path / ".gemini" / "settings.json"
    if settings_path.exists():
        settings = _json.loads(settings_path.read_text())
        hooks = settings.get("hooks", {}).get("BeforeTool", [])
        assert not any("graphify" in str(h) for h in hooks)

def test_gemini_uninstall_noop_if_not_installed(tmp_path):
    from graphify.__main__ import gemini_uninstall
    gemini_uninstall(tmp_path)  # should not raise


# ── Google Antigravity ────────────────────────────────────────────────────────

def _antigravity_install(tmp_path, project_dir=None):
    from graphify.__main__ import antigravity_install
    with patch("graphify.__main__.Path.home", return_value=tmp_path):
        antigravity_install(project_dir or tmp_path)


def _antigravity_uninstall(tmp_path, project_dir=None):
    from graphify.__main__ import antigravity_uninstall
    with patch("graphify.__main__.Path.home", return_value=tmp_path):
        antigravity_uninstall(project_dir or tmp_path)


# --- Skill installation ---

def test_antigravity_install_copies_skill(tmp_path):
    """Install copies skill.md (the build pipeline skill) to the global antigravity skills dir."""
    _antigravity_install(tmp_path)
    skill = tmp_path / ".gemini" / "antigravity" / "skills" / "graphify" / "SKILL.md"
    assert skill.exists()


def test_antigravity_install_skill_is_build_pipeline(tmp_path):
    """The installed global skill must be the build pipeline (skill.md), not a query skill."""
    _antigravity_install(tmp_path)
    skill = tmp_path / ".gemini" / "antigravity" / "skills" / "graphify" / "SKILL.md"
    content = skill.read_text()
    # skill.md contains the pipeline steps — graphify-rs serve is NOT the build pipeline
    assert "graphify-out" in content
    # Must NOT be the query-only skill — that belongs in AGENTS.md
    assert "@mcp:graphify" not in content


def test_antigravity_install_writes_version_stamp(tmp_path):
    """Install writes a .graphify_version file alongside the skill."""
    _antigravity_install(tmp_path)
    version_file = tmp_path / ".gemini" / "antigravity" / "skills" / "graphify" / ".graphify_version"
    assert version_file.exists()


# --- AGENTS.md querying instructions ---

def test_antigravity_install_writes_agents_md(tmp_path):
    """Install writes AGENTS.md with the Antigravity-specific querying instructions."""
    _antigravity_install(tmp_path)
    agents_md = tmp_path / "AGENTS.md"
    assert agents_md.exists()


def test_antigravity_agents_md_contains_marker(tmp_path):
    """AGENTS.md must contain the distinct antigravity marker, not the generic one."""
    _antigravity_install(tmp_path)
    content = (tmp_path / "AGENTS.md").read_text()
    assert "## graphify (antigravity)" in content


def test_antigravity_agents_md_contains_mcp_tools(tmp_path):
    """AGENTS.md must reference the MCP tool names so the agent knows how to query."""
    _antigravity_install(tmp_path)
    content = (tmp_path / "AGENTS.md").read_text()
    assert "@mcp:graphify:query_graph" in content
    assert "@mcp:graphify:get_neighbors" in content
    assert "@mcp:graphify:god_nodes" in content
    assert "@mcp:graphify:shortest_path" in content
    assert "@mcp:graphify:graph_stats" in content


def test_antigravity_agents_md_contains_graph_report(tmp_path):
    """AGENTS.md must reference GRAPH_REPORT.md for the always-on orientation step."""
    _antigravity_install(tmp_path)
    content = (tmp_path / "AGENTS.md").read_text()
    assert "GRAPH_REPORT.md" in content


def test_antigravity_install_idempotent(tmp_path):
    """Installing twice does not duplicate the AGENTS.md section."""
    _antigravity_install(tmp_path)
    _antigravity_install(tmp_path)
    content = (tmp_path / "AGENTS.md").read_text()
    assert content.count("## graphify (antigravity)") == 1


def test_antigravity_install_appends_to_existing_agents_md(tmp_path):
    """Install appends to an existing AGENTS.md without overwriting other content."""
    agents_md = tmp_path / "AGENTS.md"
    agents_md.write_text("# Existing rules\n\nDo not break things.\n")
    _antigravity_install(tmp_path)
    content = agents_md.read_text()
    assert "Do not break things." in content
    assert "## graphify (antigravity)" in content


def test_antigravity_marker_does_not_collide_with_generic_marker(tmp_path):
    """The antigravity section marker must be distinct from the generic ## graphify marker
    so both can coexist in a project that also uses Codex or another AGENTS.md platform."""
    from graphify.__main__ import _agents_install
    # Install a generic platform section first
    _agents_install(tmp_path, "codex")
    # Then install antigravity alongside it
    _antigravity_install(tmp_path)
    content = (tmp_path / "AGENTS.md").read_text()
    # Both sections present, neither overwrote the other
    assert "## graphify" in content
    assert "## graphify (antigravity)" in content
    assert content.count("## graphify") == 2  # one generic, one antigravity


# --- MCP server registration ---

def test_antigravity_install_creates_mcp_config(tmp_path):
    """Install creates mcp_config.json if it does not exist."""
    _antigravity_install(tmp_path)
    mcp_path = tmp_path / ".gemini" / "antigravity" / "mcp_config.json"
    assert mcp_path.exists()


def test_antigravity_mcp_config_correct_structure(tmp_path):
    """mcp_config.json must have the correct graphify server structure."""
    _antigravity_install(tmp_path)
    config = _json.loads((tmp_path / ".gemini" / "antigravity" / "mcp_config.json").read_text())
    server = config["mcpServers"]["graphify"]
    assert server["command"] == "graphify-rs"
    assert any("graph.json" in arg for arg in server["args"])
    assert server["env"]["DISABLE_CONSOLE_OUTPUT"] == "true"
    assert server["env"]["MCP_MODE"] == "stdio"


def test_antigravity_mcp_config_uses_absolute_path(tmp_path):
    """The graph path in mcp_config.json must be absolute to avoid working-directory issues."""
    _antigravity_install(tmp_path)
    config = _json.loads((tmp_path / ".gemini" / "antigravity" / "mcp_config.json").read_text())
    graph_arg = next(arg for arg in config["mcpServers"]["graphify"]["args"] if "graph.json" in arg)
    assert Path(graph_arg).is_absolute()


def test_antigravity_install_preserves_existing_mcp_servers(tmp_path):
    """Install must not remove other servers already in mcp_config.json."""
    mcp_path = tmp_path / ".gemini" / "antigravity" / "mcp_config.json"
    mcp_path.parent.mkdir(parents=True, exist_ok=True)
    mcp_path.write_text(_json.dumps({"mcpServers": {"other-tool": {"command": "foo"}}}))
    _antigravity_install(tmp_path)
    config = _json.loads(mcp_path.read_text())
    assert "other-tool" in config["mcpServers"]
    assert "graphify" in config["mcpServers"]


def test_antigravity_install_handles_malformed_mcp_config(tmp_path):
    """Install recovers gracefully if mcp_config.json exists but is not valid JSON."""
    mcp_path = tmp_path / ".gemini" / "antigravity" / "mcp_config.json"
    mcp_path.parent.mkdir(parents=True, exist_ok=True)
    mcp_path.write_text("this is not json {{{")
    # Should not raise — should overwrite with a clean config
    _antigravity_install(tmp_path)
    config = _json.loads(mcp_path.read_text())
    assert "graphify" in config["mcpServers"]


# --- Uninstall ---

def test_antigravity_uninstall_removes_skill(tmp_path):
    """Uninstall removes the skill file from the global antigravity skills dir."""
    _antigravity_install(tmp_path)
    _antigravity_uninstall(tmp_path)
    skill = tmp_path / ".gemini" / "antigravity" / "skills" / "graphify" / "SKILL.md"
    assert not skill.exists()


def test_antigravity_uninstall_removes_agents_md_section(tmp_path):
    """Uninstall removes the graphify (antigravity) section from AGENTS.md."""
    _antigravity_install(tmp_path)
    _antigravity_uninstall(tmp_path)
    agents_md = tmp_path / "AGENTS.md"
    # File deleted when it only contained the graphify section
    assert not agents_md.exists()


def test_antigravity_uninstall_preserves_other_agents_md_content(tmp_path):
    """Uninstall keeps pre-existing AGENTS.md content intact."""
    agents_md = tmp_path / "AGENTS.md"
    agents_md.write_text("# Existing rules\n\nDo not break things.\n")
    _antigravity_install(tmp_path)
    _antigravity_uninstall(tmp_path)
    assert agents_md.exists()
    content = agents_md.read_text()
    assert "Do not break things." in content
    assert "## graphify (antigravity)" not in content


def test_antigravity_uninstall_preserves_generic_graphify_section(tmp_path):
    """Uninstall must not remove a generic ## graphify section added by another platform."""
    from graphify.__main__ import _agents_install
    _agents_install(tmp_path, "codex")
    _antigravity_install(tmp_path)
    _antigravity_uninstall(tmp_path)
    content = (tmp_path / "AGENTS.md").read_text()
    assert "## graphify" in content
    assert "## graphify (antigravity)" not in content


def test_antigravity_uninstall_removes_mcp_entry(tmp_path):
    """Uninstall removes the graphify entry from mcp_config.json."""
    _antigravity_install(tmp_path)
    _antigravity_uninstall(tmp_path)
    mcp_path = tmp_path / ".gemini" / "antigravity" / "mcp_config.json"
    if mcp_path.exists():
        config = _json.loads(mcp_path.read_text())
        assert "graphify" not in config.get("mcpServers", {})


def test_antigravity_uninstall_preserves_other_mcp_servers(tmp_path):
    """Uninstall only removes the graphify MCP entry, leaving other servers untouched."""
    mcp_path = tmp_path / ".gemini" / "antigravity" / "mcp_config.json"
    mcp_path.parent.mkdir(parents=True, exist_ok=True)
    mcp_path.write_text(_json.dumps({"mcpServers": {"other-tool": {"command": "foo"}}}))
    _antigravity_install(tmp_path)
    _antigravity_uninstall(tmp_path)
    config = _json.loads(mcp_path.read_text())
    assert "other-tool" in config["mcpServers"]
    assert "graphify" not in config["mcpServers"]


def test_antigravity_uninstall_noop_when_not_installed(tmp_path):
    """Uninstall does not raise when nothing has been installed."""
    _antigravity_uninstall(tmp_path)  # should not raise


def test_antigravity_uninstall_handles_malformed_mcp_config(tmp_path, capsys):
    """Uninstall prints a warning and continues if mcp_config.json is not valid JSON."""
    _antigravity_install(tmp_path)
    mcp_path = tmp_path / ".gemini" / "antigravity" / "mcp_config.json"
    mcp_path.write_text("this is not json {{{")
    _antigravity_uninstall(tmp_path)  # should not raise
    err = capsys.readouterr().err
    assert "warning" in err.lower()


# --- Template file integrity ---

def test_antigravity_agents_template_exists_in_package():
    """agents-antigravity.md must be present in the installed package."""
    import graphify
    template = Path(graphify.__file__).parent / "agents-antigravity.md"
    assert template.exists(), "Missing: agents-antigravity.md"


def test_antigravity_agents_template_contains_marker():
    """agents-antigravity.md must contain the expected heading so uninstall can find it."""
    import graphify
    template = Path(graphify.__file__).parent / "agents-antigravity.md"
    assert "## graphify (antigravity)" in template.read_text()


def test_antigravity_install_fails_if_template_marker_missing(tmp_path, tmp_path_factory):
    """Install exits with an error if agents-antigravity.md is missing its heading."""
    import graphify.__main__ as main_mod
    bad_template = tmp_path_factory.mktemp("bad") / "agents-antigravity.md"
    bad_template.write_text("This file has no heading.\n")
    with patch.object(Path, "parent", new_callable=lambda: property(lambda self: bad_template.parent)):
        pass  # patching Path.parent globally is too broad — use a targeted patch instead

    original = main_mod.Path
    class PatchedPath(original):
        def __truediv__(self, other):
            result = super().__truediv__(other)
            if str(other) == "agents-antigravity.md":
                return bad_template
            return result

    with patch("graphify.__main__.Path", PatchedPath):
        with patch("graphify.__main__.Path.home", return_value=tmp_path):
            with pytest.raises(SystemExit):
                from graphify.__main__ import antigravity_install
                antigravity_install(tmp_path)
