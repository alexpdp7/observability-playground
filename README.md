Set up a cluster, for example using https://github.com/alexpdp7/proxmox-k8s .

Install [tobs](https://github.com/timescale/tobs):

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
