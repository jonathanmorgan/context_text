# Notes:

- must update:

    - hosts.yaml

        - need to update to match the particular layout of servers you intend to use.
        - Note: more complex configurations will require manual configuration beyond what these scripts provide.

    - /host_vars

        - each host needs a 
        - use the `research.local` file as a template for variables related to each of your hosts.
        - This includes:

            - 

    - vault password(s)

        - if you want to encrypt either files or variable values within yml files, you'll need to have one or more vault passwords to use as the symmetric encryption key.
        - if you need your deployment to run unattended, you'll want to create one or more files for your vault passwords, then direct the ansible-playbook command to them when you deploy.

            - these can be located wherever you want.

    - ansible config:

        - one way to store a single vault password is to store its location in ansible config, in  `vault_password_file`.
        - default locations:

            - /etc/ansible/ansible.cfg
            - ~/.ansible.cfg