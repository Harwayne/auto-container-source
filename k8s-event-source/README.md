# K8s Event Source

This is a lightly modified version of [KubernetesEventSource](https://github.com/knative/eventing-sources/blob/master/pkg/apis/sources/v1alpha1/kuberneteseventsource_types.go). The only code modification is switching from using flags to using environment variables.

## Installation

1. Install the CRD.
    ```shell
    ko apply -f k8s-event-source/k8s-event-source.yaml
    ```

### Example

1. Create the 'scaffold' (e.g. the `Channel`, `Subscription`, `ServiceAccount`, RBAC, etc.) for the actual `K8sEventSource` resource applied in the next step.

    ```shell
    kubectl apply -f k8s-event-source/scaffold.yaml
    ```
    
1. Create the `K8sEventSource`

    ```shell
    kubectl apply -f k8s-event-source/cr.yaml
    ```
    
### Verification

#### Create Events

Create events by launching a pod in the default namespace. Create a busybox container.

```shell
kubectl run -i --tty busybox --image=busybox --restart=Never -- sh
```

Once the shell comes up, just exit it and kill the pod.

```shell
kubectl delete pods busybox
```

#### Verify

We will verify that the kubernetes events were sent into the Knative eventing system by looking at our message dumper function logs. 

```shell
kubectl get pods -l serving.knative.dev/service=message-dumper -o=custom-columns=NAME:.metadata.name 
# Find a specific message-dumper pod and put its name into the next 
kubectl logs <pod-name> user-container
```

You should see log lines similar to:

```
{"metadata":{"name":"busybox.15644359eaa4d8e7","namespace":"default","selfLink":"/api/v1/namespaces/default/events/busybox.15644359eaa4d8e7","uid":"daf8d3ca-e10d-11e8-bf3c-42010a8a017d","resourceVersion":"7840","creationTimestamp":"2018-11-05T15:17:05Z"},"involvedObject":{"kind":"Pod","namespace":"default","name":"busybox","uid":"daf645df-e10d-11e8-bf3c-42010a8a017d","apiVersion":"v1","resourceVersion":"681388"},"reason":"Scheduled","message":"Successfully assigned busybox to gke-knative-eventing-e2e-default-pool-575bcad9-vz55","source":{"component":"default-scheduler"},"firstTimestamp":"2018-11-05T15:17:05Z","lastTimestamp":"2018-11-05T15:17:05Z","count":1,"type":"Normal","eventTime":null,"reportingComponent":"","reportingInstance":""}
Ce-Source: /apis/v1/namespaces/default/pods/busybox
{"metadata":{"name":"busybox.15644359f59f72f2","namespace":"default","selfLink":"/api/v1/namespaces/default/events/busybox.15644359f59f72f2","uid":"db14ff23-e10d-11e8-bf3c-42010a8a017d","resourceVersion":"7841","creationTimestamp":"2018-11-05T15:17:06Z"},"involvedObject":{"kind":"Pod","namespace":"default","name":"busybox","uid":"daf645df-e10d-11e8-bf3c-42010a8a017d","apiVersion":"v1","resourceVersion":"681389"},"reason":"SuccessfulMountVolume","message":"MountVolume.SetUp succeeded for volume \"default-token-pzr6x\" ","source":{"component":"kubelet","host":"gke-knative-eventing-e2e-default-pool-575bcad9-vz55"},"firstTimestamp":"2018-11-05T15:17:06Z","lastTimestamp":"2018-11-05T15:17:06Z","count":1,"type":"Normal","eventTime":null,"reportingComponent":"","reportingInstance":""}
Ce-Source: /apis/v1/namespaces/default/pods/busybox
```
