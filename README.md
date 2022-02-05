# Wdrożenie aplikacji "Hello" w środowisku Azure

Instalacja środowiska AKS & ACR z aplikacją Hello World z wykorzystaniem narzędzia Terraform

## Stacja robocza

1. Rekomendowany system - Linux (ubuntu)

2. Zainstalowane komponenty:
* Azure CLI ([instalacja](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli))
* Docker 
* kubectl ([instalacja](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/))
* terraform ([instalacja](https://learn.hashicorp.com/tutorials/terraform/install-cli))

## Instalacja Dockera dla Ubuntu

```bash
sudo su

apt-get update ;
apt-get install -qq apt-transport-https ca-certificates curl software-properties-common ;
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add - ;
add-apt-repository 'deb [arch=amd64] https://download.docker.com/linux/ubuntu '$(lsb_release -cs)' stable' ;
apt-get update ;
apt-get install -qq docker-ce ;

# do not forget to exit
exit
```

## Pobranie repozytorium git

```bash
git clone https://github.com/elektrycznyy/mat_w_aks.git
```

## Tworzenie docker image
```bash
cd mat_w_aks
docker build -t myapp:latest .
...
Successfully built 3819ec1a9a18
docker images
REPOSITORY   TAG       IMAGE ID       CREATED          SIZE
myapp        latest    3819ec1a9a18   24 seconds ago   57.2MB
alpine       3.5       f80194ae2e0c   3 years ago      4MB
```

## Tworzenie klastra AKS i usługi ACR przy użyciu Terraform

Zaloguj sie do Azure

```bash
az login
```

1. Sprawdź czy terraform jest zainstalowany
```terraform
terraform --version
Terraform v1.1.4
on linux_amd64
```
2. Zainicjuj projekt
```terraform
terraform init
...
Terraform has been successfully initialized!
```
3. Polecenie ```terraform plan``` tworzy plan umożliwiający podgląd zmian, które Terraform planuje wprowadzić w infrastrukturze.
4. Wywołaj polecenie ```terraform apply```, które wykonuje wszystkie działania zaproponowane w ```terraform plan```.
```terraform
terraform apply

Terraform used the selected providers to generate the following execution plan. Resource actions are
indicated with the following symbols:
  + create

Terraform will perform the following actions:

  # azurerm_container_registry.acr will be created

...

Changes to Outputs:
  + acr_id           = (known after apply)
  + acr_login_server = (known after apply)
  + aks_fqdn         = (known after apply)
  + aks_id           = (known after apply)
  + aks_node_rg      = (known after apply)

Do you want to perform these actions?
  Terraform will perform the actions described above.
  Only 'yes' will be accepted to approve.

  Enter a value: yes
```
5. Zatwierdź wpisując```yes```. 
Teraz tworzone są wszystkie zasoby z ```terraform plan```, może to potrwać 5-7 minut.

6. Zaloguj się do ACR
```bash
az acr login -n mateuszAKSacr
Login Succeeded
```
7. Dodatkowo otaguj odpowiednio swój dockerimage, aby umożliwić przesłanie go do ACR. Zauważ, że ten sam obraz posiada teraz dwie nazwy.
```bash
docker tag myapp:latest mateuszaksacr.azurecr.io/myapp:latest
docker images
REPOSITORY                       TAG       IMAGE ID       CREATED       SIZE
myapp                            latest    3819ec1a9a18   2 hours ago   57.2MB
mateuszaksacr.azurecr.io/myapp   latest    3819ec1a9a18   2 hours ago   57.2MB
alpine                           3.5       f80194ae2e0c   3 years ago   4MB
```
8. Umieść obraz w repozytorium ACR
```bash
docker push mateuszaksacr.azurecr.io/myapp
Using default tag: latest
The push refers to repository [mateuszaksacr.azurecr.io/myapp]
02cdc0f5399a: Pushed 
9e06fc4c8d31: Pushed 
4f4bd9b854ad: Pushed 
dc6e8505fab0: Pushed 
ada89fde400e: Pushed 
f566c57e6f2d: Pushed 
latest: digest: sha256:8cbf8ded206c73fc40c49e1be639bddb1f9b1c3f7e49b347cab954f49d9c80a6 size: 1572
```
9. Uzyskaj dostęp do klastra. Polecenie ```az aks get-credentials``` kopiuje kubeconfig zawierający konfigurację dostępu do klastra do stacji roboczej.
```bash
az aks get-credentials --name mateusz-aks --resource-group mateusz_aks_tf_rg
Merged "mateusz-aks" as current context in /home/mateuszw/.kube/config
```
Sprawdźmy zatem ilość węzłów
```bash
kubectl get nodes
NAME                             STATUS   ROLES   AGE   VERSION
aks-system-23231742-vmss000000   Ready    agent   83m   v1.19.11
aks-system-23231742-vmss000001   Ready    agent   83m   v1.19.11
```
## Uruchomienie aplikacji
Uruchamiamy aplikację
```bash
kubectl apply -f aks-depl.yaml
deployment.apps/my-python-deployment created
service/my-python-app-svc created
```
Wyświetlamy informacje
```bash
kubectl get all
NAME                                       READY   STATUS    RESTARTS   AGE
pod/my-python-deployment-d658f477c-47t6q   1/1     Running   0          94s
pod/my-python-deployment-d658f477c-qmlv7   1/1     Running   0          94s

NAME                        TYPE           CLUSTER-IP     EXTERNAL-IP      PORT(S)          AGE
service/kubernetes          ClusterIP      10.0.0.1       <none>           443/TCP          90m
service/my-python-app-svc   LoadBalancer   10.0.216.178   20.101.255.211   5000:32484/TCP   94s

NAME                                   READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/my-python-deployment   2/2     2            2           95s

NAME                                             DESIRED   CURRENT   READY   AGE
replicaset.apps/my-python-deployment-d658f477c   2         2         2       95s
```

## Sprawdzenie aplikacji
Sprawdzamy odwołanie do zewnętrznego ip load balancera 
```bash
curl 20.101.255.211:5000/czesc/Mateusz
<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<title>Moja aplikacja</title>
</head>
<body>
	<h1>Cześć, Mateusz</h1>
</body>
```
