# Chess_DSL
DSL jezik za predmet Jezici specifični za domen koji služi za igranje šaha.

## Ideja
Ideja je napraviti DSL sa pravilima za internacionalizaciju/lokalizaciju tako da se mogu komande igre prilagođavati prirodnom jeziku. <br>
Pravila za internacionalizaciju/lokalizaciju se u toku igre tumače i omogućava se parsiranje komandi.

Sama pravila lokalizacije se konfigurišu tokom igranja partije šaha gde korisnik unosi komande na željenom jeziku. <br>
Ovakav DSL je u mogućnosti da na osnovu konfiguracije tumači poteze koji su uneti preko konzole i da prepozna specifične simbole datog jezika. (npr. č, š , ü, é itd.).

### Komande
Komande pomeranja idu po formuli: <b>'ime figure' 'na polje'</b>. Ukoliko dve ili više istih figura mogu da se pomere na isto polje potrebno je dodati i <b>'sa polja'</b> parametar između. 
Izuzetak su handler komande koje se sastoje samo od naziva komande.

Primeri komandi:
- pešak e4,
- konj f3,
- top h1 d1 (primera radi i top a1 može da se pomeri na polje d1),
- poništi,
- nova igra,
- annuler itd.

### Jezici koji su implementirani u projekat su:
- srpski,
- engleski,
- španski,
- nemački, i
- francuski

Što se tiče prevoda komandi i figura na druge jezike koristi se Chess Vikipedija kako bi bilo što više tačnih naziva figura. <br>
Za ostale potrebe Google prevodilac je odradio svoj deo posla. Bar se nadamo 🙂.
