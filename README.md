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
- Helm 3.0.0+
- Install Fybrik using the [Quick Start](https://fybrik.io/dev/get-started/quickstart/) guide.
- Docker repository (such as ghcr.io).

## Installation

### code
Create a file to implement your usage of the read module. An example can be found in `hello-world-read-module.py` where you can find a python code that runs a simple web server and responds to GET requests of datasets.  

### Modify values in Makefile

In `Makefile`:
- Create a registry for helm chart and docker image. Then change the fields `DOCKER_USERNAME`, `DOCKER_PASSWORD`, `DOCKER_HOSTNAME`, `DOCKER_NAMESPACE`, `DOCKER_TAGNAME`, `DOCKER_IMG_NAME`, and `DOCKER_CHART_IMG_NAME` to your own preferences. An example can be found in `Makefile`.
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


## Deploy Fybrik module
1. In your module yaml spec (`hello-world-read-module.yaml`):
    - Change `spec.chart.name` to your chart registry.
    - Define `flows` and `capabilities` for your module, an example can be found in `hello-world-read-module.yaml`. 

2. Deploy `FybrikModule` in `fybrik-system` namespace:
```bash
kubectl create -f hello-world-read-module.yaml -n fybrik-system
```
3. Check if `FybrikApplication` successfully deployed:
```bash
kubectl get fybrikmodule hello-world-read-module -n fybrik-system
kubectl describe fybrikmodule hello-world-read-module -n fybrik-system
```


## Register data asset in a data catalog

You need to register your data asset in a data catalog in order for it to be used by the `fybrik-manager`.

- Follow step `Register the dataset in a data catalog` in [this example](https://fybrik.io/dev/samples/notebook/). These steps register the credentials required for accessing the dataset, and then register the data asset in the catalog.

- As an example you can run these commands to register two assets exist in `sample_assets`:
```bash
kubectl apply -f sample_assets/assetMedals.yaml
kubectl apply -f sample_assets/secretMedals.yaml
kubectl apply -f sample_assets/assetBank.yaml
kubectl apply -f sample_assets/secretBank.yaml
```

## Define policies

You can define OpenPolicyAgent policy to apply them to datasets. You can follow the `Define data access policies` section in [this example](https://fybrik.io/dev/samples/notebook/).

## Deploy Fybrik application which triggers module
1. In `fybrikapplication.yaml`:
    - Change `metadata.name` to your application name.
    - Define `appInfo.purpose`, `appInfo.role`, and `spec.data`.
    - Change `data.dataSetID` field to the identifier of the asset in the catalog which is in the format `<namespace>/<name>`.
 
2.  Deploy `FybrikApplication` in `default` namespace:
```bash
kubectl apply -f fybrikapplication.yaml -n default
```
3.  Check if `FybrikModule` successfully deployed:
```bash
kubectl get FybrikApplication -n default
kubectl describe FybrikApplication hello-world-read-module-test -n default
```

4.  Check if module was triggered in `fybrik-blueprints`:
```bash
kubectl get blueprint -n fybrik-blueprints
kubectl describe blueprint hello-world-read-module-test-default -n fybrik-blueprints
kubectl get pods -n fybrik-blueprints
```
If you are using the existing `hello-world-read-module.py`, you should see this in the `kubectl logs` of the `fybrik-blueprints` Pod:
```
$ kubectl logs <fybrik-blueprints pod> -n fybrik-blueprints
INFO:root:
Hello World Read Module!
INFO:root:Starting httpd server on localhost:8000
```

Then, you can do port forwarding in order to use the server by the following command:

```bash
kubectl port-forward <fybrik-blueprints pod> -n fybrik-blueprints 8000:8000 &
```

If you run the following request:
```bash
curl -X GET localhost:8000/medals-winners
```
you get the first 10 rows of the medals-winners dataset.

## Clean

Run the following command to delete the fybrik application:
```bash
kubectl delete FybrikApplication hello-world-read-module-test -n default
```

Run the following command to delete the fybrik module:
```bash
kubectl delete fybrikmodule hello-world-read-module -n fybrik-system
```
