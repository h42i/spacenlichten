#Basis

Grundlegend hat jede logische Geräteeinheit eine eigene IP-Adresse und muss ein UDP-Server euf Port 20000 bereitstellen.
Ein TCP-Server ist optional, aber wünschenswert.

Einschränkungen bei UDP:
* JSON-Pakete dürfen die Payload-Größe eines UDP-Pakets nicht übersteigen. Falls mehr Daten gesendet werden müssen, kann das JSON-Paket einfach in mehrere aufgesplittet werden.
* Bei Serverantworten (z.B. wenn "feedback" den Wert true hat) sind analog gestückelt.
* Bei einer Erweiterung des Protokolls für Aktoren, müssen diese broadcasten.

#Protokoll

Spacenlichten arbeitet zustandsbasiert. Im Umkehrschluss werden sowohl auf den Anfrage- als auch auf den Antwortkanälen nur Zustandsänderungen versendet, mit der Ausnahme, dass wenn "feedback" den Wert true hat, auf jede Anfrage mit dem vollständigen Zustand des angefragten Gerätes geantwortet wird.

##Meta

```JSON
{
    "version": STRING
}
```

Das Feld "version" enthält als Wert die verwendete Protokollversion.
Noch ist keine fertige Version vorhanden. Bisherige Spezifikationen sind nicht verlässlich.

##Geräteinformationen

```JSON
{
    "name": STRING
}
```

Das "name" ist eine eindeutige Gerätekennung.

```JSON
{
    "mode": STRING,
    "dimension": INTEGER,
    "resolution": {
        "x": INTEGER,
        "y": INTEGER,
        "z": INTEGER
    }
}
```
Die beiden Felder "mode", "dimension" und "resolution" geben den Lichtmodus ("binary", "monochrome", "rgb"), die Dimension und die Auflösung des Geräts an. Falls die Dimension 0 ist, entfällt das Feld "resolution".

##Steuerung

```JSON
{
    "feedback": BOOLEAN,
    "latch": BOOLEAN
}
```

Solange "feedback" den Wert true hat, wird auf jede Anfrage mit dem vollständigen aktuellen Zustand geantwortet. Solange "latch" den Wert false hat, werden ankommende Änderungen des sichbaren Zustands gepuffert zurückgehalten, andernfalls werden alle Zustandsänderungen übernommen. 

##Binär

```JSON
{
    "on": BOOLEAN
}
```

```JSON
{
    "on": { "0": BOOLEAN, "1": BOOLEAN, "2": BOOLEAN, ... }
}
```

```JSON
{
    "on": {
        "0": { "0": BOOLEAN, "1": BOOLEAN, "2": BOOLEAN, ... },
        "1": { "0": BOOLEAN, "1": BOOLEAN, "2": BOOLEAN, ... },
        "2": { "0": BOOLEAN, "1": BOOLEAN, "2": BOOLEAN, ... },
        ...
    }
}
```

##Monochrom

```JSON
{
    "intensity": INTEGER
}
```

```JSON
{
    "intensity": { "0": INTEGER, "1": INTEGER, "2": INTEGER, ... }
}
```

```JSON
{
    "intensity": {
        "0": { "0": INTEGER, "1": INTEGER, "2": INTEGER, ... },
        "1": { "0": INTEGER, "1": INTEGER, "2": INTEGER, ... },
        "2": { "0": INTEGER, "1": INTEGER, "2": INTEGER, ... },
        ...
    }
}
```

##RGB

```JSON
{
    "color": { "r": INTEGER, "g": INTEGER, "b": INTEGER }
}
```

```JSON
{
    "color": {
        "0": { "r": INTEGER, "g": INTEGER, "b": INTEGER },
        "1": { "r": INTEGER, "g": INTEGER, "b": INTEGER },
        "2": { "r": INTEGER, "g": INTEGER, "b": INTEGER },
        ...
    }
}
```

```JSON
{
    "color": {
        "0": {
            "0": { "r": INTEGER, "g": INTEGER, "b": INTEGER },
            "1": { "r": INTEGER, "g": INTEGER, "b": INTEGER },
            "2": { "r": INTEGER, "g": INTEGER, "b": INTEGER },
            ...
        },
        "1": {
            "0": { "r": INTEGER, "g": INTEGER, "b": INTEGER },
            "1": { "r": INTEGER, "g": INTEGER, "b": INTEGER },
            "2": { "r": INTEGER, "g": INTEGER, "b": INTEGER },
            ...
        },
        "2": {
            "0": { "r": INTEGER, "g": INTEGER, "b": INTEGER },
            "1": { "r": INTEGER, "g": INTEGER, "b": INTEGER },
            "2": { "r": INTEGER, "g": INTEGER, "b": INTEGER },
            ...
        },
        ...
    }
}
```

