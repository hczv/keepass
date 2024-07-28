# Structure

keepass_psw: test_password

## Host specific entries

```yaml
[ansible_keepass]/General
  - title: host_entry_default
    username: my_host_user
    password: my_host_password
    custom_fields: 
      - host: 
            host.subdomain.domain.tld
            host2.subdomain.domain.tld
            host3.subdomain.domain.tld

[ansible_keepass]/General
  - title: host_entry_duplicate_match_1
    username: my_host_user
    password: my_host_password
    custom_fields: 
      - host: my_duplicated_host.subdomain.domain.tld

[ansible_keepass]/General
  - title: host_entry_duplicate_match_2
    username: my_host_user
    password: my_host_password
    custom_fields: 
      - host: my_duplicated_host.subdomain.domain.tld

```

## domain specific entries

```yaml

[ansible_keepass]/General
  - title: domain_entry_default
    username: my_domain_user
    password: my_domain_password
    custom_fields: 
      - domain: 
            subdomain.domain.tld
            subdomain2.domain.tld
            subdomain3.domain.tld

[ansible_keepass]/General
  - title: domain_entry_duplicate_match_1
    username: my_domain_user
    password: my_domain_password
    custom_fields: 
      - domain: my_duplicated_subdomain.domain.tld

[ansible_keepass]/General
  - title: domain_entry_duplicate_match_2
    username: my_domain_user
    password: my_domain_password
    custom_fields: 
      - domain: my_duplicated_subdomain.domain.tld
```

## url specific entries

```yaml

[ansible_keepass]/General
  - title: url_entry_default
    username: my_url_user
    password: my_url_password
    url: host_url.subdomain.domain.tld

[ansible_keepass]/General
  - title: url_entry_wrong_protocol
    username: my_url_user
    password: my_url_password
    url: https://host_url.subdomain.domain.tld

[ansible_keepass]/General
  - title: url_entry_duplicate_match_1
    username: my_url_user
    password: my_url_password
    url: my_duplicated_host_url.subdomain.domain.tld

[ansible_keepass]/General
  - title: url_entry_duplicate_match_2
    username: my_url_user
    password: my_url_password
    url: my_duplicated_host_url.subdomain.domain.tld

```

## General entries for logic handeling

```yaml
[ansible_keepass]/General
  - title: host_entry_empty_username
    username: 
    password: my_host_password
    custom_fields: 
      - host: host_empty_username.subdomain.domain.tld

[ansible_keepass]/General
  - title: host_entry_empty_password
    username: my_host_user
    password: 
    custom_fields: 
      - host: host_empty_password.subdomain.domain.tld

[ansible_keepass]/General
  - title: host_entry_reference_username_password
    username: {REF:U@I:D37C580DA0746E44A87750DFCBDFE477} # reference to username in host_entry_default
    password: {REF:P@I:D37C580DA0746E44A87750DFCBDFE477} # reference to password in host_entry_default
    custom_fields: 
      - host: host_reference.subdomain.domain.tld
```

