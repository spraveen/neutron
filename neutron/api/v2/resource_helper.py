# (c) Copyright 2014 Cisco Systems Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
# @author: Paul Michali Cisco Systems, Inc.

from oslo.config import cfg

from neutron.api import extensions
from neutron.api.v2 import base
from neutron import manager
from neutron.plugins.common import constants
from neutron import quota


def build_plural_mappings(special_mappings, resource_map):
    """Create plural to singular mapping for all resources.

    Allows for special mappings to be provided, like policies -> policy.
    Otherwise, will strip off the last character for normal mappings, like
    routers -> router.
    """
    plural_mappings = {}
    for plural in resource_map:
        singular = special_mappings.get(plural, plural[:-1])
        plural_mappings[plural] = singular
    return plural_mappings


def build_resource_info(plural_mappings, resource_map, which_service,
                        action_map=None, register_quota=False,
                        translate_name=False, allow_bulk=False):
    """Build resources for advanced services.

    Takes the resource information, and singular/plural mappings, and creates
    API resource objects for advanced services extensions. Will optionally
    translate underscores to dashes in resource names, register the resource,
    and accept action information for resources.
    """
    resources = []
    if action_map is None:
        action_map = {}
    plugin = manager.NeutronManager.get_service_plugins()[which_service]
    for collection_name in resource_map:
        resource_name = plural_mappings[collection_name]
        params = resource_map.get(collection_name, {})
        if translate_name:
            collection_name = collection_name.replace('_', '-')
        if register_quota:
            quota.QUOTAS.register_resource_by_name(resource_name)
        member_actions = action_map.get(resource_name, {})
        controller = base.create_resource(
            collection_name, resource_name, plugin, params,
            member_actions=member_actions,
            allow_bulk=allow_bulk,
            allow_pagination=cfg.CONF.allow_pagination,
            allow_sorting=cfg.CONF.allow_sorting)
        resource = extensions.ResourceExtension(
            collection_name,
            controller,
            path_prefix=constants.COMMON_PREFIXES[which_service],
            member_actions=member_actions,
            attr_map=params)
        resources.append(resource)
    return resources
