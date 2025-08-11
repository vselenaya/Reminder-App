# --- DATA-блоки: Получаем информацию ---
data "vkcs_images_image" "ubuntu" {
  visibility  = "public"
  most_recent = true
  properties = {
    mcs_os_distro  = "ubuntu"
    mcs_os_version = "22.04"
  }
}
data "vkcs_compute_flavor" "basic" {
  name = "Basic-1-1-10"
}


# --- РЕСУРСЫ: Что мы хотим создать ---

# 1. СОЗДАЕМ ГРУППУ БЕЗОПАСНОСТИ (правильное имя из PDF)
resource "vkcs_networking_secgroup" "app_secgroup" {
  name        = "app-reminders-secgroup-tf"
  description = "Allows SSH and HTTP traffic for Reminder App"
}

# 2. СОЗДАЕМ ПРАВИЛА ДЛЯ НЕЕ (правильное имя из PDF)
resource "vkcs_networking_secgroup_rule" "ssh_rule" {
  direction         = "ingress"
  protocol          = "tcp"
  port_range_min    = 22
  port_range_max    = 22
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = vkcs_networking_secgroup.app_secgroup.id
}
resource "vkcs_networking_secgroup_rule" "http_rule" {
  direction         = "ingress"
  protocol          = "tcp"
  port_range_min    = 80
  port_range_max    = 80
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = vkcs_networking_secgroup.app_secgroup.id
}


# 3. Виртуальная машина
resource "vkcs_compute_instance" "app_vm" {
  name              = "reminder-app-vm"
  flavor_id         = data.vkcs_compute_flavor.basic.id
  key_pair          = var.key_pair_name
  availability_zone = var.availability_zone_name
  
  # ПРИМЕНЯЕМ НАШУ СОБСТВЕННУЮ ГРУППУ
  security_groups   = [vkcs_networking_secgroup.app_secgroup.name]

  block_device {
    uuid                  = data.vkcs_images_image.ubuntu.id
    source_type           = "image"
    destination_type      = "volume"
    volume_type           = "ceph-ssd"
    volume_size           = 10
    boot_index            = 0
    delete_on_termination = true
  }

  network {
    uuid = vkcs_networking_network.app_net.id
  }
  
  depends_on = [
    # Запускать ВМ только после создания сети и правил
    vkcs_networking_router_interface.app_router_interface,
    vkcs_networking_secgroup_rule.ssh_rule,
    vkcs_networking_secgroup_rule.http_rule
  ]

  user_data = <<-EOF
              #!/bin/bash
              apt-get update -y && apt-get upgrade -y
              apt-get install -y ca-certificates curl gnupg
              install -m 0755 -d /etc/apt/keyrings
              curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
              chmod a+r /etc/apt/keyrings/docker.gpg
              echo \
                "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
                $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
                tee /etc/apt/sources.list.d/docker.list > /dev/null
              apt-get update -y
              apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
              usermod -aG docker ubuntu
              EOF
}

# 4. Публичный IP-адрес
resource "vkcs_networking_floatingip" "fip" {
  pool = data.vkcs_networking_network.extnet.name
}

# 5. Привязка IP к ВМ
resource "vkcs_compute_floatingip_associate" "fip_associate" {
  floating_ip = vkcs_networking_floatingip.fip.address
  instance_id = vkcs_compute_instance.app_vm.id
}


# --- ВЫВОД ---
output "instance_public_ip" {
  value = vkcs_networking_floatingip.fip.address
}
