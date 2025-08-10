# --- DATA-блоки: Получаем информацию об облачных ресурсах ---

# 1. Находим ID шаблона Kubernetes для нужной версии
data "vkcs_kubernetes_clustertemplate" "k8s_template" {
  version = var.k8s_version
}

# 2. Находим ID типа ВМ для мастера
data "vkcs_compute_flavor" "k8s_master_flavor" {
  name = var.k8s_master_flavor_name
}

# 3. Находим ID типа ВМ для рабочих нод
data "vkcs_compute_flavor" "k8s_node_flavor" {
  name = var.k8s_node_flavor_name
}


# --- РЕСУРСЫ: Создаем сам кластер ---

# 1. Kubernetes Кластер (мастер-ноды и API)
resource "vkcs_kubernetes_cluster" "k8s_cluster" {
  # Запускать только после полной настройки сети
  depends_on = [
    vkcs_networking_router_interface.app_router_interface,
  ]

  name                = "reminder-app-cluster"
  cluster_template_id = data.vkcs_kubernetes_clustertemplate.k8s_template.id
  master_flavor       = data.vkcs_compute_flavor.k8s_master_flavor.id
  master_count        = 1
  
  # Указываем сеть и подсеть, созданные в network.tf
  network_id          = vkcs_networking_network.app_net.id
  subnet_id           = vkcs_networking_subnet.app_subnet.id
  availability_zone   = var.k8s_availability_zone

  # Включить публичный IP для доступа к API кластера - это очень важно
  floating_ip_enabled = true
}

# 2. Группа рабочих нод (ВМ, где будут работать наши контейнеры)
resource "vkcs_kubernetes_node_group" "k8s_node_group" {
  name       = "worker-nodes"
  cluster_id = vkcs_kubernetes_cluster.k8s_cluster.id
  flavor_id  = data.vkcs_compute_flavor.k8s_node_flavor.id

  # Начнем с одной ноды - для нашего приложения хватит
  node_count = 1
  
  # Настройки для автомасштабирования (мы его включим позже через kubectl)
  autoscaling_enabled = false
  min_nodes           = 1
  max_nodes           = 3
}


# --- ВЫВОД: Показать полезную информацию в конце ---

output "get_kubeconfig_command" {
  description = "Команда для скачивания файла конфигурации kubectl. Выполните ее после 'terraform apply'. Если не работает, скачайте его из UI"
  # Мы берем ID созданного кластера и подставляем в команду
  value       = "vkcs kubernetes cluster get-kubeconfig ${vkcs_kubernetes_cluster.k8s_cluster.id} --file ./kubeconfig.yaml"
}

output "cluster_id" {
  description = "ID созданного Kubernetes кластера"
  value       = vkcs_kubernetes_cluster.k8s_cluster.id
}
