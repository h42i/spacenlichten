#Meta:

```JSON
{
    "feedback": BOOLEAN,
    "latch": BOOLEAN
}
```

#Binary:

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

#Monochrome:

```JSON
{
    "intensity": { "0": INTEGER, "1": INTEGER, "2": INTEGER... }
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

#RGB:

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
        }
        "1": {
            "0": { "r": INTEGER, "g": INTEGER, "b": INTEGER },
            "1": { "r": INTEGER, "g": INTEGER, "b": INTEGER },
            "2": { "r": INTEGER, "g": INTEGER, "b": INTEGER },
            ...
        }
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

