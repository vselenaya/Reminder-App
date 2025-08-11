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
