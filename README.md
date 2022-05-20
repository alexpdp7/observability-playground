Set up a cluster, for example using [proxmox-k8s](https://github.com/alexpdp7/proxmox-k8s).

Install [tobs](https://github.com/timescale/tobs).

If you use proxmox-k8s or some Kubernetes cluster that has DNS issues with busybox uclibc containers, follow [this procedure](https://github.com/timescale/tobs/issues/371#issuecomment-1133185163) to install tobs.

If not, then run:

```
$ tobs install -n tobs
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

Patch the collector, see https://github.com/timescale/tobs/issues/379 .

Expose Promscale GRPC OpenTelemetry endpoint (if using proxmox-k8s):

```
$ kubectl expose service -n tobs tobs-opentelemetry-collector --type=LoadBalancer --name=tobs-opentelemetry-collector-external --load-balancer-ip=0.0.0.0
```

Then you can try running:

```
$ cd tester
$ OTEL_EXPORTER_OTLP_ENDPOINT=http://tobs-opentelemetry-collector-external.tobs.<k8s-domain>:4317 poetry run python nagios-otel.py
```

A `bar` metric and a trace will appear in Grafan.
