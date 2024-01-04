#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2024 Olivier Bernard (@pytoccaz)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# This program is inspired by and contains code snippets from:
# - `community.general.plugins.module_utils.identity.keycloak.keycloak` module by Eike Frost
# - `community.general.plugins.module_utils.identity.keycloak.keycloak_clientsecret` module by John Cant
# - `community.general.plugins.modules.keycloak_clientsecret_info` module by Fynn Chen
# It also contains documentation fragments from `community.general.doc_fragments.keycloak` by Eike Frost.

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = '''
---
module: get_token

short_description: Retrieves auth token for Keycloak API

version_added: 1.0.0

description:
  - This module allows you to get a Keycloak Authentication Token via the Keycloak
    REST API (OpenID Connect); the user
    connecting and the client being used must have the requisite access rights.
    In a default Keycloak installation, admin-cli and an admin user would work,
    as would a separate client definition with the scope tailored to your needs
    and a user having the expected roles.

  - "Note that this module returns a secret token. To avoid this showing up in the logs,
     please add C(no_log: true) to the task."

options:
    auth_keycloak_url:
        description:
            - URL to the Keycloak instance.
        type: str
        required: true
        aliases:
          - url

    auth_client_id:
        description:
            - OpenID Connect C(client_id) to authenticate to the API with.
        type: str
        default: admin-cli

    auth_realm:
        description:
            - Keycloak realm name to authenticate to for API access.
        type: str

    auth_username:
        description:
            - Username to authenticate for API access with.
        type: str
        aliases:
          - username

    auth_password:
        description:
            - Password to authenticate for API access with.
        type: str
        aliases:
          - password

    validate_certs:
        description:
            - Verify TLS certificates (do not disable this in production).
        type: bool
        default: true

    connection_timeout:
        description:
            - Controls the HTTP connections timeout period (in seconds) to Keycloak API.
        type: int
        default: 10

    http_agent:
        description:
            - Configures the HTTP User-Agent header.
        type: str
        default: Ansible


author:
  - Olivier Bernard (@pytoccaz)
'''

EXAMPLES = '''
- name: Get a Keycloak token
  pytoccaz.keycloak.get_token:
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
  delegate_to: localhost
  no_log: true
'''

RETURN = '''
token:
  description: the token value
  returned: on success
  type: str
  sample: cUGnX1EIeTtPPAkcyGMv0ncyqDPu68P1
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native
from ansible.module_utils.six.moves.urllib.parse import urlencode
from ansible.module_utils.urls import open_url
import json


URL_TOKEN = "{url}/realms/{realm}/protocol/openid-connect/token"


def keycloak_argument_spec():
    """
    Returns argument_spec of options common to keycloak_*-modules

    :return: argument_spec dict
    """
    return dict(
        auth_keycloak_url=dict(type='str', aliases=[
                               'url'], required=True, no_log=False),
        auth_client_id=dict(type='str', default='admin-cli'),
        auth_realm=dict(type='str'),
        auth_username=dict(type='str', aliases=['username']),
        auth_password=dict(type='str', aliases=['password'], no_log=True),
        validate_certs=dict(type='bool', default=True),
        connection_timeout=dict(type='int', default=10),
        http_agent=dict(type='str', default='Ansible'),
    )


class KeycloakError(Exception):
    pass


def get_token(module_params):
    """ Obtains a token for the authentication,
        :param module_params: parameters of the module
        :return: token
    """
    base_url = module_params.get('auth_keycloak_url')
    http_agent = module_params.get('http_agent')

    if not base_url.lower().startswith(('http', 'https')):
        raise KeycloakError(
            "auth_url '%s' should either start with 'http' or 'https'." % base_url)

    base_url = module_params.get('auth_keycloak_url')
    validate_certs = module_params.get('validate_certs')
    auth_realm = module_params.get('auth_realm')
    client_id = module_params.get('auth_client_id')
    auth_username = module_params.get('auth_username')
    auth_password = module_params.get('auth_password')
    connection_timeout = module_params.get('connection_timeout')
    auth_url = URL_TOKEN.format(url=base_url, realm=auth_realm)
    temp_payload = {
        'grant_type': 'password',
        'client_id': client_id,
        'username': auth_username,
        'password': auth_password,
    }
    # Remove empty items
    payload = dict(
        (k, v) for k, v in temp_payload.items() if v is not None)
    try:
        r = json.loads(to_native(open_url(auth_url, method='POST',
                                          validate_certs=validate_certs, http_agent=http_agent, timeout=connection_timeout,
                                          data=urlencode(payload)).read()))
    except ValueError as e:
        raise KeycloakError(
            'API returned invalid JSON when trying to obtain access token from %s: %s'
            % (auth_url, str(e)))
    except Exception as e:
        raise KeycloakError('Could not obtain access token from %s: %s'
                            % (auth_url, str(e)))

    try:
        token = r['access_token']
    except KeyError:
        raise KeycloakError(
            'Could not obtain access token from %s' % auth_url)
    return token


def main():
    """
    Module get_token
    """

    argument_spec = keycloak_argument_spec()

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=([['auth_realm', 'auth_username', 'auth_password']]),
        required_together=([['auth_realm', 'auth_username', 'auth_password']]),
    )

    # Obtain access token, initialize API
    try:
        token = get_token(module.params)
    except KeycloakError as e:
        module.fail_json(msg=str(e))

    result = {
        'token': token,
    }

    module.exit_json(**result)


if __name__ == '__main__':
    main()
