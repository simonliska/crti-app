# prereq
docker, k3d, kubectl (openlens), helm

create cluster:
```sh
k3d cluster create
```
deploy rabbit: 
```sh
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm install my-rabbitmq bitnami/rabbitmq --set auth.username=user,auth.password=PASSWORD
```
RabbitMQ resources (vhost default "/", user: corti:corti, queue: logs) were crated manually for sake of time. Otherwise I would create them using CRD (apiVersion: rabbitmq.com/v1beta1).

build, push container:
```sh
docker build -t simonliska/tuesday:crti-latest .
docker push simonliska/tuesday:crti-latest
```
deploy to k3d;
```sh
kubectl apply -f producer-deployment.yaml
kubectl apply -f consumer-deployment.yaml
```
producer is reading from 'input.txt' file and consumer is outputing to 'output.txt'

Healthcheck on consumer site:
```yaml
heartbeat=600,  # Configure heartbeat timeout to ensure connection is alive
blocked_connection_timeout=300  # Timeout for blocked connection (e.g., RabbitMQ is overloaded)
```

Monitoring:
Deploy promentheus,Grafana:
``` sh
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus-operator prometheus-community/kube-prometheus-stack --namespace default
```
Create ServiceMonitor,Service:
```sh
kubectl apply -f consumer-sm.yaml
```
i've just added label `release: prometheus-operator` becasue in default prometheus operator has label selector  
```yaml
  serviceMonitorSelector:
    matchLabels:
      release: prometheus-operator
```
Prometheus itself in production need a lot more stuff, like persistance storage - i would choose localpv storage. i.e. longhorn, also HA, Certs, exposing Grafana - LB or Ingress.  
I choose RabbitMQ message broker becasue is the one I'm working on production. Also what can be used here is `Apache Kafka`, `Redis/Valkey` or using AWS service `SQS`.
For k8s I chose `k3d` becasue It's fast way how to deploy app. For prod use more prod ready k8s (managed,unmanaged) `rancher`, aws `eks`, azure `aks` etc.  

Improvements in `producer` app:  
- Error Handling: Implement robust error handling around the RabbitMQ interactions and file operations. This can include catching exceptions when publishing messages or when the connection fails and trying to reconnect if necessary.  
- Clean Exit: The script lacks a way to cleanly close connections and exit. Consider catching signals (like SIGINT) to gracefully shutdown.  
Configurability: Make the script more configurable by allowing more command-line arguments or using environment variables for settings like the RabbitMQ credentials, host, and queue settings.
- Replace print statements with logging (file, stdout).  
- Message Buffering: If messages are generated faster than they can be sent, consider implementing a message buffering mechanism or batch the messages to reduce the number of publish calls. (copy of queue logs to another with i.e 7 day retention to prevent wrong reading from consumer)  
- Optimize File Handling: Opening the file in every loop iteration is inefficient. Consider monitoring the file for changes and only reading new lines as they are added.  

Also similar for the `consumer`:
- Persistent Connection Management:  Managing the connection outside of the main loop and handling reconnection.
- Graceful Shutdown  
- Error handling  
- Configurability  


Your solution has the ability to handle increased load:

- Horizontal Pod Autoscaling (HPA) based on metrics (number of messages in Q, or CPU usage) for automatically adjusts the number of pods in a deployment  
- Cluster Autoscaler for automatically adjust the number of nodes  