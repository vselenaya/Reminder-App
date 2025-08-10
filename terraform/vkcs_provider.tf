terraform {
    required_providers {
        vkcs = {
            source = "vk-cs/vkcs"
            version = "< 1.0.0"
        }
    }
}

provider "vkcs" {
    # Данные берем из переменных
    username   = var.vk_username
    password   = var.vk_password
    project_id = var.vk_project_id
    region     = var.vk_region
    auth_url   = var.vk_auth_url
}
