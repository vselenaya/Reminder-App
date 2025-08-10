vk_username   = "myemail@example.ru"   # login от аккаунта VK Cloud
vk_project_id = "113...ae"             # это id проекта VK Cloud, можно найти на сайте в разделе вашего проекта (также он будет в kubeconfig.yaml)
# vk_password = "твой-пароль"          # Пароль мы введем в консоли, так безопаснее
                                       # (terraform умный: он увидит, что пароль не записан -> спросит его в консоли)
key_pair_name = "my-ssh-key-vkcloud"   # Заменить на имя своего ключа в VK Cloud (см. инструкции на сайте Vk Cloud, как его создавать)
