from dataclasses import dataclass, field


@dataclass
class ResearchEvidence:
    tables: list[str] = field(default_factory=list)
    figures: list[str] = field(default_factory=list)
    narrative: list[str] = field(default_factory=list)

    @property
    def count(self) -> int:
        return (
            len(self.tables)
            + len(self.figures)
            + len(self.narrative)
        )
        
    @property
    def status(self) -> str:
        return (
            "Complete"
            if self.count > 0
            else "In Progress"
        )    