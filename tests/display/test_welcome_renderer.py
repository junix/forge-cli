"""Tests for WelcomeRenderer class."""

from unittest.mock import Mock

import pytest
from rich.panel import Panel

from forge_cli.config import AppConfig
from forge_cli.display.v3.renderers.rich.welcome import WelcomeRenderer


class TestWelcomeRenderer:
    """Test WelcomeRenderer class."""
    
    def test_basic_welcome_render(self):
        """Test basic welcome panel creation."""
        renderer = WelcomeRenderer()
        result = renderer.render()
        
        # Should return a Panel object
        assert isinstance(result, Panel)
        
        # Panel should contain welcome text
        panel_content = str(result.renderable)
        assert "Welcome to" in panel_content
        assert "Knowledge Forge Chat" in panel_content
    
    def test_with_model(self):
        """Test adding model information."""
        result = (WelcomeRenderer()
                 .with_model("qwen-max-latest")
                 .render())
        
        panel_content = str(result.renderable)
        assert "Model:" in panel_content
        assert "qwen-max-latest" in panel_content
    
    def test_with_tools(self):
        """Test adding tools information."""
        tools = ["file-search", "web-search", "page-reader"]
        result = (WelcomeRenderer()
                 .with_tools(tools)
                 .render())
        
        panel_content = str(result.renderable)
        assert "Tools:" in panel_content
        assert "file-search, web-search, page-reader" in panel_content
    
    def test_with_empty_tools(self):
        """Test with empty tools list."""
        result = (WelcomeRenderer()
                 .with_tools([])
                 .render())
        
        panel_content = str(result.renderable)
        # Should not show tools section when empty
        assert "Tools:" not in panel_content
    
    def test_with_custom_title(self):
        """Test custom title setting."""
        custom_title = "My Custom Chat"
        result = (WelcomeRenderer()
                 .with_title(custom_title)
                 .render())
        
        # Check panel title
        assert custom_title in result.title
    
    def test_with_version_info(self):
        """Test custom version info."""
        version_info = "(v4 Beta)"
        result = (WelcomeRenderer()
                 .with_version_info(version_info)
                 .render())
        
        panel_content = str(result.renderable)
        assert version_info in panel_content
    
    def test_builder_pattern_chaining(self):
        """Test method chaining with builder pattern."""
        result = (WelcomeRenderer()
                 .with_model("deepseek-r1")
                 .with_tools(["file-search", "code-interpreter"])
                 .with_title("Dev Chat")
                 .with_version_info("(Development Build)")
                 .render())
        
        panel_content = str(result.renderable)
        
        # All information should be present
        assert "deepseek-r1" in panel_content
        assert "file-search, code-interpreter" in panel_content
        assert "Development Build" in panel_content
        assert "Dev Chat" in result.title
    
    def test_from_config_with_full_config(self):
        """Test from_config class method with complete configuration."""
        # Mock config object
        config = Mock()
        config.model = "qwen-turbo"
        config.enabled_tools = ["web-search", "page-reader"]
        
        renderer = WelcomeRenderer.from_config(config)
        result = renderer.render()
        
        panel_content = str(result.renderable)
        assert "qwen-turbo" in panel_content
        assert "web-search, page-reader" in panel_content
    
    def test_from_config_with_partial_config(self):
        """Test from_config with partial configuration."""
        # Create a more realistic config object
        class PartialConfig:
            def __init__(self):
                self.model = "claude-3"
                # Explicitly don't set enabled_tools
        
        config = PartialConfig()
        renderer = WelcomeRenderer.from_config(config)
        result = renderer.render()
        
        panel_content = str(result.renderable)
        assert "claude-3" in panel_content
        # Should not crash when enabled_tools is missing
        assert "Tools:" not in panel_content
    
    def test_from_config_with_empty_config(self):
        """Test from_config with empty configuration."""
        # Create a config with no relevant attributes
        class EmptyConfig:
            pass
        
        config = EmptyConfig()
        renderer = WelcomeRenderer.from_config(config)
        result = renderer.render()
        
        # Should still create a valid panel
        assert isinstance(result, Panel)
        panel_content = str(result.renderable)
        assert "Welcome to" in panel_content
    
    def test_ascii_art_presence(self):
        """Test that ASCII art is included in the welcome message."""
        result = WelcomeRenderer().render()
        panel_content = str(result.renderable)
        
        # Check for parts of the ASCII art
        assert "____" in panel_content  # Top of ASCII art
        assert "Knowledge Forge" in panel_content  # Should be in ASCII or text
    
    def test_help_command_hint(self):
        """Test that help command hint is included."""
        result = WelcomeRenderer().render()
        panel_content = str(result.renderable)
        
        assert "/help" in panel_content
        assert "available commands" in panel_content
    
    def test_panel_styling(self):
        """Test panel styling properties."""
        result = WelcomeRenderer().render()
        
        # Check panel properties
        assert result.border_style == "cyan"
        assert result.padding == (1, 2)
        assert "cyan" in result.title  # Title should have cyan styling

    def test_from_config_with_real_appconfig(self):
        """Test from_config with real AppConfig instance."""
        # Create a real AppConfig instance using the correct alias
        config = AppConfig(
            model="deepseek-r1-distill-qwen-32b",
            tool=["file-search", "web-search", "page-reader"],
            effort="medium"
        )
        
        renderer = WelcomeRenderer.from_config(config)
        result = renderer.render()
        
        panel_content = str(result.renderable)
        assert "deepseek-r1-distill-qwen-32b" in panel_content
        assert "file-search, web-search, page-reader" in panel_content

    def test_from_config_with_minimal_appconfig(self):
        """Test from_config with minimal AppConfig instance."""
        # Create AppConfig with minimal settings (uses defaults)
        config = AppConfig()
        
        renderer = WelcomeRenderer.from_config(config)
        result = renderer.render()
        
        panel_content = str(result.renderable)
        # Should contain default model
        assert "qwen-max-latest" in panel_content
        # Should contain default tool
        assert "file-search" in panel_content

    def test_from_config_with_no_tools_appconfig(self):
        """Test from_config with AppConfig that has no enabled tools."""
        # For this test, we need to manually create a config and modify it after creation
        # since AppConfig always ensures at least one tool is enabled
        config = AppConfig()
        # Directly set the attribute to empty list after creation
        config.enabled_tools = []
        
        renderer = WelcomeRenderer.from_config(config)
        result = renderer.render()
        
        panel_content = str(result.renderable)
        # Should not show tools section when empty
        assert "Tools:" not in panel_content
        # Should still show model
        assert "qwen-max-latest" in panel_content


class TestWelcomeRendererIntegration:
    """Integration tests for WelcomeRenderer."""
    
    def test_rendable_interface_compliance(self):
        """Test that WelcomeRenderer properly implements Rendable interface."""
        renderer = WelcomeRenderer()
        
        # Should have render method
        assert hasattr(renderer, 'render')
        assert callable(renderer.render)
        
        # render() should return a Rich renderable object
        result = renderer.render()
        assert hasattr(result, 'renderable') or hasattr(result, '__rich__')
    
    def test_legacy_function_compatibility(self):
        """Test that legacy render_welcome function still works."""
        from forge_cli.display.v3.renderers.rich.welcome import render_welcome
        from unittest.mock import Mock
        
        # Mock console and config
        console = Mock()
        config = Mock()
        config.model = "test-model"
        config.enabled_tools = ["test-tool"]
        
        # Should not raise an exception
        render_welcome(console, config)
        
        # Should have called console.print with a Panel
        assert console.print.called
        call_args = console.print.call_args[0]
        assert len(call_args) == 1
        assert isinstance(call_args[0], Panel) 