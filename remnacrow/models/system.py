from .base import Struct


class RuntimeMetric(Struct):
    rss: float
    heap_used: float
    heap_total: float
    external: float
    array_buffers: float
    event_loop_delay_ms: float
    event_loop_p99_ms: float
    active_handles: float
    uptime: float
    pid: float
    timestamp: float
    instance_id: str
    instance_type: str


class RemnawaveHealth(Struct):
    runtime_metrics: list[RuntimeMetric]


class MetadataBuild(Struct):
    time: str
    number: str


class MetadataBackendGit(Struct):
    commit_sha: str
    branch: str
    commit_url: str


class MetadataFrontendGit(Struct):
    commit_sha: str
    commit_url: str


class MetadataGit(Struct):
    backend: MetadataBackendGit
    frontend: MetadataFrontendGit


class RemnawaveMetadata(Struct):
    version: str
    build: MetadataBuild
    git: MetadataGit


class NodeMetricInboundStats(Struct):
    tag: str
    upload: str
    download: str


class NodeMetricOutboundStats(Struct):
    tag: str
    upload: str
    download: str


class NodeMetrics(Struct):
    node_uuid: str
    node_name: str
    country_emoji: str
    provider_name: str
    users_online: float
    inbounds_stats: list[NodeMetricInboundStats]
    outbounds_stats: list[NodeMetricOutboundStats]


class NodesMetrics(Struct):
    nodes: list[NodeMetrics]


class X25519Keypair(Struct):
    public_key: str
    private_key: str


class X25519Keypairs(Struct):
    keypairs: list[X25519Keypair]


class PublicKey(Struct):
    pub_key: str


class SrrMatcherHeaderModification(Struct):
    key: str
    value: str


class SrrMatcherEncryption(Struct):
    method: str
    key: str


class SrrMatcherResponseModifications(Struct):
    headers: list[SrrMatcherHeaderModification] | None = None
    apply_headers_to_end: bool | None = None
    subscription_template: str | None = None
    ignore_host_xray_json_template: bool | None = None
    ignore_serve_json_at_base_subscription: bool | None = None
    additional_extended_clients_regex: list[str] | None = None
    disable_hwid_check: bool | None = None
    encryption: SrrMatcherEncryption | None = None
    exclude_hosts_by_tags: list[str] | None = None


class SrrMatcherCondition(Struct):
    header_name: str
    operator: str
    value: str
    case_sensitive: bool


class SrrMatcherRule(Struct):
    name: str
    enabled: bool
    operator: str
    conditions: list[SrrMatcherCondition]
    response_type: str
    description: str | None = None
    response_modifications: SrrMatcherResponseModifications | None = None


class SrrMatcherSettings(Struct):
    disable_subscription_access_by_path: bool | None = None


class SrrMatcherResponseRules(Struct):
    version: str
    rules: list[SrrMatcherRule]
    settings: SrrMatcherSettings | None = None


class SrrMatcherResult(Struct):
    matched: bool
    response_type: str
    matched_rule: SrrMatcherRule | None
    input_headers: dict[str, str]
    output_headers: dict[str, str]
