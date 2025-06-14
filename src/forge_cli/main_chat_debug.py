"""Debug version to fix chat mode with typed API."""

import sys
import traceback

# Add debugging at the very start
print("DEBUG: Starting main_chat_debug.py", file=sys.stderr)

try:
    from forge_cli.main import *
    print("DEBUG: Successfully imported from main", file=sys.stderr)
except Exception as e:
    print(f"DEBUG: Error importing main: {e}", file=sys.stderr)
    traceback.print_exc()
    sys.exit(1)

# Override start_chat_mode with debugging
async def start_chat_mode_debug(config: SearchConfig, initial_question: str | None = None) -> None:
    """Start interactive chat mode with typed API - debug version."""
    print("DEBUG: Starting chat mode", file=sys.stderr)
    
    try:
        # Initialize typed processor registry
        initialize_typed_registry()
        print("DEBUG: Initialized typed registry", file=sys.stderr)

        # Create display
        display = create_display(config)
        print("DEBUG: Created display", file=sys.stderr)

        # Create chat controller
        controller = ChatController(config, display)
        print("DEBUG: Created chat controller", file=sys.stderr)
        
        # Check if controller has the methods we need
        print(f"DEBUG: Controller methods: {[m for m in dir(controller) if not m.startswith('_')]}", file=sys.stderr)
        print(f"DEBUG: Has send_message: {hasattr(controller, 'send_message')}", file=sys.stderr)
        print(f"DEBUG: Has process_message: {hasattr(controller, 'process_message')}", file=sys.stderr)
        
        # Store original send_message
        original_send_message = controller.send_message
        print("DEBUG: Stored original send_message", file=sys.stderr)
        
        async def typed_send_message(content: str) -> None:
            """Send message using typed API."""
            print(f"DEBUG: typed_send_message called with: {content[:50]}...", file=sys.stderr)
            
            # Add user message to conversation
            user_message = controller.conversation.add_user_message(content)
            
            # Mark display as in chat mode
            if hasattr(display, "console"):
                display._in_chat_mode = True
            
            # For now, just use the original method
            # We'll fix the typed API integration later
            await original_send_message(content)
        
        # Replace method
        controller.send_message = typed_send_message
        print("DEBUG: Replaced send_message method", file=sys.stderr)

        # Show welcome
        controller.show_welcome()
        print("DEBUG: Showed welcome", file=sys.stderr)

        # If initial question provided, process it first
        if initial_question:
            await controller.send_message(initial_question)

        # Start chat loop
        controller.running = True

        try:
            while controller.running:
                # Get user input
                user_input = await controller.get_user_input()

                if user_input is None:  # EOF or interrupt
                    break

                # Process the input
                continue_chat = await controller.process_input(user_input)

                if not continue_chat:
                    break

        except KeyboardInterrupt:
            display.show_status("\n\n👋 Chat interrupted. Goodbye!")

        except Exception as e:
            print(f"DEBUG: Chat loop error: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            display.show_error(f"Chat error: {str(e)}")

    except Exception as e:
        print(f"DEBUG: start_chat_mode error: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        raise


# Replace the original function
start_chat_mode = start_chat_mode_debug

if __name__ == "__main__":
    print("DEBUG: Running main_chat_debug as main", file=sys.stderr)
    run_main_async()