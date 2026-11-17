(ifdd-model-mapping)=
# Von LinkML zu JSON-LD

## Eine Quelle je Namensraum

Jeder Namensraum hat genau eine LinkML-Datei. Sie steht für sich: Terme, die
jeder Context braucht (`objType`, `objName`, `origin`, `publisher`, die
`c_*`-Terme …), stehen in jeder Datei ausgeschrieben, weil jeder Context sie
im eigenen Namensraum definiert. Das Backend erkennt den Namensraum eines
Contexts daran, wohin seine `c_*`-Terme expandieren. Ein gemeinsames,
importiertes Modul würde diese Terme für alle Contexts in einen Namensraum
legen.

| LinkML | schema-Dienst | type- oder unit-Dienst |
|---|---|---|
| Schema-`id` | Präfix des eigenen Namensraums | Knoten `owl:Ontology` |
| Schema-`name` | Dateiname `<name>.jsonld` (Context-Name) | Verzeichnis `<name>/` |
| Klasse mit `class_uri: <präfix>:schema` | Kopfknoten `rdfs:Class` | Knoten `rdfs:Class` |
| Attribute dieser Klasse | Terme mit `@type`/`@container` | Knoten `rdf:Property` |
| weitere Klassen (nur `class_uri`) | Ziel von `@type: @id` | `rdfs:range` |
| Enum mit `enum_uri` (Einheiten) | – | ein Knoten je erlaubtem Wert |

Ein Schema ohne Klasse im eigenen Namensraum (etwa das Klima-Vokabular für
Zeitreihen) bekommt ein Vokabular, aber keinen Context.

## JSON-LD-Context

Der Context entsteht mit `gen-jsonld-context` und den Optionen
`--no-metadata --fix-multivalue-containers --xsd-anyuri-as-iri`. Ein kurzer
Nachschritt (`ifdd_model.context`) dann:

- entfernt `@vocab`, damit undefinierte Terme undefiniert bleiben und
  `ifdd-ct check` sie melden kann, und schreibt jeden Term als `präfix:term`;
- entfernt die Terme, die LinkML für Klassen schreibt;
- entfernt `@type: @id` bei eingebetteten Werten (`inlined: true`, etwa
  `QuantityValue`);
- entfernt das Präfix `linkml:`;
- ergänzt `@version: 1.1`, den Alias `type`, den Term `schemaVersion` und den
  Kopfknoten mit der Beschreibung der Klasse und der Version des Schemas.

Wertebereiche: `datetime`, `date` und die eigenen Typen `gyear`, `duration`
ergeben `@type` mit dem XSD-Datentyp; eine Klasse oder `uriorcurie` ergibt
`@type: @id`; `multivalued: true` ergibt `@container: @set`.

## Vokabular

Das Vokabular schreibt `ifdd_model.vocab`:

| Vokabular | LinkML |
|---|---|
| `rdfs:label` (en, de) | `title`, Annotation `title_de` |
| `rdfs:comment` (en, de) | `description`, Annotation `description_de` |
| `sh:order` | `rank` |
| `rdfs:range` | `range` (nicht bei Text und `uriorcurie`) |
| `qudt:hasQuantityKind` | Annotation `quantity_kind` |
| `qudt:applicableUnit` | Annotation `applicable_units` (IRIs, durch Leerzeichen getrennt) |
| `sh:minInclusive`, `sh:maxInclusive` | `minimum_value`, `maximum_value` |
| `qudt:symbol` (Einheiten) | `unit.symbol` |
| `qudt:hasQuantityKind` (Einheiten) | `unit.has_quantity_kind` |
| `skos:exactMatch` (Einheiten) | `exact_mappings` |

Bei Größenarten wird `qudt:applicableUnit` aus den Einheiten abgeleitet, die
auf sie verweisen.
