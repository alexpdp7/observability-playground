Set up a cluster, for example using [proxmox-k8s](https://github.com/alexpdp7/proxmox-k8s).

Install [tobs](https://github.com/timescale/tobs) (see [this known issue](https://github.com/timescale/tobs/issues/296)):

```
$ tobs install --tracing -n tobs
```

Due to this [issue](https://github.com/timescale/tobs/issues/296), the OpenTelemetry collector is not deployed for me.
Use the following command to deploy it.
(Note that this assumes you used `-n tobs` above.)

```
$ kubectl apply -f - <<EOF
apiVersion: opentelemetry.io/v1alpha1
kind: OpenTelemetryCollector
metadata:
  name: otel
  namespace: tobs
spec:
  config: |
    receivers:
      otlp:
        protocols:
          grpc:
          http:

    exporters:
      otlp:
        endpoint: "tobs-promscale-connector:9202"
        tls:
          insecure: true
        sending_queue:
          queue_size: 1000000
        timeout: 10s
      prometheusremotewrite:
        endpoint: "tobs-promscale-connector:9201/write"
        tls:
          insecure: true

    processors:
      batch:
        send_batch_size: 4000
        send_batch_max_size: 4000
        timeout: 10s

    service:
      pipelines:
        traces:
          receivers: [otlp]
          exporters: [otlp]
          processors: [batch]
        metrics:
          receivers: [otlp]
          processors: [batch]
          exporters: [prometheusremotewrite]
EOF
```

Expose Grafana:

```
$ kubectl --namespace tobs create ingress grafana --annotation kubernetes.io/ingress.class=haproxy --rule="grafana.<ingress_domain>/*=tobs-grafana:80,tls"
```

Fetch Grafana password:

```
$ tobs -n tobs grafana get-password
```

Visit https://grafana.<ingress_domain>, as `admin` using the password from the previous command.

Expose Promscale GRPC OpenTelemetry endpoint (if using proxmox-k8s):

```
$ kubectl expose service -n tobs otel-collector --type=LoadBalancer --name=otel-collector-external --load-balancer-ip=0.0.0.0
```

Run the following command to find out in which port has the `otlp-grpc` port has end up being exposed:

```
$ kubectl get -n tobs svc otel-collector otel-collector-external -o yaml
```

Then you can try running:

```
$ cd nagios-otel
$ OTEL_EXPORTER_OTLP_INSECURE=true OTEL_EXPORTER_OTLP_ENDPOINT=otel-collector-external.tobs.<load_balancer_domain>:<port> poetry run python nagios-otel.py
```
