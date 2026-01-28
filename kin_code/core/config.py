from __future__ import annotations

from enum import StrEnum, auto
import os
from pathlib import Path
import re
import shlex
import tomllib
from typing import Annotated, Any, Literal

from dotenv import dotenv_values
from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic.fields import FieldInfo
from pydantic_core import to_jsonable_python
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)
import tomli_w

from kin_code.core.paths.config_paths import CONFIG_DIR, CONFIG_FILE, PROMPT_DIR
from kin_code.core.paths.global_paths import GLOBAL_ENV_FILE, SESSION_LOG_DIR
from kin_code.core.prompts import SystemPrompt
from kin_code.core.tools.base import BaseToolConfig


def load_api_keys_from_env() -> None:
    if GLOBAL_ENV_FILE.path.is_file():
        env_vars = dotenv_values(GLOBAL_ENV_FILE.path)
        for key, value in env_vars.items():
            if value:
                os.environ.setdefault(key, value)


class MissingAPIKeyError(RuntimeError):
    def __init__(self, env_key: str, provider_name: str) -> None:
        super().__init__(
            f"Missing {env_key} environment variable for {provider_name} provider"
        )
        self.env_key = env_key
        self.provider_name = provider_name


class MissingPromptFileError(RuntimeError):
    def __init__(self, system_prompt_id: str, prompt_dir: str) -> None:
        super().__init__(
            f"Invalid system_prompt_id value: '{system_prompt_id}'. "
            f"Must be one of the available prompts ({', '.join(f'{p.name.lower()}' for p in SystemPrompt)}), "
            f"or correspond to a .md file in {prompt_dir}"
        )
        self.system_prompt_id = system_prompt_id
        self.prompt_dir = prompt_dir


class TomlFileSettingsSource(PydanticBaseSettingsSource):
    def __init__(self, settings_cls: type[BaseSettings]) -> None:
        super().__init__(settings_cls)
        self.toml_data = self._load_toml()

    def _load_toml(self) -> dict[str, Any]:
        file = CONFIG_FILE.path
        try:
            with file.open("rb") as f:
                return tomllib.load(f)
        except FileNotFoundError:
            return {}
        except tomllib.TOMLDecodeError as e:
            raise RuntimeError(f"Invalid TOML in {file}: {e}") from e
        except OSError as e:
            raise RuntimeError(f"Cannot read {file}: {e}") from e

    def get_field_value(
        self, field: FieldInfo, field_name: str
    ) -> tuple[Any, str, bool]:
        _ = field
        return self.toml_data.get(field_name), field_name, False

    def __call__(self) -> dict[str, Any]:
        return self.toml_data


class ProjectContextConfig(BaseSettings):
    max_chars: int = 40_000
    default_commit_count: int = 5
    max_doc_bytes: int = 32 * 1024
    truncation_buffer: int = 1_000
    max_depth: int = 3
    max_files: int = 1000
    max_dirs_per_level: int = 20
    timeout_seconds: float = 2.0


class SessionLoggingConfig(BaseSettings):
    save_dir: str = ""
    session_prefix: str = "session"
    enabled: bool = True

    @field_validator("save_dir", mode="before")
    @classmethod
    def set_default_save_dir(cls, v: str) -> str:
        if not v:
            return str(SESSION_LOG_DIR.path)
        return v

    @field_validator("save_dir", mode="after")
    @classmethod
    def expand_save_dir(cls, v: str) -> str:
        return str(Path(v).expanduser().resolve())


class Backend(StrEnum):
    GENERIC = auto()


class ProviderConfig(BaseModel):
    """Configuration for an LLM API provider.

    Defines how to connect to an LLM provider's API endpoint. Multiple
    providers can be configured, and models reference providers by name.

    Attributes:
        name: Unique identifier for this provider (e.g., "openrouter").
        api_base: Base URL for the API (e.g., "https://openrouter.ai/api/v1").
        api_key_env_var: Environment variable containing the API key.
        api_style: API format, typically "openai" for OpenAI-compatible APIs.
        backend: Backend implementation to use (default: GENERIC).
        reasoning_field_name: Field name for reasoning content in responses.

    Example:
        TOML configuration::

            [[providers]]
            name = "openrouter"
            api_base = "https://openrouter.ai/api/v1"
            api_key_env_var = "OPENROUTER_API_KEY"

            [[providers]]
            name = "local-ollama"
            api_base = "http://localhost:11434/v1"
            api_key_env_var = ""  # No key needed for local
    """

    name: str
    api_base: str
    api_key_env_var: str = ""
    api_style: str = "openai"
    backend: Backend = Backend.GENERIC
    reasoning_field_name: str = "reasoning_content"


class _MCPBase(BaseModel):
    name: str = Field(description="Short alias used to prefix tool names")
    prompt: str | None = Field(
        default=None, description="Optional usage hint appended to tool descriptions"
    )
    startup_timeout_sec: float = Field(
        default=10.0,
        gt=0,
        description="Timeout in seconds for the server to start and initialize.",
    )
    tool_timeout_sec: float = Field(
        default=60.0, gt=0, description="Timeout in seconds for tool execution."
    )

    @field_validator("name", mode="after")
    @classmethod
    def normalize_name(cls, v: str) -> str:
        normalized = re.sub(r"[^a-zA-Z0-9_-]", "_", v)
        normalized = normalized.strip("_-")
        return normalized[:256]


class _MCPHttpFields(BaseModel):
    url: str = Field(description="Base URL of the MCP HTTP server")
    headers: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Additional HTTP headers when using 'http' transport (e.g., Authorization or X-API-Key)."
        ),
    )
    api_key_env: str = Field(
        default="",
        description=(
            "Environment variable name containing an API token to send for HTTP transport."
        ),
    )
    api_key_header: str = Field(
        default="Authorization",
        description=(
            "HTTP header name to carry the token when 'api_key_env' is set (e.g., 'Authorization' or 'X-API-Key')."
        ),
    )
    api_key_format: str = Field(
        default="Bearer {token}",
        description=(
            "Format string for the header value when 'api_key_env' is set. Use '{token}' placeholder."
        ),
    )

    def http_headers(self) -> dict[str, str]:
        hdrs = dict(self.headers or {})
        env_var = (self.api_key_env or "").strip()
        if env_var and (token := os.getenv(env_var)):
            target = (self.api_key_header or "").strip() or "Authorization"
            if not any(h.lower() == target.lower() for h in hdrs):
                try:
                    value = (self.api_key_format or "{token}").format(token=token)
                except Exception:
                    value = token
                hdrs[target] = value
        return hdrs


class MCPHttp(_MCPBase, _MCPHttpFields):
    transport: Literal["http"]


class MCPStreamableHttp(_MCPBase, _MCPHttpFields):
    transport: Literal["streamable-http"]


class MCPStdio(_MCPBase):
    transport: Literal["stdio"]
    command: str | list[str]
    args: list[str] = Field(default_factory=list)
    env: dict[str, str] = Field(
        default_factory=dict,
        description="Environment variables to set for the MCP server process.",
    )

    def argv(self) -> list[str]:
        base = (
            shlex.split(self.command)
            if isinstance(self.command, str)
            else list(self.command or [])
        )
        return [*base, *self.args] if self.args else base


MCPServer = Annotated[
    MCPHttp | MCPStreamableHttp | MCPStdio, Field(discriminator="transport")
]


class ReasoningMode(StrEnum):
    """How to handle reasoning content in conversation history.

    STRIP: Extract reasoning for display but remove from context before next turn.
           Use for models where reasoning is output-only (DeepSeek R1, Qwen3, Nemotron).

    PRESERVE: Keep reasoning in conversation history for multi-turn coherence.
              Use for models that benefit from seeing prior reasoning
              (Kimi K2.5, GLM-4.7, Minimax-m2.1, Claude extended thinking).
    """

    STRIP = auto()
    PRESERVE = auto()


class ToolCallFormat(StrEnum):
    """How to parse tool calls from LLM responses.

    API: Parse from structured tool_calls field (OpenAI format). Default.
    XML: Parse from XML tags in content (Qwen3-coder/Nemotron format).
    AUTO: Try API first, fall back to XML if no tool calls found.
    NONE: Disable tool call parsing entirely.
    """

    API = auto()
    XML = auto()
    AUTO = auto()
    NONE = auto()


class ModelConfig(BaseModel):
    """Configuration for a specific LLM model.

    Defines model parameters including the provider to use, sampling settings,
    and optional pricing/context information for cost tracking.

    Attributes:
        name: Full model identifier (e.g., "anthropic/claude-sonnet-4").
        provider: Name of the provider to use (must match a ProviderConfig.name).
        alias: Short name for model selection (e.g., "claude-sonnet").
        temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative).
        top_p: Nucleus sampling parameter (None = use provider default).
        reasoning_enabled: Enable extended thinking/reasoning if supported.
        reasoning_mode: How to handle reasoning in context (strip or preserve).
        reasoning_budget: Max reasoning tokens to request from API (provider-specific).
        input_price: Cost per million input tokens for cost tracking.
        output_price: Cost per million output tokens for cost tracking.
        context_window: Maximum context size in tokens.

    Example:
        TOML configuration::

            [[models]]
            name = "anthropic/claude-sonnet-4"
            alias = "claude-sonnet"
            provider = "openrouter"
            temperature = 0.2

            [[models]]
            name = "anthropic/claude-opus-4"
            alias = "claude-opus"
            provider = "openrouter"
            temperature = 0.1
            reasoning_enabled = true
            reasoning_mode = "preserve"
            reasoning_budget = 8000
            context_window = 200000

            [[models]]
            name = "moonshotai/kimi-k2-instruct"
            alias = "kimi-k2"
            provider = "openrouter"
            reasoning_enabled = true
            reasoning_mode = "preserve"  # Kimi benefits from preserved reasoning

            [[models]]
            name = "qwen/qwq-32b"
            alias = "qwq"
            provider = "openrouter"
            reasoning_enabled = true
            reasoning_mode = "strip"  # QwQ uses <think> tags, strip before next turn
    """

    name: str
    provider: str
    alias: str
    temperature: float = 0.2
    top_p: float | None = None  # If set, include in API request
    reasoning_enabled: bool | None = None  # If True, send reasoning param to API
    reasoning_mode: ReasoningMode = ReasoningMode.STRIP  # How to handle reasoning in context
    reasoning_budget: int | None = None  # Max reasoning tokens (provider-specific)
    tool_call_format: ToolCallFormat = ToolCallFormat.API
    input_price: float | None = (
        None  # Price per million input tokens (None = auto-fetch)
    )
    output_price: float | None = (
        None  # Price per million output tokens (None = auto-fetch)
    )
    context_window: int | None = None  # Context window size (None = unknown)

    @model_validator(mode="before")
    @classmethod
    def _default_alias_to_name(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "alias" not in data or data["alias"] is None:
                data["alias"] = data.get("name")
        return data


DEFAULT_PROVIDERS = [
    ProviderConfig(
        name="openrouter",
        api_base="https://openrouter.ai/api/v1",
        api_key_env_var="OPENROUTER_API_KEY",
    )
]

DEFAULT_MODELS: list[ModelConfig] = []


class VibeConfig(BaseSettings):
    """Central configuration for Kin Code sessions.

    VibeConfig manages all configuration settings, merging values from multiple
    sources in priority order:

    1. Constructor arguments (highest priority)
    2. Environment variables (KIN_* prefix)
    3. TOML config file (~/.config/kin/config.toml)
    4. Built-in defaults (lowest priority)

    The configuration covers model selection, provider settings, tool/agent/skill
    paths, UI preferences, and session behavior.

    Attributes:
        active_model: Alias of the currently selected model.
        models: List of configured ModelConfig entries.
        providers: List of configured ProviderConfig entries.
        tools: Per-tool configuration overrides.
        mcp_servers: MCP server configurations for remote tools.
        system_prompt: The resolved system prompt content.
        effective_workdir: Working directory with override applied.

    Example:
        Loading configuration::

            from kin_code.core.config import VibeConfig, load_api_keys_from_env

            # Load API keys from ~/.config/kin/.env into environment
            load_api_keys_from_env()

            # Load config with defaults + TOML + env vars
            config = VibeConfig.load()

            # Or with constructor overrides
            config = VibeConfig.load(
                active_model="claude-sonnet",
                auto_approve=True
            )

        Accessing model and provider settings::

            # Get active model configuration
            model = config.get_active_model()
            print(f"Model: {model.name}, Provider: {model.provider}")

            # Get provider for the model
            provider = config.get_provider_for_model(model)
            print(f"API Base: {provider.api_base}")

        Configuring models and providers::

            # In config.toml:
            # [[providers]]
            # name = "openrouter"
            # api_base = "https://openrouter.ai/api/v1"
            # api_key_env_var = "OPENROUTER_API_KEY"
            #
            # [[models]]
            # name = "anthropic/claude-sonnet-4"
            # alias = "claude-sonnet"
            # provider = "openrouter"
            # temperature = 0.2

            # Access in code
            for model in config.models:
                print(f"{model.alias}: {model.name}")

        Working with MCP servers::

            # In config.toml:
            # [[mcp_servers]]
            # name = "filesystem"
            # transport = "stdio"
            # command = "npx @anthropic/mcp-server-filesystem"
            # args = ["/home/user/projects"]

            for server in config.mcp_servers:
                match server.transport:
                    case "stdio":
                        print(f"Stdio: {server.command}")
                    case "http" | "streamable-http":
                        print(f"HTTP: {server.url}")

        Saving configuration updates::

            # Update specific fields
            VibeConfig.save_updates({
                "active_model": "claude-opus",
                "auto_approve": False
            })

            # Create default config file
            defaults = VibeConfig.create_default()
            VibeConfig.dump_config(defaults)
    """

    active_model: str = ""
    textual_theme: str = "terminal"
    vim_keybindings: bool = False
    disable_welcome_banner_animation: bool = False
    displayed_workdir: str = ""
    workdir: Path | None = None  # Override working directory
    auto_compact_threshold: int = 200_000  # Hard ceiling fallback
    auto_compact_percent: float = 0.90  # Compact at 90% of context window
    context_warnings: bool = False
    auto_approve: bool = False
    system_prompt_id: str = "cli"
    include_commit_signature: bool = True
    include_model_info: bool = True
    include_project_context: bool = True
    include_prompt_detail: bool = True
    enable_update_checks: bool = True
    enable_auto_update: bool = True
    api_timeout: float = 720.0
    providers: list[ProviderConfig] = Field(
        default_factory=lambda: list(DEFAULT_PROVIDERS)
    )
    models: list[ModelConfig] = Field(default_factory=lambda: list(DEFAULT_MODELS))

    project_context: ProjectContextConfig = Field(default_factory=ProjectContextConfig)
    session_logging: SessionLoggingConfig = Field(default_factory=SessionLoggingConfig)
    tools: dict[str, BaseToolConfig] = Field(default_factory=dict)
    tool_paths: list[Path] = Field(
        default_factory=list,
        description=(
            "Additional directories or files to explore for custom tools. "
            "Paths may be absolute or relative to the current working directory. "
            "Directories are shallow-searched for tool definition files, "
            "while files are loaded directly if valid."
        ),
    )

    mcp_servers: list[MCPServer] = Field(
        default_factory=list, description="Preferred MCP server configuration entries."
    )

    enabled_tools: list[str] = Field(
        default_factory=list,
        description=(
            "An explicit list of tool names/patterns to enable. If set, only these"
            " tools will be active. Supports glob patterns (e.g., 'serena_*') and"
            " regex with 're:' prefix (e.g., 're:^serena_.*')."
        ),
    )
    disabled_tools: list[str] = Field(
        default_factory=list,
        description=(
            "A list of tool names/patterns to disable. Ignored if 'enabled_tools'"
            " is set. Supports glob patterns and regex with 're:' prefix."
        ),
    )
    agent_paths: list[Path] = Field(
        default_factory=list,
        description=(
            "Additional directories to search for custom agent profiles. "
            "Each path may be absolute or relative to the current working directory."
        ),
    )
    enabled_agents: list[str] = Field(
        default_factory=list,
        description=(
            "An explicit list of agent names/patterns to enable. If set, only these"
            " agents will be available. Supports glob patterns (e.g., 'custom-*')"
            " and regex with 're:' prefix."
        ),
    )
    disabled_agents: list[str] = Field(
        default_factory=list,
        description=(
            "A list of agent names/patterns to disable. Ignored if 'enabled_agents'"
            " is set. Supports glob patterns and regex with 're:' prefix."
        ),
    )
    skill_paths: list[Path] = Field(
        default_factory=list,
        description=(
            "Additional directories to search for skills. "
            "Each path may be absolute or relative to the current working directory."
        ),
    )
    enabled_skills: list[str] = Field(
        default_factory=list,
        description=(
            "An explicit list of skill names/patterns to enable. If set, only these"
            " skills will be active. Supports glob patterns (e.g., 'search-*') and"
            " regex with 're:' prefix."
        ),
    )
    disabled_skills: list[str] = Field(
        default_factory=list,
        description=(
            "A list of skill names/patterns to disable. Ignored if 'enabled_skills'"
            " is set. Supports glob patterns and regex with 're:' prefix."
        ),
    )

    model_config = SettingsConfigDict(
        env_prefix="KIN_", case_sensitive=False, extra="ignore"
    )

    @property
    def system_prompt(self) -> str:
        try:
            return SystemPrompt[self.system_prompt_id.upper()].read()
        except KeyError:
            pass

        custom_sp_path = (PROMPT_DIR.path / self.system_prompt_id).with_suffix(".md")
        if not custom_sp_path.is_file():
            raise MissingPromptFileError(self.system_prompt_id, str(PROMPT_DIR.path))
        return custom_sp_path.read_text()

    @property
    def effective_workdir(self) -> Path:
        """Get the effective working directory, using override if set."""
        if self.workdir:
            return self.workdir.expanduser().resolve()
        return Path.cwd()

    def get_active_model(self) -> ModelConfig:
        for model in self.models:
            if model.alias == self.active_model:
                return model
        raise ValueError(
            f"Active model '{self.active_model}' not found in configuration."
        )

    def get_provider_for_model(self, model: ModelConfig) -> ProviderConfig:
        for provider in self.providers:
            if provider.name == model.provider:
                return provider
        raise ValueError(
            f"Provider '{model.provider}' for model '{model.name}' not found in configuration."
        )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Define the priority of settings sources.

        Note: dotenv_settings is intentionally excluded. API keys and other
        non-config environment variables are stored in .env but loaded manually
        into os.environ for use by providers. Only KIN_* prefixed environment
        variables (via env_settings) and TOML config are used for Pydantic settings.
        """
        _ = dotenv_settings
        return (
            init_settings,
            env_settings,
            TomlFileSettingsSource(settings_cls),
            file_secret_settings,
        )

    @model_validator(mode="after")
    def _check_api_key(self) -> KinConfig:
        try:
            active_model = self.get_active_model()
            provider = self.get_provider_for_model(active_model)
            api_key_env = provider.api_key_env_var
            if api_key_env and not os.getenv(api_key_env):
                raise MissingAPIKeyError(api_key_env, provider.name)
        except ValueError:
            pass
        return self

    @field_validator("tool_paths", mode="before")
    @classmethod
    def _expand_tool_paths(cls, v: Any) -> list[Path]:
        if not v:
            return []
        return [Path(p).expanduser().resolve() for p in v]

    @field_validator("skill_paths", mode="before")
    @classmethod
    def _expand_skill_paths(cls, v: Any) -> list[Path]:
        if not v:
            return []
        return [Path(p).expanduser().resolve() for p in v]

    @field_validator("tools", mode="before")
    @classmethod
    def _normalize_tool_configs(cls, v: Any) -> dict[str, BaseToolConfig]:
        if not isinstance(v, dict):
            return {}

        normalized: dict[str, BaseToolConfig] = {}
        for tool_name, tool_config in v.items():
            if isinstance(tool_config, BaseToolConfig):
                normalized[tool_name] = tool_config
            elif isinstance(tool_config, dict):
                normalized[tool_name] = BaseToolConfig.model_validate(tool_config)
            else:
                normalized[tool_name] = BaseToolConfig()

        return normalized

    @model_validator(mode="after")
    def _validate_model_uniqueness(self) -> KinConfig:
        seen_aliases: set[str] = set()
        for model in self.models:
            if model.alias in seen_aliases:
                raise ValueError(
                    f"Duplicate model alias found: '{model.alias}'. Aliases must be unique."
                )
            seen_aliases.add(model.alias)
        return self

    @model_validator(mode="after")
    def _check_system_prompt(self) -> KinConfig:
        _ = self.system_prompt
        return self

    @classmethod
    def save_updates(cls, updates: dict[str, Any]) -> None:
        CONFIG_DIR.path.mkdir(parents=True, exist_ok=True)
        current_config = TomlFileSettingsSource(cls).toml_data

        def deep_merge(target: dict, source: dict) -> None:
            for key, value in source.items():
                if (
                    key in target
                    and isinstance(target.get(key), dict)
                    and isinstance(value, dict)
                ):
                    deep_merge(target[key], value)
                elif (
                    key in target
                    and isinstance(target.get(key), list)
                    and isinstance(value, list)
                ):
                    if key in {"providers", "models"}:
                        target[key] = value
                    else:
                        target[key] = list(set(value + target[key]))
                else:
                    target[key] = value

        deep_merge(current_config, updates)
        cls.dump_config(
            to_jsonable_python(current_config, exclude_none=True, fallback=str)
        )

    @classmethod
    def dump_config(cls, config: dict[str, Any]) -> None:
        # Filter out None values recursively since TOML doesn't support None
        def filter_none(obj: Any) -> Any:
            if isinstance(obj, dict):
                return {k: filter_none(v) for k, v in obj.items() if v is not None}
            if isinstance(obj, list):
                return [filter_none(item) for item in obj]
            return obj

        with CONFIG_FILE.path.open("wb") as f:
            tomli_w.dump(filter_none(config), f)

    @classmethod
    def _migrate(cls) -> None:
        pass

    @classmethod
    def load(cls, **overrides: Any) -> KinConfig:
        cls._migrate()
        return cls(**(overrides or {}))

    @classmethod
    def create_default(cls) -> dict[str, Any]:
        try:
            config = cls()
        except MissingAPIKeyError:
            config = cls.model_construct()

        config_dict = config.model_dump(mode="json", exclude_none=True)

        from kin_code.core.tools.manager import ToolManager

        tool_defaults = ToolManager.discover_tool_defaults()
        if tool_defaults:
            config_dict["tools"] = tool_defaults

        return config_dict


# Alias for clarity
KinConfig = VibeConfig
