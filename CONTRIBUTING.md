## Publishing a Docker image

Publish a release of `cco-operator-kamatera`

Get the release archive URL: (e.g. `https://github.com/OriHoch/cco-provider-kamatera/archive/v0.0.5.tar.gz`)

Run the following from checkout of latest `ckan-cloud-operator`:

```
docker build -t orihoch/ckan-cloud-operator:kamatera-latest \
    --build-arg K8_PROVIDER=custom-kamatera \
    --build-arg K8_PROVIDER_CUSTOM_DOWNLOAD_URL=https://github.com/OriHoch/cco-provider-kamatera/archive/v0.0.5.tar.gz \
    .
```

## Development workflow

See the [ckan-cloud-operator](https://github.com/datopian/ckan-cloud-operator) development docs regarding custom providers
