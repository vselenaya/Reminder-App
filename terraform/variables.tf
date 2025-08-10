variable "vk_username" {
  type        = string
  description = "Имя пользователя (email) в VK Cloud"
}
variable "vk_password" {
  type        = string
  description = "Пароль от аккаунта VK Cloud"
  sensitive   = true
}
variable "vk_project_id" {
  type        = string
  description = "ID проекта в VK Cloud"
}
variable "vk_region" {
  type        = string
  description = "Регион проекта"
  default     = "RegionOne"
}
variable "vk_auth_url" {
  type        = string
  description = "URL для аутентификации"
  default     = "https://infra.mail.ru:35357/v3/"
}
variable "key_pair_name" {
  type        = string
  description = "Имя вашего SSH-ключа, загруженного в VK Cloud"
}
variable "availability_zone_name" {
  type        = string
  description = "Зона доступности (например, MS1)"
  default     = "GZ1"
}

# --- Новые переменные для Kubernetes ---
variable "k8s_version" {
  type = string
  description = "Версия Kubernetes кластера"
  default = "1.28" # Используем 1.28, так как 1.31 может быть нестабилен
}
variable "k8s_master_flavor_name" {
  type = string
  description = "Тип ВМ для мастер-ноды"
  default = "STD3-4-8" # спецификация виртуальной машины (3 vCPU, 4 ГБ RAM, 8 ГБ диска)
}
variable "k8s_node_flavor_name" {
  type = string
  description = "Тип ВМ для рабочих нод"
  default = "STD2-2-4"
}
variable "k8s_availability_zone" {
  type = string
  description = "Зона доступности для кластера"
  default = "GZ1"
}

