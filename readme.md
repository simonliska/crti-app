

helm repo add bitnami https://charts.bitnami.com/bitnami
helm install my-rabbitmq bitnami/rabbitmq --set auth.username=user,auth.password=PASSWORD
