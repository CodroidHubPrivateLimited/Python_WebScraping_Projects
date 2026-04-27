from dataclasses import dataclass


@dataclass
class ViewConfig:
    title: str
    section: str = ""
