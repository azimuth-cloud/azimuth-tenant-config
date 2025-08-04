# Standalone Quickstart 

This guide assumes that Azimuth is running in [Standalone mode](https://github.com/azimuth-cloud/azimuth-config/blob/feat/existing-k8s-support/docs/configuration/17-standalone-mode.md)
and that you wish to manage the initial admin users for tenancies through this
repository.

Install the required dependencies:
  * [kubectl](https://kubernetes.io/docs/reference/kubectl/)
  * [Flux CLI](https://fluxcd.io/flux/cmd/)
  * [kubeseal](https://github.com/bitnami-labs/sealed-secrets?tab=readme-ov-file#kubeseal)

Create a detached fork of this repo
```sh
# Clone the repository
git clone \
  https://github.com/azimuth-cloud/azimuth-tenant-config.git \
  my-azimuth-tenant-config
cd my-azimuth-tenant-config

# Rename the origin remote to upstream so that we can pull changes in future
git remote rename origin upstream

# Add the new origin remote and push the initial commit
git remote add origin <repourl>
git push -u origin main
```

Create tenancies by running
```sh
./bin/bootstrap.py \
--name <tenancy-name> \
--type kubeconfig \
--cred-file <path-to-tenant-kubeconfig> \
--azimuth-kubeconfig <path-to-azimuth-kubeconfig> \
--git-remote-url <repo-url>
```
where `path-to-tenant-kubeconfig` is the path to the kubeconfig for the K8s cluster
you wish to target with the tenancy, `path-to-azimuth-kubeconfig` is the path to the
K8s cluster on which Azimuth is hosted and `repo-url` is the HTTPS URL of your forked
copy of this repo. If your Azimuth is hosted on a k3s cluster which was installed with by
`deploy_standalone` playbook in Azimuth config rather than an existing cluster, Azimuth's
kubeconfig can be extracted from `~/.kube/config` on the host it's running on. Note that this
kubeconfig points to a localhost address on the VM, so to be able to access Azimuth's K8s
cluster, you will need to do one of the following options:
  * Proxy the VM when running the bootstrap script
  * Expose the K8s API port on the VM and set the `server` field of your local copy of the kubeconfig
    to target the VM's IP address
  * Clone this repo on the VM

Uncomment the `./users` in the top level kustomization.yaml file

Create an initial admin user for the tenancy by running
```sh
./bin/create-admin.py \
--tenancy <tenancy-name> \
--oidc-admin-username <arbitrary-username> \
--oidc-admin-username <federated-auth-email>
```
where `federated-auth-email` is the email address used to login to your configured OIDC
provider (e.g the email address of your GitHub account if the GitHub provider is configured, as described in the
[Standalone mode](https://github.com/azimuth-cloud/azimuth-config/blob/feat/existing-k8s-support/docs/configuration/17-standalone-mode.md) docs)

Commit and push the changes to your repo.
