# Получение данных о существующей внешней сети
data "vkcs_networking_network" "extnet" {
  name = "internet"  # иногда часто встречается название "ext-net"
}

# Создание нашей приватной сети
resource "vkcs_networking_network" "app_net" {
  name           = "reminder-app-net"
  admin_state_up = true
}

# Создание подсети в нашей приватной сети
resource "vkcs_networking_subnet" "app_subnet" {
  name            = "reminder-app-subnet"
  network_id      = vkcs_networking_network.app_net.id
  cidr            = "192.168.200.0/24"
  dns_nameservers = ["8.8.8.8"]
}

# Создание маршрутизатора для выхода в интернет
resource "vkcs_networking_router" "app_router" {
  name                = "reminder-app-router"
  admin_state_up      = true
  external_network_id = data.vkcs_networking_network.extnet.id
}

# Подключение нашей подсети к маршрутизатору
resource "vkcs_networking_router_interface" "app_router_interface" {
  router_id = vkcs_networking_router.app_router.id
  subnet_id = vkcs_networking_subnet.app_subnet.id
}
