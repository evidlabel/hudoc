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
def _rss_url(sub):
    return (
        f"https://hudoc.{sub}.coe.int/app/transform/rss"
        f"?library={sub}eng&query=contentsitename%3A{sub.upper()}&sort=&start=1"
    )


SUBSITE_CONFIG = {
    "echr": {
        "library": "ECHR",
        "id_key": "itemid",
        "base_url": "https://hudoc.echr.coe.int/app/conversion/docx/html/body",
        "rss_url": _rss_url("echr"),
    },
    "grevio": {
        "library": "GREVIO",
        "id_key": "greviosectionid",
        "base_url": "https://hudoc.grevio.coe.int/app/conversion/docx/html/body",
        "rss_url": _rss_url("grevio"),
    },
    "commhr": {
        "library": "COMMHR",
        "id_key": "commhridentifier",
        "base_url": "https://hudoc.commhr.coe.int/app/conversion/docx/html/body",
        "rss_url": _rss_url("commhr"),
    },
    "cpt": {
        "library": "CPT",
        "id_key": "cptsectionid",
        "base_url": "https://hudoc.cpt.coe.int/app/conversion/docx/html/body",
        "rss_url": _rss_url("cpt"),
    },
    "ecri": {
        "library": "ECRI",
        "id_key": "ecriidentifier",
        "base_url": "https://hudoc.ecri.coe.int/app/conversion/docx/html/body",
        "rss_url": _rss_url("ecri"),
    },
    "ecrml": {
        "library": "ECRML",
        "id_key": "ecrmlsectionid",
        "base_url": "https://hudoc.ecrml.coe.int/app/conversion/docx/html/body",
        "rss_url": _rss_url("ecrml"),
    },
    "esc": {
        "library": "ESC",
        "id_key": "escdcidentifier",
        "base_url": "https://hudoc.esc.coe.int/app/conversion/docx/html/body",
        "rss_url": _rss_url("esc"),
    },
    "exec": {
        "library": "EXEC",
        "id_key": "execidentifier",
        "base_url": "https://hudoc.exec.coe.int/app/conversion/docx/html/body",
        "rss_url": _rss_url("exec"),
    },
    "fcnm": {
        "library": "FCNM",
        "id_key": "fcnmsectionid",
        "base_url": "https://hudoc.fcnm.coe.int/app/conversion/docx/html/body",
        "rss_url": _rss_url("fcnm"),
    },
    "greco": {
        "library": "GRECO",
        "id_key": "grecosectionid",
        "base_url": "https://hudoc.greco.coe.int/app/conversion/docx/html/body",
        "rss_url": _rss_url("greco"),
    },
    "greta": {
        "library": "GRETA",
        "id_key": "gretaidentifier",
        "base_url": "https://hudoc.greta.coe.int/app/conversion/docx/html/body",
        "rss_url": _rss_url("greta"),
    },
}


def pdf_url(subsite, doc_id):
    """The official PDF of one HUDOC document, the version to key in evid.

    The text route (``base_url``) gives the same words but no pages, so quotes
    are keyed in this PDF. Checked on ECHR judgments; other subsites use the
    same conversion service.
    """
    from urllib.parse import quote

    library = SUBSITE_CONFIG[subsite]["library"]
    item = quote(doc_id, safe="")
    return (
        f"https://hudoc.{subsite}.coe.int/app/conversion/pdf/"
        f"?library={library}&id={item}&filename={item}.pdf"
    )
