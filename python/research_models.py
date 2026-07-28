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
            if self.has_evidence
            else "In Progress"
        )    
        
        
    @property
    def summary(self) -> str:
        table_label = "table" if len(self.tables) == 1 else "tables"
        figure_label = "figure" if len(self.figures) == 1 else "figures"
        narrative_label = (
            "narrative"
            if len(self.narrative) == 1
            else "narratives"
        )

        return (
            f"{self.count} linked outputs "
            f"({len(self.tables)} {table_label}, "
            f"{len(self.figures)} {figure_label}, "
            f"{len(self.narrative)} {narrative_label})"
        )
        
        
    @property
    def has_evidence(self) -> bool:
        return self.count > 0    
        
        
        


@dataclass
class ResearchDashboard:
    complete: int
    total: int

    @property
    def percentage(self) -> float:
        if self.total == 0:
            return 0.0
        return 100.0 * self.complete / self.total

    @property
    def summary(self) -> str:
        return (
            f"{self.complete}/{self.total} "
            f"({self.percentage:.1f}%)"
        )        
        
    @property
    def ready_for_publication(self) -> bool:
        return self.complete == self.total    