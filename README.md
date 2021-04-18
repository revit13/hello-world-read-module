# hello-world-read-module

## A Helm Chart for an example Mesh for Data module

## Introduction

This helm chart defines a common structure to deploy a Kubernetes pod for an M4D module.
In the helm chart a service, a serviceaccount, and a deployment are defined.

The configuration for the chart is in the values file.

## Prerequisites

- Kubernetes cluster 1.10+
- Helm 3.0.0+
- Install Mesh for Data using the Quick Start guide.

## Installation

### code
Create a file to implement your usage of the read module. An example can be found in `hello-world-read-module.py` where you can find python code to print 
some information about the used dataset and then run a simple web server.  

### Modify values in Makefile

In `Makefile`:
- Create a registry for helm chart and docker image. Then change the fields `DOCKER_USERNAME`, `DOCKER_PASSWORD`, `DOCKER_HOSTNAME`, `DOCKER_NAMESPACE`, `DOCKER_TAGNAME`, `DOCKER_IMG_NAME`, and `DOCKER_CHART_IMG_NAME` to your own preferences. An exapmle can be found in `Makefile`.

### Build Docker image for Python application

Create a Dockerfile to run your code that created in a previous step. Then, run the following command to build a docker image from the Dockerfile.

```bash
make docker-build
```

### Push Docker image to your preferred container registry

Run the following command to login to your registry that intended to store the docker image and to push the image to the registry.

```bash
make docker-push
```

### Configure the chart
- The helm chart defines some Kubernetes resources depending on the values in `values.yaml`. These resources are used to deploy a Kubernetes pod for an M4D module.
- Modify repository in `values.yaml` to your Docker image registry. 
- Modify read action as needed with appropriate values.
- At runtime, the `m4d-manager` will pass in the read values to the module so you can leave them blank in your final chart. 

### Login to Helm registry

Run the following command to login to your registry that intended to store the helm chart.

```bash
make helm-login
```

### Lint and install Helm chart

Run the following command to create a helm chart from the helm directory `hello-world-read-module`.

```bash
make helm-verify
```

### Push the Helm chart

Run the following command to login to your registry that intended to store the helm chart and to push the chart to the registry.

```bash
make helm-chart-push
```

## Uninstallation

After pushing the chart to registry, it is possible to uninstall the helm chart.

```bash
make helm-uninstall
```

## Deploy M4D module
1. In your module yaml spec (`hello-world-module.yaml`):
    - Change `spec.chart.name` to your chart registry.
    - Define `flows` and `capabilities` for your module, an exapmle can be found in `hello-world-module.yaml`. 

2. Deploy `M4DModule` in `m4d-system` namespace:
```bash
kubectl create -f hello-world-read-module.yaml -n m4d-system
```

## Register data asset in a data catalog

A registeration of your data asset in a data catalog is needed in order to use it by the `m4d-manager`.

- Follow step `Register the dataset in a data catalog` in [this example]() to register the credentials required for accessing the dataset. Then, to register the data asset in the catalog.


## Deploy cluster metadata
Run the following command to install a configmap cluster-metadata in `m4d-system` namespace.
```bash
kubectl create -f cluster-metadata.yaml -n m4d-system
```

## Deploy M4D application which triggers module
1. In `m4dapplication.yaml`:
    - Change `metadata.name` to your application name.
    - Define `appInfo.purpose`, `appInfo.role`, and `spec.data`.
    - Change `data.dataSetID` field to the identifier of the asset in the catalog which is in the format `<namespace>/<name>`.
 
2.  Deploy `M4DApplication` in `default` namespace:
```bash
kubectl apply -f m4dapplication.yaml -n default
```
3.  Check if `M4DApplication` successfully deployed:
```bash
kubectl get m4dapplication -n default
kubectl describe M4DApplication hello-world-read-module-test -n default
```

4.  Check if module was triggered in `m4d-blueprints`:
```bash
kubectl get blueprint -n m4d-blueprints
kubectl describe blueprint hello-world-read-module-test-default -n m4d-blueprints
kubectl get pods -n m4d-blueprints
```
If you are using the existing `hello-world-read-module.py`, you should see this in the `kubectl logs` of the `m4d-blueprint` Pod:
```
$ kubectl logs hello-world-read-module-test-default-hello-worl-0ff24-94ff7t46d -n m4d-blueprints

INFO:root:
Hello World Read Module!
INFO:root:
name is default/data-csv
INFO:root:
Connection format is csv
INFO:root:
S3 bucket is cloud-object-storage-l4-cos-standard-7vz
INFO:root:
S3 endpoint is s3.eu.cloud-object-storage.appdomain.cloud
INFO:root:
url is http://www.google.com
INFO:root:
READ SUCCEEDED
INFO:root:Starting httpd server on localhost:8000
```

