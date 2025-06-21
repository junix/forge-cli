#!/usr/bin/env python3
"""Demo script for WelcomeRenderer class."""

from unittest.mock import Mock

from rich.console import Console

from forge_cli.display.v3.renderers.rich.welcome import WelcomeRenderer


def main():
    """Run WelcomeRenderer demonstrations."""
    console = Console()
    
    print("=" * 60)
    print("🎨 WELCOME RENDERER ARCHITECTURE DEMO")
    print("=" * 60)
    print()
    
    # Demo 1: Basic welcome panel
    print("🎯 Basic Welcome Panel:")
    basic_renderer = WelcomeRenderer()
    basic_panel = basic_renderer.render()
    console.print(basic_panel)
    print()
    
    # Demo 2: Welcome with model information
    print("🤖 Welcome with Model Info:")
    model_renderer = (WelcomeRenderer()
                     .with_model("qwen-max-latest"))
    model_panel = model_renderer.render()
    console.print(model_panel)
    print()
    
    # Demo 3: Welcome with tools
    print("🔧 Welcome with Tools:")
    tools_renderer = (WelcomeRenderer()
                     .with_tools(["file-search", "web-search", "page-reader"]))
    tools_panel = tools_renderer.render()
    console.print(tools_panel)
    print()
    
    # Demo 4: Full configuration
    print("🚀 Full Configuration:")
    full_renderer = (WelcomeRenderer()
                    .with_model("deepseek-r1")
                    .with_tools(["file-search", "code-interpreter", "web-search"])
                    .with_title("Development Chat")
                    .with_version_info("(v3.1 Beta)"))
    full_panel = full_renderer.render()
    console.print(full_panel)
    print()
    
    # Demo 5: From config object
    print("⚙️ From Config Object:")
    config = Mock()
    config.model = "claude-3-sonnet"
    config.enabled_tools = ["file-search", "page-reader", "function-call"]
    
    config_renderer = WelcomeRenderer.from_config(config)
    config_panel = config_renderer.render()
    console.print(config_panel)
    print()
    
    print("=" * 60)
    print("✅ All WelcomeRenderer demonstrations completed!")
    print("✅ Architecture Benefits:")
    print("  - Returns Panel objects instead of direct printing")
    print("  - Follows Rendable interface pattern")
    print("  - Builder pattern for flexible configuration")
    print("  - Backward compatibility maintained")
    print("  - Easy to test and compose")
    print("=" * 60)


if __name__ == "__main__":
    main() 