# Heartbeat Source

This is a lightly modified version of [Heartbeat](https://github.com/knative/eventing-sources/blob/4886b8f0ac53973a9f34b525452d9396d2fc209b/cmd/heartbeats/main.go). The only code modification is switching from using flags to using environment variables.

## Installation

1. Install the CRD.
    ```shell
    ko apply -f heartbeat-source/heartbeat-source.yaml
    ```

### Example

1. Create the 'scaffold' (e.g. the `Channel`, `Subscription`, etc.) for the actual `HeartbeatSource` resource applied in the next step.

    ```shell
    kubectl apply -f heartbeat-source/scaffold.yaml
    ```
    
1. Create the `HeartbeatSource`

    ```shell
    kubectl apply -f heartbeat-source/cr.yaml
    ```
    
### Verification

We will verify that the heartbeats were sent into the Knative eventing system by looking at our message dumper function logs. 

```shell
kubectl get pods -l serving.knative.dev/service=message-dumper -o=custom-columns=NAME:.metadata.name 
# Find a specific message-dumper pod and put its name into the next 
kubectl logs <pod-name> user-container
```

You should see log lines similar to:

```
{"id":1,"label":"\"I can't believe there's no controller!\""}
```
