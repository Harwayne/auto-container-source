#!/bin/bash

set -e -u

docker build -t "$DOCKER_USER/auto-container-cr-reifier" python/cr
docker push "$DOCKER_USER/auto-container-cr-reifier"

# If the resources don't exist yet, then delete will fail.
set +e
kubectl delete -f config/cr-reifier.yaml
set -e

sed "s/DOCKER_USER/$DOCKER_USER/g" config/cr-reifier.yaml | kubectl apply -f -

