# ADR-014: TUI to Web Interface Migration Analysis

## Status
**Proposed** - Analysis and recommendations for migrating from Terminal User Interface to Web-based Interface

## Context

The current forge-cli application uses a sophisticated Terminal User Interface (TUI) built with Rich library, prompt-toolkit, and a modular renderer system. While the TUI provides excellent developer experience in terminal environments, there's a need to evaluate migration to a web-based interface to improve accessibility, multi-device support, and integration capabilities.

### Current TUI Architecture

The existing system consists of:

- **Rich Library**: Primary TUI framework providing live updates, panels, tables, and styled text
- **Prompt Toolkit**: Interactive input handling with auto-completion and history  
- **Modular Renderer System**: Three renderer types (Rich, Plaintext, JSON) with pluggable architecture
- **Real-time Streaming**: Live updates via Rich's `Live` component and async stream handling
- **Interactive Chat Commands**: 15+ commands for conversation management, tool configuration, and system control

### Key TUI Components Analysis

1. **Live Display System**: Uses Rich's `Live` component for real-time streaming updates
2. **Panel-based Layout**: Structured content presentation in bordered panels
3. **Tool Status Display**: Visual indicators for tool execution states with progress tracking
4. **Citation Management**: Structured display of sources and references
5. **Command System**: Sophisticated command parsing with auto-completion and aliases
6. **Conversation State**: Persistent conversation management with save/load capabilities

## Decision

### Recommended Frontend Framework: React with TypeScript

**Primary Justification:**
- **Real-time Requirements**: React's component lifecycle excels at handling streaming updates
- **Complex State Management**: Sophisticated conversation state, tool configurations, and streaming data
- **Component Modularity**: Current modular renderer architecture maps naturally to React components
- **TypeScript Integration**: Maintains existing strong typing philosophy (Pydantic models → TypeScript interfaces)
- **Ecosystem Maturity**: Rich ecosystem for terminal-like UI components and WebSocket handling

### Supporting Technology Stack

- **Vite**: Fast development and build tooling
- **TanStack Query**: Server state management and caching for API calls
- **WebSockets/Socket.IO**: Real-time streaming communication
- **React Markdown**: Markdown rendering (replacing Rich's markdown support)
- **Tailwind CSS**: Utility-first styling for rapid UI development
- **Framer Motion**: Smooth animations for live updates
- **React Hook Form**: Form handling for chat input and commands

## Proposed Architecture

### High-Level System Design

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React Web     │    │   FastAPI/       │    │   Knowledge     │
│   Frontend      │◄──►│   WebSocket      │◄──►│   Forge API     │
│                 │    │   Backend        │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Backend API Design

**WebSocket Endpoints:**
- `/ws/chat/{session_id}` - Main chat streaming
- `/ws/status/{session_id}` - Tool execution status updates

**REST Endpoints:**
- `GET /api/conversations` - List saved conversations
- `POST /api/conversations` - Save conversation  
- `GET /api/conversations/{id}` - Load conversation
- `POST /api/chat/command` - Execute chat commands
- `GET /api/config` - Get current configuration
- `PUT /api/config` - Update configuration

### Component Architecture Mapping

Current TUI renderers map to React components:

```typescript
<ChatInterface>
  <ConversationPanel>
    <MessageList>
      <MessageItem />
      <ToolExecutionStatus />
      <CitationDisplay />
    </MessageList>
  </ConversationPanel>
  <InputPanel>
    <ChatInput />
    <CommandSuggestions />
  </InputPanel>
  <SidePanel>
    <ToolsManager />
    <ConversationHistory />
    <ConfigPanel />
  </SidePanel>
</ChatInterface>
```

### Real-time Streaming Implementation

```typescript
const useStreamingResponse = (sessionId: string) => {
  const [response, setResponse] = useState<Response | null>(null);
  
  useEffect(() => {
    const ws = new WebSocket(`/ws/chat/${sessionId}`);
    
    ws.onmessage = (event) => {
      const { event_type, data } = JSON.parse(event.data);
      
      if (event_type === 'response.output_text.delta') {
        setResponse(prev => ({
          ...prev,
          output_text: prev?.output_text + data.text
        }));
      }
    };
    
    return () => ws.close();
  }, [sessionId]);
  
  return response;
};
```

## Required Architectural Changes

### Backend Modifications

1. **WebSocket Server**: Add WebSocket support for real-time streaming
2. **Session Management**: Web-based session handling (replacing terminal sessions)
3. **Authentication System**: User authentication and authorization
4. **File Upload Handling**: Support for document processing via web uploads
5. **CORS Configuration**: Cross-origin resource sharing for web clients

### Frontend Implementation

1. **State Management**: React Context + TanStack Query for server/client state
2. **Command System**: Web-based command execution with auto-completion
3. **Responsive Design**: Multi-device support (desktop, tablet, mobile)
4. **Accessibility**: WCAG compliance, keyboard navigation, screen reader support
5. **Progressive Web App**: Offline capabilities and app-like experience

## Benefits

### User Experience Improvements
- **Accessibility**: Better screen reader support, keyboard navigation
- **Multi-device Access**: Works on tablets, phones, different screen sizes
- **Conversation Sharing**: Easy sharing via URLs and social integration
- **Rich Media Support**: Better handling of images, files, interactive content
- **Collaboration**: Multiple users can view and interact with conversations

### Technical Advantages
- **Integration Flexibility**: Embed in other web applications
- **Deployment Simplicity**: Standard web deployment patterns
- **Monitoring**: Better analytics and user behavior tracking
- **Scalability**: Horizontal scaling with load balancers
- **Maintenance**: Familiar web development tooling and practices

## Implementation Strategy

### Phase 1: Core Chat Interface (4-6 weeks)
- Basic React application setup with TypeScript
- WebSocket integration for streaming responses
- Message display and input components
- Basic conversation state management

### Phase 2: Command System (3-4 weeks)  
- Chat command execution via API
- Auto-completion and command suggestions
- Tool management interface
- Configuration panels

### Phase 3: Conversation Management (2-3 weeks)
- Save/load conversation functionality
- Conversation history and search
- Export capabilities (markdown, JSON)

### Phase 4: Advanced Features (4-5 weeks)
- File upload and processing
- Advanced tool configurations
- User authentication and profiles
- Mobile optimization

### Phase 5: Production Readiness (2-3 weeks)
- Performance optimization
- Security hardening  
- Monitoring and analytics
- Documentation and deployment

## Risks and Mitigations

### Technical Risks
- **WebSocket Complexity**: Mitigate with robust error handling and reconnection logic
- **State Synchronization**: Use established patterns (Redux/Zustand) for complex state
- **Performance**: Implement virtualization for large conversation histories

### User Experience Risks  
- **Feature Parity**: Ensure all TUI features are available in web interface
- **Learning Curve**: Provide migration guides and feature tutorials
- **Browser Compatibility**: Support modern browsers with graceful degradation

## Alternatives Considered

### Alternative Frontend Frameworks
- **Svelte/SvelteKit**: Excellent performance but smaller ecosystem
- **Vue 3**: Good option but React's streaming patterns are more mature  
- **Next.js**: Adds unnecessary complexity for this single-page application use case

### Alternative Architectures
- **Server-Side Rendering**: Not suitable for real-time streaming requirements
- **Desktop Application (Electron)**: Doesn't address multi-device and sharing requirements
- **Hybrid Approach**: Maintaining both TUI and web would increase maintenance burden

## Conclusion

Migration to a React-based web interface provides significant benefits in accessibility, usability, and integration capabilities while maintaining the sophisticated real-time features of the current TUI system. The modular architecture of the existing system facilitates a clean migration path with clear component mapping and preserved functionality.

The recommended phased approach allows for incremental development and testing, ensuring feature parity and user experience quality throughout the migration process.
