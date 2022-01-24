#!/usr/bin/env bash
# Copyright 2020 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

set -x
set -e

echo $1

source ./common.sh

export WORKING_DIR=test-script
export ACCESS_KEY=1234
export SECRET_KEY=1234

if [ $1 == "kind19" ]
then
    bin/kind delete cluster
    bin/kind create cluster --image=kindest/node:v1.19.11@sha256:07db187ae84b4b7de440a73886f008cf903fcf5764ba8106a9fd5243d6f32729

elif [ $1 == "kind21" ]
then
    bin/kind delete cluster
    bin/kind create cluster --image=kindest/node:v1.21.1@sha256:69860bda5563ac81e3c0057d654b5253219618a22ec3a346306239bba8cfa1a6
elif [ $1 == "kind22" ]
then
    bin/kind delete cluster
    bin/kind create cluster --image=kindest/node:v1.22.0@sha256:b8bda84bb3a190e6e028b1760d277454a72267a5454b57db34437c34a588d047
else
    echo "Unsupported kind version"
    exit 1
fi


#quick start

helm repo add jetstack https://charts.jetstack.io
helm repo add hashicorp https://helm.releases.hashicorp.com
helm repo add fybrik-charts https://fybrik.github.io/charts
helm repo update

bin/helm install cert-manager jetstack/cert-manager \
    --namespace cert-manager \
    --version v1.2.0 \
    --create-namespace \
    --set installCRDs=true \
    --wait --timeout 220s

# if [ $2 == "dev" ]
# then
#     cd ${PATH_TO_LOCAL_FYBRIK}
#     bin/helm dependency update charts/vault
#     bin/helm install vault charts/vault --create-namespace -n fybrik-system \
#         --set "vault.injector.enabled=false" \
#         --set "vault.server.dev.enabled=true" \
#         --values charts/vault/env/dev/vault-single-cluster-values.yaml
#     kubectl wait --for=condition=ready --all pod -n fybrik-system --timeout=120s

# else
    bin/helm install vault fybrik-charts/vault --create-namespace -n fybrik-system \
        --set "vault.injector.enabled=false" \
        --set "vault.server.dev.enabled=true" \
        --values https://raw.githubusercontent.com/fybrik/fybrik/v0.5.3/charts/vault/env/dev/vault-single-cluster-values.yaml
    kubectl wait --for=condition=ready --all pod -n fybrik-system --timeout=220s
# fi




bin/helm install fybrik-crd fybrik-charts/fybrik-crd -n fybrik-system --version v$2 --wait
bin/helm install fybrik fybrik-charts/fybrik -n fybrik-system --version v$2 --wait

kubectl wait --for=condition=ready --all pod -n fybrik-system --timeout=220s

sleep 10

kubectl apply -f https://github.com/fybrik/hello-world-read-module/releases/download/v$3/hello-world-read-module.yaml -n fybrik-system

# cd ${PATH_TO_LOCAL_FYBRIK}
# bin/helm install fybrik-crd charts/fybrik-crd -n fybrik-system --wait
# bin/helm install fybrik charts/fybrik --set global.tag=master --set global.imagePullPolicy=Always -n fybrik-system --wait


# hello-world-read-module
# kubectl apply -f hello-world-read-module/hello-world-read-module.yaml -n fybrik-system
# kubectl apply -f https://raw.githubusercontent.com/fybrik/hello-world-read-module/main/hello-world-read-module.yaml -n fybrik-system


# Notebook sample

kubectl create namespace fybrik-notebook-sample
kubectl config set-context --current --namespace=fybrik-notebook-sample

kubectl apply -f https://raw.githubusercontent.com/fybrik/hello-world-read-module/releases/$3/sample_assets/assetMedals.yaml -n fybrik-notebook-sample
kubectl apply -f https://raw.githubusercontent.com/fybrik/hello-world-read-module/releases/$3/sample_assets/secretMedals.yaml -n fybrik-notebook-sample
kubectl apply -f https://raw.githubusercontent.com/fybrik/hello-world-read-module/releases/$3/sample_assets/assetBank.yaml -n fybrik-notebook-sample
kubectl apply -f https://raw.githubusercontent.com/fybrik/hello-world-read-module/releases/$3/sample_assets/secretBank.yaml -n fybrik-notebook-sample


kubectl -n fybrik-system create configmap sample-policy --from-file=$WORKING_DIR/sample-policy-$3.rego
kubectl -n fybrik-system label configmap sample-policy openpolicyagent.org/policy=rego
# while [[ $(kubectl get cm sample-policy -n fybrik-system -o 'jsonpath={.metadata.annotations.openpolicyagent\.org/policy-status}') != '{"status":"ok"}' ]]; sleep 5; done --timeout=120s
c=0
while [[ $(kubectl get cm sample-policy -n fybrik-system -o 'jsonpath={.metadata.annotations.openpolicyagent\.org/policy-status}') != '{"status":"ok"}' ]]
do
    echo "waiting"
    ((c++)) && ((c==25)) && break
    sleep 5
done

# timeout 5 bash -c -- 'while true; do printf ".";done'


kubectl apply -f https://raw.githubusercontent.com/fybrik/hello-world-read-module/releases/$3/fybrikapplication.yaml -n default

c=0
while [[ $(kubectl get fybrikapplication my-notebook -n default -o 'jsonpath={.status.ready}') != "true" ]]
do
    echo "waiting"
    ((c++)) && ((c==30)) && break
    sleep 6
done

kubectl get pods -n fybrik-blueprints

POD_NAME=$(kubectl get pods -n fybrik-blueprints -o=name | sed "s/^.\{4\}//")

kubectl logs ${POD_NAME} -n fybrik-blueprints > res.out

DIFF=$(diff $WORKING_DIR/expected-$3.txt res.out)
if [ "${DIFF}" == "" ]
then
    echo "test succeeded"
else
    echo "test failed"
fi
# diff $WORKING_DIR/expected.txt res.out
