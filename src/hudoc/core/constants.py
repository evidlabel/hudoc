# Subsite configurations for HUDOC databases
VALID_SUBSITES = [
    "commhr",
    "cpt",
    "ecri",
    "ecrml",
    "esc",
    "exec",
    "fcnm",
    "greco",
    "greta",
    "grevio",
    "echr",
]

# Mapping of subsites to their library codes and document ID keys
SUBSITE_CONFIG = {
    "echr": {
        "library": "ECHR",
        "id_key": "itemid",
        "base_url": "https://hudoc.echr.coe.int/app/conversion/docx/html/body",
    },
    "grevio": {
        "library": "GREVIO",
        "id_key": "greviosectionid",
        "base_url": "https://hudoc.grevio.coe.int/app/conversion/docx/html/body",
    },
    "commhr": {
        "library": "COMMHR",
        "id_key": "commhridentifier",
        "base_url": "https://hudoc.commhr.coe.int/app/conversion/docx/html/body",
    },
    "cpt": {
        "library": "CPT",
        "id_key": "cptsectionid",
        "base_url": "https://hudoc.cpt.coe.int/app/conversion/docx/html/body",
    },
    "ecri": {
        "library": "ECRI",
        "id_key": "ecriidentifier",
        "base_url": "https://hudoc.ecri.coe.int/app/conversion/docx/html/body",
    },
    "ecrml": {
        "library": "ECRML",
        "id_key": "ecrmlsectionid",
        "base_url": "https://hudoc.ecrml.coe.int/app/conversion/docx/html/body",
    },
    "esc": {
        "library": "ESC",
        "id_key": "escdcidentifier",
        "base_url": "https://hudoc.esc.coe.int/app/conversion/docx/html/body",
    },
    "exec": {
        "library": "EXEC",
        "id_key": "execidentifier",
        "base_url": "https://hudoc.exec.coe.int/app/conversion/docx/html/body",
    },
    "fcnm": {
        "library": "FCNM",
        "id_key": "fcnmsectionid",
        "base_url": "https://hudoc.fcnm.coe.int/app/conversion/docx/html/body",
    },
    "greco": {
        "library": "GRECO",
        "id_key": "grecosectionid",
        "base_url": "https://hudoc.greco.coe.int/app/conversion/docx/html/body",
    },
    "greta": {
        "library": "GRETA",
        "id_key": "gretaidentifier",
        "base_url": "https://hudoc.greta.coe.int/app/conversion/docx/html/body",
    },
}
