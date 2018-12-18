#!/bin/bash

set -e -u

docker build -t "$DOCKER_USER/auto-container-crd" python/crd
docker push "$DOCKER_USER/auto-container-crd"

# If the resources don't exist yet, then delete will fail.
set +e
kubectl delete -f config/crd-decorator.yaml
set -e

sed "s/DOCKER_USER/$DOCKER_USER/g" config/crd-decorator.yaml | kubectl apply -f -

