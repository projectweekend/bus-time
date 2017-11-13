## Deploy to Raspberry Pi with Ansible

* Bus stop config is managed using a vars file: `playbooks/group_vars/bus_stops.yaml`
* Global secrets are managed using Ansible Vault: `playbooks/host_vars/penelopi.local`

```bash
$ cd playbooks/
$ ansible-playbook raspberrypi.yaml
```
