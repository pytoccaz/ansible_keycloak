# Ansible Collection - pytoccaz.keycloak

A module to retrieve auth token for Keycloak API


<!--start requires_ansible-->
## Ansible version compatibility

This collection has been tested against following Ansible versions: **>=2.13.13**.

<!--end requires_ansible-->

## Installation

Download from Galaxy:

```bash
ansible-galaxy collection install pytoccaz.keycloak
```

<!--start collection content-->
### Modules
Name | Description
--- | ---
[pytoccaz.keycloak.kc_get_token](https://github.com/pytoccaz/ansible_keycloak/blob/main/docs/pytoccaz.keycloak.kc_get_token_module.rst)|Retrieves auth token for Keycloak API

<!--end collection content-->


## Credits
This program is inspired by and contains code snippets from:
- `community.general.plugins.module_utils.identity.keycloak.keycloak` module by Eike Frost
- `community.general.plugins.module_utils.identity.keycloak.keycloak_clientsecret` module by John Cant
- `community.general.plugins.modules.keycloak_clientsecret_info` module by Fynn Chen

It also contains documentation fragments from `community.general.doc_fragments.keycloak` by Eike Frost.
