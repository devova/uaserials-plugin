from dataclasses import dataclass


@dataclass
class CatalogItem:
    title: str
    ref: str


@dataclass
class MetaItemPreview(CatalogItem):
    title_original: str
    poster: str
    labels: list[str]

    @property
    def id(self) -> int:
        return int(self.ref.split("-", 1)[0])
