from .auth import AuthRoute
from .config_profiles import ConfigProfilesRoute
from .external_squads import ExternalSquadsRoute
from .hosts import HostsRoute
from .hwid import HwidRoute
from .infra_billing import InfraBillingRoute
from .internal_squads import InternalSquadsRoute
from .ip_control import IpControlRoute
from .metadata import MetadataRoute
from .node_plugins import NodePluginsRoute
from .nodes import NodesRoute
from .passkeys import PasskeysRoute
from .remnawave_settings import RemnawaveSettingsRoute
from .snippets import SnippetsRoute
from .stats import StatsRoute
from .system import SystemRoute
from .tokens import TokensRoute
from .subscription_page_configs import SubscriptionPageConfigsRoute
from .subscription_settings import SubscriptionSettingsRoute
from .subscription_templates import SubscriptionTemplatesRoute
from .subscriptions import SubscriptionsRoute
from .users import UsersRoute

__all__ = [
    "AuthRoute",
    "ConfigProfilesRoute",
    "ExternalSquadsRoute",
    "HostsRoute",
    "HwidRoute",
    "InfraBillingRoute",
    "InternalSquadsRoute",
    "IpControlRoute",
    "MetadataRoute",
    "NodePluginsRoute",
    "NodesRoute",
    "PasskeysRoute",
    "RemnawaveSettingsRoute",
    "SnippetsRoute",
    "StatsRoute",
    "SystemRoute",
    "TokensRoute",
    "SubscriptionPageConfigsRoute",
    "SubscriptionSettingsRoute",
    "SubscriptionTemplatesRoute",
    "SubscriptionsRoute",
    "UsersRoute",
]
