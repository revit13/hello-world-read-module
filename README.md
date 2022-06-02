# hello-world-read-module

An example of read module for Fybrik.

<!-- ## A Helm Chart for an example Fybrik module -->

## Introduction

In this repository we show how to create a read module for Fybrik. We tested the read module with a python application that launches a web server to respond to GET requests of datasets.
<!-- This helm chart defines a common structure to deploy a Kubernetes pod for an Fybrik module.
In the helm chart a service, a serviceaccount, and a deployment are defined.

The configuration for the chart is in the values file. -->

## Prerequisites

- Kubernetes cluster 1.10+
- Helm 3.7.x and above
- Install Fybrik using the [Quick Start](https://fybrik.io/dev/get-started/quickstart/) guide.
- Docker repository (such as ghcr.io).

## Installation

### code
Create a file to implement your usage of the read module. An example can be found in `hello-world-read-module.py` where you can find a python code that runs a simple web server and responds to GET requests of datasets.  

### Modify values in Makefile

In `Makefile`:
- Create a registry for helm chart and docker image. Then change the fields `DOCKER_USERNAME`, `DOCKER_PASSWORD`, `DOCKER_HOSTNAME`, `DOCKER_NAMESPACE`, `DOCKER_TAGNAME`, `DOCKER_NAME`, and `HELM_TAG` to your own preferences. An example can be found in `Makefile`.
- One possible option is to create public registries in github. Then create a Personal Access Token. In this case the field `DOCKER_USERNAME` will be your github username and `DOCKER_PASSWORD` is the Personal Access Token. Note that you need to change the visibility of the packages to public.

### Build Docker image for Python application

Create a Dockerfile to run your code that you created in a previous step. Then, run the following command to build a docker image from the Dockerfile.

```bash
make docker-build
```

### Push Docker image to your preferred container registry

Run the following command to login to the registry meant to store the docker image and to push the image to the registry.

```bash
make docker-push
```

### Configure the chart
This helm chart defines a common structure to deploy a Kubernetes pod for an Fybrik module.
In the helm chart a service, a serviceaccount, and a deployment are defined.

- The helm chart defines some Kubernetes resources depending on the values in `values.yaml`.
- Modify repository in `values.yaml` to your Docker image registry.
- At runtime, the `fybrik-manager` will pass in the values (like data location, format, and credentials) to the module so you can leave them blank in your final chart.

### Login to Helm registry

Run the following command to login to the registry meant to store the helm chart.

```bash
make helm-login
```

### Lint and install Helm chart

Run the following command to create a helm chart from the helm directory `hello-world-read-module`.

```bash
make helm-verify
```

### Push the Helm chart

Run the following command to login to your registry that intended to store the helm chart and to push the chart to the registry. Then, uninstall the helm chart.

```bash
make helm-chart-push
```


## Register as a Fybrik module

To register HWRM (Hello Read World Module) as a Fybrik module apply `hello-world-read-module.yaml` to the fybrik-system namespace of your cluster.

In order to install the latest release, run:
```bash
kubectl apply -f https://github.com/fybrik/hello-world-read-module/releases/latest/download/hello-world-read-module.yaml -n fybrik-system
```

### Version compatbility matrix

| Fybrik           | HWRM     | Command
| ---              | ---     | ---
| 0.5.x            | 0.5.x   | `https://github.com/fybrik/hello-world-read-module/releases/download/v0.5.0/hello-world-read-module.yaml`
| 0.6.x            | 0.6.x   | `https://github.com/fybrik/hello-world-read-module/releases/download/v0.6.0/hello-world-read-module.yaml`
| 0.7.x            | 0.7.x   | `https://github.com/fybrik/hello-world-read-module/releases/download/v0.7.0/hello-world-read-module.yaml`
| master           | main    | `https://raw.githubusercontent.com/fybrik/hello-world-read-module/main/hello-world-read-module.yaml`

## Deploy and test Fybrik module

Here is an example how to deploy and test the module on a single cluster.

### Before you begin

Install Fybrik using the [Quick Start](https://fybrik.io/dev/get-started/quickstart/) guide. This sample assumes the use of the built-in catalog and Open Policy Agent (OPA).

> ***Notice: Please follow `version compatbility matrix` section above for deploying the correct version of Fybrik and this module.***

### Deploy the `hello-world-read-module` module

Deploy this module in the `fybrik-system` namespace:
```bash
kubectl apply -f hello-world-read-module.yaml -n fybrik-system
```
### Test using Fybrik Notebook sample

> ***Notice: Please use the README.md file of the desired release as the resources in this example may change between releases.***

Execute the sections in [Fybrik Notebook sample](https://fybrik.io/dev/samples/notebook/) until `Register the dataset in a data catalog` section (excluded).


## Register data asset in a data catalog

You need to register your data asset in a data catalog in order for it to be used by the `fybrik-manager`.

- Follow step `Register the dataset in a data catalog` in [this example](https://fybrik.io/v0.5/samples/notebook/). These steps register the credentials required for accessing the dataset, and then register the data asset in the catalog.

- As an example you can run these commands to register two assets exist in `sample_assets`:
```bash
kubectl apply -f sample_assets/assetMedals.yaml -n fybrik-notebook-sample
kubectl apply -f sample_assets/secretMedals.yaml -n fybrik-notebook-sample
kubectl apply -f sample_assets/assetBank.yaml -n fybrik-notebook-sample
kubectl apply -f sample_assets/secretBank.yaml -n fybrik-notebook-sample
```

### Define data access policies

  Define the following [OpenPolicyAgent](https://www.openpolicyagent.org/) policy to allow the write operation:

```bash
package dataapi.authz

rule[{"action": {"name":"RedactAction", "columns": column_names}, "policy": description}] {
  description := "Redact columns tagged as PII in datasets tagged with finance = true"
  input.action.actionType == "read"
  input.resource.metadata.tags.finance
  column_names := [input.resource.metadata.columns[i].name | input.resource.metadata.columns[i].tags.PII]
  count(column_names) > 0
}

rule[{"action": {"name":"RedactAction", "columns": column_names}, "policy": description}] {
  description := "Redact columns tagged as sensitive in datasets tagged with finance = true"
  input.action.actionType == "read"
  input.resource.metadata.tags.finance
  column_names := [input.resource.metadata.columns[i].name | input.resource.metadata.columns[i].tags.sensitive]
  count(column_names) > 0
}
```

  Copy the policies to a file named sample-policy.rego and then run:

```bash
kubectl -n fybrik-system create configmap sample-policy --from-file=sample-policy.rego
kubectl -n fybrik-system label configmap sample-policy openpolicyagent.org/policy=rego
while [[ $(kubectl get cm sample-policy -n fybrik-system -o 'jsonpath={.metadata.annotations.openpolicyagent\.org/policy-status}') != '{"status":"ok"}' ]]; do echo "waiting for policy to be applied" && sleep 5; done
```

### Deploy Fybrik application which triggers module
Deploy `FybrikApplication` in `default` namespace:
```bash
kubectl apply -f fybrikapplication.yaml -n default
```
3.  Run the following command to wait until the `status` of the `FybrikApplication` is `ready`:
```bash
while [[ $(kubectl get fybrikapplication my-notebook -n default -o 'jsonpath={.status.ready}') != "true" ]]; do echo "waiting for FybrikApplication" && sleep 5; done
```

4.  Check if module was triggered in `fybrik-blueprints`:
```bash
kubectl get blueprint -n fybrik-system
kubectl describe blueprint my-notebook-default -n fybrik-system
kubectl get job -n fybrik-blueprints
kubectl get pods -n fybrik-blueprints
```

If you are using the `hello-world-read-module` image, you should see this in the `kubectl logs -n fybrik-blueprints` of your completed Pod:
```
$ kubectl logs my-notebook-default-hello-world-read-module-xx -n fybrik-blueprints

INFO:root:
Hello World Read Module!
INFO:root:The avialable datasets:

INFO:root:dataset name: medals-winners

INFO:root:    format: csv

INFO:root:    endpoint_url: http://winterolympicsmedals.com/medals.csv

INFO:root:    action: Redact

INFO:root:    transferred_columns: ['age']

INFO:root:dataset name: bank

INFO:root:    format: csv

INFO:root:    endpoint_url: https://raw.githubusercontent.com/juliencohensolal/BankMarketing/master/rawData/bank-additional-full.csv

INFO:root:    action: Redact

INFO:root:    transferred_columns: ['age']

INFO:root:Starting httpd server on localhost:8000

```

## Clean

Run the following command to delete the fybrik application:
```bash
kubectl delete FybrikApplication my-notebook -n default
```

Run the following command to delete the fybrik module:
```bash
kubectl delete fybrikmodule hello-world-read-module -n fybrik-system
```

Please execute the `Cleanup` section from [Fybrik notebook sample](https://fybrik.io/dev/samples/notebook/)
