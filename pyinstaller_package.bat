pyinstaller --add-data ether_ghost\utils\eng_words_map.json:ether_ghost\utils ^
  --add-data ether_ghost\utils\phone_5.json:ether_ghost\utils ^
  --add-data ether_ghost\sessions\Payload.java:ether_ghost\sessions ^
  --add-data ether_ghost\public:ether_ghost\public ^
  --add-data ether_ghost\vessel_php\client.php:ether_ghost\vessel_php ^
  --add-data ether_ghost\vessel_php\server.php:ether_ghost\vessel_php ^
  --onefile ^
  .\run_ether_ghost.py