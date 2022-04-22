Set up a cluster, for example using [proxmox-k8s](https://github.com/alexpdp7/proxmox-k8s).

Install [tobs](https://github.com/timescale/tobs) (see [this known issue](https://github.com/timescale/tobs/issues/296)):

```
$ tobs install --tracing -n tobs
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
$ kubectl expose -n tobs service tobs-promscale-connector --port=9202 --type=LoadBalancer --name=otel-grpc --load-balancer-ip=0.0.0.0
$ kubectl get svc -n tobs otel-grpc  # to get the actual port exposed
```

Then you can try running:

```
$ cd nagios-otel
$ OTEL_EXPORTER_OTLP_INSECURE=true OTEL_EXPORTER_OTLP_ENDPOINT=otel-grpc.tobs.<k8s_domain>:<lb_port> poetry run python nagios-otel.py
ERROR:opentelemetry.exporter.otlp.proto.grpc.exporter:Failed to export span batch, error code: StatusCode.UNIMPLEMENTED
```
