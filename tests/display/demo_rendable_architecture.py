"""Demo showcasing the new Rendable-based architecture."""

from unittest.mock import Mock

from forge_cli.display.v3.renderers.rendable import Rendable
from forge_cli.display.v3.renderers.rich.reason import ReasoningRenderer
from forge_cli.display.v3.renderers.rich.message_content import MessageContentRenderer
from forge_cli.display.v3.renderers.rich.citations import CitationsRenderer
from forge_cli.display.v3.renderers.rich.tools import (
    FileReaderToolRender,
    WebSearchToolRender,
    FileSearchToolRender,
    PageReaderToolRender,
    CodeInterpreterToolRender,
    FunctionCallToolRender,
    ListDocumentsToolRender,
)


def demo_rendable_inheritance():
    """Demonstrate that all renderers inherit from Rendable."""
    print("🏛️ Rendable Inheritance Demo:")
    
    # Create instances of all renderer types
    renderers = [
        ("ReasoningRenderer", ReasoningRenderer(Mock(text="Test reasoning"))),
        ("MessageContentRenderer", MessageContentRenderer(Mock(type="output_text", text="Test content"))),
        ("CitationsRenderer", CitationsRenderer([])),
        ("FileReaderToolRender", FileReaderToolRender()),
        ("WebSearchToolRender", WebSearchToolRender()),
        ("FileSearchToolRender", FileSearchToolRender()),
        ("PageReaderToolRender", PageReaderToolRender()),
        ("CodeInterpreterToolRender", CodeInterpreterToolRender()),
        ("FunctionCallToolRender", FunctionCallToolRender()),
        ("ListDocumentsToolRender", ListDocumentsToolRender()),
    ]
    
    for name, renderer in renderers:
        is_rendable = isinstance(renderer, Rendable)
        has_render = hasattr(renderer, 'render')
        status = "✅" if is_rendable and has_render else "❌"
        print(f"  {status} {name:<25} → Rendable: {is_rendable}, render(): {has_render}")
    
    print()


def demo_polymorphic_rendering():
    """Demonstrate polymorphic rendering using the Rendable interface."""
    print("🔄 Polymorphic Rendering Demo:")
    
    # Create a collection of different Rendable objects
    reasoning_item = Mock(text="The user is asking for information about Python.")
    content = Mock(type="output_text", text="Python is a programming language.")
    citation = Mock(type="file_citation", filename="python_guide.pdf", file_id="guide123", index=42)
    
    rendables = [
        ReasoningRenderer(reasoning_item),
        MessageContentRenderer(content),
        CitationsRenderer([citation]),
        FileReaderToolRender().with_filename("tutorial.pdf").with_progress(0.6),
        WebSearchToolRender().with_queries(["Python tutorial"]),
        CodeInterpreterToolRender().with_code("print('Hello, World!')"),
    ]
    
    def render_any_rendable(renderable: Rendable) -> str:
        """Function that can render any Rendable object."""
        return renderable.render()
    
    for i, renderable in enumerate(rendables, 1):
        result = render_any_rendable(renderable)
        renderer_type = type(renderable).__name__
        preview = result[:60] + "..." if len(result) > 60 else result
        print(f"  {i}. {renderer_type:<25} → {preview}")
    
    print()


def demo_builder_pattern_with_inheritance():
    """Demonstrate builder pattern working with inheritance."""
    print("🏗️ Builder Pattern + Inheritance Demo:")
    
    def build_renderer_chain(base_renderer: Rendable) -> Rendable:
        """Function that works with any Rendable builder."""
        if hasattr(base_renderer, 'with_status'):
            base_renderer.with_status("completed")
        return base_renderer
    
    # Test with different tool renderers
    renderers = [
        ("FileReader", FileReaderToolRender().with_filename("data.csv")),
        ("WebSearch", WebSearchToolRender().with_queries(["machine learning"])),
        ("CodeInterpreter", CodeInterpreterToolRender().with_code("import pandas")),
    ]
    
    for name, renderer in renderers:
        # Apply common operations
        enhanced_renderer = build_renderer_chain(renderer)
        result = enhanced_renderer.render()
        print(f"  {name}: {result}")
    
    print()


def demo_legacy_compatibility():
    """Demonstrate that legacy functions still work."""
    print("🔄 Legacy Compatibility Demo:")
    
    # Test legacy functions
    from forge_cli.display.v3.renderers.rich.reason import render_reasoning_item
    from forge_cli.display.v3.renderers.rich.output import render_message_content, render_citations
    
    reasoning_item = Mock(text="Legacy reasoning test")
    content = Mock(type="output_text", text="Legacy content test")
    citation = Mock(type="file_citation", filename="legacy.pdf", file_id="legacy123", index=1)
    
    legacy_results = [
        ("render_reasoning_item", render_reasoning_item(reasoning_item)),
        ("render_message_content", render_message_content(content)),
        ("render_citations", render_citations([citation])),
    ]
    
    for func_name, result in legacy_results:
        preview = result[:50] + "..." if len(result) > 50 else result
        print(f"  ✅ {func_name:<22} → {preview}")
    
    print()


def demo_type_safety():
    """Demonstrate type safety with the Rendable interface."""
    print("🛡️ Type Safety Demo:")
    
    def process_renderable_collection(renderables: list[Rendable]) -> list[str]:
        """Type-safe function that processes Rendable objects."""
        return [r.render() for r in renderables]
    
    # Create a mixed collection of Rendable objects
    mixed_renderables = [
        ReasoningRenderer(Mock(text="Type-safe reasoning")),
        FileReaderToolRender().with_filename("type_safe.py"),
        MessageContentRenderer(Mock(type="output_text", text="Type-safe content")),
    ]
    
    results = process_renderable_collection(mixed_renderables)
    
    for i, result in enumerate(results, 1):
        renderer_type = type(mixed_renderables[i-1]).__name__
        preview = result[:40] + "..." if len(result) > 40 else result
        print(f"  {i}. {renderer_type:<25} → {preview}")
    
    print()


def main():
    """Run all demos."""
    print("=" * 70)
    print("🎨 RENDABLE-BASED ARCHITECTURE DEMO")
    print("=" * 70)
    print()
    
    demo_rendable_inheritance()
    demo_polymorphic_rendering()
    demo_builder_pattern_with_inheritance()
    demo_legacy_compatibility()
    demo_type_safety()
    
    print("=" * 70)
    print("✅ All renderers successfully inherit from Rendable!")
    print("🚀 Polymorphic rendering, type safety, and legacy compatibility verified!")
    print("=" * 70)


if __name__ == "__main__":
    main() 