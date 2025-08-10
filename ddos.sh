# Укажи IP-адрес твоего приложения
EXTERNAL_IP="212.233.92.216"

echo "Начинаем нагрузочное тестирование..."
echo "Нажмите Ctrl+C, чтобы остановить."

# Бесконечный цикл, который каждую секунду делает 4 запроса
while true; do
  # Запрос на главную страницу (дергает active_now и active_tomorrow)
  curl -s -o /dev/null "http://${EXTERNAL_IP}/" &
  
  # Запрос на получение всех напоминаний
  curl -s -o /dev/null "http://${EXTERNAL_IP}/?action=show_all" &

  # Запрос с фильтром по датам
  START_DATE=$(date -d '-1 day' +%Y-%m-%d)
  END_DATE=$(date -d '+1 day' +%Y-%m-%d)
  curl -s -o /dev/null "http://${EXTERNAL_IP}/?action=filter&filter_start_date=${START_DATE}&filter_end_date=${END_DATE}" &
  
  # Еще один запрос, чтобы увеличить интенсивность
  curl -s -o /dev/null "http://${EXTERNAL_IP}/" &

  # Знак '&' в конце каждой команды curl заставляет ее выполняться в фоновом режиме,
  # то есть все 4 запроса отправляются почти одновременно.
  # sleep 1 # Можно добавить небольшую паузу, если нагрузка слишком большая
  
  # Ждем, пока все фоновые процессы завершатся, прежде чем начать новую итерацию
  wait
done
