from .auth import AuthRoute
from .external_squads import ExternalSquadsRoute
from .hosts import HostsRoute
from .hwid import HwidRoute
from .internal_squads import InternalSquadsRoute
from .nodes import NodesRoute
from .passkeys import PasskeysRoute
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
    "ExternalSquadsRoute",
    "HostsRoute",
    "HwidRoute",
    "InternalSquadsRoute",
    "NodesRoute",
    "PasskeysRoute",
    "StatsRoute",
    "SystemRoute",
    "TokensRoute",
    "SubscriptionPageConfigsRoute",
    "SubscriptionSettingsRoute",
    "SubscriptionTemplatesRoute",
    "SubscriptionsRoute",
    "UsersRoute",
]
