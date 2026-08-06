from typing import Any

from ..enums import (
    HostAlpn,
    HostMihomoIpVersion,
    HostSecurityLayer,
    SubscriptionTemplateType,
)
from ..models.common import DeletedResult, TagsResult, UpdatedResult
from ..models.envelope import Envelope
from ..models.hosts import Host
from .base import BaseRoute, pack


def _add_inbound(
    body: dict[str, Any],
    config_profile_uuid: str | None,
    config_profile_inbound_uuid: str | None,
) -> None:
    if config_profile_uuid is None and config_profile_inbound_uuid is None:
        return
    if config_profile_uuid is None or config_profile_inbound_uuid is None:
        raise ValueError("config_profile_uuid and config_profile_inbound_uuid must be passed together")
    body["inbound"] = {
        "configProfileUuid": config_profile_uuid,
        "configProfileInboundUuid": config_profile_inbound_uuid,
    }


def _host_fields(
    *,
    remark: str | None = None,
    address: str | None = None,
    port: int | None = None,
    path: str | None = None,
    sni: str | None = None,
    host: str | None = None,
    alpn: HostAlpn | str | None = None,
    fingerprint: str | None = None,
    is_disabled: bool | None = None,
    security_layer: HostSecurityLayer | str | None = None,
    xhttp_extra_params: Any | None = None,
    mux_params: Any | None = None,
    sockopt_params: Any | None = None,
    final_mask: Any | None = None,
    server_description: str | None = None,
    tags: list[str] | None = None,
    is_hidden: bool | None = None,
    override_sni_from_address: bool | None = None,
    keep_sni_blank: bool | None = None,
    vless_route_id: int | None = None,
    pinned_peer_cert_sha256: str | None = None,
    verify_peer_cert_by_name: str | None = None,
    shuffle_host: bool | None = None,
    mihomo_x25519: bool | None = None,
    mihomo_ip_version: HostMihomoIpVersion | str | None = None,
    nodes: list[str] | None = None,
    xray_json_template_uuid: str | None = None,
    excluded_internal_squads: list[str] | None = None,
    exclude_from_subscription_types: list[SubscriptionTemplateType | str] | None = None,
) -> dict[str, Any]:
    return pack(
        remark=remark,
        address=address,
        port=port,
        path=path,
        sni=sni,
        host=host,
        alpn=alpn,
        fingerprint=fingerprint,
        is_disabled=is_disabled,
        security_layer=security_layer,
        xhttp_extra_params=xhttp_extra_params,
        mux_params=mux_params,
        sockopt_params=sockopt_params,
        final_mask=final_mask,
        server_description=server_description,
        tags=tags,
        is_hidden=is_hidden,
        override_sni_from_address=override_sni_from_address,
        keep_sni_blank=keep_sni_blank,
        vless_route_id=vless_route_id,
        pinned_peer_cert_sha256=pinned_peer_cert_sha256,
        verify_peer_cert_by_name=verify_peer_cert_by_name,
        shuffle_host=shuffle_host,
        mihomo_x25519=mihomo_x25519,
        mihomo_ip_version=mihomo_ip_version,
        nodes=nodes,
        xray_json_template_uuid=xray_json_template_uuid,
        excluded_internal_squads=excluded_internal_squads,
        exclude_from_subscription_types=exclude_from_subscription_types,
    )


class HostsRoute(BaseRoute):
    """``/api/hosts`` endpoints, mounted at ``RemnawaveClient.hosts``"""

    async def create_host(
        self,
        remark: str,
        address: str,
        port: int,
        config_profile_uuid: str,
        config_profile_inbound_uuid: str,
        *,
        path: str | None = None,
        sni: str | None = None,
        host: str | None = None,
        alpn: HostAlpn | str | None = None,
        fingerprint: str | None = None,
        is_disabled: bool | None = None,
        security_layer: HostSecurityLayer | str | None = None,
        xhttp_extra_params: Any | None = None,
        mux_params: Any | None = None,
        sockopt_params: Any | None = None,
        final_mask: Any | None = None,
        server_description: str | None = None,
        tags: list[str] | None = None,
        is_hidden: bool | None = None,
        override_sni_from_address: bool | None = None,
        keep_sni_blank: bool | None = None,
        vless_route_id: int | None = None,
        pinned_peer_cert_sha256: str | None = None,
        verify_peer_cert_by_name: str | None = None,
        shuffle_host: bool | None = None,
        mihomo_x25519: bool | None = None,
        mihomo_ip_version: HostMihomoIpVersion | str | None = None,
        nodes: list[str] | None = None,
        xray_json_template_uuid: str | None = None,
        excluded_internal_squads: list[str] | None = None,
        exclude_from_subscription_types: list[SubscriptionTemplateType | str] | None = None,
    ) -> Host:
        """Create a new host (POST /api/hosts)"""
        body = _host_fields(
            remark=remark, address=address, port=port, path=path, sni=sni,
            host=host, alpn=alpn, fingerprint=fingerprint, is_disabled=is_disabled,
            security_layer=security_layer, xhttp_extra_params=xhttp_extra_params,
            mux_params=mux_params, sockopt_params=sockopt_params, final_mask=final_mask,
            server_description=server_description, tags=tags, is_hidden=is_hidden,
            override_sni_from_address=override_sni_from_address, keep_sni_blank=keep_sni_blank,
            vless_route_id=vless_route_id, pinned_peer_cert_sha256=pinned_peer_cert_sha256,
            verify_peer_cert_by_name=verify_peer_cert_by_name, shuffle_host=shuffle_host,
            mihomo_x25519=mihomo_x25519, mihomo_ip_version=mihomo_ip_version,
            nodes=nodes, xray_json_template_uuid=xray_json_template_uuid,
            excluded_internal_squads=excluded_internal_squads,
            exclude_from_subscription_types=exclude_from_subscription_types,
        )
        _add_inbound(body, config_profile_uuid, config_profile_inbound_uuid)
        envelope: Envelope[Host] = await self._client.request(
            "POST", "/api/hosts",
            body=body, response_type=Envelope[Host],
        )
        return envelope.response

    async def get_hosts(self) -> list[Host]:
        """List every host (GET /api/hosts)"""
        envelope: Envelope[list[Host]] = await self._client.request(
            "GET", "/api/hosts",
            response_type=Envelope[list[Host]],
        )
        return envelope.response

    async def update_host(
        self,
        uuid: str,
        *,
        config_profile_uuid: str | None = None,
        config_profile_inbound_uuid: str | None = None,
        remark: str | None = None,
        address: str | None = None,
        port: int | None = None,
        path: str | None = None,
        sni: str | None = None,
        host: str | None = None,
        alpn: HostAlpn | str | None = None,
        fingerprint: str | None = None,
        is_disabled: bool | None = None,
        security_layer: HostSecurityLayer | str | None = None,
        xhttp_extra_params: Any | None = None,
        mux_params: Any | None = None,
        sockopt_params: Any | None = None,
        final_mask: Any | None = None,
        server_description: str | None = None,
        tags: list[str] | None = None,
        is_hidden: bool | None = None,
        override_sni_from_address: bool | None = None,
        keep_sni_blank: bool | None = None,
        vless_route_id: int | None = None,
        pinned_peer_cert_sha256: str | None = None,
        verify_peer_cert_by_name: str | None = None,
        shuffle_host: bool | None = None,
        mihomo_x25519: bool | None = None,
        mihomo_ip_version: HostMihomoIpVersion | str | None = None,
        nodes: list[str] | None = None,
        xray_json_template_uuid: str | None = None,
        excluded_internal_squads: list[str] | None = None,
        exclude_from_subscription_types: list[SubscriptionTemplateType | str] | None = None,
    ) -> Host:
        """Patch an existing host by uuid (PATCH /api/hosts)"""
        body = _host_fields(
            remark=remark, address=address, port=port, path=path, sni=sni,
            host=host, alpn=alpn, fingerprint=fingerprint, is_disabled=is_disabled,
            security_layer=security_layer, xhttp_extra_params=xhttp_extra_params,
            mux_params=mux_params, sockopt_params=sockopt_params, final_mask=final_mask,
            server_description=server_description, tags=tags, is_hidden=is_hidden,
            override_sni_from_address=override_sni_from_address, keep_sni_blank=keep_sni_blank,
            vless_route_id=vless_route_id, pinned_peer_cert_sha256=pinned_peer_cert_sha256,
            verify_peer_cert_by_name=verify_peer_cert_by_name, shuffle_host=shuffle_host,
            mihomo_x25519=mihomo_x25519, mihomo_ip_version=mihomo_ip_version,
            nodes=nodes, xray_json_template_uuid=xray_json_template_uuid,
            excluded_internal_squads=excluded_internal_squads,
            exclude_from_subscription_types=exclude_from_subscription_types,
        )
        body["uuid"] = uuid
        _add_inbound(body, config_profile_uuid, config_profile_inbound_uuid)
        envelope: Envelope[Host] = await self._client.request(
            "PATCH", "/api/hosts",
            body=body, response_type=Envelope[Host],
        )
        return envelope.response

    async def get_host_by_uuid(self, uuid: str) -> Host:
        """Fetch a single host (GET /api/hosts/{uuid})"""
        envelope: Envelope[Host] = await self._client.request(
            "GET", f"/api/hosts/{uuid}",
            response_type=Envelope[Host],
        )
        return envelope.response

    async def delete_host(self, uuid: str) -> bool:
        """Delete a host (DELETE /api/hosts/{uuid})"""
        envelope: Envelope[DeletedResult] = await self._client.request(
            "DELETE", f"/api/hosts/{uuid}",
            response_type=Envelope[DeletedResult],
        )
        return envelope.response.is_deleted

    async def reorder_hosts(self, order: dict[str, int]) -> bool:
        """Reorder hosts in the panel (POST /api/hosts/actions/reorder)"""
        body = {
            "hosts": [
                {"uuid": host_uuid, "viewPosition": position}
                for host_uuid, position in order.items()
            ]
        }
        envelope: Envelope[UpdatedResult] = await self._client.request(
            "POST", "/api/hosts/actions/reorder",
            body=body, response_type=Envelope[UpdatedResult],
        )
        return envelope.response.is_updated

    async def get_all_tags(self) -> list[str]:
        """List every tag in use across all hosts (GET /api/hosts/tags)"""
        envelope: Envelope[TagsResult] = await self._client.request(
            "GET", "/api/hosts/tags",
            response_type=Envelope[TagsResult],
        )
        return envelope.response.tags

    async def bulk_delete_hosts(self, uuids: list[str]) -> list[Host]:
        """Delete many hosts (POST /api/hosts/bulk/delete)"""
        envelope: Envelope[list[Host]] = await self._client.request(
            "POST", "/api/hosts/bulk/delete",
            body={"uuids": uuids}, response_type=Envelope[list[Host]],
        )
        return envelope.response

    async def bulk_disable_hosts(self, uuids: list[str]) -> list[Host]:
        """Disable many hosts (POST /api/hosts/bulk/disable)"""
        envelope: Envelope[list[Host]] = await self._client.request(
            "POST", "/api/hosts/bulk/disable",
            body={"uuids": uuids}, response_type=Envelope[list[Host]],
        )
        return envelope.response

    async def bulk_enable_hosts(self, uuids: list[str]) -> list[Host]:
        """Enable many hosts (POST /api/hosts/bulk/enable)"""
        envelope: Envelope[list[Host]] = await self._client.request(
            "POST", "/api/hosts/bulk/enable",
            body={"uuids": uuids}, response_type=Envelope[list[Host]],
        )
        return envelope.response

    async def bulk_update_hosts(
        self,
        uuids: list[str],
        *,
        config_profile_uuid: str | None = None,
        config_profile_inbound_uuid: str | None = None,
        remark: str | None = None,
        address: str | None = None,
        port: int | None = None,
        path: str | None = None,
        sni: str | None = None,
        host: str | None = None,
        alpn: HostAlpn | str | None = None,
        fingerprint: str | None = None,
        is_disabled: bool | None = None,
        security_layer: HostSecurityLayer | str | None = None,
        xhttp_extra_params: Any | None = None,
        mux_params: Any | None = None,
        sockopt_params: Any | None = None,
        final_mask: Any | None = None,
        server_description: str | None = None,
        tags: list[str] | None = None,
        is_hidden: bool | None = None,
        override_sni_from_address: bool | None = None,
        keep_sni_blank: bool | None = None,
        vless_route_id: int | None = None,
        pinned_peer_cert_sha256: str | None = None,
        verify_peer_cert_by_name: str | None = None,
        shuffle_host: bool | None = None,
        mihomo_x25519: bool | None = None,
        mihomo_ip_version: HostMihomoIpVersion | str | None = None,
        nodes: list[str] | None = None,
        xray_json_template_uuid: str | None = None,
        excluded_internal_squads: list[str] | None = None,
        exclude_from_subscription_types: list[SubscriptionTemplateType | str] | None = None,
    ) -> list[Host]:
        """Patch the same fields on many hosts (PATCH /api/hosts/bulk/update)"""
        body = _host_fields(
            remark=remark, address=address, port=port, path=path, sni=sni,
            host=host, alpn=alpn, fingerprint=fingerprint, is_disabled=is_disabled,
            security_layer=security_layer, xhttp_extra_params=xhttp_extra_params,
            mux_params=mux_params, sockopt_params=sockopt_params, final_mask=final_mask,
            server_description=server_description, tags=tags, is_hidden=is_hidden,
            override_sni_from_address=override_sni_from_address, keep_sni_blank=keep_sni_blank,
            vless_route_id=vless_route_id, pinned_peer_cert_sha256=pinned_peer_cert_sha256,
            verify_peer_cert_by_name=verify_peer_cert_by_name, shuffle_host=shuffle_host,
            mihomo_x25519=mihomo_x25519, mihomo_ip_version=mihomo_ip_version,
            nodes=nodes, xray_json_template_uuid=xray_json_template_uuid,
            excluded_internal_squads=excluded_internal_squads,
            exclude_from_subscription_types=exclude_from_subscription_types,
        )
        body["uuids"] = uuids
        _add_inbound(body, config_profile_uuid, config_profile_inbound_uuid)
        envelope: Envelope[list[Host]] = await self._client.request(
            "PATCH", "/api/hosts/bulk/update",
            body=body, response_type=Envelope[list[Host]],
        )
        return envelope.response
