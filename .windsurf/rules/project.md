---
trigger: always_on
description: About the codebase
globs:**/*.py
---

```text
knowledge_forge/
├── __init__.py  # Main package initializer for knowledge_forge.
├── _types/
│   ├── __init__.py  # Initializes and re-exports core data types for the Knowledge Forge application, including Pydantic models for entities like files, chunks, and traces.
│   ├── chunk_group.py  # Defines the `ChunkGroup` Pydantic model, representing a collection of `Chunk` or `Page` objects, with methods to get combined text and metadata.
│   ├── chunk.py  # Defines the `Chunk` Pydantic model, representing a segment of text from a document, with methods for merging, token estimation, and LangChain conversion.
│   ├── echo_callback.py  # Implements a simple `EchoCallback` class that logs received events, used for debugging or monitoring asynchronous callbacks.
│   ├── page.py  # Defines the `Page` Pydantic model, a specialized `Chunk` representing a document page, with URL and specific ID format validation.
│   ├── raw_file.py  # Defines the `RawFile` Pydantic model, representing a raw binary file with its content and MIME type, including an MD5 sum calculation property.
│   └── trace.py  # Defines the `Trace` Pydantic model, representing a background task or job with attributes like ID, status, progress, and associated data.
├── algo/
│   ├── __init__.py  # Initializes the `algo` sub-package for algorithms.
│   ├── stream_fix_align.py  # Implements `StreamFixAligner` for incremental fixed pattern alignment on text streams, with helper functions for synchronous and asynchronous stream processing.
│   └── stream_regex_align.py  # Implements `StreamRegexAligner` for incremental regular expression searching on text streams, with helper functions for synchronous and asynchronous processing.
├── api.py  # Main FastAPI application setup for the Knowledge Forge API, including CORS, request logging, route registration, and lifespan management for task recovery.
├── apis/
│   ├── __init__.py  # Initializes the `apis` sub-package for API endpoint definitions.
│   ├── api_file_search.py  # Defines API endpoints for file search functionality, allowing users to search document collections using vector stores with Pydantic models for requests and responses.
│   ├── api_files.py  # Defines API endpoints for file management (upload, download, retrieval, deletion), including background processing for parsing and storage, using Pydantic models for responses.
│   ├── api_response.py  # Defines API endpoints for generating and retrieving model responses, supporting different effort levels and streaming Server-Sent Events (SSE) for real-time updates.
│   ├── api_serverstatus.py  # Defines a simple API endpoint (`/serverstatus`) for checking the server's operational status, returning a success code and message.
│   ├── api_suggestions.py  # Defines API endpoints for generating search suggestions based on conversation history, using Pydantic models for request and response structures.
│   ├── api_task.py  # Defines an API endpoint for retrieving the status and details of a specific task by its ID.
│   └── api_vectorstore.py  # Defines API endpoints for managing vector stores, including creation, modification, deletion, search, and summarization, with Pydantic models for requests and responses.
├── callback.py  # Provides a generic asynchronous `Callback` base class and simple example implementations (`SimpleCallback`, `NumberCallback`) for handling data processing.
├── channel/
│   ├── __init__.py  # Initializes and exports asynchronous communication channel components, including base classes (`BaseChannel`, `DuplexChannelBase`) and implementations like `MemStream` and `DuplexEndpoint`.
│   ├── base_channel_demo.py  # Contains demonstration code for `BaseChannel`, `DuplexChannelBase`, and `DuplexEndpoint` implementations, showcasing their usage.
│   ├── base_channel.py  # Defines abstract base classes `BaseChannel` (for unidirectional asynchronous communication) and `DuplexChannelBase` (for bidirectional channels).
│   ├── memstream_demo.py  # Provides a demonstration of the `MemStream` class for bidirectional asynchronous communication between client and server workers.
│   ├── memstream.py  # Implements `MemStream`, a bidirectional memory stream for asynchronous communication, built upon `anyio`'s memory object streams.
│   ├── memstream2.py  # Implements `DuplexEndpoint` for one half of an in-memory bidirectional channel and a factory `create_duplex` to create paired endpoints, using `anyio` streams.
│   ├── queue_channel.py  # Implements `Channel`, a `BaseChannel` subclass using `asyncio.Queue` for FIFO asynchronous message passing.
│   ├── run_demo.py  # A runner script to execute the `memstream_demo.py` example, demonstrating `MemStream` functionality.
│   └── simple_producer_consumer.py  # Provides a factory function `create_simple_producer_and_consumer` that sets up a `MemStream`-based callback and processing loop for event handling.
├── chunking/
│   ├── __init__.py  # Initializes the `chunking` sub-package.
│   ├── group.py  # Provides functions (`group` using dynamic programming, `greedy_group` using a greedy algorithm) to divide a list of `Chunk` objects into a specified number of groups, aiming for even token distribution.
│   ├── langchain_chunker.py  # Implements text chunking using LangChain's `RecursiveCharacterTextSplitter`, providing functions to chunk single texts or lists of documents into `Chunk` objects.
│   └── rechunk.py  # Defines the `rechunk` function, which re-segments a list of `Chunk` objects by first splitting them into sentences and then merging sentences into new `ChunkGroup`s based on token limits and overlap.
├── citation/
│   ├── __init__.py  # Initializes the `citation` sub-package.
│   ├── citation_styling.py  # Provides a `symbol_of` function and dictionaries (e.g., `CIRCLED_DIGITS`, `SUPERSCRIPT_DIGITS`) for formatting numerical citations into various styled Unicode representations.
│   └── patch.py  # Defines `CitationPatcher` class to incrementally find and replace citation patterns (e.g., `[1]`) in text streams with styled Unicode numbers, supporting citation compression and various styles.
├── cli/
│   └── collection_search.py  # A command-line tool for searching vector store collections using `CollectionAsTool`, allowing users to query collections and get formatted answers.
├── code_interpreter/
│   ├── __init__.py  # Initializes the `code_interpreter` sub-package.
│   └── ipython.py  # Implements `IPythonExecutor` for running Python code snippets within an IPython interactive shell, and provides a schema for an OpenAI-compatible tool.
├── collection.py  # Defines the `Collection` Pydantic model representing a collection of embeddings, including attributes like ID, name, model, and metadata. Also provides a `create_collection` factory function.
├── common/
│   ├── __init__.py  # Initializes the `common` sub-package for shared utilities.
│   └── logger.py  # Configures application-wide logging using Loguru, including custom formatting for payloads and interception of standard Python logging.
├── compress/
│   ├── __init__.py  # Initializes the `compress` sub-package.
│   ├── base.py  # Defines a `Node` Pydantic model and an abstract base class `BaseCompressor` for content filtering and prioritization, including an RRF (Reciprocal Rank Fusion) implementation.
│   ├── compare_demo.py  # A demonstration script that compares `VectorCompressor` and `RerankerCompressor` by processing pages from a demo document and displaying ranked results.
│   ├── hierarchical_rag/
│   │   ├── __init__.py  # Initializes the `hierarchical_rag` sub-package.
│   │   ├── answer_generator.py  # Provides functions for generating answers from retrieved document paragraphs (`generate_answer`) and verifying their factual accuracy (`verify_answer`) using LLMs in a hierarchical RAG context.
│   │   ├── example.py  # An example script showcasing the usage of the `HierarchicalRagSystem` for answering questions from documents loaded via URL or local file, using Tencent parser and page-based navigation.
│   │   ├── loader.py  # Provides document loading (`loader`) and text extraction (`extract_text_from_document`) utilities for PDF files, using Tencent parser with OSS caching via a `SimpleOssContext`.
│   │   ├── main.py  # Defines the `HierarchicalRagSystem` class, which integrates document loading (URL, file, chunks), hierarchical navigation, and answer generation using LLMs for document QA.
│   │   └── navigator.py  # Implements hierarchical document navigation (`navigate_document_chunks`) using LLMs to select relevant `ChunkGroup`s layer by layer, based on alphabetical indexing and XML-like reasoning tags.
│   ├── reranker_based.py  # Implements `RerankerCompressor`, a `BaseCompressor` subclass that uses a provided `Ranker` (e.g., YxtRanker) to score and rerank text nodes based on query relevance.
│   └── vector_based.py  # Implements `VectorCompressor`, a `BaseCompressor` subclass that uses a FAISS-backed `FaissIndexStore` for adding and retrieving relevant text nodes via vector similarity search.
├── conf/
│   ├── __init__.py  # Initializes application configuration by loading settings from `dev.py` or `local.py` based on the `ENV` environment variable, and provides `set_env_if_not_exists` utility.
│   ├── dev.py  # Contains development-specific configurations for logging, AI/Parser APIs, database connections (PostgreSQL, MongoDB), message queues (RocketMQ, Kafka), and object storage (Baidu BOS).
│   └── local.py  # Contains local-specific configurations, similar to development, for logging, AI/Parser APIs, databases (potentially in-memory for SQLite), message queues, and object storage.
├── consoles.py  # Provides utility functions for console output using the Rich library, including `print_error`, `print_markdown`, and `print_code` for formatted and syntax-highlighted text.
├── context/
│   ├── __init__.py  # Initializes the context management module, exporting `Context` abstract base class and `create_context` factory for remote contexts.
│   ├── context.py  # Defines the `Context` abstract base class, outlining the interface for managing tasks, documents, collections, and responses, including interactions with OSS and vector stores.
│   ├── local_context.py  # Implements the `Context` interface using RocksDB (`KVStore`) for local persistence of tasks, documents, and collections, and interacts with a default OSS client.
│   └── remote_context.py  # Implements the `Context` interface using MongoDB (`MongoStore`) for remote persistence of tasks, documents, collections, and responses, interacting with OSS and a YXT vector store.
├── crawler/
│   ├── __init__.py  # Initializes the `crawler` sub-package.
│   ├── crawler_example.py  # An example script showcasing the usage of the `Crawler` class from `yxt_simple.py` for crawling single and multiple URLs.
│   └── yxt_simple.py  # Implements a `Crawler` class that uses the YXT parser service (v1) to crawl and parse web pages, returning `CrawlResult` objects. Also defines `YxtSimpleParser`.
├── demo/
│   ├── __init__.py  # Initializes the `demo` sub-package.
│   ├── demo_doc.py  # Provides functions to read a Markdown file (`en.md`), split it into pages, calculate MD5, and create a `Document` object with `Page` segments.
│   └── faiss_emb_demo.py  # A demonstration script for `FaissIndexStore`, showcasing collection creation, document addition, querying, filtering, and deletion using either YXT BGE-M3 or a HuggingFace embedding model.
├── doc_parser/
│   ├── __init__.py  # Initializes the `doc_parser` sub-package for document parsing utilities.
│   ├── conv.py  # Provides an asynchronous function `conv_word_to_pdf` to convert Word documents to PDF format using the `docx2pdf` library.
│   ├── parser.py  # Defines an abstract base class `Parser` for document parsers and a `ParseEvent` dataclass for reporting parsing progress and status.
│   ├── pdfs.py  # Provides utility functions for PDF manipulation, including counting pages, splitting PDFs, converting PDF pages to PIL Images, and batch uploading images to OSS.
│   ├── tencents.py  # Implements `TencentParser` for parsing documents using Tencent Cloud's LKE service, with support for caching results in OSS and updating page images.
│   ├── urls.py  # Provides utility functions for URL handling, specifically `contain_url` to check if a text string contains any URLs.
│   ├── yxt_v1.py  # Implements a client for the YXT V1 asynchronous document parsing API, including task submission, status polling, result fetching, and a `YxtParser` class that uses this client.
│   └── yxt_v2.py  # Implements a client for the YXT V2 asynchronous document parsing API (`aigrid-weave-gateway`), including content configuration based on file type, and a `YxtParserV2` class.
├── doc.py  # Defines core Pydantic models `DocumentContent` (for parsed content like summary, tags, segments) and `Document` (representing a file with metadata, content, and user-specific info).
├── embed/
│   ├── __init__.py  # Initializes the `embed` sub-package for text embedding models.
│   ├── base.py  # Defines an abstract base class `Embedding` for text embedding models, with methods for embedding texts/queries and converting to a LangChain-compatible interface.
│   ├── huggingface.py  # Implements the `Embedding` interface using `sentence-transformers` from Hugging Face for generating text embeddings.
│   ├── langchain_embeding.py  # Provides an adapter class `LangChainEmbedding` to wrap LangChain's `Embeddings` objects, making them compatible with the local `Embedding` interface.
│   └── yxt.py  # Implements the `Embedding` interface using the YXT embedding service API for models like 'bge-m3' and 'ada'.
├── event.py  # Defines `EventType` (an enumeration of various response-related events) and the `Event` Pydantic model for encapsulating event type and data, primarily for SSE.
├── fs/
│   ├── __init__.py  # Initializes the `fs` (file system) sub-package.
│   ├── base.py  # Defines a `StorageType` enum (URL, PATH, OSS, MEMORY) and a `BaseFile` Pydantic model as a foundation for file representations across different storage types.
│   ├── common.py  # Provides common file system utilities, including MIME type detection (sync/async), text file detection, byte-to-text conversion, suffix-to-MIME mapping, and MD5 hashing.
│   ├── excels.py  # Defines an `ExcelFile` class (subclassing `File`) for parsing Excel files, converting sheets to Markdown text and images using pandas and dataframe_image.
│   ├── file.py  # Implements a `File` class for handling files from various sources (local path, binary, base64, OSS, URL, data URI) with methods for conversion between formats and asynchronous operations.
│   ├── htmls/
│   │   ├── __init__.py  # Initializes the `htmls` sub-package under `fs`.
│   │   └── conv.py  # Provides an `html2md` async function to convert HTML content to Markdown using a bundled `html-to-markdown.osx.arm64` binary via subprocess.
│   ├── image.py  # Defines an `Image` dataclass for managing image data from various sources (path, PIL, base64, data URI, URL, OSS) with conversion and OpenAI message formatting methods. (Likely an older or alternative version to `fs.images.Image`)
│   ├── images.py  # Defines an `Image` Pydantic model for representing and manipulating image data from various sources (path, PIL, base64, data URI, URL), including methods for OSS interaction and conversion to OpenAI/Anthropic chat message formats.
│   ├── mime_types.py  # Provides functions to detect MIME types from binary data (`detect_mime_type_from_binary`) by inspecting file signatures and from file paths (`detect_mime_type_from_path`) using various strategies.
│   ├── pdf.py  # Defines a `PDF` class for handling PDF files, offering methods for MD5 calculation, page conversion to images (using PyMuPDF), image upload to OSS, PDF splitting, and merging.
│   ├── pdf2doc.py  # Provides `to_document_pages` async function to convert PDF pages into a list of `Page` objects, including uploading page images to OSS.
│   └── words.py  # Defines a `WordFile` class (subclassing `File`) for parsing Word documents, converting content to Markdown (using python-docx) and images (via PDF conversion).
├── jllms/
│   ├── __init__.py  # Initializes the `jllms` (presumably "just LLMs" or similar) sub-package.
│   ├── chunk_combiner.py  # Provides functions (`combine_chunk`, `combine_choice`, `combine_delta`, etc.) for incrementally merging chunks of streaming LLM responses, handling content, and tool calls.
│   ├── common.py  # Defines utility functions: `content_of` for extracting content from various LLM response types and `combine_toolcall` for merging tool call deltas.
│   ├── deepseek_llm.py  # Implements the `DeepseekLLM` class, a subclass of `LLM`, tailored for Deepseek models, providing context length, token counting, and capability checks.
│   ├── doubao_llm.py  # Implements the `DoubaoLLM` class, a subclass of `LLM`, for Doubao models, defining context lengths, token counting (approximate), and capability checks.
│   ├── factory_demo.py  # A demonstration script for `LLMFactory`, showcasing how to create instances of different LLMs (Qwen, Deepseek, Doubao) and check their capabilities.
│   ├── llm_demo.py  # A demonstration script to test Qwen, Deepseek, and Doubao LLM implementations, checking their async chat functionality, token counting, and model capabilities.
│   ├── llm_factory.py  # Defines `LLMFactory` for creating instances of different LLM types (Qwen, Deepseek, Doubao) by inferring type from model name or using explicit type, and managing API keys/base URLs from environment variables.
│   ├── llm.py  # Defines an abstract base class `LLM` for language model interactions, including methods for chat completion (`achat`), token counting, capability checks, and usage tracking.
│   ├── qwen_demo.py  # A demonstration script specifically for `QwenLLM`, testing its async chat, token counting, model capabilities, and the `bind` method for enabling search and thinking modes.
│   └── qwen_llm.py  # Implements the `QwenLLM` class, a subclass of `LLM`, tailored for Alibaba Qwen models, providing specific context lengths, token counting, multi-modal/tool-call support checks, and handling for search/thinking modes.
├── mcps/
│   ├── __init__.py  # Initializes the `mcps` (MCP Server/Client Protocol) sub-package.
│   ├── mcp_demo.py  # A demonstration script for the MCP (Model-Controller-Peripheral) framework, showing how to build and run MCP servers from a JSON configuration and interact with their tools via an LLM.
│   └── mcp.py  # Implements the MCP (Model-Controller-Peripheral) server and client interaction logic, including `MCPServer` (Stdio/HTTP variants), `ToolDefinition`, and utilities to build servers from config and wrap them as tools for LLMs.
├── memory/
│   └── __init__.py  # Initializes the `memory` sub-package.
├── not_given.py  # Defines the `NotGiven` sentinel class and `NOT_GIVEN` singleton instance, used to distinguish omitted keyword arguments from those explicitly passed as `None`.
├── oss/
│   ├── __init__.py  # Initializes the OSS (Object Storage Service) client package, primarily exporting Baidu BOS client components and a pre-configured `NOTEBOOK` instance for the 'ainotebook' bucket.
│   ├── aliyun/
│   │   ├── __init__.py  # Initializes the `aliyun` sub-package for Aliyun OSS.
│   │   └── bucket.py  # A command-line tool for managing Aliyun OSS buckets, providing functionalities like creating buckets and displaying bucket information using Rich for formatted output.
│   ├── aliyuns.py  # Implements `AliyunOSSClient`, an `OSSClient` subclass for interacting with Alibaba Cloud Object Storage Service (OSS), providing methods for upload, download, existence check, URL signing, and metadata operations.
│   ├── baidus.py  # Provides functions and the `BaiduBOSClient` class (an `OSSClient` subclass) for interacting with Baidu Object Storage (BOS), including operations like upload, download, URL generation, and existence checks.
│   └── base.py  # Defines an abstract base class `OSSClient` outlining the interface for Object Storage Service clients (upload, download, exists, sign_url) and a `Config` Pydantic model for OSS client configuration.
├── prompts/
│   ├── __init__.py  # Initializes the `prompts` sub-package.
│   └── router.py  # Defines a system prompt (`SYSTEM_PROMPT`) for an LLM assistant, instructing it on how to use available tools like `SemanticSearch` and `python_code_interpreter`, including when and how to call them.
├── proxy.py  # Implements a FastAPI application that acts as a proxy, forwarding requests to a target server, with a middleware to exclude certain paths like `/serverstatus`.
├── qa/
│   ├── __init__.py  # Initializes the `qa` (Question Answering) sub-package.
│   ├── base.py  # Defines a `Node` Pydantic model for text chunks and an abstract base class `BaseChunkQA` for question answering over a list of these nodes, including methods for packing responses with citations.
│   ├── deepseek_r1.py  # Implements `DeepseekR1Qa`, a `BaseChunkQA` subclass using the DeepSeek R1 model, featuring specialized prompting (`pack_r1_prompt`) and citation handling for generating answers from document nodes.
│   ├── prompts.py  # Provides functions to format prompts for question-answering tasks: `pack_prompt` for general LLMs and `pack_r1_prompt` specifically for DeepSeek R1, incorporating document nodes as context.
│   ├── qwen.py  # Implements `QwenQa`, a `BaseChunkQA` subclass for Qwen models, using R1-style prompting and citation handling for question answering over document nodes.
│   └── single_file/
│       ├── __init__.py  # Initializes the `single_file` sub-package under `qa`.
│       └── multimodal.py  # Defines `pack_pages_as_multimodal_messages` to convert `Document` pages (text and image URLs) into a list of OpenAI-compatible multimodal chat messages.
├── repo/
│   ├── __init__.py  # Initializes the `repo` sub-package, which manages document storage and retrieval using various backends like SQLite, RocksDB, and local file systems.
│   ├── idutils.py  # Provides a utility function `get_id` to extract an identifier from a dictionary, trying keys 'id', '_id', and '_key' in order.
│   ├── mongos.py  # Implements `MongoClient` for managing MongoDB connections and `MongoStore` (a `Store` subclass) for CRUD operations on MongoDB collections.
│   ├── ossstore.py  # Implements `OSSStore`, a `Store` subclass using Baidu BOS (`BaiduBOSClient`) as a key-value backend, storing data as JSON strings.
│   ├── rediss.py  # Implements `RedisStore`, a `Store` subclass using Redis (`aioredis`) as a key-value backend, storing data as JSON strings with a configurable prefix.
│   ├── rocksdb.py  # Implements `KVStore`, a `Store` subclass using RocksDB (`rocksdict`) for persistent key-value storage, serializing data as JSON.
│   └── store.py  # Defines an abstract base class `Store` outlining a simple key-value store interface with methods for store, update, fetch, and get_stats.
├── reranker/
│   ├── __init__.py  # Initializes the `reranker` sub-package.
│   ├── base.py  # Defines an abstract base class `Ranker` for text reranking implementations, with methods for reranking a source text against targets or a list of text pairs.
│   ├── bge_m3_v2.py  # Implements `BGEM3V2Ranker`, a `Ranker` subclass using the `BAAI/bge-reranker-v2-m3` model from Hugging Face Transformers for text similarity scoring.
│   ├── rrf.py  # Implements the Reciprocal Rank Fusion (RRF) algorithm for combining multiple ranking lists into a single, more robust ranking.
│   └── yxt.py  # Implements `YxtRanker`, a `Ranker` subclass that uses the YXT reranking API service (e.g., with bge-m3 model) to compute similarity scores for text pairs.
├── response/
│   ├── _types/
│   │   ├── __init__.py  # Initializes and re-exports numerous Pydantic models representing different parts of API requests and responses, including input/output messages, tool calls, and event types for streaming.
│   │   ├── _models.py  # Provides custom Pydantic `BaseModel` and `GenericModel` subclasses with enhanced serialization (`to_dict`, `to_json`), construction logic (`construct`), and type validation utilities for building response objects.
│   │   ├── computer_tool_param.py  # Defines `ComputerToolParam`, a TypedDict specifying parameters for the "computer_use_preview" tool, including display dimensions and environment type.
│   │   ├── computer_tool.py  # Defines the `ComputerTool` Pydantic model, representing the "computer_use_preview" tool with attributes for display dimensions and environment type.
│   │   ├── easy_input_message_param.py  # Defines `EasyInputMessageParam`, a TypedDict for a simplified input message structure with 'content' (string or list of content parts) and 'role'.
│   │   ├── easy_input_message.py  # Defines the `EasyInputMessage` Pydantic model, representing a simplified message input with 'content' (string or list of content parts) and 'role'.
│   │   ├── file_search_tool_param.py  # Defines `FileSearchToolParam`, a TypedDict for the "file_search" tool, including parameters like `vector_store_ids`, `filters`, `max_num_results`, and `ranking_options`.
│   │   ├── file_search_tool.py  # Defines the `FileSearchTool` Pydantic model, representing the "file_search" tool with attributes for `vector_store_ids`, `filters`, `max_num_results`, and `ranking_options`.
│   │   ├── function_definition.py  # Defines the `FunctionDefinition` Pydantic model, specifying the structure for defining a function (name, description, parameters) that an LLM can call.
│   │   ├── function_parameters.py  # Defines the `FunctionParameters` Pydantic model, representing the JSON schema for parameters of a function callable by an LLM.
│   │   ├── function_tool_param.py  # Defines `FunctionToolParam`, a TypedDict for a custom "function" tool, specifying its name, parameters (JSON schema), strictness, and description.
│   │   ├── function_tool.py  # Defines the `FunctionTool` Pydantic model, representing a custom "function" tool with attributes for its name, parameters (JSON schema), strictness, and description.
│   │   ├── input_image_content.py  # Defines the `InputImageContent` Pydantic model, representing image input to a model, with 'type' as "input_image" and an 'image_url' (URL or base64 data).
│   │   ├── input_item_list_params.py  # Defines `InputItemListParams`, a TypedDict for parameters used when listing input items, including pagination controls (`after`, `before`, `limit`), ordering, and inclusion of additional fields.
│   │   ├── input_message.py  # Defines the `InputMessage` Pydantic model, representing a message input to a model, with 'role', 'content' (string or list of text/image parts), and optional 'name'.
│   │   ├── input_text_content.py  # Defines the `InputTextContent` Pydantic model, representing text input to a model, with 'type' as "input_text" and the 'text' content.
│   │   ├── parsed_response.py  # Defines generic Pydantic models like `ParsedResponseOutputText` and `ParsedResponse` that extend base response types to include a `parsed` field for structured data extracted from LLM outputs.
│   │   ├── reasoning.py  # Defines the `Reasoning` Pydantic model, used to configure reasoning effort (`low`, `medium`, `high`) and summary generation (`auto`, `concise`, `detailed`) for o-series models.
│   │   ├── request.py  # Defines the `Request` Pydantic model for generating API responses, encapsulating model ID, input messages/text, tools, and various generation parameters (temperature, tool_choice, etc.).
│   │   ├── response_audio_delta_event.py  # Defines the `ResponseAudioDeltaEvent` Pydantic model, representing a chunk of base64 encoded audio bytes during a streaming audio response.
│   │   ├── response_audio_done_event.py  # Defines the `ResponseAudioDoneEvent` Pydantic model, signaling the completion of a streaming audio response.
│   │   ├── response_audio_transcript_delta_event.py  # Defines the `ResponseAudioTranscriptDeltaEvent` Pydantic model, representing a partial transcript chunk during a streaming audio transcription.
│   │   ├── response_audio_transcript_done_event.py  # Defines the `ResponseAudioTranscriptDoneEvent` Pydantic model, signaling the completion of a streaming audio transcription.
│   │   ├── response_code_interpreter_call_code_delta_event.py  # Defines the `ResponseCodeInterpreterCallCodeDeltaEvent` Pydantic model, representing a partial code snippet added by the code interpreter during streaming.
│   │   ├── response_code_interpreter_call_code_done_event.py  # Defines the `ResponseCodeInterpreterCallCodeDoneEvent` Pydantic model, signaling the completion of a code snippet output by the code interpreter.
│   │   ├── response_code_interpreter_call_completed_event.py  # Defines the `ResponseCodeInterpreterCallCompletedEvent` Pydantic model, signaling the completion of a code interpreter tool call, including the final `ResponseCodeInterpreterToolCall` object.
│   │   ├── response_code_interpreter_call_in_progress_event.py  # Defines the `ResponseCodeInterpreterCallInProgressEvent` Pydantic model, signaling that a code interpreter tool call has started and is in progress.
│   │   ├── response_code_interpreter_call_interpreting_event.py  # Defines the `ResponseCodeInterpreterCallInterpretingEvent` Pydantic model, signaling that the code interpreter is actively interpreting code for a tool call.
│   │   ├── response_code_interpreter_tool_call.py  # Defines the `ResponseCodeInterpreterToolCall` Pydantic model, representing a tool call to run code, including the code itself, its status, and results (logs or files).
│   │   ├── response_completed_event.py  # Defines the `ResponseCompletedEvent` Pydantic model, signaling that the entire response generation process has completed, including the final `Response` object.
│   │   ├── response_computer_tool_call_output_item.py  # Defines `ResponseComputerToolCallOutputItem`, representing the output of a computer tool call, typically a screenshot, along with safety check acknowledgments.
│   │   ├── response_computer_tool_call_output_screenshot_param.py  # Defines `ResponseComputerToolCallOutputScreenshotParam`, a TypedDict for specifying a computer screenshot output, including file ID or image URL.
│   │   ├── response_computer_tool_call_output_screenshot.py  # Defines the `ResponseComputerToolCallOutputScreenshot` Pydantic model, representing a computer screenshot output with a file ID or image URL.
│   │   ├── response_computer_tool_call_param.py  # Defines `ResponseComputerToolCallParam` TypedDict and various action TypedDicts (Click, Drag, Keypress, etc.) for specifying computer interaction tool calls.
│   │   ├── response_computer_tool_call.py  # Defines the `ResponseComputerToolCall` Pydantic model and various action models (Click, Drag, Keypress, etc.) representing a computer interaction tool call, including its status and pending safety checks.
│   │   ├── response_content_part_added_event.py  # Defines the `ResponseContentPartAddedEvent` Pydantic model, signaling that a new content part (e.g., text or refusal) has been added to an output item in the response.
│   │   ├── response_content_part_done_event.py  # Defines the `ResponseContentPartDoneEvent` Pydantic model, signaling that a content part (e.g., text or refusal) in an output item has completed generation.
│   │   ├── response_create_params.py  # Defines TypedDicts for response creation parameters, separating base, non-streaming, and streaming configurations, including input, model, tools, and various generation settings.
│   │   ├── response_created_event.py  # Defines the `ResponseCreatedEvent` Pydantic model, signaling that a new response object has been created, including the initial `Response` object itself.
│   │   ├── response_error_event.py  # Defines the `ResponseErrorEvent` Pydantic model, representing an error event during response generation, including an error code, message, and parameter.
│   │   ├── response_error.py  # Defines the `ResponseError` Pydantic model, encapsulating error details (code and message) that can occur during response generation.
│   │   ├── response_failed_event.py  # Defines the `ResponseFailedEvent` Pydantic model, signaling that the response generation process has failed, including the final (failed) `Response` object.
│   │   ├── response_file_search_call_completed_event.py  # Defines the `ResponseFileSearchCallCompletedEvent` Pydantic model, signaling that a file search tool call has completed.
│   │   ├── response_file_search_call_in_progress_event.py  # Defines the `ResponseFileSearchCallInProgressEvent` Pydantic model, signaling that a file search tool call has started and is in progress.
│   │   ├── response_file_search_call_searching_event.py  # Defines the `ResponseFileSearchCallSearchingEvent` Pydantic model, signaling that a file search tool call is actively searching for results.
│   │   ├── response_file_search_tool_call_param.py  # Defines `ResponseFileSearchToolCallParam`, a TypedDict representing a file search tool call, including its ID, queries, status, and results (list of file attributes).
│   │   ├── response_file_search_tool_call.py  # Defines the `ResponseFileSearchToolCall` Pydantic model, representing a file search tool call, including its ID, queries, status, and results. Provides methods to convert from/to OpenAI's `ChatCompletionMessageToolCall`.
│   │   ├── response_format_text_config_param.py  # Defines `ResponseFormatTextConfigParam`, a TypeAlias for configuring text response formats, allowing `ResponseFormatText`, `ResponseFormatTextJSONSchemaConfigParam`, or `ResponseFormatJSONObject`.
│   │   ├── response_format_text_config.py  # Defines `ResponseFormatTextConfig`, a TypeAlias for specifying text response formats, including plain text, JSON schema, or JSON object, using a discriminated union.
│   │   ├── response_format_text_json_schema_config_param.py  # Defines `ResponseFormatTextJSONSchemaConfigParam`, a TypedDict for configuring a JSON schema-based response format, including schema name, JSON schema itself, description, and strictness.
│   │   ├── response_format_text_json_schema_config.py  # Defines the `ResponseFormatTextJSONSchemaConfig` Pydantic model, specifying a JSON schema-based response format with schema name, the JSON schema object, description, and strictness option.
│   │   ├── response_format.py  # Defines the `ResponseFormat` Pydantic model, used to specify the desired format type of the model's response (e.g., "json_object").
│   │   ├── response_function_call_arguments_delta_event.py  # Defines the `ResponseFunctionCallArgumentsDeltaEvent` Pydantic model, representing a partial chunk of function call arguments during streaming.
│   │   ├── response_function_call_arguments_done_event.py  # Defines the `ResponseFunctionCallArgumentsDoneEvent` Pydantic model, signaling the completion of function call arguments, including the final arguments string.
│   │   ├── response_function_file_reader.py  # Defines the `ResponseFunctionFileReader` Pydantic model, representing a file reader tool call with document IDs, a query, and status. Stores results privately.
│   │   ├── response_function_tool_call_item.py  # Defines `ResponseFunctionToolCallItem`, a Pydantic model inheriting from `ResponseFunctionToolCall` but making the `id` field mandatory.
│   │   ├── response_function_tool_call_output_item.py  # Defines `ResponseFunctionToolCallOutputItem`, representing the output of a function tool call, including the call ID and the JSON string output.
│   │   ├── response_function_tool_call_param.py  # Defines `ResponseFunctionToolCallParam`, a TypedDict representing a function tool call, including arguments (JSON string), call ID, function name, and status.
│   │   ├── response_function_tool_call.py  # Defines the `ResponseFunctionToolCall` Pydantic model, representing a function tool call with arguments, call ID, function name, and status. Provides methods to convert to/from OpenAI's `ChatCompletionMessageToolCall`.
│   │   ├── response_function_web_search_param.py  # Defines `ResponseFunctionWebSearchParam`, a TypedDict representing a web search tool call, including its ID and status.
│   │   ├── response_function_web_search.py  # Defines the `ResponseFunctionWebSearch` Pydantic model, representing a web search tool call with ID, status, query, and privately stored results. Includes methods for conversion to/from general function tool calls and OpenAI's `ChatCompletionMessageToolCall`.
│   │   ├── response_in_progress_event.py  # Defines the `ResponseInProgressEvent` Pydantic model, signaling that a response generation process is currently in progress, including the `Response` object at that stage.
│   │   ├── response_includable.py  # Defines `ResponseIncludable`, a TypeAlias for specifying which additional data fields (like file search results or image URLs) should be included in the API response.
│   │   ├── response_incomplete_event.py  # Defines the `ResponseIncompleteEvent` Pydantic model, signaling that a response generation process has ended incompletely, including the `Response` object at that stage.
│   │   ├── response_input_content_param.py  # Defines `ResponseInputContentParam`, a TypeAlias representing different types of input content parameters: text, image, or file.
│   │   ├── response_input_content.py  # Defines `ResponseInputContent`, a TypeAlias representing different Pydantic models for input content: text, image, or file, using a discriminated union.
│   │   ├── response_input_file_param.py  # Defines `ResponseInputFileParam`, a TypedDict for specifying file input, including file data, file ID, and filename.
│   │   ├── response_input_file.py  # Defines the `ResponseInputFile` Pydantic model, representing file input to a model, with attributes for file data, file ID, and filename.
│   │   ├── response_input_image_param.py  # Defines `ResponseInputImageParam`, a TypedDict for specifying image input, including detail level, file ID, or image URL.
│   │   ├── response_input_image.py  # Defines the `ResponseInputImage` Pydantic model, representing image input to a model, with attributes for detail level, file ID, or image URL.
│   │   ├── response_input_item_param.py  # Defines `ResponseInputItemParam`, a TypeAlias representing various types of input items for a response, including messages, tool calls, tool call outputs, and item references.
│   │   ├── response_input_message_content_list_param.py  # Defines `ResponseInputMessageContentListParam`, a TypeAlias representing a list of `ResponseInputContentParam` objects, used for multimodal message content.
│   │   ├── response_input_message_content_list.py  # Defines `ResponseInputMessageContentList`, a TypeAlias representing a list of `ResponseInputContent` Pydantic models, used for multimodal message content.
│   │   ├── response_input_message_item.py  # Defines the `ResponseInputMessageItem` Pydantic model, representing an input message with an ID, content (list of content parts), role, and status.
│   │   ├── response_input_param.py  # Defines `ResponseInputParam`, a TypeAlias representing a list of `ResponseInputItemParam` objects, forming the complete input to the response generation process.
│   │   ├── response_input_text_param.py  # Defines `ResponseInputTextParam`, a TypedDict for specifying text input, including the text content itself.
│   │   ├── response_input_text.py  # Defines the `ResponseInputText` Pydantic model, representing text input to a model, with 'type' as "input_text" and the 'text' content.
│   │   ├── response_item_list.py  # Defines the `ResponseItemList` Pydantic model, representing a paginated list of `ResponseItem` objects, including pagination metadata like `first_id`, `last_id`, and `has_more`.
│   │   ├── response_item.py  # Defines `ResponseItem`, a TypeAlias representing various types of items that can appear in a response, including input/output messages and different tool calls/outputs, using a discriminated union.
│   │   ├── response_output_item_added_event.py  # Defines the `ResponseOutputItemAddedEvent` Pydantic model, signaling that a new output item (e.g., message, tool call) has been added to the response.
│   │   ├── response_output_item_done_event.py  # Defines the `ResponseOutputItemDoneEvent` Pydantic model, signaling that an output item (e.g., message, tool call) has completed generation.
│   │   ├── response_output_item.py  # Defines `ResponseOutputItem`, a TypeAlias representing various types of output items from a response, including messages, tool calls, and reasoning items, using a discriminated union.
│   │   ├── response_output_message_param.py  # Defines `ResponseOutputMessageParam`, a TypedDict representing an output message from the assistant, including its ID, content (text or refusal), role, and status.
│   │   ├── response_output_message.py  # Defines the `ResponseOutputMessage` Pydantic model, representing an output message from the assistant, containing content (text or refusal), role, ID, and status.
│   │   ├── response_output_refusal_param.py  # Defines `ResponseOutputRefusalParam`, a TypedDict representing a refusal output from the model, including the refusal message.
│   │   ├── response_output_refusal.py  # Defines the `ResponseOutputRefusal` Pydantic model, representing a refusal output from the model, containing the refusal message.
│   │   ├── response_output_text_param.py  # Defines `ResponseOutputTextParam`, a TypedDict representing text output from the model, including the text and a list of annotations (file citations, URL citations, file paths).
│   │   ├── response_output_text.py  # Defines the `ResponseOutputText` Pydantic model, representing text output from the model, including the text itself and a list of annotations (file citations, URL citations, file paths).
│   │   ├── response_reasoning_item_param.py  # Defines `ResponseReasoningItemParam`, a TypedDict representing a reasoning item in the response, including its ID, summary (text parts), and status.
│   │   ├── response_reasoning_item.py  # Defines the `ResponseReasoningItem` Pydantic model, representing a reasoning step or summary in the response, including its ID, summary text parts, status, and optional encrypted content.
│   │   ├── response_reasoning_summary_part_added_event.py  # Defines the `ResponseReasoningSummaryPartAddedEvent` Pydantic model, signaling that a new part has been added to a reasoning summary in the response.
│   │   ├── response_reasoning_summary_part_done_event.py  # Defines the `ResponseReasoningSummaryPartDoneEvent` Pydantic model, signaling that a reasoning summary part has completed generation.
│   │   ├── response_reasoning_summary_text_delta_event.py  # Defines the `ResponseReasoningSummaryTextDeltaEvent` Pydantic model, representing a partial chunk of text added to a reasoning summary during streaming.
│   │   ├── response_reasoning_summary_text_done_event.py  # Defines the `ResponseReasoningSummaryTextDoneEvent` Pydantic model, signaling the completion of text generation for a reasoning summary part, including the full text.
│   │   ├── response_refusal_delta_event.py  # Defines the `ResponseRefusalDeltaEvent` Pydantic model, representing a partial chunk of refusal text added to a content part during streaming.
│   │   ├── response_refusal_done_event.py  # Defines the `ResponseRefusalDoneEvent` Pydantic model, signaling the completion of refusal text generation for a content part, including the full refusal message.
│   │   ├── response_retrieve_params.py  # Defines `ResponseRetrieveParams`, a TypedDict for parameters used when retrieving a response, specifically for including additional data fields.
│   │   ├── response_status.py  # Defines `ResponseStatus`, a TypeAlias for the possible status values of a response: "completed", "failed", "in_progress", or "incomplete".
│   │   ├── response_stream_event.py  # Defines `ResponseStreamEvent`, a TypeAlias representing various types of events that can occur during a streaming response, using a discriminated union of specific event Pydantic models.
│   │   ├── response_text_annotation_delta_event.py  # Defines the `ResponseTextAnnotationDeltaEvent` Pydantic model, signaling that a new annotation (e.g., file citation, URL citation) has been added to an output text content part during streaming.
│   │   ├── response_text_config_param.py  # Defines `ResponseTextConfigParam`, a TypedDict for configuring text response behavior, specifically the `format` (e.g., plain text, JSON schema, JSON object).
│   │   ├── response_text_config.py  # Defines the `ResponseTextConfig` Pydantic model, used to specify the desired format for text output from the model (e.g., plain text, JSON schema, JSON object).
│   │   ├── response_text_delta_event.py  # Defines the `ResponseTextDeltaEvent` Pydantic model, representing a partial chunk of text added to an output text content part during streaming.
│   │   ├── response_text_done_event.py  # Defines the `ResponseTextDoneEvent` Pydantic model, signaling the completion of text generation for an output text content part, including the full text.
│   │   ├── response_usage.py  # Defines Pydantic models for tracking token usage: `InputTokensDetails`, `OutputTokensDetails`, and `ResponseUsage`. `ResponseUsage` supports addition operations to combine usage statistics.
│   │   ├── response_web_search_call_completed_event.py  # Defines the `ResponseWebSearchCallCompletedEvent` Pydantic model, signaling that a web search tool call has completed.
│   │   ├── response_web_search_call_in_progress_event.py  # Defines the `ResponseWebSearchCallInProgressEvent` Pydantic model, signaling that a web search tool call has started and is in progress.
│   │   ├── response_web_search_call_searching_event.py  # Defines the `ResponseWebSearchCallSearchingEvent` Pydantic model, signaling that a web search tool call is actively searching for results.
│   │   ├── response.py  # Defines the main `Response` Pydantic model, encapsulating all aspects of an API response, including ID, creation timestamp, status, model used, output items (messages, tool calls), usage statistics, and various configuration parameters.
│   │   ├── text_format_type.py  # Defines the `TextFormatType` Pydantic model, used to specify the format type for text output, typically "text".
│   │   ├── tool_choice_function_param.py  # Defines `ToolChoiceFunctionParam`, a TypedDict for specifying that a particular function (by name) should be called by the model.
│   │   ├── tool_choice_function.py  # Defines the `ToolChoiceFunction` Pydantic model, used to instruct the model to call a specific function by name.
│   │   ├── tool_choice_options.py  # Defines `ToolChoiceOptions`, a TypeAlias for the literal string values controlling tool usage: "none", "auto", or "required".
│   │   ├── tool_choice_types_param.py  # Defines `ToolChoiceTypesParam`, a TypedDict for specifying that a particular type of built-in tool (e.g., "file_search", "web_search_preview") should be used by the model.
│   │   ├── tool_choice_types.py  # Defines the `ToolChoiceTypes` Pydantic model, used to instruct the model to use a specific type of built-in tool (e.g., "file_search", "web_search_preview").
│   │   ├── tool_param.py  # Defines `ToolParam`, a TypeAlias representing different types of tool parameters (file search, function, web search, computer tool), and `ParseableToolParam` which includes OpenAI's `ChatCompletionToolParam`.
│   │   ├── tool_type.py  # Defines the `ToolType` enum with values for different categories of tools: WEB_SEARCH, FILE_SEARCH, and FUNCTION.
│   │   ├── tool.py  # Defines `Tool`, a TypeAlias representing different Pydantic models for tools (file search, function, web search, computer tool), using a discriminated union.
│   │   ├── web_search_tool_param.py  # Defines `WebSearchToolParam`, a TypedDict for the web search tool, including parameters for search context size and user location.
│   │   └── web_search_tool.py  # Defines the `WebSearchTool` Pydantic model, representing the web search tool with attributes for search context size and user location.
│   ├── chat_input.py  # Provides utility functions for processing chat messages: `fold_chat_messages` merges consecutive messages from the same role, and `verify_chat_messages` validates message structure and ordering against OpenAI API requirements.
│   ├── chat2reponse.py  # Defines `convert_to_response` function, which processes streaming chunks from LLMs (OpenAI/Qwen-like) and converts them into a standardized `Response` object, handling text content and tool calls.
│   ├── id_utils.py  # Provides utility functions `reason_id_of` and `message_id_of` to generate standardized IDs for reasoning items and messages from chat completion IDs by adding prefixes.
│   ├── response_differ_alone.py  # A standalone demonstration script for the `diff_responses` function, showcasing how it detects changes between different versions of a simplified `Response` object and emits events.
│   ├── response_differ_demo.py  # A demonstration script for the `diff_responses` function, using more complete mock `Response` objects to illustrate how changes in tool call status and assistant text output are detected and event types are yielded.
│   └── response_differ.py  # Implements the `diff_responses` function, which compares two `Response` objects and yields `EventType` values describing changes in tool call status, assistant text output, or reasoning items.
├── search/
│   ├── __init__.py  # Initializes the `search` sub-package.
│   ├── bings.py  # Provides synchronous (`search`) and asynchronous (`asearch`) functions for interacting with the Bing Search API (v7.0) for web and news searches, including freshness and market/country code parameters.
│   ├── qwen.py  # Implements `QwenSearcher` for performing web searches using a Qwen LLM's built-in search capabilities. Includes a backward-compatible `asearch` function.
│   ├── search_engine.py  # A placeholder file defining an empty `SearchEngine` class, likely intended for a future search engine abstraction or implementation.
│   └── tasks/
│       ├── __init__.py  # Initializes the `tasks` sub-package under `search`.
│       └── search_tool_select.py  # Defines a prompt template and the `select_tool` function (using `achat`) to determine if a search tool is needed based on chat history, outputting a JSON with 'query' or 'reply'.
├── service/
│   ├── __init__.py  # Initializes and provides access to core services like `Context`, `DocService`, `VectorStoreService`, and different effort-level `ResponseService` implementations. Manages global service instances.
│   ├── doc_service.py  # Implements `DocService` for document-related operations such as summary/tag generation, document parsing (via context), preparing file uploads (including URL download and MD5 checks), and background processing of uploads.
│   ├── response_service/
│   │   ├── __init__.py  # Initializes the `response_service` sub-package.
│   │   ├── base.py  # Defines `BaseResponseService`, providing common functionalities for response services, including callback management, ID generation, response storage, event emission, LLM instance management, and QA processing with nodes.
│   │   ├── high_effort.py  # Implements `HighEffortResponseService`, a subclass of `BaseResponseService`, currently returning a placeholder response indicating the feature is not fully implemented.
│   │   ├── low_effort.py  # Implements `LowEffortResponseService` for basic response generation, supporting file search (via collection tools), web search (Bing), and file reading tools. It orchestrates LLM calls and tool execution.
│   │   ├── medium_effort.py  # Implements `MediumEffortResponseService`, similar to `LowEffortResponseService`, using Qwen LLM for response generation and supporting file search tools. It processes requests, handles tool calls, and performs QA.
│   │   └── utils.py  # A placeholder file indicating that its previous functionality (likely `response_input2chat_messages`) has been moved to `knowledge_forge.response._types.Request`.
│   └── vectorstore_service.py  # Implements `VectorStoreService` for managing vector store collections, including creation, updates (adding/removing files), document addition/deletion from vector stores, querying, and creating tool wrappers (`CollectionAsTool`, `CollectionAsRetriever`).
├── streams/
│   ├── __init__.py  # Initializes the `streams` sub-package, exporting stream processing algorithms and type definitions.
│   ├── algo.py  # Provides utility functions for processing text streams: `parse_delimited_stream` (sync/async) for identifying sections marked by delimiters, `convert_tokens` (sync/async) for replacing mapped tokens, and `convert_to_xml_to_markdown_block` (sync/async) for converting XML-delimited sections to Markdown.
│   └── types.py  # Defines generic `AsyncStream` and `Stream` classes for iterating over asynchronous and synchronous data sources, respectively, with type casting and mapping capabilities.
├── tasks/
│   ├── outline.py  # Provides `generate_suggestions` async function to generate search engine query suggestions based on conversation history using an LLM, with specific prompting rules for different conversation contexts.
│   ├── select_search.py  # Defines `select_tool` function that uses an LLM with a specific prompt template to determine if a web search is needed based on chat history, outputting a JSON with 'query' or 'reply'.
│   ├── suggestions.py  # Provides an async function `generate_suggestions` (similar to the one in `tasks/outline.py`) to generate search query suggestions from conversation history using an LLM (Qwen-max by default).
│   ├── super_concise_summary.py  # Implements `generate_super_concise_summary` async function to create a very short (<=400 chars) summary of a document using an LLM, with specific Chinese intro phrasing.
│   ├── task_monitor.py  # Implements a task monitoring system with a base `TaskMonitor` class, a `VectorizeTaskMonitor` subclass for tracking vectorization progress, and a `TaskMonitorRegistry` to manage active monitors.
│   ├── task_recovery.py  # Provides functions to list pending tasks (`list_pending_tasks`), recover individual tasks (`recover_task`), and orchestrate recovery for all pending tasks (`recover_pending_tasks`, `recover_file_upload_tasks`), including marking tasks as failed or needing retry.
│   ├── title_generate/
│   │   └── generate_title.py  # Provides an async function `generate_title` to create a concise (<=20 words) title for a conversation using an LLM (Qwen-plus) based on a provided prompt template.
│   ├── transcript_writer.py  # Contains a system prompt (`SYSTEMP`) designed to instruct an LLM to act as a world-class podcast writer, generating engaging dialogue in Chinese between two speakers on a given topic.
│   └── yxt_doc_inspector.py  # A script that uses the YXT V1 asynchronous parsing API to inspect a document (from file or URL) and extract its summary and keywords, similar to `doc_parser/yxt_v1.py` but focused on inspection.
├── tokenizer.py  # Provides utility functions for text tokenization using `tiktoken`, including `tokenize` (get token strings), `count_token` (get token count), `truncate` (truncate by token limit), and context expansion functions (`search_and_expand_context`, `expand_context`).
├── tools/
│   ├── __init__.py  # Initializes the `tools` sub-package.
│   ├── base_tool.py  # Defines an abstract base class `Tool` with methods for name, schema, and execution. Includes `ToolResult` and `ToolError` Pydantic models, and utilities for converting to/from Langchain tools and OpenAI function schemas.
│   ├── bing_web_search.py  # Implements `BingWebSearchTool`, a `Tool` subclass that uses the Bing Search API (`asearch` from `search.bings`) to perform web and news searches, returning structured `BingSearchResults`.
│   ├── collection_as_retriever_test.py  # A command-line test script for the `CollectionAsRetriever` tool, allowing users to list collections and retrieve chunks from a specified collection using queries.
│   ├── collection_as_retriever.py  # Implements `CollectionAsRetriever`, a `Tool` subclass for retrieving relevant document chunks from a specified vector store collection based on queries, without generating a final answer.
│   ├── collection_as_tool_test.py  # A command-line test script for the `CollectionAsTool`, allowing users to search within a specified collection and get an answer generated by an LLM.
│   ├── collection_as_tool.py  # Implements `CollectionAsTool`, a `Tool` subclass that searches a specific vector store collection for relevant chunks based on a query and then uses an LLM to generate an answer from these chunks.
│   ├── document_seeker.py  # Implements `DocumentSeekerTool`, a `Tool` subclass that searches across multiple specified vector stores to find relevant document candidates based on a list of queries, returning metadata and scores.
│   ├── example_openai_tool.py  # Provides an example `WeatherTool` that inherits from `OpenAIToolSchema` to demonstrate how to define a tool compatible with OpenAI's function calling schema, including parameter definitions.
│   ├── file_reader_tool.py  # Implements `FileReaderTool`, a `Tool` subclass that reads content from specified documents (potentially bounded to a provided set) and uses an LLM to answer queries based on that content. Returns a list of `Node` objects representing the relevant information.
│   ├── list_collections.py  # A command-line script to list available collections from the local context, displaying their ID, name, description, and document count.
│   ├── multimodal_understand_tool_test.py  # A command-line test script for `MultimodalUnderstandTool`, allowing users to provide an image URL and a query to test image analysis capabilities either directly or via LLM function calling.
│   ├── multimodal_understand_tool.py  # Implements `MultimodalUnderstandTool`, a `Tool` subclass that uses the `qwen-vl-max` LLM to analyze images provided via URL based on a user's query.
│   ├── openai_tool.py  # Defines `OpenAIToolSchema`, a `Tool` subclass, for creating tools with schemas compatible with OpenAI's function calling, including `ParameterDefinition` for parameter specification.
│   ├── python_tool.py  # Implements `PythonCodeInterpreter`, a `Tool` subclass that uses `IPythonExecutor` to run Python code snippets, providing linting and error handling capabilities.
│   ├── scrape.py  # Implements `ScrapeTool`, a `Tool` subclass that uses the YXT parser (v1) via `extract_parse_result` to retrieve and parse the content of a given URL.
│   ├── toolset_demo.py  # An empty file, likely intended as a placeholder for a demonstration script for the `ToolSet` class.
│   └── toolset.py  # Implements `ToolSet` for managing a collection of `Tool` instances, providing methods to add, remove, get schema, and execute tools by name, with callback support.
└── utils/
    ├── __init__.py  # Initializes the `utils` sub-package and provides an `md5sum_of` function to calculate the MD5 hash of byte data or file content.
    ├── base64_utils.py  # Provides utility functions for base64 encoding and decoding of bytes, strings, and file contents (`bytes_to_b64`, `b64_to_bytes`, `str_to_b64`, `b64_to_str`, `file_to_b64`).
    ├── encoders.py  # Defines `DateTimeEncoder`, a `json.JSONEncoder` subclass that handles serialization of `datetime` objects into ISO 8601 string format (UTC).
    ├── pretty_print.py  # Provides a `prettyprint` decorator and helper functions (`set_doc`, `strip_oneof`) to customize the string representation (`__str__`, `__repr__`) of dataclasses for improved readability, especially for nested structures.
    └── urls.py  # Provides utility functions for URL handling: `fetch_title` (async fetch HTML title), `extract_urls` (regex-based URL extraction), and `is_image_url` (async check if URL points to an image).
````
