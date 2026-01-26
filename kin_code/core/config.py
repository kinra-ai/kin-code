"""Configuration management with Pydantic validation.

This module defines the KinConfig class (aliased as VibeConfig for backward
compatibility) that centralizes all agent configuration including models,
providers, tools, MCP servers, system prompts, and runtime settings. The
configuration system supports TOML files, environment variables, and
programmatic overrides with comprehensive validation.

Key Components:
    KinConfig: Main configuration class with Pydantic validation and TOML persistence.
    ModelConfig: Model-specific settings (name, pricing, context window, temperature).
    ProviderConfig: Provider connection details (API base URL, key, backend type).
    MCPServer: Discriminated union of MCP server configurations (http, streamable-http, stdio).
    Backend: Enum for LLM backend types (MISTRAL, GENERIC).
    BaseToolConfig: Base configuration for tools (permissions, workdir, allow/deny lists).
    ProjectContextConfig: Settings for project context gathering.
    SessionLoggingConfig: Configuration for session logging behavior.

The configuration system:
- Loads from TOML file (~/.config/kin-code/config.toml by default)
- Supports KIN_* prefixed environment variables for overrides
- Validates API keys, provider compatibility, and model uniqueness
- Resolves system prompts from built-in enums or custom .md files
- Manages MCP server configurations with discriminated unions
- Provides agent-specific config files for specialized behaviors
- Supports per-tool configuration with allowlists/denylists
- Handles path expansion for workdir, tool_paths, and skill_paths

Typical usage:

    from kin_code.core.config import KinConfig, ModelConfig, ProviderConfig

    # Load default configuration
    config = KinConfig.load()

    # Load with agent-specific overrides
    config = KinConfig.load(agent="python-dev")

    # Access active model settings
    model = config.get_active_model()
    provider = config.get_provider_for_model(model)

    # Save configuration updates
    KinConfig.save_updates({
        "active_model": "devstral-small",
        "context_warnings": True,
    })

    # Create default config for first-time setup
    default_dict = KinConfig.create_default()

Configuration priority (highest to lowest):
1. Programmatic overrides passed to KinConfig.load(**overrides)
2. KIN_* environment variables
3. TOML configuration file
4. Agent-specific TOML file
5. Field defaults
"""

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

from kin_code.core.paths.config_paths import (
    AGENT_DIR,
    CONFIG_DIR,
    CONFIG_FILE,
    PROMPT_DIR,
)
from kin_code.core.paths.global_paths import GLOBAL_ENV_FILE, SESSION_LOG_DIR
from kin_code.core.prompts import SystemPrompt
from kin_code.core.tools.base import BaseToolConfig

_MIN_CONTEXT_WINDOW = 512


def _strip_none_values(obj: Any) -> Any:
    """Recursively remove None values from nested dicts and lists for TOML serialization."""
    match obj:
        case dict():
            return {k: _strip_none_values(v) for k, v in obj.items() if v is not None}
        case list():
            return [_strip_none_values(item) for item in obj]
        case _:
            return obj


def load_api_keys_from_env() -> None:
    if GLOBAL_ENV_FILE.path.is_file():
        env_vars = dotenv_values(GLOBAL_ENV_FILE.path)
        for key, value in env_vars.items():
            if value:
                os.environ.setdefault(key, value)


class MissingAPIKeyError(RuntimeError):
    """Raised when a required API key environment variable is not set.

    This exception is raised during configuration validation when a provider
    requires an API key but the corresponding environment variable is missing.

    Attributes:
        env_key: The name of the missing environment variable.
        provider_name: The name of the provider that requires the API key.
    """

    def __init__(self, env_key: str, provider_name: str) -> None:
        super().__init__(
            f"Missing {env_key} environment variable for {provider_name} provider"
        )
        self.env_key = env_key
        self.provider_name = provider_name


class MissingPromptFileError(RuntimeError):
    """Raised when a system prompt file cannot be found.

    This exception is raised when the system_prompt_id does not match a
    built-in prompt enum value and no corresponding .md file exists in
    the prompts directory.

    Attributes:
        system_prompt_id: The prompt identifier that was not found.
        prompt_dir: The directory path where custom prompts should be located.
    """

    def __init__(self, system_prompt_id: str, prompt_dir: str) -> None:
        super().__init__(
            f"Invalid system_prompt_id value: '{system_prompt_id}'. "
            f"Must be one of the available prompts ({', '.join(f'{p.name.lower()}' for p in SystemPrompt)}), "
            f"or correspond to a .md file in {prompt_dir}"
        )
        self.system_prompt_id = system_prompt_id
        self.prompt_dir = prompt_dir


class WrongBackendError(RuntimeError):
    """Raised when a provider's backend doesn't match its API type.

    This exception is raised during configuration validation when a Mistral API
    provider is configured with a non-Mistral backend, or vice versa.

    Attributes:
        backend: The incorrectly configured backend.
        is_mistral_api: Whether the provider is a Mistral API endpoint.
    """

    def __init__(self, backend: Backend, is_mistral_api: bool) -> None:
        super().__init__(
            f"Wrong backend '{backend}' for {'' if is_mistral_api else 'non-'}"
            f"mistral API. Use '{Backend.MISTRAL}' for mistral API and '{Backend.GENERIC}' for others."
        )
        self.backend = backend
        self.is_mistral_api = is_mistral_api


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
        del field  # Required by protocol but not used in TOML source
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
    MISTRAL = auto()
    GENERIC = auto()


class ProviderConfig(BaseModel):
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


class ModelConfig(BaseModel):
    name: str
    provider: str
    alias: str
    temperature: float = 0.2
    input_price: float = 0.0  # Price per million input tokens
    output_price: float = 0.0  # Price per million output tokens
    context_window: int | None = None
    supports_tools: bool = True  # Whether the model supports tool calling

    @model_validator(mode="before")
    @classmethod
    def _default_alias_to_name(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "alias" not in data or data["alias"] is None:
                data["alias"] = data.get("name")
        return data


DEFAULT_PROVIDERS = [
    ProviderConfig(
        name="mistral",
        api_base="https://api.mistral.ai/v1",
        api_key_env_var="MISTRAL_API_KEY",
        backend=Backend.MISTRAL,
    ),
    ProviderConfig(
        name="llamacpp",
        api_base="http://127.0.0.1:8080/v1",
        api_key_env_var="",  # NOTE: if you wish to use --api-key in llama-server, change this value
    ),
]

DEFAULT_MODELS = [
    ModelConfig(
        name="kin-code-latest",
        provider="mistral",
        alias="devstral-2",
        input_price=0.4,
        output_price=2.0,
        context_window=128_000,
    ),
    ModelConfig(
        name="devstral-small-latest",
        provider="mistral",
        alias="devstral-small",
        input_price=0.1,
        output_price=0.3,
        context_window=128_000,
    ),
    ModelConfig(
        name="devstral",
        provider="llamacpp",
        alias="local",
        input_price=0.0,
        output_price=0.0,
    ),
]


class KinConfig(BaseSettings):
    active_model: str = "devstral-2"
    textual_theme: str = "terminal"
    vim_keybindings: bool = False
    disable_welcome_banner_animation: bool = False
    displayed_workdir: str = ""
    auto_compact_threshold: int = 200_000
    context_warnings: bool = False
    instructions: str = ""
    workdir: Path | None = Field(default=None, exclude=True)
    system_prompt_id: str = "cli"
    include_commit_signature: bool = True
    include_model_info: bool = True
    include_project_context: bool = True
    include_prompt_detail: bool = True
    enable_update_checks: bool = True
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
            "Additional directories to search for custom tools. "
            "Each path may be absolute or relative to the current working directory."
        ),
    )

    mcp_servers: list[MCPServer] = Field(
        default_factory=list, description="Preferred MCP server configuration entries."
    )

    enabled_tools: list[str] = Field(
        default_factory=list,
        description=(
            "An explicit list of tool names/patterns to enable. If set, only these"
            " tools will be active. Supports exact names, glob patterns (e.g.,"
            " 'serena_*'), and regex with 're:' prefix or regex-like patterns (e.g.,"
            " 're:^serena_.*' or 'serena.*')."
        ),
    )
    disabled_tools: list[str] = Field(
        default_factory=list,
        description=(
            "A list of tool names/patterns to disable. Ignored if 'enabled_tools'"
            " is set. Supports exact names, glob patterns (e.g., 'bash*'), and"
            " regex with 're:' prefix or regex-like patterns."
        ),
    )

    skill_paths: list[Path] = Field(
        default_factory=list,
        description=(
            "Additional directories to search for skills. "
            "Each path may be absolute or relative to the current working directory."
        ),
    )

    model_config = SettingsConfigDict(
        env_prefix="KIN_", case_sensitive=False, extra="ignore"
    )

    @property
    def effective_workdir(self) -> Path:
        return self.workdir if self.workdir is not None else Path.cwd()

    @property
    def system_prompt(self) -> str:
        """Get the system prompt content for the configured prompt ID.

        Attempts to load the prompt from built-in prompts first, then checks
        for a custom .md file in the prompts directory.

        Returns:
            The system prompt content as a string.

        Raises:
            MissingPromptFileError: If the system_prompt_id does not match a
                built-in prompt or a .md file in the prompts directory.
        """
        try:
            return SystemPrompt[self.system_prompt_id.upper()].read()
        except KeyError:
            pass

        custom_sp_path = (PROMPT_DIR.path / self.system_prompt_id).with_suffix(".md")
        if not custom_sp_path.is_file():
            raise MissingPromptFileError(self.system_prompt_id, str(PROMPT_DIR.path))
        return custom_sp_path.read_text()

    def get_active_model(self) -> ModelConfig:
        """Get the currently active model configuration.

        Searches the configured models list for one matching the active_model alias.

        Returns:
            The ModelConfig for the active model.

        Raises:
            ValueError: If the active model alias is not found in the models list.
        """
        for model in self.models:
            if model.alias == self.active_model:
                return model
        raise ValueError(
            f"Active model '{self.active_model}' not found in configuration."
        )

    def get_provider_for_model(self, model: ModelConfig) -> ProviderConfig:
        """Get the provider configuration for a given model.

        Searches the configured providers list for one matching the model's provider name.

        Args:
            model: The model configuration to find a provider for.

        Returns:
            The ProviderConfig for the model's provider.

        Raises:
            ValueError: If the model's provider is not found in the providers list.
        """
        for provider in self.providers:
            if provider.name == model.provider:
                return provider
        raise ValueError(
            f"Provider '{model.provider}' for model '{model.name}' not found in configuration."
        )

    def get_effective_context_window(self) -> int:
        """Get effective context window, preferring model's value over global default.

        Returns the model's context_window if available and valid (>= _MIN_CONTEXT_WINDOW),
        otherwise falls back to auto_compact_threshold.
        """
        try:
            active_model = self.get_active_model()
            if (
                active_model.context_window is not None
                and active_model.context_window >= _MIN_CONTEXT_WINDOW
            ):
                return active_model.context_window
        except ValueError:
            pass
        return self.auto_compact_threshold

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
        into os.environ for use by providers. Only VIBE_* prefixed environment
        variables (via env_settings) and TOML config are used for Pydantic settings.
        """
        del dotenv_settings  # Intentionally excluded per docstring
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

    @model_validator(mode="after")
    def _check_api_backend_compatibility(self) -> KinConfig:
        try:
            active_model = self.get_active_model()
            provider = self.get_provider_for_model(active_model)
            MISTRAL_API_BASES = [
                "https://codestral.mistral.ai",
                "https://api.mistral.ai",
            ]
            is_mistral_api = any(
                provider.api_base.startswith(api_base) for api_base in MISTRAL_API_BASES
            )
            if (is_mistral_api and provider.backend != Backend.MISTRAL) or (
                not is_mistral_api and provider.backend != Backend.GENERIC
            ):
                raise WrongBackendError(provider.backend, is_mistral_api)

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

    @field_validator("workdir", mode="before")
    @classmethod
    def _expand_workdir(cls, v: Any) -> Path | None:
        if v is None or (isinstance(v, str) and not v.strip()):
            return None

        if isinstance(v, str):
            v = Path(v).expanduser().resolve()
        elif isinstance(v, Path):
            v = v.expanduser().resolve()
        if not v.is_dir():
            raise ValueError(
                f"Tried to set {v} as working directory, path doesn't exist"
            )
        return v

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
        serializable = to_jsonable_python(config, fallback=str)
        serializable = _strip_none_values(serializable)
        with CONFIG_FILE.path.open("wb") as f:
            tomli_w.dump(serializable, f)

    @classmethod
    def _get_agent_config(cls, agent: str | None) -> dict[str, Any] | None:
        """Load agent-specific configuration from a TOML file.

        Args:
            agent: Optional name of the agent configuration to load. If None, returns None.

        Returns:
            Dictionary of configuration values, or None if agent is None.

        Raises:
            ValueError: If the agent configuration file is not found.
        """
        if agent is None:
            return None

        agent_config_path = (AGENT_DIR.path / agent).with_suffix(".toml")
        try:
            return tomllib.load(agent_config_path.open("rb"))
        except FileNotFoundError:
            raise ValueError(
                f"Config '{agent}.toml' for agent not found in {AGENT_DIR.path}"
            )

    @classmethod
    def _migrate(cls) -> None:
        pass

    @classmethod
    def load(cls, agent: str | None = None, **overrides: Any) -> KinConfig:
        cls._migrate()
        agent_config = cls._get_agent_config(agent)
        init_data = {**(agent_config or {}), **overrides}
        return cls(**init_data)

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


# Backward compatibility alias
VibeConfig = KinConfig
