<h1 align="center">Oświetlenie do szafy <img src="https://raw.githubusercontent.com/iiiypuk/rpi-icon/master/raspberry-pi-logo_resized_256.png" width="40" height="40"/> </h1>

<h4>
  <a href="https://botland.com.pl/paski-led-standardowe/9682-zestaw-pasek-led-smd3528-ip20-48w-60-diodm-barwa-zimna-5m-zasilacz-12v3a-5904422313937.html">
    💡Oświetlenie LED💡
  </a> 
  do szafy wykorzystujące Rasbperry Pi Zero z podłączonym 
  <a href="https://botland.com.pl/ultradzwiekowe-czujniki-odleglosci/5686-ultradzwiekowy-czujnik-odleglosci-hc-sr04-2-200cm-uchwyt-montazowy-5904422308452.html">
    📐czujnikiem dystansu📏 
  </a>   
  wraz z zapisem godzin otwarcia do bazdy danych.
</h4>

<h4>
Pasek LED zasilany jest osobno z 12V zasilacza i przełączany przez Raspberry Pi za pomocą 
  <a href="https://botland.com.pl/przekazniki-przekazniki-arduino/8463-modul-przekaznika-1-kanal-styki-10a250vac-cewka-5v-5904422300517.html">
    ⚡modułu przekaźnika⚡
  </a>
</h4>

<h5>Adres IP komputera z bazą danych ma znajdować się w pliku "adres.txt".
W przypadku braku połączenia program automatycznie zapisuje instrukcje do pliku "temp.txt", który automatycznie przesyła dane do bazy i usuwa się po ponownym połączeniu.</h5>

<br>
<h3>Struktura tabeli w bazie</h3>
<table>
  <tr>
    <th>ID</th>
    <th>Data</th>
    <th>Stan</th>
    <th>Dlugosc</th>
    <th>CzyStartowe</th>
    <th>CzyOffline</th>
  </tr>
    <tr>
    <th>int</th>
    <th>datetime2</th>
    <th>bit</th>
    <th>float</th>
    <th>bit</th>
    <th>bit</th>
  </tr>
 </table>
