# -*- coding: iso-8859-1 -*-
# This file contains the lists of error messages used by xmlproc

import string

# The interface to the outside world

# Todo:
# - 3047 needed in Swedish, Norwegian and French
# - 2024 ditto
# - 2025 ditto
# - 2004 must be retranslated

error_lists={}  # The hash of errors

def add_error_list(language,list):
    error_lists[string.lower(language)]=list

def get_error_list(language):
    return error_lists[string.lower(language)]

def get_language_list():
    return error_lists.keys()

# Errors in English

english={

    # --- Warnings: 1000-1999
    1000: "Undeclared namespace prefix '%s'",
    1002: "Unsupported encoding '%s'",
    1003: "Obsolete namespace syntax",
    1005: "Unsupported character number '%d' in character reference",
    1006: "Element '%s' has attribute list, but no element declaration",
    1007: "Attribute '%s' defined more than once",
    1008: "Ambiguous content model",

    # --- Namespace warnings
    1900: "Namespace prefix names cannot contain ':'s.",
    1901: "Namespace URI cannot be empty",
    1902: "Namespace prefix not declared",
    1903: "Attribute names not unique after namespace processing",

    # --- Validity errors: 2000-2999
    2000: "Actual value of attribute '%s' does not match fixed value",
    2001: "Element '%s' not allowed here",
    2002: "Document root element '%s' does not match declared root element",
    2003: "Element '%s' not declared",
    2004: "Element '%s' ended before required elements found (%s)",
    2005: "Character data not allowed in the content of this element",
    2006: "Attribute '%s' not declared",
    2007: "ID '%s' appears more than once in document",
    2008: "Only unparsed entities allowed as the values of ENTITY attributes",
    2009: "Notation '%s' not declared",
    2010: "Required attribute '%s' not present",
    2011: "IDREF referred to non-existent ID '%s'",
    2012: "Element '%s' declared more than once",
    2013: "Only one ID attribute allowed on each element type",
    2014: "ID attributes cannot be #FIXED or defaulted",
    2015: "xml:space must be declared an enumeration type",
    2016: "xml:space must have exactly one or both of the values 'default' and 'preserve'",
    2017: "'%s' is not an allowed value for the '%s' attribute",
    2018: "Value of '%s' attribute must be a valid name",
    2019: "Value of '%s' attribute not a valid name token",
    2020: "Value of '%s' attribute not a valid name token sequence",
    2021: "Token '%s' in the value of the '%s' attribute is not a valid name",
    2022: "Notation attribute '%s' uses undeclared notation '%s'",
    2023: "Unparsed entity '%s' uses undeclared notation '%s'",
    2024: "Cannot resolve relative URI '%s' when document URI unknown",
    2025: "Element '%s' missing before element '%s'",

    # --- Well-formedness errors: 3000-3999
    # From xmlutils
    3000: "Couldn't open resource '%s'",
    3001: "Construct started, but never completed",
    3002: "Whitespace expected here",
    3003: "Didn't match '%s'",   ## FIXME: This must be redone
    3004: "One of %s or '%s' expected",
    3005: "'%s' expected",
    3047: "encoding '%s' conflicts with autodetected encoding",
    3048: "character set conversion problem: %s",

    # From xmlproc.XMLCommonParser
    3006: "SYSTEM or PUBLIC expected",
    3007: "Text declaration must appear first in entity",
    3008: "XML declaration must appear first in document",
    3009: "Multiple text declarations in a single entity",
    3010: "Multiple XML declarations in a single document",
    3011: "XML version missing on XML declaration",
    3012: "Standalone declaration on text declaration not allowed",
    3045: "Processing instruction target names beginning with 'xml' are reserved",
    3046: "Unsupported XML version",

    # From xmlproc.XMLProcessor
    3013: "Illegal construct",
    3014: "Premature document end, element '%s' not closed",
    3015: "Premature document end, no root element",
    3016: "Attribute '%s' occurs twice",
    3017: "Elements not allowed outside root element",
    3018: "Illegal character number '%d' in character reference",
    3019: "Entity recursion detected",
    3020: "External entity references not allowed in attribute values",
    3021: "Undeclared entity '%s'",
    3022: "'<' not allowed in attribute values",
    3023: "End tag for '%s' seen, but '%s' expected",
    3024: "Element '%s' not open",
    3025: "']]>' must not occur in character data",
    3027: "Not a valid character number",
    3028: "Character references not allowed outside root element",
    3029: "Character data not allowed outside root element",
    3030: "Entity references not allowed outside root element",
    3031: "References to unparsed entities not allowed in element content",
    3032: "Multiple document type declarations",
    3033: "Document type declaration not allowed inside root element",
    3034: "Premature end of internal DTD subset",
    3042: "Element crossed entity boundary",

    # From xmlproc.DTDParser
    3035: "Parameter entities cannot be unparsed",
    3036: "Parameter entity references not allowed in internal subset declarations",
    3037: "External entity references not allowed in entity replacement text",
    3038: "Unknown parameter entity '%s'",
    3039: "Expected type or alternative list",
    3040: "Choice and sequence lists cannot be mixed",
    3041: "Conditional sections not allowed in internal subset",
    3043: "Conditional section not closed",
    3044: "Token '%s' defined more than once",
    # next: 3049

    # From regular expressions that were not matched
    3900: "Not a valid name",
    3901: "Not a valid version number (%s)",
    3902: "Not a valid encoding name",
    3903: "Not a valid comment",
    3905: "Not a valid hexadecimal number",
    3906: "Not a valid number",
    3907: "Not a valid parameter reference",
    3908: "Not a valid attribute type",
    3909: "Not a valid attribute default definition",
    3910: "Not a valid enumerated attribute value",
    3911: "Not a valid standalone declaration",

    # --- Internal errors: 4000-4999
    4000: "Internal error: Entity stack broken",
    4001: "Internal error: Entity reference expected.",
    4002: "Internal error: Unknown error number %d.",
    4003: "Internal error: External PE references not allowed in declarations",

    # --- XCatalog errors: 5000-5099
    5000: "Uknown XCatalog element: %s.",
    5001: "Required XCatalog attribute %s on %s missing.",

    # --- SOCatalog errors: 5100-5199
    5100: "Invalid or unsupported construct: %s.",
    }

# Errors in Norwegian
norsk = english.copy()
norsk.update({

    # --- Warnings: 1000-1999
    1000: "Navneroms-prefikset '%s' er ikke deklarert",
    1002: "Tegn-kodingen '%s' er ikke st�ttet",
    1003: "Denne navnerom-syntaksen er foreldet",
    1005: "Tegn nummer '%d' i tegn-referansen er ikke st�ttet",
    1006: "Element '%s' har attributt-liste, men er ikke deklarert",
    1007: "Attributt '%s' deklarert flere ganger",
    1008: "Tvetydig innholds-modell",

    # --- Namespace warnings: 1900-1999
    1900: "Navnerommets prefiks-navn kan ikke inneholde kolon",
    1901: "Navnerommets URI kan ikke v�re tomt",
    1902: "Navnerommets prefiks er ikke deklarert",
    1903: "Attributt-navn ikke unike etter navneroms-prosessering",

    # --- Validity errors: 2000-2999
    2000: "Faktisk verdi til attributtet '%s' er ikke lik #FIXED-verdien",
    2001: "Elementet '%s' er ikke tillatt her",
    2002: "Dokumentets rot-element '%s' er ikke det samme som det deklarerte",
    2003: "Element-typen '%s' er ikke deklarert",
    2004: "Elementet '%s' avsluttet, men innholdet ikke ferdig",
    2005: "Tekst-data er ikke tillatt i dette elementets innhold",
    2006: "Attributtet '%s' er ikke deklarert",
    2007: "ID-en '%s' brukt mer enn en gang",
    2008: "Bare uparserte entiteter er tillatt som verdier til ENTITY-attributter",
    2009: "Notasjonen '%s' er ikke deklarert",
    2010: "P�krevd attributt '%s' mangler",
    2011: "IDREF viste til ikke-eksisterende ID '%s'",
    2012: "Elementet '%s' deklarert mer enn en gang",
    2013: "Bare ett ID-attributt er tillatt pr element-type",
    2014: "ID-attributter kan ikke v�re #FIXED eller ha standard-verdier",
    2015: "xml:space m� deklareres som en oppramstype",
    2016: "xml:space m� ha en eller begge av verdiene 'default' og 'preserve'",
    2017: "'%s' er ikke en gyldig verdi for '%s'-attributtet",
    2018: "Verdien til '%s'-attributtet m� v�re et gyldig navn",
    2019: "Verdien til '%s'-attributtet er ikke et gyldig NMTOKEN",
    2020: "Verdien til '%s'-attributtet er ikke et gyldig NMTOKENS",
    2021: "Symbolet '%s' i verdien til '%s'-attributtet er ikke et gyldig navn",
    2022: "Notasjons-attributtet '%s' bruker en notasjon '%s' som ikke er deklarert",
    2023: "Uparsert entitet '%s' bruker en notasjon '%s' som ikke er deklarert",

    # --- Well-formedness errors: 3000-3999
    # From xmlutils
    3000: "Kunne ikke �pne '%s'",
    3001: "For tidlig slutt p� entiteten",
    3002: "Blanke forventet her",
    3003: "Matchet ikke '%s'",   ## FIXME: This must be redone
    3004: "En av %s eller '%s' forventet",
    3005: "'%s' forventet",

    # From xmlproc.XMLCommonParser
    3006: "SYSTEM eller PUBLIC forventet",
    3007: "Tekst-deklarasjonen m� st� f�rst i entiteten",
    3008: "XML-deklarasjonen m� st� f�rst i dokumentet",
    3009: "Flere tekst-deklarasjoner i samme entitet",
    3010: "Flere tekst-deklarasjoner i samme dokument",
    3011: "XML-versjonen mangler p� XML-deklarasjonen",
    3012: "'Standalone'-deklarasjon p� tekst-deklarasjon ikke tillatt",

    # From xmlproc.XMLProcessor
    3013: "Syntaksfeil",
    3014: "Dokumentet slutter for tidlig, elementet '%s' er ikke lukket",
    3015: "Dokumentet slutter for tidlig, rot-elementet mangler",
    3016: "Attributtet '%s' gjentatt",
    3017: "Kun ett rot-element er tillatt",
    3018: "Ulovlig tegn nummer '%d' i tegn-referanse",
    3019: "Entitets-rekursjon oppdaget",
    3020: "Eksterne entitets-referanser ikke tillatt i attributt-verdier",
    3021: "Entiteten '%s' er ikke deklarert",
    3022: "'<' er ikke tillatt i attributt-verdier",
    3023: "Slutt-tagg for '%s', men '%s' forventet",
    3024: "Elementet '%s' lukket, men ikke �pent",
    3025: "']]>' ikke tillatt i tekst-data",
    3027: "Ikke et gyldig tegn-nummer",
    3028: "Tegn-referanser ikke tillatt utenfor rot-elementet",
    3029: "Tekst-data ikke tillatt utenfor rot-elementet",
    3030: "Entitets-referanser ikke tillatt utenfor rot-elementet",
    3031: "Referanser til uparserte entiteter er ikke tillatt i element-innhold",
    3032: "Mer enn en dokument-type-deklarasjon",
    3033: "Dokument-type-deklarasjon kun tillatt f�r rot-elementet",
    3034: "Det interne DTD-subsettet slutter for tidlig",
    3042: "Element krysset entitets-grense",
    3045: "Processing instruction navn som begynner med 'xml' er reservert",
    3046: "Denne XML-versjonen er ikke st�ttet",

    # From xmlproc.DTDParser
    3035: "Parameter-entiteter kan ikke v�re uparserte",
    3036: "Parameter-entitets-referanser ikke tillatt inne i deklarasjoner i det interne DTD-subsettet",
    3037: "Eksterne entitets-referanser ikke tillatt i entitetsdeklarasjoner",
    3038: "Parameter-entiteten '%s' ikke deklarert",
    3039: "Forventet attributt-type eller liste av alternativer",
    3040: "Valg- og sekvens-lister kan ikke blandes",
    3041: "'Conditional sections' er ikke tillatt i det interne DTD-subsettet",
    3043: "'Conditional section' ikke lukket",
    3044: "Symbolet '%s' er definert mer enn en gang",

    # From regular expressions that were not matched
    3900: "Ikke et gyldig navn",
    3901: "Ikke et gyldig versjonsnummer (%s)",
    3902: "Ikke et gyldig tegnkodings-navn",
    3903: "Ikke en gyldig kommentar",
    3905: "Ikke et gyldig heksadesimalt tall",
    3906: "Ikke et gyldig tall",
    3907: "Ikke en gyldig parameter-entitets-referanse",
    3908: "Ikke en gyldig attributt-type",
    3909: "Ikke en gyldig attributt-standard-verdi",
    3910: "Ikke en gyldig verdi for opprams-attributter",
    3911: "Ikke en gyldig verdi for 'standalone'",

    # --- Internal errors: 4000-4999
    4000: "Intern feil: Entitets-stakken korrupt.",
    4001: "Intern feil: Entitets-referanse forventet.",
    4002: "Intern feil: Ukjent feilmelding %d.",
    4003: "Intern feil: Eksterne parameter-entiteter ikke tillatt i deklarasjoner",
    # --- XCatalog errors: 5000-5099
    5000: "Ukjent XCatalog-element: %s.",
    5001: "P�krevd XCatalog-attributt %s p� %s mangler.",

    # --- SOCatalog errors: 5100-5199
    5100: "Ugyldig eller ikke st�ttet konstruksjon: %s.",
    })

# Errors in Swedish
# Contributed by Marus Brisenfeldt, <marcusb@infotek.no>

svenska = english.copy()
svenska.update({

    # --- Warnings: 1000-1999
    1000: "Namnrymds-prefixet '%s' �r inte deklarerat",
    1002: "Systemet st�der inte teckenupps�ttningen '%s'",
    1003: "Denna namnrymds-syntax �r f�rlegad",
    1005: "Teckennummer '%d' i teckenreferansen st�ds inte",
    1006: "Ett attribut m�ste deklareras f�r elementet '%s'",
    1007: "Attributet '%s' �r deklarerat flera g�nger",
    1008: "Tvetydig innh�llsmodell",

    # --- Namespace warnings: 1900-1999
    1900: "Namnrymdens prefixnamn kan inte inneh�lla kolon",
    1901: "Namnrymdens URI f�r inte vara tom (m�ste deklareras)",
    1902: "Namnrymdsprefixet �r inte deklarerat",
    1903: "Attribut-namn inte unika efter namnrymds-prosessering",

    # --- Validity errors: 2000-2999
    2000: "Attributet '%s' faktiska v�rde �r inte likt #FIXED-v�rdet",
    2001: "Elementet '%s' till�ts inte h�r",
    2002: "Dokumentets rot-element '%s' �r inte det samma som deklarerat",
    2003: "Elementtypen '%s' �r inte deklarerad",
    2004: "Elementet '%s' �r avslutat, men innh�llet �r inte fullst�ndigt",
    2005: "Textdata (PCDATA) �r inte till�tet som inneh�ll i elementet",
    2006: "Attributet '%s' �r inte deklarerat",
    2007: "ID't '%s' anv�nds mer �n en g�ng",
    2008: "Endast icke 'parsade' entiteter �r till�tna som v�rden till ENTITY-attribut",
    2009: "Notationen '%s' �r inte deklarerad",
    2010: "Erfordligt attribut '%s' saknas",
    2011: "IDREF h�nvisar till ett icke existerande ID ('%s')",
    2012: "Elementet '%s' har deklarerats mer �n en g�ng",
    2013: "Endast ett ID-attribut er till�tet per elementtyp",
    2014: "ID-attribut kan inte vara '#FIXED' eller ha ett standardv�rde",
    2015: "xml:space m�ste deklareras som en listtyp",
    2016: "xml:space m�ste ha en eller b�da av v�rdena 'default' och 'preserve'",
    2017: "'%s' �r inte ett giltigt v�rde p� attributet '%s'",
    2018: "V�rdet p� attributet '%s' m�ste vara ett giltigt namn",
    2019: "V�rdet p� attributet '%s' �r inte ett giltigt NMTOKEN",
    2020: "V�rdet p� attributet '%s' �r inte ett giltigt NMTOKENS",
    2021: "Symbolen '%s' i v�rdet p� attributet '%s' �r inte ett giltigt namn",
    2022: "Notations-attributet '%s' anv�nder en notation ('%s') som inte �r deklarerad",
    2023: "Icke 'parsad' entitet anv�nder en notation ('%s') som inte �r deklarerad",

    # --- Well-formedness errors: 3000-3999
    # From xmlutils
    3000: "Systemet kunde inte �ppna '%s'",
    3001: "Entitet p�b�rjad, men inte avslutad",
    3002: "Mellanslag f�rv�ntat h�r",
    3003: "Matchar inte '%s'",   ## FIXME: This must be redone
    3004: "Antingen %s eller '%s' f�rv�ntad",
    3005: "'%s' f�rv�ntad",

    # From xmlproc.XMLCommonParser
    3006: "Antingen SYSTEM eller PUBLIC f�rv�ntad",
    3007: "Textdeklarationen m�ste st� f�rst i entiteten",
    3008: "XML-deklarationen m�ste st� f�rst i dokumentet",
    3009: "Flera textdeklarationer i samma entitet",
    3010: "Flera textdeklarationer i samma dokument",
    3011: "XML-version saknas i XML-deklarationen",
    3012: "'Standalone'-deklaration i textdeklarationen �r inte till�tet",

    # From xmlproc.XMLProcessor
    3013: "Syntaxfel",
    3014: "F�r tidigt dokumentslut, elementet '%s' �r inte st�ngt",
    3015: "F�r tidigt dokumentslut, rotelement saknas",
    3016: "Attributet '%s' anv�nt tv� g�nger",
    3017: "Endast ett rotelement �r till�tet",
    3018: "Olovlig teckennummer ('%d') i teckenreferansen",
    3019: "Entitets-upprepning uppt�ckt",
    3020: "Externa entitets-referanser �r inte till�tna i attributv�rden",
    3021: "Entiteten '%s' �r inte deklarerad",
    3022: "'<' er inte till�tet i attributv�rdet",
    3023: "Sluttagg f�r '%s' ist�llet f�r f�rv�ntad '%s'",
    3024: "Finner elementet '%s' sluttagg, men inte dess starttagg",
    3025: "']]>' inte till�tet i textdata",
    3027: "Inget giltigt teckennummer",
    3028: "Teckenreferanser �r inte till�tna utanf�r rotelementet",
    3029: "Textdata �r inte till�tet utanf�r rotelementet",
    3030: "Entitetsreferanser �r inte till�tna utanf�r rotelementet",
    3031: "Referanser till icke 'parsade' entiteter till�ts inte i elementinnh�llet",
    3032: "Multipla dokumenttypsdeklarationer",
    3033: "Dokumenttypsdeklarationer till�ts inte i rotelementet",
    3034: "Det interna DTD-subsettet avslutas f�r tidigt",
    3042: "Element �verskrider entitetsgr�ns",

    # From xmlproc.DTDParser
    3035: "Parameterentiteter kan inte vara 'oparsade'",
    3036: "Parameterentitetsreferanser till�ts inte inne i deklarationer i det interna DTD-subsettet",
    3037: "Externa entitetsreferanser till�ts inte i entitetsdeklarationer",
    3038: "Parameterentiteten '%s' �r inte deklarerad",
    3039: "F�rv�ntat attributtyp eller lista av alternativ",
    3040: "Val- och sekvenslistor kan inte blandas",
    3041: "'Villkorssektioner' �r inte till�tna i den interna DTD-delm�ngden (subsetet)",
    3043: "'Villkorssektionen' �r inte st�ngd",
    3044: "Symbolen '%s' har definerats mer �n en g�ng",
    3045: "Processinstruktionsnamn som b�rjar med 'xml' �r reserverade",
    3046: "Systemet st�der inte anv�nd XML-versjon",

    # From regular expressions that were not matched
    3900: "Inget giltigt namn",
    3901: "Inget giltigt versionsnummer",
    3902: "Inget giltigt teckenkodsnamn",
    3903: "Ingen giltig kommentar",
    3905: "Inget giltigt hexadecimalt tal",
    3906: "Inget giltigt tal",
    3907: "Ingen giltig parameterentitetsreferans",
    3908: "Ingen giltig attributtyp",
    3909: "Inge giltigt attributstandardv�rde",
    3910: "Ikke en gyldig attributt-standard-verdi",
    3911: "Ikke en gyldig verdi for 'standalone'",

    # --- Internal errors: 4000-4999
    4000: "Internt fel: Entitetsstacken korrupt.",
    4001: "Internt fel: Entitetsreferans f�rv�ntad.",
    4002: "Internt fel: Ok�nt felmeddelande %d.",
    4003: "Internt fel: Externa parameterentiteter till�ts inte i deklarationer.",
    # --- XCatalog errors: 5000-5099
    5000: "Ok�nt XCatalog-element: %s.",
    5001: "N�dv�ndigt XCatalog-attribut %s p� %s saknas.",

    # --- SOCatalog errors: 5100-5199
    5100: "Konstruktionen: %s �r ogiltig eller saknar st�d.",
    })

# Errors in French
# Contributed by Alexandre Fayolle, Logilab. Alexandre.Fayolle@logilab.fr

french = english.copy()
french.update({
    # Les termes fran�ais utilis�s sont tir�s de l'ouvrage
    # XML, Langage et applications, Alain Michard, Eyrolles
    # ISBN 2-212-09052-8

    # --- Warnings: 1000-1999
    1000: "Pr�fixe de domaine nominal non d�clar� '%s'",
    1002: "Encodage non support� '%s'",
    1003: "Syntaxe de domaine nominal obsol�te",
    1005: "Caract�re num�ro '%d' non support� dans la r�f�rence de caract�re",
    1006: "L'�l�ment '%s' a une liste d'attributs mais pas de d�claration d'�l�ment",
    1007: "L'attribute '%s' est d�fini plus d'une fois",
    1008: "Mod�le de contenu ambigu",

    # --- Namespace warnings
    1900: "Les pr�fixes de domaines nominaux ne peuvent contenir le caract�re ':'",
    1901: "L'URI du domaine nominal ne doit pas �tre vide",
    1902: "Le pr�fixe du domaine nominal n'est pas d�clar�",
    1903: "Le nom d'attribut n'est pas unique apr�s traitement des domaines nominaux",

    # --- Validity errors: 2000-2999
    2000: "La valeur de l'attribut '%s' ne correspond pas � la valeur impos�e",
    2001: "L'�l�ment '%s' ne peut figurer � cet endroit",
    2002: "L'�l�ment racine du document '%s' ne correspond pas � la racine d�clar�e",
    2003: "L'�l�ment '%s' n'a pas �t� d�clar�",
    2004: "L'�l�ment '%s' est termin�, mais il n'est pas complet",
    2005: "Les donn�es ne sont pas autoris�es comme contenu de cet �l�ment",
    2006: "L'attribut '%s' n'a pas �t� d�clar�",
    2007: "L'ID '%s' appara�t plusieurs fois dans le document",
    2008: "Seules les entit�s non XML sont permises dans les attributs ENTITY",
    2009: "La notation '%s' n'a pas �t� d�clar�e",
    2010: "L'attribut requis '%s' est absent",
    2011: "L'attribut IDREF point sur un ID inexistant '%s'",
    2012: "L'�l�ment '%s' est d�clar� plus d'une fois",
    2013: "Un seul attribut ID par type d'�l�ment",
    2014: "Les attributs ID nepeuvent �tre #FIXED ou avoir de valeur par d�faut",
    2015: "xml:space doit �tre de type �num�ration",
    2016: "xml:space doit avoir comme valeurs possibles 'default' et 'preserve'",
    2017: "'%s' n'est pas une valeur autoris�e pour l'attribut '%s'",
    2018: "La valeur de l'attribut '%s' doit �tre un nom valide",
    2019: "La valeur de l'attribut '%s' n'est pas un identifiant de nom valide",
    2020: "La valeur de l'attribut '%s' n'est pas une liste d'identifiants de noms valides",
    2021: "L'identifiant '%s' dans la valeur de l'attribut '%s' n'est pas valide",
    2022: "L'attribut notation '%s' utilise la notation non d�clar�e '%s'",
    2023: "L'entit� non XML '%s' utilise la notation non d�clar�e '%s'",

    # --- Well-formedness errors: 3000-3999
    # From xmlutils
    3000: "Impossible d'ouvrir la ressource '%s'",
    3001: "Construction commenc�e mais jamais achev�e",
    3002: "Caract�res d'espacement attendus � cet endroit",
    3003: "Impossible de faire correspondre '%s'",   ## FIXME: This must be redone
    3004: "'%s' ou '%s' �tait attendu",
    3005: "'%s' �tat attendu",

    # From xmlproc.XMLCommonParser
    3006: "SYSTEM ou PUBLIC �tait attendu",
    3007: "La d�claration de texte doit appara�tre en premier dans une entit�",
    3008: "La d�claration XML doit appara�tre en premier dans un document",
    3009: "Plusieurs d�clarations de texte dans une seule entit�",
    3010: "Plusieurs d�clarations XML dans le document",
    3011: "Il manque la versin d'XML dans la d�claratino XML",
    3012: "Une d�claration ind�pendante de texte sont interdites",
    3045: "Les noms de cibles d'instruction de traitement commen�ant par 'xml' sont r�serv�s",
    3046: "Version de XML non support�e",

    # From xmlproc.XMLProcessor
    3013: "Construction ill�gale",
    3014: "Fin de document pr�matur�e, l'�l�ment '%s' n'est pas ferm�",
    3015: "Fin de document pr�matur�e, pas d'�l�ment racine",
    3016: "L'attribut '%s' appar�it deux fois",
    3017: "Les �l�ments ne peuvent appara�tre � l'ext�rieur de l'�l�ment racine",
    3018: "Caract�re num�ro '%d' non support� dans la r�f�rence de caract�re",
    3019: "Une entit� r�cursive a �t� d�tect�e",
    3020: "Les r�f�rences � des entit�s externes sont interdites dans les valeurs d'attributs",
    3021: "L'entit� '%s' n'a pas �t� d�clar�e",
    3022: "'<' est interdit dans les valeurs d'attributs",
    3023: "La balise de fin pour '%s' a �t� vue, alors que '%s' �tait attendu",
    3024: "L'�l�ment'%s' n'a pas �t� ouvert",
    3025: "']]>' ne doit pas appara�tre dans les sections litt�rales",
    3027: "Num�ro de caract�re invalide",
    3028: "Les r�f�rences de caract�res sont interdites en dehors de l'�l�ment racine",
    3029: "Les sections litt�rales sont interdites en dehors de l'�l�ment racine",
    3030: "Les r�f�rences � des entit�s sont interdites en dehors de l'�l�ment racine",
    3031: "Les r�f�rences � des entit�s non XML sont interdites dans un �l�ment",
    3032: "Il y a de multiples d�claratinos de type de document",
    3033: "La d�claration de type de document est interdite dans l'�l�ment racine",
    3034: "Fin pr�matur�e de la DTD interne",
    3042: "Un �l�ment chevauche les limites d'une entit�",

    # From xmlproc.DTDParser
    3035: "Les entit�s param�tres ne peuvent pas �tre d�r�f�renc�es",
    3036: "Les r�f�rences � des entit�s param�tres sont interdites dans la DTD interne",
    3037: "Les r�f�rences � des entit�s externes sont interdites dans le texte de remplacement",
    3038: "L'entit� param�tre '%s' est inconnue",
    3039: "Un type une liste de valeurs possibles est attendu",
    3040: "Les liste de choix et les listes de s�quences ne peuvent �tre m�lang�es",
    3041: "Les sections conditionnelles sont interdites dans la DTD interne",
    3043: "La section conditionnelle n'est pas ferm�e",
    3044: "Le marqueur '%s' est d�fini plusieurs fois",
    # next: 3047

    # From regular expressions that were not matched
    3900: "Nom invalide",
    3901: "Num�ro de version invalide (%s)",
    3902: "Nom d'encodage invalide",
    3903: "Commentaire invalide",
    3905: "Nombre hexad�cimal invalide",
    3906: "Nombre invalide",
    3907: "R�f�rence � un param�tre invalide",
    3908: "Type d'attribut invalide",
    3909: "D�finitionde valeur par d�faut d'attribut invalide",
    3910: "Valeur d'attribut �num�r� invalide",
    3911: "D�claration autonome invalide",

    # --- Internal errors: 4000-4999
    4000: "Erreur interne : pile dentit�s cass�e",
    4001: "Erreur interne : r�f�rence � une entit� attendue.",
    4002: "Erreur interne : num�ro d'erreur inconnu.",
    4003: "Erreur interne : r�f�rence � un PE externe interdite dans la d�claration",

    # --- XCatalog errors: 5000-5099
    5000: "L'�l�ment de XCatalog est inconnu : %s.",
    5001: "L'attribut de XCatalog  %s requis sur %s est manquant.",

    # --- SOCatalog errors: 5100-5199
    5100: "Construction invalide ou non support�e : %s.",
    })

# Errors in Spanish
# Contributed by Ricardo Javier Cardenes (ricardo@conysis.com)

spanish = {

    # --- Warnings: 1000-1999
    1000: "Prefijo de espacio de nombres sin declarar '%s'",
    1002: "Codificaci�n no soportada '%s'",
    1003: "Sintaxis de espacio de nombres obsoleta",
    1005: "Caracter n�mero '%d' no soportado en la referencia a caracter",
    1006: "El elemento '%s' tiene lista de atributos, pero no declaraci�n de elemento",
    1007: "El atributo '%s' est� definido m�s de una vez",
    1008: "Modelo de contenido ambiguo",

    # --- Namespace warnings
    1900: "Los prefijos de espacio de nombres no pueden contener ':'.",
    1901: "Las URI de los espacios de nombre no pueden estar vac�as",
    1902: "Prefijo de espacio de nombres sin declarar",
    1903: "Nombres de atributo repetidos despu�s de procesar el espacio de nombres",

    # --- Validity errors: 2000-2999
    2000: "El valor real del atributo '%s' no se corresponde al valor fijado",
    2001: "No se permite aqu� el elemento '%s'",
    2002: "El elemento '%s' ra�z del documento no es el mismo que se declar�",
    2003: "El elemento '%s' no est� declarado",
    2004: "El elemento '%s' termina antes de encontrar los elementos requeridos (%s)",
    2005: "No se permite texto en el contenido de este elemento",
    2006: "El atributo '%s' no ha sido declarado",
    2007: "El ID '%s' aparece m�s de una vez en el documento",
    2008: "S�lo se permiten entidades sin analizar como valores de los atributos ENTITY",
    2009: "No est� declarada la notaci�n '%s'",
    2010: "No est� presente el atributo '%s' necesario",
    2011: "IDREF referida a un ID '%s', que no existe",
    2012: "El elemento '%s' est� declarado m�s de una vez",
    2013: "S�lo se permite un atributo ID por cada tipo de elemento",
    2014: "Los atributos ID no pueden ser #FIXED ni tener valor por defecto",
    2015: "xml:space debe ser declarado como tipo enumerado",
    2016: "xml:space debe tener exactamente los valores 'default' y 'preserve'",
    2017: "'%s' no es un tipo v�lido para el atributo '%s'",
    2018: "El valor del atributo '%s' debe ser un nombre v�lido",
    2019: "El valor del atributo '%s' no es un NMTOKEN v�lido",
    2020: "El valor del atributo '%s' no es un NMTOKENS v�lido",
    2021: "El s�mbolo '%s' en el valor del atributo '%s' no es un nombre v�lido",
    2022: "El atributo de notaci�n '%s' usa la notaci�n '%s', que no est� declarada",
    2023: "La entidad sin analizar '%s' usa la notaci�n '%s', que no est� declarada",
    2024: "No se puede resolver la URI relativa '%s' si se desconoce la URI del documento",
    2025: "No se encuentra el elemento '%s' antes del '%s'",

    # --- Well-formedness errors: 3000-3999
    # From xmlutils
    3000: "No pude abrir el recurso '%s'",
    3001: "Se empez� la construcci�n, pero no se pudo completar",
    3002: "Aqu� se esperaba un espacio en blanco",
    3003: "'%s' no se corresponde",   ## FIXME: This must be redone
    3004: "Se esperaba %s o '%s'",
    3005: "Se esperaba '%s'",
    3047: "La codificaci�n '%s' es conflictiva con la autodetectada",
    3048: "Problema de conversi�n de conjunto de caracteres: %s",

    # From xmlproc.XMLCommonParser
    3006: "Se esperaba SYSTEM o PUBLIC",
    3007: "La declaraci�n de texto debe aparecer la primera en la entidad",
    3008: "La declaraci�n XML debe aparecer la primera en el documento",
    3009: "Varias declaraciones de texto en la misma entidad",
    3010: "M�ltiples declaraciones XML en el mismo documento",
    3011: "Falta la versi�n en la declaraci�n XML",
    3012: "No se permite una declaraci�n 'standalone' en una declaraci�n de texto",
    3045: "Los nombres de PI que comienzan por 'xml' est�n reservados",
    3046: "Versi�n XML no soportada",
    
    # From xmlproc.XMLProcessor
    3013: "Construcci�n ilegal",
    3014: "El documento acab� prematuramente. No se cerr� el elemento '%s'",
    3015: "Fin prematuro del documento. No hay elemento ra�z",
    3016: "El atributo '%s' est� duplicado",
    3017: "No se permiten elementos fuera del ra�z",
    3018: "Caracter ilegal n�mero '%d' en la referencia a caracter",
    3019: "Detectada recursividad de entidades",
    3020: "No se permiten referencias a entidades externas en los valores de los atributos",
    3021: "Entidad '%s' sin declarar",
    3022: "No se permite '<' en los valores de atributos",
    3023: "Se encontr� la etiqueta de fin de '%s', pero se esperaba '%s'",
    3024: "Element '%s' not open",
    3025: "No debe aparecer ']]>' dentro de datos de texto",
    3027: "No es un n�mero de caracter v�lido",
    3028: "No se permite la referencia a caracteres fuera del elemento ra�z",
    3029: "No se admite texto fuera del elemento ra�z",
    3030: "No se admiten referencias a entidades fuera del elemento ra�z",
    3031: "No se admiten referencias a entidades sin analizar en el contenido de un elemento",
    3032: "M�ltiples declaraciones de tipo de documento",
    3033: "No se admite una declaraci�n de tipo de documento dentro del elemento ra�z",
    3034: "Fin prematuro de un subconjunto interno de DTD",
    3042: "Un elemento cruza los l�mites de la entidad",

    # From xmlproc.DTDParser
    3035: "Las entidades param�tricas no pueden ser de tipo 'unparsed'",
    3036: "No se permiten referencias a entidades param�tricas en un subconjunto interno de declaraciones",
    3037: "No se permiten referencias a entidades externas en texto de reemplazo de entidades",
    3038: "Entidad param�trica desconocida '%s'",
    3039: "Se esperaba un tipo o una lista de alternativas",
    3040: "No se puede mezclar listas secuenciales con alternativas",
    3041: "No se admiten secciones condicionales en subconjuntos internos",
    3043: "Secci�n condicional sin cerrar",
    3044: "Se defini� el s�mbolo '%s' m�s de una vez",
    # next: 3049
    
    # From regular expressions that were not matched
    3900: "No es un nombre v�lido",
    3901: "No es un n�mero de versi�n v�lido (%s)",
    3902: "No es un nombre de codificaci�n v�lido",
    3903: "No es un comentario v�lido",
    3905: "No es un n�mero hexadecimal v�lido",
    3906: "No es un n�mero v�lido",
    3907: "No es una referencia a par�metro v�lida",
    3908: "No es un tipo de atributo v�lido",
    3909: "No es una definici�n de atributo por defecto v�lida",
    3910: "No es un valor de atributo enumerado v�lido",
    3911: "No es una declaraci�n 'standalone' v�lida",
    
    # --- Internal errors: 4000-4999
    4000: "Error interno: Pila de la entidad corrupta",
    4001: "Error interno: Se esperaba una referencia a entidad.",
    4002: "Error interno: N�mero de error desconocido.",
    4003: "Error interno: No se admiten refrencias PE externas en las declaraciones",

    # --- XCatalog errors: 5000-5099
    5000: "Elemento XCatalog desconocido: %s.",
    5001: "Falta el atributo XCatalog %s necesario en %s.",
     
    # --- SOCatalog errors: 5100-5199
    5100: "Construcci�n inv�lida o no soportada: %s.",
    }

# Updating the error hash

add_error_list("en", english)
add_error_list("no", norsk)
add_error_list("sv", svenska)
add_error_list("fr", french)
add_error_list("es", spanish)

# Checking

def _test():
    def compare(l1, l2):
        for key in l1:
            if not key in l2:
                print "l1:", key

        for key in l2:
            if not key in l1:
                print "l2:", key

    en = english.keys()
    no = norsk.keys()
    sv = svenska.keys()
    fr = french.keys()
    es = spanish.keys()

    en.sort()
    no.sort()
    sv.sort()
    fr.sort()
    es.sort()

    print "en == no"
    compare(en, no)

    print "en == sv"
    compare(en, sv)

    print "en == fr"
    compare(en, fr)

    print "en == es"
    compare(en, es)

if __name__ == "__main__":
    _test()
