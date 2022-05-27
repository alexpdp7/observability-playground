Set up a cluster, for example using [proxmox-k8s](https://github.com/alexpdp7/proxmox-k8s).

Install [tobs](https://github.com/timescale/tobs).

There are some known issues with installing tobs:

* tobs uses busybox:1.28 that uses uclibc, that has DNS issues.
  [On proxmox-k8s, DNS resolution does not work well, breaking tobs install](https://github.com/alexpdp7/proxmox-k8s/issues/1).
  [This issue might remove the usage of busybox:1.28](https://github.com/timescale/tobs/issues/338).
* [One of the images used by tobs is huge, causing timeouts during installation](https://github.com/timescale/tobs/issues/377)

If those are solved, then you may be able to install tobs by running `tobs install -n tobs`.
However, I recommend installing tobs using Helm and a patched fork:

```
$ git clone git@github.com:alexpdp7/tobs.git
$ cd tobs/chart
$ rm Chart.lock
$ helm dependency build
$ helm install --create-namespace -n tobs --wait tobs . --debug --timeout=15m
```

(note the timeout parameter to prevent the issue with the huge image.)

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
$ kubectl expose service -n tobs tobs-opentelemetry-collector --type=LoadBalancer --name=tobs-opentelemetry-collector-external --load-balancer-ip=0.0.0.0
```

Then you can try running:

```
$ cd tester
$ OTEL_EXPORTER_OTLP_ENDPOINT=http://tobs-opentelemetry-collector-external.tobs.<k8s-domain>:4317 poetry run python nagios-otel.py
```

A `bar` metric and a trace will appear in Grafan.
